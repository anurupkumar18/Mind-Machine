"""Validate reviewed memory files and build a disposable local search index."""

from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEMORY = ROOT / "memory"
CACHE = ROOT / ".cache" / "memory-index.sqlite"
REQUIRED_HEADINGS = {
    "episodic": ["Goal", "Changed files", "Validation evidence", "Blocker", "Owner", "Next action"],
}
FORBIDDEN_MARKERS = ("@utah.edu", "unid", "student id", "api_key", "password")
# API-key-shaped tokens only (e.g. sk-abc123...), not ordinary hyphenated
# words like "risk-register" -- word boundary before "sk-", then key-shaped
# characters after it.
FORBIDDEN_PATTERNS = (re.compile(r"\bsk-[a-z0-9]"),)


def validate(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    lowered = text.lower()
    errors = [
        f"{path.relative_to(ROOT)} contains a forbidden marker: {marker}"
        for marker in FORBIDDEN_MARKERS
        if marker in lowered
    ]
    errors += [
        f"{path.relative_to(ROOT)} contains a forbidden marker: {pattern.pattern}"
        for pattern in FORBIDDEN_PATTERNS
        if pattern.search(lowered)
    ]
    category = path.parent.name
    for heading in REQUIRED_HEADINGS.get(category, []):
        if f"## {heading}" not in text:
            errors.append(f"{path.relative_to(ROOT)} is missing ## {heading}")
    return errors


def check_current_handoff_pointer() -> list[str]:
    """The INDEX's 'Current handoff' pointer must name the latest episodic file.

    Prevents the exact drift an earlier audit found: the pointer had gone stale
    by 11 records with nothing catching it. 'Latest' is by filename sort, which
    matches the NNNN- numeric prefix convention used under memory/episodic/.
    """
    index_path = MEMORY / "INDEX.md"
    episodic_files = sorted((MEMORY / "episodic").glob("*.md"))
    if not index_path.exists() or not episodic_files:
        return []
    latest = episodic_files[-1].name
    index_text = index_path.read_text(encoding="utf-8")
    if latest not in index_text:
        return [
            f"{index_path.relative_to(ROOT)} 'Current handoff' pointer is stale: "
            f"expected it to reference {latest} (the latest file in memory/episodic/), "
            "but it doesn't. Update the pointer and the current-state summary block."
        ]
    return []


def build_index(files: list[Path]) -> None:
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(CACHE) as connection:
        connection.execute("DROP TABLE IF EXISTS memory_documents")
        connection.execute("CREATE TABLE memory_documents (path TEXT PRIMARY KEY, content TEXT NOT NULL)")
        connection.executemany(
            "INSERT INTO memory_documents(path, content) VALUES (?, ?)",
            [(str(path.relative_to(ROOT)), path.read_text(encoding="utf-8")) for path in files],
        )


def main() -> int:
    files = sorted(MEMORY.rglob("*.md"))
    errors = [error for path in files for error in validate(path)]
    errors.extend(check_current_handoff_pointer())
    if errors:
        print("\n".join(errors))
        return 1
    build_index(files)
    print(f"Validated {len(files)} memory documents and rebuilt {CACHE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

