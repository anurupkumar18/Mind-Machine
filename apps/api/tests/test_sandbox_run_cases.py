"""`run_cases` is the lower-level primitive extracted from `execute_repair`
so equivalence checking (app.domain.equivalence) can reuse the sandboxed
execution machinery against an arbitrary case list, not just a
challenge's configured hidden tests."""

from __future__ import annotations

from app.domain.sandbox import run_cases

GOOD_BFS = """
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


def test_runs_against_an_arbitrary_case_list_not_the_configured_hidden_tests() -> None:
    custom_cases = [{"graph": {"X": ["Y"], "Y": []}, "start": "X"}]

    outcomes = run_cases(challenge_id="traversal-invariant-02", repair_source=GOOD_BFS, cases=custom_cases)

    assert outcomes is not None
    assert len(outcomes) == 1
    assert outcomes[0].ok is True
    assert outcomes[0].output == ["X", "Y"]


def test_returns_none_for_unknown_challenge() -> None:
    outcomes = run_cases(challenge_id="does-not-exist", repair_source=GOOD_BFS, cases=[])

    assert outcomes is None


def test_returns_none_for_disallowed_code() -> None:
    outcomes = run_cases(
        challenge_id="traversal-invariant-02",
        repair_source="import os\ndef bfs(g, s): return [s]",
        cases=[{"graph": {"A": []}, "start": "A"}],
    )

    assert outcomes is None


def test_case_that_raises_is_reported_as_not_ok_not_a_crash() -> None:
    bad_source = "def bfs(graph, start):\n    raise ValueError('boom')\n"

    outcomes = run_cases(
        challenge_id="traversal-invariant-02",
        repair_source=bad_source,
        cases=[{"graph": {"A": []}, "start": "A"}],
    )

    assert outcomes is not None
    assert outcomes[0].ok is False
    assert "boom" in outcomes[0].error
