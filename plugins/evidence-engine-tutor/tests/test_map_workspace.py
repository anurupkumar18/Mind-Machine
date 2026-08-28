from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("map_workspace", ROOT / "scripts" / "map_workspace.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class WorkspaceMapTests(unittest.TestCase):
    def test_maps_supported_files_without_reading_excluded_directories(self) -> None:
        result = MODULE.map_workspace(ROOT / "tests" / "fixtures" / "sample-workspace")

        self.assertEqual(result["scope"], "read-only source and metadata map")
        self.assertEqual(result["metadata_files"], ["package.json"])
        self.assertEqual(result["detected_languages"], ["python", "typescript"])
        self.assertIn("src/index.ts", result["entrypoints"])
        self.assertNotIn("worker.py", result["entrypoints"])
        files = {item["path"]: item for item in result["files"]}
        self.assertEqual(files["src/index.ts"]["imports"], ["./greet"])
        self.assertEqual(files["src/index.ts"]["symbols"][0]["name"], "start")
        self.assertEqual(files["worker.py"]["symbols"][0], {"name": "Worker", "line": 4, "kind": "class"})
        self.assertIn("No project code was executed.", result["limitations"])


if __name__ == "__main__":
    unittest.main()
