# Evidence Engine Tutor

Private Codex-plugin foundation for consented codebase onboarding and
collaborative feature delivery.

After explicit in-conversation consent, this preview runs its own bounded
mapper over JavaScript, TypeScript, Python, Java, Kotlin, `package.json`, and
`pyproject.toml`.
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
6. Reply `Explorer`, `Builder`, and `Reviewer` in separate new conversations.
   Each should explain its purpose, cite only the existing map, ask one bounded
   question, and avoid a score or correctness verdict.
   Lowercase mode choices are supported. In Builder follow-ups, verify that the
   plugin restates the learner's answer as a prediction rather than confirming
   it or claiming runtime behavior.

## Collaborative feature-delivery foundation

The `feature-delivery` skill introduces a live-workspace workflow after an
exact in-conversation `yes`. The learner selects Observe, Guide, Pair, or
Delegate mode. The bundled workbench snapshot maps TypeScript, Python, Java,
and Kotlin source text and metadata, then returns entry points, imports,
symbols, approval requirements, and explicit limitations.

This foundation remains local and read-only until a later action is separately
approved. It does not yet edit a workspace, run project commands, collect a
diff, call a network service, authenticate a user, or persist/sync learning
records. See `docs/LIVE_WORKSPACE_CONTRACT.md` for the product contract.
