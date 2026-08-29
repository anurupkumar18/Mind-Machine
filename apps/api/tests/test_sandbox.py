from __future__ import annotations

import hashlib
import hmac

from app.domain.sandbox import SANDBOX_SECRET, ExecutionStatus, execute_repair

GOOD_REPAIR = """
from collections import deque


def bfs(graph, start):
    frontier = deque([start])
    visited = {start}
    order = []
    while frontier:
        node = frontier.popleft()
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                frontier.append(neighbor)
    return order
"""

BAD_REPAIR = """
from collections import deque


def bfs(graph, start):
    # Bug: pops from the same end it pushes to, so this behaves like a
    # depth-first stack instead of a breadth-first queue.
    frontier = deque([start])
    visited = {start}
    order = []
    while frontier:
        node = frontier.pop()
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                frontier.append(neighbor)
    return order
"""

MALICIOUS_REPAIR = """
import os

def bfs(graph, start):
    os.system("echo pwned")
    return [start]
"""

SYNTAX_ERROR_REPAIR = "def bfs(graph, start"


def test_known_good_repair_passes_all_properties() -> None:
    record = execute_repair(challenge_id="traversal-invariant-02", repair_source=GOOD_REPAIR)

    assert record.status is ExecutionStatus.COMPLETED
    assert record.exit_status == 0
    assert all(result.passed for result in record.property_results)
    assert len(record.property_results) >= 2


def test_known_bad_repair_fails_a_property() -> None:
    record = execute_repair(challenge_id="traversal-invariant-02", repair_source=BAD_REPAIR)

    assert record.status is ExecutionStatus.COMPLETED
    assert record.exit_status == 0
    assert any(not result.passed for result in record.property_results)


def test_evidence_record_is_signed_and_matches_recomputed_signature() -> None:
    record = execute_repair(challenge_id="traversal-invariant-02", repair_source=GOOD_REPAIR)

    payload = record.signing_payload()
    expected = hmac.new(SANDBOX_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    assert record.signature == expected


def test_code_hash_reflects_submitted_source() -> None:
    record = execute_repair(challenge_id="traversal-invariant-02", repair_source=GOOD_REPAIR)

    assert record.code_hash == hashlib.sha256(GOOD_REPAIR.encode()).hexdigest()


def test_disallowed_import_is_rejected_without_execution() -> None:
    record = execute_repair(challenge_id="traversal-invariant-02", repair_source=MALICIOUS_REPAIR)

    assert record.status is ExecutionStatus.REJECTED
    assert record.property_results == []
    # Rejection must still be signed evidence, not a silent drop.
    assert record.signature


def test_syntax_error_is_reported_as_failed_execution_not_a_crash() -> None:
    record = execute_repair(challenge_id="traversal-invariant-02", repair_source=SYNTAX_ERROR_REPAIR)

    assert record.status is ExecutionStatus.ERRORED
    assert record.property_results == []
    assert record.signature


def test_unknown_challenge_id_is_rejected() -> None:
    record = execute_repair(challenge_id="does-not-exist", repair_source=GOOD_REPAIR)

    assert record.status is ExecutionStatus.REJECTED
