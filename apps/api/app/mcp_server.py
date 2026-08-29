"""Evidence Engine's MCP tool surface (docs/IMPLEMENTATION_PLAN.md §3.2).

Started as a Phase 1 spike (one tool, proving real protocol connectivity)
and now also carries `submit_repair`, the Phase 3 tool that triggers real
sandboxed execution (I8) via `app.domain.sandbox`. Still a known
simplification, stated explicitly: this does not yet implement the opaque
signed challenge token session (§3.2) -- tools take challenge_id directly
rather than an issued token, and `submit_prediction`/`submit_diagnosis`
don't exist yet. That's real remaining Phase 3 work.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from mcp.server.mcpserver import MCPServer

from app.domain.fixtures import fixture_data
from app.domain.runtime import canonical_next_frontier
from app.domain.sandbox import execute_repair

KNOWN_CHALLENGES = {"traversal-invariant-02"}

mcp = MCPServer(
    name="evidence-engine",
    version="0.1.0",
    instructions=(
        "Evidence Engine issues verified code-reasoning practice challenges. "
        "Call start_challenge with a challenge_id to begin. Evidence comes "
        "from Evidence Engine's own execution, never from this tool's caller."
    ),
)


@mcp.tool()
def start_challenge(challenge_id: str) -> dict[str, Any]:
    """Issue a challenge instance and its starting trace metadata."""
    if challenge_id not in KNOWN_CHALLENGES:
        raise ValueError(f"Unknown challenge id: {challenge_id!r}")

    data = fixture_data()
    frontier, _visited = canonical_next_frontier()
    return {
        "challenge_id": challenge_id,
        "objective": data["objective"],
        "start_node": data["start"],
        "expected_first_frontier": frontier,
        "trace": {"stage": "planner", "tool": "start_challenge"},
    }


@mcp.tool()
def submit_repair(challenge_id: str, repair_source: str) -> dict[str, Any]:
    """Execute a submitted repair in Evidence Engine's own sandbox (I8).

    Returns the signed evidence record. The host model can narrate this
    result; it cannot alter it, and never sees hidden test inputs or the
    reference implementation's source.
    """
    record = execute_repair(challenge_id=challenge_id, repair_source=repair_source)
    payload = asdict(record)
    payload["status"] = record.status.value
    payload["trace"] = {"stage": "verifier", "tool": "submit_repair"}
    return payload


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
