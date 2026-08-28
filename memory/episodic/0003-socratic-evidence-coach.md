# Task handoff: Socratic evidence coach

## Goal

Layer the approved V2 Socratic coaching flow over the existing deterministic BFS evidence loop without changing its public-fixture boundary.

## Changed files

Added a fixture-defined diagnostic runbook, stateless diagnosis and confirmation API endpoints, browser-only structured session state, and a gated UI that removes repair code and direct repair instructions.

## Validation evidence

`make check` verifies the fixture policy, API diagnosis escalation, canonical confirmation, and web contracts.

## Constraints

No model API, identity, persistence, repository input, arbitrary execution, or mastery score was added. Canonical fixture execution remains the only evidence source.

## Blocker

None.

## Owner

Shared team.

## Next action

Run a live browser rehearsal using the revised demo runbook before declaring V2 presentation-ready.
