# Task handoff: initial research and drift rules archived

## Goal

Preserve early product and Canvas research as context and inspiration for teammates
without allowing historical ideas, improvised code, or stale plans to masquerade as
the current implementation or desired future product.

## Inputs

- Two pasted text exports supplied by the product owner: an early Learning Evidence
  Engine handoff and an August 29, 2026 Canvas access/roadmap investigation.
- Three original ChatGPT share URLs, preserved in the research archive. The pasted
  exports did not map individual text sections to individual URLs.

## Changed files

- `docs/research/INITIAL_RESEARCH_AND_INSPIRATION.md` — new synthesis of reusable
  ideas, course-context and LTI patterns, open-source/prior-art leads, expansion
  ideas, explicit discrepancies, fresh-review questions, and a promotion rule.
- `AGENTS.md` — new source-of-truth and drift rule for human and AI contributors.
- `README.md` — new repository interpretation guide and research link.
- `docs/VISION.md`, `docs/IMPLEMENTATION_PLAN.md`, `docs/CANVAS_INTEGRATION.md`,
  `docs/STUDY_WORKSPACE.md`, `docs/PROJECT_CHARTER.md`, and
  `docs/TEAM_PRODUCT_DIRECTION.md` — status banners or links distinguishing current
  behavior, current safeguards, future direction, and historical research.
- `docs/DISCORD_TLDR.md` — added a link to the research archive outside the
  copy-ready post.
- `memory/INDEX.md` — summarized the archive and advanced the handoff pointer.

## Reusable ideas preserved

- learner commitment followed by observable results and structured evidence;
- models assisting with selection and coaching without becoming the correctness
  authority;
- reusable three-level Socratic diagnostic runbooks;
- episodic, semantic, and procedural memory separation;
- context, experience, evidence, and infrastructure as distinct layers;
- one high-quality deterministic vertical slice before broad integration work;
- consent-first, cited course-source workspaces and narrow institution-sponsored
  pilot framing; and
- open-source and prior-art leads that require current license, security, evidence,
  accessibility, and architecture review.

## Discrepancies made explicit

- Historical use of real student code and assignment constraints conflicts with the
  current curated/generated-practice boundary.
- Historical assignment and rubric upload ideas conflict with invariant I1.
- `python_execute_diagnostics` and `python_ast_analyzer` are stale proposed tool
  names, not the current MCP surface.
- The Canvas Free-for-Teacher status differs between research snapshots and must be
  freshly verified before reliance.
- LTI remains a candidate, not the selected institutional architecture.
- Automatic enrollment provisioning, browser-extension access, durable workspace
  storage, semantic retrieval, and authorization are not implemented or approved.
- Existing code and passing tests describe current behavior only; they do not make
  an experiment part of the desired future product.

## Validation evidence

- All local links in the 12 research-related Markdown files resolve, and all three
  original ChatGPT share URLs are preserved exactly.
- A current-source search confirmed that `python_execute_diagnostics` and
  `python_ast_analyzer` are not present in `apps/`, `plugins/`, or `scripts/`, so
  the archive labels them as stale historical names.
- `git diff --check` passed.
- `make check` passed: memory validation, Python/Web lint, strict type checks,
  158 API tests, 5 web tests, and the API smoke test.

## Blocker

None for preserving the research. Any idea promoted into product or implementation
work requires a fresh decision and relevant technical/institutional evidence.

## Owner

Evidence Engine team. Each future discovery item needs a named owner before it
moves from historical inspiration into active work.

## Next action

Use the archive during the next product review to identify one idea worth current
discovery, one stale code path worth removal, and one disputed factual assumption
that needs primary-source verification.
