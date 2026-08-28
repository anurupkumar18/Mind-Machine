# Evidence Engine — Implementation Plan & Team Review Package

**Repo:** Mind-Machine (product name: "Evidence Engine") · **Purpose of this document:** the single reference for team review, sanity-check, and sign-off, and the source of task IDs every PR should reference (see §5.1). Sections are ordered so a first-time reader can follow the reasoning, not just the conclusions.

A polished, shareable export of this document (for sign-off outside GitHub) is generated from this same source — ask in the team channel if you need the link resent.

---

## 0. How to use this document

1. Read §1 (Executive Summary) and §2 (Non-Negotiable Invariants) first — everything else is downstream of those two.
2. Each phase in §6 has an explicit **Definition of Done** — treat these as the actual acceptance gates, not aspirational.
3. §8 (Open Questions for the Team) is the part that most needs your input, not just your approval — please answer it, don't just skim it.
4. §9 (Sign-off) is where the team records agreement per role before Phase 0 starts.

---

## 1. Executive Summary

**Problem**: students can feel like they understand a lecture and still fail to apply it — fluent recognition isn't the same as reconstructable understanding. Generic AI chatbots make this worse by answering on demand, removing the productive struggle that builds durable skill.

**Solution**: Evidence Engine is an MCP-based tool, delivered as a ChatGPT App and a Codex plugin (surfaces every University of Utah student already has via their Enterprise/Edu seat), that generates fresh, verified, never-repeating algorithmic bugs for a student to diagnose and repair — evidence of success is always a real executed test, never a model's opinion. Content is grounded in the student's own Canvas course (read-only) when connected. No student ever pays for or configures an LLM; no student's real coursework, submissions, or grades are ever touched; no score is ever shown to a student or instructor.

**Why now, why us**: the pedagogy (retrieval practice, desirable difficulty, non-evaluative Socratic scaffolding) is well-established research, largely unimplemented with real rigor in existing tools; the access model (piggyback on already-provisioned ChatGPT/Codex seats via MCP) removes the cost barrier that normally kills a hackathon AI-tutor idea; and the technical core (property-based invariant validation + mutation synthesis + real knowledge tracing) is genuinely hard engineering, not a prompt wrapper.

**What this is not**: not a chatbot, not a grading system, not a mastery estimator, not something that touches a graded assignment, not something requiring install/signup/payment.

---

## 2. Non-Negotiable Invariants (read this before anything else)

These are the constraints every subsequent design decision must satisfy. Any PR that violates one of these should be rejected regardless of how good the surrounding code is. Also recorded in `docs/PROJECT_CHARTER.md`.

| # | Invariant | Why |
|---|---|---|
| I1 | **Never reads, modifies, executes, or operates on a student's actual coursework, homework, or exam submission.** All practice content is curated or procedurally generated in our own safe space. | Academic-integrity risk to the student, and a tool that can touch something gradeable is a tool students avoid, not one they return to. |
| I2 | **No model ever decides pass/fail or produces a mastery score.** Evidence always comes from a real, executed, deterministic verification. | Core product differentiator; also the Charter's original founding constraint. |
| I3 | **No LLM call is ever made on a student's behalf by our own infrastructure.** The host platform's (ChatGPT's/Codex's) own model does all reasoning, under the student's existing seat. | This is what makes the product free to run per-student — violating it reintroduces the funding problem that caused the access-model pivot (see §4). |
| I4 | **Canvas access is read-only, student-consented, and scoped to course materials — never gradebook, submissions, or another student's data.** Enforced twice: Canvas's own scoped developer-key restriction, and our own code refusing those endpoints regardless. | Same root concern as I1, applied to the new data source. |
| I5 | **No server-side learner data store; no login; no PII.** Skill-state/misconception data lives client-side only (browser localStorage + QR transfer, or a local Codex workspace file). | Privacy invariant; also load-bearing for the Privacy and Ethics judging criterion. |
| I6 | **The non-evaluative guardrail is structural, not just promised.** The diagnosis-coaching tool is never given the verdict as part of its own schema, so it cannot leak one. | Distinguishes this from prompt-engineered "guardrails" that can be talked around. |
| I7 | **Any new tool exposed to the host model must extend the shared guardrail test suite before merge.** | Turns "don't forget the guardrail" into a checked requirement, not a hope — see §7. |

---

## 3. Vision, Positioning, and Judging-Criteria Alignment

Full drafted content lives in `docs/VISION.md` — summarized here for reviewers who want the headline without opening a second file.

**Core loop**: `objective → plan commitment → prediction → controlled bug → diagnosis → repair → deterministic evidence → targeted retry`

**Why it wins** (five points, each defensible individually):
1. Verifiable, not vibes-based, and never runs out of content (generated + validated, not a fixed puzzle bank).
2. Pedagogy *and* engagement design are both grounded in cited research, not decoration (retrieval practice, desirable difficulty, flow theory, growth mindset — see `docs/VISION.md` for full citations).
3. Genuinely accessible at zero incremental cost (existing Enterprise/Edu seat, no key, no signup).
4. Real, hard AI engineering (property-based validation, AST mutation synthesis, information-theoretic guardrail, real Bayesian knowledge tracing) pointed at something that can only help, never hurt, a student's standing.
5. Grounded in a real, already-adopted institutional data source (Canvas), read-only, enforced structurally.

**Judging-criteria mapping** (Track 2 "Learn," full rubric):

| Criterion | How this plan answers it |
|---|---|
| Feasibility | Zero per-student LLM cost; one lightweight MCP server is the only new infra; Canvas/ChatGPT/Codex already deployed university-wide. |
| Presentation | Live demo synthesizes a fresh, verified scenario from a real Canvas topic in front of the audience — not a scripted walkthrough. |
| Design | Combines property-based validation, AST mutation synthesis, and Bayesian knowledge tracing with a real institutional data source. |
| Innovation | Verifiable-by-construction tutoring + content generation that never touches gradeable work — the combination is the novel part. |
| Impact | Practice targets what a student's own course is teaching right now, without instructor authoring effort. |
| Scalability & Sustainability | Cost scales with our server, not per-student model usage; Canvas has broad higher-ed adoption; natural partners are UofU's teaching-and-learning center, CS department, or Instructure itself. |
| Community Engagement | Plan includes piloting with one real UofU CS course and instructor (§8, open question). |
| Interdisciplinary Collaboration | Design already draws on learning-science research alongside engineering; plan proposes involving an instructor/TA in content review (§8). |
| Privacy and Ethics | I1, I4, I5 above are structural, not aspirational — enforced in code and tested (§7). |
| Data Quality and Availability | Canvas is structured/reliable; the system generates and empirically verifies content rather than needing historical training data. |

---

## 4. Architecture Overview

```
                        ┌──────────────────────────┐
   Student (existing    │   ChatGPT App  /  Codex   │   <- host model does ALL
   UofU Enterprise/Edu   │   plugin (two clients,    │      reasoning/dialogue,
   seat — no new cost)   │   one shared contract)    │      under the student's
                        └────────────┬─────────────┘      own seat (I3)
                                     │  MCP (tool calls + resources)
                                     ▼
                        ┌──────────────────────────┐
                        │   Evidence Engine MCP     │   <- deterministic only;
                        │   server (ours, hosted)   │      never calls an LLM
                        └───┬─────────────┬─────────┘      itself (I3)
                            │             │
              ┌─────────────┘             └───────────────┐
              ▼                                            ▼
   ┌─────────────────────┐                     ┌─────────────────────────┐
   │ Practice-content     │                     │ Canvas read-only client │
   │ pipeline: invariant  │                     │ (scoped OAuth2 token,   │
   │ hypothesis → verify  │                     │ syllabus/modules/pages  │
   │ → mutate → kill-ratio│                     │ only — I4)              │
   │ filter → verify      │                     └─────────────────────────┘
   │ repair (I2, I6)      │
   └─────────────────────┘
              │
              ▼
   ┌─────────────────────┐
   │ BKT skill model      │   <- client-held state (I5); never
   │ (client-side state)  │      surfaced as a score
   └─────────────────────┘
```

Code execution for the pipeline (property-based tests, mutation trials, repair verification) runs inside the **host platform's own code-execution sandbox** (ChatGPT's Code Interpreter / Codex's native execution), not infrastructure we build — our server generates the deterministic test/mutation code and validates the *shape* of what comes back (the remote-execution trust-boundary mitigation, §6 Phase 1).

---

## 5. Agentic Software Engineering Practices — making AI-assisted build work good, not slop

This project will be built substantially with AI coding agents (Claude Code, Codex, etc.). That's an asset, not a risk, **if** it follows the same discipline a careful human engineering team would use. These rules apply to every phase in §6, agent-authored or human-authored, no exceptions.

### 5.1 Spec-first, never vibes-first
- Every agent task must reference a specific phase + task ID from §6 (e.g. "Phase 2, Task 2.3"). A prompt like "build the MCP server" is not an acceptable task description — it produces scope drift and unreviewable diffs.
- Before writing code, the agent (or engineer) states the bounded outcome and acceptance criteria for the change, matching the phase's Definition of Done — this mirrors the existing `.agents/skills/evidence-engine-delivery/SKILL.md` requirement and is now mandatory project-wide, not just for that skill.

### 5.2 Verify before trusting library/API usage
- No SDK/API call (Canvas API, Apps SDK, MCP SDK, OpenAI SDK, Hypothesis, `ast`) is written from memory/training-data recall alone for anything non-trivial. Check current official docs first; cite the doc source in the PR description. This project has already been burned once in this planning process by unverified assumptions (the original access-model plan) — the same discipline applies to code.
- Prefer official SDKs over hand-rolled HTTP where one exists.

### 5.3 Test-first, verification-required
- No merged change without a test that proves the specific acceptance criteria in its phase's Definition of Done.
- Any tool that becomes reachable by the host model (i.e., anything an LLM could call) must extend the guardrail test suite (I7) — this is a hard merge gate, not a suggestion.
- The mutation/invariant pipeline (Phase 1) additionally needs a battery of known-good/known-bad cases — this is the test suite that actually validates the hard part, not just "the code runs."

### 5.4 Small, reviewable, traceable diffs
- One phase-task per PR wherever feasible. No drive-by refactors bundled into a feature PR.
- Every PR description states: which task it implements, what was tested, what docs were updated, and whether it touches any invariant in §2 (if yes, name which and how it's preserved).
- Every merged change gets a corresponding episodic memory record (`memory/episodic/NNNN-*.md`) — this project already had a stale-tracking problem once (the original audit found a memory pointer 11 records out of date); §6 Phase 0 includes automating this check so it can't recur silently.

### 5.5 Human review gate
- No agent self-merges. Every PR needs a named human reviewer before merge, regardless of how "obviously correct" the agent judged its own output.
- A PR touching any §2 invariant needs a second reviewer, not just one.

### 5.6 Anti-slop PR checklist
See `.github/pull_request_template.md` — the same checklist, wired into every new PR automatically.

### 5.7 Anti-drift infrastructure
- `memory/INDEX.md` carries a living ~10-line "current state" summary, updated on every episodic record — not just a pointer to go find the latest file.
- `scripts/memory_check.py` (existing CI check) is extended to assert the INDEX pointer actually matches the latest episodic file — automated, not manual discipline.
- `AGENTS.md` and `.agents/skills/evidence-engine-delivery/SKILL.md` reference this document and its invariants directly.

---

## 6. Phased Implementation Plan

Each phase lists: **Goal**, **Tasks**, **Key files**, **Definition of Done**, **Primary risk** (cross-referenced to §7), **Suggested skillset**. Phases are mostly parallelizable across team members after Phase 0 and the shared contracts in Phase 1/2 land; dependencies are called out explicitly.

### Phase 0 — Foundations, docs, and anti-drift infrastructure
**Goal**: everyone (team + future agents) can read a small set of documents and know exactly what's decided, what's not, and what the rules are.
**Tasks**:
1. Write `docs/VISION.md` — done.
2. Update `docs/PROJECT_CHARTER.md` with the invariants in §2, I1 listed first — done.
3. Update `AGENTS.md`, `.agents/skills/evidence-engine-delivery/SKILL.md`, `references/evidence-boundaries.md` to reference this document — done.
4. Fix the stale `memory/INDEX.md` pointer; add the living current-state summary block — done.
5. Extend `scripts/memory_check.py` per §5.7 — done.
6. Set up the PR template with the anti-slop checklist — done.
**Key files**: `docs/VISION.md`, `docs/PROJECT_CHARTER.md`, `AGENTS.md`, `memory/INDEX.md`, `scripts/memory_check.py`, `.github/pull_request_template.md`.
**Definition of Done**: a new contributor (or agent) can read `AGENTS.md` → `docs/VISION.md` → this plan and understand the product, the invariants, and the process without asking a teammate.
**Primary risk**: none technical — the risk is skipping this phase under time pressure, which is exactly how the original drift happened.
**Skillset**: anyone; good onboarding task for a new team member.

### Phase 1 — Deterministic core: mutation pipeline + knowledge tracing
**Goal**: the hard, differentiated engineering — implemented and tested independent of any host-platform integration.
**Tasks**:
1. AST-level mutation-operator library (Python `ast` module): a catalog of well-defined operators (comparison-flip, off-by-one, guard-clause drop, ordering swap, etc.), each documented with what class of bug it produces.
2. Property-test-harness generator (Hypothesis-based): given a set of candidate invariant hypotheses (proposed by the host model, passed in as structured input — not generated by us), generates a runnable test harness.
3. Kill-ratio filtering logic: given a mutant and the harness, classify as accept (breaks exactly one verified property, still runs) / reject (breaks zero or many, or crashes/doesn't parse).
4. Verdict-format contract: define the single, structured, machine-parseable output format the host's code-execution tool must emit; write the validator that checks its *shape* before our server trusts it (the trust-boundary mitigation).
5. BKT module: per-skill 4-parameter (P(L0), P(T), P(G), P(S)) Bayesian update from real verifier outcomes; `select_target_invariant` ranking by lowest-confidence skill.
6. Content-boundary enforcement: any student-pasted text is only ever treated as a topic hint, never as literal mutation input (I1 enforcement in code).
**Key files**: new `mcp_server/mutation/` (operator library), `mcp_server/verification/` (harness generator, verdict validator), `mcp_server/knowledge_tracing/` (BKT), reusing existing deterministic pieces of `apps/api/app/runtime.py`, `interpretation.py`, `policy.py` where applicable.
**Definition of Done**: a test battery of known-good/known-bad invariant hypotheses and mutation candidates all classify correctly; BKT unit tests show P(mastery) moving the right direction on synthetic attempt sequences; a test proves pasted student code is never returned mutated.
**Primary risk**: kill-ratio tuning (R1), invariant-hypothesis reliability on messy input (R2).
**Skillset**: someone comfortable with Python AST manipulation, property-based testing, and basic Bayesian/statistical modeling — this is the phase most worth pairing an experienced engineer with an agent, rather than delegating outright.

### Phase 2 — MCP server & tool contracts
**Goal**: expose Phase 1's engine as a well-formed MCP server, with the structural guardrail (I6) baked into the schema layer, not the prompt layer.
**Tasks**:
1. Define and implement the tool surface: `derive_invariant_hypotheses`, `record_invariant_verification`, `synthesize_mutation_candidates`, `record_mutation_kill_results`, `select_target_invariant`, `submit_diagnosis`, `submit_repair_and_verify`, `update_skill_model`.
2. Schema-level guardrail: `submit_diagnosis`'s input/output types must not contain any field capable of carrying a verdict — enforce with a schema test, not a code-review habit.
3. Curated-fixture fallback tools (`list_fixtures`, `get_fixture`) wrapping the existing fixture library unchanged.
4. Tool descriptions carry the non-evaluative instructions read by the calling host model.
**Key files**: `mcp_server/tools/`, `mcp_server/server.py`, `docs/MCP_SERVER.md` (the technical reference doc — written as part of this phase).
**Definition of Done**: an MCP client (a test harness, not necessarily ChatGPT/Codex yet) can run the full predict→diagnose→repair→evidence loop against curated fixtures end-to-end; the schema guardrail test passes; `docs/MCP_SERVER.md` fully documents every tool's contract.
**Primary risk**: remote-execution trust boundary (R3) — this phase is where the mitigation is actually implemented, not just designed.
**Skillset**: backend engineer familiar with MCP/tool-schema design.

### Phase 3 — Canvas integration (read-only)
**Goal**: pull real course context in, with the read/never-read boundary enforced in code, not just policy.
**Tasks**:
1. Register a Canvas developer key scoped to the minimal read allowlist (course list, syllabus, modules, pages, files, assignment descriptions) — **requires institutional/admin coordination; start this early, it's likely the longest lead-time item in the whole plan** (see R5).
2. Implement the OAuth2 consent flow (student authorizes their own enrollments).
3. Implement `list_enrolled_courses`, `get_course_syllabus`, `get_course_modules`, `get_course_materials`, `get_assignment_description` as MCP tools.
4. Implement the code-level refusal for gradebook/submission/quiz-response endpoints, independent of the token's actual scope — belt-and-suspenders.
5. Write `docs/CANVAS_INTEGRATION.md`.
**Key files**: `mcp_server/canvas/`, `docs/CANVAS_INTEGRATION.md`.
**Definition of Done**: a test proves the Canvas client is constructed with only the allowlisted scopes and refuses to call any gradebook/submission endpoint even when reachable; a live (sandbox/demo) Canvas course's syllabus successfully drives a Phase 1 pipeline run end-to-end.
**Primary risk**: institutional access lead time (R5) — flagged as the item most likely to block the timeline if not started immediately.
**Skillset**: backend engineer; ideally someone who can also make the institutional ask (advisor/instructor contact).

### Phase 4 — ChatGPT App (Apps SDK)
**Goal**: the richer of the two client surfaces, with custom UI for the trace and evidence diff.
**Tasks**:
1. Apps SDK app scaffold, connected to the Phase 2 MCP server.
2. Custom UI widget: step-by-step visual diff for the evidence result (lighter style, not full animation — per earlier scoping decision).
3. Custom UI widget: tool-call trace panel (Planner/Diagnostician/Coach/Verifier, as ChatGPT's own tool-call sequence, styled).
4. Language-preference passthrough (tell the host model what language to converse in — §3, personalization).
5. Skill-state client storage: localStorage + QR-code cross-device transfer (client-only, no server persistence — I5).
**Key files**: new `chatgpt_app/` (or equivalent Apps SDK project structure), reusing UI ideas prototyped in `apps/web` where applicable.
**Definition of Done**: a full predict→diagnose→repair→evidence loop runs inside an actual ChatGPT conversation, sourced from either a Canvas topic or a named topic, with the trace and visual diff both visible.
**Primary risk**: Apps SDK is a newer/preview surface — budget time for platform rough edges (R6).
**Skillset**: frontend engineer comfortable with a new, less-documented SDK; pair with an agent for scaffolding, human-verify the integration points.

### Phase 5 — Codex plugin
**Goal**: extend the existing `plugins/evidence-engine-tutor` scaffold from a read-only source-mapper preview into a full client of the shared MCP server.
**Tasks**:
1. Wire the existing plugin's skill/MCP-connection scaffold to the Phase 2 server's full tool surface (not just the source-mapper).
2. Local workspace-file skill-state persistence (Codex's equivalent of the ChatGPT App's localStorage — I5).
3. Update `plugins/evidence-engine-tutor/README.md` and `docs/V2_CODEX_PLUGIN.md` to describe the full loop.
**Key files**: `plugins/evidence-engine-tutor/`, `docs/V2_CODEX_PLUGIN.md`.
**Definition of Done**: the same full loop as Phase 4's DoD, run inside an actual Codex session instead of ChatGPT.
**Primary risk**: low relative to other phases — this is mostly wiring already-scaffolded pieces to the Phase 2 contract.
**Skillset**: whoever built the original plugin scaffold, or anyone comfortable with Codex's skill/plugin format.

### Phase 6 — Content: curated library + procedural variation
**Goal**: enough seed content that Phase 1's engine has real, good material to draw from and vary, independent of live invariant-hypothesis generation working perfectly on the first try.
**Tasks**:
1. Author 4-6 new curated fixtures (BFS is done; add DFS, a sorting invariant, a recursion base-case bug, a linked-list invariant) in the existing JSON schema — dev-team-assisted via ChatGPT/Codex, human-reviewed before merge.
2. Procedural-variation logic for the curated set (fresh graph shapes/input arrays per the existing schema) as the reliable middle ground between "fixed 12 puzzles" and "fully live-synthesized from scratch."
**Key files**: `fixtures/challenges/`.
**Definition of Done**: at least 5 curated fixtures total, each passing the Phase 1 test battery; procedural variation produces at least 3 distinct variants per fixture, all independently verified.
**Primary risk**: content-quality risk (R2, shared with Phase 1).
**Skillset**: anyone comfortable reading/writing the fixture JSON schema; good task to involve a CS-education-minded teammate or instructor in (ties to Interdisciplinary Collaboration, §3).

### Phase 7 — Instructor dashboard (moonshot, lowest priority)
**Goal**: the "TA-triage" story from the pitch, without becoming part of the student flow or a privacy risk.
**Tasks**:
1. Aggregated, fully anonymized view of recurring misconception/skill-gap trends (seeded/synthetic data for the hackathon demo).
2. Explicit re-verification that the aggregation can never be reversed to identify an individual student (I5 extension) — this needs a specific test, not just a design intention.
**Key files**: `apps/web` (repurposed as the dashboard's home, not a public product surface).
**Definition of Done**: dashboard renders aggregate trends from seeded data; a test confirms no individual-student identification is possible from the exposed data.
**Primary risk**: lowest-priority item — cut first if the timeline is tight.
**Skillset**: anyone; low technical risk relative to Phases 1-3.

### Phase 8 — Demo readiness
**Goal**: a rehearsed, de-risked live demo that actually reflects Phases 1-6, not a scripted illusion of them.
**Tasks**:
1. Rewrite `docs/DEMO_RUNBOOK.md` around the live "pick a topic from a real Canvas course, watch a fresh scenario synthesize live" moment.
2. Pre-vet a small set of known-good demo topics/courses in advance specifically to de-risk kill-ratio failure live in front of judges — rehearsal, not scripting the outcome.
3. Full dry run via screen-share on a team member's Enterprise account (the actual judging format, R4).
4. Prepare the pitch narrative directly against §3's judging-criteria table so presentation time maps cleanly onto rubric points.
**Key files**: `docs/DEMO_RUNBOOK.md`.
**Definition of Done**: at least two full, successful dry runs of the live demo, on two different pre-vetted topics, timed to fit the actual presentation slot.
**Primary risk**: presentation-criterion risk if under-rehearsed — schedule this phase with real calendar time, not "whatever's left."
**Skillset**: whoever is presenting, plus one engineer on hand to react if something breaks live.

---

## 7. Consolidated Risk Register (sanity-check this section as a team)

| ID | Risk | Phase | Mitigation | Status |
|---|---|---|---|---|
| R1 | Kill-ratio tuning (mutant must be exactly one coherent bug) is genuinely hard, may take longer than budgeted | 1 | Real iteration against real content before hackathon; curated fixtures (Phase 6) as fallback if live generation underperforms | Open |
| R2 | Invariant-hypothesis / content-generation quality on messy or ambiguous input | 1, 6 | Scope to pure/deterministic code; explicit "not a good fit yet" response instead of a bad result | Open |
| R3 | Remote-execution trust boundary — we don't control the sandbox that runs verification | 1, 2 | Structured, validated verdict format; acknowledged, not eliminated | Open |
| R4 | Hackathon judges likely lack a UofU Enterprise seat | 8 | Live screen-share demo on a team member's account; no separate public fallback maintained | Accepted (decided) |
| R5 | Canvas developer-key registration needs institutional/admin coordination — likely the longest lead-time dependency in the whole plan | 3 | **Start this immediately, in parallel with Phase 0/1**, not sequentially after other phases | **Open — needs an owner named today** |
| R6 | ChatGPT Apps SDK is a newer/preview surface; may have undocumented rough edges | 4 | Budget slack time; Codex plugin (Phase 5) as a working fallback surface if Apps SDK blocks | Open |
| R7 | BKT cold start — noisy estimates on a student's first few attempts per skill | 1 | Present honestly as growing confidence, not immediate precision | Accepted (by design) |
| R8 | Team/timeline: this is a materially larger scope than a typical hackathon MVP (own admission — the "big bet" was chosen deliberately) | all | Explicit phase prioritization above (Phases 1-3 are load-bearing; 4/5 need at least one working surface, not necessarily both polished; 7 is cuttable) | **Open — needs explicit team timeline sanity-check, see §8** |
| R9 | Agent-generated slop (untested, unreviewed, off-spec AI output) | all | §5's full practice set — spec-first tasks, mandatory tests, human review gate, PR checklist | Mitigated by process (needs the team to actually follow it) |

---

## 8. Open Questions for the Team (please actually answer these, not just approve the doc)

1. **Canvas access (R5)**: who on the team can make the institutional ask for a scoped developer key, and by when? This is the plan's biggest schedule risk and currently has no named owner.
2. **Timeline sanity-check (R8)**: given the team's actual size and hours available before the hackathon, is the full Phase 1-8 scope realistic, or should Phase 4 *or* 5 (not both) be the initial target, with the other added only if time allows? Recommend deciding this explicitly rather than discovering it under deadline pressure.
3. **Instructor/course pilot (Community Engagement, Interdisciplinary Collaboration)**: does the team have an existing relationship with a UofU CS instructor willing to let us pilot against their real (anonymized) Canvas course structure, or does this need to be initiated fresh?
4. **Team roles per phase**: §6 suggests a skillset per phase but doesn't assign names — needs the team to self-assign, particularly Phase 1 (the hardest, most differentiated work) and Phase 3 (the most schedule-risky).
5. **Fallback posture if R1 (kill-ratio tuning) isn't solved in time**: confirm the team agrees the curated-fixture-library fallback (Phase 6) is an acceptable demo posture, not a failure state, so nobody feels pressure to ship an under-tested live-generation path just to avoid "falling back."

---

## 9. Team Sign-off

| Role | Name | Reviewed | Concerns / conditions | Date |
|---|---|---|---|---|
| Product/vision owner | | ☐ | | |
| Engineering lead | | ☐ | | |
| Canvas/institutional liaison | | ☐ | | |
| ML/testing-theory reviewer (Phase 1 sanity-check) | | ☐ | | |
| Presentation/demo owner | | ☐ | | |

**Recorded decisions this document assumes as already made** (see full reasoning trail in `memory/episodic/0013-hackathon-replan-and-implementation-plan.md`): CS/algorithms-only scope; MCP + ChatGPT App + Codex plugin access model; no public website; OpenAI for any low-volume AI calls we make ourselves; Canvas read-only and Core, not stretch. These are treated as settled — the open items in §8 are what still need real team input.
