# Task handoff: Codex plugin consent preview

## Goal

Begin V2 with an installable private Codex plugin that explains and obtains
explicit consent before any future workspace inspection.

## Changed files

- `plugins/evidence-engine-tutor/` — marketplace-installable plugin manifest,
  consent-first onboarding skill, and manual rehearsal guide.
- `scripts/check_plugin_contract.py` — verifies that slice one has no MCP or
  app tool layer and retains the consent/no-write/no-score boundary.
- `README.md` and `docs/V2_CODEX_PLUGIN.md` — position the web app as the demo
  and document the private preview boundary.

## Validation evidence

Run the plugin validator, the narrow contract check, and `make check` before
commit. Reinstall through the personal marketplace, then test in a new Codex
conversation: it must request an exact `yes` and inspect no files or commands.

## Constraints and risks

The personal marketplace resolves `~/plugins/evidence-engine-tutor`; that path
is a local symlink to the version-controlled source. The plugin is
instruction-only in this slice, so its consent acknowledgement is conversational
session state rather than durable application state.

## Blocker

None.

## Owner

Shared team.

## Next action

After manual confirmation, add only a consent-gated, read-only source mapper
for TypeScript/JavaScript and Python. Do not add command execution or editing.
