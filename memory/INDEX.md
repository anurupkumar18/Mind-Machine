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

**Phase 2/3 (post-gate build) is well underway.** Kernel (`apps/api/app/domain/`): `properties.py` (declarative DSL, §3.1, evaluates against a reference-oracle execution, not hardcoded golden values) + `sandbox.py` (real isolated execution, I8, signed evidence records) + `mutation.py` (two operator families — comparison-operator replacement and integer-constant boundary — generating real mixed kill/survive results, not just 100%-kill) are wired together and proven to generalize across two structurally different challenges (`traversal-invariant-02`/bfs, `binary-search-invariant-01`/binary search), not just work by coincidence for the first one. MCP surface (`apps/api/app/mcp_server.py`): all 4 workflow tools exist (`start_challenge` issuing a stateless signed `challenge_token` — `challenge_token.py`, per I5 — then `submit_prediction`/`submit_diagnosis`/`submit_repair`), the full predict→diagnose→repair→evidence loop runs end-to-end verified over a real stdio subprocess, and the I6/I7 guardrail eval suite (`tests/test_guardrails.py`, 29 tests, confirmed to have real teeth) sweeps the pre-repair tools for leaks. Phase 3's DoD is essentially met. **Only `traversal-invariant-02` is wired through the MCP layer** — the second challenge exists at the kernel level only. **Kill-ratio classification is now correct and has produced a real result**: `app.domain.kill_ratio.classify_mutant` fixes an undercounting bug in the earlier ad hoc checks (an errored/timed-out mutant is killed, not surviving). Reclassified, binary_search is 12/15 killed; the 3 survivors were individually investigated — one is a **confirmed genuine equivalent mutant** (`// 2` -> `// 1`, proven via 2000 randomized trials with 0 mismatches against the reference, an O(n)-scan degenerate that can never be killed by more test cases), the other two were real test-input gaps, now closed with two added hidden test cases. Stated, not-hidden gaps: equivalent-mutant detection is still manual (this was one hand-investigated case, not an automated mechanism), no kill-ratio *filtering* pipeline yet, no tool-call-ordering enforcement on the token, `binary-search-invariant-01` still not wired through the MCP layer. Full history: `episodic/0019-*.md` through `0025-*.md`.

## Current handoff

- `episodic/0025-kill-ratio-classification-and-equivalent-mutant.md`
