# Task handoff: Phase 3 — opaque signed challenge token + full 4-tool loop

## Goal

Close the last piece Phase 3's Definition of Done names
(`docs/IMPLEMENTATION_PLAN.md` §6): the opaque signed challenge token
(§3.2), the two missing tools (`submit_prediction`, `submit_diagnosis`),
and a genuine end-to-end predict→diagnose→repair→evidence loop.

## Changed files

- `apps/api/app/domain/challenge_token.py` — new. `issue_token(challenge_id)`
  / `verify_token(token)`. Stateless by design (I5: no server-side learner
  data store) — the token is a base64 JSON payload (challenge_id,
  session_id, issued_at) plus an HMAC-SHA256 signature, `payload.signature`.
  No session table anywhere; verification is pure signature/shape checking.
- `apps/api/tests/test_challenge_token.py` — 5 tests: round-trip,
  session-id uniqueness across issuances, tampered payload rejected,
  tampered signature rejected, malformed input rejected without crashing.
- `apps/api/app/mcp_server.py` — `start_challenge` now issues and returns
  `challenge_token`. Two new tools: `submit_prediction` (reuses the
  existing `canonical_next_frontier` domain logic from the pre-revision-8
  MVP) and `submit_diagnosis` (reuses the existing `socratic.diagnose`,
  also pre-existing). `submit_repair`'s parameter changed from
  `challenge_id` to `challenge_token` — a deliberate breaking change to
  match §3.2's actual tool surface, not an accidental one.
- `apps/api/tests/test_mcp_server.py`, `test_mcp_server_repair.py` —
  updated for the token-based contract; added a tampered-token-is-rejected
  test for `submit_repair`.
- `apps/api/tests/test_mcp_server_workflow.py` — new. The actual DoD test:
  one `challenge_token` carried through `start_challenge` →
  `submit_prediction` → `submit_diagnosis` → `submit_repair`, asserting
  each stage's trace metadata and, at the diagnosis stage, that I6 holds —
  no `tests_passed`, `property_results`, or `signature` field is present
  before a repair is actually submitted.
- `docs/IMPLEMENTATION_PLAN.md` — Phase 3's entry now has a Status line
  distinguishing what's actually done from what still isn't (the
  behavioral eval set, tool-call ordering enforcement).

## Validation evidence

`make check` passes in full: 42 API tests (was 35), both lints, both
typechecks, web tests, smoke. Beyond the automated in-memory-stream tests,
manually re-verified the entire loop over a real stdio subprocess (`uv run
python3 -m app.mcp_server`, driven by `mcp.client.stdio.stdio_client` —
the transport Codex CLI actually uses): all four tools listed, a token
issued by `start_challenge` accepted by all three subsequent calls, and
`submit_repair` returning `status: completed` for a known-good repair.
This is the same real-subprocess verification pattern used for spikes 2
and the earlier `submit_repair`-only wiring (`episodic/0016`,
`episodic/0019`) — not relying on the in-memory test shortcut alone.

## Known limits / explicit scope decisions

- Token verification checks signature validity and extracts
  `challenge_id` only. It does not enforce that tools are called in
  order — nothing currently stops a client from calling `submit_repair`
  first, skipping prediction/diagnosis entirely. Nothing about current
  correctness depends on that ordering (each tool is independently
  correct given a valid token), but a real workflow-integrity or
  analytics story might eventually want it enforced.
- I6 is verified for exactly one case (one diagnosis call, checking three
  field names are absent). The plan calls for "the answer-leakage/
  over-helping behavioral eval set" (I6, I7) — a real adversarial eval
  suite, not a single field-presence assertion. That's real remaining
  work, not something this task should be read as having completed.
- Session state genuinely doesn't exist server-side (I5 upheld) — but that
  also means nothing currently remembers *what* a student predicted or
  diagnosed by the time `submit_repair` runs. That's consistent with how
  the fixture's own domain logic already worked (each stage was always
  independently checkable against the fixture, not against prior
  answers), so this isn't a regression, but it's worth naming: the token
  binds calls to one challenge *instance*, not to a remembered
  conversation history.
- Still one hardcoded challenge, still `apps/api/app/domain/socratic.py`'s
  original fixture-driven coaching logic, unmodified — this task wired
  existing tested domain code into new MCP tools, it didn't rewrite that
  logic.

## Blocker

None — independent of Phase 1's open institutional questions.

## Owner

Shared team.

## Next action

The two Phase 3 DoD items still open: a real answer-leakage/over-helping
behavioral eval set (I6, I7) — likely a small adversarial prompt/response
corpus checked against `submit_diagnosis` and `submit_prediction`, not
just field-presence assertions — and a decision on whether tool-call
ordering needs enforcement. Separately, kill-ratio filtering and a second
mutation-operator family remain open from `episodic/0020` (Phase 2, R1),
and `submit_prediction`/`submit_diagnosis` review under I7's "any new tool
exposed to the host model must extend the guardrail test suite" hasn't
happened yet in any dedicated guardrail suite beyond what's in this task's
own tests.
