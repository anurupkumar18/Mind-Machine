# Task handoff: correct kill/survived classification + real equivalent-mutant finding

## Goal

`episodic/0024` produced the kernel's first genuinely mixed mutant
dataset (7/12 killed on binary_search's constant mutants) and named this
as the natural next step: investigate the survivors to distinguish
genuine equivalent mutants from real test-input-set gaps — the
"equivalent-mutant tolerance" work item §6 Phase 2 names, until now
entirely unstarted.

## What was found

The ad hoc "is this mutant killed" checks used across
`test_mutation.py`/`test_mutation_constants.py`
(`status == "completed" and any(not passed)`) were wrong in a way that
undercounted kills: a mutant that crashes (`status: errored`) or hangs
(`status: timed_out`) is not "surviving" — it's failing differently, and
should count as killed. Recomputing binary_search's 15 mutants (3
comparison + 12 constant) with a corrected definition gives **12/15
killed**, not 7/12 — the earlier number was an artifact of the buggy
check, not a smaller real kill count.

Investigated the 3 genuine survivors individually:
- **`// 2` -> `// 1`** (`mid = (low + high) // 1`): ran 2000 randomized
  trials against the reference implementation — 0 mismatches. This
  mutation degenerates the algorithm into an exhaustive top-down linear
  scan that happens to always produce the same input/output result as
  real binary search (just O(n) instead of O(log n)). No test-input set
  could ever kill it under `output_equals_reference`, because by that
  property's definition it isn't wrong. **This is a confirmed, real
  equivalent mutant** — the first one this project has actually found and
  proven, not just discussed as a hypothetical category.
- **`mid - 1` -> `mid - 2`**: skips checking index `mid - 1` entirely.
  Confirmed a genuine bug: `binary_search([1..7], target=3)` returns `-1`
  instead of `2`. A real test-coverage gap, not equivalence.
- **`mid - 1` -> `mid - 0`** (i.e. `high = mid`): can infinite-loop —
  confirmed by hand-tracing `binary_search([5, 10], target=1)` (low/high
  converge to the same value and never change again) and by a randomized
  trial script that itself hung and had to be killed. Also a real gap.

## Changed files

- `apps/api/app/domain/kill_ratio.py` — new. `classify_mutant(record) ->
  "killed" | "survived"`. Survived requires `status == COMPLETED` *and*
  at least one property result *and* all of them passing — anything else
  (errored, timed out, rejected, or completed with zero properties
  evaluated) is killed.
- `apps/api/tests/test_kill_ratio.py` — 5 tests covering each branch of
  the classifier directly against constructed `EvidenceRecord`s.
- `apps/api/app/domain/sandbox.py` — `_BINARY_SEARCH_TEST_INPUTS` gains
  two hidden test cases: `{"sorted_values": [1,2,3,4,5,6,7], "target": 3}`
  (closes the `mid - 2` gap) and `{"sorted_values": [5, 10], "target": 1}`
  (closes the `mid - 0` gap; the correct reference implementation
  terminates fine on this input, only the buggy mutant hangs).
- `apps/api/tests/test_kill_ratio_binary_search.py` — new. Documents and
  verifies all three findings above with a module-scoped fixture (to
  avoid redundantly re-triggering the ~5s timeout hit three times).
- `apps/api/tests/test_mutation.py`, `test_mutation_constants.py` —
  refactored their own ad hoc killed-checks to use `classify_mutant`
  instead of duplicating the (buggy) inline logic.
- `docs/IMPLEMENTATION_PLAN.md` — R1 row in the risk register updated
  with the corrected numbers and the equivalent-mutant finding.

## Validation evidence

`make check` passes in full: 88 API tests (was 80), both lints, both
typechecks, web tests, smoke. The equivalent-mutant claim isn't just
asserted — it's backed by a 2000-trial randomized comparison against the
reference implementation (0 mismatches, run manually and reported
verbatim, not cherry-picked). The two closed gaps are each backed by a
hand-traced concrete counterexample before the fix, and a passing
regression test after. Full suite runtime went from ~5.6s to ~14s, almost
entirely from the new hang-detection test case correctly taking its
5-second sandbox timeout when run against the one mutant designed to
trigger it — a real cost of verifying real hang-safety, not test bloat
(a `pytest.fixture(scope="module")` avoids paying it more than once).

## Known limits / explicit scope decisions

- Equivalent-mutant *handling* is still manual investigation, not an
  automated mechanism. There's no code yet that detects "this mutant is
  equivalent" automatically (e.g., via randomized differential testing
  against the oracle) — a human (well, this session) did that analysis
  for one specific mutant. A real content pipeline authoring many
  challenges would want this automated, not investigated by hand each
  time.
- Kill-ratio *filtering* (deciding which mutants become curated practice
  content) still doesn't exist as code — this task produced an accurate
  kill/survived signal and one worked example of interpreting it, not a
  filtering pipeline.
- The bfs challenge's single comparison mutant was already killed under
  both the old and corrected classifier — this investigation is entirely
  about binary_search, which is now the more thoroughly exercised of the
  two challenges.

## Blocker

None — independent of Phase 1's open institutional questions.

## Owner

Shared team.

## Next action

With a correct classifier, a real confirmed equivalent mutant, and two
closed test-coverage gaps, reasonable next steps: automate equivalent-
mutant detection (differential testing against the oracle across
randomized inputs, the same technique used by hand here) rather than
requiring manual investigation per survivor; a third mutation-operator
family; or (unrelated) wiring `binary-search-invariant-01` through
`app.mcp_server`, still open since `episodic/0023`.
