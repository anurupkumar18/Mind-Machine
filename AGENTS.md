# Evidence Engine agent guide

## Read in this order

1. `memory/INDEX.md`
2. `docs/VISION.md` and `docs/IMPLEMENTATION_PLAN.md` (product framing, invariants, phased task IDs)
3. Relevant files in `memory/semantic/`
4. The latest relevant record in `memory/episodic/`
5. `docs/PROJECT_CHARTER.md` and the affected contract

Do not load every memory file. The normal context budget is the index, at most two semantic records, and one episodic handoff.

## Product invariants (I1-I7, full rationale in `docs/IMPLEMENTATION_PLAN.md` §2 / `docs/PROJECT_CHARTER.md`)

- **I1** Never read, modify, execute, or operate on a student's actual coursework, homework, or exam submission. All practice content is curated or procedurally generated in our own safe space. Anything a student pastes is a topic hint at most, never literal content to mutate and hand back.
- **I2** Never make a mastery percentage or let a model determine pass/fail. Evidence always comes from a real, executed, deterministic verification.
- **I3** Never call an LLM on a student's behalf from our own infrastructure. The host platform's (ChatGPT's/Codex's) own model does all reasoning, under the student's existing seat.
- **I4** Canvas access is read-only, student-consented, and scoped to course materials — never gradebook, submissions, or another student's data. Enforce this in code even if a broader token is ever presented, not just via the requested OAuth scope.
- **I5** No server-side learner data store, no login, no PII, no student records, private repositories, credentials, names, IDs, or emails in memory files. Skill-state lives client-side only.
- **I6** The non-evaluative guardrail is structural: any tool that coaches/diagnoses must never receive the verdict as part of its own input/output schema.
- **I7** Any new tool exposed to the host model must extend the shared non-evaluative guardrail test suite before merge.
- Keep challenge selection, deterministic evidence generation, and learning interpretation separate.
- Execute only canonical, allowlisted fixture variants, or code generated and verified by our own pipeline — never arbitrary user-provided code.

## Working agreement

- Scope each task to one vertical outcome, reference a specific phase + task ID from `docs/IMPLEMENTATION_PLAN.md` §6, and state its acceptance criteria before editing. See `docs/IMPLEMENTATION_PLAN.md` §5 for the full agentic-engineering discipline (spec-first, verify-before-trusting-APIs, test-first, small diffs, human review gate) — it applies to every change, agent-authored or not.
- Keep files small, domain-focused, and named after the behavior they own.
- Update a semantic or long-term memory record only through a reviewed PR. Add a compact episodic handoff when a task changes the next contributor's context.
- Run the narrowest relevant check before committing; run `make check` before merge.
- Report changed files, checks, evidence, risks, and next action. Never record private prompts or raw chain-of-thought in memory.
- Use `.github/pull_request_template.md`'s checklist on every PR.

