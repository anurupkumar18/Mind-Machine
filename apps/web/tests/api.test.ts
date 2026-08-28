import { afterEach, describe, expect, it, vi } from "vitest";

import { EvidenceServiceError, getApprovedChallengeCandidates, getApprovedCodeContext, submitConfirmation } from "../lib/api";

const context = {
  repository_id: "public-graph-traversal",
  source: "synthetic-public-fixture",
  files: [{ path: "bfs.py", language: "python", symbols: ["bfs"], line_count: 14 }],
  excluded_files: [".env*", "credentials"]
};

const candidate = {
  objective_ref: "Explain and preserve breadth-first traversal invariants.",
  code_refs: [{ file: "bfs.py", start_line: 1, end_line: 14 }],
  template_id: "TRAVERSAL-INVARIANT-02",
  evidence_plan: ["frontier_prediction", "visited_invariant", "mutation_repair"],
  rationale: "Static analysis found the allowlisted bfs symbol."
};

afterEach(() => vi.restoreAllMocks());

describe("approved challenge context contract", () => {
  it("loads only the fixed allowlisted context and candidate endpoints", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(new Response(JSON.stringify(context), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify([candidate]), { status: 200 }));

    await expect(getApprovedCodeContext()).resolves.toEqual(context);
    await expect(getApprovedChallengeCandidates()).resolves.toEqual([candidate]);

    expect(fetchMock).toHaveBeenNthCalledWith(1, "http://localhost:8000/code-context/public-graph-traversal");
    expect(fetchMock).toHaveBeenNthCalledWith(2, "http://localhost:8000/challenge-candidates/public-graph-traversal");
  });

  it("preserves the expected confirmation rejection status for instructional recovery", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify({ detail: "Confirmation does not preserve the fixture invariant." }), { status: 400 })
    );

    await expect(submitConfirmation("frontier_exit")).rejects.toMatchObject({
      name: "EvidenceServiceError",
      message: "The evidence service could not verify this step.",
      status: 400
    } satisfies Partial<EvidenceServiceError>);
  });
});
