from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class PolicyMode(StrEnum):
    NO_CODE_HELP = "no_code_help"
    HINTS_ONLY = "hints_only"


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


class RepairResponse(BaseModel):
    accepted: bool
    tests_passed: bool
    result: str
    evidence_type: str = "mutation_repair"


class SocraticStage(StrEnum):
    READ = "read"
    ASSESS = "assess"
    GUIDE = "guide"
    ADAPT = "adapt"
    CONFIRM = "confirm"


class DiagnosisRequest(BaseModel):
    diagnosis: str
    attempt: int = Field(ge=1, le=3)


class SocraticResponse(BaseModel):
    accepted: bool
    stage: SocraticStage
    scaffold_level: int
    observation: str
    question: str


class ConfirmationRequest(BaseModel):
    repair_timing: str


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


class PropertySpec(BaseModel):
    """A declarative property selection -- never executable code (§3.1).

    Only ``property`` names present in `app.domain.properties`'s catalog
    are meaningful; unrecognized names fail evaluation rather than
    silently passing or running arbitrary code.
    """

    function: str = Field(min_length=1)
    property: str = Field(min_length=1)
    oracle: str = Field(min_length=1)
    arguments: list[str] = Field(default_factory=list)


class PropertyCheckResult(BaseModel):
    passed: bool
    detail: str


class CanvasModule(BaseModel):
    id: int
    name: str


class CanvasCourseContext(BaseModel):
    course_name: str
    syllabus_body: str
    modules: list[CanvasModule]


class TopicMatch(BaseModel):
    module_name: str
    matched_challenge_id: str | None
    matched_terms: list[str]


class CourseTopicsResponse(BaseModel):
    course_name: str
    syllabus_body: str
    topics: list[TopicMatch]
