"""Automated equivalent-mutant detection (docs/IMPLEMENTATION_PLAN.md §6,
Phase 2, R1). Generalizes the manual technique from episodic/0025 (2000
randomized trials against the reference implementation) into reusable
code: differential testing against the oracle across randomly generated
valid inputs, reusing the sandbox's real execution machinery
(app.domain.sandbox.run_cases) rather than a separate, unsandboxed path.
"""

from __future__ import annotations

from app.domain.equivalence import check_equivalence
from app.domain.sandbox import FIXTURES_ROOT

BINARY_SEARCH_SOURCE = (FIXTURES_ROOT / "repos" / "public-search" / "binary_search.py").read_text(encoding="utf-8")

# The confirmed genuine equivalent mutant from episodic/0025.
DIVISOR_ONE_MUTANT = """
def binary_search(sorted_values, target):
    low, high = 0, len(sorted_values) - 1
    while low <= high:
        mid = (low + high) // 1
        if sorted_values[mid] == target:
            return mid
        if sorted_values[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
"""

# A confirmed real bug (episodic/0025): skips checking index mid - 1.
SKIPPED_INDEX_MUTANT = """
def binary_search(sorted_values, target):
    low, high = 0, len(sorted_values) - 1
    while low <= high:
        mid = (low + high) // 2
        if sorted_values[mid] == target:
            return mid
        if sorted_values[mid] < target:
            low = mid + 1
        else:
            high = mid - 2
    return -1
"""


def test_the_confirmed_equivalent_mutant_is_reported_equivalent() -> None:
    result = check_equivalence(
        challenge_id="binary-search-invariant-01", mutant_source=DIVISOR_ONE_MUTANT, trials=300, seed=1
    )

    assert result.is_likely_equivalent is True
    assert result.mismatches == []
    assert result.trials_run == 300


def test_the_confirmed_buggy_mutant_is_reported_not_equivalent() -> None:
    result = check_equivalence(
        challenge_id="binary-search-invariant-01", mutant_source=SKIPPED_INDEX_MUTANT, trials=300, seed=1
    )

    assert result.is_likely_equivalent is False
    assert result.mismatches


def test_the_unmutated_reference_is_equivalent_to_itself() -> None:
    result = check_equivalence(
        challenge_id="binary-search-invariant-01", mutant_source=BINARY_SEARCH_SOURCE, trials=100, seed=2
    )

    assert result.is_likely_equivalent is True


def test_results_are_deterministic_given_the_same_seed() -> None:
    first = check_equivalence(
        challenge_id="binary-search-invariant-01", mutant_source=SKIPPED_INDEX_MUTANT, trials=50, seed=7
    )
    second = check_equivalence(
        challenge_id="binary-search-invariant-01", mutant_source=SKIPPED_INDEX_MUTANT, trials=50, seed=7
    )

    assert first.mismatches == second.mismatches


def test_disallowed_code_is_reported_not_equivalent_not_a_crash() -> None:
    result = check_equivalence(
        challenge_id="binary-search-invariant-01",
        mutant_source="import os\ndef binary_search(sorted_values, target): return -1",
        trials=50,
        seed=1,
    )

    assert result.is_likely_equivalent is False
