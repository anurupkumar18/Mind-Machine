# Task handoff: Builder non-evaluation fix

## Goal

Correct Builder-mode language after manual testing showed it calling a learner
"right" and asserting deterministic runtime behavior from a static map.

## Changed files

- `plugins/evidence-engine-tutor/skills/codebase-onboarding/SKILL.md` — accepts
  lowercase mode choices and prohibits correctness, runtime, and fixture claims
  in every map-practice response; Builder now uses a fixed neutral follow-up.
- contract check and plugin docs — verify and document the non-evaluative
  boundary.

## Validation evidence

Run plugin contract and manifest checks plus `make check`. Reinstall, start a
new task, consent, choose `builder`, then give any answer. The follow-up must
only restate it as a prediction, cite existing map anchors, and ask for one
next inspection.

## Constraints and risks

Existing conversations retain prior loaded skill instructions. Test this change
only from a new Codex task after reinstalling the cache-busted plugin.

## Blocker

None.

## Owner

Shared team.

## Next action

Await a new-task Builder rehearsal before changing the next learning flow.
