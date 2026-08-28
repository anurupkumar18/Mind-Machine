# Task handoff: map practice modes

## Goal

Turn the consented source map into transparent Explorer, Builder, and Reviewer
micro-explorations without expanding the read-only boundary.

## Changed files

- `plugins/evidence-engine-tutor/skills/codebase-onboarding/SKILL.md` —
  defines the three learner-selected views, their status/why/boundary language,
  and non-evaluative follow-ups.
- `plugins/evidence-engine-tutor/scripts/map_workspace.py` — returns import
  line anchors so each view can cite visible map evidence precisely.
- plugin tests, contract check, README, and V2 guide — verify/document the
  modes and their no-score/no-extra-inspection behavior.

## Validation evidence

Run mapper tests, plugin validation, contract check, and `make check`. In a
new Codex task, consent, map, then choose each view. It must ask only the
documented bounded question and use no new workspace inspection.

## Constraints and risks

Modes reuse conversation-local map data. They cannot establish runtime truth,
so all language remains prediction, observation, or review note rather than a
correctness decision.

## Blocker

None.

## Owner

Shared team.

## Next action

After manual feedback, add the first focused source-path walkthrough or revise
the mode UX; do not add project command execution or editing.
