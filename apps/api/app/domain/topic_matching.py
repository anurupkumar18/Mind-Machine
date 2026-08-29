"""Deterministic keyword-overlap topic matching -- a heuristic, not a
semantic-understanding claim. Same framing PROJECT_CHARTER.md uses for the
practice-selection heuristic generally, and the same substring-match idiom
`app.domain.policy.select_coaching_card` already uses in this codebase.
"""

from __future__ import annotations

from app.domain.contracts import CanvasCourseContext, TopicMatch

CHALLENGE_TOPIC_TAGS: dict[str, list[str]] = {
    "traversal-invariant-02": ["graph traversal", "bfs", "breadth-first", "visited"],
}


class NoMatchingChallengeError(ValueError):
    """Raised when a topic string matches no known challenge's tags."""


def _matched_terms(title: str, tags: list[str]) -> list[str]:
    lowered = title.lower()
    return [tag for tag in tags if tag in lowered]


def match_topics(context: CanvasCourseContext) -> list[TopicMatch]:
    matches: list[TopicMatch] = []
    for module in context.modules:
        matched_challenge_id: str | None = None
        matched_terms: list[str] = []
        for challenge_id, tags in CHALLENGE_TOPIC_TAGS.items():
            terms = _matched_terms(module.name, tags)
            if terms:
                matched_challenge_id = challenge_id
                matched_terms = terms
                break
        matches.append(
            TopicMatch(
                module_name=module.name,
                matched_challenge_id=matched_challenge_id,
                matched_terms=matched_terms,
            )
        )
    return matches


def resolve_challenge_for_topic(topic: str) -> str:
    for challenge_id, tags in CHALLENGE_TOPIC_TAGS.items():
        if _matched_terms(topic, tags):
            return challenge_id
    raise NoMatchingChallengeError(f"No challenge matches topic: {topic!r}")
