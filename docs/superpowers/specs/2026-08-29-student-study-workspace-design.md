# Student study workspace (real materials, cited Q&A) — design

## Status

Approved for implementation, pending one feasibility spike (see "Blocking
unknown" below). Written 2026-08-29.

## Problem

`docs/research/canvas-access-deep-research-findings.md` (recorded in
`memory/episodic/0029-canvas-access-research-consent-upload-path.md`)
found that real Canvas API/LTI access stays institutionally blocked (R5,
unchanged), but a genuinely compliant alternative needs no institutional
approval at all: a student uploads their own course materials directly.

This design goes further than using that upload path just to pick *which
coding challenge* to practice (the narrow option considered and rejected
during brainstorming). Instead, per explicit product direction, it builds
the fuller vision from the research doc: a **student study workspace** —
upload real course materials, ask questions about them, get answers with
citations back to the source material.

## Relationship to Evidence Engine's existing identity

This is a **second, distinct capability**, not a variant of the existing
code-repair coaching loop. `docs/PROJECT_CHARTER.md`'s thesis currently
states Evidence Engine "is not a generic tutor" — this workspace *is* a
general study Q&A tool by design, and is intentionally allowed to answer
directly, unlike the non-evaluative Socratic coaching in `submit_diagnosis`
(I6). Per explicit product decision, the charter itself gets revised (not
a "second mode" bolted on, not a separate product) — the thesis and
invariants I1, I2, I3, I5, I6 all need new or amended language to say what
each capability still guarantees. **Writing that revised charter language
is the next task after this design is approved**, informed directly by
what's specified here; this document intentionally flags every invariant
this design touches so that follow-up rewrite has a concrete list to work
from, rather than re-deriving it.

### Invariants this design changes (for the charter-rewrite task to act on)

- **I1** (never operates on a student's actual coursework/homework/exam):
  currently an absolute prohibition. This design needs a redrawn boundary:
  *allowed* — syllabus, instructor-provided files, assignment/rubric
  *prompts* (not the student's own submitted answers), the student's own
  notes; *excluded* — graded submissions, quiz/exam questions, roster or
  peer-authored content, gradebook data. The reject/flag heuristics below
  are the enforcement mechanism; the charter needs to state this is a
  best-effort heuristic boundary, not a guarantee (matching this project's
  existing honesty about heuristic limits elsewhere — e.g. the
  practice-selection heuristic, `topic_matching.py`'s keyword matching).
- **I2** (no model ever decides pass/fail; evidence always from sandboxed
  execution): unaffected for the code-repair loop. Needs a clarifying
  sentence that this invariant is scoped to that loop specifically, since
  the workspace has no pass/fail concept at all — it answers questions,
  it doesn't grade or verify anything.
- **I3** (never call an LLM on a student's behalf): stays intact by
  design — `answer_from_materials` returns retrieved excerpts and
  citations only; the host platform's own model (already the case for
  everything else) synthesizes the actual answer. No embedding model, no
  server-side LLM call anywhere in this design (see "Retrieval" below).
- **I5** (no separate account, server-side learner data store): this is
  the biggest change. Real server-side storage is required — uploaded
  files, extracted text, chunks — for materials to be usable across
  sessions. The charter's rewritten I5 needs to state the actual
  guarantee this design provides instead: no account/login beyond an
  opaque workspace identifier, explicit student visibility into
  everything stored (`list_workspace_materials`), immediate and complete
  deletion on request (`remove_material`, `delete_workspace`), and a
  stated default retention period. "No server-side data" becomes
  "no server-side data without explicit student visibility and control."
- **I6** (non-evaluative Socratic guardrail, never gives direct
  answers/hidden tests before a repair attempt): stays scoped to the
  code-repair coaching tools exactly as today. The charter needs one
  sentence making explicit that this invariant does not apply to
  `answer_from_materials` — that tool's entire purpose is to enable a
  direct, cited answer. The two capabilities need to be clearly
  distinguishable to anyone reading the charter, so nobody mistakes I6's
  scope as covering the whole product.
- **I4, I7, I8**: unaffected. I4 (Canvas gating) is untouched — this
  design still routes zero content through a real Canvas connection; I7's
  guardrail-suite-extension rule and I8's signed-evidence-record rule
  apply only to the code-repair loop and aren't relevant to a tool that
  was never claiming to produce verified evidence.

## Non-goals

- No embedding-model-based semantic search (see "Retrieval method" below)
  — keyword/BM25-style only, for this version.
- No web UI — ingestion happens via native chat file-attachment inside
  ChatGPT/Codex, per explicit product decision during brainstorming.
- No automatic Canvas sync of any kind — this is entirely student-
  initiated upload, independent of (and not a resolution to) the still-
  blocked institutional Canvas/LTI path (R5).
- No grading, scoring, or mastery estimation of any kind for this
  capability — it answers questions, nothing else.
- Does not touch the existing code-repair MCP tools
  (`start_challenge`, `submit_prediction`, `submit_diagnosis`,
  `submit_repair`, `list_course_topics`) or their guardrail suite in
  `test_guardrails.py`. This is new, additive tool surface.

## Blocking unknown (feasibility spike required before implementation)

**How does a ChatGPT App or Codex plugin actually deliver an attached
file's content to an MCP tool call?** Candidates, in descending order of
likelihood based on the MCP spec's resource/blob primitives, but none
verified against a real ChatGPT or Codex session (this repo's existing
Phase 1 spike 2, `docs/MCP_SERVER.md`, already documents that neither a
real ChatGPT workspace connection nor a Codex CLI install exists to test
against):

1. The host model reads the attachment itself and passes extracted plain
   text as a tool argument (no binary handling needed on our side, but we
   lose page-boundary fidelity for citations unless the host also passes
   structure).
2. The host passes a fetchable resource URI (per MCP's resource
   primitives) that our tool then retrieves.
3. The host passes raw file bytes (base64) directly as a tool argument.

This determines `add_course_material`'s actual parameter shape and
whether we need our own PDF/document parsing code at all. **Do not start
implementing `add_course_material` until this is resolved** — treat it
exactly like the sandbox and MCP-connectivity spikes in
`docs/IMPLEMENTATION_PLAN.md` §6: a blocking feasibility question, logged
as unresolved-and-gated if it can't be answered in time, not silently
assumed. The rest of this design (chunking, storage, retrieval, data
boundary enforcement, deletion) is independent of this unknown and can be
built and tested against synthetic plain-text input regardless of how
real ingestion eventually works.

## Architecture

```
Student (in a ChatGPT/Codex conversation, attaches a file)
        |
        v
add_course_material(workspace_id, <content — shape TBD by the spike>, filename)
        |
        v
  extract_text()  -- format-specific extraction (plain text first;
        |            PDF/docx support is a later, separate task)
        v
  chunk_with_provenance()  -- splits into chunks, each tagged with
        |                     {filename, page_or_section}
        v
  classify_for_data_boundary()  -- heuristic reject/flag against the I1
        |                          allow/exclude list (see below)
        v
  store_chunks(workspace_id, chunks)  -- server-side, per-workspace
        |
        v
  response narrates: filename, page/chunk count, any flagged/rejected
  content and why -- host model relays this as the "pre-index review"
  step from the research doc's UX pattern


list_workspace_materials(workspace_id) -> [{filename, chunk_count, added_at}]
remove_material(workspace_id, filename) -> deletes that file's chunks
delete_workspace(workspace_id) -> deletes everything for that workspace


answer_from_materials(workspace_id, question)
        |
        v
  keyword_search(question, workspace_id)  -- BM25-style ranking over
        |                                    stored chunks, same
        |                                    transparent-heuristic idiom
        |                                    as topic_matching.py
        v
  returns: [{excerpt, filename, page_or_section, score}, ...]
  (top-k, e.g. k=5) -- host model synthesizes the actual answer from
  these excerpts and must cite filename/page per excerpt used
```

### Data boundary enforcement (`classify_for_data_boundary`)

A transparent, documented heuristic — explicitly not a guarantee, matching
this project's existing honesty about heuristic limits:

- **Reject outright** (never stored): content matching structural patterns
  of a graded submission or exam (e.g., a file explicitly named/labeled
  as a submission, an answer key, or a completed quiz attempt with
  scores/grades visible in the text).
- **Flag for explicit confirmation** (stored only if the student
  confirms after seeing the flag): content containing patterns common to
  assignment/exam *questions* mixed with the student's own work, or
  anything that looks like it might contain another student's name/work
  (a possible discussion-post or group-work paste).
- **Allow**: syllabus text, module/topic lists, instructor-provided
  slides/readings, the student's own notes.

This mirrors the include/exclude table from the research findings doc.
The heuristic is pattern/keyword-based (regex and structural checks, e.g.
looking for "Grade:", "Score:", "Submitted by", percentage patterns near
a filename containing "quiz" or "exam") — no ML classifier, consistent
with I3 (no inference cost) and this project's existing preference for
simple, auditable heuristics over model-based judgment calls.

### Retrieval method

Keyword/BM25-style ranking (e.g. a standard BM25 implementation over
tokenized chunks — no external service, pure Python, same "deterministic,
documented heuristic, not semantic understanding" framing as
`topic_matching.py`). No embedding model, no vector database, no
third-party API — keeps I3 intact and avoids a new infrastructure
dependency for this version. A future revision could add semantic search
as an explicitly separate, costed decision, not bundled into this one.

### Contracts (new, in `apps/api/app/domain/contracts.py` or a new
`apps/api/app/domain/workspace_contracts.py` if that file is judged too
large by then — this is an implementation-time file-structure call, not
fixed here)

```python
class MaterialChunk(BaseModel):
    workspace_id: str
    filename: str
    location: str  # e.g. "page 3" or "section 2.1" — format depends on source
    text: str

class IngestResult(BaseModel):
    filename: str
    chunk_count: int
    status: Literal["stored", "flagged", "rejected"]
    reason: str | None  # populated for flagged/rejected

class MaterialSummary(BaseModel):
    filename: str
    chunk_count: int
    added_at: str  # ISO timestamp

class RetrievedExcerpt(BaseModel):
    excerpt: str
    filename: str
    location: str
    score: float

class AnswerContext(BaseModel):
    workspace_id: str
    question: str
    excerpts: list[RetrievedExcerpt]
```

(Exact field set to be finalized at implementation time against whatever
the ingestion spike determines about `add_course_material`'s real input
shape — the shapes above are illustrative of the data model, not a final
contract.)

## Error handling

- `add_course_material` with content that fully fails extraction (e.g.
  corrupt file): returns an error, not a silently-empty ingest.
- `answer_from_materials` on a workspace with zero stored chunks: returns
  an explicit "no materials in this workspace yet" result, not an empty
  excerpt list that could be mistaken for "no relevant match found."
  Distinguishing these two empty-result cases matters — the host model
  needs to tell the student different things in each case.
- `remove_material`/`delete_workspace` on an unknown workspace or
  filename: error, not silent no-op — the student's mental model
  ("I deleted this") must match what actually happened.

## Testing

- Deterministic unit tests for `extract_text`, `chunk_with_provenance`,
  `classify_for_data_boundary` (reject/flag/allow cases, including
  adversarial filenames and content), and `keyword_search`'s ranking —
  all independent of the ingestion-shape spike, buildable and testable
  against synthetic plain-text input immediately.
- An I6/I7-*style* guardrail suite adapted for this capability's actual
  guarantee (not I6's "never answer directly" — the opposite guarantee
  applies here): every returned excerpt must be traceable to real stored
  content (no fabricated citations), and `answer_from_materials` must
  never return content from a different workspace than the one requested
  (a real cross-student data-leak risk this project's culture would
  insist on testing explicitly, analogous to how `test_guardrails.py`
  sweeps for hidden-test leakage today).
- A dedicated data-boundary test suite: real (synthetic, not actual
  student) examples of submission-like, exam-like, and roster-like
  content, proving the reject/flag heuristics catch the obvious cases the
  research doc's exclude list names. Documented as best-effort, same
  honesty standard as the rest of this design.

## Open questions

- The ingestion-shape spike (see "Blocking unknown") — must be resolved
  or explicitly logged as "unresolved, gated" before `add_course_material`
  is implemented, per this project's existing Definition-of-Done standard
  for feasibility spikes.
- Retention default (e.g. "delete after 90 days of workspace inactivity")
  — a specific number needs picking at implementation time; this design
  establishes that a default must exist and be stated to the student, not
  what the number is.
- PDF/docx extraction is out of scope for the first implementation slice
  (plain-text and pasted content only); which document formats to support
  first is a follow-up decision once the ingestion-shape spike resolves.
