# Task handoff: real Codex CLI connectivity verified (Phase 1 spike 2, Codex half)

## Goal

Resolve the long-open "Codex CLI side unverified" half of Phase 1 spike 2
(`docs/IMPLEMENTATION_PLAN.md` §6, `docs/MCP_SERVER.md`) — the plan has
said since its early revisions that only the stdio-transport server side
was proven, never a real Codex client. This was driven by the account
holder wanting to actually try the product themselves after a session
building the student study workspace feature; a raw terminal REPL and
then a small local web page were built first for manual testing, and the
account holder then asked to try connecting Codex CLI for real.

## Changed files

- `docs/MCP_SERVER.md` — Status, "Connecting Codex CLI", and "Known
  limits" sections rewritten to reflect real verification and the exact
  reproducible commands. Also corrected a stale claim ("one tool,
  `start_challenge`") to the current 10-tool, two-capability reality.
- `scripts/try_it_yourself.py` (new, prior commit `b43fdfc`, fixed in
  `df005c6`) and `scripts/web_tester.py` (new, commit `41bf5ea`) — manual
  testing tools built earlier in this same session, ahead of the Codex
  verification below. Not re-described in full here; see their own
  docstrings and `docs/MCP_SERVER.md`.

## What was actually done (real actions, not simulated)

1. Installed Codex CLI globally: `npm install -g @openai/codex` (v0.151.0).
2. Confirmed it was already authenticated on this machine with a personal
   ChatGPT account (`codex doctor` → `auth is configured`, `stored auth
   mode: chatgpt`) — no login step needed, no UofU workspace involved.
3. Registered this repo's MCP server: `codex mcp add evidence-engine --
   uv run --directory <repo>/apps/api python3 -m app.mcp_server`. Verified
   via `codex mcp get evidence-engine` and confirmed no collision with the
   4 MCP servers already configured for this Codex install (`computer-use`,
   `node_repl`, `sites-design-picker`, `notion`, `openaiDeveloperDocs`).
4. Ran `codex exec --skip-git-repo-check --approve-for-me "<prompt asking
   it to call list_course_topics>"` — a real, non-interactive Codex
   session, using the actual `gpt-5.6-terra` model, actually invoked
   `list_course_topics` over the registered stdio transport and returned
   the real fixture payload (course name, syllabus body, four modules,
   the BFS module correctly matched to `traversal-invariant-02`).

First attempt (no `--approve-for-me`) failed with "MCP tool call requires
approval, but approval policy is never" — a real config-conflict finding,
not a connectivity failure: `codex exec`'s default approval policy
doesn't grant MCP tool-call approval non-interactively. `--approve-for-me`
(routes approval through automatic review under the workspace-write
sandbox) resolved it. A second attempt without `--approve-for-me` but
with an explicit tool-name prompt also failed (the model didn't attempt
the call at all that time) — noted as nondeterministic model behavior,
not investigated further since `--approve-for-me` reliably worked.

## Validation evidence

Real `codex exec` output (not paraphrased) included the tool payload
verbatim:
```json
{"course_name":"CS 3500 — Foundations of Software Engineering", ...,
"topics":[...,{"module_name":"Unit 3: Graph Traversal (BFS/DFS)",
"matched_challenge_id":"traversal-invariant-02","matched_terms":
["graph traversal","bfs"]},...]}
```
`make check` unaffected — no application code changed, only docs and two
standalone dev scripts already committed in prior turns this session.

## Known limits / explicit scope decisions

- This proves a **personal** Codex CLI can connect — it says nothing about
  UofU's institutional ChatGPT Edu/Codex workspace (R11, still open, still
  needs a named human owner to actually reach out per `episodic/0018`).
  Do not conflate "Codex CLI works" with "R11 is resolved."
- Tried once, non-interactively, on one machine. Not tried: interactive
  `codex` sessions, a student's own account, multiple tool calls in one
  session, the streamable-http/ChatGPT-App leg (still fully unverified).
- The unrelated `notion` MCP server (pre-existing on this Codex install,
  not part of this repo) threw an auth error on every run
  (`AuthRequiredError`) — cosmetic noise in the logs, unrelated to
  evidence-engine, not investigated or fixed (not this repo's server).

## Blocker

None for what was verified. R11 (institutional workspace approval) and
the streamable-http/ChatGPT-App leg remain open, same as before — this
closes a real but narrower gap (personal-account Codex CLI connectivity),
not the institutional one.

## Owner

Shared team. R11 outreach still needs a named owner (`episodic/0018`,
`episodic/0029` — unchanged by this).

## Next action

Update `docs/IMPLEMENTATION_PLAN.md` §6/§9's R11 risk-register entry to
note this personal-Codex-CLI data point exists, distinct from the
institutional question, the same way the Canvas mock-mode demo's entry
was annotated in `docs/IMPLEMENTATION_PLAN.md` §4/R5 (`episodic/0028`) —
not done in this handoff, flagged as a small follow-up for whoever picks
this up next.
