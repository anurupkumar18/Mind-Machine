"""In-process per-workspace storage. Uses a fresh uuid4 workspace_id per
test since the store is module-level state shared across the test
session (not reset between tests) -- unique IDs avoid cross-test
pollution the same way real workspaces avoid cross-student pollution."""

from __future__ import annotations

import uuid

import pytest

from app.domain.workspace_contracts import MaterialChunk
from app.domain.workspace_store import (
    UnknownMaterialError,
    UnknownWorkspaceError,
    all_chunks,
    delete_workspace,
    list_materials,
    remove_material,
    store_chunks,
)


def _workspace_id() -> str:
    return str(uuid.uuid4())


def _chunk(workspace_id: str, filename: str, text: str = "content") -> MaterialChunk:
    return MaterialChunk(workspace_id=workspace_id, filename=filename, location="chunk 1", text=text)


def test_store_chunks_then_list_materials_returns_summary() -> None:
    ws = _workspace_id()
    store_chunks(workspace_id=ws, filename="notes.txt", chunks=[_chunk(ws, "notes.txt")])

    materials = list_materials(ws)

    assert len(materials) == 1
    assert materials[0].filename == "notes.txt"
    assert materials[0].chunk_count == 1
    assert materials[0].added_at


def test_list_materials_on_unknown_workspace_returns_empty_list() -> None:
    assert list_materials(_workspace_id()) == []


def test_store_chunks_then_all_chunks_returns_the_chunks() -> None:
    ws = _workspace_id()
    chunk = _chunk(ws, "notes.txt", text="hello")
    store_chunks(workspace_id=ws, filename="notes.txt", chunks=[chunk])

    assert all_chunks(ws) == [chunk]


def test_remove_material_deletes_it() -> None:
    ws = _workspace_id()
    store_chunks(workspace_id=ws, filename="notes.txt", chunks=[_chunk(ws, "notes.txt")])

    remove_material(workspace_id=ws, filename="notes.txt")

    assert list_materials(ws) == []
    assert all_chunks(ws) == []


def test_remove_material_on_unknown_material_raises() -> None:
    with pytest.raises(UnknownMaterialError):
        remove_material(workspace_id=_workspace_id(), filename="does-not-exist.txt")


def test_delete_workspace_removes_everything() -> None:
    ws = _workspace_id()
    store_chunks(workspace_id=ws, filename="a.txt", chunks=[_chunk(ws, "a.txt")])
    store_chunks(workspace_id=ws, filename="b.txt", chunks=[_chunk(ws, "b.txt")])

    delete_workspace(ws)

    assert list_materials(ws) == []


def test_delete_workspace_on_unknown_workspace_raises() -> None:
    with pytest.raises(UnknownWorkspaceError):
        delete_workspace(_workspace_id())
