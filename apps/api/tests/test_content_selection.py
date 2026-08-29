"""Kill-ratio filtering policy (docs/IMPLEMENTATION_PLAN.md §6, Phase 2,
R1): decides what to do with a generated mutant, combining
app.domain.kill_ratio.classify_mutant and
app.domain.equivalence.check_equivalence rather than either alone.

Policy, stated plainly because "what counts as good content" is a
judgment call worth being explicit about:
- killed -> accept as practice content. This is what a real bug looks
  like: the mutation changes behavior, and the existing properties catch
  it.
- survived, and equivalence-checking agrees it's equivalent -> reject. No
  test-input set will ever kill a genuine equivalent mutant, so more
  hidden tests can't fix this one; it's not useful practice content.
- survived, but equivalence-checking does NOT confirm it's equivalent ->
  flag for human review. This is the ambiguous, interesting case from
  episodic/0025: it might be a weak test-input set (fixable by adding a
  case) or a genuine equivalent mutant the random trials didn't happen to
  distinguish (equivalence-checking is statistical, not a proof). Silently
  picking one interpretation would hide a real judgment call.

`decide()` is the pure policy (unit-tested against constructed inputs
covering all three branches, including the one no mutant in the current
dataset happens to exercise). `select_mutant()` is the orchestration,
integration-tested against the two branches real mutants exist for.
"""

from __future__ import annotations

from app.domain.content_selection import decide, select_mutant
from app.domain.equivalence import EquivalenceResult
from app.domain.mutation import Mutant, generate_comparison_mutants, generate_constant_mutants
from app.domain.sandbox import FIXTURES_ROOT

BINARY_SEARCH_SOURCE = (FIXTURES_ROOT / "repos" / "public-search" / "binary_search.py").read_text(encoding="utf-8")


def _mutant(description: str) -> Mutant:
    all_mutants = generate_comparison_mutants(BINARY_SEARCH_SOURCE) + generate_constant_mutants(BINARY_SEARCH_SOURCE)
    matches = [m for m in all_mutants if m.description == description]
    assert matches, f"no mutant with description {description!r}"
    return matches[0]


def test_decide_accepts_a_killed_mutant_without_needing_equivalence_data() -> None:
    assert decide(kill_outcome="killed", equivalence_result=None) == "accepted"


def test_decide_rejects_a_survived_mutant_confirmed_equivalent() -> None:
    result = EquivalenceResult(is_likely_equivalent=True, trials_run=200)

    assert decide(kill_outcome="survived", equivalence_result=result) == "rejected_equivalent"


def test_decide_flags_a_survived_mutant_not_confirmed_equivalent() -> None:
    result = EquivalenceResult(is_likely_equivalent=False, trials_run=200)

    assert decide(kill_outcome="survived", equivalence_result=result) == "flagged_for_review"


def test_select_mutant_accepts_a_real_killed_mutant() -> None:
    mutant = _mutant("Eq->NotEq at compare #1.0")

    decision = select_mutant(challenge_id="binary-search-invariant-01", mutant=mutant, equivalence_trials=100, seed=1)

    assert decision.outcome == "accepted"
    assert decision.equivalence_result is None  # never needed -- it was already killed


def test_select_mutant_rejects_the_confirmed_equivalent_mutant() -> None:
    mutant = _mutant("2->1 at constant #3")

    decision = select_mutant(
        challenge_id="binary-search-invariant-01", mutant=mutant, equivalence_trials=500, seed=1
    )

    assert decision.outcome == "rejected_equivalent"
    assert decision.equivalence_result is not None
    assert decision.equivalence_result.is_likely_equivalent is True


def test_select_mutant_decision_carries_the_evidence_it_was_based_on() -> None:
    """Auditable, not a bare verdict -- a human reviewing a rejected or
    flagged mutant needs to see why."""
    mutant = _mutant("2->1 at constant #3")

    decision = select_mutant(
        challenge_id="binary-search-invariant-01", mutant=mutant, equivalence_trials=200, seed=3
    )

    assert decision.mutant is mutant
    assert decision.kill_outcome == "survived"
    assert decision.equivalence_result is not None
