# Task handoff: Hackathon replan and implementation plan

## Goal

Reconcile the product's drifted docs/code (standalone web app vs. unfinished Codex
plugin, neither accessible, neither AI-powered) into one coherent plan for the
UofU "AI in Education" hackathon (Track 2, "Learn"), then produce a detailed,
team-reviewable implementation plan and documentation package.

## Changed files

- `docs/VISION.md` — new. Product framing: problem, audience, core loop, why it
  wins, scope tiers, known limits, explicitly out of scope, naming note.
- `docs/PROJECT_CHARTER.md` — rewritten around the numbered invariants I1-I7 and
  the new MCP + ChatGPT App + Codex plugin + Canvas architecture.
- `docs/IMPLEMENTATION_PLAN.md` — new. Executive summary, invariants, judging-
  criteria alignment, architecture, agentic-engineering practices (anti-slop
  discipline), a 9-phase implementation plan with Definitions of Done, a
  consolidated risk register, open questions for the team, and a sign-off table.
- `AGENTS.md` — references the new docs; invariants I1-I7 spelled out; working
  agreement now requires citing a phase+task ID from `docs/IMPLEMENTATION_PLAN.md`.
- `.agents/skills/evidence-engine-delivery/SKILL.md` — read order and required
  outcome framing updated to reference the new docs.
- `memory/INDEX.md` — fixed the stale "current handoff" pointer (was 11 records
  behind) and added a living current-state summary block.
- `scripts/memory_check.py` — now asserts the INDEX pointer names the actual
  latest episodic file, so this specific staleness can't recur silently.
- `.github/pull_request_template.md` — new. Anti-slop checklist from
  `docs/IMPLEMENTATION_PLAN.md` §5.6 wired into every PR.

## Validation evidence

`python scripts/memory_check.py` run after this record and the INDEX update
landed together (the new staleness check requires this file to exist and be
named in INDEX.md's current-handoff pointer before it passes).

## Constraints and risks

This handoff records planning/documentation output only — no product code
(MCP server, mutation pipeline, Canvas client, ChatGPT App, Codex plugin
extension) has been written yet. See `docs/IMPLEMENTATION_PLAN.md` §6-8 for
what Phase 0 covers vs. what's still open, and §8 specifically for open
questions that need real team input (Canvas access ownership, timeline
sanity-check, instructor pilot).

## Blocker

None for Phase 0. Phase 3 (Canvas integration) has a named risk (R5) around
institutional developer-key access with no owner yet — see
`docs/IMPLEMENTATION_PLAN.md` §8, item 1.

## Owner

Shared team; see `docs/IMPLEMENTATION_PLAN.md` §9 for the sign-off roles still
needing names.

## Next action

Team reviews and signs off on `docs/IMPLEMENTATION_PLAN.md` (§8 open questions,
§9 sign-off table), then begins Phase 1 (deterministic mutation pipeline +
knowledge tracing) per the plan.
