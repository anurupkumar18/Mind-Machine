import { expect, test } from "@playwright/test";

const context = {
  repository_id: "public-graph-traversal",
  source: "synthetic-public-fixture",
  files: [{ path: "bfs.py", language: "python", symbols: ["bfs"], line_count: 15 }],
  excluded_files: [".env*", "credentials", "binaries", "dependencies", "non-Python files"]
};

const candidate = [{
  objective_ref: "Explain and preserve breadth-first traversal invariants.",
  code_refs: [{ file: "bfs.py", start_line: 1, end_line: 15 }],
  template_id: "TRAVERSAL-INVARIANT-02",
  evidence_plan: ["frontier_prediction", "visited_invariant", "mutation_repair"],
  rationale: "Static analysis found the allowlisted bfs symbol; the curated traversal template is compatible."
}];

test("retries the fixed approved challenge context after a load failure", async ({ page }) => {
  let contextAttempts = 0;
  let contextAvailable = false;
  await page.route("http://localhost:8000/code-context/public-graph-traversal", async (route) => {
    contextAttempts += 1;
    if (!contextAvailable) await route.abort("failed");
    else await route.fulfill({ contentType: "application/json", json: context });
  });
  await page.route("http://localhost:8000/challenge-candidates/public-graph-traversal", (route) => route.fulfill({ contentType: "application/json", json: candidate }));

  await page.goto("/");
  await expect.poll(() => contextAttempts).toBeGreaterThan(0);
  await expect(page.getByRole("heading", { name: "Challenge context unavailable" })).toBeVisible();
  const attemptsBeforeRetry = contextAttempts;
  contextAvailable = true;
  await page.getByRole("button", { name: "Retry approved context" }).click();

  await expect(page.getByRole("heading", { name: "Challenge context" })).toBeVisible();
  await expect(page.getByText("bfs.py", { exact: true })).toBeVisible();
  await expect(page.getByText("TRAVERSAL-INVARIANT-02", { exact: true })).toBeVisible();
  expect(contextAttempts).toBeGreaterThan(attemptsBeforeRetry);
});

test("recovers from malformed saved browser state", async ({ page }) => {
  await page.addInitScript(() => {
    sessionStorage.setItem("evidence-engine-plan", JSON.stringify({ objective: 7 }));
    sessionStorage.setItem("evidence-engine-socratic-session", "not-json");
  });
  await page.route("http://localhost:8000/code-context/public-graph-traversal", (route) => route.fulfill({ contentType: "application/json", json: context }));
  await page.route("http://localhost:8000/challenge-candidates/public-graph-traversal", (route) => route.fulfill({ contentType: "application/json", json: candidate }));

  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Challenge context" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Load an editable starter plan" })).toBeVisible();
});

test("guides a diagnosis through conceptual confirmation without exposing repair code", async ({ page }) => {
  await page.route("http://localhost:8000/code-context/public-graph-traversal", (route) => route.fulfill({ contentType: "application/json", json: context }));
  await page.route("http://localhost:8000/challenge-candidates/public-graph-traversal", (route) => route.fulfill({ contentType: "application/json", json: candidate }));
  await page.route("http://localhost:8000/checkpoint", (route) => route.fulfill({ contentType: "application/json", json: {
    accepted: true,
    card: { id: "bfs-invariant", title: "Preserve the frontier invariant", misconception: "A queued node can be rediscovered.", corrective_question: "When should a discovered node be marked visited?", hint: "Track discovery separately from traversal." }
  } }));
  await page.route("http://localhost:8000/challenge/predict", (route) => route.fulfill({ contentType: "application/json", json: {
    correct: true, expected_frontier: ["B", "C"], observed_visited: ["A", "B", "C"], evidence_type: "frontier_prediction"
  } }));
  await page.route("http://localhost:8000/challenge/diagnose", async (route) => {
    const request = route.request().postDataJSON() as { diagnosis: string };
    const accepted = request.diagnosis === "late_frontier_recognition";
    await route.fulfill({ contentType: "application/json", json: accepted
      ? { accepted: true, stage: "confirm", scaffold_level: 0, observation: "D is discovered from two parents.", question: "At which abstract lifecycle event must the traversal record a node to preserve the invariant?" }
      : { accepted: false, stage: "guide", scaffold_level: 1, observation: "D can enter the frontier twice.", question: "Which event records the first discovery?" }
    });
  });
  await page.route("http://localhost:8000/challenge/repair", async (route) => {
    const request = route.request().postDataJSON() as { repair_timing: string };
    if (request.repair_timing === "frontier_entry") {
      await route.fulfill({ contentType: "application/json", json: { accepted: true, tests_passed: true, result: "The canonical traversal tests pass after the confirmed conceptual repair.", evidence_type: "mutation_repair" } });
      return;
    }
    await route.fulfill({ status: 400, contentType: "application/json", json: { detail: "Confirmation does not preserve the fixture invariant." } });
  });
  await page.route("http://localhost:8000/evidence", async (route) => {
    const request = route.request().postDataJSON() as { prediction_correct: boolean; invariant_preserved: boolean; repair_passed: boolean };
    expect(request).toMatchObject({ prediction_correct: true, invariant_preserved: true, repair_passed: true });
    await route.fulfill({ contentType: "application/json", json: {
      status: "Demonstrated",
      items: [{ label: "Repaired controlled mutation", state: "demonstrated", detail: "Observed through a deterministic fixture." }],
      next_action: "Try a transfer graph with a different branching pattern."
    } });
  });

  await page.goto("/");
  await page.getByRole("button", { name: "Load an editable starter plan" }).click();
  await page.getByRole("button", { name: "Use this plan to get coaching" }).click();
  await page.getByRole("button", { name: "B", exact: true }).click();
  await page.getByRole("button", { name: "C", exact: true }).click();
  await page.getByRole("button", { name: "Commit prediction & reveal state" }).click();

  await page.getByRole("button", { name: "The traversal recognizes a discovered node too late, allowing another parent to add it first." }).click();
  await expect(page.getByText("At which abstract lifecycle event must the traversal record a node to preserve the invariant?")).toBeVisible();
  await expect(page.getByText("visited.add", { exact: false })).toHaveCount(0);

  await page.getByRole("button", { name: "When the node leaves the frontier" }).click();
  await expect(page.locator("p[role=alert]")).toHaveText("Choose the lifecycle event that preserves the invariant.");
  await page.getByRole("button", { name: "When the node enters the frontier" }).click();
  await expect(page.getByText("Canonical traversal tests passed after your conceptual confirmation.")).toBeVisible();
  await page.getByRole("button", { name: "Generate evidence map" }).click();
  await expect(page.getByRole("heading", { name: "Graph traversal — Demonstrated" })).toBeVisible();
  await expect(page.getByText("Try a transfer graph with a different branching pattern.")).toBeVisible();
});
