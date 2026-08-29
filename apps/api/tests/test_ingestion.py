"""Ingestion ties chunking, the I1 data-boundary heuristic, and storage
together. Flagged/rejected content is never stored -- only a student
explicitly re-uploading under a different name (after fixing whatever
triggered the flag/reject) results in storage; there is no
'confirm anyway' override in this first slice (stated limitation,
docs/superpowers/specs/2026-08-29-student-study-workspace-design.md)."""

from __future__ import annotations

import uuid

from app.domain.ingestion import ingest_material
from app.domain.workspace_store import list_materials


def _workspace_id() -> str:
    return str(uuid.uuid4())


def test_ingest_material_stores_clean_content() -> None:
    ws = _workspace_id()

    result = ingest_material(workspace_id=ws, filename="syllabus.txt", text="This course covers BFS and DFS.")

    assert result.status == "stored"
    assert result.chunk_count == 1
    assert result.reason is None
    assert [m.filename for m in list_materials(ws)] == ["syllabus.txt"]


def test_ingest_material_does_not_store_rejected_content() -> None:
    ws = _workspace_id()

    result = ingest_material(workspace_id=ws, filename="hw1_submission.pdf", text="My answer to problem 1.")

    assert result.status == "rejected"
    assert result.chunk_count == 0
    assert result.reason is not None
    assert list_materials(ws) == []


def test_ingest_material_does_not_store_flagged_content() -> None:
    ws = _workspace_id()

    result = ingest_material(workspace_id=ws, filename="final_exam.txt", text="Some course content.")

    assert result.status == "flagged"
    assert result.chunk_count > 0
    assert result.reason is not None
    assert list_materials(ws) == []


def test_ingest_material_with_blank_text_stores_zero_chunks() -> None:
    ws = _workspace_id()

    result = ingest_material(workspace_id=ws, filename="empty.txt", text="   ")

    assert result.status == "stored"
    assert result.chunk_count == 0
