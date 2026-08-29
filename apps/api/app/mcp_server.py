"""Phase 1 spike 2: a real MCP tool backed by Evidence Engine's domain logic.

Minimal scope on purpose: one tool, one fixed challenge, stdio transport.
Proves an MCP client can discover and invoke a tool that returns real,
fixture-grounded data through the actual MCP protocol -- not a stub. The
opaque signed challenge token and the full 4-tool workflow surface
(docs/IMPLEMENTATION_PLAN.md §3.2) are Phase 3 work, not this spike.
"""

from __future__ import annotations

from typing import Any

from mcp.server.mcpserver import MCPServer

from app.domain.fixtures import fixture_data
from app.domain.runtime import canonical_next_frontier

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


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
