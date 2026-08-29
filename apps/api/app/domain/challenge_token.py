"""Opaque signed challenge tokens (docs/IMPLEMENTATION_PLAN.md §3.2).

Stateless by design, consistent with I5 (no server-side learner data
store): the token itself carries the claims a tool call needs
(challenge_id, session_id, issued_at), signed so the host model can carry
it between tool calls but never forge or alter it. There is no server-side
session table to look the token up in.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from dataclasses import dataclass

TOKEN_SECRET = os.getenv("EVIDENCE_ENGINE_TOKEN_SECRET", "dev-only-token-signing-key")


class InvalidTokenError(ValueError):
    pass


@dataclass(frozen=True)
class ChallengeClaims:
    challenge_id: str
    session_id: str
    issued_at: float


def _sign(payload_b64: str) -> str:
    return hmac.new(TOKEN_SECRET.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()


def issue_token(challenge_id: str) -> str:
    claims = {"challenge_id": challenge_id, "session_id": secrets.token_hex(16), "issued_at": time.time()}
    payload_b64 = base64.urlsafe_b64encode(json.dumps(claims, sort_keys=True).encode()).decode()
    return f"{payload_b64}.{_sign(payload_b64)}"


def verify_token(token: str) -> ChallengeClaims:
    try:
        payload_b64, signature = token.rsplit(".", 1)
    except ValueError as error:
        raise InvalidTokenError("malformed token") from error

    expected_signature = _sign(payload_b64)
    if not hmac.compare_digest(signature, expected_signature):
        raise InvalidTokenError("signature does not match")

    try:
        claims = json.loads(base64.urlsafe_b64decode(payload_b64.encode()))
    except Exception as error:
        raise InvalidTokenError("payload is not valid") from error

    try:
        return ChallengeClaims(
            challenge_id=str(claims["challenge_id"]),
            session_id=str(claims["session_id"]),
            issued_at=float(claims["issued_at"]),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise InvalidTokenError("payload is missing required claims") from error
