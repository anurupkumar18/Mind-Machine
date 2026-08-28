from __future__ import annotations

import importlib.util
import os
import tempfile
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
        self.assertEqual(result["metadata_files"], ["apps/api/pyproject.toml", "apps/web/package.json"])
        self.assertEqual(result["detected_languages"], ["python", "typescript"])
        self.assertEqual(result["unmapped_extensions"], [])
        self.assertIn("src/index.ts", result["entrypoints"])
        self.assertNotIn("worker.py", result["entrypoints"])
        files = {item["path"]: item for item in result["files"]}
        self.assertEqual(files["src/index.ts"]["imports"], [{"module": "./greet", "line": 1}])
        self.assertEqual(files["src/index.ts"]["symbols"][0]["name"], "start")
        self.assertEqual(files["worker.py"]["symbols"][0], {"name": "Worker", "line": 4, "kind": "class"})
        self.assertIn("No project code was executed.", result["limitations"])

    def test_maps_java_and_kotlin_source_with_jvm_imports(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "Main.java").write_text(
                "import example.Service;\npublic class Main { public static void main(String[] args) {} }\n",
                encoding="utf-8",
            )
            (root / "App.kt").write_text("import example.Helper\nfun main() = println(Helper)\n", encoding="utf-8")
            (root / "Service.java").write_text("package example;\nclass Service {}\n", encoding="utf-8")
            (root / "Health.kt").write_text("package example\nfun readinessState() = true\n", encoding="utf-8")

            result = MODULE.map_workspace(root)

        files = {item["path"]: item for item in result["files"]}
        self.assertEqual(result["detected_languages"], ["java", "kotlin"])
        self.assertIn("Main.java", result["entrypoints"])
        self.assertIn("App.kt", result["entrypoints"])
        self.assertEqual(files["Main.java"]["imports"], [{"module": "example.Service", "line": 1}])
        self.assertEqual(files["App.kt"]["imports"], [{"module": "example.Helper", "line": 1}])
        self.assertEqual(files["Service.java"]["symbols"], [{"name": "Service", "line": 2, "kind": "class"}])
        self.assertEqual(files["Health.kt"]["symbols"], [{"name": "readinessState", "line": 2, "kind": "function"}])
        self.assertNotIn("Health.kt", result["entrypoints"])

    def test_excludes_sensitive_content_and_classifies_unmapped_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "safe.ts").write_text("export function safe() {}\n", encoding="utf-8")
            (root / "unsafe.ts").write_text('const api_key = "synthetic-secret-value";\n', encoding="utf-8")
            (root / "Cargo.toml").write_text("[package]\nname = 'fixture'\n", encoding="utf-8")

            result = MODULE.map_workspace(root)

        self.assertEqual([item["path"] for item in result["files"]], ["safe.ts"])
        self.assertEqual(result["excluded_sensitive_files"], ["unsafe.ts"])
        self.assertEqual(result["unmapped_extensions"], [".toml"])
        self.assertIn("Files with detected sensitive content were excluded from the returned map.", result["limitations"])

    def test_does_not_follow_file_symlinks_outside_the_authorized_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, tempfile.TemporaryDirectory() as external_temporary:
            root = Path(temporary)
            external = Path(external_temporary) / "outside.ts"
            external.write_text("export const outside = true;\n", encoding="utf-8")
            external_directory = Path(external_temporary) / "outside-directory"
            external_directory.mkdir()
            (external_directory / "nested.ts").write_text("export const nested = true;\n", encoding="utf-8")
            (root / "inside.ts").write_text("export const inside = true;\n", encoding="utf-8")
            (root / "outside.ts").symlink_to(external)
            (root / "linked").symlink_to(external_directory, target_is_directory=True)

            result = MODULE.map_workspace(root)

        self.assertEqual([item["path"] for item in result["files"]], ["inside.ts"])
        self.assertEqual(result["excluded_symlink_paths"], ["linked", "outside.ts"])
        self.assertIn("Symbolic links were excluded so the map stays inside the authorized workspace.", result["limitations"])

    def test_stops_at_the_deterministic_file_limit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for number in range(MODULE.MAX_FILES + 2):
                (root / f"file_{number:03}.ts").write_text("export const value = 1;\n", encoding="utf-8")

            result = MODULE.map_workspace(root)

        self.assertEqual(len(result["files"]), MODULE.MAX_FILES)
        self.assertTrue(result["truncated"])

    def test_sensitive_files_count_toward_the_total_scan_byte_limit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            prefix = 'const api_key = "synthetic-secret";\n'
            contents = prefix + ("x" * (MODULE.MAX_FILE_BYTES - len(prefix)))
            for number in range(5):
                (root / f"sample_{number}.ts").write_text(contents, encoding="utf-8")

            result = MODULE.map_workspace(root)

        self.assertEqual(result["files"], [])
        self.assertEqual(len(result["excluded_sensitive_files"]), MODULE.MAX_TOTAL_BYTES // MODULE.MAX_FILE_BYTES)
        self.assertTrue(result["truncated"])

    def test_ignores_named_pipes_without_trying_to_read_them(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "inside.ts").write_text("export const inside = true;\n", encoding="utf-8")
            os.mkfifo(root / "stream.ts")

            result = MODULE.map_workspace(root)

        self.assertEqual([item["path"] for item in result["files"]], ["inside.ts"])
        self.assertEqual(result["ignored_non_regular_paths"], ["stream.ts"])
        self.assertIn("Non-regular filesystem entries were excluded from the returned map.", result["limitations"])

    def test_rejects_non_directory_workspace(self) -> None:
        with self.assertRaisesRegex(ValueError, "existing directory"):
            MODULE.map_workspace(ROOT / "tests" / "fixtures" / "sample-workspace" / "src" / "index.ts")


if __name__ == "__main__":
    unittest.main()
