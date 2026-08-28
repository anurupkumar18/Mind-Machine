"""Verify the intentionally narrow V2 preview plugin contract."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "evidence-engine-tutor"


def main() -> None:
    manifest = json.loads((PLUGIN / ".codex-plugin" / "plugin.json").read_text())
    skill = (PLUGIN / "skills" / "codebase-onboarding" / "SKILL.md").read_text()

    assert manifest["name"] == "evidence-engine-tutor"
    assert manifest["skills"] == "./skills/"
    assert "mcpServers" not in manifest
    assert "apps" not in manifest
    assert "read-only" in manifest["description"]
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
    ):
        assert boundary in skill, boundary
    mapper = PLUGIN / "scripts" / "map_workspace.py"
    assert mapper.is_file()
    assert "exec(" not in mapper.read_text()


if __name__ == "__main__":
    main()
