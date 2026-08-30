# Student Study Workspace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the student study workspace — upload real course materials via chat attachment, get cited answers via keyword retrieval + host-model synthesis — as a second, distinct Evidence Engine capability alongside the existing code-repair coaching loop.

**Architecture:** Five small domain modules (`chunking.py`, `data_boundary.py`, `workspace_store.py`, `retrieval.py`, `ingestion.py`) plus one new contracts file (`workspace_contracts.py`), wired into five new MCP tools (`add_course_material`, `list_workspace_materials`, `remove_material`, `delete_workspace`, `answer_from_materials`) in `apps/api/app/mcp_server.py`. Storage is an in-process dict (explicitly not a database — a stated, documented limitation, not a gap). Retrieval is deterministic keyword overlap (no embeddings, no inference cost, matching `app.domain.topic_matching`'s existing style). `add_course_material` takes already-extracted plain text as its best-guess parameter shape — the design's open feasibility spike (how ChatGPT/Codex actually deliver file-attachment content to a tool call) stays unresolved and is documented as such, matching this project's existing practice for the MCP-connectivity spike.

**Tech Stack:** Python 3.12, pydantic v2, pytest + `mcp.shared.memory` in-memory client/server streams (existing test pattern), mypy strict, ruff.

**Design doc:** `docs/superpowers/specs/2026-08-29-student-study-workspace-design.md`

**Explicitly out of scope for this plan** (per the design's non-goals and the brainstorming conversation): rewriting `docs/PROJECT_CHARTER.md`'s thesis/invariants — that's a separate, deliberate next task after this code ships, not part of this plan. PDF/docx extraction. A web UI. Any change to the existing code-repair MCP tools or their guardrail suite.

---

### Task 1: Workspace contracts

**Files:**
- Create: `apps/api/app/domain/workspace_contracts.py`

- [x] **Step 1: Write the file**

Create `apps/api/app/domain/workspace_contracts.py`:

```python
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
```

- [x] **Step 2: Typecheck**

Run: `cd apps/api && uv run mypy app`
Expected: `Success: no issues found`

- [x] **Step 3: Commit**

```bash
git add apps/api/app/domain/workspace_contracts.py
git commit -m "Add contracts for the student study workspace capability"
```

**Note:** no dedicated test file for this task — matches this codebase's existing convention (`apps/api/app/domain/contracts.py`'s models have no standalone test file either; they're exercised through their consumers in later tasks).

---

### Task 2: `chunking` module

**Files:**
- Create: `apps/api/app/domain/chunking.py`
- Test: `apps/api/tests/test_chunking.py`

- [x] **Step 1: Write the failing test**

Create `apps/api/tests/test_chunking.py`:

```python
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
```

- [x] **Step 2: Run the tests to verify they fail**

Run: `cd apps/api && uv run pytest tests/test_chunking.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.domain.chunking'`

- [x] **Step 3: Write the implementation**

Create `apps/api/app/domain/chunking.py`:

```python
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
```

- [x] **Step 4: Run the tests to verify they pass**

Run: `cd apps/api && uv run pytest tests/test_chunking.py -v`
Expected: 4 passed

- [x] **Step 5: Typecheck and lint**

Run: `cd apps/api && uv run mypy app && uv run ruff check .`
Expected: both clean

- [x] **Step 6: Commit**

```bash
git add apps/api/app/domain/chunking.py apps/api/tests/test_chunking.py
git commit -m "Add provenance-tagged text chunking for study materials"
```

---

### Task 3: `data_boundary` module

**Files:**
- Create: `apps/api/app/domain/data_boundary.py`
- Test: `apps/api/tests/test_data_boundary.py`

- [x] **Step 1: Write the failing test**

Create `apps/api/tests/test_data_boundary.py`:

```python
"""Heuristic I1 data-boundary enforcement: best-effort pattern matching,
not a guarantee (docs/superpowers/specs/2026-08-29-student-study-
workspace-design.md). Covers the allow/flag/reject cases from the
research doc's include/exclude table, plus adversarial synthetic
examples of submission-like, exam-like, and roster/discussion-like
content."""

from __future__ import annotations

from app.domain.data_boundary import classify_for_data_boundary


def test_allows_plain_syllabus_text() -> None:
    status, reason = classify_for_data_boundary(
        "syllabus.txt", "This course covers graph traversal and dynamic programming."
    )

    assert status == "allow"
    assert reason is None


def test_allows_students_own_notes() -> None:
    status, reason = classify_for_data_boundary(
        "my_notes.txt", "Remember: BFS marks visited on enqueue, not dequeue."
    )

    assert status == "allow"
    assert reason is None


def test_rejects_content_with_a_visible_grade() -> None:
    status, reason = classify_for_data_boundary(
        "homework1.txt", "Great work on this problem set.\nGrade: 95/100"
    )

    assert status == "reject"
    assert reason is not None and "graded-submission" in reason


def test_rejects_content_with_a_visible_score() -> None:
    status, reason = classify_for_data_boundary("notes.txt", "Score: 42 out of 50")

    assert status == "reject"
    assert reason is not None


def test_rejects_filename_indicating_a_submission() -> None:
    status, reason = classify_for_data_boundary("problem_set_1_submission.pdf", "Some content.")

    assert status == "reject"
    assert reason is not None and "submission" in reason


def test_rejects_answer_key_content() -> None:
    status, reason = classify_for_data_boundary("study_guide.txt", "Answer Key: 1) B 2) A 3) C")

    assert status == "reject"
    assert reason is not None


def test_flags_filename_indicating_an_exam() -> None:
    status, reason = classify_for_data_boundary("midterm_exam.txt", "Some content about the course.")

    assert status == "flag"
    assert reason is not None and "exam" in reason.lower()


def test_flags_discussion_post_like_content() -> None:
    status, reason = classify_for_data_boundary(
        "forum.txt", "Posted by Jane Smith: I think the answer is related to invariants."
    )

    assert status == "flag"
    assert reason is not None


def test_flags_reply_marker_content() -> None:
    status, reason = classify_for_data_boundary("thread.txt", "Re: question about assignment 3")

    assert status == "flag"
    assert reason is not None
```

- [x] **Step 2: Run the tests to verify they fail**

Run: `cd apps/api && uv run pytest tests/test_data_boundary.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.domain.data_boundary'`

- [x] **Step 3: Write the implementation**

Create `apps/api/app/domain/data_boundary.py`:

```python
"""Heuristic data-boundary enforcement for uploaded study materials (I1).

Best-effort pattern matching, not a guarantee -- same honesty standard
this project already applies to its other heuristics (topic_matching.py's
keyword overlap, the practice-selection heuristic in PROJECT_CHARTER.md).
Never a machine-learning classifier: no inference cost, and a
transparent, auditable rule set is easier to reason about and extend than
an opaque model.
"""

from __future__ import annotations

import re
from typing import Literal

DataBoundaryStatus = Literal["allow", "flag", "reject"]

_REJECT_TEXT_PATTERNS = [
    (re.compile(r"\bgrade\s*:\s*\d", re.IGNORECASE), "content matches a graded-submission pattern (a visible grade)"),
    (re.compile(r"\bscore\s*:\s*\d", re.IGNORECASE), "content matches a graded-submission pattern (a visible score)"),
    (re.compile(r"\bsubmitted\s+by\b", re.IGNORECASE), "content matches a graded-submission pattern (a submission marker)"),
    (re.compile(r"\banswer\s+key\b", re.IGNORECASE), "content matches a graded-submission pattern (an answer key)"),
]
_REJECT_FILENAME_MARKERS = ["graded", "submission", "gradebook", "answerkey"]

_FLAG_TEXT_PATTERNS = [
    (re.compile(r"\bposted\s+by\b", re.IGNORECASE), "content matches a discussion-post-like pattern (a poster attribution)"),
    (re.compile(r"^\s*re\s*:", re.IGNORECASE | re.MULTILINE), "content matches a discussion-post-like pattern (a reply marker)"),
]
_FLAG_FILENAME_MARKERS = ["quiz", "exam", "test"]


def classify_for_data_boundary(filename: str, text: str) -> tuple[DataBoundaryStatus, str | None]:
    lowered_filename = filename.lower()

    for marker in _REJECT_FILENAME_MARKERS:
        if marker in lowered_filename:
            return "reject", f"filename contains {marker!r}, which looks like a graded submission"
    for pattern, reason in _REJECT_TEXT_PATTERNS:
        if pattern.search(text):
            return "reject", reason

    for marker in _FLAG_FILENAME_MARKERS:
        if marker in lowered_filename:
            return "flag", f"filename contains {marker!r}, which may be exam/quiz content"
    for pattern, reason in _FLAG_TEXT_PATTERNS:
        if pattern.search(text):
            return "flag", reason

    return "allow", None
```

- [x] **Step 4: Run the tests to verify they pass**

Run: `cd apps/api && uv run pytest tests/test_data_boundary.py -v`
Expected: 9 passed

- [x] **Step 5: Typecheck and lint**

Run: `cd apps/api && uv run mypy app && uv run ruff check .`
Expected: both clean

- [x] **Step 6: Commit**

```bash
git add apps/api/app/domain/data_boundary.py apps/api/tests/test_data_boundary.py
git commit -m "Add heuristic I1 data-boundary classifier for uploaded materials"
```

---

### Task 4: `workspace_store` module

**Files:**
- Create: `apps/api/app/domain/workspace_store.py`
- Test: `apps/api/tests/test_workspace_store.py`

- [x] **Step 1: Write the failing test**

Create `apps/api/tests/test_workspace_store.py`:

```python
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
```

- [x] **Step 2: Run the tests to verify they fail**

Run: `cd apps/api && uv run pytest tests/test_workspace_store.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.domain.workspace_store'`

- [x] **Step 3: Write the implementation**

Create `apps/api/app/domain/workspace_store.py`:

```python
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
```

- [x] **Step 4: Run the tests to verify they pass**

Run: `cd apps/api && uv run pytest tests/test_workspace_store.py -v`
Expected: 7 passed

- [x] **Step 5: Typecheck and lint**

Run: `cd apps/api && uv run mypy app && uv run ruff check .`
Expected: both clean

- [x] **Step 6: Commit**

```bash
git add apps/api/app/domain/workspace_store.py apps/api/tests/test_workspace_store.py
git commit -m "Add in-process per-workspace storage for study materials"
```

---

### Task 5: `retrieval` module

**Files:**
- Create: `apps/api/app/domain/retrieval.py`
- Test: `apps/api/tests/test_retrieval.py`

- [x] **Step 1: Write the failing test**

Create `apps/api/tests/test_retrieval.py`:

```python
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
```

- [x] **Step 2: Run the tests to verify they fail**

Run: `cd apps/api && uv run pytest tests/test_retrieval.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.domain.retrieval'`

- [x] **Step 3: Write the implementation**

Create `apps/api/app/domain/retrieval.py`:

```python
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
```

- [x] **Step 4: Run the tests to verify they pass**

Run: `cd apps/api && uv run pytest tests/test_retrieval.py -v`
Expected: 5 passed

- [x] **Step 5: Typecheck and lint**

Run: `cd apps/api && uv run mypy app && uv run ruff check .`
Expected: both clean

- [x] **Step 6: Commit**

```bash
git add apps/api/app/domain/retrieval.py apps/api/tests/test_retrieval.py
git commit -m "Add deterministic keyword-overlap retrieval for study materials"
```

---

### Task 6: `ingestion` module (orchestrator)

**Files:**
- Create: `apps/api/app/domain/ingestion.py`
- Test: `apps/api/tests/test_ingestion.py`

- [x] **Step 1: Write the failing test**

Create `apps/api/tests/test_ingestion.py`:

```python
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
```

- [x] **Step 2: Run the tests to verify they fail**

Run: `cd apps/api && uv run pytest tests/test_ingestion.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.domain.ingestion'`

- [x] **Step 3: Write the implementation**

Create `apps/api/app/domain/ingestion.py`:

```python
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
```

- [x] **Step 4: Run the tests to verify they pass**

Run: `cd apps/api && uv run pytest tests/test_ingestion.py -v`
Expected: 4 passed

- [x] **Step 5: Typecheck and lint**

Run: `cd apps/api && uv run mypy app && uv run ruff check .`
Expected: both clean

- [x] **Step 6: Commit**

```bash
git add apps/api/app/domain/ingestion.py apps/api/tests/test_ingestion.py
git commit -m "Add ingestion orchestrator wiring chunking, data-boundary, and storage"
```

---

### Task 7: MCP tool surface — 5 new tools

**Files:**
- Modify: `apps/api/app/mcp_server.py`
- Modify: `apps/api/tests/test_mcp_server.py`

- [x] **Step 1: Write the failing tests**

Append to `apps/api/tests/test_mcp_server.py`:

```python


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
```

- [x] **Step 2: Run the tests to verify they fail**

Run: `cd apps/api && uv run pytest tests/test_mcp_server.py -v`
Expected: FAIL — the 5 new tool names aren't registered yet

- [x] **Step 3: Update imports**

In `apps/api/app/mcp_server.py`, replace:

```python
from app.domain.canvas_mock import mock_course_context
from app.domain.challenge_token import InvalidTokenError, issue_token, verify_token
from app.domain.contracts import CourseTopicsResponse, DiagnosisRequest
from app.domain.fixtures import fixture_data
from app.domain.runtime import canonical_next_frontier
from app.domain.sandbox import execute_repair
from app.domain.socratic import diagnose
from app.domain.topic_matching import (
    NoMatchingChallengeError,
    match_topics,
    resolve_challenge_for_topic,
)
```

with:

```python
from app.domain.canvas_mock import mock_course_context
from app.domain.challenge_token import InvalidTokenError, issue_token, verify_token
from app.domain.contracts import CourseTopicsResponse, DiagnosisRequest
from app.domain.fixtures import fixture_data
from app.domain.ingestion import ingest_material
from app.domain.retrieval import keyword_search
from app.domain.runtime import canonical_next_frontier
from app.domain.sandbox import execute_repair
from app.domain.socratic import diagnose
from app.domain.topic_matching import (
    NoMatchingChallengeError,
    match_topics,
    resolve_challenge_for_topic,
)
from app.domain.workspace_store import (
    UnknownMaterialError,
    UnknownWorkspaceError,
    all_chunks,
    delete_workspace as delete_workspace_chunks,
    list_materials,
    remove_material as remove_material_chunks,
)
```

- [x] **Step 4: Update the server instructions string**

Replace:

```python
mcp = MCPServer(
    name="evidence-engine",
    version="0.1.0",
    instructions=(
        "Evidence Engine issues verified code-reasoning practice challenges. "
        "Optionally call list_course_topics first to see what the (mock) "
        "connected course covers and get a matching topic. Call "
        "start_challenge with either a challenge_id or a topic to begin; it "
        "returns a challenge_token to pass to every subsequent tool call. "
        "Evidence comes from Evidence Engine's own execution, never from "
        "this tool's caller."
    ),
)
```

with:

```python
mcp = MCPServer(
    name="evidence-engine",
    version="0.1.0",
    instructions=(
        "Evidence Engine issues verified code-reasoning practice challenges. "
        "Optionally call list_course_topics first to see what the (mock) "
        "connected course covers and get a matching topic. Call "
        "start_challenge with either a challenge_id or a topic to begin; it "
        "returns a challenge_token to pass to every subsequent tool call. "
        "Evidence comes from Evidence Engine's own execution, never from "
        "this tool's caller. Separately, a student study workspace lets a "
        "student add their own course materials (add_course_material), "
        "review or remove them (list_workspace_materials, remove_material, "
        "delete_workspace), and ask questions about them "
        "(answer_from_materials) -- this workspace answers directly, "
        "unlike the non-evaluative code-repair coaching above."
    ),
)
```

- [x] **Step 5: Add the 5 new tools**

Append these five tools to `apps/api/app/mcp_server.py`, after the existing `submit_repair` tool and before the `main()` function:

```python
@mcp.tool()
def add_course_material(workspace_id: str, filename: str, text: str) -> dict[str, Any]:
    """Ingest one uploaded study material into a student's workspace.

    Part of the student study workspace capability -- distinct from the
    code-repair coaching tools above; see
    docs/superpowers/specs/2026-08-29-student-study-workspace-design.md.

    Takes already-extracted plain text, not a raw file. How ChatGPT/Codex
    actually deliver attachment content to a tool call is unverified
    against a real host session -- this is the design's best-guess shape,
    matching this repo's existing practice of shipping a spike's
    engineering half before its institutional/connectivity half is
    confirmed (see docs/MCP_SERVER.md).
    """
    result = ingest_material(workspace_id=workspace_id, filename=filename, text=text)
    payload = result.model_dump()
    payload["trace"] = {"stage": "workspace", "tool": "add_course_material"}
    return payload


@mcp.tool()
def list_workspace_materials(workspace_id: str) -> dict[str, Any]:
    """List the materials currently stored in a study workspace."""
    materials = list_materials(workspace_id)
    return {
        "workspace_id": workspace_id,
        "materials": [m.model_dump() for m in materials],
        "trace": {"stage": "workspace", "tool": "list_workspace_materials"},
    }


@mcp.tool()
def remove_material(workspace_id: str, filename: str) -> dict[str, Any]:
    """Delete one material from a study workspace."""
    try:
        remove_material_chunks(workspace_id=workspace_id, filename=filename)
    except UnknownMaterialError as error:
        raise ValueError(str(error)) from error
    return {
        "workspace_id": workspace_id,
        "filename": filename,
        "deleted": True,
        "trace": {"stage": "workspace", "tool": "remove_material"},
    }


@mcp.tool()
def delete_workspace(workspace_id: str) -> dict[str, Any]:
    """Delete an entire study workspace and everything stored in it."""
    try:
        delete_workspace_chunks(workspace_id)
    except UnknownWorkspaceError as error:
        raise ValueError(str(error)) from error
    return {
        "workspace_id": workspace_id,
        "deleted": True,
        "trace": {"stage": "workspace", "tool": "delete_workspace"},
    }


@mcp.tool()
def answer_from_materials(workspace_id: str, question: str) -> dict[str, Any]:
    """Retrieve cited excerpts from a workspace's materials for a question.

    Returns excerpts only -- the host model synthesizes the actual answer
    and must cite filename/location for each excerpt it uses; no
    inference happens in this tool.
    """
    if not all_chunks(workspace_id):
        return {
            "workspace_id": workspace_id,
            "question": question,
            "excerpts": [],
            "status": "no_materials",
            "trace": {"stage": "workspace", "tool": "answer_from_materials"},
        }

    excerpts = keyword_search(workspace_id=workspace_id, question=question)
    return {
        "workspace_id": workspace_id,
        "question": question,
        "excerpts": [e.model_dump() for e in excerpts],
        "status": "no_match" if not excerpts else "ok",
        "trace": {"stage": "workspace", "tool": "answer_from_materials"},
    }
```

- [x] **Step 6: Run the tests to verify they pass**

Run: `cd apps/api && uv run pytest tests/test_mcp_server.py -v`
Expected: all passed (9 original + 7 new = 16)

- [x] **Step 7: Typecheck and lint**

Run: `cd apps/api && uv run mypy app && uv run ruff check .`
Expected: both clean

- [x] **Step 8: Run the full existing suite to confirm no regression**

Run: `cd apps/api && uv run pytest -q`
Expected: all pass (119 previous + new tests from Tasks 2-7)

- [x] **Step 9: Commit**

```bash
git add apps/api/app/mcp_server.py apps/api/tests/test_mcp_server.py
git commit -m "Add student study workspace MCP tools: ingest, list, remove, delete, answer"
```

---

### Task 8: Workspace guardrail suite (citation integrity + cross-workspace isolation)

**Files:**
- Create: `apps/api/tests/test_workspace_guardrails.py`

This capability's guarantee is different from the code-repair loop's I6 (which forbids direct answers). Here the guarantee is: `answer_from_materials` never fabricates a citation, and never returns another workspace's content — a real cross-student data-leak risk this project's culture would insist on testing explicitly, the same way `test_guardrails.py` sweeps for hidden-test leakage in the other capability.

- [x] **Step 1: Write the tests**

Create `apps/api/tests/test_workspace_guardrails.py`:

```python
"""Guardrail suite for the student study workspace capability: every
returned excerpt must trace to real stored content, and a workspace must
never receive another workspace's material. Distinct from, and not a
replacement for, test_guardrails.py's I6/I7 suite for the code-repair
coaching tools -- this capability is meant to answer directly; its
guarantee is data isolation and citation integrity, not non-evaluation.
"""

from __future__ import annotations

import json
import uuid
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


def _payload(result: object) -> dict[str, object]:
    return json.loads(result.content[0].text)  # type: ignore[attr-defined,union-attr,no-any-return]


async def test_answer_from_materials_never_leaks_another_workspaces_content() -> None:
    workspace_a = f"ws-a-{uuid.uuid4()}"
    workspace_b = f"ws-b-{uuid.uuid4()}"

    async with connected_client() as session:
        await session.call_tool(
            "add_course_material",
            {
                "workspace_id": workspace_a,
                "filename": "a.txt",
                "text": "The secret ingredient in workspace A is xylophone-quokka-77.",
            },
        )
        await session.call_tool(
            "add_course_material",
            {
                "workspace_id": workspace_b,
                "filename": "b.txt",
                "text": "The secret ingredient in workspace B is xylophone-quokka-77.",
            },
        )
        result_a = await session.call_tool(
            "answer_from_materials", {"workspace_id": workspace_a, "question": "xylophone-quokka-77"}
        )

    payload_a = _payload(result_a)
    filenames = {excerpt["filename"] for excerpt in payload_a["excerpts"]}  # type: ignore[index]
    assert filenames == {"a.txt"}, "workspace A's answer must never include workspace B's material"


async def test_every_returned_excerpt_traces_to_real_stored_content() -> None:
    workspace_id = f"ws-trace-{uuid.uuid4()}"
    original_text = "Dynamic programming stores subproblem results to avoid recomputation."

    async with connected_client() as session:
        await session.call_tool(
            "add_course_material", {"workspace_id": workspace_id, "filename": "dp.txt", "text": original_text}
        )
        result = await session.call_tool(
            "answer_from_materials", {"workspace_id": workspace_id, "question": "dynamic programming subproblems"}
        )

    payload = _payload(result)
    excerpts = payload["excerpts"]  # type: ignore[index]
    assert excerpts, "expected at least one excerpt for a clearly matching question"
    for excerpt in excerpts:  # type: ignore[union-attr]
        assert excerpt["excerpt"] in original_text, "every excerpt must be verbatim from what was actually ingested"
        assert excerpt["filename"] == "dp.txt"


async def test_removed_material_never_appears_in_later_answers() -> None:
    workspace_id = f"ws-removed-{uuid.uuid4()}"

    async with connected_client() as session:
        await session.call_tool(
            "add_course_material",
            {"workspace_id": workspace_id, "filename": "old.txt", "text": "The unique marker is qwerty-marker-99."},
        )
        await session.call_tool("remove_material", {"workspace_id": workspace_id, "filename": "old.txt"})
        result = await session.call_tool(
            "answer_from_materials", {"workspace_id": workspace_id, "question": "qwerty-marker-99"}
        )

    payload = _payload(result)
    assert payload["excerpts"] == [], "removed material must never surface in a later answer"
```

- [x] **Step 2: Run the tests to verify they pass**

Run: `cd apps/api && uv run pytest tests/test_workspace_guardrails.py -v`
Expected: 3 passed

These are not expected to fail against Task 7's implementation — running them is what proves the isolation/traceability guarantee structurally, the same standard `test_guardrails.py` already sets for the other capability.

- [x] **Step 3: Lint**

Run: `cd apps/api && uv run ruff check .`
Expected: clean

- [x] **Step 4: Commit**

```bash
git add apps/api/tests/test_workspace_guardrails.py
git commit -m "Add guardrail suite for study-workspace citation integrity and isolation"
```

---

### Task 9: `docs/STUDY_WORKSPACE.md`

**Files:**
- Create: `docs/STUDY_WORKSPACE.md`

- [x] **Step 1: Write the file**

Create `docs/STUDY_WORKSPACE.md`:

```markdown
# Student study workspace

## What this is

A second, distinct Evidence Engine capability alongside the code-repair
coaching loop: a student uploads their own real course materials (via
native chat file-attachment in ChatGPT/Codex) and asks questions about
them, getting cited answers. Unlike the coaching loop's non-evaluative
guardrail (I6), this capability is *meant* to answer directly — see
`docs/superpowers/specs/2026-08-29-student-study-workspace-design.md` for
the full design and exactly which charter invariants this capability
required rewriting (I1, I2, I3, I5, I6).

## How it works

1. `add_course_material(workspace_id, filename, text)` — ingests text
   into a workspace. A heuristic data-boundary check
   (`app.domain.data_boundary`) rejects content that looks like a graded
   submission or exam key outright, and flags content that looks like an
   exam/quiz file or a discussion post for exclusion — neither is stored.
   Everything else is chunked (`app.domain.chunking`) and stored
   (`app.domain.workspace_store`).
2. `list_workspace_materials` / `remove_material` / `delete_workspace` —
   full student visibility and control over what's stored.
3. `answer_from_materials(workspace_id, question)` — deterministic
   keyword-overlap retrieval (`app.domain.retrieval`, no embeddings, no
   inference cost) returns cited excerpts; the host model (ChatGPT/Codex)
   synthesizes the actual answer from them.

## Known limitations, stated explicitly

- **Storage is in-process, not a database.** Data does not survive a
  process restart. A real persistence layer is future work once this
  capability is validated in use, not a redesign of what's here.
- **Plain text only.** PDF/docx extraction is out of scope for this
  slice; the exact mechanism by which ChatGPT/Codex would deliver a real
  file attachment's content to `add_course_material` is an open,
  unverified feasibility question (see the design doc's "Blocking
  unknown" section) — this implementation ships with the most-likely
  best-guess shape (already-extracted plain text as a string argument),
  matching this project's existing practice of shipping a spike's
  engineering half before its institutional/connectivity half is
  confirmed (`docs/MCP_SERVER.md`).
- **No "confirm anyway" override for flagged content.** If content is
  flagged (e.g. a filename containing "exam"), it is simply not stored —
  the student must remove whatever triggered the flag and re-upload.
  Adding an explicit confirm-and-store-anyway flow is a stated follow-up,
  not part of this slice.
- **The data-boundary heuristic is best-effort, not a guarantee** —
  pattern/keyword-based, the same honesty standard this project applies
  to its other heuristics (`app.domain.topic_matching`, the
  practice-selection heuristic in `docs/PROJECT_CHARTER.md`).
- **Retrieval is keyword-overlap, not semantic search** — a paraphrased
  question that shares no vocabulary with the source material may not
  retrieve anything relevant. A future revision could add embedding-based
  search as an explicitly separate, costed decision.

## Relationship to Canvas / `docs/CANVAS_INTEGRATION.md`

Independent of, and not a replacement for, the Canvas integration work.
This capability's upload path needs no institutional approval of any
kind — a student uploads only material they already have access to and
choose to share, distinct from either the mock Canvas topic-grounding
demo or the still-blocked real Canvas/LTI path (R5).
```

- [x] **Step 2: Commit**

```bash
git add docs/STUDY_WORKSPACE.md
git commit -m "Document the student study workspace capability"
```

---

### Task 10: Memory episodic entry + INDEX.md update

**Files:**
- Create: `memory/episodic/0030-student-study-workspace.md` (verify this number is still available — check `ls memory/episodic/ | tail -3` immediately before creating; the latest at plan-writing time is `0029-canvas-access-research-consent-upload-path.md`)
- Modify: `memory/INDEX.md`

- [x] **Step 1: Write the episodic entry**

Create `memory/episodic/0030-student-study-workspace.md` (adjust the number if a higher one already exists):

```markdown
# Task handoff: student study workspace (real materials, cited Q&A)

## Goal

Build a second, distinct Evidence Engine capability per explicit product
direction: a student uploads real course materials and gets cited
answers, going beyond the narrower "use uploads only to pick a coding
topic" option considered during brainstorming. Design:
`docs/superpowers/specs/2026-08-29-student-study-workspace-design.md`.

## Changed files

- `apps/api/app/domain/workspace_contracts.py` — new. `MaterialChunk`,
  `IngestResult`, `MaterialSummary`, `RetrievedExcerpt`.
- `apps/api/app/domain/chunking.py` — new. Plain-text-only chunking with
  provenance labels (chunk-index based; page/section-based extraction is
  future work).
- `apps/api/app/domain/data_boundary.py` — new. Heuristic reject/flag/
  allow classification enforcing a redrawn I1 boundary (see the design
  doc's invariant-change list) — never a guarantee, same honesty standard
  as this project's other heuristics.
- `apps/api/app/domain/workspace_store.py` — new. In-process, per-
  workspace storage. Explicitly not a database — stated limitation.
- `apps/api/app/domain/retrieval.py` — new. Deterministic keyword-overlap
  ranking, no embeddings, no inference cost (I3-consistent).
- `apps/api/app/domain/ingestion.py` — new. Orchestrates chunking →
  data-boundary check → storage.
- `apps/api/app/mcp_server.py` — adds 5 new tools: `add_course_material`,
  `list_workspace_materials`, `remove_material`, `delete_workspace`,
  `answer_from_materials`. Top-level server `instructions` updated.
- `apps/api/tests/test_chunking.py`, `test_data_boundary.py`,
  `test_workspace_store.py`, `test_retrieval.py`, `test_ingestion.py`,
  `test_workspace_guardrails.py` — new. `test_mcp_server.py` — extended.
- `docs/STUDY_WORKSPACE.md` — new, documents the capability and its
  stated limitations.

## Validation evidence

`make check` passes in full, confirmed by Task 11's full run — every new
domain module's tests, the extended MCP-server tests, and the new
workspace guardrail suite, plus zero regressions in the pre-existing
119 API + 5 web tests.

## Known limits / explicit scope decisions

- **Charter rewrite is a separate, deliberate next task, not part of
  this work.** `docs/PROJECT_CHARTER.md`'s thesis and invariants I1, I2,
  I3, I5, I6 all need new language reflecting this second capability —
  the design doc lists exactly what changes for each. Per explicit
  product decision during brainstorming, the whole product was sketched
  first; formalizing the charter language comes next, informed by what
  actually got built here rather than speculatively beforehand.
- The ingestion-shape feasibility spike (how ChatGPT/Codex deliver real
  file-attachment content to a tool call) remains unresolved — this
  implementation ships with plain text as the best-guess parameter shape,
  matching how this project already handles the still-unverified
  MCP-connectivity spike (`docs/MCP_SERVER.md`).
- In-process storage only; no persistence across a process restart.
- No PDF/docx extraction; no "confirm anyway" override for flagged
  content; retrieval is keyword-only, not semantic.

## Blocker

None for what's built — independent of Phase 1's Canvas/institutional
questions and of the kill-ratio work in `apps/api/app/domain/kill_ratio.py`
(untouched by this work).

## Owner

Shared team.

## Next action

1. Rewrite `docs/PROJECT_CHARTER.md`'s thesis and I1/I2/I3/I5/I6 per the
   design doc's explicit list — this is the immediately next task.
2. Once a real ChatGPT/Codex session exists (same blocker as Phase 1
   spike 1/2), verify `add_course_material`'s actual parameter shape
   against real attachment delivery and adjust if the best-guess plain-
   text shape turns out wrong.
3. Consider a persistence layer, PDF extraction, and a flagged-content
   confirm-and-store-anyway flow as explicit, separately-scoped follow-up
   work — not bundled into this slice.
```

- [x] **Step 2: Update `memory/INDEX.md`**

Replace the "Current handoff" line:

```
- `episodic/0029-canvas-access-research-consent-upload-path.md`
```

with (adjusting the number to match Step 1's actual filename):

```
- `episodic/0030-student-study-workspace.md`
```

Then, in the "Current state" living-summary paragraph, add one sentence
after the existing sentence about the research findings (the one ending
"...UofU's Digital Learning Technologies contact)."):

```
Per explicit product decision, this became real, buildable work rather
than staying a research note: a second, distinct capability now exists —
`apps/api/app/domain/{workspace_contracts,chunking,data_boundary,
workspace_store,retrieval,ingestion}.py` plus 5 new MCP tools
(`add_course_material`, `list_workspace_materials`, `remove_material`,
`delete_workspace`, `answer_from_materials`), documented in
`docs/STUDY_WORKSPACE.md`. It redefines Evidence Engine's mission (the
charter's "not a generic tutor" framing needs updating) and requires
rewriting invariants I1/I2/I3/I5/I6 — that rewrite is the next task,
deliberately sequenced after the product shape was built, not before.
```

- [x] **Step 3: Run the memory checker**

Run: `python3 scripts/memory_check.py`
Expected: `Validated N memory documents and rebuilt .cache/memory-index.sqlite`

- [x] **Step 4: Commit**

```bash
git add memory/episodic/ memory/INDEX.md
git commit -m "Record student study workspace capability in memory"
```

---

### Task 11: Full verification

**Files:** none (verification only)

- [x] **Step 1: Run the full project check**

Run: `make check`
Expected: `memory-check`, both lints, both typechecks, full API + web test suites, and smoke all pass with no failures.

- [x] **Step 2: Confirm the episodic entry's validation-evidence claim is accurate**

Re-read the "Validation evidence" section of
`memory/episodic/0030-student-study-workspace.md` (Task 10) against Step
1's actual `make check` output. If anything failed or was skipped,
correct the episodic entry to say so accurately before considering this
plan complete — this repo's memory discipline requires evidence claims to
be true, not aspirational.
