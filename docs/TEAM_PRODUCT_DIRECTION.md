# Evidence Engine team product direction

**Decision date:** September 2, 2026<br>
**Source:** 30-minute team product deep dive<br>
**Owner:** Evidence Engine team<br>
**Status:** Group direction; feasibility open; implementation not scheduled

## Decision summary

The team agreed to explore Evidence Engine as more than a single code-practice
tool. The north star is an institution-supported learning layer that lets students
focus on course material instead of repeatedly learning how to configure AI,
compare tools, write prompts, install integrations, and rebuild a workflow for
every class or semester.

The desired experience combines:

- permitted Canvas or browser-based course context;
- ChatGPT, Codex, agents, custom GPTs, tools, plugins, and MCP servers as possible
  interaction and delivery surfaces;
- NotebookLM-style source-grounded Q&A, citations, summaries, and study aids;
- professor- and IT-approved class packages containing reusable skills,
  guardrails, hooks, tools, and configuration; and
- Evidence Engine's verified-practice loop, where learning claims come from
  executed evidence rather than model confidence.

This is an agreed product direction, not a final architecture, implementation
commitment, permission claim, or promise that automatic provisioning is possible.

Earlier research explored narrower, broader, and sometimes contradictory product
shapes. It is preserved in
[`research/INITIAL_RESEARCH_AND_INSPIRATION.md`](research/INITIAL_RESEARCH_AND_INSPIRATION.md)
as inspiration and a discrepancy register, not as an extension of this decision.

## Problem and opportunity

Students do not enter a course with equal time, money, technical confidence, or
knowledge of rapidly changing AI tools. Even when useful tools exist, students may
have to decide which model to use, create prompts and guardrails, connect course
materials, configure plugins, and repeat that work every semester. That setup cost
can distract from the intended subject and widen the gap between students who know
how to operate AI systems and students who do not.

Professors face the inverse problem: they want students to receive useful support
without leaking answers, undermining course policies, using unapproved data, or
turning every class into an AI-configuration exercise. University IT must also
evaluate identity, privacy, security, procurement, accessibility, support, and
vendor risk.

The opportunity is a shared baseline: the institution and teaching team define a
safe, course-relevant starting environment, while students retain meaningful
choice over how they learn within that boundary.

## North-star student experience

1. **Enroll once.** Enrollment makes an approved class package available without
   requiring the student to discover and assemble every AI component.
2. **Choose a comfortable surface.** The student works through ChatGPT, Codex, an
   agent, a custom GPT, or another supported interface rather than learning a
   separate Evidence Engine product.
3. **Receive course-aware support.** Permitted Canvas context, approved sources, or
   student-added materials ground answers and study aids in the class.
4. **Learn in the form that helps.** The system can offer cited explanations,
   summaries, study guides, questions, structured practice, visual support, and
   adjustable scaffolding without claiming unsupported “learning styles.”
5. **Practice, do not just consume.** Evidence Engine turns relevant objectives
   into safe practice that requires prediction, diagnosis, repair, and reflection.
6. **See evidence.** When correctness is objectively testable, the verifier runs
   the tests. The conversational model cannot invent the authoritative result.
7. **Stay in control.** Students can see what sources and tools are active, what
   data is used, and what can be removed or disconnected.

This is the experience to investigate. No enrollment event, Canvas API, extension,
or host platform has yet been proven to support the complete flow.

## Class package concept

A class package is a governance and configuration concept, not a defined file
format or API. It could combine two layers:

### Universal institutional layer

- consent and transparency requirements;
- privacy, retention, and data-boundary defaults;
- accessibility and learner-control expectations;
- source citation and provenance rules;
- safe tool-use and prompt-injection defenses;
- the separation between model coaching and authoritative evidence; and
- a supported way to update shared practices as AI platforms change.

### Course-specific layer

- professor-approved skills, prompts, and Socratic behaviors;
- course policies and graded-work boundaries;
- approved tools, plugins, hooks, and MCP servers;
- permitted materials, topics, and learning objectives;
- challenge catalogs and verification rules where applicable; and
- course-specific support and escalation information.

The package should save setup time without removing student agency or letting a
single instructor configuration silently override institutional safeguards.

## NotebookLM-style capability direction

“NotebookLM-style” describes a capability set, not a selected vendor, repository,
or requirement for full feature parity. The direction currently means:

- ingesting explicitly permitted sources;
- answering questions with clear citations back to those sources;
- generating source-grounded summaries and study aids;
- organizing context across a course or learning objective;
- showing provenance and allowing source removal; and
- connecting grounded understanding to active, verified practice.

Before implementation, the team must evaluate open-source projects for license,
maintenance, security, deployment model, accessibility, data handling, retrieval
quality, extensibility, and compatibility with the Evidence Engine boundary. No
project is selected or endorsed by this decision.

## Possible product surfaces

These are alternatives or complementary paths to investigate, not settled
architecture:

- **ChatGPT App or custom GPT:** approachable conversational access with course
  tools attached where account and workspace policy permit it.
- **Codex plugin or agent:** deeper support for code reasoning, controlled
  workspace interaction, and verified programming practice.
- **MCP server:** shared capability layer that can serve multiple approved hosts.
- **Canvas integration:** course roster, topic, and source context where scopes,
  consent, and institutional approval allow it.
- **Companion browser extension:** a possible bridge or learner control surface
  only if platform policy, institutional security, and accessibility review permit
  it. It must never be used to bypass Canvas or host access controls.

## Stakeholder view

### Students

The product should reduce repeated setup, provide a consistent safety baseline,
support different levels of AI familiarity, preserve control over data and
scaffolding, and keep attention on learning the course material.

### Professors and teaching teams

The product should make pedagogy and course boundaries configurable and visible,
keep graded work protected, provide source provenance, and let instructors approve
the learning tools associated with their course without making them operate the
underlying infrastructure.

### University IT and governance teams

The product must make identity, consent, data flow, retention, access control,
security, accessibility, procurement, vendor dependencies, auditability, support
ownership, and incident response inspectable before institutional use.

## Relationship to the current repository

| Category | What is true now | What this decision adds |
| --- | --- | --- |
| Verified practice | A deterministic BFS learning UI and an MCP repair workflow exist; the verification kernel has also been exercised with binary search. | Make verified practice one capability inside a broader course-aware learning environment. |
| Study workspace | Plain-text, in-process, keyword-based source retrieval and citation tools exist as an early prototype. | Explore source-grounded Q&A, summaries, study aids, durable student control, and course-level context. |
| Canvas | A fixture-backed mock demonstrates topic matching; real institutional access is blocked and gated. | Explore Canvas as one approved context and provisioning surface, not as a presumed integration. |
| Host delivery | Codex stdio connectivity is verified; ChatGPT has only passed an external protocol handshake. | Explore a consistent capability layer across approved ChatGPT, Codex, agent, GPT, plugin, and MCP surfaces. |
| Institutional packages | No enrollment-triggered provisioning or class-package contract exists. | Investigate whether professors and IT can centrally approve and provision a safe course baseline. |
| Browser extension | No extension exists. | Treat an extension as one feasibility option, never as an access-control workaround. |

Nothing in this decision changes application behavior, institutional permission,
or the current charter invariants.

## Decisions made

- Keep the product name **Evidence Engine**.
- Broaden the north star from a standalone code-practice loop to a low-setup,
  institution-supported learning layer anchored by verified practice.
- Treat student experience and equitable access to a strong AI setup as first-order
  product goals.
- Explore a professor- and IT-approved class-package model.
- Treat Canvas, a browser extension, ChatGPT, Codex, agents, GPTs, plugins, and MCP
  as possible surfaces or connectors rather than prematurely selecting one stack.
- Define the NotebookLM direction at the capability level and evaluate open-source
  implementations later.
- Preserve the existing boundaries around graded work, hidden tests, consent, and
  model-authored verdicts during discovery.

## Not decided

- whether Canvas permits or supports the required access and provisioning;
- whether automatic access can be triggered by enrollment;
- whether a browser extension is necessary, allowed, or maintainable;
- which host surface should be primary;
- which open-source NotebookLM-like project, if any, should be adopted;
- the class-package schema, distribution mechanism, update policy, or owner;
- data storage, retention, tenancy, identity, or authorization architecture;
- funding, procurement, hosting, service-level expectations, or support model;
- how the existing charter should change for direct-answer study support; or
- implementation milestones or delivery dates.

## Discovery questions and risks

1. **Institutional permissions:** who can approve Canvas access, custom GPTs,
   plugins, MCP servers, extensions, and enrollment-linked provisioning?
2. **Data boundary:** which course materials may flow to which systems, for what
   purpose, for how long, and under whose control?
3. **Graded work:** how are assignments, exams, submissions, answer keys, and
   instructor-only content excluded or handled?
4. **Identity and access:** how are course membership, workspace ownership,
   removal, role changes, and least privilege enforced?
5. **Course-package governance:** who authors, reviews, versions, distributes,
   updates, audits, and retires each component?
6. **Vendor and platform change:** how does the experience remain stable as AI
   products, APIs, policies, and model behavior evolve?
7. **Open-source fit:** which projects meet license, security, quality,
   accessibility, deployment, and maintenance requirements?
8. **Equity and accessibility:** does the institutional baseline genuinely help
   students with different devices, abilities, schedules, and AI familiarity?
9. **Pedagogical evidence:** which outcomes show better learning without turning a
   heuristic or model opinion into a mastery claim?
10. **Operations:** who pays for, secures, monitors, supports, and responds to
    incidents in the shared infrastructure?

## Deferred next stage

No implementation begins from this decision alone. A future discovery slice should
bring professors, students, accessibility partners, Canvas administrators,
information security, privacy/legal, procurement, and platform owners into the
same conversation. Its outputs should be a validated student journey, an approved
data-flow map, a permission matrix, class-package ownership rules, an open-source
component evaluation, and a scoped pilot proposal. Any resulting charter or
architecture change requires separate review.

## Related references

- [`../README.md`](../README.md) — teammate- and judge-facing repository overview
- [`VISION.md`](VISION.md) — product framing
- [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md) — currently authoritative invariants
- [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md) — current phased plan and
  unscheduled discovery note
- [`CANVAS_INTEGRATION.md`](CANVAS_INTEGRATION.md) — current mock and access gate
- [`STUDY_WORKSPACE.md`](STUDY_WORKSPACE.md) — current source-grounding prototype
- [`DISCORD_TLDR.md`](DISCORD_TLDR.md) — copy-ready team recap
- [`research/INITIAL_RESEARCH_AND_INSPIRATION.md`](research/INITIAL_RESEARCH_AND_INSPIRATION.md)
  — historical research seeds, prior-art leads, and known discrepancies
