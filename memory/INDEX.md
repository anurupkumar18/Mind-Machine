# Shared memory index

## Loading budget

Load this index, the relevant semantic records, and one current episodic handoff. Do not load the entire history unless investigating a specific regression.

## Semantic records

- `semantic/architecture.md` — layer boundaries and module map
- `semantic/contracts.md` — public API and fixture contract

## Long-term records

- `long-term/public-data.md` — non-negotiable data boundary

## Current state (living summary — update this block whenever you close out an episodic record; do not just repoint below and leave this stale)

Evidence Engine (revision 8 of the plan) is an MCP server exposing 4 model-facing workflow tools (`start_challenge`, `submit_prediction`, `submit_diagnosis`, `submit_repair`) behind a signed challenge token, connected to a ChatGPT App and a Codex plugin riding the University of Utah's ChatGPT/Codex access. The key architectural fact this revision changed: **verification now runs inside Evidence Engine's own sandbox** (I8) — the host model no longer self-reports test results; an earlier design that let it do so was the finding of an external review and is corrected. Properties are expressed through a reviewed declarative DSL, never free-form model-authored code. Knowledge tracing (BKT) is cut for now — a transparent "recent success by skill tag" heuristic stands in, explicitly not a mastery estimate; real BKT is deferred to post-pilot. Canvas integration stays Core but is hard-gated behind confirmed UofU institutional data-policy approval, narrowed to syllabus/topic titles by default (no assignment/quiz/discussion content), with a client-side caching backup path bound by the same approval gate. We are at Phase 1 (feasibility spikes: workspace admin approval, MCP connectivity, trusted-sandbox proof-of-concept, Canvas institutional decision) — this is a blocking gate before deeper build. **Spike 3 (trusted-sandbox proof-of-concept) is done**: `apps/api/app/domain/sandbox.py` executes a submitted repair against one fixed challenge's hidden tests in an isolated subprocess (AST denylist gate, rlimits, timeout, no inherited env) and returns an HMAC-signed evidence record — proven against a known-good and a known-bad repair. Isolation is process-level, not container/VM-level, and is explicitly not production-grade (see the episodic record for the exact gaps). **Spike 2 (MCP connectivity) is engineering-complete, institutionally open**: `apps/api/app/mcp_server.py` exposes a real `start_challenge` tool, protocol-verified over in-memory streams (automated tests) and manually confirmed working end-to-end over both stdio (subprocess — Codex's transport) and streamable-http (ChatGPT's transport). See `docs/MCP_SERVER.md`. What's *not* proven: an actual Codex CLI install calling it (none on this machine) or an actual ChatGPT workspace connection (needs a public HTTPS deploy + institutional approval — spike 1). Spikes 1 and 4 remain open and need named human owners; none are resolvable by an engineering session alone. Full plan: `docs/IMPLEMENTATION_PLAN.md`. Invariants I1-I8: `docs/PROJECT_CHARTER.md`. Product framing: `docs/VISION.md`.

## Current handoff

- `episodic/0016-mcp-connectivity-spike.md`
