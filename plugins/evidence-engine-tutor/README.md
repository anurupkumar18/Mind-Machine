# Evidence Engine Tutor

Private Codex-plugin preview for consent-first codebase onboarding.

The first slice intentionally has no workspace-reading tool, command runner,
file editor, persistence, telemetry, score, or pass/fail decision. It teaches
the learner what will happen before later slices introduce read-only source
mapping.

## Manual rehearsal

1. Install `evidence-engine-tutor` from the `personal` marketplace.
2. Start a new Codex conversation in a workspace.
3. Invoke `evidence-engine-tutor` and ask to start a read-only codebase
   onboarding session.
4. Confirm that it asks for explicit consent and clearly states that no files
   have been inspected, no commands have run, and nothing has been changed.

The next slice may add source inspection only after the learner explicitly
consents in that conversation.
