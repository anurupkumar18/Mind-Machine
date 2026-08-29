# Evidence Engine

Evidence Engine generates fresh, verified algorithmic bugs for a student to diagnose and repair — evidence of success comes from tests Evidence Engine runs itself, in its own sandbox, never a claim self-reported by whichever model is hosting the conversation. It's delivered as a ChatGPT App and a Codex plugin, using the ChatGPT/Codex access a University of Utah student can get through their institutional account — no separate Evidence Engine account, no API key, and it never touches a student's real coursework, exams, or grades.

**Start here:**
- [`docs/VISION.md`](docs/VISION.md) — what this is, who it's for, why it wins.
- [`docs/IMPLEMENTATION_PLAN.md`](docs/IMPLEMENTATION_PLAN.md) — the full phased build plan, invariants, risk register, and team sign-off.
- [`docs/PROJECT_CHARTER.md`](docs/PROJECT_CHARTER.md) — the non-negotiable invariants (I1-I8) every change must satisfy.
- [`AGENTS.md`](AGENTS.md) — collaboration rules for anyone (human or agent) working in this repo.

## Status

This repo is mid-rebuild around the plan in `docs/IMPLEMENTATION_PLAN.md` (revision 8 — an external review found the previous design let the host platform self-report verification results instead of Evidence Engine executing them; see `docs/IMPLEMENTATION_PLAN.md` §0). Phase 1's feasibility spikes (UofU workspace admin approval, a real MCP tool invocation, a trusted-sandbox proof-of-concept, and the Canvas institutional-approval question) are the current blocking gate before deeper build-out. The existing `apps/web` + `apps/api` deterministic BFS demo is being repurposed as an internal dev/QA harness rather than the public product surface; `plugins/evidence-engine-tutor` is being extended from a read-only preview into the full Codex plugin client. Local dev for the harness is still `make setup && make dev` (`http://localhost:3000`, API on `http://localhost:8000`); run `make check` before merge, and see `.github/pull_request_template.md` for the required checklist on every PR.
