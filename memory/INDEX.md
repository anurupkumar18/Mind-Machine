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

**Phase 2/3 (post-gate build) is well underway.** Kernel (`apps/api/app/domain/`): `properties.py` (declarative DSL, §3.1, reference-oracle execution not hardcoded golden values) + `sandbox.py` (real isolated execution, I8, signed evidence records, plus the reusable `run_cases`/`run_oracle`/`generate_random_case` primitives) + `mutation.py` (two operator families) + `kill_ratio.py` (correct killed/survived classification) + `equivalence.py` (automated differential-testing equivalent-mutant detection, batched into one sandboxed subprocess call per check — not one per trial) are wired together and proven to generalize across two structurally different challenges (`traversal-invariant-02`/bfs, `binary-search-invariant-01`/binary search). One confirmed real equivalent mutant found and now auto-detected (`// 2` -> `// 1`, 2000 trials, 0 mismatches). MCP surface (`apps/api/app/mcp_server.py`): all 4 workflow tools exist behind a stateless signed `challenge_token` (I5), the full predict→diagnose→repair→evidence loop runs end-to-end verified over a real stdio subprocess, and the I6/I7 guardrail eval suite (`tests/test_guardrails.py`, confirmed to have real teeth) sweeps the pre-repair tools for leaks. Phase 3's DoD is essentially met. **The Phase 2 mutation pipeline is now complete end-to-end**: `app.domain.content_selection.select_mutant` combines classification and equivalence-checking into accept/reject/flag-for-review, run against binary_search's full 15-mutant set as a live sanity check (14 accepted, 1 correctly rejected as equivalent, 0 flagged — both real gaps were already closed in `episodic/0025`). Stated, not-hidden gaps: **only `traversal-invariant-02` is wired through the MCP layer** (the second challenge exists at the kernel level only — deliberately not forced through yet, since it needs real content-design judgment about what "prediction" means for a non-graph-traversal challenge, not just mechanical wiring, and this has now been deferred across several consecutive handoffs); the policy's `flagged_for_review` branch has no real example, only a unit test; still exactly two mutation-operator families; no tool-call-ordering enforcement on the token. Full history: `episodic/0019-*.md` through `0027-*.md`.

## Current handoff

- `episodic/0027-content-selection-policy.md`
