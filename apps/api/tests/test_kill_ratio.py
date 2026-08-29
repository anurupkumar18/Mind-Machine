"""Phase 2 (docs/IMPLEMENTATION_PLAN.md §6, Phase 2, R1): mutant
classification. A mutant "survives" only if it completes and every
property passes -- exactly the state a legitimate accepted repair would
be in. Anything else (a failing property, an error, a timeout) means the
mutant was caught in some way, so it counts as killed. The ad hoc
`status == "completed" and any(not passed)` checks used in
test_mutation.py/test_mutation_constants.py undercounted kills: a mutant
that crashes or hangs is not "surviving," it's failing differently."""

from __future__ import annotations

from app.domain.kill_ratio import classify_mutant
from app.domain.sandbox import EvidenceRecord, ExecutionStatus, PropertyResult


def _record(status: ExecutionStatus, property_results: list[PropertyResult]) -> EvidenceRecord:
    return EvidenceRecord(
        challenge_id="x",
        challenge_version="v1",
        code_hash="h",
        test_suite_version="v",
        runtime_digest="d",
        status=status,
        exit_status=0,
        property_results=property_results,
    )


def test_completed_with_all_properties_passing_survives() -> None:
    record = _record(ExecutionStatus.COMPLETED, [PropertyResult(name="p", passed=True, detail="")])

    assert classify_mutant(record) == "survived"


def test_completed_with_a_failing_property_is_killed() -> None:
    record = _record(
        ExecutionStatus.COMPLETED,
        [PropertyResult(name="p", passed=True, detail=""), PropertyResult(name="q", passed=False, detail="")],
    )

    assert classify_mutant(record) == "killed"


def test_errored_execution_is_killed_not_survived() -> None:
    record = _record(ExecutionStatus.ERRORED, [])

    assert classify_mutant(record) == "killed"


def test_timed_out_execution_is_killed_not_survived() -> None:
    """A mutant that hangs is caught, not passing -- the opposite of survival."""
    record = _record(ExecutionStatus.TIMED_OUT, [])

    assert classify_mutant(record) == "killed"


def test_completed_with_no_properties_at_all_is_killed() -> None:
    """No properties evaluated means nothing confirmed correctness --
    can't call that a survival."""
    record = _record(ExecutionStatus.COMPLETED, [])

    assert classify_mutant(record) == "killed"
