# Shared memory index

## Loading budget

Load this index, the relevant semantic records, and one current episodic handoff. Do not load the entire history unless investigating a specific regression.

## Semantic records

- `semantic/architecture.md` — layer boundaries and module map
- `semantic/contracts.md` — public API and fixture contract

## Long-term records

- `long-term/public-data.md` — non-negotiable data boundary

## Current state (living summary — update this block whenever you close out an episodic record; do not just repoint below and leave this stale)

Evidence Engine is being rebuilt around: (1) an MCP server exposing a deterministic, verified practice-generation pipeline (invariant hypothesis → property-test validation → AST mutation synthesis → kill-ratio filtering → repair verification) plus a real Bayesian Knowledge Tracing model, never surfaced as a score; (2) two client surfaces — a ChatGPT App and a Codex plugin — both riding the University of Utah's existing Enterprise/Edu seats, so we never call an LLM ourselves; (3) read-only Canvas integration for course context. The standalone `apps/web`/`apps/api` deterministic BFS demo is being repurposed as an internal dev/QA harness and instructor-dashboard home, not a public product surface. Full plan, invariants (I1-I7), and phased tasks: `docs/IMPLEMENTATION_PLAN.md`. Product framing: `docs/VISION.md`. We are at the start of Phase 0/1 — see `docs/IMPLEMENTATION_PLAN.md` §6 for what's done vs. open.

## Current handoff

- `episodic/0013-hackathon-replan-and-implementation-plan.md`
