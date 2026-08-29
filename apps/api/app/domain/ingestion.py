"""Orchestrates ingestion of one uploaded material into a workspace.

Ties together chunking, the I1 data-boundary heuristic, and storage.
Text-only input for this slice (docs/superpowers/specs/2026-08-29-
student-study-workspace-design.md's non-goals) -- the MCP tool that calls
this passes already-extracted plain text; real file-format extraction and
the exact ChatGPT/Codex attachment-delivery shape are unverified and
noted as a follow-up spike in the design doc.
"""

from __future__ import annotations

from app.domain.chunking import chunk_with_provenance
from app.domain.data_boundary import classify_for_data_boundary
from app.domain.workspace_contracts import IngestResult
from app.domain.workspace_store import store_chunks


def ingest_material(*, workspace_id: str, filename: str, text: str) -> IngestResult:
    boundary_status, reason = classify_for_data_boundary(filename, text)

    if boundary_status == "reject":
        return IngestResult(filename=filename, chunk_count=0, status="rejected", reason=reason)

    chunks = chunk_with_provenance(workspace_id=workspace_id, filename=filename, text=text)

    if boundary_status == "flag":
        return IngestResult(filename=filename, chunk_count=len(chunks), status="flagged", reason=reason)

    store_chunks(workspace_id=workspace_id, filename=filename, chunks=chunks)
    return IngestResult(filename=filename, chunk_count=len(chunks), status="stored", reason=None)
