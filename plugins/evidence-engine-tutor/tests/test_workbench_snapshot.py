from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("workbench_snapshot", ROOT / "scripts" / "workbench_snapshot.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class WorkbenchSnapshotTests(unittest.TestCase):
    def test_returns_context_modes_and_uncollected_action_states(self) -> None:
        snapshot = MODULE.build_snapshot(
            ROOT / "tests" / "fixtures" / "sample-workspace",
            "Add a greeting endpoint",
            "pair",
        )

        self.assertEqual(snapshot["scope"], "local read-only workbench foundation")
        self.assertEqual(snapshot["guidance_mode"]["name"], "pair")
        self.assertFalse(snapshot["guidance_mode"]["capabilities"]["edit"])
        self.assertEqual(snapshot["change"]["status"], "not collected")
        self.assertEqual(snapshot["verification"]["status"], "not run")
        self.assertEqual(snapshot["approvals"]["write"], {"status": "planned", "requirement": "write approval with affected-path diff preview"})
        self.assertEqual(snapshot["approvals"]["sync"]["status"], "unavailable")
        self.assertEqual(snapshot["context"]["call_path_candidate"], [{"from": "src/index.ts", "import": "./greet", "line": 1}])
        self.assertIn("No project code was executed.", snapshot["limitations"])
        self.assertEqual(snapshot["limitations"].count("No project code was executed."), 1)

    def test_reports_generic_read_only_extensions(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            (workspace / "main.rs").write_text("fn main() {}\n", encoding="utf-8")
            snapshot = MODULE.build_snapshot(workspace, "Inspect a Rust project", "guide")

        self.assertEqual(snapshot["context"]["unmapped_extensions"], [".rs"])
        self.assertIn({"language": "generic read-only", "status": "unmapped extensions: .rs"}, snapshot["adapters"])

    def test_rejects_unknown_mode_and_short_task(self) -> None:
        workspace = ROOT / "tests" / "fixtures" / "sample-workspace"
        with self.assertRaisesRegex(ValueError, "Unsupported guidance mode"):
            MODULE.build_snapshot(workspace, "Add endpoint", "silent")
        with self.assertRaisesRegex(ValueError, "at least three characters"):
            MODULE.build_snapshot(workspace, "ok", "guide")
        with self.assertRaisesRegex(ValueError, "existing directory"):
            MODULE.build_snapshot(workspace / "src" / "index.ts", "Valid task", "guide")


if __name__ == "__main__":
    unittest.main()
