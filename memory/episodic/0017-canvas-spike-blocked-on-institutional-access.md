# Task handoff: Phase 1 spike 4 — Canvas institutional decision (unresolved)

## Goal

Obtain a Canvas sandbox/dev key and an explicit (even informal) answer on
the §4 data-policy question — or, per the plan's own Definition of Done,
document clearly that it's unresolved and keep Canvas fully gated rather
than silently skip it. Phase 1, task 4 (`docs/IMPLEMENTATION_PLAN.md` §6).

## Changed files

- `apps/api/.env.example` — documents `CANVAS_BASE_URL`/`CANVAS_ACCESS_TOKEN`
  and the I4 scope note; no real values anywhere.
- `scripts/verify_canvas_access.py` — new, minimal read-only connectivity
  check, unused so far (no valid token exists to run it against).
- `docs/IMPLEMENTATION_PLAN.md` — R5 row in the risk register updated with
  this outcome.

## What was attempted

Two independent self-service paths to a working Canvas API token, both
dead ends, in order:

1. **UofU's own Canvas instance.** The account holder has an active UofU
   Canvas account, but the institution's Canvas admins have disabled
   self-service access-token generation for that account — Canvas's own
   "Approved Integrations" page shows the standard `+ New Access Token`
   control replaced with a notice: administrators must generate a token on
   the user's behalf on request. This is itself a useful, concrete data
   point for R5, not just a dead end: it names the actual next action
   (someone contacts a UofU Canvas admin) rather than leaving it abstract.
2. **Instructure's public "Free for Teacher" trial instance**
   (`canvas.instructure.com`), which would have let us build/verify a real
   Canvas API client against a real Canvas API without any institutional
   dependency. Instructure discontinued that program; signup is closed.

A third path was then checked and closed: Canvas's own official developer
docs (`developerdocs.instructure.com/services/canvas/oauth2/file.oauth`)
confirm that OAuth2 developer-key registration — the credential a real,
per-student-consent integration would actually use, not a personal token —
is **also admin-only**: "For Canvas Cloud (hosted by Instructure),
developer keys are issued by the admin of the institution." Same wall as
path 1, not a way around it. The same docs also state outright that
"asking any other user to manually generate a token and enter it into your
application is a violation of Canvas' API Policy" — confirming the plan's
existing design (real OAuth2 consent per student, never collecting
personal tokens from users) is the only compliant path, and that every
route to real Canvas access — this spike's or the eventual product's —
runs through the same UofU Canvas admin approval.

No PII from the account holder's real UofU Canvas account (name, email,
other integrations visible on that settings page) is recorded here or
anywhere else in this repo, per invariant I5.

## What's built and ready, unblocked by this outcome

- `apps/api/.env.example` documents the two env vars a Canvas client would
  read (`CANVAS_BASE_URL`, `CANVAS_ACCESS_TOKEN`) and the I4 scope note.
  `apps/api/.env` exists locally (gitignored) with the placeholder values,
  unfilled — confirmed via `git status`/grep that no real token was ever
  entered, read, or handled by this agent.
- `scripts/verify_canvas_access.py` — a minimal, read-only connectivity
  check (`GET /api/v1/users/self` only, no course/syllabus/module content
  touched). Never prints the token; unit-verified locally that its request
  builder and response summarizer work correctly (ad hoc, not committed as
  a pytest suite — matches the existing untested-operational-script pattern
  of `scripts/memory_check.py` / `scripts/check_plugin_contract.py`). Ready
  to run the moment a valid token exists, from either instance.

## Validation evidence

No live Canvas API call was made — there is no valid token to make one
with. `make check` is unaffected by this episode (no app code changed).

## Blocker

Both remaining paths to a token require a human, institutional action, not
more engineering:
1. Someone contacts a UofU Canvas administrator directly and requests a
   token be generated for this purpose. That person owns R5/R11's
   institutional side — no one has volunteered for it yet.
2. The §4 data-policy question — whether UofU's privacy/security office
   has approved this specific data flow — is entirely separate from having
   a working token, and remains completely unaddressed regardless of how
   the token question resolves.

Per §6's Definition of Done, this is being explicitly logged as
**unresolved, gated** rather than skipped. Per I4, this changes nothing
about current behavior: Canvas was already fully gated (no real Canvas
content flows anywhere) before this attempt, and stays that way.

## Owner

Shared team — needs a named UofU institutional contact per
`docs/IMPLEMENTATION_PLAN.md` §9 (R5). Still unnamed.

## Next action

Not resolvable by continuing to write code. The productive next
engineering steps are the ones that don't depend on this spike:
Phase 2 (property-DSL catalog on top of the sandbox spike, `episodic/0015`)
or Phase 3 (expanding `apps/api/app/mcp_server.py` toward the full 4-tool
surface, `episodic/0016`). Someone on the team reaching out to a UofU
Canvas administrator is the only thing that unblocks the Canvas half.
