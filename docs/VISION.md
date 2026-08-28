# Evidence Engine — Vision

## One line

Evidence Engine proves a student can actually reason about and repair code — not by asking an AI to grade them, but by making them predict, break, and fix real, running code and showing them a real passing test as proof — delivered inside the ChatGPT and Codex access every University of Utah student already has, at zero incremental cost per student, and grounded in what their own Canvas course is actually teaching.

## The problem

Two things are true at once for a CS/algorithms student: they can watch a lecture, read a chapter, or ask a chatbot to "explain BFS" and *feel* like they understand it — and still get it wrong under exam pressure or on a new problem. Fluent explanations create an illusion of understanding that doesn't transfer, because recognizing an explanation and reconstructing the reasoning yourself are different cognitive acts. Generic AI tutors make this worse, not better — a chatbot that answers on demand removes exactly the struggle that builds durable understanding, and its "you're right!" is an opinion, not evidence.

## Who this is for

A CS1/CS2-and-beyond student who wants to close the gap between "I watched it" and "I can do it" — specifically for algorithmic/code reasoning, where correctness is objectively checkable. Not a replacement for lectures or textbooks; a place to find out, honestly, whether the lecture actually landed.

## What this is not

- Not a chatbot. There is no open-ended "ask me anything" box that answers questions directly.
- Not a grading system. It never produces a score, a mastery percentage, or a pass/fail judgment from a model's opinion.
- Not a hardcoded demo. The engine is fixture-driven and content-agnostic; every scenario runs through the same deterministic pipeline, and it generates fresh scenarios rather than repeating a fixed set.
- Not something you install, configure, pay for, or need a technical background for — it lives inside ChatGPT and Codex, which you already have.
- **Not something that ever touches your real homework, exam, or graded submission.** Every practice scenario is curated or procedurally generated in Evidence Engine's own safe space — nothing you paste is ever mutated and handed back to you; at most it tells the system what topic to generate practice on.

## The core loop

`objective → plan commitment → prediction → controlled bug → diagnosis → repair → deterministic evidence → targeted retry`

The student commits to a plan, predicts what a real algorithm will do next, gets a realistic bug injected into working code, diagnoses it through Socratic dialogue (the AI asks, it never tells), repairs it, and sees the result of an actual test run — not a model's opinion of whether they're right.

## How it actually runs

Evidence Engine is a single MCP (Model Context Protocol) server exposing a deterministic evidence engine as tools and resources, connected to two surfaces students already have through their University of Utah Enterprise/Edu seat: a ChatGPT App and a Codex plugin. **We never call an LLM on a student's behalf** — the Socratic dialogue is ChatGPT's or Codex's own model, reasoning under the student's own seat, constrained by our tool contracts; our code only ever returns real, deterministic results (a generated scenario, a test outcome, an evidence record). When connected, practice is grounded in the student's own Canvas course (syllabus, modules, materials — read-only, never gradebook or submissions).

## Why this wins

1. **It's verifiable, not vibes-based, and it never runs out of content.** Evidence comes from a real, generated, executed test on freshly synthesized scenarios — not a fixed puzzle bank, and never anything that could cost a student a grade.
2. **The pedagogy and the engagement design are both real research, not decoration.** Retrieval practice (testing effect, meta-analytic g≈0.74), desirable difficulty / productive failure, and guardrailed Socratic dialogue drive *learning*; flow theory's challenge-skill balance (via real knowledge tracing) and growth-mindset-consistent non-evaluative framing drive *wanting to come back*. A 2025 Harvard RCT found AI tutoring produced roughly double the learning rate of active-learning classrooms — with the finding's own caveat that success comes from pedagogical guardrails, not the raw model. This product is built around that caveat, not despite it.
3. **It's genuinely accessible at zero incremental cost.** No new account, no API key, no download beyond what a University of Utah student already has through their Enterprise/Edu seat — and no per-student LLM bill for us to fund, because we never call one.
4. **It's real, hard AI engineering, not a wrapper — pointed at something that can only help, never hurt, a student's standing.** Property-based invariant validation, AST-level mutation synthesis with kill-ratio filtering, an information-theoretic (not just promised) non-evaluative guardrail, and real Bayesian knowledge tracing — applied entirely within a zero-stakes practice space, by explicit design.
5. **It's grounded in a real, already-adopted institutional data source, read-only.** Practice is targeted at what a student's own Canvas course is actually teaching, without requiring the student to describe it themselves, and without ever touching a grade, a submission, or anyone else's data — the read/never-read boundary is enforced by Canvas's own scoped-token system, not just a promise in our code.

## Scope tiers

- **Core (the demo centerpiece):** the invariant-derivation → mutation-synthesis → repair-verification pipeline generating fresh, verified practice scenarios on demand — sourced from the student's own Canvas syllabus/modules (read-only) when connected, a named topic, or procedural variation of the curated library — never from a student's own submitted work — plus the real (simple) BKT skill model keeping difficulty in the engagement sweet spot.
- **Stretch:** the ChatGPT App's custom trace/visual-diff UI widgets; skill-state cross-device transfer (QR-based).
- **Moonshot:** an adversarial, self-verifying content pipeline expanding the safe seed/reference library without a human bottleneck; an aggregated, fully anonymized instructor-facing dashboard (never able to identify an individual student, so it can never be used against one).

## Non-negotiable invariants

See `docs/PROJECT_CHARTER.md` and `docs/IMPLEMENTATION_PLAN.md` §2 for the enforced, numbered versions (I1-I7). Summary:

- No model ever decides pass/fail or produces a mastery score — evidence always comes from a real, canonical test run.
- No login, no PII, no server-side persistence of learner responses.
- Our infrastructure never calls an LLM on a student's behalf — all reasoning happens inside the platform the student already has access to.
- Canvas access is read-only, student-consented, and scoped to course materials — never gradebook, submissions, or another student's data.
- The non-evaluative guardrail is structural (built into tool schemas), not just a prompt instruction.
- Any new feature that adds a tool the host model can call must extend the shared non-evaluative guardrail test suite before it ships.

## Known limits (stated up front, not discovered by a judge)

- Works best on pure, deterministic code with clear input/output behavior; code with side effects or ambiguous correctness gets an honest "not a good fit yet" rather than a bad result.
- Knowledge-tracing confidence is genuinely low on a student's first few attempts at a skill — shown honestly as growing confidence over a session, not claimed as immediate precision.
- Verification execution is trusted to the host platform's sandbox rather than infrastructure we control, mitigated but not eliminated by requiring a structured, validated verdict format.
- By design, the tool cannot help with an actual graded assignment directly — that's a deliberate boundary, not a missing feature.
- "Learning style" personalization deliberately means modality/scaffolding choice (text, voice, visual diff, support level), not the VARK-style model, which the cognitive-science literature doesn't support as a basis for tailoring instruction — stated honestly rather than oversold.
- Canvas integration only helps for courses that actually use Canvas's syllabus/module features with real content in them.

## Explicitly out of scope (for now)

- Non-code subjects (math, history, etc.) — the verifiable-evidence mechanism is specific to checkable code/algorithms; broadening subject matter would force LLM-graded evaluation and give up the core differentiator.
- Accounts, login, or any server-side learner data store.
- A standalone public website as a product surface — the product lives inside ChatGPT/Codex; judging happens via a live screen-share demo, not a public link.
- Writing to Canvas in any way, or reading anything beyond course materials (gradebook, submissions, other students' data).

## Naming note

The product is "Evidence Engine" everywhere a user sees it. The repository is historically named `Mind-Machine`; that's a repo-level artifact, not a product name, and isn't user-facing.
