# MCP server

## Status

Phase 1 spike 2 (`docs/IMPLEMENTATION_PLAN.md` §6): prove one real MCP tool
can be invoked from the transports Codex and ChatGPT actually use. Done for
the engineering half; the "from the target ChatGPT workspace and from
Codex" half needs a human with institutional access (§9, R11) — this repo
can't obtain that on its own.

`apps/api/app/mcp_server.py` exposes one tool, `start_challenge`, backed by
real domain logic (`app.domain.fixtures`, `app.domain.runtime`) rather than
a stub response. It is intentionally minimal: one fixed challenge, no
opaque signed challenge token yet (that's Phase 3, §3.2).

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

## Connecting Codex CLI (not yet done — needs a Codex install)

Add to `~/.codex/config.toml`:

```toml
[mcp_servers.evidence-engine]
command = "uv"
args = ["run", "--directory", "/absolute/path/to/apps/api", "python3", "-m", "app.mcp_server"]
```

Then ask Codex to call `start_challenge`. This machine doesn't have the
Codex CLI installed, so this step is unverified here — the stdio-transport
test above proves the server side works; only the Codex client side is
unverified.

## Connecting a ChatGPT App (needs a public HTTPS endpoint + UofU workspace approval)

ChatGPT Apps connect over streamable-http to a publicly reachable URL, not
localhost. This needs, in order: a hosting decision (see `render.yaml` for
the existing API deploy target), a public HTTPS URL for the `/mcp` route,
and the UofU ChatGPT Edu/Codex workspace admin approval tracked as Phase 1
spike 1 (§9, R11) — none of which exist yet. Until then this leg stays
unverified against a real ChatGPT workspace, same limitation the plan
already names.

## Known limits of this spike

- One tool, one hardcoded challenge — the 4-tool workflow surface and
  signed challenge tokens (§3.2) are Phase 3.
- No auth on the streamable-http transport yet; a real deployment needs the
  OAuth/token verification the `mcp` SDK supports before it's public.
- Proves protocol-level connectivity, not institutional access. Spikes 1
  and 4 in `docs/IMPLEMENTATION_PLAN.md` §6 are still open and still need a
  named human owner.
