"""Phase 1 spike 4 (docs/IMPLEMENTATION_PLAN.md §6): confirm a Canvas
access token can authenticate against the real Canvas API.

Deliberately minimal and read-only: calls only /api/v1/users/self, which
returns nothing beyond the token owner's own identity -- no course,
syllabus, or module content is touched here. That's Phase 4 work, gated
on this spike resolving (and on the institutional data-policy answer,
which this script does not and cannot obtain on its own).

Never prints the token. Reads it from the environment only.

Usage:
    cd apps/api && set -a && source .env && set +a
    python3 ../../scripts/verify_canvas_access.py
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request


def build_self_check_request(base_url: str, access_token: str) -> urllib.request.Request:
    url = f"{base_url.rstrip('/')}/api/v1/users/self"
    return urllib.request.Request(url, headers={"Authorization": f"Bearer {access_token}"})


def summarize_self_response(payload: dict[str, object]) -> str:
    name = payload.get("name", "<unknown>")
    user_id = payload.get("id", "<unknown>")
    return f"Authenticated as: {name} (id={user_id})"


def main() -> int:
    base_url = os.environ.get("CANVAS_BASE_URL", "").strip()
    access_token = os.environ.get("CANVAS_ACCESS_TOKEN", "").strip()

    if not base_url or not access_token:
        print(
            "CANVAS_BASE_URL and/or CANVAS_ACCESS_TOKEN are not set. "
            "Fill them into apps/api/.env (gitignored, never commit it) "
            "and source it before running this script.",
            file=sys.stderr,
        )
        return 2

    request = build_self_check_request(base_url, access_token)
    try:
        with urllib.request.urlopen(request, timeout=10) as response:  # noqa: S310 - fixed institutional API host
            payload = json.loads(response.read())
    except urllib.error.HTTPError as error:
        # Deliberately not printing response body: some Canvas error payloads
        # can echo back request context we'd rather not assume is safe to log.
        print(f"Canvas rejected the token: HTTP {error.code} {error.reason}", file=sys.stderr)
        return 1
    except urllib.error.URLError as error:
        print(f"Could not reach {base_url}: {error.reason}", file=sys.stderr)
        return 1

    print(summarize_self_response(payload))
    print(f"Base URL: {base_url}")
    print("Spike 4 (connectivity half): PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
