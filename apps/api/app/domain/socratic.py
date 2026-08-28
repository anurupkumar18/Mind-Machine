"""Fixture-defined Socratic guidance with no persistence or answer generation."""

from __future__ import annotations

from typing import cast

from app.domain.contracts import DiagnosisRequest, SocraticResponse, SocraticStage
from app.domain.fixtures import fixture_value


def diagnose(request: DiagnosisRequest) -> SocraticResponse:
    runbook = cast(dict[str, object], fixture_value("diagnostic_runbook"))
    accepted = request.diagnosis == runbook["accepted_diagnosis"]
    if accepted:
        confirmation = cast(dict[str, str], runbook["confirmation"])
        return SocraticResponse(
            accepted=True,
            stage=SocraticStage.CONFIRM,
            scaffold_level=0,
            observation=confirmation["observation"],
            question=confirmation["question"],
        )

    scaffolds = cast(list[dict[str, str]], runbook["scaffolds"])
    scaffold = scaffolds[min(request.attempt, len(scaffolds)) - 1]
    return SocraticResponse(
        accepted=False,
        stage=SocraticStage.GUIDE if request.attempt == 1 else SocraticStage.ADAPT,
        scaffold_level=request.attempt,
        observation=scaffold["observation"],
        question=scaffold["question"],
    )
