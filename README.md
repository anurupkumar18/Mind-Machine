# Evidence Engine

An evidence-backed graph-traversal learning workspace. Learners commit to a plan, predict a traversal state, diagnose a controlled mutation, repair an allowlisted variant, and receive an inspectable evidence map.

Learners can choose guided, supported, or independent planning prompts. The support level changes only the amount of explanation and optional editable starter plan; it never changes deterministic evidence or creates a mastery score.

## Local development

```bash
make setup
make dev
```

Open `http://localhost:3000`. The API runs on `http://localhost:8000`.

Run `make check` before merge. See `docs/PROJECT_CHARTER.md` and `AGENTS.md` for product and collaboration constraints.
