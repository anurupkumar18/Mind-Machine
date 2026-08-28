# Task handoff: context recovery

## Goal

Make approved challenge-context loading recoverable when the local API is temporarily unavailable.

## Changed files

Added an explicit context-load failure state and retry action, extracted the fixed approved-context loader, added focused component coverage, and styled the error panel.

## Validation evidence

`cd apps/web && pnpm test`, `pnpm lint`, and `pnpm typecheck` pass.

## Constraints

Retry reloads only the fixed `public-graph-traversal` context and candidate. It adds no user inputs, persistence, arbitrary execution, or grading behavior.

## Blocker

None.

## Owner

Shared team.

## Next action

Run `make check`, commit the recovery slice, then add browser-level coverage for the failure-to-retry transition.
