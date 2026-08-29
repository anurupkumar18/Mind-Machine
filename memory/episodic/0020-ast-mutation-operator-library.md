# Task handoff: Phase 2 kernel — first AST mutation operator (R1)

## Goal

Build the AST mutation-operator library `docs/IMPLEMENTATION_PLAN.md` §6
Phase 2 calls for, and prove it actually classifies correctly through the
real sandbox+property pipeline — Phase 2's own remaining Definition of
Done item, not yet attempted before this task.

## Changed files

- `apps/api/app/domain/mutation.py` — new. `generate_comparison_mutants
  (source)` walks any Python source's `ast.Compare` nodes and produces one
  mutant per operator it can swap for a standard mutation-testing
  replacement (Eq<->NotEq, Lt<->GtE, Gt<->LtE, In<->NotIn, Is<->IsNot).
  Generic — not branching on which challenge or fixture the source came
  from, per `memory/semantic/architecture.md`'s module rule. Deliberately
  scoped to this one operator family; kill-ratio filtering and
  equivalent-mutant tolerance (also named in §6 Phase 2) are explicitly
  not implemented — a caller classifies a mutant by running its
  `mutated_source` through the existing `sandbox.execute_repair`, exactly
  as any submitted repair, and reading the property results.
- `apps/api/tests/test_mutation.py` — 5 tests, TDD. The two that matter
  most: a real mutant of the `traversal-invariant-02` reference
  implementation (`neighbor not in visited` -> `neighbor in visited`) is
  confirmed *killed* (a property actually fails) when run through the real
  sandbox+property-DSL pipeline, and the unmutated reference source is
  confirmed to pass as the known-good baseline. This is the literal
  "known-good/known-bad mutation-candidate test battery" Phase 2's DoD
  names — done for one operator, one challenge, not the full catalog.
- `docs/IMPLEMENTATION_PLAN.md` — R1 row in the risk register updated.

## Validation evidence

`make check` passes in full: 35 API tests (was 30), both lints, both
typechecks, web tests, smoke. Manually inspected the generated mutant for
the real fixture (`fixtures/repos/public-graph-traversal/bfs.py`): exactly
one mutant, `NotIn->In at compare #0.0`, matching the fixture's one
`if neighbor not in visited:` line — confirms the operator is walking real
AST structure, not hardcoded to expect a particular mutation.

## Known limits / explicit scope decisions

- One operator family (comparison-operator replacement). No boundary-value,
  arithmetic, or boolean-connective operators yet — real content variety
  (Phase 7, R1's "real iteration before the hackathon") needs more.
- No kill-ratio *filtering* — nothing yet decides "this mutant is too easy/
  hard/equivalent, discard it from the catalog." Right now every generated
  mutant is treated as a candidate; a real content pipeline needs to filter
  candidates by whether they're actually killed by the property set (this
  slice proves the classification mechanism works, not that filtering
  exists).
- No equivalent-mutant tolerance (§6) — a mutation that happens not to
  change observable behavior for the given test inputs would currently be
  silently treated as "survived" with no distinction from "the test suite
  is too weak." That distinction matters for a real catalog and isn't
  built yet.
- Still exercised against exactly one challenge/reference implementation.
  The mutation operator itself is generic; the test battery that exercises
  it is not yet run against anything else.

## Blocker

None — independent of Phase 1's open institutional questions.

## Owner

Shared team.

## Next action

Any of, roughly independent:
1. A second mutation operator family (boundary/arithmetic constants, or
   boolean connective swaps) to broaden coverage beyond comparisons.
2. Kill-ratio filtering: given a batch of generated mutants, decide which
   are useful practice content (killed by at least one property, not
   trivially equivalent) versus which to discard.
3. `submit_prediction`/`submit_diagnosis` + the opaque signed challenge
   token/session (§3.2) — the Phase 3 workflow-tool work identified as
   still open in `episodic/0019`, unrelated to mutation testing.
