# Task handoff: teammate- and judge-readable repository overview

## Goal

Replace the root README's dense, outdated status paragraph with an accessible
entry point for teammates joining after a product discussion and for hackathon
judges evaluating the idea, current proof, limitations, and proposed submission
path.

## Changed files

- `README.md` — rewritten around the product problem, two complementary product
  experiences, judge-facing differentiation, an explicit current-state matrix,
  product boundaries, architecture, verified local setup, repository map,
  prioritized submission path, and teammate contribution lanes.
- `memory/INDEX.md` — current handoff pointer advanced to this record.
- `memory/episodic/0033-teammate-and-judge-readme.md` — this handoff.

## Source and scope decisions

- Current-versus-planned claims were reconciled against `docs/VISION.md`,
  `docs/PROJECT_CHARTER.md`, `docs/IMPLEMENTATION_PLAN.md`,
  `docs/MCP_SERVER.md`, `docs/STUDY_WORKSPACE.md`, `memory/INDEX.md`, and the
  current source/manifests.
- The README calls out the mission tension introduced by the study workspace:
  the existing charter predates that capability and needs a team-reviewed
  revision before the capability is product-ready.
- The proposed hackathon path centers one excellent BFS evidence loop and one
  real host integration. Broader challenge content, Canvas, knowledge tracing,
  and an instructor dashboard remain follow-up or deferred work.
- No implementation behavior, deployment, or external account state changed.

## Validation evidence

- All local Markdown links in `README.md` resolve.
- The browser-based MCP tester command was checked against
  `scripts/web_tester.py` and corrected to use port 8791.
- `make check` passed: memory validation, Python/Web lint, strict type checks,
  158 API tests, 5 web tests, and the API smoke test.

## Blocker

None. Team alignment and owner assignment are the next collaborative decisions,
not blockers to using the rewritten README.

## Owner

Shared team; product/vision owner should facilitate the submission-path review.

## Next action

Have the team review the README's proposed submission path and assign owners for
product-contract alignment, the primary host integration, sandbox/auth hardening,
challenge content, institutional access, and the demo/pitch.
