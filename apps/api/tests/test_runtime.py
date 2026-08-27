from app.domain.runtime import (
    allowlisted_repair_passes,
    canonical_next_frontier,
    mutation_creates_duplicate_frontier,
)


def test_canonical_bfs_exposes_next_frontier_and_visited_state() -> None:
    assert canonical_next_frontier() == (["B", "C"], ["A", "B", "C"])


def test_controlled_mutation_is_observable() -> None:
    assert mutation_creates_duplicate_frontier() is True


def test_only_allowlisted_repair_can_pass() -> None:
    assert allowlisted_repair_passes("mark_visited_on_enqueue") is True
    assert allowlisted_repair_passes("paste_arbitrary_code") is False
