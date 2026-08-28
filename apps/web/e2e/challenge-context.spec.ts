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
  await page.route("http://localhost:8000/code-context/public-graph-traversal", async (route) => {
    contextAttempts += 1;
    if (contextAttempts === 1) await route.abort("failed");
    else await route.fulfill({ contentType: "application/json", json: context });
  });
  await page.route("http://localhost:8000/challenge-candidates/public-graph-traversal", (route) => route.fulfill({ contentType: "application/json", json: candidate }));

  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Challenge context unavailable" })).toBeVisible();
  await page.getByRole("button", { name: "Retry approved context" }).click();

  await expect(page.getByRole("heading", { name: "Challenge context" })).toBeVisible();
  await expect(page.getByText("bfs.py", { exact: true })).toBeVisible();
  await expect(page.getByText("TRAVERSAL-INVARIANT-02", { exact: true })).toBeVisible();
  expect(contextAttempts).toBeGreaterThanOrEqual(2);
});
