# Evidence Engine Tutor

Private Codex-plugin preview for consent-first codebase onboarding.

After explicit in-conversation consent, this preview runs its own bounded
mapper over JavaScript, TypeScript, Python, `package.json`, and `pyproject.toml`.
It never imports or executes project code, runs project commands, edits files,
persists learner data, adds telemetry, scores, or determines pass/fail.

## Manual rehearsal

1. Install `evidence-engine-tutor` from the `personal` marketplace.
2. Start a new Codex conversation in a workspace.
3. Invoke `evidence-engine-tutor` and ask to start a read-only codebase
   onboarding session.
4. Reply `yes`; confirm that the returned map names only supported files,
   metadata (including nested app manifests), symbols, imports, and entry
   points, with a single `path:L<line>` anchor per factual statement.
5. Confirm that it says no project code ran, no files changed, and no learner
   data was stored.

The next slice will add learner-selected Explorer, Builder, and Reviewer
practice interactions over this map.
