"""Read only allowlisted public-fixture context; never ingest user repositories."""

from __future__ import annotations

import ast
import json
from pathlib import Path

from app.domain.contracts import ChallengeCandidate, CodeContext, CodeFile, CodeReference

ROOT = Path(__file__).resolve().parents[4]
REGISTRY_PATH = ROOT / "fixtures" / "approved_repositories.json"


def _registry() -> dict[str, dict[str, str]]:
    entries = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return {entry["id"]: entry for entry in entries}


def approved_context(repository_id: str) -> CodeContext:
    entry = _registry().get(repository_id)
    if entry is None:
        raise KeyError(repository_id)
    source_root = ROOT / entry["path"]
    files = [
        CodeFile(
            path=str(path.relative_to(source_root)),
            language="python",
            symbols=[node.name for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))) if isinstance(node, ast.FunctionDef)],
            line_count=len(path.read_text(encoding="utf-8").splitlines()),
        )
        for path in sorted(source_root.rglob("*.py"))
    ]
    return CodeContext(
        repository_id=repository_id,
        source=entry["source"],
        files=files,
        excluded_files=[".env*", "credentials", "binaries", "dependencies", "non-Python files"],
    )


def curated_candidate(context: CodeContext) -> ChallengeCandidate:
    bfs_file = next((file for file in context.files if "bfs" in file.symbols), None)
    if bfs_file is None:
        raise ValueError("The approved fixture has no BFS symbol.")
    return ChallengeCandidate(
        objective_ref="Explain and preserve breadth-first traversal invariants.",
        code_refs=[CodeReference(file=bfs_file.path, start_line=1, end_line=bfs_file.line_count)],
        template_id="TRAVERSAL-INVARIANT-02",
        evidence_plan=["frontier_prediction", "visited_invariant", "mutation_repair"],
        rationale="Static analysis found the allowlisted bfs symbol; the curated traversal template is compatible.",
    )
