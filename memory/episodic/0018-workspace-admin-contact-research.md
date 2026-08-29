# Task handoff: Phase 1 spike 1 — UofU workspace admin contact (research done, outreach not sent)

## Goal

Confirm whether a UofU ChatGPT Edu/Codex workspace admin can approve
installing a custom App/plugin before the hackathon, and who that contact
is. Phase 1, task 1 (`docs/IMPLEMENTATION_PLAN.md` §6) — the plan's own
highest-priority unknown (R11).

## Changed files

- `docs/IMPLEMENTATION_PLAN.md` — §9 open question 2 and R11's row in the
  risk register updated with the findings below, including the named
  contacts and their emails (kept in the plan doc, not here — see
  `docs/IMPLEMENTATION_PLAN.md` §9 for the actual addresses).

## What was found (all public information, via web search/fetch of
`ai.utah.edu` — no account access, no outreach, no forms submitted)

- **UofU's ChatGPT Edu offering explicitly includes Codex.** Confirmed on
  `ai.utah.edu/tools/chatgpt/index.php` ("What's Included in ChatGPT Edu?"
  lists Codex). This resolves an ambiguity the plan carried implicitly —
  Codex isn't a separate, unaddressed access question, it's part of the
  same institutional offering as ChatGPT Edu.
- **A real review process exists for a custom tool/GPT that isn't already
  approved**: the AI Tool Form (`bit.ly/ai-tools-utah`, referenced from
  `ai.utah.edu/tools/` and `ai.utah.edu/faq.php`). Review involves "IT,
  information security, legal counsel, and other stakeholders as
  necessary." No stated timeline. The FAQ separately confirms this is the
  same path for "a custom GPT or specialized AI application," which is
  what an MCP-backed ChatGPT App / Codex plugin is.
- **Named AI Office Leadership roster** (`ai.utah.edu/about.php`), by
  function — all public university-published contact info, not student
  PII. Full names and emails are kept in `docs/IMPLEMENTATION_PLAN.md` §9,
  not duplicated here since this repo's memory-file check flags any
  institutional email address regardless of whether it's a student's or
  staff's: Chief AI Officer; AI Programs Manager (also the site's listed webmaster
  contact — a reasonable single entry point); five people under
  "Technology, Tools, Infrastructure" (most relevant to this ask);
  Purchasing (relevant since the review process includes procurement);
  Policy and Regulation (relevant since the review process includes legal
  counsel).
- **A separate, institution-independent fallback exists**: OpenAI's
  "Codex for Students" program gives verified US/Canada university
  students $100 in Codex credits on a personal ChatGPT account, unrelated
  to UofU's Enterprise/Edu workspace or any admin approval. Confirmed to
  exist via web search; not tested against this project. This is a real
  candidate for the plan's own named fallback ("personal accounts for the
  demo") if institutional approval doesn't land in time — not a substitute
  for institutional approval itself, since it doesn't grant the ability to
  install a custom App/plugin into a shared institutional workspace.

## What was deliberately not done

No email was sent, no AI Tool Form was submitted, and no account was
created or logged into. Submitting a form or sending outreach on the
team's behalf isn't something an agent should do unprompted — this needs
a real person's name attached to the institutional ask, and requires
explicit go-ahead per-action, not a standing assumption.

## Validation evidence

None applicable — this is institutional research, not code. No files
under `apps/` changed; `make check` unaffected.

## Blocker

Still genuinely open. Identifying who to contact is not the same as
institutional approval existing — that requires someone on the team
actually reaching out (AI Tool Form and/or a direct email to the
Technology/Tools/Infrastructure contacts or Callie Reed) and getting a
real answer, on a timeline that may or may not fit the hackathon.

## Owner

Shared team — still unnamed for the actual outreach action, though the
"who to contact" half of R11 is no longer unknown.

## Next action

A team member should either submit the AI Tool Form
(`bit.ly/ai-tools-utah`) describing this project, or email the AI
Programs Manager and/or the Technology/Tools/Infrastructure contacts
directly (addresses in `docs/IMPLEMENTATION_PLAN.md` §9), asking
specifically: can a custom MCP-based ChatGPT App and
Codex plugin be installed and used within UofU's ChatGPT Edu/Codex
workspace, and what's the realistic timeline for that decision. Whoever
does this should report back what's said so `docs/IMPLEMENTATION_PLAN.md`
§9/R11 can move from "open" to an actual pass/fail/informal-answer outcome,
matching how spike 4 (Canvas) was resolved to "confirmed blocked" rather
than left as a vague unknown.
