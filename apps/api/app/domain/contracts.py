from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class PolicyMode(StrEnum):
    NO_CODE_HELP = "no_code_help"
    HINTS_ONLY = "hints_only"
    BOUNDED_SNIPPETS = "bounded_snippets"


class PlanCommitment(BaseModel):
    objective: str = Field(min_length=8, max_length=300)
    strategy: str = Field(min_length=8, max_length=300)
    representation: str = Field(min_length=3, max_length=160)
    invariant: str = Field(min_length=8, max_length=300)
    complexity: str = Field(min_length=3, max_length=80)
    planned_tests: str = Field(min_length=8, max_length=300)


class CheckpointRequest(BaseModel):
    policy_mode: PolicyMode
    plan: PlanCommitment


class CoachingCard(BaseModel):
    id: str
    title: str
    misconception: str
    corrective_question: str
    hint: str | None = None
    snippet: str | None = None


class CheckpointResponse(BaseModel):
    accepted: bool
    card: CoachingCard


class PredictionRequest(BaseModel):
    predicted_frontier: list[str] = Field(min_length=1, max_length=8)

    @field_validator("predicted_frontier")
    @classmethod
    def normalize_nodes(cls, nodes: list[str]) -> list[str]:
        return [node.strip().upper() for node in nodes if node.strip()]


class PredictionResponse(BaseModel):
    correct: bool
    expected_frontier: list[str]
    observed_visited: list[str]
    evidence_type: str = "frontier_prediction"


class RepairRequest(BaseModel):
    repair_id: str


class RepairResponse(BaseModel):
    accepted: bool
    tests_passed: bool
    result: str
    evidence_type: str = "mutation_repair"


class EvidenceRequest(BaseModel):
    prediction_correct: bool
    invariant_preserved: bool
    cycle_counterexample_passed: bool
    repair_passed: bool
    retry_scheduled: bool


class EvidenceItem(BaseModel):
    label: str
    state: str
    detail: str


class EvidenceResponse(BaseModel):
    status: str
    items: list[EvidenceItem]
    next_action: str


class CodeReference(BaseModel):
    file: str
    start_line: int
    end_line: int


class ChallengeCandidate(BaseModel):
    objective_ref: str
    code_refs: list[CodeReference]
    template_id: str
    evidence_plan: list[str]
    rationale: str


class ChallengeTemplate(BaseModel):
    id: str
    allowed_inputs: list[str]
    runtime_variant: str
    verifier: str
    evidence_schema: list[str]


class CodeFile(BaseModel):
    path: str
    language: str
    symbols: list[str]
    line_count: int


class CodeContext(BaseModel):
    repository_id: str
    source: str
    files: list[CodeFile]
    excluded_files: list[str]
