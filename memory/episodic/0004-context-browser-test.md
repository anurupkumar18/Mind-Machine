# Task handoff: context browser test

## Goal

Add browser-level regression coverage for the approved context failure-and-retry transition.

## Changed files

Added Playwright configuration, a mocked approved-context E2E flow, an E2E script, and a Vitest include rule that keeps browser specs out of unit tests.

## Validation evidence

The isolated browser run passed with `PLAYWRIGHT_PORT=3100 node ./node_modules/@playwright/test/cli.js test`. `pnpm test`, `pnpm lint`, and `pnpm typecheck` also pass.

## Constraints

The browser mock covers only the fixed approved context and candidate endpoints. It does not add repository input, persistence, arbitrary execution, or grading behavior.

## Blocker

Repository-wide validation may be affected by unrelated uncommitted API and fixture work already present in the shared tree.

## Owner

Shared team.

## Next action

Run `make check`, commit the browser-test slice if the shared tree is healthy, then wait for product direction before beginning a second allowlisted fixture slice.
