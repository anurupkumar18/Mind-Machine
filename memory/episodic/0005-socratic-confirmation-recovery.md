# Task handoff: Socratic confirmation recovery

## Goal

Make an expected rejected lifecycle-timing confirmation recover with instructional guidance while keeping service failures generic.

## Changed files

- `apps/web/lib/api.ts` — expose the HTTP status on existing generic service errors.
- `apps/web/app/page.tsx` — map only the fixture's expected `400` confirmation rejection to retry guidance.
- `apps/web/tests/api.test.ts` — cover that status mapping.

## Validation evidence

- Live browser rehearsal completed the public BFS context, plan, prediction, Socratic scaffold, canonical confirmation, retry scheduling, and evidence map.
- A rejected `frontier_exit` timing visibly says: "Choose the lifecycle event that preserves the invariant."
- `make check` passed: memory validation, API lint/type/tests, web lint/type/unit tests, and smoke tests.

## Constraints and risks

No fixture, API response shape, persistence, model use, code disclosure, arbitrary execution, or mastery score changed. This recovery patch is interleaved with the shared uncommitted Socratic-coach slice, so do not commit it separately.

## Blocker

None for validation. Commit ownership remains shared because the related Socratic-coach work is already uncommitted in the tree.

## Owner

Shared team.

## Next action

Review and commit the complete Socratic-coach slice together, then add browser automation for its diagnosis-to-confirmation path before beginning another allowlisted fixture.
