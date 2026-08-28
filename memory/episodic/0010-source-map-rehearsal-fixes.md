# Task handoff: source-map rehearsal fixes

## Goal

Correct the nested-metadata and duplicated-anchor issues found during the first
manual slice-2 rehearsal.

## Changed files

- `plugins/evidence-engine-tutor/scripts/map_workspace.py` — discovers nested
  `package.json` and `pyproject.toml` files while honoring the same ignored
  paths as source scanning.
- `plugins/evidence-engine-tutor/skills/codebase-onboarding/SKILL.md` — asks
  for one `path:L<line>` anchor per fact and cautious "candidate entry point"
  wording.
- `plugins/evidence-engine-tutor/tests/` and product docs — cover nested app
  metadata and document the corrected learner-visible behavior.

## Validation evidence

Run mapper tests, plugin checks, `make check`, reinstall the plugin, and use a
new Codex task. The workspace rehearsal should now list
`apps/api/pyproject.toml` and `apps/web/package.json` and use one anchor per
statement.

## Constraints and risks

The mapper remains a source-text-only utility; the skill can describe only
relationships visible in its output and should not claim semantic certainty.

## Blocker

None.

## Owner

Shared team.

## Next action

After manual confirmation, implement the learner-selected Explorer, Builder,
and Reviewer micro-exploration without adding project command execution.
