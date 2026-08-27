from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import cast

from app.domain.contracts import ChallengeTemplate

ROOT = Path(__file__).resolve().parents[4]
FIXTURE_PATH = ROOT / "fixtures" / "challenges" / "traversal-invariant-02.json"


@lru_cache(maxsize=1)
def challenge_template() -> ChallengeTemplate:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return ChallengeTemplate.model_validate(payload["template"])


@lru_cache(maxsize=1)
def fixture_data() -> dict[str, object]:
    return cast(dict[str, object], json.loads(FIXTURE_PATH.read_text(encoding="utf-8")))


def fixture_value(key: str) -> object:
    return fixture_data()[key]
