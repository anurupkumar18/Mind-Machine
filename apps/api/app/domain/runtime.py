from __future__ import annotations

from collections import deque
from typing import cast

from app.domain.fixtures import fixture_data, fixture_value


def canonical_next_frontier() -> tuple[list[str], list[str]]:
    data = fixture_data()
    graph = data["graph"]
    assert isinstance(graph, dict)
    start = str(data["start"])
    frontier = deque([start])
    visited = {start}
    current = frontier.popleft()
    for neighbor in graph[current]:
        if neighbor not in visited:
            visited.add(neighbor)
            frontier.append(neighbor)
    return list(frontier), sorted(visited)


def mutation_creates_duplicate_frontier() -> bool:
    data = fixture_data()
    graph = data["graph"]
    assert isinstance(graph, dict)
    frontier = deque([str(data["start"])])
    visited: set[str] = set()
    while frontier:
        current = frontier.popleft()
        if current in visited:
            continue
        visited.add(current)
        for neighbor in graph[current]:
            frontier.append(neighbor)
        if len(frontier) != len(set(frontier)):
            return True
    return False


def allowlisted_repair_passes(repair_id: str) -> bool:
    mutation = cast(dict[str, str], fixture_value("mutation"))
    if repair_id != mutation["allowed_repair"]:
        return False
    expected_frontier, visited = canonical_next_frontier()
    return (
        expected_frontier == cast(list[str], fixture_value("expected_first_frontier"))
        and visited == cast(list[str], fixture_value("expected_first_visited"))
        and mutation_creates_duplicate_frontier()
    )
