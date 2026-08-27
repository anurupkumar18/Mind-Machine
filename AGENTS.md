# Evidence Engine agent guide

## Read in this order

1. `memory/INDEX.md`
2. Relevant files in `memory/semantic/`
3. The latest relevant record in `memory/episodic/`
4. `docs/PROJECT_CHARTER.md` and the affected contract

Do not load every memory file. The normal context budget is the index, at most two semantic records, and one episodic handoff.

## Product invariants

- Accept public or synthetic material only. Never add student records, private repositories, credentials, names, IDs, or emails.
- Keep challenge selection, deterministic evidence generation, and learning interpretation separate.
- Never make a mastery percentage or let a model determine pass/fail.
- Execute only canonical, allowlisted fixture variants. Never execute user-provided code.
- Treat all persistence as opt-in and absent by default; the MVP keeps learner state in the browser only.

## Working agreement

- Scope each task to one vertical outcome and state its acceptance criteria before editing.
- Keep files small, domain-focused, and named after the behavior they own.
- Update a semantic or long-term memory record only through a reviewed PR. Add a compact episodic handoff when a task changes the next contributor's context.
- Run the narrowest relevant check before committing; run `make check` before merge.
- Report changed files, checks, evidence, risks, and next action. Never record private prompts or raw chain-of-thought in memory.

