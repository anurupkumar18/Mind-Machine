from __future__ import annotations

from app.domain.contracts import EvidenceItem, EvidenceRequest, EvidenceResponse


def interpret_evidence(request: EvidenceRequest) -> EvidenceResponse:
    checks = [
        ("Predicted BFS frontier", request.prediction_correct),
        ("Preserved visited-set invariant", request.invariant_preserved),
        ("Handled cycle counterexample", request.cycle_counterexample_passed),
        ("Repaired controlled mutation", request.repair_passed),
        ("Scheduled targeted retry", request.retry_scheduled),
    ]
    items = [
        EvidenceItem(
            label=label,
            state="demonstrated" if passed else "needs evidence",
            detail="Observed through a deterministic fixture." if passed else "Complete the targeted retry.",
        )
        for label, passed in checks
    ]
    core_passes = sum(passed for _, passed in checks[:4])
    status = "Demonstrated" if core_passes == 4 else "Partially demonstrated" if core_passes >= 2 else "Needs evidence"
    next_action = "Retry the cycle-handling counterexample with a new graph." if core_passes < 4 else "Try a transfer graph with a different branching pattern."
    return EvidenceResponse(status=status, items=items, next_action=next_action)

