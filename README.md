# Evidence Engine

An evidence-backed graph-traversal learning workspace. Learners commit to a plan, predict a traversal state, diagnose a controlled mutation, repair an allowlisted variant, and receive an inspectable evidence map.

## V2 preview: Codex-native onboarding

The standalone app remains the deterministic Evidence Engine demo. The primary
V2 learner experience is now the private `evidence-engine-tutor` Codex plugin.
Its second preview is consent-first and can create a bounded source map for
TypeScript, JavaScript, and Python only after an exact in-conversation `yes`.
It never executes project code, runs project commands, edits files, persists
learner data, adds telemetry, scores, or makes pass/fail decisions. See
`plugins/evidence-engine-tutor/README.md` for the local preview rehearsal.

Learners can choose guided, supported, or independent planning prompts. The support level changes only the amount of explanation and optional editable starter plan; it never changes deterministic evidence or creates a mastery score.

## Local development

```bash
make setup
make dev
```

Open `http://localhost:3000`. The API runs on `http://localhost:8000`.

Run `make check` before merge. See `docs/PROJECT_CHARTER.md` and `AGENTS.md` for product and collaboration constraints.
