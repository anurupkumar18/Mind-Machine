"""Deterministic keyword-overlap retrieval over stored material chunks.

Same "transparent heuristic, not semantic understanding" framing as
app.domain.topic_matching -- no embedding model, no vector database (no
inference cost). Ranks by the fraction of each chunk's tokens that match
a question term; ties broken by chunk insertion order.
"""

from __future__ import annotations

import re

from app.domain.workspace_contracts import MaterialChunk, RetrievedExcerpt
from app.domain.workspace_store import all_chunks

_WORD_PATTERN = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _WORD_PATTERN.findall(text.lower())


def _score(question_terms: set[str], chunk: MaterialChunk) -> float:
    chunk_terms = _tokenize(chunk.text)
    if not chunk_terms:
        return 0.0
    matches = sum(1 for term in chunk_terms if term in question_terms)
    return matches / len(chunk_terms)


def keyword_search(*, workspace_id: str, question: str, top_k: int = 5) -> list[RetrievedExcerpt]:
    question_terms = set(_tokenize(question))
    if not question_terms:
        return []

    scored = [(chunk, _score(question_terms, chunk)) for chunk in all_chunks(workspace_id)]
    relevant = [(chunk, score) for chunk, score in scored if score > 0]
    relevant.sort(key=lambda pair: pair[1], reverse=True)

    return [
        RetrievedExcerpt(excerpt=chunk.text, filename=chunk.filename, location=chunk.location, score=score)
        for chunk, score in relevant[:top_k]
    ]
