# Task handoff: code-context workspace

## Goal

Expose the approved public `CodeContext` and curated BFS traversal candidate in the learner workspace.

## Changed files

Added typed approved-context API helpers, a read-only `ChallengeContext` workspace component and styles, page data loading, and endpoint-focused web tests.

## Validation evidence

`cd apps/web && pnpm test`, `pnpm lint`, and `pnpm typecheck` pass.

## Constraints

The UI uses the fixed `public-graph-traversal` fixture only. It adds no repository input, source execution, persistence, or grading behavior.

## Blocker

None.

## Owner

Shared team.

## Next action

Run `make check`, commit this slice, then consider a second allowlisted fixture or a browser-level context-panel check.
