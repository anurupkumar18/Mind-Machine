"""Chunking splits uploaded text into provenance-tagged pieces for
retrieval. First-slice scope is plain text only (docs/superpowers/specs/
2026-08-29-student-study-workspace-design.md's non-goals)."""

from __future__ import annotations

from app.domain.chunking import chunk_with_provenance


def test_chunk_with_provenance_returns_empty_list_for_blank_text() -> None:
    chunks = chunk_with_provenance(workspace_id="ws-1", filename="notes.txt", text="   ")

    assert chunks == []


def test_chunk_with_provenance_returns_one_chunk_for_short_text() -> None:
    chunks = chunk_with_provenance(workspace_id="ws-1", filename="notes.txt", text="Hello world")

    assert len(chunks) == 1
    assert chunks[0].workspace_id == "ws-1"
    assert chunks[0].filename == "notes.txt"
    assert chunks[0].location == "chunk 1"
    assert chunks[0].text == "Hello world"


def test_chunk_with_provenance_splits_long_text_into_ordered_chunks() -> None:
    long_text = "a" * 2500

    chunks = chunk_with_provenance(workspace_id="ws-1", filename="reading.txt", text=long_text)

    assert len(chunks) == 3
    assert [c.location for c in chunks] == ["chunk 1", "chunk 2", "chunk 3"]
    assert len(chunks[0].text) == 1000
    assert len(chunks[1].text) == 1000
    assert len(chunks[2].text) == 500
    assert "".join(c.text for c in chunks) == long_text


def test_chunk_with_provenance_strips_surrounding_whitespace() -> None:
    chunks = chunk_with_provenance(workspace_id="ws-1", filename="notes.txt", text="  padded  ")

    assert len(chunks) == 1
    assert chunks[0].text == "padded"
