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
    ):
        assert boundary in skill, boundary


if __name__ == "__main__":
    main()
