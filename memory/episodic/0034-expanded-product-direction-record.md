# Task handoff: expanded product direction recorded

## Goal

Capture the September 2, 2026 team product decision as a durable north-star
reference without changing application behavior, weakening the current charter,
or presenting unresolved institutional ideas as implemented functionality.

## Changed files

- `README.md` — added the concise team direction and links to the canonical recap,
  one-page brief, and Discord summary.
- `docs/TEAM_PRODUCT_DIRECTION.md` — canonical decision record covering the
  problem, north-star journey, class-package concept, stakeholders, possible
  surfaces, current-versus-future state, decisions, non-decisions, and discovery
  risks.
- `docs/VISION.md`, `docs/CANVAS_INTEGRATION.md`, and
  `docs/STUDY_WORKSPACE.md` — added short future-direction sections linked to the
  canonical record.
- `docs/IMPLEMENTATION_PLAN.md` — added an unscheduled discovery item without
  changing the committed phases.
- `docs/PROJECT_CHARTER.md` — added a direction pointer while keeping I1-I8
  authoritative.
- `docs/DISCORD_TLDR.md` — copy-ready team post.
- `docs/EVIDENCE_ENGINE_PROJECT_BRIEF.docx` — completed one-page brief using the
  supplied template.
- `memory/INDEX.md` — added the direction to current state and advanced the handoff.

## Decision and scope

- The product name remains Evidence Engine.
- The agreed north star is an institution-supported learning layer that reduces
  repeated AI setup and combines course-aware, source-grounded support with
  verified practice.
- “NotebookLM-style” is a capability direction, not a selected project or a full
  feature-parity commitment.
- Canvas, a companion browser extension, ChatGPT, Codex, agents, custom GPTs,
  plugins, and MCP servers remain alternative or complementary surfaces pending
  discovery.
- Enrollment-triggered class packages are an institutional goal, not a confirmed
  Canvas capability.
- No code, API, schema, fixture, dependency, or deployment changed. Existing
  safeguards around graded work, consent, hidden tests, and model-authored verdicts
  remain in force.

## Copy-ready Discord recap

> **Quick Evidence Engine recap:** We agreed on a broader north star than the
> current code-practice prototype. The goal is an institution-supported learning
> layer that lets students focus on the class instead of repeatedly figuring out
> which AI tools to use, how to prompt them, and how to rebuild a setup every
> semester.
>
> Long term, enrolling in a class could make a professor- and IT-approved package
> available automatically: course-specific skills, guardrails, hooks, tools,
> plugins, MCP servers, and permitted context. Students could use that through
> ChatGPT, Codex, an agent, or a custom GPT. Canvas or a companion browser extension
> might connect course context, while NotebookLM-style source-grounded Q&A,
> citations, summaries, and study aids help students understand the material.
> Evidence Engine's existing verified-practice loop would then help them prove they
> can apply it through prediction, diagnosis, repair, and tests the AI cannot fake.
>
> This is our **agreed direction, not current functionality or approved
> architecture**. Canvas permissions, automatic enrollment provisioning, browser
> extension policy, privacy, hosting, and the exact open-source components are all
> open questions we need to work through with professors and university IT. For
> now, the repo contains useful prototypes and the existing safety boundaries stay
> in force. Next step: align on this direction, assign discovery owners, and choose
> one realistic pilot path.

## Validation evidence

- All local links in the 10 changed Markdown files resolve; `git diff --check`
  passed.
- The Discord post is 210 words and is reproduced verbatim in this handoff.
- The supplied DOCX template remained unchanged. The completed brief remains one
  US Letter page with the original margins, title rule, heading styles, typography,
  bullets, and numbering; all preserve-only package parts match byte-for-byte and
  no placeholder text remains.
- The completed DOCX was rendered and every page was inspected at 100% zoom. No
  clipping, overlap, broken lists, unexpected wrapping, or spacing defect was
  found.
- `make check` passed: memory validation, Python/Web lint, strict type checks,
  158 API tests, 5 web tests, and the API smoke test.

## Blocker

None for documentation. Institutional permissions and technical feasibility are
open discovery questions, not blockers concealed by this record.

## Owner

Evidence Engine team; future discovery needs named product, professor,
institutional/IT, privacy/security, accessibility, and technical owners.

## Next action

Review the direction as a team, assign discovery owners, and choose one realistic
pilot path before changing the charter or implementing enrollment-linked behavior.
