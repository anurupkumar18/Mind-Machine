"""Mock stand-in for the Phase 4 Canvas read-only client (I4).

Real Canvas access is confirmed institutionally blocked (memory/episodic/
0017, 0018) -- this module returns fixture data shaped like the real
Canvas API responses it stands in for, so the topic-grounding pipeline
downstream of it is exercised honestly, and swapping in a real client
later (once institutional approval lands) means replacing this module's
implementation, not the pipeline that consumes it. No network call is
ever made here.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.domain.contracts import CanvasCourseContext, CanvasModule

ROOT = Path(__file__).resolve().parents[4]
COURSE_FIXTURE_PATH = ROOT / "fixtures" / "canvas" / "course.json"


@lru_cache(maxsize=1)
def mock_course_context() -> CanvasCourseContext:
    payload = json.loads(COURSE_FIXTURE_PATH.read_text(encoding="utf-8"))
    return CanvasCourseContext(
        course_name=payload["course"]["name"],
        syllabus_body=payload["course"]["syllabus_body"],
        modules=[CanvasModule(id=m["id"], name=m["name"]) for m in payload["modules"]],
    )
