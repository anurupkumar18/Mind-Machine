from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.domain.contracts import (
    ChallengeCandidate,
    CheckpointRequest,
    CheckpointResponse,
    CodeContext,
    ConfirmationRequest,
    DiagnosisRequest,
    EvidenceRequest,
    EvidenceResponse,
    PredictionRequest,
    PredictionResponse,
    RepairResponse,
    SocraticResponse,
)
from app.domain.interpretation import interpret_evidence
from app.domain.policy import select_coaching_card
from app.domain.repo_context import approved_context, curated_candidate
from app.domain.runtime import canonical_next_frontier, canonical_repair_confirmed
from app.domain.socratic import diagnose

app = FastAPI(title="Evidence Engine API", version="0.1.0")
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "persistence": "none"}


@app.get("/code-context/{repository_id}", response_model=CodeContext)
def code_context(repository_id: str) -> CodeContext:
    try:
        return approved_context(repository_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Repository is not an approved public fixture.") from error


@app.get("/challenge-candidates/{repository_id}", response_model=list[ChallengeCandidate])
def challenge_candidates(repository_id: str) -> list[ChallengeCandidate]:
    try:
        return [curated_candidate(approved_context(repository_id))]
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Repository is not an approved public fixture.") from error


@app.post("/checkpoint", response_model=CheckpointResponse)
def checkpoint(request: CheckpointRequest) -> CheckpointResponse:
    return CheckpointResponse(accepted=True, card=select_coaching_card(request.plan, request.policy_mode))


@app.post("/challenge/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest) -> PredictionResponse:
    expected_frontier, visited = canonical_next_frontier()
    return PredictionResponse(
        correct=request.predicted_frontier == expected_frontier,
        expected_frontier=expected_frontier,
        observed_visited=visited,
    )


@app.post("/challenge/repair", response_model=RepairResponse)
def repair(request: ConfirmationRequest) -> RepairResponse:
    passed = canonical_repair_confirmed(request.repair_timing)
    if not passed:
        raise HTTPException(status_code=400, detail="Confirmation does not preserve the fixture invariant.")
    return RepairResponse(
        accepted=True,
        tests_passed=passed,
        result="The canonical traversal tests pass after the confirmed conceptual repair.",
    )


@app.post("/challenge/diagnose", response_model=SocraticResponse)
def diagnosis(request: DiagnosisRequest) -> SocraticResponse:
    return diagnose(request)


@app.post("/evidence", response_model=EvidenceResponse)
def evidence(request: EvidenceRequest) -> EvidenceResponse:
    return interpret_evidence(request)
