## What this PR does

<!-- One or two sentences. Reference the phase + task ID from docs/IMPLEMENTATION_PLAN.md §6, e.g. "Phase 2, Task 2.3". -->

## Anti-slop checklist

- [ ] Matches an explicit task ID from `docs/IMPLEMENTATION_PLAN.md` §6
- [ ] Tests included and passing, covering the task's acceptance criteria specifically (not just "existing tests still pass")
- [ ] No unrelated file changes
- [ ] If a new LLM-reachable tool was added: guardrail test suite extended (invariant I7)
- [ ] If behavior changed: relevant doc updated (`README.md`, `docs/VISION.md`, `docs/MCP_SERVER.md`, `docs/CANVAS_INTEGRATION.md` as applicable)
- [ ] If a new known limitation was discovered: risk register (`docs/IMPLEMENTATION_PLAN.md` §7) updated
- [ ] Episodic memory record added (`memory/episodic/NNNN-*.md`) and `memory/INDEX.md` current-state summary updated
- [ ] `make check` passes locally before push

## Invariants touched

<!-- Does this PR touch any of I1-I7 in docs/PROJECT_CHARTER.md / docs/IMPLEMENTATION_PLAN.md §2? If yes, name which and how it's preserved. A PR touching an invariant needs a second reviewer. -->

## Validation evidence

<!-- What did you run, and what did it show? -->
