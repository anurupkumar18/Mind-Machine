"""Validate reviewed memory files and build a disposable local search index."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEMORY = ROOT / "memory"
CACHE = ROOT / ".cache" / "memory-index.sqlite"
REQUIRED_HEADINGS = {
    "episodic": ["Goal", "Changed files", "Validation evidence", "Blocker", "Owner", "Next action"],
}
FORBIDDEN_MARKERS = ("@utah.edu", "unid", "student id", "api_key", "sk-", "password")


def validate(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors = [
        f"{path.relative_to(ROOT)} contains a forbidden marker: {marker}"
        for marker in FORBIDDEN_MARKERS
        if marker in text.lower()
    ]
    category = path.parent.name
    for heading in REQUIRED_HEADINGS.get(category, []):
        if f"## {heading}" not in text:
            errors.append(f"{path.relative_to(ROOT)} is missing ## {heading}")
    return errors


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
    if errors:
        print("\n".join(errors))
        return 1
    build_index(files)
    print(f"Validated {len(files)} memory documents and rebuilt {CACHE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

