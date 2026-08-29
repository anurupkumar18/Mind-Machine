# Task handoff: Canvas access research — a compliant path exists now, distinct from the blocked LTI/API path

## Goal

Resolve, or at least sharpen, the open question from `episodic/0017`/`0018`
(Canvas institutional access confirmed blocked) by researching whether any
compliant alternative exists short of full admin approval. Research was run
in a parallel conversation against `docs/research/canvas-access-deep-
research-prompt.md`; this entry records the findings and their implication
for this project.

## Changed files

- `docs/research/canvas-access-deep-research-prompt.md` — pre-existing
  (authored in the parallel conversation), the prompt used for the research.
- `docs/research/canvas-access-deep-research-findings.md` — new, the full
  research report.

## Findings (see the findings doc for full detail and sources)

- **Confirms `episodic/0017`/`0018`**: there is no compliant student-only
  API workaround at UofU. LTI 1.3 is the best *institutional-approval*
  path (lower friction than full OAuth developer-key registration), but it
  still requires a Canvas/LTI administrator — not a technical bypass, and
  R5 in `docs/IMPLEMENTATION_PLAN.md` stays open regardless.
- **New, actionable finding**: a genuinely compliant path exists *right
  now*, with no institutional approval needed — a **student-initiated
  upload / "Add course materials" workflow**, not a "Connect Canvas"
  integration. The student uploads syllabus/instructor-provided files/
  their own notes directly; no token, no OAuth, no scraping. This is
  distinct from, and more valuable than, `apps/api/app/domain/canvas_mock.py`
  (`episodic/0028`) — the mock demonstrates the topic-grounding *shape*
  with fictional data; this upload path would ground practice in a
  student's *real* course material, compliantly, today.
- Explicit **non-solutions** confirmed by Canvas's own docs: personal
  access tokens collected from students (violates Canvas's API Policy per
  its own text, already known from `episodic/0017`), session-cookie
  scraping, browser automation impersonating a student login — all
  functionally equivalent violations, not workarounds.
- **Precedent**: UCSD TritonAI/TritonGPT and Instructure's own Project
  Athena are the closest product precedents — both are instructor-
  sponsored, course-scoped, read-only-on-published-material pilots. Georgia
  Tech's AI-Tutor and the CanvasCram thesis are research/architecture
  precedent, not institutional-approval precedent (their credential models
  aren't publicly documented, and CanvasCram's doesn't appear to be a
  compliant multi-user credential model).
- **UofU contact chain**: published entry point is UIT Digital Learning
  Technologies (LTI + ed-tech consultation). Recommended framing: one
  course, one term, instructor-sponsored, LTI 1.3, read-only on
  instructor-selected published materials only, no grades/submissions/
  roster/write access — narrower scope reduces review burden versus asking
  for broad API access.
- **Design pattern for the upload path**: create workspace → upload/paste
  → pre-index review with per-file exclude → narrow consent question →
  answer only from indexed sources with citations → remove-source/delete-
  workspace/download-my-data controls. Explicit include/exclude data
  boundaries (never grades, submissions, peers' posts, roster data,
  copyrighted publisher content without clear permission). Known failure
  modes at scale: no auto-sync, incomplete materials, license restrictions
  on redistribution even of viewable content, accidental upload of private
  data — mitigated by provenance tracking, upload warnings, sensitive-data
  detection, short retention defaults.

## Validation evidence

Not applicable — this is external research, not code. No files under
`apps/` changed; `make check` unaffected.

## Blocker

None for the upload-path option — it needs no institutional approval by
design. The LTI/institutional-approval path (R5) remains blocked exactly as
before; this research sharpens the ask (LTI 1.3, narrow scope, DLT contact)
but doesn't resolve it — still needs a named human owner to actually reach
out, same as `episodic/0018`.

## Owner

Shared team. The upload-path option specifically has no blocker, so it's
buildable by whoever picks it up next without waiting on an institutional
answer.

## Next action

This is a real product-direction decision, not just an engineering task —
next conversation should brainstorm (per `docs/PROJECT_CHARTER.md`'s
invariants, especially I1/I4/I5) whether/how to build the consent-first
upload workflow as real Phase-4-adjacent product work, since unlike the
mock (`episodic/0028`) it would ground practice in a student's actual,
real course material without waiting on institutional approval. Separately,
whoever owns the R5 institutional outreach (`episodic/0018`, still unnamed)
now has a sharper, narrower ask to make (LTI 1.3, one course, one term,
read-only, DLT contact) if that path is still worth pursuing in parallel.
