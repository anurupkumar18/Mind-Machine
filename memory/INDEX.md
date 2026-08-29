# Shared memory index

## Loading budget

Load this index, the relevant semantic records, and one current episodic handoff. Do not load the entire history unless investigating a specific regression.

## Semantic records

- `semantic/architecture.md` — layer boundaries and module map
- `semantic/contracts.md` — public API and fixture contract

## Long-term records

- `long-term/public-data.md` — non-negotiable data boundary

## Current state (living summary — update this block whenever you close out an episodic record; do not just repoint below and leave this stale)

Evidence Engine (revision 8 of the plan) is an MCP server exposing 4 model-facing workflow tools (`start_challenge`, `submit_prediction`, `submit_diagnosis`, `submit_repair`) behind a signed challenge token, connected to a ChatGPT App and a Codex plugin riding the University of Utah's ChatGPT/Codex access. The key architectural fact this revision changed: **verification now runs inside Evidence Engine's own sandbox** (I8) — the host model no longer self-reports test results; an earlier design that let it do so was the finding of an external review and is corrected. Properties are expressed through a reviewed declarative DSL, never free-form model-authored code. Knowledge tracing (BKT) is cut for now — a transparent "recent success by skill tag" heuristic stands in, explicitly not a mastery estimate; real BKT is deferred to post-pilot. Canvas integration stays Core but is hard-gated behind confirmed UofU institutional data-policy approval, narrowed to syllabus/topic titles by default (no assignment/quiz/discussion content), with a client-side caching backup path bound by the same approval gate. We are at Phase 1 (feasibility spikes: workspace admin approval, MCP connectivity, trusted-sandbox proof-of-concept, Canvas institutional decision) — this is a blocking gate before deeper build. Full plan: `docs/IMPLEMENTATION_PLAN.md`. Invariants I1-I8: `docs/PROJECT_CHARTER.md`. Product framing: `docs/VISION.md`.

## Current handoff

- `episodic/0014-external-review-revision-8.md`
