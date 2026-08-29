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
  Top-level server `instructions` string updated to mention the new tool.
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
  `PROJECT_CHARTER.md`). A code-quality review during implementation noted
  the matcher's "first match wins" tie-break (by dict insertion order) is
  currently undocumented in-code — harmless with today's single challenge
  entry, but worth a one-line comment in `topic_matching.py` when a second
  challenge's tags are added.

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
already scale to more than one challenge without further changes. At that
point also add the tie-break-order comment noted above.
