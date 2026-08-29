# Task handoff: Phase 2 kernel (property DSL) + Phase 3 first tool (submit_repair)

## Goal

Start Phase 2 (trusted challenge kernel, `docs/IMPLEMENTATION_PLAN.md` §6)
by building the declarative property DSL §3.1 actually commits to, since
the Phase 1 sandbox spike (`episodic/0015`) used a golden-expected-output
model that doesn't generalize to procedurally mutated variants. Then close
the gap identified in the retrospective before this task: the MCP server
(spike 2, `episodic/0016`) and the sandbox kernel (spike 3, `episodic/0015`)
were built and tested independently but never wired together.

## Changed files

- `apps/api/app/domain/contracts.py` — adds `PropertySpec` (function,
  property, oracle, arguments — all plain strings, never executable code)
  and `PropertyCheckResult`.
- `apps/api/app/domain/properties.py` — new. The property evaluator
  catalog: `output_equals_reference` and `output_is_permutation`, matching
  §3.1's own literal example. `evaluate_property(spec, submitted_output,
  reference_output)` raises `UnknownPropertyError` rather than silently
  passing on an unrecognized property name.
- `apps/api/tests/test_properties.py` — 7 tests, TDD.
- `apps/api/app/domain/sandbox.py` — reworked `execute_repair`'s internals:
  the sandboxed subprocess now only executes the *submitted* repair and
  reports raw outputs (no more `expected` values baked into hidden-test
  fixtures); the reference oracle (`fixtures/repos/public-graph-traversal/
  bfs.py`) runs directly in the trusted parent process (it's our own
  reviewed code, not student input, so it doesn't need sandboxing); the two
  outputs are compared via `evaluate_property`. Public signature and
  black-box behavior (known-good passes, known-bad fails, signed record)
  unchanged — internals are what moved from hardcoded values to real
  oracle execution. `_CHALLENGES` is now a small `ChallengeConfig` registry
  (entry point, oracle path, test inputs, property spec) instead of a bare
  set of IDs.
- `apps/api/tests/test_sandbox.py` — 2 new tests confirming property
  results carry the DSL's property name and that failure detail cites the
  oracle mismatch; existing 7 tests unchanged and still passing.
- `apps/api/app/mcp_server.py` — adds `submit_repair(challenge_id,
  repair_source)`, wired to `sandbox.execute_repair`. This is the tool
  §3.2 calls out as "the only tool that triggers real sandboxed execution."
  Explicit, stated simplification: no opaque signed challenge token yet —
  `submit_repair` takes `challenge_id` directly, and
  `submit_prediction`/`submit_diagnosis` don't exist. That's real
  remaining Phase 3 scope, not silently assumed done.
- `apps/api/tests/test_mcp_server_repair.py` — 3 tests: tool discovery, a
  full call through the real MCP protocol returning a signed record with
  all properties passing for a known-good repair, and a disallowed-import
  repair reported as `rejected` rather than executed.
- `docs/IMPLEMENTATION_PLAN.md` — R1/R2 rows in the risk register updated.

## Validation evidence

`make check` passes in full: memory check, both lints, both typechecks,
30 API tests (was 18), 5 web tests, smoke. Beyond the automated in-memory-
stream MCP tests, manually re-verified end-to-end over a real stdio
subprocess (`uv run python3 -m app.mcp_server`, driven by
`mcp.client.stdio.stdio_client`): `start_challenge` then `submit_repair`
with a known-good repair returns `status: completed` and a real HMAC
signature. Manually confirmed the oracle-execution model is genuine (not
a relabeled golden-output check) by running a known-bad repair directly:
the failure detail shows `expected ['A', 'B', 'C', 'D'], got ['A', 'C',
'D', 'B']` — the expected value came from executing the reference
implementation on that call, not a hardcoded fixture value.

## Known limits / explicit scope decisions

- The property catalog has exactly two entries. Real content variety
  (Phase 7) needs more property types as new challenges are authored —
  adding one means writing and reviewing a new function in
  `properties.py`, never accepting one from a tool call.
- No AST mutation-operator library yet (R1) — this slice replaces
  hand-authored *expected outputs* with oracle execution, which is the
  prerequisite for mutation testing to work at all, but doesn't yet
  generate mutated variants itself.
- `submit_repair` has no opaque signed challenge token / session state
  (§3.2). `submit_prediction` and `submit_diagnosis` don't exist. I6 (never
  exposing hidden tests/verdict to the coaching model before a repair
  attempt) has no enforcement mechanism yet since there's no multi-step
  session to enforce it across — that's what building the other three
  tools and the token would actually require.
- Still one hardcoded challenge (`traversal-invariant-02`). The
  `ChallengeConfig` registry is now structured to make adding a second
  challenge straightforward, but no second challenge has been authored.

## Blocker

None — this work doesn't depend on any of Phase 1's open institutional
questions (spikes 1 and 4).

## Owner

Shared team.

## Next action

Two reasonable next slices, roughly independent:
1. `submit_prediction` and `submit_diagnosis` tools plus the opaque signed
   challenge token / session state that threads a challenge instance
   across all four tool calls (§3.2) — needed before I6 has anything to
   actually enforce.
2. The AST mutation-operator library (§6 Phase 2, R1) — generate mutated
   variants of a reference implementation and classify them via the
   property DSL's known-good/known-bad test battery (Phase 2's other
   Definition-of-Done item, not yet attempted).
