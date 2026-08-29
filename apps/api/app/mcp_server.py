"""Evidence Engine's MCP tool surface (docs/IMPLEMENTATION_PLAN.md §3.2).

The four workflow tools, each backed by the opaque signed challenge token
issued by `start_challenge`: `submit_prediction`, `submit_diagnosis`, and
`submit_repair` all take a `challenge_token`, never a raw challenge_id,
and verify it before acting. `submit_repair` is the only one that
triggers real sandboxed execution (I8), via `app.domain.sandbox`.

Known simplification, stated explicitly: token verification only checks
signature validity and extracts `challenge_id` -- it does not yet enforce
tool-call ordering (nothing stops calling `submit_repair` before
`submit_prediction`). Nothing in the current design depends on that
ordering for correctness, but a real workflow-integrity story may want it.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from mcp.server.mcpserver import MCPServer

from app.domain.canvas_mock import mock_course_context
from app.domain.challenge_token import InvalidTokenError, issue_token, verify_token
from app.domain.contracts import CourseTopicsResponse, DiagnosisRequest
from app.domain.fixtures import fixture_data
from app.domain.ingestion import ingest_material
from app.domain.retrieval import keyword_search
from app.domain.runtime import canonical_next_frontier
from app.domain.sandbox import execute_repair
from app.domain.socratic import diagnose
from app.domain.topic_matching import (
    NoMatchingChallengeError,
    match_topics,
    resolve_challenge_for_topic,
)
from app.domain.workspace_store import (
    UnknownMaterialError,
    UnknownWorkspaceError,
    all_chunks,
    list_materials,
)
from app.domain.workspace_store import (
    delete_workspace as delete_workspace_chunks,
)
from app.domain.workspace_store import (
    remove_material as remove_material_chunks,
)

KNOWN_CHALLENGES = {"traversal-invariant-02"}

mcp = MCPServer(
    name="evidence-engine",
    version="0.1.0",
    instructions=(
        "Evidence Engine issues verified code-reasoning practice challenges. "
        "Optionally call list_course_topics first to see what the (mock) "
        "connected course covers and get a matching topic. Call "
        "start_challenge with either a challenge_id or a topic to begin; it "
        "returns a challenge_token to pass to every subsequent tool call. "
        "Evidence comes from Evidence Engine's own execution, never from "
        "this tool's caller. Separately, a student study workspace lets a "
        "student add their own course materials (add_course_material), "
        "review or remove them (list_workspace_materials, remove_material, "
        "delete_workspace), and ask questions about them "
        "(answer_from_materials) -- this workspace answers directly, "
        "unlike the non-evaluative code-repair coaching above."
    ),
)


def _require_challenge_id(challenge_token: str) -> str:
    try:
        claims = verify_token(challenge_token)
    except InvalidTokenError as error:
        raise ValueError(f"Invalid challenge_token: {error}") from error
    return claims.challenge_id


@mcp.tool()
def list_course_topics() -> dict[str, Any]:
    """List the (mock) connected course's module/topic titles and which
    have a matching practice challenge today.

    Backed by fixture data, not a real Canvas connection -- real Canvas
    access is gated behind confirmed institutional approval (I4) and not
    yet available. See docs/CANVAS_INTEGRATION.md.
    """
    context = mock_course_context()
    response = CourseTopicsResponse(
        course_name=context.course_name,
        syllabus_body=context.syllabus_body,
        topics=match_topics(context),
    )
    payload = response.model_dump()
    payload["trace"] = {"stage": "planner", "tool": "list_course_topics"}
    return payload


@mcp.tool()
def start_challenge(challenge_id: str | None = None, topic: str | None = None) -> dict[str, Any]:
    """Issue a challenge instance, its token, and starting trace metadata.

    Exactly one of challenge_id or topic must be given. topic resolves to
    a challenge_id via the same keyword-overlap matcher list_course_topics
    uses (app.domain.topic_matching); see docs/CANVAS_INTEGRATION.md.
    """
    if (challenge_id is None) == (topic is None):
        raise ValueError("Provide exactly one of challenge_id or topic")
    if topic is not None:
        try:
            challenge_id = resolve_challenge_for_topic(topic)
        except NoMatchingChallengeError as error:
            raise ValueError(str(error)) from error
    assert challenge_id is not None

    if challenge_id not in KNOWN_CHALLENGES:
        raise ValueError(f"Unknown challenge id: {challenge_id!r}")

    data = fixture_data()
    frontier, _visited = canonical_next_frontier()
    return {
        "challenge_id": challenge_id,
        "challenge_token": issue_token(challenge_id),
        "objective": data["objective"],
        "start_node": data["start"],
        "expected_first_frontier": frontier,
        "trace": {"stage": "planner", "tool": "start_challenge"},
    }


@mcp.tool()
def submit_prediction(challenge_token: str, predicted_frontier: list[str]) -> dict[str, Any]:
    """Record the student's state prediction. Deterministic, no model verdict."""
    _require_challenge_id(challenge_token)

    normalized = [node.strip().upper() for node in predicted_frontier if node.strip()]
    expected_frontier, observed_visited = canonical_next_frontier()
    return {
        "correct": normalized == expected_frontier,
        "expected_frontier": expected_frontier,
        "observed_visited": observed_visited,
        "trace": {"stage": "planner", "tool": "submit_prediction"},
    }


@mcp.tool()
def submit_diagnosis(challenge_token: str, diagnosis: str, attempt: int) -> dict[str, Any]:
    """Record the student's diagnosis and return Socratic coaching.

    Per I6, this never receives or returns the repair verdict or hidden
    test information -- only `submit_repair` does, and only after the
    student has actually submitted a repair attempt.
    """
    _require_challenge_id(challenge_token)

    response = diagnose(DiagnosisRequest(diagnosis=diagnosis, attempt=attempt))
    payload = response.model_dump()
    payload["trace"] = {"stage": "diagnostician", "tool": "submit_diagnosis"}
    return payload


@mcp.tool()
def submit_repair(challenge_token: str, repair_source: str) -> dict[str, Any]:
    """Execute a submitted repair in Evidence Engine's own sandbox (I8).

    Returns the signed evidence record. The host model can narrate this
    result; it cannot alter it, and never sees hidden test inputs or the
    reference implementation's source.
    """
    challenge_id = _require_challenge_id(challenge_token)

    record = execute_repair(challenge_id=challenge_id, repair_source=repair_source)
    payload = asdict(record)
    payload["status"] = record.status.value
    payload["trace"] = {"stage": "verifier", "tool": "submit_repair"}
    return payload


@mcp.tool()
def add_course_material(workspace_id: str, filename: str, text: str) -> dict[str, Any]:
    """Ingest one uploaded study material into a student's workspace.

    Part of the student study workspace capability -- distinct from the
    code-repair coaching tools above; see
    docs/superpowers/specs/2026-08-29-student-study-workspace-design.md.

    Takes already-extracted plain text, not a raw file. How ChatGPT/Codex
    actually deliver attachment content to a tool call is unverified
    against a real host session -- this is the design's best-guess shape,
    matching this repo's existing practice of shipping a spike's
    engineering half before its institutional/connectivity half is
    confirmed (see docs/MCP_SERVER.md).
    """
    result = ingest_material(workspace_id=workspace_id, filename=filename, text=text)
    payload = result.model_dump()
    payload["trace"] = {"stage": "workspace", "tool": "add_course_material"}
    return payload


@mcp.tool()
def list_workspace_materials(workspace_id: str) -> dict[str, Any]:
    """List the materials currently stored in a study workspace."""
    materials = list_materials(workspace_id)
    return {
        "workspace_id": workspace_id,
        "materials": [m.model_dump() for m in materials],
        "trace": {"stage": "workspace", "tool": "list_workspace_materials"},
    }


@mcp.tool()
def remove_material(workspace_id: str, filename: str) -> dict[str, Any]:
    """Delete one material from a study workspace."""
    try:
        remove_material_chunks(workspace_id=workspace_id, filename=filename)
    except UnknownMaterialError as error:
        raise ValueError(str(error)) from error
    return {
        "workspace_id": workspace_id,
        "filename": filename,
        "deleted": True,
        "trace": {"stage": "workspace", "tool": "remove_material"},
    }


@mcp.tool()
def delete_workspace(workspace_id: str) -> dict[str, Any]:
    """Delete an entire study workspace and everything stored in it."""
    try:
        delete_workspace_chunks(workspace_id)
    except UnknownWorkspaceError as error:
        raise ValueError(str(error)) from error
    return {
        "workspace_id": workspace_id,
        "deleted": True,
        "trace": {"stage": "workspace", "tool": "delete_workspace"},
    }


@mcp.tool()
def answer_from_materials(workspace_id: str, question: str) -> dict[str, Any]:
    """Retrieve cited excerpts from a workspace's materials for a question.

    Returns excerpts only -- the host model synthesizes the actual answer
    and must cite filename/location for each excerpt it uses; no
    inference happens in this tool.
    """
    if not all_chunks(workspace_id):
        return {
            "workspace_id": workspace_id,
            "question": question,
            "excerpts": [],
            "status": "no_materials",
            "trace": {"stage": "workspace", "tool": "answer_from_materials"},
        }

    excerpts = keyword_search(workspace_id=workspace_id, question=question)
    return {
        "workspace_id": workspace_id,
        "question": question,
        "excerpts": [e.model_dump() for e in excerpts],
        "status": "no_match" if not excerpts else "ok",
        "trace": {"stage": "workspace", "tool": "answer_from_materials"},
    }


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
