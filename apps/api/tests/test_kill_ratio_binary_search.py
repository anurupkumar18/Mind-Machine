"""Phase 2 (docs/IMPLEMENTATION_PLAN.md §6, R1): real equivalent-mutant
tolerance and test-coverage investigation on the binary_search kernel,
using the corrected classify_mutant (episodic/0025).

Three mutants of binary_search's integer constants survived the original
3-case test-input set. Investigated each with 2000 random-input trials
against the reference implementation (see episodic/0025 for detail):

- `// 2` -> `// 1` (mid = low + high): 0/2000 mismatches. This is a real
  equivalent mutant -- the resulting control flow degenerates into an
  exhaustive top-down scan that happens to always produce the same
  input/output behavior as real binary search, just O(n) instead of
  O(log n). No test-input set will ever kill it under
  output_equals_reference, because it isn't actually wrong by that
  property's definition.
- `mid - 1` -> `mid - 2` (skips checking index mid-1 entirely) and
  `mid - 1` -> `mid - 0` (can infinite-loop): both are genuine bugs the
  original 3 test cases were too narrow to expose. A 7-element array with
  the target at the specific index the skip/loop would miss closes the
  gap for both.
"""

from __future__ import annotations

import pytest

from app.domain.kill_ratio import classify_mutant
from app.domain.mutation import generate_constant_mutants
from app.domain.sandbox import FIXTURES_ROOT, execute_repair

BINARY_SEARCH_SOURCE = (FIXTURES_ROOT / "repos" / "public-search" / "binary_search.py").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def mutant_outcomes() -> dict[str, str]:
    outcomes = {}
    for mutant in generate_constant_mutants(BINARY_SEARCH_SOURCE):
        record = execute_repair(challenge_id="binary-search-invariant-01", repair_source=mutant.mutated_source)
        outcomes[mutant.description] = classify_mutant(record)
    return outcomes


def test_the_divisor_mutation_to_one_is_a_genuine_equivalent_mutant(mutant_outcomes: dict[str, str]) -> None:
    assert mutant_outcomes["2->1 at constant #3"] == "survived"


def test_the_high_boundary_gap_mutants_are_now_killed_by_the_strengthened_test_set(
    mutant_outcomes: dict[str, str],
) -> None:
    assert mutant_outcomes["1->2 at constant #5"] == "killed"
    assert mutant_outcomes["1->0 at constant #5"] == "killed"


def test_known_good_repair_still_passes_the_strengthened_test_set() -> None:
    good = """
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
    record = execute_repair(challenge_id="binary-search-invariant-01", repair_source=good)

    assert record.status.value == "completed"
    assert all(result.passed for result in record.property_results)
