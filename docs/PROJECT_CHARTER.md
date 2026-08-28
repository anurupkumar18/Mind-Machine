# Evidence Engine charter

## Thesis

The Evidence Engine verifies whether a learner can reason about and repair code. It is not a generic tutor, a grading system, or a mastery estimator.

## Non-negotiable invariants

Every design decision and every PR must satisfy all of these. See `docs/IMPLEMENTATION_PLAN.md` §2 for the full rationale behind each.

| # | Invariant |
|---|---|
| I1 | Never reads, modifies, executes, or operates on a student's actual coursework, homework, or exam submission. All practice content is curated or procedurally generated in our own safe space. |
| I2 | No model ever decides pass/fail or produces a mastery score. Evidence always comes from a real, executed, deterministic verification. |
| I3 | No LLM call is ever made on a student's behalf by our own infrastructure. The host platform's (ChatGPT's/Codex's) own model does all reasoning, under the student's existing seat. |
| I4 | Canvas access is read-only, student-consented, and scoped to course materials — never gradebook, submissions, or another student's data. Enforced twice: Canvas's own scoped developer-key restriction, and our own code refusing those endpoints regardless. |
| I5 | No server-side learner data store; no login; no PII. Skill-state/misconception data lives client-side only. |
| I6 | The non-evaluative guardrail is structural, not just promised: the diagnosis-coaching tool is never given the verdict as part of its own schema, so it cannot leak one. |
| I7 | Any new tool exposed to the host model must extend the shared non-evaluative guardrail test suite before merge. |

## Evidence loop

`objective/policy -> plan commitment -> external mental model -> prediction -> controlled perturbation -> diagnosis/repair -> deterministic evidence -> targeted retry`

## Architecture and access model

Evidence Engine is a single MCP (Model Context Protocol) server exposing the deterministic evidence engine as tools and resources, connected to a ChatGPT App and a Codex plugin — surfaces every University of Utah student already has through their Enterprise/Edu seat. We never call an LLM ourselves (I3); the host platform's own model reasons under the student's seat, constrained by our tool contracts. There is no public website as a product surface and no per-student API key to fund.

Canvas integration (read-only, I4) lets the practice-generation pipeline target what a student's actual course is covering, without the student describing it manually.

- **Selection:** curated challenge templates, procedural variation of them, and live-synthesized scenarios from a named topic or Canvas-derived topic — never a student's own submitted code (I1).
- **Evidence:** canonical, generated-and-verified tests, always executed, never an LLM grade (I2).
- **Interpretation:** qualitative, event-level evidence only.
- **Coaching:** guides a learner through evidence via Socratic dialogue, structurally unable to supply a repair implementation or determine pass/fail (I6).
- **Knowledge tracing:** a real Bayesian Knowledge Tracing model drives what gets targeted next; its output is never surfaced as a score to a student or instructor.

Full detail: `docs/VISION.md` (product framing), `docs/IMPLEMENTATION_PLAN.md` (phased build plan), `docs/MCP_SERVER.md` (tool contracts, written alongside Phase 2), `docs/CANVAS_INTEGRATION.md` (written alongside Phase 3).
