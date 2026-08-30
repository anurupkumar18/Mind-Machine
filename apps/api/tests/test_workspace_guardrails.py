"""Guardrail suite for the student study workspace capability: every
returned excerpt must trace to real stored content, and a workspace must
never receive another workspace's material. Distinct from, and not a
replacement for, test_guardrails.py's I6/I7 suite for the code-repair
coaching tools -- this capability is meant to answer directly; its
guarantee is data isolation and citation integrity, not non-evaluation.
"""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import anyio
import pytest
from mcp import ClientSession
from mcp.shared.memory import create_client_server_memory_streams

from app.mcp_server import mcp

pytestmark = pytest.mark.anyio


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


async def test_answer_from_materials_never_leaks_another_workspaces_content() -> None:
    workspace_a = f"ws-a-{uuid.uuid4()}"
    workspace_b = f"ws-b-{uuid.uuid4()}"

    async with connected_client() as session:
        await session.call_tool(
            "add_course_material",
            {
                "workspace_id": workspace_a,
                "filename": "a.txt",
                "text": "The secret ingredient in workspace A is xylophone-quokka-77.",
            },
        )
        await session.call_tool(
            "add_course_material",
            {
                "workspace_id": workspace_b,
                "filename": "b.txt",
                "text": "The secret ingredient in workspace B is xylophone-quokka-77.",
            },
        )
        result_a = await session.call_tool(
            "answer_from_materials", {"workspace_id": workspace_a, "question": "xylophone-quokka-77"}
        )

    payload_a = _payload(result_a)
    filenames = {excerpt["filename"] for excerpt in payload_a["excerpts"]}  # type: ignore[index]
    assert filenames == {"a.txt"}, "workspace A's answer must never include workspace B's material"


async def test_every_returned_excerpt_traces_to_real_stored_content() -> None:
    workspace_id = f"ws-trace-{uuid.uuid4()}"
    original_text = "Dynamic programming stores subproblem results to avoid recomputation."

    async with connected_client() as session:
        await session.call_tool(
            "add_course_material", {"workspace_id": workspace_id, "filename": "dp.txt", "text": original_text}
        )
        result = await session.call_tool(
            "answer_from_materials", {"workspace_id": workspace_id, "question": "dynamic programming subproblems"}
        )

    payload = _payload(result)
    excerpts = payload["excerpts"]  # type: ignore[index]
    assert excerpts, "expected at least one excerpt for a clearly matching question"
    for excerpt in excerpts:  # type: ignore[union-attr]
        assert excerpt["excerpt"] in original_text, "every excerpt must be verbatim from what was actually ingested"
        assert excerpt["filename"] == "dp.txt"


async def test_removed_material_never_appears_in_later_answers() -> None:
    workspace_id = f"ws-removed-{uuid.uuid4()}"

    async with connected_client() as session:
        await session.call_tool(
            "add_course_material",
            {"workspace_id": workspace_id, "filename": "old.txt", "text": "The unique marker is qwerty-marker-99."},
        )
        await session.call_tool("remove_material", {"workspace_id": workspace_id, "filename": "old.txt"})
        result = await session.call_tool(
            "answer_from_materials", {"workspace_id": workspace_id, "question": "qwerty-marker-99"}
        )

    payload = _payload(result)
    assert payload["excerpts"] == [], "removed material must never surface in a later answer"
