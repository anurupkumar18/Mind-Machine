from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.domain.contracts import (
    ChallengeCandidate,
    CheckpointRequest,
    CheckpointResponse,
    CodeContext,
    EvidenceRequest,
    EvidenceResponse,
    PredictionRequest,
    PredictionResponse,
    RepairRequest,
    RepairResponse,
)
from app.domain.interpretation import interpret_evidence
from app.domain.policy import select_coaching_card
from app.domain.repo_context import approved_context, curated_candidate
from app.domain.runtime import allowlisted_repair_passes, canonical_next_frontier

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
def repair(request: RepairRequest) -> RepairResponse:
    if request.repair_id != "mark_visited_on_enqueue":
        raise HTTPException(status_code=400, detail="Repair is not allowlisted for this fixture.")
    passed = allowlisted_repair_passes(request.repair_id)
    return RepairResponse(
        accepted=True,
        tests_passed=passed,
        result="Canonical traversal tests pass." if passed else "Canonical traversal tests failed.",
    )


@app.post("/evidence", response_model=EvidenceResponse)
def evidence(request: EvidenceRequest) -> EvidenceResponse:
    return interpret_evidence(request)
