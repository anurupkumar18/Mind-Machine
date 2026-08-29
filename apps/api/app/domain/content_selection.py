"""Kill-ratio filtering policy (docs/IMPLEMENTATION_PLAN.md §6, Phase 2, R1).

Combines app.domain.kill_ratio.classify_mutant (is this mutant actually
different from a legitimate repair?) and app.domain.equivalence's
statistical check (if it survived, is that because it's genuinely
equivalent, or because the test-input set has a gap?) into one decision
about whether a generated mutant is worth curating as practice content.

`decide` is the pure policy: given a kill outcome and (when relevant) an
equivalence result, what to do. `select_mutant` is the orchestration that
actually runs a mutant through the real sandbox and, only when needed,
the equivalence checker -- equivalence checking is skipped entirely for
killed mutants, since it's only meaningful for survivors.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.domain.equivalence import EquivalenceResult, check_equivalence
from app.domain.kill_ratio import MutantOutcome, classify_mutant
from app.domain.mutation import Mutant
from app.domain.sandbox import execute_repair

SelectionOutcome = Literal["accepted", "rejected_equivalent", "flagged_for_review"]


def decide(*, kill_outcome: MutantOutcome, equivalence_result: EquivalenceResult | None) -> SelectionOutcome:
    if kill_outcome == "killed":
        return "accepted"
    if equivalence_result is not None and equivalence_result.is_likely_equivalent:
        return "rejected_equivalent"
    return "flagged_for_review"


@dataclass(frozen=True)
class MutantSelectionDecision:
    mutant: Mutant
    kill_outcome: MutantOutcome
    equivalence_result: EquivalenceResult | None
    outcome: SelectionOutcome


def select_mutant(*, challenge_id: str, mutant: Mutant, equivalence_trials: int, seed: int) -> MutantSelectionDecision:
    record = execute_repair(challenge_id=challenge_id, repair_source=mutant.mutated_source)
    kill_outcome = classify_mutant(record)

    equivalence_result = None
    if kill_outcome == "survived":
        equivalence_result = check_equivalence(
            challenge_id=challenge_id, mutant_source=mutant.mutated_source, trials=equivalence_trials, seed=seed
        )

    outcome = decide(kill_outcome=kill_outcome, equivalence_result=equivalence_result)
    return MutantSelectionDecision(
        mutant=mutant, kill_outcome=kill_outcome, equivalence_result=equivalence_result, outcome=outcome
    )
