"""Phase 3 (docs/IMPLEMENTATION_PLAN.md §3.2): the opaque signed challenge
token that binds all four MCP tool calls to one challenge instance without
any server-side session store (I5: no server-side learner data store)."""

from __future__ import annotations

import pytest

from app.domain.challenge_token import InvalidTokenError, issue_token, verify_token


def test_issued_token_round_trips_the_challenge_id() -> None:
    token = issue_token("traversal-invariant-02")

    claims = verify_token(token)

    assert claims.challenge_id == "traversal-invariant-02"


def test_two_tokens_for_the_same_challenge_have_different_session_ids() -> None:
    first = verify_token(issue_token("traversal-invariant-02"))
    second = verify_token(issue_token("traversal-invariant-02"))

    assert first.session_id != second.session_id


def test_tampered_payload_is_rejected() -> None:
    token = issue_token("traversal-invariant-02")
    payload, signature = token.rsplit(".", 1)
    tampered = payload + "x." + signature

    with pytest.raises(InvalidTokenError):
        verify_token(tampered)


def test_tampered_signature_is_rejected() -> None:
    token = issue_token("traversal-invariant-02")
    payload, signature = token.rsplit(".", 1)
    flipped_signature = ("0" if signature[0] != "0" else "1") + signature[1:]

    with pytest.raises(InvalidTokenError):
        verify_token(payload + "." + flipped_signature)


def test_malformed_token_is_rejected_not_a_crash() -> None:
    with pytest.raises(InvalidTokenError):
        verify_token("not-a-real-token")
