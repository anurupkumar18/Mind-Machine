"""Deterministic keyword-overlap retrieval -- no embeddings, no inference
cost, same transparent-heuristic idiom as app.domain.topic_matching."""

from __future__ import annotations

import uuid

from app.domain.retrieval import keyword_search
from app.domain.workspace_contracts import MaterialChunk
from app.domain.workspace_store import store_chunks


def _workspace_id() -> str:
    return str(uuid.uuid4())


def test_keyword_search_on_empty_workspace_returns_no_results() -> None:
    assert keyword_search(workspace_id=_workspace_id(), question="what is BFS?") == []


def test_keyword_search_returns_matching_chunk() -> None:
    ws = _workspace_id()
    chunk = MaterialChunk(
        workspace_id=ws,
        filename="notes.txt",
        location="chunk 1",
        text="Breadth-first search marks nodes visited when they enter the frontier.",
    )
    store_chunks(workspace_id=ws, filename="notes.txt", chunks=[chunk])

    results = keyword_search(workspace_id=ws, question="when are nodes marked visited?")

    assert len(results) == 1
    assert results[0].filename == "notes.txt"
    assert results[0].location == "chunk 1"
    assert results[0].excerpt == chunk.text
    assert results[0].score > 0


def test_keyword_search_returns_no_results_when_nothing_matches() -> None:
    ws = _workspace_id()
    chunk = MaterialChunk(workspace_id=ws, filename="notes.txt", location="chunk 1", text="Sorting algorithms overview.")
    store_chunks(workspace_id=ws, filename="notes.txt", chunks=[chunk])

    results = keyword_search(workspace_id=ws, question="quantum entanglement")

    assert results == []


def test_keyword_search_ranks_more_relevant_chunk_higher() -> None:
    ws = _workspace_id()
    high = MaterialChunk(workspace_id=ws, filename="a.txt", location="chunk 1", text="visited visited visited frontier")
    low = MaterialChunk(workspace_id=ws, filename="b.txt", location="chunk 1", text="visited mentioned once here amid unrelated words that pad the chunk out")
    store_chunks(workspace_id=ws, filename="a.txt", chunks=[high])
    store_chunks(workspace_id=ws, filename="b.txt", chunks=[low])

    results = keyword_search(workspace_id=ws, question="visited frontier")

    assert results[0].filename == "a.txt"


def test_keyword_search_respects_top_k() -> None:
    ws = _workspace_id()
    for i in range(10):
        chunk = MaterialChunk(workspace_id=ws, filename=f"file{i}.txt", location="chunk 1", text="visited node frontier")
        store_chunks(workspace_id=ws, filename=f"file{i}.txt", chunks=[chunk])

    results = keyword_search(workspace_id=ws, question="visited frontier", top_k=3)

    assert len(results) == 3
