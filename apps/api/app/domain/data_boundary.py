"""Heuristic data-boundary enforcement for uploaded study materials (I1).

Best-effort pattern matching, not a guarantee -- same honesty standard
this project already applies to its other heuristics (topic_matching.py's
keyword overlap, the practice-selection heuristic in PROJECT_CHARTER.md).
Never a machine-learning classifier: no inference cost, and a
transparent, auditable rule set is easier to reason about and extend than
an opaque model.
"""

from __future__ import annotations

import re
from typing import Literal

DataBoundaryStatus = Literal["allow", "flag", "reject"]

_REJECT_TEXT_PATTERNS = [
    (re.compile(r"\bgrade\s*:\s*\d", re.IGNORECASE), "content matches a graded-submission pattern (a visible grade)"),
    (re.compile(r"\bscore\s*:\s*\d", re.IGNORECASE), "content matches a graded-submission pattern (a visible score)"),
    (re.compile(r"\bsubmitted\s+by\b", re.IGNORECASE), "content matches a graded-submission pattern (a submission marker)"),
    (re.compile(r"\banswer\s+key\b", re.IGNORECASE), "content matches a graded-submission pattern (an answer key)"),
]
_REJECT_FILENAME_MARKERS = ["graded", "submission", "gradebook", "answerkey"]

_FLAG_TEXT_PATTERNS = [
    (re.compile(r"\bposted\s+by\b", re.IGNORECASE), "content matches a discussion-post-like pattern (a poster attribution)"),
    (re.compile(r"^\s*re\s*:", re.IGNORECASE | re.MULTILINE), "content matches a discussion-post-like pattern (a reply marker)"),
]
_FLAG_FILENAME_MARKERS = ["quiz", "exam", "test"]


def classify_for_data_boundary(filename: str, text: str) -> tuple[DataBoundaryStatus, str | None]:
    lowered_filename = filename.lower()

    for marker in _REJECT_FILENAME_MARKERS:
        if marker in lowered_filename:
            return "reject", f"filename contains {marker!r}, which looks like a graded submission"
    for pattern, reason in _REJECT_TEXT_PATTERNS:
        if pattern.search(text):
            return "reject", reason

    for marker in _FLAG_FILENAME_MARKERS:
        if marker in lowered_filename:
            return "flag", f"filename contains {marker!r}, which may be exam/quiz content"
    for pattern, reason in _FLAG_TEXT_PATTERNS:
        if pattern.search(text):
            return "flag", reason

    return "allow", None
