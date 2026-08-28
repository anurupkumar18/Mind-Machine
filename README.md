# Evidence Engine

Evidence Engine generates fresh, verified algorithmic bugs for a student to diagnose and repair — evidence of success is always a real executed test, never a model's opinion. It's delivered as a ChatGPT App and a Codex plugin, riding the ChatGPT/Codex Enterprise-Edu seat a University of Utah student already has — no install, no signup, no API key, and it never touches a student's real coursework or grades.

**Start here:**
- [`docs/VISION.md`](docs/VISION.md) — what this is, who it's for, why it wins.
- [`docs/IMPLEMENTATION_PLAN.md`](docs/IMPLEMENTATION_PLAN.md) — the full phased build plan, invariants, risk register, and team sign-off.
- [`docs/PROJECT_CHARTER.md`](docs/PROJECT_CHARTER.md) — the non-negotiable invariants (I1-I7) every change must satisfy.
- [`AGENTS.md`](AGENTS.md) — collaboration rules for anyone (human or agent) working in this repo.

## Status

This repo is mid-rebuild around the plan in `docs/IMPLEMENTATION_PLAN.md`. The existing `apps/web` + `apps/api` deterministic BFS demo is being repurposed as an internal dev/QA harness (see Phase 1-2 of the plan) rather than the public product surface; `plugins/evidence-engine-tutor` is being extended from a read-only preview into the full Codex plugin client (Phase 5). Local dev for the harness is still `make setup && make dev` (`http://localhost:3000`, API on `http://localhost:8000`); run `make check` before merge, and see `.github/pull_request_template.md` for the required checklist on every PR.
