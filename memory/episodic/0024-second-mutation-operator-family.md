# Task handoff: second mutation-operator family (integer-constant boundary)

## Goal

Add a second AST mutation-operator family (Phase 2, R1) before attempting
kill-ratio filtering — the existing single operator (comparison-operator
replacement) had only ever produced a 100%-kill dataset (1/1 on bfs, 3/3
on binary_search from `episodic/0023`), which gives filtering logic
nothing real to filter. Self-directed priority call, reasoning stated in
the prior turn's status update to the user.

## Changed files

- `apps/api/app/domain/mutation.py` — adds `generate_constant_mutants
  (source)`: walks `ast.Constant` nodes where `type(node.value) is int`
  (explicitly excluding `bool`, an `int` subclass in Python — `True`/
  `False` aren't boundary values in this sense) and produces two mutants
  per constant, `value+1` and `value-1`. Same `Mutant` dataclass and
  deterministic-hash-id pattern as the comparison operator.
- `apps/api/tests/test_mutation_constants.py` — new, 5 tests: mutant count
  and description content for a small synthetic source, bool-exclusion
  confirmed on a source mixing `True` with real int literals, parse
  validity, id uniqueness/determinism, and a real-pipeline kill check on
  binary_search.
- `docs/IMPLEMENTATION_PLAN.md` — R1 row in the risk register updated.

Also fixed a mypy failure this change surfaced: `ast.Constant.value`'s
declared type is a wide union (`str | int | float | bool | ... | None`),
so even though `_int_constant_nodes` already filters to real `int` values
at runtime, mypy couldn't narrow that across the function boundary. Added
an explicit `assert type(original_value) is int` at the point of use —
both a type-narrowing hint and a real runtime safety check, not just a
mypy workaround.

## Validation evidence

`make check` passes in full: 80 API tests (was 75), both lints, both
typechecks, web tests, smoke. Manually ran all 12 generated constant
mutants for `binary_search.py` through `execute_repair` and inspected
every result individually (not just the "at least one killed" assertion):
**7/12 killed**, including 2 that ended in `status: errored` rather than
`completed` (mutating the `// 2` divisor in `mid = (low + high) // 2`
turned out riskier/more failure-prone than the off-by-one shifts on
`mid + 1`/`mid - 1`). This is the first genuinely mixed result the kernel
has produced — real, useful signal, not a padded or cherry-picked number.

## Known limits / explicit scope decisions

- No investigation yet into *why* the 5/12 surviving mutants weren't
  killed — some may be genuine equivalent mutants (the value change
  happens not to affect output for these specific test inputs), others
  may indicate the current 3-case test-input set for binary_search is too
  narrow to catch everything a real kill-ratio filter would want caught.
  Distinguishing those two cases is exactly the "equivalent-mutant
  tolerance" work item §6 Phase 2 names, still unstarted.
- Still no kill-ratio *filtering* logic — nothing yet decides which
  mutants become curated practice content. This task's job was producing
  a dataset worth filtering, not building the filter.
- Two operator families now, still missing others a real catalog would
  want (boolean-connective swaps, off-by-one on loop bounds specifically
  rather than all integer literals, etc.).

## Blocker

None — independent of Phase 1's open institutional questions.

## Owner

Shared team.

## Next action

With a real mixed-result dataset now available (7/12 + 1/1 + 3/3 across
two operators and two challenges), the natural next step is finally
kill-ratio filtering / equivalent-mutant investigation (Phase 2, R1) —
look at the 5 surviving binary_search constant mutants specifically and
determine which are genuinely equivalent versus which expose a test-input
gap. Separately, still open and independent: a third mutation-operator
family, or wiring `binary-search-invariant-01` through `app.mcp_server`
(`episodic/0023`'s stated next action, still not done).
