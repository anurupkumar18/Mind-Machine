# Task handoff: ChatGPT App connectivity — real progress, paused mid-verification for the night

## Goal

Extend the same real-connectivity verification just done for Codex CLI
(`episodic/0031`) to the other half of Phase 1 spike 2: a real ChatGPT
client, not just protocol-level testing. Driven by the account holder
asking to "try connecting a ChatGPT App too" right after the Codex
verification, then needing to stop for the night before the human-only
final step.

## Changed files

- `scripts/run_streamable_http.py` — new. Standalone launcher running
  `app.mcp_server`'s existing `mcp` instance over streamable-http (the
  transport a ChatGPT App uses), since `app.mcp_server.main()` only runs
  stdio. Disables the `mcp` SDK's DNS-rebinding Host-header check
  (`TransportSecuritySettings(enable_dns_rebinding_protection=False)`) —
  necessary because a tunnel's public hostname otherwise gets rejected as
  an invalid Host header; explicitly scoped in the script's own comment
  as acceptable only for a throwaway local dev tunnel, not a real
  deployment's posture.
- `docs/MCP_SERVER.md` — "What's verified" and "Connecting a ChatGPT App"
  sections rewritten with the real status and exact resume steps.

## What was actually done (real actions)

1. Installed `cloudflared` (`brew install cloudflared`).
2. Started the server over streamable-http locally; confirmed with `curl`
   against `http://127.0.0.1:8765/mcp` first (HTTP 200) before exposing
   anything publicly.
3. First public-tunnel attempt failed real: `cloudflared tunnel --url
   http://127.0.0.1:8765` produced a real `https://*.trycloudflare.com`
   URL, but a real MCP `initialize` POST to it returned **HTTP 421
   Misdirected Request** — the `mcp` SDK's `TransportSecurityMiddleware`
   rejecting the tunnel's Host header (logged: `WARNING Invalid Host
   header: thermal-astronomy-lady-districts.trycloudflare.com`). A real,
   diagnosed finding, not a guess: read `mcp/server/transport_security.py`
   directly to confirm the exact validation logic before fixing it.
4. Fixed by passing `transport_security=TransportSecuritySettings(
   enable_dns_rebinding_protection=False)` to `mcp.run(...)` in the new
   script. Restarted the local server and the tunnel; the same `curl`
   request against the new tunnel URL then returned a real 200 with the
   server's actual `initialize` response (capabilities, the real
   `instructions` string, `serverInfo: {"name": "evidence-engine", ...}`).
5. Wrote out the exact ChatGPT-side steps (Settings → Connectors →
   Developer mode → "Add custom connector" → paste `<tunnel-url>/mcp`)
   for the account holder to do themselves — adding a connector to a
   ChatGPT account is an account-settings action only the account holder
   can take, not something automatable from here.
6. Account holder asked to stop for the night before doing that manual
   step. Both the local streamable-http server and the `cloudflared`
   tunnel were killed (`pkill -f run_streamable_http.py`, `pkill -f
   "cloudflared tunnel"`) — confirmed via `ps aux` that neither process
   remained running. The tunnel URL from this session
   (`thermal-astronomy-lady-districts.trycloudflare.com`) is now dead;
   restarting both processes will mint a new random URL.

## Validation evidence

Real, not simulated: `make check` unaffected (only new/changed files are
a standalone script and docs — no `apps/api/app` or test changes). The
curl-verified 200 response from the public tunnel is quoted above and in
`docs/MCP_SERVER.md`'s "What's verified" section.

## Known limits / explicit scope decisions

- `enable_dns_rebinding_protection=False` is fine for a five-minute
  throwaway tunnel, explicitly not something to carry into any real
  deployment — a real public deployment needs either a stable, known
  hostname in `allowed_hosts`/`allowed_origins`, or a different auth
  story entirely (the doc's existing "no auth on streamable-http yet"
  known limit already covers this).
- Same personal-account-vs-institutional-workspace distinction as
  `episodic/0031`: this proves the *protocol* works over a public URL,
  it says nothing about UofU's ChatGPT Edu/Codex workspace approval
  (R11) or about a real, non-tunnel public deployment (`render.yaml`
  exists as a hosting option, not yet used).
- The actual "does a real ChatGPT client complete the handshake and call
  a tool" question is **still unanswered** — only the network/protocol
  layer up to a raw `initialize` call was proven tonight. A ChatGPT
  client might still hit something a raw curl call wouldn't (session
  handling, SSE streaming behavior, ChatGPT-side connector validation
  quirks) — don't claim more than what was actually tested.

## Blocker

None technical — purely a "ran out of time for the night" stop, not a
dead end. The next session can restart both processes (new tunnel URL
each time) and pick up exactly at the ChatGPT UI step.

## Owner

Shared team / whoever resumes this session.

## Next action

1. `cd apps/api && uv run python3 ../../scripts/run_streamable_http.py`
2. `cloudflared tunnel --url http://127.0.0.1:8765` (new URL each run)
3. In ChatGPT: Settings → Connectors → Advanced settings → Developer mode
   → Add custom connector → URL = `<new-tunnel-url>/mcp` → no auth
4. New chat, enable the connector, ask ChatGPT to call `list_course_topics`
5. Record the real result (or real failure) in a follow-up episodic entry
   the same way `episodic/0031` did for Codex, and update
   `docs/MCP_SERVER.md`'s "Connecting a ChatGPT App" section from
   "in progress, paused" to either "verified working" or a documented
   real failure with its cause.
6. Kill both background processes again when done
   (`pkill -f run_streamable_http.py`, `pkill -f "cloudflared tunnel"`).
