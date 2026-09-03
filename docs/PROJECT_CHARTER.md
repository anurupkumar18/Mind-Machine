# Evidence Engine charter

## Thesis

Evidence Engine gives learners low-stakes code-repair practice and returns reproducible evidence from tests executed in a controlled verifier Evidence Engine itself runs. The host model may coach and interpret results, but it never creates the authoritative verdict. It is not a generic tutor, a grading system, or a mastery estimator.

> **Direction recorded, contract unchanged (2026-09-02):** the team has agreed on
> a broader north star involving institution-managed class packages,
> NotebookLM-style source-grounded study support, and possible Canvas or browser
> integration. This decision is documented in
> [`TEAM_PRODUCT_DIRECTION.md`](TEAM_PRODUCT_DIRECTION.md), but it does not modify
> this charter. I1–I8 remain authoritative until a separate team-reviewed revision
> reconciles course materials, persistence, institutional provisioning,
> direct-answer behavior, privacy, and access control.
>
> Historical research and existing prototype code are not amendments to this
> contract. Conflicts are cataloged in
> [`research/INITIAL_RESEARCH_AND_INSPIRATION.md`](research/INITIAL_RESEARCH_AND_INSPIRATION.md)
> and require an explicit reviewed decision.

## Non-negotiable invariants

Every design decision and every PR must satisfy all of these. See `docs/IMPLEMENTATION_PLAN.md` §2 for the full rationale behind each.

| # | Invariant |
|---|---|
| I1 | Never reads, modifies, executes, or operates on a student's actual coursework, homework, exam, quiz, or discussion content. All practice content is curated, procedurally generated, or drawn from a vetted reference-implementation catalog — never a student's real assignment. |
| I2 | No model ever decides pass/fail or produces a mastery score. Evidence always comes from tests executed inside Evidence Engine's own controlled, isolated sandbox — never self-reported by the host platform. |
| I3 | We never call an LLM on a student's behalf. The host platform's own model does the conversational reasoning under the student's existing seat, so we carry no per-student LLM inference cost. We do host and pay for the verification sandbox (real compute) — that's execution, not LLM inference. |
| I4 | Canvas access is read-only, student-consented, narrowed to syllabus and module/topic titles by default, and gated behind confirmed institutional data-policy approval — no real Canvas content is transmitted to the host platform, our server, or logs until that approval is documented. Assignment, quiz, discussion, and submission content is excluded from the allowlist entirely. |
| I5 | Evidence Engine has no separate account, login, or server-side learner data store. Skill-selection state lives client-side only. This doesn't eliminate the logins the host platforms themselves require (UofU SSO, Canvas OAuth) — those are pre-existing institutional logins, not something we add. |
| I6 | The non-evaluative guardrail works by never giving the coaching model access to hidden tests or the canonical repair at any point before the student submits a repair attempt — not by omitting a field from one tool's schema. Verified against a fixed behavioral eval set testing for answer-leakage and over-helping. |
| I7 | Any new tool exposed to the host model must extend the shared guardrail test suite before merge, including the answer-leakage/over-helping behavioral eval set. |
| I8 | Every evidence record is produced by Evidence Engine's own sandboxed execution and cryptographically signed — includes challenge ID + version, base-code hash, submitted-repair hash, test-suite/oracle version, seed, runtime digest, exit status, and per-property results. The host model can narrate this record; it cannot alter or fabricate it. |

## Evidence loop

`objective/policy -> plan commitment -> external mental model -> prediction -> controlled perturbation -> diagnosis/repair -> deterministic evidence -> targeted retry`

## Architecture and access model

Evidence Engine is an MCP (Model Context Protocol) server exposing four model-facing workflow tools (`start_challenge`, `submit_prediction`, `submit_diagnosis`, `submit_repair`) behind an opaque signed challenge token, connected to a ChatGPT App and a Codex plugin. Internal pipeline steps (property selection, mutation synthesis, kill-ratio filtering) are never separately callable by the host model. We never call an LLM ourselves (I3); the host platform's own model reasons under the student's seat, constrained by the tool contracts, and narrates evidence records it cannot alter (I8). There is no public website as a product surface and no per-student API key to fund.

Canvas integration (read-only, narrowed, gated — I4) lets the practice-generation pipeline target what a student's actual course is covering, once institutional approval confirms the data flow is allowed.

- **Selection:** a declarative property-DSL catalog (predefined, reviewed property constructors — never free-form model-authored executable code) applied to a curated reference-implementation library, procedural variation, or a named/Canvas-derived topic — never a student's own submitted code (I1).
- **Evidence:** tests executed inside Evidence Engine's own sandbox, signed, always real, never an LLM's self-report (I2, I8).
- **Interpretation:** qualitative, event-level evidence only.
- **Coaching:** guides a learner through evidence via Socratic dialogue, never given the hidden tests or canonical repair before a repair attempt (I6).
- **Knowledge tracing:** deferred. A transparent, documented practice-selection heuristic (recent success by skill tag) targets content for now; it is explicitly not a mastery estimate. Real Bayesian Knowledge Tracing is out of scope until a pilot produces data to calibrate it.

Full detail: `docs/VISION.md` (product framing), `docs/IMPLEMENTATION_PLAN.md` (phased build plan, including the external-review-driven revision that introduced I8 and narrowed I1/I4/I6), `docs/MCP_SERVER.md` (tool contracts, written alongside the MCP-workflow phase), `docs/CANVAS_INTEGRATION.md` (written alongside the Canvas phase).
