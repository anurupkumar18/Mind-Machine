"""Create a bounded, read-only source map for an authorized local workspace.

The utility reads selected source text and project metadata only. It never
imports, executes, formats, writes, uploads, or persists workspace content.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any


LANGUAGES = {
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".py": "python",
    ".java": "java",
    ".kt": "kotlin",
    ".kts": "kotlin",
}
EXCLUDED_DIRECTORIES = {
    ".git", ".gradle", ".idea", ".mvn", ".next", ".venv", "__pycache__",
    "build", "coverage", "dist", "node_modules", "out", "target", "venv",
}
METADATA_EXCLUDED_DIRECTORIES = EXCLUDED_DIRECTORIES | {"test", "tests"}
MAX_FILE_BYTES = 500_000
MAX_FILES = 200
MAX_TOTAL_BYTES = 2_000_000
MAX_DISCOVERED_FILES = 2_000
MAX_DEPTH = 12
MAX_SYMBOLS_PER_FILE = 50
MAX_IMPORTS_PER_FILE = 50
PRIVATE_FILENAME_PARTS = {"credential", "secret", "private_key"}
SENSITIVE_CONTENT = re.compile(
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----|(?:api[_-]?key|access[_-]?token|secret[_-]?key|password)\s*[:=]\s*[\"'][^\"']{8,}|\b(?:AKIA|ASIA)[A-Z0-9]{16}\b|\bgh[pousr]_[A-Za-z0-9_]{20,}\b",
    re.IGNORECASE,
)
PYTHON_SYMBOL = re.compile(r"^(?:async\s+)?(?:def|class)\s+(?P<name>[A-Za-z_]\w*)", re.MULTILINE)
JS_SYMBOL = re.compile(r"^(?:export\s+)?(?:default\s+)?(?:async\s+)?(?:function|class|const|let)\s+(?P<name>[A-Za-z_$][\w$]*)", re.MULTILINE)
JAVA_SYMBOL = re.compile(
    r"^\s*(?:@\w+(?:\([^)]*\))?\s*)*(?:(?:public|protected|private|abstract|final|static|sealed|non-sealed)\s+)*(?P<kind>class|interface|enum|record)\s+(?P<name>[A-Za-z_]\w*)",
    re.MULTILINE,
)
KOTLIN_SYMBOL = re.compile(
    r"^\s*(?:@\w+(?:\([^)]*\))?\s*)*(?:(?:public|private|internal|protected|open|abstract|data|sealed|enum)\s+)*(?P<kind>class|interface|object|fun)\s+(?P<name>[A-Za-z_]\w*)",
    re.MULTILINE,
)
PYTHON_IMPORT = re.compile(r"^(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))", re.MULTILINE)
JS_IMPORT = re.compile(r"(?:from\s+|require\()[\"']([^\"']+)[\"']", re.MULTILINE)
JVM_IMPORT = re.compile(r"^import\s+([\w.*]+)", re.MULTILINE)


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def is_excluded(relative: Path, excluded_directories: set[str]) -> bool:
    return any(
        part in excluded_directories or part.startswith(".env") or any(marker in part.lower() for marker in PRIVATE_FILENAME_PARTS)
        for part in relative.parts
    )


def contains_sensitive_content(text: str) -> bool:
    return SENSITIVE_CONTENT.search(text) is not None


def symbols_for(text: str, language: str) -> list[dict[str, Any]]:
    matcher = {
        "python": PYTHON_SYMBOL,
        "javascript": JS_SYMBOL,
        "typescript": JS_SYMBOL,
        "java": JAVA_SYMBOL,
        "kotlin": KOTLIN_SYMBOL,
    }[language]
    symbols: list[dict[str, Any]] = []
    for match in matcher.finditer(text):
        if language in {"java", "kotlin"}:
            kind = match.group("kind")
            kind = "function" if kind == "fun" else kind
        else:
            kind = "class" if "class " in match.group(0) else "function"
        symbols.append({"name": match.group("name"), "line": line_number(text, match.start()), "kind": kind})
        if len(symbols) == MAX_SYMBOLS_PER_FILE:
            break
    return symbols


def imports_for(text: str, language: str) -> list[dict[str, Any]]:
    if language == "python":
        matches = [
            {"module": next(value for value in match.groups() if value), "line": line_number(text, match.start())}
            for match in PYTHON_IMPORT.finditer(text)
        ]
    elif language in {"javascript", "typescript"}:
        matches = [
            {"module": match.group(1), "line": line_number(text, match.start())}
            for match in JS_IMPORT.finditer(text)
        ]
    else:
        matches = [
            {"module": match.group(1), "line": line_number(text, match.start())}
            for match in JVM_IMPORT.finditer(text)
        ]
    return sorted(matches, key=lambda item: (item["module"], item["line"]))[:MAX_IMPORTS_PER_FILE]


def entrypoint(path: Path, text: str) -> bool:
    if "tests" in path.parts or "scripts" in path.parts:
        return False
    if path.suffix == ".py":
        return path.name in {"app.py", "main.py"} or "if __name__ == \"__main__\"" in text or "if __name__ == '__main__'" in text
    if path.suffix in {".js", ".jsx", ".ts", ".tsx"}:
        return path.name in {"index.js", "index.ts", "main.js", "main.ts"}
    if path.suffix == ".java":
        return re.search(r"\bstatic\s+void\s+main\s*\(", text) is not None
    if path.suffix in {".kt", ".kts"}:
        return re.search(r"\bfun\s+main\s*\(", text) is not None
    return False


def map_workspace(root: Path) -> dict[str, Any]:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"Workspace must be an existing directory: {root}")

    files: list[dict[str, Any]] = []
    metadata: list[str] = []
    entrypoints: list[str] = []
    languages: set[str] = set()
    unsupported_extensions: set[str] = set()
    excluded_sensitive: list[str] = []
    excluded_symlinks: list[str] = []
    ignored_non_regular: list[str] = []
    total_bytes = 0
    discovered_files = 0
    truncated = False

    stop_scan = False
    for current, directories, filenames in os.walk(root):
        current_path = Path(current)
        relative_directory = current_path.relative_to(root)
        if len(relative_directory.parts) > MAX_DEPTH:
            directories[:] = []
            truncated = True
            continue
        included_directories: list[str] = []
        for directory in sorted(directories):
            relative_child = relative_directory / directory
            if is_excluded(relative_child, EXCLUDED_DIRECTORIES):
                continue
            if (current_path / directory).is_symlink():
                excluded_symlinks.append(relative_child.as_posix())
                continue
            included_directories.append(directory)
        directories[:] = included_directories
        for filename in sorted(filenames):
            discovered_files += 1
            if discovered_files > MAX_DISCOVERED_FILES:
                truncated = True
                stop_scan = True
                break
            path = current_path / filename
            relative = path.relative_to(root)
            if is_excluded(relative, EXCLUDED_DIRECTORIES):
                continue
            if path.is_symlink():
                excluded_symlinks.append(relative.as_posix())
                continue
            if not path.is_file():
                ignored_non_regular.append(relative.as_posix())
                continue
            if filename in {"package.json", "pyproject.toml"} and not is_excluded(relative, METADATA_EXCLUDED_DIRECTORIES):
                metadata.append(relative.as_posix())
                continue
            language = LANGUAGES.get(path.suffix)
            if language is None:
                if path.suffix:
                    unsupported_extensions.add(path.suffix)
                continue
            size = path.stat().st_size
            if size > MAX_FILE_BYTES:
                truncated = True
                continue
            if len(files) == MAX_FILES or total_bytes + size > MAX_TOTAL_BYTES:
                truncated = True
                stop_scan = True
                break
            total_bytes += size
            text = path.read_text(encoding="utf-8", errors="replace")
            if contains_sensitive_content(text):
                excluded_sensitive.append(relative.as_posix())
                continue
            languages.add(language)
            files.append({
                "path": relative.as_posix(),
                "language": language,
                "line_count": text.count("\n") + (1 if text else 0),
                "symbols": symbols_for(text, language),
                "imports": imports_for(text, language),
            })
            if entrypoint(relative, text):
                entrypoints.append(relative.as_posix())
        if stop_scan:
            break

    limitations = [
        "No project code was executed.",
        "No files were changed.",
        "Only JavaScript, TypeScript, Python, Java, and Kotlin source files were mapped.",
    ]
    if excluded_sensitive:
        limitations.append("Files with detected sensitive content were excluded from the returned map.")
    if excluded_symlinks:
        limitations.append("Symbolic links were excluded so the map stays inside the authorized workspace.")
    if ignored_non_regular:
        limitations.append("Non-regular filesystem entries were excluded from the returned map.")
    if truncated:
        limitations.append("Mapping was truncated by deterministic workspace limits.")
    return {
        "scope": "read-only source and metadata map",
        "workspace": root.name,
        "metadata_files": sorted(metadata),
        "detected_languages": sorted(languages),
        "unmapped_extensions": sorted(unsupported_extensions),
        "excluded_sensitive_files": sorted(excluded_sensitive),
        "excluded_symlink_paths": sorted(excluded_symlinks),
        "ignored_non_regular_paths": sorted(ignored_non_regular),
        "truncated": truncated,
        "entrypoints": entrypoints,
        "files": files,
        "limitations": limitations,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a bounded read-only JavaScript, TypeScript, Python, Java, and Kotlin source map.")
    parser.add_argument("workspace", type=Path)
    args = parser.parse_args()
    print(json.dumps(map_workspace(args.workspace), indent=2))


if __name__ == "__main__":
    main()
