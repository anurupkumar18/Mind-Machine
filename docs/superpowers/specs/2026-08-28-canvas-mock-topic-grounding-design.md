# Canvas mock topic-grounding — design

## Status

Approved for implementation. Written 2026-08-28.

## Problem

`docs/VISION.md` and `docs/PROJECT_CHARTER.md` (I4) describe Canvas as the
mechanism that grounds practice-challenge selection in what a student's own
course is actually covering — read-only, narrowed to syllabus/module-topic
titles. Real Canvas access is confirmed institutionally blocked
(`memory/episodic/0017-canvas-spike-blocked-on-institutional-access.md`,
`memory/episodic/0018-workspace-admin-contact-research.md`): UofU disabled
self-service tokens, OAuth2 dev-key registration is admin-only, and
Instructure's public trial instance is discontinued. I4 hard-gates any real
Canvas content until institutional approval is confirmed in writing — no
engineering path exists around that gate, and this work does not attempt
one.

For the demo, the goal is to make the *shape* of Canvas grounding usable and
demonstrable — a student's course context narrowing which practice challenge
they get — using fixture data that never claims to be real, so the demo
shows the mechanism without touching the gate at all.

## Non-goals

- No real Canvas API calls, OAuth flow, or token handling. `CANVAS_BASE_URL`
  / `CANVAS_ACCESS_TOKEN` in `.env.example` stay unused.
- No web UI changes. This is MCP/backend-only, per explicit product
  decision.
- No expansion of the fixture-loading layer to wire a second challenge
  (`binary-search-invariant-01`) into the MCP surface. That fixture-loading
  generalization is separate, larger work with its own scope, and today
  only `traversal-invariant-02` is reachable through `start_challenge`. This
  feature is built to scale cleanly if/when a second challenge is wired in,
  but doesn't do that wiring itself.
- No changes to `apps/api/app/domain/kill_ratio.py` or its tests — that
  work is in progress in a parallel session.

## Architecture

A new, explicitly-labeled *mock* Canvas layer occupies the same seam the
real Phase 4 Canvas client will occupy, so replacing the mock with a real
client later is a swap, not a rewrite.

```
list_course_topics()  --calls-->  canvas_mock.mock_course_context()
        |                                   |
        |                                   v
        |                         fixtures/canvas/course.json
        |                         (fictional course, Canvas-API-shaped,
        |                          I4 allowlist fields only)
        v
  topic_matching.match_topics(course_context)
        |
        v
  [{module_title, matched_challenge_id | None, matched_terms}]


start_challenge(challenge_id=None, topic=None)
        |  if topic given, resolve via the same matcher
        v
  existing start_challenge body (unchanged for challenge_id path)
```

### `fixtures/canvas/course.json`

A single fictional course, shaped like the real Canvas API responses it
stands in for (`GET /api/v1/courses/:id`, `GET /api/v1/courses/:id/modules`),
trimmed to exactly what I4's default allowlist permits:

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

No assignment, quiz, discussion, submission, or gradebook data exists
anywhere in this fixture — the boundary I4 draws can't be crossed even by
accident, because the excluded categories simply aren't modeled.

`syllabus_body` is treated as untrusted text on principle (matches the
plan's stated handling for real Canvas text, §4) even though it's static
fixture content: length-capped read, no HTML execution, no link-following.
For this mock it is not actually used by the matcher (module titles are
sufficient and simpler to reason about) — it's included in the fixture and
surfaced in `list_course_topics()`'s response for demo realism (a real
Canvas response would include it), with a code comment noting it's
currently display-only.

### `apps/api/app/domain/canvas_mock.py`

```python
"""Mock stand-in for the Phase 4 Canvas read-only client (I4).

Real Canvas access is confirmed institutionally blocked (memory/episodic/
0017, 0018) — this module returns fixture data shaped like the real
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

### Topic tags + matcher

Challenge topic tags live in a small, explicit module-level mapping —
deliberately not folded into `ChallengeTemplate`/`fixtures.py`, to avoid
touching shared fixture-loading internals other in-flight work may also be
touching:

```python
# apps/api/app/domain/topic_matching.py

CHALLENGE_TOPIC_TAGS: dict[str, list[str]] = {
    "traversal-invariant-02": ["graph traversal", "bfs", "breadth-first", "visited"],
}
```

Matching is a case-insensitive substring check between a module title (and,
for robustness, tag aliases like `"bfs"`) and each challenge's tag list —
the same transparent-heuristic idiom `policy.select_coaching_card` already
uses in this codebase, not a semantic-understanding claim. First match wins;
documented as a heuristic in the module docstring, same framing this
project already uses for the practice-selection heuristic in
`docs/PROJECT_CHARTER.md`.

```python
def match_topics(context: CanvasCourseContext) -> list[TopicMatch]:
    """Deterministic keyword-overlap match, not semantic understanding.

    Mirrors the heuristic framing PROJECT_CHARTER.md uses for practice
    selection generally: transparent, documented, not a claim of
    comprehension.
    """
```

Returns one `TopicMatch` per module: `{module_name, matched_challenge_id:
str | None, matched_terms: list[str]}`. A module with no matching challenge
still appears, with `matched_challenge_id=None` — the response is honest
about catalog coverage rather than hiding gaps.

### New/changed contracts (`apps/api/app/domain/contracts.py`, additive)

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

### MCP surface (`apps/api/app/mcp_server.py`, additive + one backward-compatible extension)

```python
@mcp.tool()
def list_course_topics() -> dict[str, Any]:
    """List the (mock) connected course's module/topic titles and which
    have a matching practice challenge today.

    Backed by fixture data, not a real Canvas connection — real Canvas
    access is gated behind confirmed institutional approval (I4) and not
    yet available. See docs/CANVAS_INTEGRATION.md.
    """
    context = mock_course_context()
    matches = match_topics(context)
    return CourseTopicsResponse(
        course_name=context.course_name,
        syllabus_body=context.syllabus_body,
        topics=matches,
    ).model_dump() | {"trace": {"stage": "planner", "tool": "list_course_topics"}}


@mcp.tool()
def start_challenge(challenge_id: str | None = None, topic: str | None = None) -> dict[str, Any]:
    """Issue a challenge instance, its token, and starting trace metadata.

    Exactly one of challenge_id or topic must be given. topic resolves via
    the same keyword-overlap matcher list_course_topics uses.
    """
    if (challenge_id is None) == (topic is None):
        raise ValueError("Provide exactly one of challenge_id or topic")
    if topic is not None:
        challenge_id = resolve_challenge_for_topic(topic)  # raises ValueError if no match
    if challenge_id not in KNOWN_CHALLENGES:
        raise ValueError(f"Unknown challenge id: {challenge_id!r}")
    # ... unchanged from here
```

`resolve_challenge_for_topic` lives in `topic_matching.py` alongside
`match_topics`, reusing `CHALLENGE_TOPIC_TAGS` directly against the raw
topic string (not routed through the mock course fixture), so a caller can
pass a free-text topic even without first calling `list_course_topics()`.

## Error handling

- `start_challenge` with neither or both of `challenge_id`/`topic` given:
  `ValueError`, existing MCP error-surfacing behavior (proven in
  `test_mcp_server.py`'s unknown-challenge case).
- `start_challenge(topic=...)` with no matching challenge: `ValueError`
  naming the topic, distinct message from the unknown-challenge-id case.
- `list_course_topics()` has no error paths — the fixture always loads
  (same `lru_cache` pattern as `fixtures.fixture_data`, which has no
  existing error handling either, since the fixture is a checked-in file
  not runtime input).

## Testing

- `apps/api/tests/test_canvas_mock.py` — `mock_course_context()` returns
  the expected shape from the fixture; no network access attempted (assert
  via `pytest-socket` if already in use elsewhere in the suite, otherwise a
  straightforward shape/content assertion is sufficient since the module
  contains no networking code at all).
- `apps/api/tests/test_topic_matching.py` — exact match, alias match
  (`"bfs"`), no-match module, `resolve_challenge_for_topic` success and
  `ValueError` cases.
- `apps/api/tests/test_mcp_server.py` — extend with: `list_course_topics()`
  tool-discovery + real-call assertions over the in-memory MCP streams
  (same pattern as the existing `start_challenge` test); `start_challenge`
  called with `topic=` instead of `challenge_id=`; the both-given and
  neither-given error cases.
- `apps/api/tests/test_guardrails.py` (I7 — mandatory for any new
  host-facing tool): extend `LEAK_MARKERS` sweep to cover
  `list_course_topics()` and topic-based `start_challenge()` calls. These
  tools structurally cannot reach hidden-test or reference-implementation
  content (no code path from `canvas_mock`/`topic_matching` touches
  `sandbox.py`'s internals), so the new tests assert that structural fact
  the same way the existing suite does for the three pre-repair tools —
  not a single-input spot check.

## Docs and memory

- `docs/CANVAS_INTEGRATION.md` — new file, the one `PROJECT_CHARTER.md`
  already names as owed "written alongside the Canvas phase." Documents:
  this is mock-mode (fixture-backed, no real Canvas connection), exactly
  which fields the fixture models and why (I4 allowlist), and exactly what
  changes when real institutional access lands (swap
  `canvas_mock.mock_course_context()`'s implementation for a real read-only
  OAuth2 client hitting the same allowlisted endpoints; `topic_matching.py`
  and the MCP surface are unaffected by that swap).
- `docs/IMPLEMENTATION_PLAN.md` §4 — add a short note that a mock-mode
  demo of the topic-grounding shape now exists, distinct from the still-
  blocked real integration (R5 unchanged).
- New episodic memory entry (`memory/episodic/0025-canvas-mock-topic-
  grounding.md`) following this repo's existing per-unit-of-work practice,
  and `memory/INDEX.md`'s current-state block updated.

## Open questions

None — scope was narrowed through the brainstorming conversation (backend-
only, no second-challenge wiring, no touching `kill_ratio.py`).
