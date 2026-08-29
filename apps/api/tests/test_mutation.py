"""Phase 2 (docs/IMPLEMENTATION_PLAN.md §6, R1): the AST mutation-operator
library. Generic, not fixture-specific (memory/semantic/architecture.md:
"application code must not branch on fixture-specific prose or
outcomes") -- it walks any source's comparison operators, not bfs's
particular structure."""

from __future__ import annotations

import ast

from app.domain.mutation import generate_comparison_mutants
from app.domain.sandbox import FIXTURES_ROOT, execute_repair

BFS_SOURCE = (FIXTURES_ROOT / "repos" / "public-graph-traversal" / "bfs.py").read_text(encoding="utf-8")


def test_generates_at_least_one_mutant_for_bfs_source() -> None:
    mutants = generate_comparison_mutants(BFS_SOURCE)

    assert len(mutants) >= 1


def test_each_mutant_source_parses_and_differs_from_original() -> None:
    mutants = generate_comparison_mutants(BFS_SOURCE)

    for mutant in mutants:
        ast.parse(mutant.mutated_source)  # raises if invalid
        assert mutant.mutated_source != BFS_SOURCE


def test_mutant_ids_are_unique_and_deterministic() -> None:
    first_run = generate_comparison_mutants(BFS_SOURCE)
    second_run = generate_comparison_mutants(BFS_SOURCE)

    ids_first = [m.mutant_id for m in first_run]
    ids_second = [m.mutant_id for m in second_run]
    assert len(ids_first) == len(set(ids_first))
    assert ids_first == ids_second


def test_membership_mutant_of_bfs_is_killed_by_the_existing_property() -> None:
    """The known-bad half of Phase 2's DoD test battery: a real mutant
    should actually fail the property that's supposed to catch it."""
    mutants = generate_comparison_mutants(BFS_SOURCE)
    membership_mutants = [m for m in mutants if "NotIn" in m.description]
    assert membership_mutants, "expected a NotIn->In mutation of `if neighbor not in visited`"

    record = execute_repair(challenge_id="traversal-invariant-02", repair_source=membership_mutants[0].mutated_source)

    assert record.status.value == "completed"
    assert any(not result.passed for result in record.property_results), "mutant should be killed, not survive"


def test_unmutated_reference_source_passes_as_known_good() -> None:
    """The known-good half of the same test battery."""
    record = execute_repair(challenge_id="traversal-invariant-02", repair_source=BFS_SOURCE)

    assert record.status.value == "completed"
    assert all(result.passed for result in record.property_results)
