# Task handoff: read-only source map

## Goal

Extend the private Codex plugin so an exact learner `yes` enables a bounded,
read-only TypeScript/JavaScript/Python project map.

## Changed files

- `plugins/evidence-engine-tutor/scripts/map_workspace.py` — deterministic
  metadata and source-text mapper; it never imports, executes, or writes
  project code.
- `plugins/evidence-engine-tutor/skills/codebase-onboarding/SKILL.md` — turns
  consent into a mapped, anchored explanation and explicit next-mode choice.
- `plugins/evidence-engine-tutor/tests/` and `scripts/check_plugin_contract.py`
  — public fixture and boundary checks for paths, symbols, imports, and no
  arbitrary execution.
- `README.md`, `docs/V2_CODEX_PLUGIN.md`, and `docs/PROJECT_CHARTER.md` —
  document the separate local, explicit-consent adapter boundary.

## Validation evidence

Run the mapper unit test, plugin contract checker, plugin validator, and
`make check`. Reinstall from the personal marketplace and test in a new Codex
conversation: exact `yes` must return only bounded map information and repeat
that no project code ran or files changed.

## Constraints and risks

The mapper reads local source text after consent; it is not a hosted input and
does not execute it. Its symbol/import extraction is intentionally lightweight
and can miss dynamic relationships. It supports only JavaScript, TypeScript,
and Python.

## Blocker

None.

## Owner

Shared team.

## Next action

After manual confirmation, implement a learner-selected Explorer, Builder, or
Reviewer micro-exploration over the existing map. Do not add command execution
or editing.
