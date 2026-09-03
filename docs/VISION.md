# Evidence Engine — Vision

> **Document status:** working product narrative spanning current capabilities and
> future direction. It is not a complete implementation description. Where it
> conflicts with the current charter, verified source behavior, or a later dated
> decision, surface the discrepancy rather than silently reconciling it. Historical
> ideas live in [`research/INITIAL_RESEARCH_AND_INSPIRATION.md`](research/INITIAL_RESEARCH_AND_INSPIRATION.md).

## One line

Evidence Engine proves a student can actually reason about and repair code — not by asking an AI to grade them, but by making them predict, break, and fix real, running code and showing them evidence from tests executed in Evidence Engine's own sandbox — delivered inside the ChatGPT and Codex access University of Utah students can already get through their institutional account, and grounded in what their own Canvas course is teaching once institutional approval allows it.

## September 2026 north star (direction agreed; feasibility open)

The team has agreed to explore a broader destination around this verified-practice
core: an institution-supported learning layer that gives each enrolled student a
low-setup, course-aware AI environment. A professor- and IT-approved class package
could make course-specific skills, guardrails, hooks, tools, plugins, and MCP
servers available through ChatGPT, Codex, agents, or custom GPTs. Permitted Canvas
context or a companion browser extension could connect the course, while
NotebookLM-style source-grounded Q&A, citations, summaries, and study aids help a
student move from understanding material to practicing it with real evidence.

This is a product direction, not a claim about current functionality, permissions,
or final architecture. Institutional provisioning, Canvas access, browser-extension
policy, privacy, procurement, and the open-source component strategy remain open
discovery questions. The canonical decision record is
[`TEAM_PRODUCT_DIRECTION.md`](TEAM_PRODUCT_DIRECTION.md).

## The problem

Two things are true at once for a CS/algorithms student: they can watch a lecture, read a chapter, or ask a chatbot to "explain BFS" and *feel* like they understand it — and still get it wrong under exam pressure or on a new problem. Fluent explanations create an illusion of understanding that doesn't transfer, because recognizing an explanation and reconstructing the reasoning yourself are different cognitive acts. Generic AI tutors make this worse, not better — a chatbot that answers on demand removes exactly the struggle that builds durable understanding, and its "you're right!" is an opinion, not evidence.

## Who this is for

A CS1/CS2-and-beyond student who wants to close the gap between "I watched it" and "I can do it" — specifically for algorithmic/code reasoning, where correctness is objectively checkable. Not a replacement for lectures or textbooks; a place to find out, honestly, whether the lecture actually landed.

## What this is not

- Not an unconstrained answer bot. The current code-practice loop stays
  non-evaluative before repair; the newer study-workspace direction may answer
  questions only from student-selected, permitted sources with citations.
- Not a grading system. It never produces a score, a mastery percentage, or a pass/fail judgment from a model's opinion.
- Not a hardcoded demo. The engine is fixture-driven and content-agnostic; every scenario runs through the same pipeline, and it generates fresh scenarios rather than repeating a fixed set.
- Not something you install, configure, pay for, or need a technical background for — it lives inside ChatGPT and Codex.
- **Not something that ever touches your real homework, exam, quiz, discussion post, or graded submission.** Every practice scenario is curated or procedurally generated in Evidence Engine's own safe space, drawn from a vetted reference-implementation catalog — nothing you paste is ever mutated and handed back to you; at most it tells the system what topic to generate practice on.
- **Not a system that treats a host-reported test result as proof of execution.** Evidence comes from tests Evidence Engine runs itself, in its own sandbox — never a claim self-reported by the model doing the coaching.

## The core loop

`objective → plan commitment → prediction → controlled bug → diagnosis → repair → deterministic evidence → targeted retry`

The student commits to a plan, predicts what a real algorithm will do next, gets a realistic bug injected into working code, diagnoses it through Socratic dialogue (the AI asks, it never tells), repairs it, and sees the result of a test Evidence Engine actually ran — not a model's opinion of whether they're right.

## How it actually runs

Evidence Engine is an MCP (Model Context Protocol) server connected to two surfaces a University of Utah student can access through their institutional ChatGPT/Codex account: a ChatGPT App and a Codex plugin. The host platform's own model handles the conversational reasoning — we never call an LLM on a student's behalf, so we carry no per-student LLM inference cost. What we do run and pay for is a small, isolated **verification sandbox**: when a student submits a repair, Evidence Engine executes the hidden tests itself, in a controlled container we own, and returns a signed evidence record. The host model can narrate that record to the student; it cannot alter it, and it never sees the hidden tests or the canonical repair before the student submits an attempt. When connected, and once institutional approval for the data flow is confirmed, practice is grounded in the student's own Canvas course (syllabus and module/topic titles — read-only, never gradebook, submissions, assignments, quizzes, or discussions).

## Why this wins

1. **Its evidence is real, not self-reported.** A signed record from Evidence Engine's own sandbox execution — challenge version, code hashes, test-suite version, seed, exit status, per-property results — not a shape-checked claim from whichever platform happens to be hosting the conversation.
2. **The pedagogy and the engagement design are both grounded in cited research, not decoration.** Retrieval practice (testing effect), desirable difficulty/productive failure, and guardrailed Socratic dialogue drive learning; a flow-theory-informed practice-selection heuristic and growth-mindset-consistent non-evaluative framing drive wanting to come back. A 2025 Harvard RCT found AI tutoring roughly doubled the learning rate of active-learning classrooms under its own studied conditions (194 students, two structured intro-physics lessons) — that result motivates this design; it doesn't validate this specific product, and we don't claim otherwise.
3. **It's accessible without a separate account, API key, or payment.** It uses whatever ChatGPT/Codex access a student's University of Utah account already has — no new signup for Evidence Engine itself, though the underlying institutional access (Enterprise/Edu enrollment, SSO) is a real prerequisite we don't control or eliminate.
4. **It's real, substantial engineering, not a wrapper.** A declarative property catalog, AST-level mutation synthesis with kill-ratio filtering, a genuinely isolated verification sandbox, and a non-evaluative guardrail enforced by never exposing hidden tests to the coaching model — not a prompt wrapped around a chat window.
5. **Canvas grounding is opt-in, narrow, and gated.** When approved, it reads syllabus and topic titles only — never assignments, quizzes, discussions, or submissions — and the read/never-read boundary is enforced by Canvas's own scoped tokens, our own code, and a confirmed institutional data-policy decision before any real content flows anywhere.

## Scope tiers

- **Core:** the property-DSL-constrained mutation → server-side verification loop, generating varied practice scenarios from a curated reference-implementation catalog, a named topic, or (once approved) Canvas-derived context — never from a student's own submitted work — plus a transparent, honestly-framed practice-selection heuristic (see "Known limits").
- **Stretch:** the ChatGPT App's custom trace/visual-diff UI widgets; skill-state cross-device transfer (QR-based); the instructor dashboard.
- **Deferred to post-pilot:** real Bayesian Knowledge Tracing (see below); an adversarial self-verifying content pipeline for expanding the catalog without a human bottleneck.

## Known limits (stated up front, not discovered by a judge)

- Works best on pure, deterministic code with clear input/output behavior.
- **No real knowledge tracing yet.** What targets practice content is a transparent heuristic (recent pass/fail rate per skill tag) — explicitly not a calibrated mastery estimate. Real Bayesian Knowledge Tracing needs a stable skill taxonomy, a challenge-to-skill mapping, calibrated parameters, and pilot data to validate against; none of that exists yet, so we're not claiming it.
- Verification now runs in Evidence Engine's own sandbox, which is real infrastructure we built and are responsible for securing (isolation, resource limits) — this is a stronger evidence claim than relying on the host platform, but it's not a claim that the sandbox is unbreakable.
- By design, the tool cannot help with an actual graded assignment directly — that's a deliberate boundary, not a missing feature.
- "Learning style" personalization means modality/scaffolding choice (text, voice, visual diff, support level), not the VARK-style model, which the cognitive-science literature doesn't support as a basis for tailoring instruction.
- Canvas integration only helps for courses that actually use Canvas's syllabus/module features with real content in them, and only reaches syllabus/topic-title-level detail by default.
- "Never repeats" is not a guarantee — content is varied and repetition is minimized by tracking consumed challenge/variant IDs locally, not a mathematical impossibility of repeats.
- A passing test suite is evidence for the properties it checks, not a proof of general correctness — any finite test suite has coverage boundaries.

## Explicitly out of scope (for now)

- Non-code subjects (math, history, etc.) — the verifiable-evidence mechanism is specific to checkable code/algorithms.
- Accounts, login, or any server-side learner data store of our own.
- A standalone public website as a product surface — the product lives inside ChatGPT/Codex; judging happens via a live screen-share demo.
- Writing to Canvas, or reading anything beyond syllabus/topic titles unless institutional approval explicitly extends that.
- Real Bayesian Knowledge Tracing (see "Scope tiers") until a pilot produces data to calibrate against.
- Letting a model author executable verification code directly — properties are expressed through a reviewed, declarative catalog, never free-form model-generated Python, since Evidence Engine now executes that code itself.

## Naming note

The product is "Evidence Engine" everywhere a user sees it. The repository is historically named `Mind-Machine`; that's a repo-level artifact, not a product name, and isn't user-facing.
