---
name: evidence-engine-delivery
description: Build, review, or extend the Evidence Engine using public fixtures, small vertical slices, deterministic verification, compact shared-memory handoffs, and human-reviewed durable decisions. Use for feature work, tests, refactors, demo hardening, or collaboration handoffs in this repository.
---

# Evidence Engine Delivery

1. Read `AGENTS.md`, `memory/INDEX.md`, relevant semantic records, and one episodic handoff.
2. State the bounded outcome, acceptance criteria, affected contract, and public-data implications.
3. Implement one coherent vertical slice. Keep selection, runtime, evidence, interpretation, and visualization separate.
4. Put fixture content in `fixtures/`; execute only allowlisted variants. Do not add persistence, arbitrary code execution, private inputs, or a mastery score.
5. Run the narrowest tests, then `make check` before merge.
6. Add a compact episodic handoff when the next contributor needs new context. Update semantic or long-term memory only in a reviewed PR.
7. Report changed files, validation evidence, limitations, and the next bounded task.

Use `references/evidence-boundaries.md` when a task touches contracts, policy, runtime execution, or interpretation.

