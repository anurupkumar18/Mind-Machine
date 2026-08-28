"""Verify Evidence Engine Tutor's consent and approval boundaries."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "evidence-engine-tutor"


def main() -> None:
    manifest = json.loads((PLUGIN / ".codex-plugin" / "plugin.json").read_text())
    onboarding = (PLUGIN / "skills" / "codebase-onboarding" / "SKILL.md").read_text()
    delivery = (PLUGIN / "skills" / "feature-delivery" / "SKILL.md").read_text()

    assert manifest["name"] == "evidence-engine-tutor"
    assert manifest["skills"] == "./skills/"
    assert "mcpServers" not in manifest
    assert "apps" not in manifest
    assert "local project mapping" in manifest["description"]
    for boundary in (
        "Do not inspect workspace files",
        "run commands",
        "edit files",
        "Do not persist learner information",
        "score, mastery estimate",
        "pass/fail judgment",
        "Reply `yes` to continue",
        "scripts/map_workspace.py",
        "Do not use `rg`, read other",
        "files, run tests",
        "no project code ran, no files changed",
        "do not duplicate a prose line",
        "candidate entry point",
        "Learner-selected map practice",
        "What is happening",
        "not a correctness judgment",
        "Do not approve, reject, rank, or score",
        "ignoring surrounding",
        "whitespace and letter case",
        "Critical non-evaluative rule",
        "Never say or imply that a learner is right, wrong, correct",
        "Never claim runtime behavior, fixture comparison",
        "Do not label, refine, confirm, or reject the prediction",
    ):
        assert boundary in onboarding, boundary
    mapper = PLUGIN / "scripts" / "map_workspace.py"
    assert mapper.is_file()
    mapper_text = mapper.read_text()
    assert "exec(" not in mapper_text
    for prohibited in ("subprocess", "requests", "httpx", "socket", "write_text"):
        assert prohibited not in mapper_text, prohibited
    for prohibited in ("That’s the right", "That is the right", "correctness verdict"):
        assert prohibited not in onboarding

    for boundary in (
        "May I use this open workspace",
        "Observe",
        "Guide",
        "Pair",
        "Delegate",
        "write approval",
        "command approval",
        "network approval",
        "Sync is unavailable in this foundation",
        "not enabled in this foundation",
        "Do not run it in this",
        "Treat “do not run commands” as declining this utility too",
        "Do not assign a score, mastery estimate, or pass/fail result",
        "scripts/workbench_snapshot.py",
    ):
        assert boundary in delivery, boundary

    snapshot = PLUGIN / "scripts" / "workbench_snapshot.py"
    assert snapshot.is_file()
    snapshot_text = snapshot.read_text()
    for prohibited in ("subprocess", "requests", "httpx", "socket", "write_text", "exec("):
        assert prohibited not in snapshot_text, prohibited
    assert '"pair": {"read": True, "propose": True, "edit": False, "command": False' in snapshot_text


if __name__ == "__main__":
    main()
