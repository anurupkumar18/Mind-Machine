"""Contracts for the student study workspace (real materials, cited Q&A).

Distinct from the code-repair challenge contracts in `contracts.py` --
this is Evidence Engine's second capability
(docs/superpowers/specs/2026-08-29-student-study-workspace-design.md),
not a variant of the existing coaching loop.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class MaterialChunk(BaseModel):
    workspace_id: str
    filename: str
    location: str
    text: str


class IngestResult(BaseModel):
    filename: str
    chunk_count: int
    status: Literal["stored", "flagged", "rejected"]
    reason: str | None = None


class MaterialSummary(BaseModel):
    filename: str
    chunk_count: int
    added_at: str


class RetrievedExcerpt(BaseModel):
    excerpt: str
    filename: str
    location: str
    score: float
