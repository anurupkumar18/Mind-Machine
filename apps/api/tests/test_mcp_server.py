"""Phase 1 spike 2: prove a real MCP tool call reaches Evidence Engine's
domain logic through the actual MCP protocol (in-memory client/server
streams, not a bypass of the wire format)."""

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


async def test_start_challenge_tool_is_discoverable() -> None:
    async with connected_client() as session:
        tools = await session.list_tools()

    names = [tool.name for tool in tools.tools]
    assert "start_challenge" in names


async def test_start_challenge_returns_grounded_challenge_data() -> None:
    async with connected_client() as session:
        result = await session.call_tool("start_challenge", {"challenge_id": "traversal-invariant-02"})

    assert result.is_error is not True
    payload = json.loads(result.content[0].text)  # type: ignore[union-attr]
    assert payload["challenge_id"] == "traversal-invariant-02"
    assert payload["expected_first_frontier"] == ["B", "C"]
    assert payload["trace"]["tool"] == "start_challenge"
    assert payload["challenge_token"]


async def test_unknown_challenge_id_is_reported_as_tool_error_not_a_crash() -> None:
    async with connected_client() as session:
        result = await session.call_tool("start_challenge", {"challenge_id": "does-not-exist"})

    assert result.is_error is True


async def test_list_course_topics_tool_is_discoverable() -> None:
    async with connected_client() as session:
        tools = await session.list_tools()

    names = [tool.name for tool in tools.tools]
    assert "list_course_topics" in names


async def test_list_course_topics_returns_mock_course_with_a_matched_topic() -> None:
    async with connected_client() as session:
        result = await session.call_tool("list_course_topics", {})

    assert result.is_error is not True
    payload = json.loads(result.content[0].text)  # type: ignore[union-attr]
    assert payload["course_name"]
    matched = [t for t in payload["topics"] if t["matched_challenge_id"] == "traversal-invariant-02"]
    assert matched, "expected at least one mock module to match traversal-invariant-02"


async def test_start_challenge_accepts_topic_instead_of_challenge_id() -> None:
    async with connected_client() as session:
        result = await session.call_tool("start_challenge", {"topic": "graph traversal"})

    assert result.is_error is not True
    payload = json.loads(result.content[0].text)  # type: ignore[union-attr]
    assert payload["challenge_id"] == "traversal-invariant-02"


async def test_start_challenge_rejects_both_challenge_id_and_topic() -> None:
    async with connected_client() as session:
        result = await session.call_tool(
            "start_challenge", {"challenge_id": "traversal-invariant-02", "topic": "graph traversal"}
        )

    assert result.is_error is True


async def test_start_challenge_rejects_neither_challenge_id_nor_topic() -> None:
    async with connected_client() as session:
        result = await session.call_tool("start_challenge", {})

    assert result.is_error is True


async def test_start_challenge_rejects_unmatched_topic() -> None:
    async with connected_client() as session:
        result = await session.call_tool("start_challenge", {"topic": "dynamic programming"})

    assert result.is_error is True


async def test_workspace_tools_are_discoverable() -> None:
    async with connected_client() as session:
        tools = await session.list_tools()

    names = [tool.name for tool in tools.tools]
    for expected in (
        "add_course_material",
        "list_workspace_materials",
        "remove_material",
        "delete_workspace",
        "answer_from_materials",
    ):
        assert expected in names


async def test_add_course_material_stores_and_lists_it() -> None:
    workspace_id = "test-ws-store-and-list"
    async with connected_client() as session:
        add_result = await session.call_tool(
            "add_course_material",
            {"workspace_id": workspace_id, "filename": "syllabus.txt", "text": "This course covers BFS and DFS."},
        )
        list_result = await session.call_tool("list_workspace_materials", {"workspace_id": workspace_id})

    assert add_result.is_error is not True
    add_payload = json.loads(add_result.content[0].text)  # type: ignore[union-attr]
    assert add_payload["status"] == "stored"

    assert list_result.is_error is not True
    list_payload = json.loads(list_result.content[0].text)  # type: ignore[union-attr]
    assert [m["filename"] for m in list_payload["materials"]] == ["syllabus.txt"]


async def test_add_course_material_rejects_graded_submission_content() -> None:
    workspace_id = "test-ws-reject"
    async with connected_client() as session:
        result = await session.call_tool(
            "add_course_material",
            {"workspace_id": workspace_id, "filename": "hw_submission.txt", "text": "My work."},
        )

    assert result.is_error is not True
    payload = json.loads(result.content[0].text)  # type: ignore[union-attr]
    assert payload["status"] == "rejected"


async def test_answer_from_materials_reports_no_materials_for_empty_workspace() -> None:
    async with connected_client() as session:
        result = await session.call_tool(
            "answer_from_materials", {"workspace_id": "test-ws-never-used", "question": "anything?"}
        )

    assert result.is_error is not True
    payload = json.loads(result.content[0].text)  # type: ignore[union-attr]
    assert payload["status"] == "no_materials"
    assert payload["excerpts"] == []


async def test_answer_from_materials_returns_cited_excerpts() -> None:
    workspace_id = "test-ws-answer"
    async with connected_client() as session:
        await session.call_tool(
            "add_course_material",
            {
                "workspace_id": workspace_id,
                "filename": "notes.txt",
                "text": "Breadth-first search marks nodes visited when they enter the frontier.",
            },
        )
        result = await session.call_tool(
            "answer_from_materials", {"workspace_id": workspace_id, "question": "when are nodes marked visited?"}
        )

    assert result.is_error is not True
    payload = json.loads(result.content[0].text)  # type: ignore[union-attr]
    assert payload["status"] == "ok"
    assert payload["excerpts"][0]["filename"] == "notes.txt"


async def test_remove_material_deletes_it_and_errors_on_unknown() -> None:
    workspace_id = "test-ws-remove"
    async with connected_client() as session:
        await session.call_tool(
            "add_course_material", {"workspace_id": workspace_id, "filename": "notes.txt", "text": "Some content."}
        )
        removed = await session.call_tool("remove_material", {"workspace_id": workspace_id, "filename": "notes.txt"})
        unknown = await session.call_tool(
            "remove_material", {"workspace_id": workspace_id, "filename": "does-not-exist.txt"}
        )

    assert removed.is_error is not True
    assert unknown.is_error is True


async def test_delete_workspace_deletes_it_and_errors_on_unknown() -> None:
    workspace_id = "test-ws-delete"
    async with connected_client() as session:
        await session.call_tool(
            "add_course_material", {"workspace_id": workspace_id, "filename": "notes.txt", "text": "Some content."}
        )
        deleted = await session.call_tool("delete_workspace", {"workspace_id": workspace_id})
        unknown = await session.call_tool("delete_workspace", {"workspace_id": workspace_id})

    assert deleted.is_error is not True
    assert unknown.is_error is True
