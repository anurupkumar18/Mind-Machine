# Shared memory index

## Loading budget

Load this index, the relevant semantic records, and one current episodic handoff. Do not load the entire history unless investigating a specific regression.

## Semantic records

- `semantic/architecture.md` — layer boundaries and module map
- `semantic/contracts.md` — public API and fixture contract

## Long-term records

- `long-term/public-data.md` — non-negotiable data boundary

## Current state (living summary — update this block whenever you close out an episodic record; do not just repoint below and leave this stale)

Evidence Engine (revision 8 of the plan) is an MCP server, target 4-tool surface `start_challenge`/`submit_prediction`/`submit_diagnosis`/`submit_repair` behind a signed challenge token, connected to a ChatGPT App and Codex plugin riding UofU's ChatGPT/Codex access. Core architectural fact: **verification runs inside Evidence Engine's own sandbox** (I8), never self-reported by the host model. Properties are a reviewed declarative DSL, never model-authored code. BKT is cut for now (heuristic stand-in, explicitly not a mastery estimate). Canvas is Core but hard-gated behind confirmed institutional approval. Full plan: `docs/IMPLEMENTATION_PLAN.md`. Invariants I1-I8: `docs/PROJECT_CHARTER.md`. Product framing: `docs/VISION.md`.

**Phase 1 (feasibility spikes, the blocking gate) — all four have a documented outcome**: spike 3 (trusted sandbox) passed — `apps/api/app/domain/sandbox.py`. Spike 2 (MCP connectivity) engineering-complete, institutionally open — `apps/api/app/mcp_server.py`, `docs/MCP_SERVER.md`; no Codex CLI or real ChatGPT workspace connection verified yet. Spike 4 (Canvas) confirmed blocked on institutional access with no self-service or policy bypass (personal tokens disabled, OAuth2 dev keys admin-only, Instructure's free trial discontinued) — `scripts/verify_canvas_access.py` ready, unused. Spike 1 (workspace admin) has candidate contacts identified (UofU's ChatGPT Edu includes Codex; AI Tool Form + named AI Office Leadership contacts in `docs/IMPLEMENTATION_PLAN.md` §9) but no outreach sent yet. Spikes 1 and 4 need a named human owner — not resolvable by engineering alone.

**Phase 2/3 (post-gate build) is well underway**: the property DSL (§3.1) is real — `apps/api/app/domain/properties.py` evaluates submitted output against a reference-oracle execution (not hand-authored golden values), wired into `sandbox.py`. A first AST mutation operator exists — `apps/api/app/domain/mutation.py` (comparison-operator replacement), proven to actually get killed by the property pipeline for the reference bfs implementation. **The full 4-tool MCP surface exists and runs end-to-end**: `apps/api/app/mcp_server.py` now has `start_challenge` (issues an opaque signed `challenge_token` — `apps/api/app/domain/challenge_token.py`, stateless per I5), `submit_prediction`, `submit_diagnosis` (I6-clean, no verdict/hidden-test fields), and `submit_repair` (real sandboxed execution, I8) — the whole predict→diagnose→repair→evidence loop verified over a real stdio subprocess, not just in-memory tests. **The I6/I7 guardrail eval suite now exists**: `apps/api/tests/test_guardrails.py` (29 tests) sweeps `start_challenge`/`submit_prediction`/`submit_diagnosis` across realistic and adversarial inputs and asserts no evidence-only field or hidden-content substring ever leaks — confirmed to have real teeth by deliberately injecting a leak and watching it fail before reverting. Phase 3's Definition of Done is essentially complete; the one remaining stated gap is tool-call-ordering enforcement on the token (nothing stops calling `submit_repair` first — not currently load-bearing for correctness). **The sandbox kernel is now proven to generalize, not just work for bfs by coincidence**: a hidden `(graph, start)` calling-convention coupling in `_run_oracle`/the runner template was found and fixed to generic `**kwargs`, and a second, structurally different challenge (`binary-search-invariant-01`, `fixtures/repos/public-search/binary_search.py`) was added at the sandbox/mutation/properties kernel level — 3/3 generated mutants killed by the real pipeline. Not yet wired through `app.mcp_server`'s `start_challenge` (still only knows the original challenge's objective/coaching content). Known simplifications elsewhere, stated not hidden: only one mutation-operator family, no kill-ratio filtering or equivalent-mutant tolerance (Phase 2, R1), no tool-call-ordering enforcement on the token. See `episodic/0019-*.md` through `0023-*.md`.

## Current handoff

- `episodic/0023-sandbox-generalization-second-challenge.md`
