"""Phase 3 DoD (docs/IMPLEMENTATION_PLAN.md §6): the full
predict->diagnose->repair->evidence loop, end to end, through the real
MCP protocol, using one challenge_token issued by start_challenge."""

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


def _payload(result: object) -> dict[str, object]:
    return json.loads(result.content[0].text)  # type: ignore[attr-defined,union-attr,no-any-return]


async def test_full_predict_diagnose_repair_evidence_loop() -> None:
    async with connected_client() as session:
        start_result = await session.call_tool("start_challenge", {"challenge_id": "traversal-invariant-02"})
        start_payload = _payload(start_result)
        token = start_payload["challenge_token"]
        assert start_payload["trace"]["stage"] == "planner"

        prediction_result = await session.call_tool(
            "submit_prediction", {"challenge_token": token, "predicted_frontier": ["B", "C"]}
        )
        prediction_payload = _payload(prediction_result)
        assert prediction_payload["correct"] is True
        assert prediction_payload["trace"]["stage"] == "planner"

        diagnosis_result = await session.call_tool(
            "submit_diagnosis",
            {"challenge_token": token, "diagnosis": "late_frontier_recognition", "attempt": 1},
        )
        diagnosis_payload = _payload(diagnosis_result)
        assert diagnosis_payload["accepted"] is True
        assert diagnosis_payload["trace"]["stage"] == "diagnostician"
        # I6: coaching never carries a verdict or hidden-test/repair information.
        assert "tests_passed" not in diagnosis_payload
        assert "property_results" not in diagnosis_payload
        assert "signature" not in diagnosis_payload

        repair_result = await session.call_tool(
            "submit_repair", {"challenge_token": token, "repair_source": GOOD_REPAIR}
        )
        repair_payload = _payload(repair_result)
        assert repair_payload["status"] == "completed"
        assert repair_payload["trace"]["stage"] == "verifier"
        assert all(item["passed"] for item in repair_payload["property_results"])
