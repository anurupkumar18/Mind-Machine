"""In-process, per-workspace storage for study-workspace material chunks.

Known limitation, stated explicitly: this is an in-memory store, not a
database -- data does not survive a process restart. Matches this
project's existing MVP conventions (no database anywhere yet); a real
persistence layer is future work once this capability is validated, not
a redesign of what's here. See docs/STUDY_WORKSPACE.md.
"""

from __future__ import annotations

from datetime import UTC, datetime

from app.domain.workspace_contracts import MaterialChunk, MaterialSummary

_STORE: dict[str, dict[str, list[MaterialChunk]]] = {}
_ADDED_AT: dict[str, dict[str, str]] = {}


class UnknownWorkspaceError(ValueError):
    """Raised when a workspace_id has no stored materials to delete."""


class UnknownMaterialError(ValueError):
    """Raised when a filename has no stored chunks in a given workspace."""


def store_chunks(*, workspace_id: str, filename: str, chunks: list[MaterialChunk]) -> None:
    workspace = _STORE.setdefault(workspace_id, {})
    workspace[filename] = chunks
    _ADDED_AT.setdefault(workspace_id, {})[filename] = datetime.now(UTC).isoformat()


def list_materials(workspace_id: str) -> list[MaterialSummary]:
    workspace = _STORE.get(workspace_id, {})
    added_at = _ADDED_AT.get(workspace_id, {})
    return [
        MaterialSummary(filename=filename, chunk_count=len(chunks), added_at=added_at[filename])
        for filename, chunks in workspace.items()
    ]


def all_chunks(workspace_id: str) -> list[MaterialChunk]:
    workspace = _STORE.get(workspace_id, {})
    return [chunk for chunks in workspace.values() for chunk in chunks]


def remove_material(*, workspace_id: str, filename: str) -> None:
    workspace = _STORE.get(workspace_id)
    if workspace is None or filename not in workspace:
        raise UnknownMaterialError(f"No material {filename!r} in workspace {workspace_id!r}")
    del workspace[filename]
    del _ADDED_AT[workspace_id][filename]


def delete_workspace(workspace_id: str) -> None:
    if workspace_id not in _STORE:
        raise UnknownWorkspaceError(f"Unknown workspace: {workspace_id!r}")
    del _STORE[workspace_id]
    _ADDED_AT.pop(workspace_id, None)
