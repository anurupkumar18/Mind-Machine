# Task handoff: automated equivalent-mutant detection

## Goal

`episodic/0025`'s own stated next action: automate the manual
differential-testing technique used to confirm a real equivalent mutant
(2000 randomized trials, hand-run and hand-interpreted), so future
survivors don't each need a bespoke investigation.

## Changed files

- `apps/api/app/domain/sandbox.py` — refactor + additions, all backward
  compatible (verified via the full existing 92-test regression suite
  before adding anything new):
  - `_run_in_subprocess` now takes `cases` as an explicit parameter
    instead of always reading `config.test_inputs` — `execute_repair`
    passes `config.test_inputs` itself; nothing about its behavior
    changed, this just makes the case list swappable.
  - New public `run_cases(challenge_id, repair_source, cases)`: runs
    arbitrary cases through the real sandbox (same denylist, rlimits,
    timeout as any submitted repair) and returns `list[CaseOutcome] |
    None` — `None` for anything that didn't reach a per-case result
    (unknown challenge, disallowed code, syntax error, process error,
    timeout). Deliberately less granular than `execute_repair`'s
    `EvidenceRecord` status (which stays as the API surface for actual
    submissions); this is the lower-level primitive both `execute_repair`
    and the new equivalence checker build on.
  - New public `run_oracle(challenge_id, case)` and
    `generate_random_case(challenge_id, rng)` — thin wrappers so
    `app.domain.equivalence` doesn't reach into `sandbox.py` internals
    directly.
  - `ChallengeConfig` gains `input_generator: Callable[[Random], dict]`.
    Implemented for both challenges: `_random_bfs_input` (1-6 nodes,
    random edges, every node has a graph-dict entry so no `KeyError`) and
    `_random_binary_search_input` (length 1-15, distinct sorted ints,
    target present ~50% of the time).
- `apps/api/app/domain/equivalence.py` — new. `check_equivalence
  (challenge_id, mutant_source, trials, seed) -> EquivalenceResult`.
  Generates `trials` random cases from a seeded RNG, runs the mutant
  against *all of them in one sandboxed subprocess call* (not one
  subprocess per trial — see performance note below), then compares each
  output against the oracle run directly in the trusted process (same
  pattern `execute_repair` already uses). `is_likely_equivalent` is true
  only if literally no mismatch was found across the trials actually run
  — explicitly a statistical check, not a proof, and the module docstring
  says so.
- `apps/api/tests/test_sandbox_run_cases.py` — 4 tests for the new
  `run_cases` primitive directly.
- `apps/api/tests/test_equivalence.py` — 5 tests: the confirmed equivalent
  mutant is reported equivalent (300 trials), a confirmed real bug is
  reported not-equivalent with mismatch evidence, the unmutated reference
  is equivalent to itself (a necessary sanity check — a checker that
  couldn't recognize identity would be broken), same-seed determinism,
  disallowed code reported not-equivalent rather than crashing.
- `docs/IMPLEMENTATION_PLAN.md` — R1 row in the risk register updated.

## Validation evidence

`make check` passes in full: 97 API tests (was 92 after the `run_cases`
refactor, 88 before it), both lints, both typechecks, web tests, smoke.
Manually reran the divisor-mutation-to-1 mutant at the original 2000-trial
scale (matching `episodic/0025`'s manual investigation exactly) through
the new automated checker: `is_likely_equivalent: True, trials: 2000,
mismatches: 0` — same conclusion the hand investigation reached,
reproduced automatically.

**Performance**: the full `test_equivalence.py` suite (800 total trials
across 5 tests) runs in 0.31s, because every trial for a given mutant
batches into one subprocess call via the refactored `run_cases`, not one
subprocess per trial. Spawning a subprocess per trial (the naive
approach) would have cost roughly 50-100ms × trial count — the 2000-trial
manual check alone would have taken minutes, not been practical to run
routinely. This batching is why automating this was worth doing now
rather than leaving it as "just call execute_repair in a loop."

## Known limits / explicit scope decisions

- Still statistical, not a proof. Explicitly documented in the module
  docstring: a mutant with a narrow edge case unlikely to be hit by random
  generation could be misclassified as equivalent. More trials narrow
  this risk, they don't eliminate it. This is an accepted, stated
  limitation, not a gap to silently ignore.
- Random input generators exist for both current challenges but aren't
  validated against any notion of "realistic" distribution beyond basic
  structural validity (no `KeyError`s, no obviously degenerate inputs).
  Authoring a new challenge means authoring a new generator by hand — no
  automatic derivation from a challenge's test_inputs shape.
- This gives a signal (equivalent vs. not), not a *policy*. Nothing yet
  decides what to actually do with that signal — e.g., should a
  content-generation pipeline discard likely-equivalent mutants
  automatically, flag them for human review, or something else. That's
  real remaining Phase 2/7 work.
- `run_cases`'s collapsed `None` return (for disallowed code, syntax
  errors, process errors, and timeouts all alike) means
  `check_equivalence` can't currently distinguish "this mutant is
  malicious/broken" from "this mutant timed out" from "this mutant has a
  syntax error" — all three just report `is_likely_equivalent: False,
  trials_run: 0`. That's a reasonable simplification for equivalence
  checking specifically (none of those states looks equivalent to a
  working reference), but would need more detail for other use cases.

## Blocker

None — independent of Phase 1's open institutional questions.

## Owner

Shared team.

## Next action

Kill-ratio *policy*: decide what a content pipeline should actually do
with `classify_mutant` + `check_equivalence`'s combined signal (e.g., a
survived mutant that's also flagged `is_likely_equivalent` is a strong
equivalent-mutant candidate for automatic exclusion from curated content;
a survived mutant that's *not* flagged equivalent is a real test-coverage
gap worth investigating, the same distinction made by hand in
`episodic/0025`). Separately, still open and independent: a third
mutation-operator family, or wiring `binary-search-invariant-01` through
`app.mcp_server` (deferred again — genuinely requires content-design
judgment about what "prediction" means for a non-graph-traversal
challenge, not just mechanical parameterization; worth flagging to the
team as needing a real content-design decision rather than continuing to
defer it as if it were equally well-scoped engineering work).
