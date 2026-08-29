# Evidence Engine agent guide

## Read in this order

1. `memory/INDEX.md`
2. `docs/VISION.md` and `docs/IMPLEMENTATION_PLAN.md` (product framing, invariants, phased task IDs)
3. Relevant files in `memory/semantic/`
4. The latest relevant record in `memory/episodic/`
5. `docs/PROJECT_CHARTER.md` and the affected contract

Do not load every memory file. The normal context budget is the index, at most two semantic records, and one episodic handoff.

## Product invariants (I1-I8, full rationale in `docs/IMPLEMENTATION_PLAN.md` §1 / `docs/PROJECT_CHARTER.md`)

- **I1** Never read, modify, execute, or operate on a student's actual coursework, homework, exam, quiz, or discussion content. All practice content is curated, procedurally generated, or drawn from a vetted reference-implementation catalog. Anything a student pastes is a topic hint at most, never literal content to mutate and hand back.
- **I2** Never make a mastery percentage or let a model determine pass/fail. Evidence always comes from tests executed inside Evidence Engine's own controlled, isolated sandbox — never self-reported by the host platform (I8 is the mechanism).
- **I3** Never call an LLM on a student's behalf from our own infrastructure. The host platform's (ChatGPT's/Codex's) own model does the conversational reasoning, under the student's existing seat — no per-student LLM cost. We do host and pay for the verification sandbox (I8); that's execution, not LLM inference.
- **I4** Canvas access is read-only, student-consented, narrowed to syllabus and module/topic titles by default, and gated behind confirmed institutional data-policy approval — no real Canvas content is transmitted anywhere until that's documented. Assignment/quiz/discussion/submission content is excluded from the allowlist entirely, and enforced in code even if a broader token is ever presented.
- **I5** No server-side learner data store, no separate Evidence Engine account/login, no PII, no student records, private repositories, credentials, names, IDs, or emails in memory files. Skill-state lives client-side only. (The host platforms' own logins — UofU SSO, Canvas OAuth — are pre-existing and outside this invariant.)
- **I6** The non-evaluative guardrail works by never giving the coaching model access to hidden tests or the canonical repair before a repair attempt is submitted — not by omitting a schema field. Verified against a behavioral answer-leakage/over-helping eval set.
- **I7** Any new tool exposed to the host model must extend the shared guardrail test suite before merge, including the behavioral eval set.
- **I8** Every evidence record is produced by Evidence Engine's own sandboxed execution and cryptographically signed (challenge ID+version, code hashes, test-suite version, seed, runtime digest, exit status, per-property results). The host model can narrate it; it cannot alter or fabricate it.
- Keep challenge selection, sandboxed evidence generation, and learning interpretation separate.
- Properties are expressed through a reviewed, declarative DSL — never free-form model-authored executable code, since Evidence Engine now executes that code itself.

## Working agreement

- Scope each task to one vertical outcome, reference a specific phase + task ID from `docs/IMPLEMENTATION_PLAN.md` §6, and state its acceptance criteria before editing. See `docs/IMPLEMENTATION_PLAN.md` §5 for the full agentic-engineering discipline (spec-first, verify-before-trusting-APIs, test-first, small diffs, human review gate) — it applies to every change, agent-authored or not.
- Keep files small, domain-focused, and named after the behavior they own.
- Update a semantic or long-term memory record only through a reviewed PR. Add a compact episodic handoff when a task changes the next contributor's context.
- Run the narrowest relevant check before committing; run `make check` before merge.
- Report changed files, checks, evidence, risks, and next action. Never record private prompts or raw chain-of-thought in memory.
- Use `.github/pull_request_template.md`'s checklist on every PR.

