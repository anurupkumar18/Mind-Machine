# Initial research and inspiration archive

> **Status: historical research, not a specification.** These notes capture early
> exploration and are preserved to give teammates useful context, alternative
> ideas, and leads for deeper investigation. They do **not** define the current
> implementation or guarantee the future product. Some ideas conflict with the
> current charter, current code, later team decisions, or one another.

**Research period:** August 2026 and earlier project exploration<br>
**Archived:** September 2, 2026<br>
**Authority:** Inspiration only; every claim and proposal requires fresh review

## Original source set

The original research was shared through three ChatGPT conversations:

1. <https://chatgpt.com/share/e/6a98b2c7-747c-800f-a404-a7a366df3b1e>
2. <https://chatgpt.com/share/e/6a98b2d4-aadc-800f-97e3-c542cea456b0>
3. <https://chatgpt.com/share/e/6a98b2e3-71f8-800f-bebc-b451b1096fc2>

Two pasted exports supplied with this archive contained a product-direction
handoff and a Canvas access/roadmap investigation. The exports did not identify
which conversation URL produced each section, so this document does not assign
individual claims to a specific URL.

The share pages may require ChatGPT access and may not remain available. Where a
teammate wants to rely on a factual claim, find the underlying primary source and
verify it again rather than citing the conversation.

## How to use this document

- Use it to ask better questions, find prior art, and avoid repeating discarded
  exploration.
- Do not use it as acceptance criteria, architecture, a permission decision, or
  proof that a named project or institutional path is still available.
- Treat named tools, modules, metrics, and product surfaces as proposals unless
  they are confirmed in the current source and tests.
- When this document conflicts with the current charter or a later approved
  decision, surface the discrepancy. Do not silently blend the two.
- Before implementation, record which idea is being adopted, what it supersedes,
  what evidence supports it, and how obsolete code or documentation will be
  removed or isolated.

The repository-wide interpretation rule is in [`../../AGENTS.md`](../../AGENTS.md).
The latest group product direction is
[`../TEAM_PRODUCT_DIRECTION.md`](../TEAM_PRODUCT_DIRECTION.md).

## Reusable ideas worth carrying forward

### 1. Evidence over fluent confidence

The strongest recurring idea is to distinguish “the code works” from “the learner
can reason about why it works.” A defensible learning loop asks the student to
commit to a prediction, observes a result, generates structured evidence, and only
then offers a cautious interpretation.

```text
student commitment
→ observable result
→ structured evidence
→ cautious interpretation
→ targeted retry
```

This aligns with the current verification engine, but the historical research
sometimes applied it to a student's own code. That input boundary is not currently
allowed; see the discrepancy matrix below.

### 2. Separate model assistance from correctness

The research proposed a useful responsibility split:

- models may help map objectives, select practice, ask follow-up questions, and
  summarize evidence;
- deterministic tools should produce correctness evidence where possible; and
- learning interpretations should preserve uncertainty and avoid fake precision.

The warning against model-generated mastery percentages remains valuable. Event-
level statements such as “the learner predicted the wrong frontier, diagnosed the
failure after evidence, and completed a repair” are more inspectable than an
unsupported percentage.

### 3. Procedural Socratic runbooks

The early notes suggested reusable diagnostic pathways rather than one-off prompts.
A three-level scaffold is a useful design seed:

1. name the relevant state, invariant, or structural area without giving the fix;
2. ask the learner to dry-run the code or representation; and
3. provide abstract preconditions, postconditions, or pseudocode constraints.

Example topics included index boundaries, mutable default arguments, runtime
exceptions, and locks held across `await`. These examples are not an approved
challenge catalog. A future content-design slice could evaluate whether runbooks
generalize while preserving the hidden-answer boundary.

### 4. Three kinds of project memory

The research separated:

- **episodic:** what happened in a session or implementation slice;
- **semantic:** approved facts, contracts, and architecture; and
- **procedural:** repeatable diagnostic or delivery pathways.

It also recommended keeping canonical memory in Git-reviewed documents and treating
any local search index as disposable and rebuildable. That principle still fits the
repository, provided old memory entries are treated as historical evidence rather
than current product requirements.

### 5. Context, experience, evidence, and infrastructure are different layers

One historical architecture separated:

```text
Context:        learning objectives, approved sources, repository context
Experience:     Socratic pairing, explanation, reflection
Evidence:       predictions, diagnostics, execution, tests, repairs
Infrastructure: MCP, host models, runbooks, storage, integrations
```

The separation is useful even if the inputs and product surfaces change. It can
help prevent Canvas, a browser extension, a model provider, or a particular plugin
from becoming mistaken for the product itself.

### 6. Start with one compelling vertical slice

The research repeatedly favored one deterministic, deeply tested learning journey
over a wide but shallow feature set. A generic version remains useful:

```text
safe challenge
→ observed failure or perturbation
→ learner prediction
→ bounded Socratic scaffold
→ diagnosis and repair
→ executed tests
→ evidence record
```

The exact challenge, whether student code may be involved, and the host surface are
separate decisions. The principle is to prove the learning interaction before
adding integrations for their own sake.

## Course-context and Canvas ideas to investigate

### Consent-first course workspace

The Canvas research suggested a lower-dependency path that starts with materials a
student or instructor is authorized to provide:

1. create a course workspace;
2. upload files or paste permitted text;
3. preview the sources before indexing;
4. explicitly consent to their use in that workspace;
5. answer only from indexed sources and show citations;
6. provide remove-source, delete-workspace, and data-export controls.

This inspired parts of the current study-workspace prototype, but the prototype is
plain-text, in-process, keyword-based, and lacks ownership controls. The research
flow is not implemented end to end.

Potential mitigations from the notes included source provenance, upload warnings,
sensitive-data detection, file-size and type limits, short retention defaults, and
an instructor-owned source path. Each needs legal, privacy, security, accessibility,
and academic-integrity review before being treated as a product requirement.

### Institution-sponsored LTI pilot

The historical roadmap proposed asking for a narrow, instructor-sponsored pilot
rather than broad API access:

- one course and one term;
- LTI 1.3 course-navigation placement;
- instructor-selected, published materials only;
- no grades, submissions, roster, or write operations;
- source citations, deletion controls, retention policy, security architecture,
  and a pilot evaluation plan.

Later possibilities mentioned Deep Linking, Names and Role Provisioning Services,
and Assignment and Grade Services. Those are research leads only. Requesting roster
or grade capabilities would materially change the product's privacy and governance
scope and is not authorized by the current charter or team direction.

### Non-solutions that remain useful warnings

The historical notes strongly warned against:

- collecting student-generated personal access tokens for a multi-user product;
- exporting or logging browser cookies;
- scraping authenticated Canvas pages or automating a student's login;
- treating an instructor's visibility as blanket permission to upload all course
  content; and
- treating a marketplace listing as a bypass around each institution's review.

These warnings are consistent with the current project direction. They still need
fresh primary-source verification before being used as legal or platform-policy
claims.

## Open-source and prior-art watchlist

These names appeared in the initial research. Inclusion means “investigate,” not
“adopt,” “verified,” or “currently compatible.” Before reuse, review the current
project, maintainers, license, security posture, accessibility, data flow,
deployment model, and architectural fit.

| Lead | Historical reason it looked interesting | Questions for a fresh review |
| --- | --- | --- |
| Socrates Skill | A `Read → Assess → Guide → Adapt → Confirm` learning sequence. | Is the project still maintained, licensed for reuse, and compatible with non-evaluative coaching? |
| Ben Rosche Socratic Tutor | Separation between instructor ground truth and the learner workspace. | What is the actual implementation and license, and can its boundary generalize safely? |
| Socratic Sentinel | MCP or terminal interception as part of a learning loop. | Does interception improve evidence, or add brittle coupling and surveillance risk? |
| Algorithm visualization projects | Turning state transitions into observable artifacts. | Does a visualization measure reasoning, or merely improve demo polish? |
| UC San Diego TritonAI/TritonGPT | A possible faculty-sponsored, campus-supported course assistant precedent. | What is publicly verified about governance, sources, Canvas integration, and student control today? |
| Instructure Project Athena | A possible institution-led, course-context product precedent. | Which capabilities are live, what permissions are used, and what privacy commitments are enforceable? |
| Georgia Tech ECE AI-Tutor | A course-material retrieval and voluntary-pilot research lead. | What did the study actually measure, and what architecture or Canvas access was documented? |
| CanvasCram | A student-project example connecting Canvas context to study generation. | Was its credential model compliant and scalable, or only suitable for a personal prototype? |
| University of Alberta LearnWise | A possible governance and adoption precedent. | What technical and institutional details are public and current? |
| Dong, “How to Build an AI Tutor…” | General source-ingestion and evidence-citing retrieval patterns. | Which parts are reproducible and suitable for the project's data boundaries? |
| TutorLLM | Retrieval plus learner-model or recommendation ideas. | Is personalization validated, explainable, and appropriate before the core grounded workflow works? |

The team should add primary-source links and dated verification notes when any lead
moves from inspiration into active discovery.

## Expansion ideas for fresh eyes

| Idea | Potential value | Do not assume |
| --- | --- | --- |
| Evidence map across attempts | Makes predictions, diagnoses, repairs, and retries inspectable. | That the map measures mastery or should become a score. |
| Procedural runbook library | Reuses well-designed Socratic pathways across challenge classes. | That early examples are correct, complete, or safe to expose. |
| Professor-authored class packages | Makes pedagogy and course boundaries explicit. | That enrollment can provision them automatically. |
| Institution-maintained universal guardrails | Gives students a supported baseline as AI tools evolve. | That one policy works for every discipline or host platform. |
| Source-grounded study workspace | Connects explanations and summaries to visible course sources. | That the current prototype has durable storage, semantic retrieval, or access control. |
| Repo-aware code defense | Could test whether a learner understands AI-assisted code. | That actual student coursework may be read or executed under the current charter. |
| Browser companion | Could make context and controls available near course work. | That an extension is allowed, necessary, accessible, or safer than approved APIs. |
| Multi-tenant LTI platform | Could support institution-controlled course deployments. | That LTI approval, identity, storage, or cross-institution registration is solved. |
| Instructor insights | Could reveal unanswered topics or content gaps. | That learner analytics, roster access, or dashboards are approved or privacy-preserving. |
| Multimodal study aids | Could support diagrams, voice, or visual comparisons. | That modality preference is a validated “learning style” or should outrank the core loop. |

## Known discrepancies and decision forks

| Historical note | Current repository position | Required treatment |
| --- | --- | --- |
| Use real student code and assignment constraints as the learning surface. | The current charter forbids reading, modifying, or executing actual coursework and uses curated or generated practice. | Treat this as an unresolved product fork. Do not implement against student coursework without a reviewed charter decision, consent model, and data-flow design. |
| Named tools `python_execute_diagnostics` and `python_ast_analyzer` already exist. | Those tool names are not part of the current MCP surface. The repository evolved toward challenge and study-workspace tools. | Treat the names and described capabilities as stale prototype notes; verify current source before planning. |
| Student uploads may include assignment prompts or rubric exports. | Current invariants exclude assignments, quizzes, discussions, submissions, and answer keys from the practice path. | Do not broaden allowed inputs by copying the historical list. Reconcile the charter first. |
| Free-for-Teacher Canvas remained available for testing. | Later repository notes say the trial path was discontinued or otherwise unavailable for the needed admin configuration. | Consider the status disputed and stale; reverify with primary sources before relying on it. |
| Live Canvas OAuth can be optional for the demo, with manual or fixture context. | The current project has mock topic grounding and a student-upload prototype; real Canvas remains institutionally gated. | Keep mocks and uploads honestly labeled. Do not present them as proof of production Canvas access. |
| LTI 1.3 is the best institutional path. | The September direction keeps Canvas, LTI, browser, and host-managed paths open. | Retain LTI as one discovery candidate, not the chosen architecture. |
| Mastery-oriented quizzes or learner modeling may be future phases. | The project rejects model-authored mastery percentages and has deferred real knowledge tracing. | Use “mastery” only as an aspirational learning outcome until validated measurement exists. |
| A student course workspace can answer from uploaded sources. | A limited implementation exists, but storage, file extraction, semantic retrieval, and ownership controls do not. | Distinguish the prototype from the desired experience in every product claim. |
| Enrollment could automatically provide a complete class package. | No provisioning mechanism or institutional permission has been verified. | Describe this only as a north-star institutional goal. |

## Questions for teammates reviewing with fresh eyes

1. Which historical idea still sharpens the learner value proposition, and which
   only adds integration scope?
2. What is the smallest experience that demonstrates improved reasoning rather
   than a more convenient chatbot?
3. Which current code paths support the latest product direction, which are useful
   experiments, and which are now dead or misleading?
4. Where should course context end and protected graded work begin for each product
   capability?
5. Can a class package be a portable, auditable contract rather than a collection
   of hidden prompts and one-off settings?
6. Which host surface gives the best student experience without making the system
   dependent on one vendor?
7. What would professors and IT need to inspect before approving even a one-course
   pilot?
8. Which claims need user research, learning evidence, or primary-source policy
   verification before they appear in a hackathon pitch?

## Promotion rule

An idea leaves this archive only through an explicit team decision. The adopting
change must:

1. cite the research seed and fresh supporting evidence;
2. state the desired observable behavior;
3. identify affected charter and data boundaries;
4. name superseded plans, docs, APIs, and code paths;
5. include a deletion or migration plan for obsolete implementation;
6. update tests and acceptance criteria; and
7. leave a dated decision record and episodic handoff.

This keeps the archive useful without allowing yesterday's improvisation to become
tomorrow's accidental architecture.
