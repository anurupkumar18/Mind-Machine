"""Proves the sandbox kernel actually generalizes beyond the one challenge
it was built against (traversal-invariant-02/bfs), not just coincidentally
works for it. Before this test existed, `_run_oracle` and the sandboxed
runner both hardcoded a `(graph, start)` call signature -- this exercises
a second challenge with an entirely different function shape
(list[int], int) to force that into a genuine `**kwargs` call."""

from __future__ import annotations

from app.domain.sandbox import execute_repair

GOOD_BINARY_SEARCH = """
def binary_search(sorted_values, target):
    low, high = 0, len(sorted_values) - 1
    while low <= high:
        mid = (low + high) // 2
        if sorted_values[mid] == target:
            return mid
        if sorted_values[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
"""

BAD_BINARY_SEARCH = """
def binary_search(sorted_values, target):
    low, high = 0, len(sorted_values) - 1
    while low < high:
        mid = (low + high) // 2
        if sorted_values[mid] == target:
            return mid
        if sorted_values[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
"""


def test_known_good_repair_passes_for_a_structurally_different_challenge() -> None:
    record = execute_repair(challenge_id="binary-search-invariant-01", repair_source=GOOD_BINARY_SEARCH)

    assert record.status.value == "completed"
    assert all(result.passed for result in record.property_results)


def test_known_bad_repair_fails_for_a_structurally_different_challenge() -> None:
    """`low < high` instead of `low <= high` misses the case where the
    target is the single remaining element."""
    record = execute_repair(challenge_id="binary-search-invariant-01", repair_source=BAD_BINARY_SEARCH)

    assert record.status.value == "completed"
    assert any(not result.passed for result in record.property_results)
