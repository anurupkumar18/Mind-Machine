# Task handoff: prove the kernel generalizes — fix a hidden coupling, add a second challenge

## Goal

Before adding more mutation operators or kill-ratio filtering (Phase 2,
R1), verify the kernel built in `episodic/0019`/`0020` actually
generalizes rather than working by coincidence for the one challenge
(`traversal-invariant-02`/`bfs`) it's ever been exercised against. Not a
task from a specific plan line item — a self-directed priority call: a
kernel proven against exactly one example is a weaker claim than the
episodic records up to this point implied.

## What was found

Inspecting `apps/api/app/domain/sandbox.py` before making any change:
`_run_oracle` and the sandboxed runner template both hardcoded a
`(graph, start)` two-positional-argument call —
`entry_point(dict(case["graph"]), case["start"])` — not a generic "call
this function with these arguments." `ChallengeConfig.test_inputs` was
never actually generic; every "challenge" would have had to share bfs's
exact argument names and shapes. This was a real architecture gap, not a
cosmetic one — the module docstring and episodic records described the
registry as if it already generalized.

## Changed files

- `apps/api/app/domain/sandbox.py` — `_run_oracle` and the runner template
  now call the entry point as `entry_point(**case)` /
  `{entry_point}(**case)`, so `test_inputs` entries are just kwargs, not
  bfs-specific keys. Added `copy.deepcopy(case)` before the trusted
  in-process oracle call, defensive against a reference implementation
  mutating its arguments and corrupting the shared `test_inputs` list
  across calls (the sandboxed subprocess side already gets a fresh
  JSON-decoded dict per case, no copy needed there). Registered a second
  challenge, `binary-search-invariant-01`.
- `fixtures/repos/public-search/binary_search.py` — new reference
  implementation. Deliberately different shape from bfs: two
  differently-named/-typed arguments (`sorted_values: list[int]`,
  `target: int`), three comparisons of different kinds (`<=`, `==`, `<`)
  versus bfs's one `not in`.
- `apps/api/tests/test_sandbox_generalization.py` — new. A known-good and
  a known-bad (`low < high` instead of `low <= high`, missing the
  single-remaining-element case) repair for the new challenge, run through
  the unchanged public `execute_repair` API.
- `apps/api/tests/test_mutation.py` — 2 new tests: the mutation operator
  generates 3 mutants for binary_search's three comparisons (not just
  works for bfs's one), and at least one is genuinely killed through the
  real pipeline.
- `docs/IMPLEMENTATION_PLAN.md` — R1 row in the risk register updated.

## Validation evidence

`make check` passes in full: 75 API tests (was 71), both lints, both
typechecks, web tests, smoke. Manually ran all 3 generated binary_search
mutants through `execute_repair` and inspected results directly (not just
the "at least one" test assertion): all 3 killed —
`LtE->Gt`, `Eq->NotEq`, `Lt->GtE`, each producing `status=completed`
with at least one failing property. A small sample (one challenge, one
operator family) but a genuine 3/3, not cherry-picked.

## Known limits / explicit scope decisions

- `binary-search-invariant-01` exists only at the sandbox/mutation/
  properties kernel level, not wired through `app.mcp_server`'s
  `start_challenge` tool — that tool still only knows about
  `traversal-invariant-02` and pulls its `objective`/coaching text from
  `fixtures/challenges/traversal-invariant-02.json`, a file structure this
  task didn't touch or extend. Wiring a second challenge through the MCP
  layer (objective text, coaching cards, diagnostic runbook) is a
  separate, larger task this one deliberately didn't take on.
- Kill ratio (3/3) is a real number from a real run, not a target or a
  claim about mutation testing in general — three mutants is a small
  sample, and comparison-operator replacement is one operator family. R1
  ("kill-ratio tuning still genuinely hard") remains open; this result is
  encouraging, not a resolution.
- The `**case` calling convention assumes every challenge's reference
  implementation and every submitted repair use keyword-compatible
  parameter names matching `test_inputs`' keys exactly. That's an
  implicit contract now, not enforced anywhere (a repair with differently
  named parameters would fail with a Python `TypeError`, surfaced as
  `status: errored` — not silently wrong, but not a clear error message
  either). Worth a follow-up if this becomes a real usability issue once
  challenges are authored by someone other than whoever wrote the kernel.

## Blocker

None — independent of Phase 1's open institutional questions.

## Owner

Shared team.

## Next action

Any of, roughly independent:
1. Wire `binary-search-invariant-01` through `app.mcp_server` (needs
   objective/coaching content, not just the kernel pieces this task
   added) to prove the *entire* stack generalizes, not just the sandbox
   layer.
2. A second mutation-operator family (arithmetic/boundary constants,
   boolean connectives) — comparison-operator replacement is the only one
   that exists.
3. Kill-ratio filtering: decide which generated mutants are useful
   practice content versus equivalent/trivial, now that there's a second
   real data point (3/3 for binary_search, 1/1 for bfs) to reason about.
