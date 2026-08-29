"""Automated equivalent-mutant detection (docs/IMPLEMENTATION_PLAN.md §6,
Phase 2, R1).

Generalizes the manual technique used to confirm a real equivalent mutant
(episodic/0025: 2000 randomized trials against the reference
implementation, 0 mismatches) into reusable code. This is a statistical
check, not a proof -- "likely equivalent" means no mismatch was found in
the trials actually run, not that none exists. A mutant with a narrow
edge case a random generator is unlikely to hit could still be
misclassified as equivalent; more trials narrow that risk, they don't
eliminate it.

Reuses the real sandbox (app.domain.sandbox.run_cases) to execute the
mutant, so the same isolation/denylist/timeout guarantees apply here as
to a real submitted repair -- this never runs untrusted code outside the
sandbox boundary.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

from app.domain.sandbox import generate_random_case, run_cases, run_oracle


@dataclass(frozen=True)
class Mismatch:
    case: dict[str, Any]
    mutant_output: Any
    reference_output: Any


@dataclass(frozen=True)
class EquivalenceResult:
    is_likely_equivalent: bool
    trials_run: int
    mismatches: list[Mismatch] = field(default_factory=list)


def check_equivalence(*, challenge_id: str, mutant_source: str, trials: int, seed: int) -> EquivalenceResult:
    rng = random.Random(seed)
    cases = [generate_random_case(challenge_id, rng) for _ in range(trials)]

    outcomes = run_cases(challenge_id=challenge_id, repair_source=mutant_source, cases=cases)
    if outcomes is None:
        # Didn't even run (disallowed code, syntax error, crash, timeout
        # across the whole batch) -- definitely not behaviorally
        # equivalent to a working reference implementation.
        return EquivalenceResult(is_likely_equivalent=False, trials_run=0, mismatches=[])

    mismatches = []
    for case, outcome in zip(cases, outcomes, strict=True):
        reference_output = run_oracle(challenge_id, case)
        if not outcome.ok or outcome.output != reference_output:
            mismatches.append(Mismatch(case=case, mutant_output=outcome.output, reference_output=reference_output))

    return EquivalenceResult(is_likely_equivalent=not mismatches, trials_run=trials, mismatches=mismatches)
