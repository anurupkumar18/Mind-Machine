# MCP server

## Status

Phase 1 spike 2 (`docs/IMPLEMENTATION_PLAN.md` §6): prove one real MCP tool
can be invoked from the transports Codex and ChatGPT actually use.

**2026-08-30 update — the Codex CLI half is now actually verified, not
just engineering-complete.** A real, personally-authenticated Codex CLI
(a ChatGPT-account login already present on the dev machine, not a UofU
institutional workspace) was pointed at this server over real stdio and
successfully called `list_course_topics`, getting back the real fixture
response — the first time this repo has proven Codex-side connectivity
against a real client rather than only against `mcp.shared.memory`'s
in-memory test harness. See "Connecting Codex CLI" below for the exact
commands. **This does not resolve R11** (§9) — that's specifically about
installing this inside UofU's shared ChatGPT Edu/Codex *workspace* for
distribution to arbitrary students, which still needs institutional
approval and is unrelated to whether a personal Codex CLI can connect.

`apps/api/app/mcp_server.py` now exposes 10 tools across two capabilities:
the original code-repair workflow (`list_course_topics`, `start_challenge`,
`submit_prediction`, `submit_diagnosis`, `submit_repair`, all backed by
real domain logic, not stubs) and the student study workspace
(`add_course_material`, `list_workspace_materials`, `remove_material`,
`delete_workspace`, `answer_from_materials` — see
`docs/STUDY_WORKSPACE.md`).

## What's verified

- `apps/api/tests/test_mcp_server.py` drives the server through the real
  MCP protocol over in-memory streams (`mcp.shared.memory`): tool
  discovery, a successful call returning fixture-grounded data, and an
  unknown-challenge call reported as a tool error rather than a crash.
- Manually verified end-to-end over both transports a real client would use:
  - **stdio** (subprocess) — the transport Codex CLI's MCP client uses.
  - **streamable-http** — the transport a hosted ChatGPT App connects to.

## Running it locally

```bash
cd apps/api
uv run python3 -m app.mcp_server            # stdio transport (default)
```

For streamable-http (needed for a ChatGPT App, which connects over HTTPS,
not stdio):

```python
from app.mcp_server import mcp
mcp.run(transport="streamable-http", port=8765)  # serves POST /mcp
```

## Connecting Codex CLI (verified working, 2026-08-30)

Install Codex CLI (`npm install -g @openai/codex`) and confirm it's
authenticated (`codex doctor` — look for `auth is configured`; a personal
ChatGPT-Plus/Codex-enabled account is enough, no UofU workspace needed for
this step). Then register this server:

```bash
codex mcp add evidence-engine -- uv run --directory /absolute/path/to/apps/api python3 -m app.mcp_server
```

Verify with a single non-interactive call (avoids needing an interactive
terminal):

```bash
codex exec --skip-git-repo-check --approve-for-me \
  "You have an MCP tool available named list_course_topics (provided by \
  the evidence-engine MCP server). It takes no arguments. Call it right \
  now as your first action, then stop and report the raw JSON result. \
  Do not read any files first."
```

`--approve-for-me` is needed because MCP tool calls require approval by
default and `codex exec`'s default policy doesn't grant it non-
interactively. This was run for real on 2026-08-30 and returned the
actual `list_course_topics` payload (course name, syllabus body, and the
four mock modules with their topic-match results) — confirmed against a
real Codex client, not simulated.

`codex mcp remove evidence-engine` undoes the registration.

## Connecting a ChatGPT App (needs a public HTTPS endpoint + UofU workspace approval)

ChatGPT Apps connect over streamable-http to a publicly reachable URL, not
localhost. This needs, in order: a hosting decision (see `render.yaml` for
the existing API deploy target), a public HTTPS URL for the `/mcp` route,
and the UofU ChatGPT Edu/Codex workspace admin approval tracked as Phase 1
spike 1 (§9, R11) — none of which exist yet. Until then this leg stays
unverified against a real ChatGPT workspace, same limitation the plan
already names.

## Known limits of this spike

- Codex CLI connectivity is proven with a personal account on one dev
  machine, once, non-interactively. It hasn't been tried across multiple
  machines, an interactive session, or with a student's own account.
- No auth on the streamable-http transport yet; a real deployment needs the
  OAuth/token verification the `mcp` SDK supports before it's public.
- Proves protocol-level connectivity, not institutional access. Spikes 1
  and 4 in `docs/IMPLEMENTATION_PLAN.md` §6 are still open and still need a
  named human owner — a working personal Codex CLI connection is a real,
  useful data point for R11, not a substitute for it.
- The still-unverified leg is specifically: a real ChatGPT App (streamable-
  http, public HTTPS) and Codex/ChatGPT running inside UofU's actual
  institutional workspace.
