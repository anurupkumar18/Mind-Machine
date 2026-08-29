"""Splits uploaded text into provenance-tagged chunks for retrieval.

First-slice scope: plain text only (docs/superpowers/specs/2026-08-29-
student-study-workspace-design.md's non-goals) -- format-specific
extraction (PDF/docx) is future work. "Location" here is a chunk-index
label since plain text has no page structure; richer location tagging
arrives with real document-format support.
"""

from __future__ import annotations

from app.domain.workspace_contracts import MaterialChunk

_CHUNK_SIZE_CHARS = 1000


def chunk_with_provenance(*, workspace_id: str, filename: str, text: str) -> list[MaterialChunk]:
    stripped = text.strip()
    if not stripped:
        return []

    chunks: list[MaterialChunk] = []
    for index, start in enumerate(range(0, len(stripped), _CHUNK_SIZE_CHARS)):
        chunk_text = stripped[start : start + _CHUNK_SIZE_CHARS]
        chunks.append(
            MaterialChunk(
                workspace_id=workspace_id,
                filename=filename,
                location=f"chunk {index + 1}",
                text=chunk_text,
            )
        )
    return chunks
