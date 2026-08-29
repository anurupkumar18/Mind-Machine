"""canvas_mock.py returns fixture data shaped like the real Canvas API
this stands in for until institutional approval lands (I4; memory/episodic/
0017, 0018)."""

from __future__ import annotations

from app.domain.canvas_mock import mock_course_context
from app.domain.contracts import CanvasCourseContext


def test_mock_course_context_returns_the_fixture_course() -> None:
    context = mock_course_context()

    assert isinstance(context, CanvasCourseContext)
    assert context.course_name == "CS 3500 — Foundations of Software Engineering"
    assert "graph traversal" in context.syllabus_body.lower()


def test_mock_course_context_includes_all_fixture_modules() -> None:
    context = mock_course_context()

    module_names = [module.name for module in context.modules]
    assert module_names == [
        "Unit 1: Recursion and Induction",
        "Unit 2: Sorting and Divide-and-Conquer",
        "Unit 3: Graph Traversal (BFS/DFS)",
        "Unit 4: Dynamic Programming",
    ]


def test_mock_course_context_never_includes_excluded_categories() -> None:
    """I4: assignments/quizzes/discussions/submissions/gradebook must never
    appear anywhere in the mock course, matching the real allowlist boundary."""
    payload = mock_course_context().model_dump()
    blob = str(payload).lower()

    for excluded in ("assignment", "quiz", "submission", "gradebook", "discussion"):
        assert excluded not in blob
