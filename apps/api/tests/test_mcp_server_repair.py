"""Phase 3 (docs/IMPLEMENTATION_PLAN.md §3.2): submit_repair is the only
tool that triggers real sandboxed execution (I8). This wires the MCP
surface from Phase 1 spike 2 to the sandbox kernel from Phase 2 -- until
now the two were unconnected. Scoped simplification, stated explicitly:
this does not yet implement the opaque signed challenge token session
(§3.2's token issuance/validation) -- submit_repair takes challenge_id
directly. That's real remaining Phase 3 work, not silently assumed done.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import anyio
import pytest
from mcp import ClientSession
from mcp.shared.memory import create_client_server_memory_streams

from app.mcp_server import mcp

pytestmark = pytest.mark.anyio

GOOD_REPAIR = """
from collections import deque


def bfs(graph, start):
    frontier = deque([start])
    visited = {start}
    order = []
    while frontier:
        node = frontier.popleft()
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                frontier.append(neighbor)
    return order
"""


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@asynccontextmanager
async def connected_client() -> AsyncIterator[ClientSession]:
    async with create_client_server_memory_streams() as (client_streams, server_streams):
        server_read, server_write = server_streams
        client_read, client_write = client_streams

        async with anyio.create_task_group() as tg:
            tg.start_soon(
                mcp._lowlevel_server.run,
                server_read,
                server_write,
                mcp._lowlevel_server.create_initialization_options(),
            )
            async with ClientSession(client_read, client_write) as session:
                await session.initialize()
                yield session
            tg.cancel_scope.cancel()


async def test_submit_repair_tool_is_discoverable() -> None:
    async with connected_client() as session:
        tools = await session.list_tools()

    names = [tool.name for tool in tools.tools]
    assert "submit_repair" in names


async def test_submit_repair_returns_a_signed_evidence_record_via_the_real_sandbox() -> None:
    async with connected_client() as session:
        result = await session.call_tool(
            "submit_repair",
            {"challenge_id": "traversal-invariant-02", "repair_source": GOOD_REPAIR},
        )

    assert result.is_error is not True
    payload = json.loads(result.content[0].text)  # type: ignore[union-attr]
    assert payload["status"] == "completed"
    assert payload["signature"]
    assert all(item["passed"] for item in payload["property_results"])
    assert payload["trace"]["stage"] == "verifier"


async def test_submit_repair_with_disallowed_code_is_reported_not_executed() -> None:
    async with connected_client() as session:
        result = await session.call_tool(
            "submit_repair",
            {"challenge_id": "traversal-invariant-02", "repair_source": "import os\ndef bfs(g,s): return [s]"},
        )

    assert result.is_error is not True
    payload = json.loads(result.content[0].text)  # type: ignore[union-attr]
    assert payload["status"] == "rejected"
