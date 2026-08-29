"""Mutant classification (docs/IMPLEMENTATION_PLAN.md §6, Phase 2, R1).

A mutant "survives" only if it reaches `completed` and every property
passes -- the same bar a legitimate accepted repair would have to clear.
Anything else means the mutant was caught: a failing property, an error,
a timeout, or (degenerate but possible) no properties evaluated at all.
This is stricter than checking only `completed AND any(not passed)`,
which would wrongly call an errored or timed-out mutant a "survivor."
"""

from __future__ import annotations

from typing import Literal

from app.domain.sandbox import EvidenceRecord, ExecutionStatus

MutantOutcome = Literal["killed", "survived"]


def classify_mutant(record: EvidenceRecord) -> MutantOutcome:
    if record.status is not ExecutionStatus.COMPLETED:
        return "killed"
    if not record.property_results:
        return "killed"
    if all(result.passed for result in record.property_results):
        return "survived"
    return "killed"
