# Task handoff: student study workspace (real materials, cited Q&A)

## Goal

Build a second, distinct Evidence Engine capability per explicit product
direction: a student uploads real course materials and gets cited
answers, going beyond the narrower "use uploads only to pick a coding
topic" option considered during brainstorming. Design:
`docs/superpowers/specs/2026-08-29-student-study-workspace-design.md`.

## Changed files

- `apps/api/app/domain/workspace_contracts.py` — new. `MaterialChunk`,
  `IngestResult`, `MaterialSummary`, `RetrievedExcerpt`.
- `apps/api/app/domain/chunking.py` — new. Plain-text-only chunking with
  provenance labels (chunk-index based; page/section-based extraction is
  future work).
- `apps/api/app/domain/data_boundary.py` — new. Heuristic reject/flag/
  allow classification enforcing a redrawn I1 boundary (see the design
  doc's invariant-change list) — never a guarantee, same honesty standard
  as this project's other heuristics.
- `apps/api/app/domain/workspace_store.py` — new. In-process, per-
  workspace storage. Explicitly not a database — stated limitation. Also
  documents a real access-control gap found during review: `workspace_id`
  has no ownership check or unguessability guarantee, unlike the signed
  `challenge_token` — deferred as explicit future work.
- `apps/api/app/domain/retrieval.py` — new. Deterministic keyword-overlap
  ranking, no embeddings, no inference cost (I3-consistent).
- `apps/api/app/domain/ingestion.py` — new. Orchestrates chunking →
  data-boundary check → storage.
- `apps/api/app/mcp_server.py` — adds 5 new tools: `add_course_material`,
  `list_workspace_materials`, `remove_material`, `delete_workspace`,
  `answer_from_materials`. Top-level server `instructions` updated.
- `apps/api/tests/test_chunking.py`, `test_data_boundary.py`,
  `test_workspace_store.py`, `test_retrieval.py`, `test_ingestion.py`,
  `test_workspace_guardrails.py` — new. `test_mcp_server.py` — extended.
- `docs/STUDY_WORKSPACE.md` — new, documents the capability and its
  stated limitations, including the workspace_id access-control gap.
- `apps/api/pyproject.toml` — added `[tool.ruff.lint.isort]
  combine-as-imports = true` (needed for a clean single-statement
  aliased import in mcp_server.py).

## Validation evidence

`make check` passes in full, confirmed by Task 11's full run — every new
domain module's tests, the extended MCP-server tests, and the new
workspace guardrail suite, plus zero regressions in the pre-existing
119 API + 5 web tests. (158 API tests confirmed passing during Task 8's
review, before Task 11's final full-project run.)

## Known limits / explicit scope decisions

- **Charter rewrite is a separate, deliberate next task, not part of
  this work.** `docs/PROJECT_CHARTER.md`'s thesis and invariants I1, I2,
  I3, I5, I6 all need new language reflecting this second capability —
  the design doc lists exactly what changes for each. Per explicit
  product decision during brainstorming, the whole product was sketched
  first; formalizing the charter language comes next, informed by what
  actually got built here rather than speculatively beforehand.
- The ingestion-shape feasibility spike (how ChatGPT/Codex deliver real
  file-attachment content to a tool call) remains unresolved — this
  implementation ships with plain text as the best-guess parameter shape,
  matching how this project already handles the still-unverified
  MCP-connectivity spike (`docs/MCP_SERVER.md`).
- In-process storage only; no persistence across a process restart.
- No PDF/docx extraction; no "confirm anyway" override for flagged
  content; retrieval is keyword-only, not semantic.
- **`workspace_id` has no access control** (found during Task 7's code
  review, documented in `workspace_store.py` and `docs/STUDY_WORKSPACE.md`)
  — anyone who obtains a workspace_id has full read/destructive access.
  A capability-token scheme mirroring `challenge_token.py` is the natural
  fix, deferred as explicit future work.
- **Worktree note**: this worktree was created via `EnterWorktree`'s
  default `fresh` base-ref (origin/master), which was momentarily behind
  local master by 2 unpushed commits (the design doc and the plan doc)
  at creation time. Caught and fixed mid-implementation (after Task 8) by
  merging those two commits into the worktree branch — no functional
  impact since subagents retrieved the plan/design text via `git show`
  in the meantime, but worth remembering for future worktree creation:
  push pending commits before branching, or use `worktree.baseRef: head`.

## Blocker

None for what's built — independent of Phase 1's Canvas/institutional
questions and of the kill-ratio work in `apps/api/app/domain/kill_ratio.py`
(untouched by this work).

## Owner

Shared team.

## Next action

1. Rewrite `docs/PROJECT_CHARTER.md`'s thesis and I1/I2/I3/I5/I6 per the
   design doc's explicit list — this is the immediately next task.
2. Once a real ChatGPT/Codex session exists (same blocker as Phase 1
   spike 1/2), verify `add_course_material`'s actual parameter shape
   against real attachment delivery and adjust if the best-guess plain-
   text shape turns out wrong.
3. Consider a persistence layer, PDF extraction, a flagged-content
   confirm-and-store-anyway flow, and a capability-token scheme for
   `workspace_id` (mirroring `challenge_token.py`) as explicit, separately
   -scoped follow-up work — not bundled into this slice.
