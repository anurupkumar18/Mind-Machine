# Task handoff: External review, revision 8

## Goal

Incorporate an external technical review of the merged revision-7 plan
(PR #1/#2). The review's central finding: verification was self-reported by
the host platform (ChatGPT/Codex ran tests, we validated the shape of its
report, not that execution happened) — undermining invariant I2. Worked
through the review's other nine points with the owner via targeted Q&A,
biased toward keeping the existing plan except where a critique was strong
enough to survive scrutiny or was explicitly agreed to.

## Changed files

- `docs/PROJECT_CHARTER.md` — invariants table now I1-I8; I8 is new (signed,
  sandboxed evidence record); I1/I4/I6 narrowed and strengthened; I3/I5
  reworded for precision (no per-student LLM cost ≠ no infrastructure; no
  separate Evidence Engine login ≠ no login anywhere in the flow).
- `docs/VISION.md` — corrected overstated claims throughout ("structurally
  impossible to leak" → hidden tests never exposed to the coaching model;
  "never repeats" → repetition minimized, tracked locally; "no login/
  install" → no separate Evidence Engine account; "zero incremental cost"
  → no per-student LLM cost, sandbox/hosting cost is ours); BKT moved from
  Core to explicitly deferred; Canvas scope tier narrowed.
- `docs/IMPLEMENTATION_PLAN.md` — revision 8: redesigned architecture
  (server-side verification sandbox, declarative property DSL replacing
  free-form model-authored test code, 4-tool consolidated MCP surface with
  signed challenge tokens and trace metadata), Canvas institutional-approval
  gate formalized as a Phase 1 blocker, BKT replaced with a transparent
  practice-selection heuristic, phases resequenced to put feasibility
  spikes before deep build), risk register and open questions updated
  (two new highest-priority risks: sandbox build effort, UofU workspace
  admin approval uncertainty).
- `AGENTS.md` — invariants list updated to I1-I8 matching the charter.
- `README.md` — language corrections matching VISION.md; status section
  points at the new Phase 1 feasibility-spike gate.
- `memory/INDEX.md` — current-state summary rewritten for revision 8;
  handoff pointer updated to this record.

## Validation evidence

`python3 scripts/memory_check.py` run after this record and the INDEX update
landed together (the staleness check requires this file to exist and be
named in INDEX.md's current-handoff pointer before it passes).

## Constraints and risks

This handoff is planning/documentation only — no code for the sandbox,
the property DSL, or the 4-tool MCP surface has been written yet. The
architecture described here (server-side sandbox execution) is a real,
non-trivial infrastructure commitment that revision 7 didn't have; see
`docs/IMPLEMENTATION_PLAN.md` §8 (R10, R11) for the two highest-priority
unknowns this introduces — neither has an owner yet.

## Blocker

Phase 1's four feasibility spikes (UofU workspace admin approval, one real
MCP tool invocation, a trusted-sandbox proof-of-concept, Canvas institutional
data-policy decision) are a blocking gate before Phase 2 build-out starts.
None have been run yet; R11 (workspace admin approval) is flagged as the
single highest-priority unknown in the plan.

## Owner

Shared team; `docs/IMPLEMENTATION_PLAN.md` §10 needs names against the
sign-off roles, including a new "sandbox/infra owner" role this revision
added.

## Next action

Run Phase 1's four feasibility spikes. Do not start Phase 2 (the mutation
pipeline / sandbox build-out) until they've resolved — a failure on any of
them changes scope or approach, per revision 8's explicit design.
