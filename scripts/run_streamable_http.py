"""Run Evidence Engine's MCP server over streamable-http, the transport a
ChatGPT App actually connects to (see docs/MCP_SERVER.md). The default
`app.mcp_server.main()` only runs stdio (what Codex CLI uses) -- this is
a standalone dev launcher for the other transport, not a change to the
production entry point.

Run via apps/api's own uv-managed environment:

    cd apps/api && uv run python3 ../../scripts/run_streamable_http.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "api"))

from app.mcp_server import mcp  # noqa: E402 -- must follow the sys.path fix above
from mcp.server.transport_security import TransportSecuritySettings  # noqa: E402

PORT = 8765

if __name__ == "__main__":
    # DNS-rebinding protection is on by default and only allows localhost
    # Host headers -- correct for a real deployment, but it rejects every
    # request that arrives via a tunnel's public hostname. Disabled here
    # only because this is a throwaway local dev tunnel being torn down
    # right after testing, never a real deployment's posture.
    mcp.run(
        transport="streamable-http",
        port=PORT,
        transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
    )
