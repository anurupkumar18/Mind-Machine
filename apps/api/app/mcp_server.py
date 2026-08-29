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

from app.domain.challenge_token import InvalidTokenError, issue_token, verify_token
from app.domain.contracts import DiagnosisRequest
from app.domain.fixtures import fixture_data
from app.domain.runtime import canonical_next_frontier
from app.domain.sandbox import execute_repair
from app.domain.socratic import diagnose

KNOWN_CHALLENGES = {"traversal-invariant-02"}

mcp = MCPServer(
    name="evidence-engine",
    version="0.1.0",
    instructions=(
        "Evidence Engine issues verified code-reasoning practice challenges. "
        "Call start_challenge with a challenge_id to begin; it returns a "
        "challenge_token to pass to every subsequent tool call. Evidence "
        "comes from Evidence Engine's own execution, never from this tool's "
        "caller."
    ),
)


def _require_challenge_id(challenge_token: str) -> str:
    try:
        claims = verify_token(challenge_token)
    except InvalidTokenError as error:
        raise ValueError(f"Invalid challenge_token: {error}") from error
    return claims.challenge_id


@mcp.tool()
def start_challenge(challenge_id: str) -> dict[str, Any]:
    """Issue a challenge instance, its token, and starting trace metadata."""
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


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
