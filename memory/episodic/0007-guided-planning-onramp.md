# Task handoff: guided planning onramp

## Goal

Replace the blank-plan experience with a transparent, learner-selected support level and editable novice starter plan.

## Changed files

- `apps/web/components/PlanCommitment.tsx` — explains why a plan is collected, supplies plain-language prompt help, and provides guided, supported, and independent modes.
- `apps/web/app/page.tsx` and `apps/web/lib/types.ts` — keep the selected support level in browser session storage only, restore browser state after hydration, and expose the editable starter plan.
- `apps/web/app/styles.css` — presents support choices as responsive, scannable cards.
- `apps/web/tests/plan-commitment.test.tsx` and `apps/web/e2e/challenge-context.spec.ts` — cover the guided onramp contract and updated end-to-end action label.
- `README.md` and `docs/DEMO_RUNBOOK.md` — document the support boundary and revised test path.

## Validation evidence

The UI makes clear that support changes guidance only. Browser state is restored after the initial render so the learner's selected support level does not create a server/client hydration mismatch. The learner must still explicitly save an editable plan, predict an observable graph state, and use deterministic fixture evidence.

## Constraints and risks

Only browser session storage is used. The one approved BFS fixture remains unchanged, so this is a support-level selector rather than a false claim of distinct problem difficulty. Broader challenge difficulty requires additional allowlisted fixture variants.

## Blocker

None.

## Owner

Shared team.

## Next action

Run web unit and browser checks, inspect the guided path in a real browser, then run `make check` before committing.
