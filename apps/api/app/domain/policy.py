from __future__ import annotations

from typing import cast

from app.domain.contracts import CoachingCard, PlanCommitment, PolicyMode
from app.domain.fixtures import fixture_value


def select_coaching_card(plan: PlanCommitment, policy: PolicyMode) -> CoachingCard:
    cards = cast(list[dict[str, object]], fixture_value("coaching_cards"))
    reasoning = f"{plan.invariant} {plan.strategy}".lower()
    selected = next(
        (card for card in cards if not all(term in reasoning for term in cast(list[str], card["trigger_terms"]))),
        cards[0],
    )
    return CoachingCard(
        id=cast(str, selected["id"]),
        title=cast(str, selected["title"]),
        misconception=cast(str, selected["misconception"]),
        corrective_question=cast(str, selected["corrective_question"]),
        hint=None if policy == PolicyMode.NO_CODE_HELP else cast(str, selected["hint"]),
    )
