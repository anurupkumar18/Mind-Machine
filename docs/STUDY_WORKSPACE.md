# Student study workspace

> **Document status:** describes a limited prototype plus an exploratory direction.
> The existing implementation is evidence of current behavior, not proof that its
> storage, retrieval, access model, or tool shape belongs in the future product.
> Historical ideas and conflicts are cataloged in
> [`research/INITIAL_RESEARCH_AND_INSPIRATION.md`](research/INITIAL_RESEARCH_AND_INSPIRATION.md).

## What this is

A second, distinct Evidence Engine capability alongside the code-repair
coaching loop: a student uploads their own real course materials (via
native chat file-attachment in ChatGPT/Codex) and asks questions about
them, getting cited answers. Unlike the coaching loop's non-evaluative
guardrail (I6), this capability is *meant* to answer directly — see
`docs/superpowers/specs/2026-08-29-student-study-workspace-design.md` for
the full design and exactly which charter invariants this capability
required rewriting (I1, I2, I3, I5, I6).

## September 2026 product direction (not implemented)

The team sees this prototype as the first technical slice of a broader,
NotebookLM-style course workspace: source-grounded Q&A with citations, summaries,
study aids, and a path from course material into personalized, verified practice.
The intended student experience is low-setup and available through whichever
institution-supported surface fits the course—ChatGPT, Codex, an agent, a custom
GPT, or another approved client.

The long-term direction also imagines professor- and IT-approved class packages
that provide the right skills, guardrails, hooks, tools, plugins, and MCP servers
when a student enrolls. No provisioning mechanism, persistence model, file
pipeline, retrieval architecture, or open-source NotebookLM component has been
selected. The current plain-text, in-process, keyword-retrieval implementation and
all limitations below remain unchanged.

See [`TEAM_PRODUCT_DIRECTION.md`](TEAM_PRODUCT_DIRECTION.md) for the canonical
meeting recap and unresolved institutional questions.

## How it works

1. `add_course_material(workspace_id, filename, text)` — ingests text
   into a workspace. A heuristic data-boundary check
   (`app.domain.data_boundary`) rejects content that looks like a graded
   submission or exam key outright, and flags content that looks like an
   exam/quiz file or a discussion post for exclusion — neither is stored.
   Everything else is chunked (`app.domain.chunking`) and stored
   (`app.domain.workspace_store`).
2. `list_workspace_materials` / `remove_material` / `delete_workspace` —
   full student visibility and control over what's stored.
3. `answer_from_materials(workspace_id, question)` — deterministic
   keyword-overlap retrieval (`app.domain.retrieval`, no embeddings, no
   inference cost) returns cited excerpts; the host model (ChatGPT/Codex)
   synthesizes the actual answer from them.

## Known limitations, stated explicitly

- **Storage is in-process, not a database.** Data does not survive a
  process restart. A real persistence layer is future work once this
  capability is validated in use, not a redesign of what's here.
- **Plain text only.** PDF/docx extraction is out of scope for this
  slice; the exact mechanism by which ChatGPT/Codex would deliver a real
  file attachment's content to `add_course_material` is an open,
  unverified feasibility question (see the design doc's "Blocking
  unknown" section) — this implementation ships with the most-likely
  best-guess shape (already-extracted plain text as a string argument),
  matching this project's existing practice of shipping a spike's
  engineering half before its institutional/connectivity half is
  confirmed (`docs/MCP_SERVER.md`).
- **No "confirm anyway" override for flagged content.** If content is
  flagged (e.g. a filename containing "exam"), it is simply not stored —
  the student must remove whatever triggered the flag and re-upload.
  Adding an explicit confirm-and-store-anyway flow is a stated follow-up,
  not part of this slice.
- **The data-boundary heuristic is best-effort, not a guarantee** —
  pattern/keyword-based, the same honesty standard this project applies
  to its other heuristics (`app.domain.topic_matching`, the
  practice-selection heuristic in `docs/PROJECT_CHARTER.md`).
- **Retrieval is keyword-overlap, not semantic search** — a paraphrased
  question that shares no vocabulary with the source material may not
  retrieve anything relevant. A future revision could add embedding-based
  search as an explicitly separate, costed decision.
- **`workspace_id` has no ownership/access control** — it is an
  unvalidated, caller-supplied string, unlike the cryptographically
  signed `challenge_token` used by the code-repair tools. Anyone who
  obtains a workspace_id has full read and destructive access to it. A
  capability-token-style scheme mirroring `challenge_token.py` is the
  natural fix, deferred as explicit future work (see
  `apps/api/app/domain/workspace_store.py`'s module docstring).

## Relationship to Canvas / `docs/CANVAS_INTEGRATION.md`

Independent of, and not a replacement for, the Canvas integration work.
This capability's upload path needs no institutional approval of any
kind — a student uploads only material they already have access to and
choose to share, distinct from either the mock Canvas topic-grounding
demo or the still-blocked real Canvas/LTI path (R5).
