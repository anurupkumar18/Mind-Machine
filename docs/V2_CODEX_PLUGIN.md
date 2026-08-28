# V2 Codex plugin preview

`evidence-engine-tutor` moves codebase onboarding into Codex while preserving
the Evidence Engine's safety boundary.

## Slice 1: consent-first entry

The installable local plugin presents what will happen, why it helps, and what
it will not do before it can access workspace content. Consent is limited to
the conversation; this initial preview does not yet inspect files, run
commands, edit a project, add persistence, or produce a score.

The personal marketplace entry resolves to `~/plugins/evidence-engine-tutor`,
which is a local symlink to this repository's version-controlled plugin source.
This keeps manual preview installation separate from public distribution.

## Next slice

Add a read-only TypeScript/JavaScript and Python project map after explicit
consent, with source-path and symbol anchors. It must remain local to the
authorized Codex workspace and must not execute project code.
