# Task handoff: Phase 1 spike 3 — trusted execution sandbox PoC

## Goal

Prove the riskiest new infrastructure in `docs/IMPLEMENTATION_PLAN.md` (I8):
that Evidence Engine can execute a submitted repair against a fixed
challenge's hidden tests in an isolated subprocess and produce a signed
evidence record, before the mutation/property-DSL pipeline is built on top
of it. Phase 1, task 3 (`docs/IMPLEMENTATION_PLAN.md` §6).

## Changed files

- `apps/api/app/domain/sandbox.py` — `execute_repair(challenge_id, repair_source)`.
  Static denylist gate (AST-based; rejects imports outside a small allowlist
  and disallowed names like `os`, `subprocess`, `eval`, `exec`) runs before
  any execution. Passing code runs in a subprocess with CPU-time and
  (where the platform honors it) address-space rlimits, no inherited env,
  a temp cwd, and a hard wall-clock timeout. Result is an `EvidenceRecord`
  (challenge id+version, code hash, test-suite version, runtime digest,
  status, exit status, per-property results) signed with HMAC-SHA256.
- `apps/api/tests/test_sandbox.py` — 7 tests: known-good repair passes,
  known-bad repair (DFS-shaped bug) fails, signature verifies against a
  recomputed HMAC, code hash reflects the submitted source, a malicious
  `os.system` repair is rejected pre-execution, a syntax-error repair is
  reported as `errored` (not a crash), an unknown challenge id is rejected.

## Validation evidence

`make check` passes in full (memory check, both lints, both typechecks,
API pytest incl. the 7 new sandbox tests, web vitest, API smoke). Manual
run confirms a known-good repair produces `status=completed`, `exit_status=0`,
all three hidden cases passing, and a verifiable signature.

## Known limits of this PoC (explicitly not production-grade)

- Isolation is process-level (rlimits, denylist AST gate, no inherited env),
  not container/VM-level. `RLIMIT_AS` is silently skipped where the host OS
  won't honor it (confirmed on macOS in this dev environment) — CPU-time
  capping and the timeout still apply, but memory is not hard-capped there.
  Production execution needs real container/VM isolation with the network
  disabled at the OS level, not app-level rlimits alone.
- The static denylist gate is defense-in-depth, not the primary isolation
  mechanism — it can be bypassed by an obfuscated payload; the subprocess
  boundary and rlimits are what should hold if it is.
- Hidden tests and the challenge are hardcoded to the single fixed
  `traversal-invariant-02` bfs challenge, matching the spike's scope
  ("one fixed challenge's hidden tests against a known-good and a
  known-bad repair"). The property-DSL catalog (§3.1) that generalizes
  this to arbitrary challenges is unbuilt — that's Phase 2, not this spike.
- No MCP server or `submit_repair` tool wraps this yet (Phase 3). This is
  the kernel the tool will call, not the tool itself.

## Blocker

None for this spike — it is DoD-complete per §6 ("pass, fail, or
unresolved/gated" — this one is a pass: a fixed challenge with a known-good
and known-bad repair produces correct signed evidence records through a
real, isolated subprocess). The other three Phase 1 spikes (institutional
workspace-admin approval, live MCP tool invocation in ChatGPT/Codex, Canvas
sandbox key + data-policy answer) are still open and need named owners —
see `docs/IMPLEMENTATION_PLAN.md` §9. None of them are resolvable by an
engineering session alone.

## Owner

Shared team.

## Next action

Two independent paths, either can start now:
1. Take this kernel toward Phase 2 (§6): replace the hardcoded bfs hidden
   tests with the property-DSL catalog (§3.1) and curated reference
   implementations, add the AST mutation-operator library.
2. Pursue Phase 1 spike 2 (MCP connectivity) in parallel — get one real MCP
   tool invoked from the target ChatGPT workspace and from Codex — since it
   doesn't depend on this spike's outcome.
Spikes 1 and 4 (§9, R11 and R5) need a named human owner with an actual
UofU/Canvas contact; no amount of further engineering resolves them.
