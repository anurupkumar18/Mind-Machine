# Evidence Engine — Implementation Plan & Team Review Package (Revision 8)

**Repo:** Mind-Machine (product name: "Evidence Engine") · **Purpose of this document:** the single reference for team review, sanity-check, and sign-off, and the source of task IDs every PR should reference (see §5.1... now §7.1 below).

---

## 0. What changed this revision, and why

Revision 7 of this plan (MCP server + ChatGPT App/Codex plugin + Canvas, docs/anti-drift infra) merged to `master`. An external technical review of that merged plan found one finding serious enough to redesign the core architecture around: **Evidence Engine did not actually execute the verification it treated as authoritative.** The host platform (ChatGPT/Codex) ran the generated tests and reported a verdict; our server validated the *shape* of that report, not that execution genuinely happened as described. That directly undermined invariant I2 and the product's central differentiator.

The review raised nine other points. Per explicit instruction, this revision biases toward the existing plan and only acts where a critique was strong enough to survive scrutiny or where it was put to the team and explicitly agreed. Six decisions came out of that review:

1. **Verification moves server-side.** Evidence Engine now runs the tests itself, in a controlled sandbox it owns, and signs the result. The load-bearing fix — see §1 (I8) and §3.
2. **Canvas stays Core**, but real content is hard-gated behind confirmed institutional data-policy approval, the default allowlist is narrowed, and a backup ingestion/caching path is added (built on the same sanctioned API, never a policy-bypassing scraper) so students don't have to re-supply course context every session — see §4.
3. **Knowledge tracing (BKT) is cut for now**, deferred to post-pilot. Replaced with a transparent heuristic explicitly not called mastery estimation — see §5.
4. **Scope stays ambitious** (dashboard, QR transfer, dual client surfaces, procedural generation all stay), but phase order changes to front-load the highest-uncertainty questions before deeper build-out — see §6.
5. **The MCP tool surface consolidates** from 8 granular tools to 4 model-facing workflow tools behind a signed challenge token, with each tool returning structured trace metadata so the visible-trace UI still works — see §3.
6. **Overstated language throughout the pitch is corrected** — "structurally impossible to leak," "never repeats," "no login/install," "zero incremental cost" all get precise, defensible replacements (applied in `docs/VISION.md`, `README.md`, this document).

Not adopted: the review's recommendation to drop the dashboard, QR transfer, dual-surface strategy, and procedural generation outright — kept, resequenced around risk instead. The "hard AI engineering" framing critique — kept as-is; the underlying engineering is substantial regardless of pitch phrasing.

---

## 1. Non-Negotiable Invariants

See `docs/PROJECT_CHARTER.md` for the authoritative table (I1-I8). Summary of what changed this revision: I1 narrowed to explicitly exclude assignment/quiz/discussion/submission content; I2 strengthened from "deterministic verification" to "executed inside our own sandbox, never self-reported"; I3 clarified to distinguish "no per-student LLM cost" (still true) from "we run no infrastructure" (never should have been implied); I4 gated behind confirmed institutional approval and narrowed to syllabus/titles by default; I5 reworded — "no login" was true of Evidence Engine itself, not the overall flow; I6 strengthened from schema-omission to genuinely never exposing hidden tests to the coaching model; I7 unchanged in intent; **I8 is new** — the signed, sandboxed evidence record that makes I2 true rather than aspirational.

---

## 2. Executive Summary (updated)

**Problem**: unchanged — students can feel like they understand a lecture and still fail to apply it.

**Solution**: Evidence Engine is an MCP-based tool, delivered as a ChatGPT App and a Codex plugin, that generates fresh, verified practice bugs for a student to diagnose and repair. Evidence now comes from tests **executed inside Evidence Engine's own sandbox** — a signed evidence record, not a shape-checked claim. Content is grounded in the student's own Canvas course once institutional approval allows it. Students don't create a separate Evidence Engine account or pay for an LLM API key; we carry no per-student LLM cost, but we do carry the cost of hosting the MCP server and the verification sandbox.

---

## 3. Architecture Overview (redesigned trust chain + consolidated tool surface)

```
Student (UofU account,        ChatGPT App / Codex plugin
existing ChatGPT/Codex   -->  (host model does the conversational
access)                        reasoning; narrates evidence records
                               it cannot alter — I3, I8)
                                        |
                                        |  MCP: 4 workflow tools only
                                        |  (start_challenge, submit_prediction,
                                        |   submit_diagnosis, submit_repair)
                                        |  each response carries structured
                                        |  trace metadata for UI display
                                        v
                        Evidence Engine MCP server
                        (issues an opaque signed challenge
                         token per session; internal pipeline
                         steps are NOT separately model-callable)
                                        |
                    +-------------------+-------------------+
                    v                                       v
     Internal content pipeline                  Canvas read-only client
     (server-side only):                        (gated behind institutional
     - select/generate from a vetted             approval, I4; narrowed
       reference-implementation +                 allowlist by default;
       property-DSL catalog (3.1)                  backup caching path, §4)
     - AST mutation + kill-ratio filter
     - hidden tests never leave the server
                    |
                    v
     Evidence Engine's own sandbox (I8)
     - isolated container: network off,
       CPU/memory/process/time caps
     - executes the submitted repair against
       versioned hidden tests + the property DSL
     - produces a signed evidence record
                    |
                    v
     submit_repair returns the signed record
     to the host model — the record is
     authoritative; the host cannot edit it
```

### 3.1 Property representation — a declarative DSL, not model-authored executable code

Now that Evidence Engine executes code itself (I8), letting a model author free-form Python "invariants" would be a direct code-injection path into our own infrastructure. Properties are represented declaratively and only predefined property constructors become executable code, e.g.:

```json
{"function": "bfs", "property": "output_is_permutation", "arguments": ["reachable_vertices"], "oracle": "reference_implementation_v3"}
```

The host model's role narrows to *selecting which property from a curated, reviewed catalog* applies to a given challenge, not proposing free-form test code. This removes the single riskiest, least-specified step from revision 7's design while preserving the "varied, verified practice content" story: many curated reference implementations × many catalog properties × many mutation operators still produces substantial variety without ever executing untrusted, model-authored code.

### 3.2 Tool surface (consolidated)

Four model-facing tools, each backed by an opaque signed challenge token:
- `start_challenge` — issues a new challenge instance, returns the token and a trace-metadata stub.
- `submit_prediction` — records the student's state prediction; returns trace metadata for the "Planner" stage.
- `submit_diagnosis` — records the student's diagnosis; per I6, never receives or returns the verdict; returns trace metadata for the "Diagnostician/Coach" stage.
- `submit_repair` — the only tool that triggers real sandboxed execution (I8); returns the signed evidence record plus trace metadata for the "Verifier" stage.

This keeps the visible-trace UI (Planner → Diagnostician → Coach → Verifier) working via structured trace data on each response, while removing the 8-tool granular surface that was a tampering and orchestration-failure risk. Internal pipeline mechanics are never separately callable by the host model.

---

## 4. Canvas Integration (institutional gate + narrowed scope + backup ingestion path)

**Hard gate**: no real Canvas content is transmitted anywhere — not to the host platform, not to our MCP server, not to logs — until UofU's privacy/security office and Canvas administration have confirmed in writing that this data flow is approved. This is a Phase 1 feasibility-spike blocker (§6), not a background risk to resolve eventually.

Confirmed against Canvas's own developer docs: this gate has no self-service bypass, by policy, not just by this institution's configuration. OAuth2 developer-key registration — the credential a real per-student-consent integration needs — is admin-only ("developer keys are issued by the admin of the institution," per `developerdocs.instructure.com`), and Canvas's own API Policy explicitly forbids collecting personal access tokens from users as a substitute ("asking any other user to manually generate a token and enter it into your application is a violation of Canvas' API Policy"). There is no engineering path around UofU's Canvas admin approval — only an institutional one.

**Narrowed default allowlist**: syllabus text and module/topic *titles* only. `get_assignment_description` is removed from the tool surface entirely — assignment/quiz/discussion/submission content is excluded by design, since that content can itself contain homework or exam prompts (a direct I1 risk, not just a privacy one). Full syllabus/materials access beyond titles remains available only behind the institutional approval above, and even then never extends to assignments, quizzes, discussions, or submissions.

**All Canvas text is treated as untrusted data, never instructions** — stripped of HTML/scripts, length-capped, no following of external links, provenance preserved for citation. `docs/CANVAS_INTEGRATION.md` (written alongside Phase 4) must document exactly which systems Canvas data reaches and for how long.

**Backup/complementary ingestion path**: the goal is for a student to connect their course context once and have it available every session, with Codex/ChatGPT as the one place they need to go — not something they bounce between Canvas and the tool for.
- **What it is**: client-side caching of already-fetched, already-approved Canvas context (the same sanctioned OAuth2 API calls as the primary path, cached locally so a student isn't re-fetching or re-pasting every session, consistent with I5's no-server-persistence boundary), and potentially a lightweight companion tool/extension calling the same sanctioned API using the student's own authenticated session, as an alternate client rather than a second access path.
- **What it explicitly is not**: literal HTML scraping or any technique that bypasses Canvas's actual access controls or OAuth consent flow — that would likely violate Canvas's terms of service and undermine the institutional-trust story I4 depends on. This path is bound by the identical approval gate and untrusted-data handling as the primary path; it changes how often context needs re-supplying, not what's allowed to flow.

---

## 5. Knowledge tracing — cut for now (was BKT, revision 7)

Real Bayesian Knowledge Tracing is deferred to post-pilot. The review's methodological objections were substantive: no stable skill taxonomy, no challenge-to-skill mapping, no calibrated parameters, the untested assumption that one repair attempt represents one skill, and no handling of item difficulty or forgetting. A handful of monotonicity unit tests proves the formula was implemented correctly, not that the resulting estimate means anything — and "not a mastery estimator" sitting next to a system computing and storing P(mastery) was a real contradiction, not just optics.

**Replacement for the MVP**: a transparent heuristic — recent pass/fail history per skill tag (last N attempts), targeting tags with the lowest recent success rate. Call this **practice-selection state**; explicitly not a mastery estimate, never framed as one. Prerequisites a future real-BKT phase would need (skill taxonomy, Q-matrix, calibration data, uncertainty intervals) are documented as explicit future work in `docs/VISION.md`, contingent on pilot data existing to calibrate against.

---

## 6. Phased Implementation Plan (resequenced, risk-first)

Documentation, invariants, and anti-drift infrastructure (this revision's predecessor) is **done**, merged. Everything below is new or restructured.

### Phase 1 — Feasibility spikes (blocking gate; run before deeper build)
1. **Institutional access**: confirm whether a UofU ChatGPT Edu/Codex workspace admin can approve installing a custom App/plugin before the hackathon, and who that contact is. If unresolvable in time, decide the fallback (personal accounts for the demo, org approval as a stated next step) explicitly, not under deadline pressure.
2. **MCP connectivity**: get one real MCP tool successfully invoked from the target ChatGPT workspace and from Codex.
3. **Trusted execution proof-of-concept**: build the minimal version of the sandbox in §3 and execute one fixed challenge's hidden tests against a known-good and a known-bad repair, producing a signed evidence record. The riskiest new infrastructure in the whole plan — prove it before the mutation pipeline depends on it.
4. **Canvas institutional decision**: obtain a Canvas sandbox/dev key and an explicit answer (even informal) on the §4 data-policy question — or document clearly that it's unresolved and keep Canvas fully gated.
**Definition of Done**: all four spikes have a clear outcome (pass, fail, or "unresolved, gated") — none silently skipped. Any failure triggers an explicit scope/architecture conversation.

### Phase 2 — Trusted challenge kernel
Curated reference implementations + versioned hidden tests; the property DSL and catalog (§3.1); the server-controlled sandbox; signed evidence records (I8); reproducible seeds and a recorded runtime digest; the AST mutation-operator library and kill-ratio filtering, operating within the property-DSL constraint; type/context-aware mutations and equivalent-mutant tolerance.
**Definition of Done**: a known-good/known-bad mutation-candidate test battery classifies correctly; a fixed challenge with a known-good and known-bad repair produces correct signed evidence records end-to-end through the real sandbox.

### Phase 3 — MCP workflow
The 4 workflow tools (§3.2) with opaque signed challenge tokens; structured trace metadata per response; I6 enforced by never sending hidden tests/canonical repairs to the coaching model's context; the answer-leakage/over-helping behavioral eval set (I6, I7).
**Definition of Done**: full predict→diagnose→repair→evidence loop runs end-to-end against Phase 2's kernel; the behavioral eval set passes; no tool response prior to `submit_repair` contains verdict or hidden-test information.
**Status**: the 4-tool surface and the opaque signed challenge token exist and the full loop runs end-to-end (`apps/api/app/mcp_server.py`, verified over a real stdio subprocess, not just in-memory tests — see `memory/episodic/0021-*.md`). **The answer-leakage/over-helping behavioral eval set (I6, I7) now exists**: `apps/api/tests/test_guardrails.py` sweeps `start_challenge`/`submit_prediction`/`submit_diagnosis` across the realistic and adversarial input space (all valid `attempt` values, matched/near-matched/adversarial `diagnosis` strings incl. prompt-injection-style probes, malformed predictions) and asserts no evidence-only field or hidden-content substring (the reference implementation's source, both signing secrets) ever appears — confirmed to actually have teeth by deliberately injecting a leak and watching it fail (`memory/episodic/0022-*.md`). Token verification still doesn't enforce tool-call ordering (nothing stops calling `submit_repair` first) — that's the one remaining stated gap in this phase.

### Phase 4 — Canvas integration
Proceeds only once Phase 1's Canvas spike resolves. Narrowed allowlist, backup/caching ingestion path, `docs/CANVAS_INTEGRATION.md`.

### Phase 5 — ChatGPT App · Phase 6 — Codex plugin
Unchanged in shape from revision 7, built against the consolidated 4-tool surface.

### Phase 7 — Content: curated library + procedural variation
Folds in property-DSL catalog authoring; 8-12 human-reviewed challenges across 3-4 bug classes, multiple validated variants each, explicit equivalent-mutant/ambiguous-repair review.

### Phase 8 — Instructor dashboard (moonshot, kept, lowest priority)
Unchanged — still cuttable first, still requires the anonymization-can't-be-reversed test.

### Phase 9 — Pilot, Evaluation & Demo Readiness
A small pilot (5-10 students/teammates); a pre/post transfer task and delayed-retention check; hint-leakage rate measured against real sessions; completion/retry rates and time-to-first-challenge; a basic usability/trust read; an explicit comparison against plain ChatGPT with no tool; then the demo rehearsal (pre-vetted topics, screen-share dry run, pitch mapped to the judging-criteria table).
**Definition of Done**: pilot data collected and summarized; at least two full successful demo dry runs; every "why this wins" pitch claim is backed by something observed in the pilot or explicitly labeled a design rationale rather than a measured outcome.

---

## 7. Agentic Software Engineering Practices — unchanged from revision 7

Spec-first tasks referencing a phase/task ID here; verify SDK/API usage against current docs before writing integration code (this project has now been corrected twice by unverified assumptions — once on the access model, once on the verification trust chain — the same discipline applies going forward); test-first with mandatory guardrail-suite extension for any new host-reachable tool; small traceable diffs with an episodic record per merge; human review gate, second reviewer for anything touching an invariant. See `.github/pull_request_template.md` for the PR checklist.

---

## 8. Consolidated Risk Register

| ID | Risk | Phase | Mitigation | Status |
|---|---|---|---|---|
| R1 | Kill-ratio tuning still genuinely hard | 2 | Real iteration before the hackathon; curated fixtures as fallback | Open, first operator built: `app.domain.mutation` implements comparison-operator replacement (Eq/NotEq/Lt/GtE/Gt/LtE/In/NotIn/Is/IsNot), generic across any source, verified to actually classify correctly through the real sandbox+property pipeline for the one comparison in the traversal-invariant-02 reference implementation. Only one operator type exists; kill-ratio *tuning* and equivalent-mutant tolerance are still unaddressed — see `memory/episodic/0020-*.md` |
| R2 | Content-generation quality on the property-DSL catalog | 2, 7 | Catalog is human-reviewed and narrow by design, lower risk than free-form hypothesis generation | Open, reduced. First slice built: `app.domain.properties` implements `output_equals_reference` and `output_is_permutation` against a reference-oracle execution model (not hand-authored expected values) — see `memory/episodic/0019-*.md` |
| R3 | ~~Remote-execution trust boundary~~ | — | **Resolved** — verification is server-side and signed (I8) | Resolved |
| R4 | Judges likely lack a UofU seat | 9 | Live screen-share demo, no public fallback | Accepted |
| R5 | Canvas institutional approval lead time | 1, 4 | Explicit Phase 1 blocking spike, needs a named owner | Open — needs an owner named. Confirmed blocked: UofU Canvas admins have disabled self-service access tokens (a UofU admin must generate one on request); Instructure's public trial instance is discontinued. Both self-service paths are dead ends; only a direct UofU Canvas-admin contact remains |
| R6 | ChatGPT Apps SDK is a newer, preview surface | 5 | Budget slack; Codex plugin as a working fallback | Open; MCP server itself now proven reachable over streamable-http (`docs/MCP_SERVER.md`), a public HTTPS endpoint and workspace approval remain open |
| R7 | Practice-selection heuristic (was BKT cold start) | 2 | Simpler heuristic, no calibration claim being made | Reduced |
| R8 | Timeline: ambitious scope kept in full | all | Resequenced risk-first (Phase 1 spikes) so a hard blocker surfaces early | Open — needs team timeline sanity-check |
| R9 | Agent-generated slop | all | Spec-first tasks, mandatory tests, human review, PR checklist | Process in place |
| R10 | Sandbox build is real, non-trivial infrastructure | 1, 2 | Phase 1 spike proves the minimal version first; scope to exactly what verification needs | Spike passed (`apps/api/app/domain/sandbox.py`); production-grade container/VM isolation still open for Phase 2 |
| R11 | UofU workspace admin approval may not be obtainable before the hackathon | 1 | Explicit Phase 1 spike; fallback decided in advance | Open — highest-priority unknown. Candidate contacts and process identified (§9); nobody has reached out yet. Fallback if this doesn't resolve in time: personal ChatGPT/Codex accounts for the demo (OpenAI's separate "Codex for Students" $100-credit program, independent of any UofU approval, is a viable personal-account fallback path — confirmed to exist, not yet tested against this project) |

---

## 9. Open Questions for the Team

1. **Sandbox ownership (R10)**: who builds and operates the verification sandbox — skillset, hosting choice, isolation approach need an owner.
2. **Workspace admin contact (R11)** — candidate contacts identified (public info from `ai.utah.edu/about.php`), not yet reached out to (see `memory/episodic/0018-*.md`): UofU's ChatGPT Edu offering **explicitly includes Codex** (confirmed on `ai.utah.edu/tools/chatgpt/index.php`), and there is a formal review process for a custom tool/GPT not already approved — the **AI Tool Form** (`bit.ly/ai-tools-utah`), reviewed by IT, information security, legal counsel, "and other stakeholders as necessary." The published AI Office Leadership roster's "Technology, Tools, Infrastructure" function (most relevant to installing a custom App/plugin) is Shawn Halladay, Jake Johansen, Jim Livingston, Caprice Post, and Jon Thomas; Callie Reed is the AI Programs Manager and a reasonable single point of contact; Manish Parashar is Chief AI Officer. Someone on the team needs to actually submit the AI Tool Form and/or email one of these contacts — an AI agent submitting a form or sending an email on the team's behalf isn't appropriate here, this needs a real person's name attached to the ask.
3. **Canvas institutional contact (R5)**: still needs a named owner.
4. **Timeline sanity-check (R8)**: does the team agree Phase 1's four spikes should gate further work, even at the cost of less calendar time for polish later?
5. **Pilot participants (Phase 9)**: who are the 5-10 students/teammates, and is there lead time to get delayed-retention data, or does that compress to same-session-only measurement?

---

## 10. Team Sign-off

Roles: product/vision owner, engineering lead, Canvas/institutional liaison, ML/testing-theory reviewer, presentation/demo owner, **sandbox/infra owner** (new this revision, given R10/R11 are now the plan's biggest unknowns).

**Recorded decisions this document assumes as already made**: revision 7's decisions, plus the six in §0 above. These are settled — §9 is what still needs real team input.
