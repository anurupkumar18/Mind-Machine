# Deep Research Prompt: Canvas LMS Access Workarounds

Paste everything below into a ChatGPT deep-research session.

---

## Context

I'm building a student-facing AI study tool that grounds its answers in a
student's actual course material (syllabus, modules, assignments) pulled
from Canvas LMS. My institution (University of Utah) blocks the two normal
paths to a real Canvas API credential:

1. Self-service personal access tokens are disabled for student accounts —
   Canvas shows "contact your admin" instead of a token-generation button.
2. OAuth2 developer-key registration is admin-only per Canvas's own docs
   ("For Canvas Cloud, developer keys are issued by the admin of the
   institution").

Canvas's developer docs also state that asking a user to manually generate
a token and hand it to a third-party app is itself a violation of Canvas's
API policy — so scraping a logged-in student session or building a
browser-automation agent that logs in as the student is very likely the
same violation in a different shape, not a real workaround.

Current fallback: a fixture-backed mock Canvas layer for demo purposes,
while we pursue an actual UofU Canvas admin contact for a real
institutional integration approval.

## What I need researched

1. **Legitimate technical workarounds short of full admin approval** —
   e.g., LTI 1.3 as a lower-friction path than a personal API token,
   Canvas's "Free for Teacher" or open sandbox instances (status as of
   2026), Common Cartridge / QTI export as a student- or instructor-
   initiated manual data path, any Canvas API scopes an instructor
   (not IT admin) can self-approve.
2. **Precedent at other schools.** Which universities' CS/ed-tech student
   projects or research labs got a real Canvas integration approved, and
   how (contact chain, what they asked for, how long it took, what scope
   they were granted). Look for hackathon projects, campus AI-tutor
   pilots, and ed-tech startups that started as a student project.
3. **Research papers / prior art** on LMS-grounded AI tutoring or
   RAG-over-coursework systems — how they sourced their data (real API
   access, IRB-approved pilot, synthetic/mock data, browser export by the
   student themselves under explicit consent). Include HCI/ed-tech venues
   (LAK, L@S, EDM, CHI) and any Instructure/Canvas developer-community
   writeups.
4. **The consent-first alternative**: instead of an institutional
   integration, a design where the *student* exports their own data
   (Canvas has a personal data-export feature, and instructors can
   download course content they own) and uploads it to the tool directly —
   no token, no scraping, no institutional approval needed. What's the
   actual UX/legal shape other tools use for this pattern, and where does
   it break down at scale?
5. **If we do get institutional approval**: what's the most ambitious,
   "revolutionary" version of this worth designing toward now — e.g. LTI
   Advantage deep integration with Deep Linking + Names/Roles/Assignment
   & Grade Services, becoming a listed Canvas App, multi-institution
   OAuth so it's not tied to one school. What do the best-in-class
   examples (e.g. established ed-tech LTI tools) actually implement?

## Constraints on the answer

- Flag anything that would violate Canvas's API Policy or a student's
  institutional Terms of Use — I want the compliant workaround list
  clearly separated from anything legally/ethically risky, not blended.
- Prefer concrete sources (docs, papers, GitHub repos, case studies) with
  links over general advice.
- Keep the "if we get approval" section separate from the "workaround
  right now" section — I need both, but they're different timelines.

## Output format

A markdown report with these sections: (1) Compliant workarounds
available now, ranked by effort vs. value; (2) Precedent — other schools
and how they got access; (3) Research papers and prior art; (4)
Consent-first / student-export design pattern, worked out in more detail;
(5) The ambitious version to build toward once approved.
