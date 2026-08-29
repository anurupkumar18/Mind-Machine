"""Topic-tag matching: deterministic keyword overlap, not semantic
understanding (docs/superpowers/specs/2026-08-28-canvas-mock-topic-
grounding-design.md)."""

from __future__ import annotations

import pytest

from app.domain.contracts import CanvasCourseContext, CanvasModule
from app.domain.topic_matching import (
    NoMatchingChallengeError,
    match_topics,
    resolve_challenge_for_topic,
)


def test_match_topics_matches_module_containing_a_tag() -> None:
    context = CanvasCourseContext(
        course_name="Test Course",
        syllabus_body="",
        modules=[CanvasModule(id=1, name="Unit 3: Graph Traversal (BFS/DFS)")],
    )

    matches = match_topics(context)

    assert len(matches) == 1
    assert matches[0].matched_challenge_id == "traversal-invariant-02"
    assert matches[0].matched_terms


def test_match_topics_matches_via_alias() -> None:
    context = CanvasCourseContext(
        course_name="Test Course",
        syllabus_body="",
        modules=[CanvasModule(id=1, name="BFS Practice Week")],
    )

    matches = match_topics(context)

    assert matches[0].matched_challenge_id == "traversal-invariant-02"
    assert "bfs" in matches[0].matched_terms


def test_match_topics_leaves_unmatched_module_honest_about_no_match() -> None:
    context = CanvasCourseContext(
        course_name="Test Course",
        syllabus_body="",
        modules=[CanvasModule(id=1, name="Unit 4: Dynamic Programming")],
    )

    matches = match_topics(context)

    assert matches[0].matched_challenge_id is None
    assert matches[0].matched_terms == []


def test_resolve_challenge_for_topic_success() -> None:
    assert resolve_challenge_for_topic("graph traversal review") == "traversal-invariant-02"


def test_resolve_challenge_for_topic_raises_when_nothing_matches() -> None:
    with pytest.raises(NoMatchingChallengeError):
        resolve_challenge_for_topic("dynamic programming")
