# Task handoff: live workspace foundation

## Goal

Replace the obsolete synthetic-only product boundary with a consented local
feature-delivery foundation for the Codex plugin, without shipping workspace
writes, commands, sync, or cloud services.

## Changed files

- `docs/PROJECT_CHARTER.md` and `docs/LIVE_WORKSPACE_CONTRACT.md` — define the
  live-workspace product surfaces, guidance modes, action approvals, adapter
  limits, and opt-in archive design.
- `plugins/evidence-engine-tutor/skills/feature-delivery/SKILL.md` — adds the
  consented feature workflow and explicit Observe/Guide/Pair/Delegate modes.
- `plugins/evidence-engine-tutor/scripts/workbench_snapshot.py` — returns a
  local read-only context snapshot with candidate paths, approval requirements,
  and uncollected change/test state.
- mapper, plugin manifest, contract check, tests, and plugin docs — extend
  source mapping through Java/Kotlin and cover the new foundation.

## Validation evidence

`python3 scripts/check_plugin_contract.py` and the plugin test discovery
command pass (11 plugin tests). `make check` passes with API lint/type/tests,
web lint/type/Vitest, three Playwright cases, and smoke tests; `pnpm build`
also produces the optimized web build. The Playwright cases cover retrying
context loading, malformed saved browser-state recovery, and the guided
diagnosis path through evidence-map rendering. A browser rehearsal loaded the
editable starter plan and coaching flow with no browser console warnings or
errors.

Adversarial mapper coverage verifies that file symlinks are not followed
outside the authorized workspace, named pipes are not read, and excluded
sensitive files count toward the deterministic total-byte cap. The personal
plugin was reinstalled at version `0.1.0+codex.20260828143143`; its cached
manifest, mapper, snapshot script, and feature-delivery skill match the
workspace sources. `git diff --check` passes.
The snapshot CLI against the public plugin fixture must show a candidate call
path and state that no code, diff, tests, network data, or archive content was
collected.

## Blocker

None. The workbench is a local script, not yet an MCP server or UI. Pair and
Delegate remain planning-only because text instructions are not approval
enforcement. Sync, OAuth, encryption, and a policy-enforced write/command
layer remain future vertical slices.

## Owner

Shared team.

## Next action

Build the MCP tool/UI around `workbench_snapshot.py`, then validate a single
approved TypeScript feature-delivery loop before adding Python or Java/Kotlin
runtime adapters.
