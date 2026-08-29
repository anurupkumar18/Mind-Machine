# Canvas Mock Topic-Grounding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give the demo a working, honest demonstration of Canvas-grounded topic selection (VISION.md / I4) using fixture data shaped like the real Canvas API, without touching the confirmed-blocked real Canvas gate.

**Architecture:** A new `canvas_mock.py` module returns a fictional course (name, syllabus text, module titles) loaded from a checked-in fixture, shaped like real Canvas API responses. A new `topic_matching.py` module does deterministic keyword-overlap matching between module titles and each challenge's topic tags. Two changes to the MCP surface — a new `list_course_topics` tool, and an optional `topic` parameter on the existing `start_challenge` — expose this to the host model. Everything is additive; existing `challenge_id`-only callers are unaffected.

**Tech Stack:** Python 3.12, pydantic v2 (strict-typed contracts), pytest + `mcp.shared.memory` in-memory client/server streams (the existing test pattern in this repo), mypy strict, ruff.

**Design doc:** `docs/superpowers/specs/2026-08-28-canvas-mock-topic-grounding-design.md`

---

### Task 1: Canvas course fixture + contracts

**Files:**
- Create: `fixtures/canvas/course.json`
- Modify: `apps/api/app/domain/contracts.py` (append at end of file)

- [x] **Step 1: Create the fixture directory and file**

Create `fixtures/canvas/course.json`:

```json
{
  "course": {
    "id": 900001,
    "name": "CS 3500 — Foundations of Software Engineering",
    "course_code": "CS3500",
    "syllabus_body": "<p>Unit 3 covers graph traversal: BFS/DFS, visited-set invariants, and correctness arguments for search algorithms.</p>"
  },
  "modules": [
    {"id": 1, "name": "Unit 1: Recursion and Induction"},
    {"id": 2, "name": "Unit 2: Sorting and Divide-and-Conquer"},
    {"id": 3, "name": "Unit 3: Graph Traversal (BFS/DFS)"},
    {"id": 4, "name": "Unit 4: Dynamic Programming"}
  ]
}
```

- [x] **Step 2: Append the new contracts**

At the end of `apps/api/app/domain/contracts.py`, add:

```python


class CanvasModule(BaseModel):
    id: int
    name: str


class CanvasCourseContext(BaseModel):
    course_name: str
    syllabus_body: str
    modules: list[CanvasModule]


class TopicMatch(BaseModel):
    module_name: str
    matched_challenge_id: str | None
    matched_terms: list[str]


class CourseTopicsResponse(BaseModel):
    course_name: str
    syllabus_body: str
    topics: list[TopicMatch]
```

- [x] **Step 3: Typecheck**

Run: `cd apps/api && uv run mypy app`
Expected: `Success: no issues found`

- [x] **Step 4: Commit**

```bash
git add fixtures/canvas/course.json apps/api/app/domain/contracts.py
git commit -m "Add mock Canvas course fixture and Canvas/topic-match contracts"
```

---

### Task 2: `canvas_mock` module

**Files:**
- Create: `apps/api/app/domain/canvas_mock.py`
- Test: `apps/api/tests/test_canvas_mock.py`

- [x] **Step 1: Write the failing test**

Create `apps/api/tests/test_canvas_mock.py`:

```python
"""canvas_mock.py returns fixture data shaped like the real Canvas API
this stands in for until institutional approval lands (I4; memory/episodic/
0017, 0018)."""

from __future__ import annotations

from app.domain.canvas_mock import mock_course_context
from app.domain.contracts import CanvasCourseContext


def test_mock_course_context_returns_the_fixture_course() -> None:
    context = mock_course_context()

    assert isinstance(context, CanvasCourseContext)
    assert context.course_name == "CS 3500 — Foundations of Software Engineering"
    assert "graph traversal" in context.syllabus_body.lower()


def test_mock_course_context_includes_all_fixture_modules() -> None:
    context = mock_course_context()

    module_names = [module.name for module in context.modules]
    assert module_names == [
        "Unit 1: Recursion and Induction",
        "Unit 2: Sorting and Divide-and-Conquer",
        "Unit 3: Graph Traversal (BFS/DFS)",
        "Unit 4: Dynamic Programming",
    ]


def test_mock_course_context_never_includes_excluded_categories() -> None:
    """I4: assignments/quizzes/discussions/submissions/gradebook must never
    appear anywhere in the mock course, matching the real allowlist boundary."""
    payload = mock_course_context().model_dump()
    blob = str(payload).lower()

    for excluded in ("assignment", "quiz", "submission", "gradebook", "discussion"):
        assert excluded not in blob
```

- [x] **Step 2: Run the tests to verify they fail**

Run: `cd apps/api && uv run pytest tests/test_canvas_mock.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.domain.canvas_mock'`

- [x] **Step 3: Write the implementation**

Create `apps/api/app/domain/canvas_mock.py`:

```python
"""Mock stand-in for the Phase 4 Canvas read-only client (I4).

Real Canvas access is confirmed institutionally blocked (memory/episodic/
0017, 0018) -- this module returns fixture data shaped like the real
Canvas API responses it stands in for, so the topic-grounding pipeline
downstream of it is exercised honestly, and swapping in a real client
later (once institutional approval lands) means replacing this module's
implementation, not the pipeline that consumes it. No network call is
ever made here.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.domain.contracts import CanvasCourseContext, CanvasModule

ROOT = Path(__file__).resolve().parents[4]
COURSE_FIXTURE_PATH = ROOT / "fixtures" / "canvas" / "course.json"


@lru_cache(maxsize=1)
def mock_course_context() -> CanvasCourseContext:
    payload = json.loads(COURSE_FIXTURE_PATH.read_text(encoding="utf-8"))
    return CanvasCourseContext(
        course_name=payload["course"]["name"],
        syllabus_body=payload["course"]["syllabus_body"],
        modules=[CanvasModule(id=m["id"], name=m["name"]) for m in payload["modules"]],
    )
```

- [x] **Step 4: Run the tests to verify they pass**

Run: `cd apps/api && uv run pytest tests/test_canvas_mock.py -v`
Expected: 3 passed

- [x] **Step 5: Typecheck and lint**

Run: `cd apps/api && uv run mypy app && uv run ruff check .`
Expected: both clean

- [x] **Step 6: Commit**

```bash
git add apps/api/app/domain/canvas_mock.py apps/api/tests/test_canvas_mock.py
git commit -m "Add mock Canvas client (fixture-backed, I4 stand-in for Phase 4)"
```

---

### Task 3: `topic_matching` module

**Files:**
- Create: `apps/api/app/domain/topic_matching.py`
- Test: `apps/api/tests/test_topic_matching.py`

- [x] **Step 1: Write the failing test**

Create `apps/api/tests/test_topic_matching.py`:

```python
"""Topic-tag matching: deterministic keyword overlap, not semantic
understanding (docs/superpowers/specs/2026-08-28-canvas-mock-topic-
grounding-design.md)."""

from __future__ import annotations

import pytest

from app.domain.contracts import CanvasCourseContext, CanvasModule
from app.domain.topic_matching import (
    NoMatchingChallengeError,
    match_topics,
    resolve_challenge_for_topic,
)


def test_match_topics_matches_module_containing_a_tag() -> None:
    context = CanvasCourseContext(
        course_name="Test Course",
        syllabus_body="",
        modules=[CanvasModule(id=1, name="Unit 3: Graph Traversal (BFS/DFS)")],
    )

    matches = match_topics(context)

    assert len(matches) == 1
    assert matches[0].matched_challenge_id == "traversal-invariant-02"
    assert matches[0].matched_terms


def test_match_topics_matches_via_alias() -> None:
    context = CanvasCourseContext(
        course_name="Test Course",
        syllabus_body="",
        modules=[CanvasModule(id=1, name="BFS Practice Week")],
    )

    matches = match_topics(context)

    assert matches[0].matched_challenge_id == "traversal-invariant-02"
    assert "bfs" in matches[0].matched_terms


def test_match_topics_leaves_unmatched_module_honest_about_no_match() -> None:
    context = CanvasCourseContext(
        course_name="Test Course",
        syllabus_body="",
        modules=[CanvasModule(id=1, name="Unit 4: Dynamic Programming")],
    )

    matches = match_topics(context)

    assert matches[0].matched_challenge_id is None
    assert matches[0].matched_terms == []


def test_resolve_challenge_for_topic_success() -> None:
    assert resolve_challenge_for_topic("graph traversal review") == "traversal-invariant-02"


def test_resolve_challenge_for_topic_raises_when_nothing_matches() -> None:
    with pytest.raises(NoMatchingChallengeError):
        resolve_challenge_for_topic("dynamic programming")
```

- [x] **Step 2: Run the tests to verify they fail**

Run: `cd apps/api && uv run pytest tests/test_topic_matching.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.domain.topic_matching'`

- [x] **Step 3: Write the implementation**

Create `apps/api/app/domain/topic_matching.py`:

```python
"""Deterministic keyword-overlap topic matching -- a heuristic, not a
semantic-understanding claim. Same framing PROJECT_CHARTER.md uses for the
practice-selection heuristic generally, and the same substring-match idiom
`app.domain.policy.select_coaching_card` already uses in this codebase.
"""

from __future__ import annotations

from app.domain.contracts import CanvasCourseContext, TopicMatch

CHALLENGE_TOPIC_TAGS: dict[str, list[str]] = {
    "traversal-invariant-02": ["graph traversal", "bfs", "breadth-first", "visited"],
}


class NoMatchingChallengeError(ValueError):
    """Raised when a topic string matches no known challenge's tags."""


def _matched_terms(title: str, tags: list[str]) -> list[str]:
    lowered = title.lower()
    return [tag for tag in tags if tag in lowered]


def match_topics(context: CanvasCourseContext) -> list[TopicMatch]:
    matches: list[TopicMatch] = []
    for module in context.modules:
        matched_challenge_id: str | None = None
        matched_terms: list[str] = []
        for challenge_id, tags in CHALLENGE_TOPIC_TAGS.items():
            terms = _matched_terms(module.name, tags)
            if terms:
                matched_challenge_id = challenge_id
                matched_terms = terms
                break
        matches.append(
            TopicMatch(
                module_name=module.name,
                matched_challenge_id=matched_challenge_id,
                matched_terms=matched_terms,
            )
        )
    return matches


def resolve_challenge_for_topic(topic: str) -> str:
    for challenge_id, tags in CHALLENGE_TOPIC_TAGS.items():
        if _matched_terms(topic, tags):
            return challenge_id
    raise NoMatchingChallengeError(f"No challenge matches topic: {topic!r}")
```

- [x] **Step 4: Run the tests to verify they pass**

Run: `cd apps/api && uv run pytest tests/test_topic_matching.py -v`
Expected: 5 passed

- [x] **Step 5: Typecheck and lint**

Run: `cd apps/api && uv run mypy app && uv run ruff check .`
Expected: both clean

- [x] **Step 6: Commit**

```bash
git add apps/api/app/domain/topic_matching.py apps/api/tests/test_topic_matching.py
git commit -m "Add deterministic topic-tag matcher for Canvas-grounded challenge selection"
```

---

### Task 4: MCP surface — `list_course_topics` tool + `start_challenge(topic=...)`

**Files:**
- Modify: `apps/api/app/mcp_server.py`
- Modify: `apps/api/tests/test_mcp_server.py`

- [x] **Step 1: Write the failing tests**

Append to `apps/api/tests/test_mcp_server.py`:

```python


async def test_list_course_topics_tool_is_discoverable() -> None:
    async with connected_client() as session:
        tools = await session.list_tools()

    names = [tool.name for tool in tools.tools]
    assert "list_course_topics" in names


async def test_list_course_topics_returns_mock_course_with_a_matched_topic() -> None:
    async with connected_client() as session:
        result = await session.call_tool("list_course_topics", {})

    assert result.is_error is not True
    payload = json.loads(result.content[0].text)  # type: ignore[union-attr]
    assert payload["course_name"]
    matched = [t for t in payload["topics"] if t["matched_challenge_id"] == "traversal-invariant-02"]
    assert matched, "expected at least one mock module to match traversal-invariant-02"


async def test_start_challenge_accepts_topic_instead_of_challenge_id() -> None:
    async with connected_client() as session:
        result = await session.call_tool("start_challenge", {"topic": "graph traversal"})

    assert result.is_error is not True
    payload = json.loads(result.content[0].text)  # type: ignore[union-attr]
    assert payload["challenge_id"] == "traversal-invariant-02"


async def test_start_challenge_rejects_both_challenge_id_and_topic() -> None:
    async with connected_client() as session:
        result = await session.call_tool(
            "start_challenge", {"challenge_id": "traversal-invariant-02", "topic": "graph traversal"}
        )

    assert result.is_error is True


async def test_start_challenge_rejects_neither_challenge_id_nor_topic() -> None:
    async with connected_client() as session:
        result = await session.call_tool("start_challenge", {})

    assert result.is_error is True


async def test_start_challenge_rejects_unmatched_topic() -> None:
    async with connected_client() as session:
        result = await session.call_tool("start_challenge", {"topic": "dynamic programming"})

    assert result.is_error is True
```

- [x] **Step 2: Run the tests to verify they fail**

Run: `cd apps/api && uv run pytest tests/test_mcp_server.py -v`
Expected: FAIL — `list_course_topics` tool not found / `start_challenge()` rejects unexpected keyword `topic`

- [x] **Step 3: Update the imports and `KNOWN_CHALLENGES` area**

In `apps/api/app/mcp_server.py`, replace:

```python
from app.domain.challenge_token import InvalidTokenError, issue_token, verify_token
from app.domain.contracts import DiagnosisRequest
from app.domain.fixtures import fixture_data
from app.domain.runtime import canonical_next_frontier
from app.domain.sandbox import execute_repair
from app.domain.socratic import diagnose
```

with:

```python
from app.domain.canvas_mock import mock_course_context
from app.domain.challenge_token import InvalidTokenError, issue_token, verify_token
from app.domain.contracts import CourseTopicsResponse, DiagnosisRequest
from app.domain.fixtures import fixture_data
from app.domain.runtime import canonical_next_frontier
from app.domain.sandbox import execute_repair
from app.domain.socratic import diagnose
from app.domain.topic_matching import NoMatchingChallengeError, match_topics, resolve_challenge_for_topic
```

- [x] **Step 4: Replace `start_challenge` and add `list_course_topics`**

Replace the existing `start_challenge` tool:

```python
@mcp.tool()
def start_challenge(challenge_id: str) -> dict[str, Any]:
    """Issue a challenge instance, its token, and starting trace metadata."""
    if challenge_id not in KNOWN_CHALLENGES:
        raise ValueError(f"Unknown challenge id: {challenge_id!r}")

    data = fixture_data()
    frontier, _visited = canonical_next_frontier()
    return {
        "challenge_id": challenge_id,
        "challenge_token": issue_token(challenge_id),
        "objective": data["objective"],
        "start_node": data["start"],
        "expected_first_frontier": frontier,
        "trace": {"stage": "planner", "tool": "start_challenge"},
    }
```

with:

```python
@mcp.tool()
def list_course_topics() -> dict[str, Any]:
    """List the (mock) connected course's module/topic titles and which
    have a matching practice challenge today.

    Backed by fixture data, not a real Canvas connection -- real Canvas
    access is gated behind confirmed institutional approval (I4) and not
    yet available. See docs/CANVAS_INTEGRATION.md.
    """
    context = mock_course_context()
    response = CourseTopicsResponse(
        course_name=context.course_name,
        syllabus_body=context.syllabus_body,
        topics=match_topics(context),
    )
    payload = response.model_dump()
    payload["trace"] = {"stage": "planner", "tool": "list_course_topics"}
    return payload


@mcp.tool()
def start_challenge(challenge_id: str | None = None, topic: str | None = None) -> dict[str, Any]:
    """Issue a challenge instance, its token, and starting trace metadata.

    Exactly one of challenge_id or topic must be given. topic resolves to
    a challenge_id via the same keyword-overlap matcher list_course_topics
    uses (app.domain.topic_matching); see docs/CANVAS_INTEGRATION.md.
    """
    if (challenge_id is None) == (topic is None):
        raise ValueError("Provide exactly one of challenge_id or topic")
    if topic is not None:
        try:
            challenge_id = resolve_challenge_for_topic(topic)
        except NoMatchingChallengeError as error:
            raise ValueError(str(error)) from error
    assert challenge_id is not None

    if challenge_id not in KNOWN_CHALLENGES:
        raise ValueError(f"Unknown challenge id: {challenge_id!r}")

    data = fixture_data()
    frontier, _visited = canonical_next_frontier()
    return {
        "challenge_id": challenge_id,
        "challenge_token": issue_token(challenge_id),
        "objective": data["objective"],
        "start_node": data["start"],
        "expected_first_frontier": frontier,
        "trace": {"stage": "planner", "tool": "start_challenge"},
    }
```

- [x] **Step 5: Run the tests to verify they pass**

Run: `cd apps/api && uv run pytest tests/test_mcp_server.py -v`
Expected: all passed (3 original + 6 new = 9)

- [x] **Step 6: Typecheck and lint**

Run: `cd apps/api && uv run mypy app && uv run ruff check .`
Expected: both clean

- [x] **Step 7: Run the full existing suite to confirm no regression**

Run: `cd apps/api && uv run pytest -q`
Expected: all pass, no failures in `test_mcp_server_workflow.py` or `test_mcp_server_repair.py` (both call `start_challenge` with `challenge_id=` only, which is unaffected)

- [x] **Step 8: Commit**

```bash
git add apps/api/app/mcp_server.py apps/api/tests/test_mcp_server.py
git commit -m "Add list_course_topics MCP tool and topic-based start_challenge"
```

---

### Task 5: Guardrail suite extension (I7)

**Files:**
- Modify: `apps/api/tests/test_guardrails.py`

I7 requires any new host-facing tool to extend the shared guardrail suite before merge. `list_course_topics` and the topic-based path of `start_challenge` are new host-facing surfaces, so this task is mandatory, not optional polish.

- [x] **Step 1: Update the module docstring's tool count**

In `apps/api/tests/test_guardrails.py`, replace:

```python
I7: "Any new tool exposed to the host model must extend the shared
guardrail test suite before merge, including the answer-leakage/
over-helping behavioral eval set." This is that suite's first version,
covering the three pre-repair tools (`start_challenge`,
`submit_prediction`, `submit_diagnosis`). `submit_repair` is exempt by
design -- it's the one tool meant to carry evidence-only fields.
```

with:

```python
I7: "Any new tool exposed to the host model must extend the shared
guardrail test suite before merge, including the answer-leakage/
over-helping behavioral eval set." This suite covers `start_challenge`
(both its challenge_id and topic-based forms), `list_course_topics`,
`submit_prediction`, and `submit_diagnosis`. `submit_repair` is exempt by
design -- it's the one tool meant to carry evidence-only fields.
```

- [x] **Step 2: Write the failing tests**

Append to `apps/api/tests/test_guardrails.py`:

```python


async def test_list_course_topics_never_leaks_hidden_content() -> None:
    async with connected_client() as session:
        result = await session.call_tool("list_course_topics", {})

    _assert_no_leak(_payload(result))


async def test_start_challenge_via_topic_never_leaks_hidden_content() -> None:
    async with connected_client() as session:
        result = await session.call_tool("start_challenge", {"topic": "graph traversal"})

    _assert_no_leak(_payload(result))
```

These aren't expected to fail against Task 4's implementation (there's no code path from `canvas_mock`/`topic_matching` into `sandbox.py`'s hidden-test or secret material), but running them before declaring the task done is exactly what proves that structurally, not just by absence of a counterexample.

- [x] **Step 3: Run the tests to verify they pass**

Run: `cd apps/api && uv run pytest tests/test_guardrails.py -v`
Expected: all passed (existing tests + 2 new)

- [x] **Step 4: Lint**

Run: `cd apps/api && uv run ruff check .`
Expected: clean

- [x] **Step 5: Commit**

```bash
git add apps/api/tests/test_guardrails.py
git commit -m "Extend I6/I7 guardrail suite to cover list_course_topics and topic-based start_challenge"
```

---

### Task 6: `docs/CANVAS_INTEGRATION.md`

**Files:**
- Create: `docs/CANVAS_INTEGRATION.md`

`docs/PROJECT_CHARTER.md` already names this file as owed "written alongside the Canvas phase." This task writes it now, documenting the mock.

- [x] **Step 1: Write the file**

Create `docs/CANVAS_INTEGRATION.md`:

```markdown
# Canvas integration

## Status: mock mode

Real Canvas access is confirmed institutionally blocked. Two independent
paths were checked and closed (`memory/episodic/0017-canvas-spike-blocked-
on-institutional-access.md`, `memory/episodic/0018-workspace-admin-
contact-research.md`):

- UofU Canvas admins have disabled self-service personal-access-token
  generation; only a Canvas admin can issue one on request.
- OAuth2 developer-key registration (the credential a real per-student-
  consent integration needs) is admin-only for Canvas Cloud, per Canvas's
  own developer docs.
- Instructure's public "Free for Teacher" trial instance, which would have
  let this be verified against a real Canvas API independent of any
  institution, is discontinued.

Per invariant I4 (`docs/PROJECT_CHARTER.md`), no real Canvas content is
transmitted anywhere until UofU's privacy/security office and Canvas
administration confirm in writing that this data flow is approved. That
confirmation does not exist yet, so this integration runs entirely in
**mock mode**: everything described below reads a checked-in fixture, not
a real Canvas course, and no network call to any Canvas instance is ever
made.

## What's mocked and why

`apps/api/app/domain/canvas_mock.py` returns a fictional course
(`fixtures/canvas/course.json`) shaped like the real Canvas API responses
it stands in for (`GET /api/v1/courses/:id`, `GET /api/v1/courses/:id/
modules`), trimmed to exactly what I4's default allowlist would permit
from a real course: course name, syllabus text, and module/topic titles.
No assignment, quiz, discussion, submission, or gradebook data exists
anywhere in the fixture or the code that reads it — the excluded
categories simply aren't modeled, so the I4 boundary can't be crossed even
by accident.

`apps/api/app/domain/topic_matching.py` matches a Canvas module/topic
title against each known challenge's topic tags via case-insensitive
keyword overlap — a transparent heuristic, not a semantic-understanding
claim, in the same spirit as the practice-selection heuristic
`docs/PROJECT_CHARTER.md` already documents for content selection
generally.

Two MCP tools expose this to the host model:

- `list_course_topics()` — returns the mock course's module/topic titles
  and, for each, whether a matching practice challenge exists today.
  Honest about catalog coverage: a module with no match is still listed,
  with `matched_challenge_id: null`, rather than hidden.
- `start_challenge(challenge_id=None, topic=None)` — accepts either the
  original `challenge_id`, or a free-text `topic` resolved through the
  same matcher. Exactly one must be given.

## What changes when real access lands

Institutional approval unblocks a straightforward swap, not a redesign:

1. `canvas_mock.mock_course_context()`'s implementation is replaced with a
   real read-only OAuth2 client hitting the same two allowlisted Canvas
   endpoints (`CANVAS_BASE_URL` / `CANVAS_ACCESS_TOKEN`, already documented
   in `apps/api/.env.example`), returning the same `CanvasCourseContext`
   shape.
2. `topic_matching.py` and the MCP tool surface (`list_course_topics`,
   `start_challenge`) are unaffected by that swap — they consume
   `CanvasCourseContext`, not the fixture directly.
3. The untrusted-data handling the plan already specifies for real Canvas
   text (§4: stripped of HTML/scripts, length-capped, no following of
   external links, provenance preserved for citation) needs to be added at
   the point where the real client parses a live API response — the mock
   fixture is static, checked-in content, so that handling isn't exercised
   by mock mode today.
4. `scripts/verify_canvas_access.py` (Phase 1 spike 4) is the existing,
   ready, unused connectivity check for the moment a valid token exists.

## Non-goals of the current (mock) implementation

- No OAuth flow, consent screen, or token handling of any kind.
- No web UI — this is MCP/backend-only by explicit product decision.
- No second challenge wired through `start_challenge`'s `challenge_id`
  path (only `traversal-invariant-02` is reachable today; that's a
  separate, larger fixture-loading generalization, not part of this work).
```

- [x] **Step 2: Commit**

```bash
git add docs/CANVAS_INTEGRATION.md
git commit -m "Document the mock-mode Canvas integration (owed per PROJECT_CHARTER.md)"
```

---

### Task 7: `docs/IMPLEMENTATION_PLAN.md` §4 update

**Files:**
- Modify: `docs/IMPLEMENTATION_PLAN.md`

- [x] **Step 1: Add a note after the backup-ingestion-path bullets**

In `docs/IMPLEMENTATION_PLAN.md`, find this line (currently line 115):

```
- **What it explicitly is not**: literal HTML scraping or any technique that bypasses Canvas's actual access controls or OAuth consent flow — that would likely violate Canvas's terms of service and undermine the institutional-trust story I4 depends on. This path is bound by the identical approval gate and untrusted-data handling as the primary path; it changes how often context needs re-supplying, not what's allowed to flow.
```

Insert immediately after it (before the following `---`):

```

**Mock-mode demo (2026-08-28, distinct from the still-blocked real integration)**: `apps/api/app/domain/canvas_mock.py` + `topic_matching.py` demonstrate the topic-grounding *shape* — Canvas module/topic titles narrowing which practice challenge a student gets — entirely against a checked-in fixture (`fixtures/canvas/course.json`), never a real Canvas connection. This does not touch or weaken the I4 gate: no code path in the mock reaches a real Canvas endpoint, and R5 below is unchanged by its existence. Full detail: `docs/CANVAS_INTEGRATION.md`.
```

- [x] **Step 2: Update the R5 risk-register row**

Find the R5 row (search for `| R5 |`):

```
| R5 | Canvas institutional approval lead time | 1, 4 | Explicit Phase 1 blocking spike, needs a named owner | Open — needs an owner named. Confirmed blocked: UofU Canvas admins have disabled self-service access tokens (a UofU admin must generate one on request); Instructure's public trial instance is discontinued. Both self-service paths are dead ends; only a direct UofU Canvas-admin contact remains |
```

Replace with (appending one sentence to the last column, everything else unchanged):

```
| R5 | Canvas institutional approval lead time | 1, 4 | Explicit Phase 1 blocking spike, needs a named owner | Open — needs an owner named. Confirmed blocked: UofU Canvas admins have disabled self-service access tokens (a UofU admin must generate one on request); Instructure's public trial instance is discontinued. Both self-service paths are dead ends; only a direct UofU Canvas-admin contact remains. A mock-mode demo of the topic-grounding shape now exists (`docs/CANVAS_INTEGRATION.md`) — distinct from, and no substitute for, resolving this row |
```

- [x] **Step 3: Commit**

```bash
git add docs/IMPLEMENTATION_PLAN.md
git commit -m "Note the mock-mode Canvas demo in the implementation plan (§4, R5)"
```

---

### Task 8: Memory episodic entry + INDEX.md update

**Files:**
- Create: `memory/episodic/0028-canvas-mock-topic-grounding.md`
- Modify: `memory/INDEX.md`

The latest existing episodic file is `memory/episodic/0027-content-selection-policy.md`, so this is `0028`. Re-check `ls memory/episodic/` immediately before creating the file in case another session has added entries since this plan was written, and adjust the number if so.

- [x] **Step 1: Write the episodic entry**

Create `memory/episodic/0028-canvas-mock-topic-grounding.md` (adjust the number per the check above):

```markdown
# Task handoff: mock-mode Canvas topic-grounding demo

## Goal

Make Canvas-grounded topic selection (VISION.md, I4) demoable without
touching the confirmed-blocked real Canvas gate (`episodic/0017`,
`episodic/0018`). Design: `docs/superpowers/specs/2026-08-28-canvas-mock-
topic-grounding-design.md`.

## Changed files

- `fixtures/canvas/course.json` — new, a fictional course shaped like real
  Canvas API responses (`GET /courses/:id`, `GET /courses/:id/modules`),
  trimmed to I4's allowlist (course name, syllabus text, module/topic
  titles). No assignment/quiz/discussion/submission/gradebook data exists
  anywhere in it.
- `apps/api/app/domain/contracts.py` — adds `CanvasModule`,
  `CanvasCourseContext`, `TopicMatch`, `CourseTopicsResponse`.
- `apps/api/app/domain/canvas_mock.py` — new. Loads the fixture; explicit
  I4 stand-in for the real Phase 4 Canvas client, no network call.
- `apps/api/app/domain/topic_matching.py` — new. Deterministic
  keyword-overlap matching between Canvas module titles and each
  challenge's topic tags (`CHALLENGE_TOPIC_TAGS`), same transparent-
  heuristic idiom as `app.domain.policy.select_coaching_card`.
- `apps/api/app/mcp_server.py` — adds `list_course_topics()` tool; extends
  `start_challenge` to accept an optional `topic` (resolved via the same
  matcher) alongside the existing `challenge_id`, backward-compatible.
- `apps/api/tests/test_canvas_mock.py`, `test_topic_matching.py` — new.
  `test_mcp_server.py`, `test_guardrails.py` — extended (I7: any new
  host-facing tool must extend the shared guardrail suite).
- `docs/CANVAS_INTEGRATION.md` — new, the file `PROJECT_CHARTER.md` already
  named as owed "written alongside the Canvas phase." Documents mock mode
  and exactly what changes when real access lands.
- `docs/IMPLEMENTATION_PLAN.md` — §4 note + R5 risk-register row updated.

## Validation evidence

`make check` passes in full: all API tests (including the new
`test_canvas_mock.py`, `test_topic_matching.py`, and the `test_mcp_server.py`
/ `test_guardrails.py` extensions), both lints, both typechecks, web tests,
smoke — confirmed by Task 9's full run.

## Known limits / explicit scope decisions

- Only `traversal-invariant-02` has a topic-tag entry — the second
  challenge (`binary-search-invariant-01`) isn't wired through
  `start_challenge`'s `challenge_id` path at all yet (separate,
  pre-existing gap, not created or closed by this work).
- Topic matching is a documented heuristic (case-insensitive substring
  overlap), not semantic understanding — consistent with how this project
  already frames its other heuristics (practice selection,
  `PROJECT_CHARTER.md`).
- No web UI — MCP/backend-only, per explicit product decision made during
  brainstorming.

## Blocker

None — independent of Phase 1's open institutional questions (R5 unchanged
by this work; see the note added to `docs/IMPLEMENTATION_PLAN.md` §4).

## Owner

Shared team.

## Next action

If/when a second challenge gets wired through `start_challenge` (a
separate, pre-existing gap — see `episodic/0023`'s and `episodic/0024`'s
stated next actions), add its topic tags to
`topic_matching.CHALLENGE_TOPIC_TAGS` — the matcher and both MCP tools
already scale to more than one challenge without further changes.
```

- [x] **Step 2: Update `memory/INDEX.md`**

Replace the "Current handoff" line at the end of the file:

```
- `episodic/0027-content-selection-policy.md`
```

with (adjusting the filename per the actual number used in Step 1):

```
- `episodic/0028-canvas-mock-topic-grounding.md`
```

Then, in the "Current state" living-summary paragraph, add one sentence
after the existing Canvas-related sentence ("Canvas is Core but hard-gated
behind confirmed institutional approval."):

```
A mock-mode demo of the topic-grounding shape (fixture-backed, no real
Canvas connection) now exists — `apps/api/app/domain/canvas_mock.py`,
`topic_matching.py`, `docs/CANVAS_INTEGRATION.md` — distinct from, and no
substitute for, the still-blocked real integration.
```

- [x] **Step 3: Run the memory checker**

Run: `python3 scripts/memory_check.py`
Expected: `Validated N memory documents and rebuilt .cache/memory-index.sqlite` (exit 0, no forbidden-marker or missing-heading errors, and no stale-pointer error)

- [x] **Step 4: Commit**

```bash
git add memory/episodic/ memory/INDEX.md
git commit -m "Record mock-mode Canvas topic-grounding in memory"
```

---

### Task 9: Full verification

**Files:** none (verification only)

- [x] **Step 1: Run the full project check**

Run: `make check`
Expected: `memory-check`, both lints, both typechecks, full API + web test suites, and smoke all pass with no failures.

- [x] **Step 2: Manually exercise the new tools over the real stdio transport**

Run: `cd apps/api && uv run python3 -m app.mcp_server` in one terminal (leave it running), then in another terminal use any MCP-capable client (or the existing in-memory test pattern is sufficient evidence — this step is optional if Task 4/5's tests already exercise the real MCP protocol layer, which they do via `mcp.shared.memory`). Skip this step if short on time; Task 4/5's automated tests already prove protocol-level correctness.

- [x] **Step 3: Confirm the episodic entry's validation-evidence claim is accurate**

Re-read the "Validation evidence" section of `memory/episodic/0028-canvas-
mock-topic-grounding.md` (Task 8) against Step 1's actual `make check`
output. If `make check` failed or any suite was skipped, correct the
episodic entry to say so accurately before committing anything further —
this repo's memory discipline requires evidence claims to be true, not
aspirational.
