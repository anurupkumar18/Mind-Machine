"""Heuristic I1 data-boundary enforcement: best-effort pattern matching,
not a guarantee (docs/superpowers/specs/2026-08-29-student-study-
workspace-design.md). Covers the allow/flag/reject cases from the
research doc's include/exclude table, plus adversarial synthetic
examples of submission-like, exam-like, and roster/discussion-like
content."""

from __future__ import annotations

from app.domain.data_boundary import classify_for_data_boundary


def test_allows_plain_syllabus_text() -> None:
    status, reason = classify_for_data_boundary(
        "syllabus.txt", "This course covers graph traversal and dynamic programming."
    )

    assert status == "allow"
    assert reason is None


def test_allows_students_own_notes() -> None:
    status, reason = classify_for_data_boundary(
        "my_notes.txt", "Remember: BFS marks visited on enqueue, not dequeue."
    )

    assert status == "allow"
    assert reason is None


def test_rejects_content_with_a_visible_grade() -> None:
    status, reason = classify_for_data_boundary(
        "homework1.txt", "Great work on this problem set.\nGrade: 95/100"
    )

    assert status == "reject"
    assert reason is not None and "graded-submission" in reason


def test_rejects_content_with_a_visible_score() -> None:
    status, reason = classify_for_data_boundary("notes.txt", "Score: 42 out of 50")

    assert status == "reject"
    assert reason is not None


def test_rejects_filename_indicating_a_submission() -> None:
    status, reason = classify_for_data_boundary("problem_set_1_submission.pdf", "Some content.")

    assert status == "reject"
    assert reason is not None and "submission" in reason


def test_rejects_answer_key_content() -> None:
    status, reason = classify_for_data_boundary("study_guide.txt", "Answer Key: 1) B 2) A 3) C")

    assert status == "reject"
    assert reason is not None


def test_flags_filename_indicating_an_exam() -> None:
    status, reason = classify_for_data_boundary("midterm_exam.txt", "Some content about the course.")

    assert status == "flag"
    assert reason is not None and "exam" in reason.lower()


def test_flags_discussion_post_like_content() -> None:
    status, reason = classify_for_data_boundary(
        "forum.txt", "Posted by Jane Smith: I think the answer is related to invariants."
    )

    assert status == "flag"
    assert reason is not None


def test_flags_reply_marker_content() -> None:
    status, reason = classify_for_data_boundary("thread.txt", "Re: question about assignment 3")

    assert status == "flag"
    assert reason is not None
