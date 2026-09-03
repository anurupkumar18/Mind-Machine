# Canvas integration

> **Document status:** current mock behavior, historical access investigation, and
> future possibilities coexist here. None proves production permission or selects
> the final architecture. See
> [`research/INITIAL_RESEARCH_AND_INSPIRATION.md`](research/INITIAL_RESEARCH_AND_INSPIRATION.md)
> for earlier leads and explicit discrepancies that require fresh verification.

## September 2026 product direction (not implemented)

The team has agreed to explore Canvas as one possible entry point into a broader,
institution-supported Evidence Engine experience. The north star is not merely a
one-time API import: when a student enrolls, a professor- and IT-approved class
package could make the right skills, guardrails, hooks, tools, plugins, MCP servers,
and course context available with minimal setup. A companion browser extension is
also an option to investigate where it is permitted and meaningfully improves the
student experience.

Neither Canvas provisioning nor a browser extension is approved, verified, or
selected as the architecture. Both must be evaluated with professors and university
IT for consent, privacy, security, data retention, procurement, support ownership,
and platform-policy compliance. They are complementary possibilities, not permission
workarounds. The current mock-only status and invariant I4 remain unchanged.

See [`TEAM_PRODUCT_DIRECTION.md`](TEAM_PRODUCT_DIRECTION.md) for the complete group
decision and the boundary between product direction and current capability.

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
