# Task handoff: kill-ratio filtering policy — the mutation pipeline is now complete end-to-end

## Goal

`episodic/0026`'s stated next action: decide what to actually do with the
classification + equivalence signal, closing the last named piece of
Phase 2, R1's mutation-testing pipeline
(`docs/IMPLEMENTATION_PLAN.md` §6: "the AST mutation-operator library and
kill-ratio filtering").

## Changed files

- `apps/api/app/domain/content_selection.py` — new. `decide(kill_outcome,
  equivalence_result) -> "accepted" | "rejected_equivalent" |
  "flagged_for_review"`, the pure policy (module docstring states it
  explicitly): killed mutants are accepted outright; survived mutants
  confirmed equivalent are rejected; survived mutants *not* confirmed
  equivalent are flagged for human review rather than the code silently
  picking an interpretation — equivalence-checking is statistical
  (`episodic/0026`), so "survived and not confirmed equivalent" genuinely
  is ambiguous between "weak test coverage" and "equivalent mutant our
  random trials didn't happen to catch."
  `select_mutant(challenge_id, mutant, equivalence_trials, seed)` is the
  orchestration: runs the mutant through the real sandbox, classifies it,
  and — only for survivors, since it's meaningless for kills — runs the
  equivalence check. Returns an auditable `MutantSelectionDecision`
  carrying the mutant, the kill outcome, the equivalence result (if any),
  and the final decision, not just a bare verdict.
- `apps/api/tests/test_content_selection.py` — 6 tests. `decide` is unit-
  tested against constructed `EquivalenceResult`s covering all three
  branches, including "flagged_for_review," which no real mutant in the
  current dataset actually exercises (see Known limits). `select_mutant`
  is integration-tested against the two real branches that do have live
  examples: a real killed mutant (accepted, equivalence check correctly
  skipped) and the confirmed equivalent mutant from `episodic/0025`/`0026`
  (rejected, with the equivalence evidence attached).
- `docs/IMPLEMENTATION_PLAN.md` — R1 row in the risk register updated:
  the full pipeline this plan names is now real, not just its pieces.

## Validation evidence

`make check` passes in full: 103 API tests (was 97), both lints, both
typechecks, web tests, smoke. Ran the complete policy against
binary_search's real 15-mutant set (both operator families) as a final
end-to-end sanity check, not just the unit/integration tests: **14
accepted, 1 rejected_equivalent (the confirmed `// 2` -> `// 1` mutant),
0 flagged_for_review** — matching expectations exactly, since both real
test-coverage gaps found in `episodic/0025` were already closed by the
hidden test cases added there.

## Known limits / explicit scope decisions

- **`flagged_for_review` has no real example in the current dataset.**
  Both actual gaps this pipeline would have flagged were already fixed
  in `episodic/0025` before this policy existed to flag them — the
  pipeline's most interesting branch is only unit-tested against
  constructed inputs, never exercised end-to-end against a real generated
  mutant. Worth remembering: this branch is real code with real test
  coverage, but "have we actually seen it fire on real content" is a
  different, weaker claim than for `accepted`/`rejected_equivalent`.
- Only run against one challenge's mutant set (binary_search) as a live
  sanity check; bfs's single comparison mutant was already known-killed
  before this task, not independently re-verified through the full new
  pipeline in this task (though the underlying `classify_mutant` was
  already exercised against it in `episodic/0025`).
- This is a policy for *individual mutant* disposition, not a
  content-authoring pipeline. It doesn't decide how many accepted
  mutants a challenge needs, how to dedupe near-identical ones, or
  anything about presenting them as practice content (Phase 7 scope).
- Equivalence-checking trial counts (500 in the sanity run, matching what
  was used in `episodic/0025`/`0026`'s validation) are not tuned or
  justified by any formal confidence-interval reasoning — a round number
  that happened to be enough to reproduce the known result, not a derived
  parameter.

## Blocker

None — independent of Phase 1's open institutional questions.

## Owner

Shared team.

## Next action

With mutation generation → classification → equivalence-checking →
selection now a complete, tested pipeline, the highest-value next steps
are either: (1) apply it to a genuinely new mutant — ideally from a third
mutation-operator family, which would also finally give
`flagged_for_review` a real example to exercise if the new operator
produces a genuine test-coverage gap rather than another equivalent
mutant; or (2) step back from the mutation-testing kernel entirely and
address the two items that have now been deferred across several
consecutive handoffs: wiring `binary-search-invariant-01` through
`app.mcp_server` (needs real content-design judgment about prediction/
diagnosis semantics for a non-graph-traversal challenge, not pure
engineering — flagged repeatedly, still undecided) and tool-call-ordering
enforcement on the challenge token (low-priority, stated as not
load-bearing). Separately, unrelated to any of this: Phase 1 spikes 1 and
4 remain genuinely blocked on institutional outreach nobody has sent yet.
