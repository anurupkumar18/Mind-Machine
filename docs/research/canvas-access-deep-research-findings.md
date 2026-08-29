# Canvas LMS access: compliant paths and roadmap

Research findings from the deep-research session run against
`canvas-access-deep-research-prompt.md` in this same directory. Status
checked August 29, 2026.

**Bottom line**: there is no compliant student-only API workaround at UofU
when personal tokens and developer-key OAuth are disabled. LTI 1.3 is the
best approval path, but it still requires an institutional Canvas
administrator to register/deploy it. Do not use user-supplied tokens,
session-cookie scraping, or browser automation.

## 1. Compliant workarounds available now

| Path | Effort | Value | What it enables | Constraint |
|---|---|---|---|---|
| Direct student uploads | Low | High | PDFs, downloaded files, copied syllabus/assignment text, notes | Student must select material; no automatic sync |
| Instructor-provided export/upload | Low–medium | High | Full course content as `.imscc`, plus selected slides/readings | Requires an instructor/TA; excludes grades, submissions, quiz attempts, and student discussion posts |
| Fixture/mock Canvas | Low | Medium | Product, UX, RAG/evaluation, and demo development | Not proof of production integration |
| Free-for-Teacher sandbox | Medium | Medium | Test Canvas course behavior and import/export flows | Not a deployment substitute; no admin/developer-key LTI configuration |
| Campus-approved pilot LTI 1.3 | Medium–high | Very high | Real course context inside Canvas | Requires a Canvas/LTI administrator |
| OAuth/API integration | High | Very high | Cross-course sync and external app workflow | Requires institutional developer-key approval |

### Recommended immediate product shape

Build an "Add course materials" workflow, not a "Connect Canvas" workflow:

- Ask the student to upload only materials they are authorized to use:
  syllabus, instructor-provided PDFs/slides, assignment/rubric exports, or
  their own notes.
- Extract, index, and show every source used in answers.
- Let the student remove a document or delete the course workspace
  immediately.
- Clearly state that uploads are used only for that student's study
  workspace and are not shared with classmates or used to train models.

This avoids tokens, Canvas automation, and impersonated browser access. It
does not eliminate copyright, FERPA, institutional-policy, or
academic-integrity considerations; terms should require that uploaders
have permission and prohibit sharing course content.

### Important corrections / non-solutions

- **LTI 1.3 is not student self-service.** Canvas LTI registration and
  deployment use institution-controlled developer-key/admin
  configuration. It is a lower-risk approval request, not a technical
  bypass.
- **Free-for-Teacher** remains useful for testing, but Canvas states that
  developer-key configuration/admin access is not available there.
- **Common Cartridge is instructor-owned content export.** Canvas course
  export is generally for instructor/TA roles; it produces `.imscc`
  containing course content but not grades, submissions, quiz attempts, or
  student-authored discussion posts.
- No standard Canvas feature was found that lets a student export an
  entire enrolled course's modules, files, pages, and assignments as a
  personal-data package. Canvas Student ePortfolio has a data-export
  feature, but it is for the portfolio service, not enrolled Canvas
  courses.

### Do not do these

- Ask students to generate and paste personal access tokens — Canvas's
  OAuth documentation says multi-user applications must use OAuth and that
  asking another user for a manually generated token violates its terms.
- Export/log browser cookies, scrape authenticated pages, or automate a
  student login — substitutes a session credential for a token, same
  authorization/terms risk.
- Treat an instructor's ability to view material as authorization to
  upload an entire course, including copyrighted publisher content or
  student records.

## 2. Precedent — other schools and how access was obtained

Public sources almost never disclose the exact email chain, security-review
duration, or developer-key scopes. Where sources do not say, it would be
unsafe to infer them.

| Institution/project | Access model evidenced publicly | Scope / lesson |
|---|---|---|
| UC San Diego — TritonAI / TritonGPT | Campus-native Canvas integration; instructors request a connected course, UCSD verifies and configures it | Instructor selects approved Canvas areas/websites, can exclude assessment material, students access a course-grounded tutor. Strong model for "faculty sponsor → campus AI/LMS team → bounded pilot." |
| Hinds Community College + Instructure Project Athena | Institution partnered directly with Instructure after a pilot | Athena is designed around read-only access to material a student can view; Hinds planned a 7,000-student rollout after a spring pilot. Closest current product precedent for this use case. |
| Georgia Tech ECE AI-Tutor | Instructor/course-team deployment with IRB-approved study | RAG over course material, 118 voluntary users, 10,000+ interactions. Public paper doesn't specify Canvas API/LTI access — cite as a research/pilot precedent, not an API approval precedent. |
| New College of Florida — CanvasCram | Student thesis prototype using Canvas API | Closest student-project precedent. Public abstract says it implemented the Canvas API but doesn't document institutional approval or a compliant multi-user credential model. Do not replicate a token-collection workflow. |
| University of Alberta — LearnWise pilot | Institution-led pilot through teaching/learning governance | Useful as an institutional adoption precedent; public material doesn't disclose technical scopes/timelines. |

### UofU contact chain

UofU's published entry point is **UIT Digital Learning Technologies**,
which explicitly lists Learning Tools Interoperability and
education-technology consultation. Start with a faculty sponsor and a
one-course, read-only pilot request to DLT, rather than asking for broad
API access.

Ask for:
- One course, one term, instructor-sponsored.
- LTI 1.3, course-navigation placement.
- Read-only access to instructor-selected published materials.
- No grades, submissions, roster, or write operations.
- Source citations, deletion controls, retention policy, security
  architecture, and pilot evaluation plan.

That framing materially reduces review scope.

## 3. Research papers and prior art

- **CanvasCram** — undergraduate thesis: Canvas API feeds a RAG knowledge
  base to generate study guides and quizzes. Value is architectural; its
  credential/deployment model is not publicly established.
- **Georgia Tech AI-Tutor** — course-material RAG, Socratic interaction,
  instructor analytics, and an IRB-approved voluntary pilot.
- **Dong, "How to Build an AI Tutor…"** — general course-material
  ingestion with evidence-citing RAG, useful as a prototype reference
  rather than an LMS governance model.
- **TutorLLM** — combines retrieval with learner-model/knowledge-tracing
  recommendations; useful for a later personalization layer after basic
  grounded QA is reliable.
- **Instructure Project Athena** — not a paper, but important product
  prior art: course context, upcoming assessments, personalized study
  guides/quizzes, read-only student-permission-bound access, and privacy
  commitments.

The recurring design pattern: instructor-approved corpus → retrieval with
citations → Socratic coaching → voluntary pilot → analytics only after
governance approval.

## 4. Consent-first / student-export design pattern

### UX

1. Create course workspace.
2. Upload files or paste text/links manually.
3. Display a pre-index review: filename, page count, detected course, and
   "exclude" option.
4. Ask a narrow consent question: "Use these materials to answer
   questions in this workspace?"
5. Answer only from indexed sources and show page/file citations.
6. Provide "remove source," "delete workspace," and "download my data"
   controls.

### Data boundaries

| Include by default | Exclude by default |
|---|---|
| Syllabus, assignment prompts, instructor-provided files, student notes | Grades, submissions, peers' discussion posts, roster data, quiz/exam questions, copyrighted publisher content unless clearly permitted |

### Where it fails at scale

- No automatic updates when deadlines/modules change.
- High user effort and incomplete materials.
- Inconsistent file formats and inaccessible embedded media.
- Course-content licenses can prohibit redistribution to an external
  service even when a student can view the material.
- Students may accidentally upload private feedback, grades, or
  classmates' information.

Mitigations: document-level provenance, upload warnings, sensitive-data
detection, file-size/type limits, short retention defaults, and a
"course owner upload" path for instructors.

## 5. The ambitious version after approval

Build toward a multi-tenant LTI 1.3 / LTI Advantage platform, not a
token-driven consumer integration.

### Phase 1: safe, compelling pilot

- OIDC/LTI 1.3 launch in Course Navigation.
- Per-course tenant and role-aware session.
- Instructor chooses which materials may be indexed.
- Read-only retrieval from published material only.
- Source-level citations, feedback reporting, deletion, audit log.
- No grade passback, roster sync, or write permissions.

### Phase 2: instructor workflow

- **Deep Linking**: instructor selects/creates study activities and
  places them in a Canvas module or assignment.
- **Names and Role Provisioning Service (NRPS)**: only if a real
  collaborative/class-level feature needs roster membership; do not
  request it for a personal study tool.
- Instructor dashboard: approved corpus, source freshness, unanswered
  questions, and content-gap signals.

### Phase 3: assessed learning workflows

- **Assignment and Grade Services (AGS)**: create line items and return
  scores only if the institution explicitly wants graded formative
  activities. Keep it opt-in and instructor-reviewable.
- Mastery-oriented quizzes, spaced repetition, and instructor-authored
  feedback — not automatic high-stakes grading.

### Multi-institution reality

An App Center listing can improve discovery, but it does not bypass each
institution's security, procurement, privacy, and LTI-registration
process. Architect for per-institution registration: issuer, client ID,
deployment ID, JWKS validation, encrypted tenant configuration, and
separate data boundaries. OAuth can complement LTI for narrowly approved
REST endpoints, but it is not a universal sign-in switch for Canvas Cloud.

The product bar is clear from UCSD, Athena, and commercial LTI tools:
course-scoped, instructor-controlled sources; student-permission-bound
access; citations; strong privacy boundaries; and no unnecessary data
collection.
