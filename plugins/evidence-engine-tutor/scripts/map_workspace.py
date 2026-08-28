"""Create a bounded, read-only source map for a local workspace.

This utility reads source text and project metadata only. It never imports,
executes, formats, or writes code in the workspace being mapped.
"""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any


LANGUAGES = {".js": "javascript", ".jsx": "javascript", ".ts": "typescript", ".tsx": "typescript", ".py": "python"}
EXCLUDED_DIRECTORIES = {".git", ".next", ".venv", "__pycache__", "build", "coverage", "dist", "node_modules", "venv"}
METADATA_EXCLUDED_DIRECTORIES = EXCLUDED_DIRECTORIES | {"test", "tests"}
MAX_FILE_BYTES = 500_000
PYTHON_SYMBOL = re.compile(r"^(?:async\s+)?(?:def|class)\s+(?P<name>[A-Za-z_]\w*)", re.MULTILINE)
JS_SYMBOL = re.compile(r"^(?:export\s+)?(?:default\s+)?(?:async\s+)?(?:function|class|const|let)\s+(?P<name>[A-Za-z_$][\w$]*)", re.MULTILINE)
PYTHON_IMPORT = re.compile(r"^(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))", re.MULTILINE)
JS_IMPORT = re.compile(r"(?:from\s+|require\()[\"']([^\"']+)[\"']", re.MULTILINE)


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def source_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if any(part in EXCLUDED_DIRECTORIES or part.startswith(".env") for part in path.relative_to(root).parts):
            continue
        if path.is_file() and path.suffix in LANGUAGES and path.stat().st_size <= MAX_FILE_BYTES:
            yield path


def metadata_files(root: Path) -> list[str]:
    matches: list[str] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in METADATA_EXCLUDED_DIRECTORIES or part.startswith(".env") for part in relative.parts):
            continue
        if path.is_file() and path.name in {"package.json", "pyproject.toml"}:
            matches.append(relative.as_posix())
    return matches


def symbols_for(text: str, language: str) -> list[dict[str, Any]]:
    matcher = PYTHON_SYMBOL if language == "python" else JS_SYMBOL
    return [
        {"name": match.group("name"), "line": line_number(text, match.start()), "kind": "class" if "class " in match.group(0) else "function"}
        for match in matcher.finditer(text)
    ]


def imports_for(text: str, language: str) -> list[dict[str, Any]]:
    if language == "python":
        matches = [
            {"module": next(value for value in match.groups() if value), "line": line_number(text, match.start())}
            for match in PYTHON_IMPORT.finditer(text)
        ]
    else:
        matches = [
            {"module": match.group(1), "line": line_number(text, match.start())}
            for match in JS_IMPORT.finditer(text)
        ]
    return sorted(matches, key=lambda item: (item["module"], item["line"]))


def entrypoint(path: Path, text: str) -> bool:
    if "tests" in path.parts or "scripts" in path.parts:
        return False
    return path.name in {"app.py", "main.py", "index.js", "index.ts", "main.js", "main.ts"} or "if __name__ == \"__main__\"" in text or "if __name__ == '__main__'" in text


def map_workspace(root: Path) -> dict[str, Any]:
    root = root.resolve()
    files: list[dict[str, Any]] = []
    entrypoints: list[str] = []
    languages: set[str] = set()

    for path in source_files(root):
        relative = path.relative_to(root).as_posix()
        language = LANGUAGES[path.suffix]
        text = path.read_text(encoding="utf-8", errors="replace")
        languages.add(language)
        files.append({
            "path": relative,
            "language": language,
            "line_count": text.count("\n") + (1 if text else 0),
            "symbols": symbols_for(text, language),
            "imports": imports_for(text, language),
        })
        if entrypoint(Path(relative), text):
            entrypoints.append(relative)

    return {
        "scope": "read-only source and metadata map",
        "workspace": root.name,
        "metadata_files": metadata_files(root),
        "detected_languages": sorted(languages),
        "entrypoints": entrypoints,
        "files": files,
        "limitations": ["No project code was executed.", "No files were changed.", "Only JavaScript, TypeScript, and Python source files were mapped."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a read-only JavaScript, TypeScript, and Python source map.")
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--output", type=Path, help="Optional path outside the mapped workspace for JSON output.")
    args = parser.parse_args()
    result = json.dumps(map_workspace(args.workspace), indent=2) + "\n"
    if args.output:
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result, end="")


if __name__ == "__main__":
    main()
