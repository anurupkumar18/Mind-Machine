"""Build a local, read-only foundation snapshot for a Codex feature session.

This module deliberately reads source text through the bundled mapper only. It
does not inspect git state, execute project commands, edit files, call a
network service, or persist learner data.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
if str(SCRIPT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIRECTORY))

from map_workspace import map_workspace


GUIDANCE_MODES = {
    "observe": {"read": True, "propose": False, "edit": False, "command": False, "explain": True},
    "guide": {"read": True, "propose": True, "edit": False, "command": False, "explain": True},
    "pair": {"read": True, "propose": True, "edit": False, "command": False, "explain": True},
    "delegate": {"read": True, "propose": True, "edit": False, "command": False, "explain": True},
}

APPROVALS = {
    "read": {"status": "available", "requirement": "workspace consent"},
    "write": {"status": "planned", "requirement": "write approval with affected-path diff preview"},
    "command": {"status": "planned", "requirement": "command approval with exact command preview"},
    "network": {"status": "planned", "requirement": "network approval with destination and payload-category preview"},
    "sync": {"status": "unavailable", "requirement": "encrypted archive and retention preview"},
}

SUPPORTED_ADAPTERS = {
    "typescript": "source-map foundation",
    "javascript": "source-map foundation",
    "python": "source-map foundation",
    "java": "source-map foundation",
    "kotlin": "source-map foundation",
}


def candidate_call_path(mapped: dict[str, Any]) -> list[dict[str, Any]]:
    entrypoints = set(mapped["entrypoints"])
    for file in mapped["files"]:
        if file["path"] in entrypoints and file["imports"]:
            imported = file["imports"][0]
            return [{"from": file["path"], "import": imported["module"], "line": imported["line"]}]
    return []


def build_snapshot(workspace: Path, task: str, mode: str) -> dict[str, Any]:
    if mode not in GUIDANCE_MODES:
        raise ValueError(f"Unsupported guidance mode: {mode}")
    normalized_task = task.strip()
    if len(normalized_task) < 3:
        raise ValueError("Task must contain at least three characters.")

    mapped = map_workspace(workspace)
    adapters = sorted({file["language"] for file in mapped["files"]})
    adapter_statuses = [{"language": language, "status": SUPPORTED_ADAPTERS[language]} for language in adapters]
    if mapped["unmapped_extensions"]:
        adapter_statuses.append({
            "language": "generic read-only",
            "status": f"unmapped extensions: {', '.join(mapped['unmapped_extensions'])}",
        })
    return {
        "scope": "local read-only workbench foundation",
        "task": normalized_task,
        "guidance_mode": {"name": mode, "capabilities": GUIDANCE_MODES[mode]},
        "context": {
            "entrypoints": mapped["entrypoints"],
            "metadata_files": mapped["metadata_files"],
            "call_path_candidate": candidate_call_path(mapped),
            "files": mapped["files"],
            "unmapped_extensions": mapped["unmapped_extensions"],
            "excluded_sensitive_files": mapped["excluded_sensitive_files"],
            "excluded_symlink_paths": mapped["excluded_symlink_paths"],
            "ignored_non_regular_paths": mapped["ignored_non_regular_paths"],
            "truncated": mapped["truncated"],
        },
        "adapters": adapter_statuses,
        "change": {"status": "not collected", "reason": "Diff collection is unavailable until the planned policy-enforcing MCP action layer exists."},
        "verification": {"status": "not run", "reason": "Tests are unavailable until the planned policy-enforcing MCP action layer exists."},
        "approvals": APPROVALS,
        "next_decision": "Confirm feature scope and choose a mapped path or planning decision.",
        "limitations": list(dict.fromkeys(mapped["limitations"] + [
            "No project code was executed.",
            "No files were changed.",
            "No diff, command output, network data, or archive content was collected.",
        ])),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a local read-only workbench snapshot.")
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--task", required=True)
    parser.add_argument("--mode", choices=sorted(GUIDANCE_MODES), default="guide")
    args = parser.parse_args()
    print(json.dumps(build_snapshot(args.workspace, args.task, args.mode), indent=2))


if __name__ == "__main__":
    main()
