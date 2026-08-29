"""Minimal trusted-execution proof-of-concept (Phase 1 spike 3, I8).

Executes a student's submitted repair against a fixed challenge's hidden
tests inside an isolated subprocess, then signs the result. This is a
feasibility spike, not the production sandbox: isolation here is
process-level (resource limits, no inherited environment, a static
denylist gate) rather than container/VM-level. That gap is a known limit
of this PoC, not a claim of production-grade isolation.
"""

from __future__ import annotations

import ast
import hashlib
import hmac
import json
import os
import resource
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

from app.domain.contracts import PropertySpec
from app.domain.properties import UnknownPropertyError, evaluate_property

SANDBOX_SECRET = os.getenv("EVIDENCE_ENGINE_SANDBOX_SECRET", "dev-only-sandbox-signing-key")

TEST_SUITE_VERSION = "traversal-invariant-02.v1"
RUNTIME_DIGEST = f"cpython-{sys.version_info.major}.{sys.version_info.minor}"

FIXTURES_ROOT = Path(__file__).resolve().parents[4] / "fixtures"

DISALLOWED_NAMES = {
    "os",
    "sys",
    "subprocess",
    "socket",
    "shutil",
    "importlib",
    "ctypes",
    "requests",
    "urllib",
    "open",
    "eval",
    "exec",
    "__import__",
    "compile",
}

ALLOWED_IMPORT_MODULES = {"collections", "heapq", "itertools", "math", "functools"}

_TIMEOUT_SECONDS = 5
_CPU_SECONDS = 2
_ADDRESS_SPACE_BYTES = 768 * 1024 * 1024

_HIDDEN_TEST_INPUTS: list[dict[str, Any]] = [
    {"graph": {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": ["A"]}, "start": "A"},
    {"graph": {"A": ["B"], "B": ["A"]}, "start": "A"},
    {"graph": {"A": []}, "start": "A"},
]


@dataclass(frozen=True)
class ChallengeConfig:
    entry_point: str
    oracle_path: Path
    test_inputs: list[dict[str, Any]]
    property_spec: PropertySpec


_CHALLENGES: dict[str, ChallengeConfig] = {
    "traversal-invariant-02": ChallengeConfig(
        entry_point="bfs",
        oracle_path=FIXTURES_ROOT / "repos" / "public-graph-traversal" / "bfs.py",
        test_inputs=_HIDDEN_TEST_INPUTS,
        property_spec=PropertySpec(
            function="bfs",
            property="output_equals_reference",
            oracle="reference_implementation_v1",
        ),
    ),
}


def _run_oracle(config: ChallengeConfig, case: dict[str, Any]) -> Any:
    """Executes the reference implementation directly, no sandbox.

    This is our own reviewed fixture source, not student input -- the
    sandbox boundary exists for the submitted repair, not for code we
    wrote and control.
    """
    namespace: dict[str, Any] = {}
    exec(config.oracle_path.read_text(encoding="utf-8"), namespace)  # noqa: S102 - trusted, reviewed fixture source
    entry_point = namespace[config.entry_point]
    return entry_point(dict(case["graph"]), case["start"])


class ExecutionStatus(StrEnum):
    COMPLETED = "completed"
    REJECTED = "rejected"
    ERRORED = "errored"
    TIMED_OUT = "timed_out"


@dataclass
class PropertyResult:
    name: str
    passed: bool
    detail: str


@dataclass
class EvidenceRecord:
    challenge_id: str
    challenge_version: str
    code_hash: str
    test_suite_version: str
    runtime_digest: str
    status: ExecutionStatus
    exit_status: int
    property_results: list[PropertyResult] = field(default_factory=list)
    signature: str = ""

    def signing_payload(self) -> str:
        payload = {
            "challenge_id": self.challenge_id,
            "challenge_version": self.challenge_version,
            "code_hash": self.code_hash,
            "test_suite_version": self.test_suite_version,
            "runtime_digest": self.runtime_digest,
            "status": self.status.value,
            "exit_status": self.exit_status,
            "property_results": [
                {"name": r.name, "passed": r.passed, "detail": r.detail} for r in self.property_results
            ],
        }
        return json.dumps(payload, sort_keys=True)

    def sign(self) -> None:
        self.signature = hmac.new(SANDBOX_SECRET.encode(), self.signing_payload().encode(), hashlib.sha256).hexdigest()


def _contains_disallowed_names(source: str) -> bool:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name.split(".")[0] not in ALLOWED_IMPORT_MODULES for alias in node.names):
                return True
        elif isinstance(node, ast.ImportFrom):
            module = (node.module or "").split(".")[0]
            if module not in ALLOWED_IMPORT_MODULES:
                return True
        elif isinstance(node, ast.Name) and node.id in DISALLOWED_NAMES:
            return True
        if isinstance(node, ast.Attribute) and node.attr in DISALLOWED_NAMES:
            return True
    return False


_RUNNER_TEMPLATE = """
import json

{repair_source}

cases = {cases}
results = []
for case in cases:
    try:
        output = {entry_point}(dict(case["graph"]), case["start"])
        results.append({{"ok": True, "output": output}})
    except Exception as error:  # noqa: BLE001 - reporting to parent, not swallowing
        results.append({{"ok": False, "error": f"raised {{type(error).__name__}}: {{error}}"}})
print(json.dumps(results))
"""


def _preexec_limits() -> None:
    resource.setrlimit(resource.RLIMIT_CPU, (_CPU_SECONDS, _CPU_SECONDS))
    try:
        resource.setrlimit(resource.RLIMIT_AS, (_ADDRESS_SPACE_BYTES, _ADDRESS_SPACE_BYTES))
    except (ValueError, OSError):
        # RLIMIT_AS is unsupported/unadjustable on some platforms (e.g. macOS
        # with an existing lower hard limit). CPU-time capping still applies;
        # production execution should run this in a container/VM with real
        # memory isolation rather than relying on rlimits alone.
        pass


def _run_in_subprocess(repair_source: str, config: ChallengeConfig) -> tuple[int, str, str]:
    runner = _RUNNER_TEMPLATE.format(
        repair_source=repair_source,
        cases=json.dumps(config.test_inputs),
        entry_point=config.entry_point,
    )
    with tempfile.TemporaryDirectory() as tmp:
        script_path = Path(tmp) / "runner.py"
        script_path.write_text(runner)
        try:
            completed = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=tmp,
                env={},
                capture_output=True,
                text=True,
                timeout=_TIMEOUT_SECONDS,
                preexec_fn=_preexec_limits if os.name == "posix" else None,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return -1, "", "timed out"
        return completed.returncode, completed.stdout, completed.stderr


def execute_repair(*, challenge_id: str, repair_source: str) -> EvidenceRecord:
    code_hash = hashlib.sha256(repair_source.encode()).hexdigest()
    record = EvidenceRecord(
        challenge_id=challenge_id,
        challenge_version="v1",
        code_hash=code_hash,
        test_suite_version=TEST_SUITE_VERSION,
        runtime_digest=RUNTIME_DIGEST,
        status=ExecutionStatus.REJECTED,
        exit_status=-1,
    )

    config = _CHALLENGES.get(challenge_id)
    if config is None:
        record.sign()
        return record

    if _contains_disallowed_names(repair_source):
        record.sign()
        return record

    try:
        ast.parse(repair_source)
    except SyntaxError:
        record.status = ExecutionStatus.ERRORED
        record.sign()
        return record

    returncode, stdout, stderr = _run_in_subprocess(repair_source, config)

    if returncode == -1 and stdout == "" and stderr == "timed out":
        record.status = ExecutionStatus.TIMED_OUT
        record.sign()
        return record

    if returncode != 0:
        record.status = ExecutionStatus.ERRORED
        record.exit_status = returncode
        record.sign()
        return record

    try:
        parsed = json.loads(stdout)
    except (json.JSONDecodeError, ValueError):
        record.status = ExecutionStatus.ERRORED
        record.exit_status = returncode
        record.sign()
        return record

    record.status = ExecutionStatus.COMPLETED
    record.exit_status = returncode
    record.property_results = _build_property_results(config, parsed)
    record.sign()
    return record


def _build_property_results(config: ChallengeConfig, submitted_results: list[dict[str, Any]]) -> list[PropertyResult]:
    property_results = []
    for i, (case, submitted) in enumerate(zip(config.test_inputs, submitted_results, strict=True)):
        name = f"case_{i}:{config.property_spec.property}"
        if not submitted["ok"]:
            property_results.append(PropertyResult(name=name, passed=False, detail=submitted["error"]))
            continue
        reference_output = _run_oracle(config, case)
        try:
            check = evaluate_property(
                config.property_spec,
                submitted_output=submitted["output"],
                reference_output=reference_output,
            )
        except UnknownPropertyError as error:
            property_results.append(PropertyResult(name=name, passed=False, detail=str(error)))
            continue
        property_results.append(PropertyResult(name=name, passed=check.passed, detail=check.detail))
    return property_results
