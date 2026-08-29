# Task handoff: Phase 1 spike 2 — MCP connectivity

## Goal

Prove one real MCP tool can be invoked over the transports Codex and
ChatGPT actually use, before building the full 4-tool workflow surface on
top of it. Phase 1, task 2 (`docs/IMPLEMENTATION_PLAN.md` §6).

## Changed files

- `apps/api/app/mcp_server.py` — one MCP tool, `start_challenge`, backed by
  real domain logic (`app.domain.fixtures`, `app.domain.runtime`), not a
  stub. Deliberately minimal: one fixed challenge, no opaque signed token
  yet (that's Phase 3, §3.2).
- `apps/api/tests/test_mcp_server.py` — 3 tests driving the server through
  the real MCP protocol over in-memory client/server streams
  (`mcp.shared.memory`): tool discovery, a successful call returning
  fixture-grounded data, an unknown-challenge call reported as a tool error
  rather than a crash.
- `apps/api/pyproject.toml` / `uv.lock` — added the `mcp[cli]` SDK
  (installed version: `mcp==2.1.1`, a newer major line than most current
  MCP documentation assumes — `FastMCP` is renamed `MCPServer`, imported
  from `mcp.server.mcpserver`; some client helper signatures differ from
  v1 docs, e.g. `streamable_http_client` yields a 2-tuple here, not 3).
- `docs/MCP_SERVER.md` — new: status, what's verified, how to run it, how
  to connect Codex CLI and a ChatGPT App (both unverified end-to-end here,
  see Blocker), known limits.
- `docs/IMPLEMENTATION_PLAN.md` — R6 status updated.

## Validation evidence

`make check` passes (18 API tests incl. the 3 new MCP tests, both lints,
both typechecks, web tests, smoke). Beyond the automated test (in-memory
streams), manually verified real end-to-end tool calls over both transports
a real client would use:
- **stdio**, via a real subprocess (`uv run python3 -m app.mcp_server`)
  driven by `mcp.client.stdio.stdio_client` — the exact transport Codex
  CLI's MCP client uses.
- **streamable-http**, via `mcp.run(transport="streamable-http")` on
  localhost, driven by `mcp.client.streamable_http.streamable_http_client`
  — the transport a hosted ChatGPT App connects to.
Both returned the same fixture-grounded `start_challenge` payload with no
protocol errors.

## Known limits

- Proves protocol-level connectivity only. It does **not** prove the tool
  was invoked from an actual ChatGPT workspace or an actual Codex CLI
  install — this machine has no Codex CLI installed, and there is no
  public HTTPS endpoint or UofU workspace approval for a real ChatGPT App
  connection. Both remain genuinely open (Phase 1 spikes 1 and 4-adjacent,
  §9 R11).
- One tool, one hardcoded challenge, no auth on the HTTP transport, no
  opaque signed challenge token — all explicitly Phase 3 scope, not this
  spike's.
- The `mcp` SDK installed (2.1.1) is a newer major version than most
  existing MCP tutorials/blog posts describe; anyone extending
  `mcp_server.py` should check the installed package's actual API
  (`python3 -c "import mcp.server.mcpserver as m; help(m.MCPServer)"`)
  rather than trusting v1-era docs, per the "verify APIs before trusting
  them" discipline in `docs/IMPLEMENTATION_PLAN.md` §7.

## Blocker

Institutional access is not resolvable from an engineering session:
whoever picks this up next needs a real Codex CLI install to close the
Codex leg, and a public HTTPS deploy plus UofU ChatGPT Edu/Codex workspace
admin approval to close the ChatGPT leg (§9, R11 — still the
highest-priority unknown in the whole plan, still no named owner).

## Owner

Shared team.

## Next action

1. Whoever has a Codex CLI install: add the `[mcp_servers.evidence-engine]`
   config in `docs/MCP_SERVER.md` and confirm `start_challenge` is callable
   from an actual Codex session — that closes the Codex half of this spike.
2. Whoever can reach a UofU ChatGPT Edu/Codex workspace admin: pursue Phase
   1 spike 1 (§9 R11) in parallel — it's a prerequisite for the ChatGPT half
   regardless of hosting.
3. Engineering-side, either: deploy `mcp_server.py` behind a public HTTPS
   URL (see `render.yaml` for the existing deploy target) as prep, or move
   on to Phase 2/3 work (the property-DSL catalog building on the sandbox
   spike, or the full 4-tool surface) since neither depends on spike 1/4
   resolving first.
