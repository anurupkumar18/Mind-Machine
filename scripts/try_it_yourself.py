"""Interactive REPL for manually trying Evidence Engine's MCP tools.

Launches apps/api/app/mcp_server.py as a real subprocess over the same
stdio transport a real Codex/ChatGPT client would use (see
docs/MCP_SERVER.md) -- not a mock, not pytest's in-memory streams. Lets
a human click through the tool surface by hand: list tools, pick one,
fill in arguments, see the real response.

Run it via apps/api's own uv-managed environment (it depends on the `mcp`
package, which lives there, not anywhere else):

    cd apps/api && uv run python3 ../../scripts/try_it_yourself.py
"""

from __future__ import annotations

import asyncio
import json
import shutil
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "apps" / "api"


def _uv_available() -> bool:
    return shutil.which("uv") is not None


# Parameters expected to hold multi-line content (source code, prose).
# input() only ever reads one line, so pasting multi-line text into it
# spills the remaining lines into whatever's read next -- the main menu
# prompt, in practice, producing a flood of "Not a valid choice." These
# fields collect lines until an explicit EOF marker instead.
_MULTILINE_PARAMS = {"text", "repair_source", "diagnosis"}


def _prompt_multiline() -> str:
    print("    (paste your value; finish with a line containing only EOF)")
    lines: list[str] = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "EOF":
            break
        lines.append(line)
    return "\n".join(lines)


def _prompt_json_value(param_name: str) -> object:
    """Prompt for one tool argument. Accepts JSON (numbers, strings,
    lists) or falls back to a plain string if it doesn't parse as JSON --
    so typing  graph traversal  works without needing quotes, but typing
    ["B", "C"]  also works for list-shaped arguments."""
    if param_name in _MULTILINE_PARAMS:
        raw = _prompt_multiline().strip()
        return raw if raw else None

    raw = input(f"    {param_name} = ").strip()
    if raw == "":
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


async def _run_repl() -> None:
    if not _uv_available():
        print("error: 'uv' not found on PATH -- install it first (see apps/api/pyproject.toml)")
        sys.exit(1)

    server = StdioServerParameters(
        command="uv",
        args=["run", "python3", "-m", "app.mcp_server"],
        cwd=str(API_DIR),
    )

    print(f"Starting Evidence Engine's MCP server from {API_DIR} (stdio transport)...")
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            print(f"Connected. {len(tools)} tools available.\n")

            while True:
                print("Tools:")
                for i, tool in enumerate(tools, start=1):
                    print(f"  {i}. {tool.name} -- {(tool.description or '').strip().splitlines()[0]}")
                print("  q. quit")

                choice = input("\nPick a tool number (or q): ").strip().lower()
                if choice in ("q", "quit", "exit"):
                    break

                try:
                    index = int(choice) - 1
                    tool = tools[index]
                except (ValueError, IndexError):
                    print("Not a valid choice.\n")
                    continue

                schema = tool.input_schema or {}
                properties: dict[str, object] = schema.get("properties", {})  # type: ignore[assignment]
                required = set(schema.get("required", []))  # type: ignore[arg-type]

                print(f"\n{tool.name}({', '.join(properties)})")
                if tool.description:
                    print(f"  {tool.description.strip()}")

                arguments: dict[str, object] = {}
                for param_name in properties:
                    marker = "" if param_name in required else " (optional, press enter to skip)"
                    print(f"  {param_name}{marker}")
                    value = _prompt_json_value(param_name)
                    if value is not None:
                        arguments[param_name] = value

                print(f"\nCalling {tool.name}({arguments!r}) ...")
                try:
                    result = await session.call_tool(tool.name, arguments)
                except Exception as error:  # noqa: BLE001 -- surfacing any client-side error to the user is the point
                    print(f"Client-side error: {error}\n")
                    continue

                if result.is_error:
                    print("-> tool returned an error:")
                    for block in result.content:
                        text = getattr(block, "text", None)
                        if text:
                            print(f"   {text}")
                else:
                    payload_text = result.content[0].text  # type: ignore[union-attr]
                    try:
                        payload = json.loads(payload_text)
                        print("-> " + json.dumps(payload, indent=2))
                    except json.JSONDecodeError:
                        print(f"-> {payload_text}")
                print()

    print("Disconnected.")


def main() -> None:
    try:
        asyncio.run(_run_repl())
    except KeyboardInterrupt:
        print("\nInterrupted.")


if __name__ == "__main__":
    main()
