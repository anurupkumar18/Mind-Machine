# Task handoff: Socratic browser coverage

## Goal

Cover the complete fixture-defined diagnosis-to-confirmation recovery path in the browser.

## Changed files

- `apps/web/e2e/challenge-context.spec.ts` — adds a mocked browser flow for guided diagnosis, rejected timing recovery, and canonical conceptual confirmation.
- `apps/web/playwright.config.ts` — uses the same local origin as the Next development server so browser scripts load their client bundle reliably.
- `docs/DEMO_RUNBOOK.md` — describes the recovery prompt visible after a rejected lifecycle choice.

## Validation evidence

The browser spec asserts the first scaffold, accepted conceptual diagnosis, generic recovery prompt, canonical confirmation, and absence of repair implementation text. The recovery selector is scoped to the application alert so Next's route-announcer live region cannot mask it. It uses only the fixed approved fixture endpoints.

## Constraints and risks

No API contract, fixture, persistence, model use, user-code execution, repository input, or mastery score changes. The browser suite intentionally mocks the deterministic API contract; run the local API browser rehearsal before a hosted demonstration.

## Blocker

None.

## Owner

Shared team.

## Next action

Run the browser spec and `make check`, then commit and push the coverage slice. Complete browser review after each as required by the operating goal.
