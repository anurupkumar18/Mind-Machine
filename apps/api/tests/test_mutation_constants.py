"""Second AST mutation operator (docs/IMPLEMENTATION_PLAN.md §6 Phase 2, R1):
integer-constant boundary mutation (+1/-1 on numeric literals), the
classic off-by-one bug generator. Generic across any source, same as
comparison-operator replacement."""

from __future__ import annotations

import ast

from app.domain.mutation import generate_constant_mutants
from app.domain.sandbox import FIXTURES_ROOT, execute_repair

BINARY_SEARCH_SOURCE = (FIXTURES_ROOT / "repos" / "public-search" / "binary_search.py").read_text(encoding="utf-8")

SOURCE_WITH_BOOL_AND_INT = """
def f(x):
    flag = True
    return x + 1 if flag else x - 2
"""


def test_generates_two_mutants_per_integer_constant() -> None:
    source = "def f(x):\n    return x + 1\n"

    mutants = generate_constant_mutants(source)

    assert len(mutants) == 2
    values = sorted(m.description for m in mutants)
    assert any("1->2" in v for v in values)
    assert any("1->0" in v for v in values)


def test_boolean_literals_are_not_treated_as_integer_constants() -> None:
    mutants = generate_constant_mutants(SOURCE_WITH_BOOL_AND_INT)

    # Only the two real int literals (1, 2) should be mutated -- 2 mutants
    # each -- never the `True` literal, even though bool is an int subclass.
    assert len(mutants) == 4
    assert all("flag = True" in m.mutated_source for m in mutants)


def test_each_mutant_source_parses_and_differs_from_original() -> None:
    mutants = generate_constant_mutants(BINARY_SEARCH_SOURCE)

    for mutant in mutants:
        ast.parse(mutant.mutated_source)
        assert mutant.mutated_source != BINARY_SEARCH_SOURCE


def test_mutant_ids_are_unique_and_deterministic() -> None:
    first_run = generate_constant_mutants(BINARY_SEARCH_SOURCE)
    second_run = generate_constant_mutants(BINARY_SEARCH_SOURCE)

    ids_first = [m.mutant_id for m in first_run]
    assert len(ids_first) == len(set(ids_first))
    assert ids_first == [m.mutant_id for m in second_run]


def test_at_least_one_binary_search_constant_mutant_is_killed() -> None:
    mutants = generate_constant_mutants(BINARY_SEARCH_SOURCE)
    assert mutants, "expected binary_search's integer literals to produce mutants"

    killed = []
    for mutant in mutants:
        record = execute_repair(challenge_id="binary-search-invariant-01", repair_source=mutant.mutated_source)
        if record.status.value == "completed" and any(not r.passed for r in record.property_results):
            killed.append(mutant)

    assert killed, "expected at least one constant mutant to be killed by the existing property"
