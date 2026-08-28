from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

PLAN = {
    "objective": "Traverse a graph in breadth-first order.",
    "strategy": "Use a queue and mark nodes as visited on enqueue.",
    "representation": "Adjacency list",
    "invariant": "Every queued node is already marked visited.",
    "complexity": "O(V + E)",
    "planned_tests": "Cycle graph and two parents pointing to one node."
}


def test_full_evidence_api_path() -> None:
    checkpoint = client.post("/checkpoint", json={"policy_mode": "hints_only", "plan": PLAN})
    assert checkpoint.status_code == 200
    assert checkpoint.json()["card"]["hint"] is not None
    assert "snippet" not in checkpoint.json()["card"]

    prediction = client.post("/challenge/predict", json={"predicted_frontier": ["B", "C"]})
    assert prediction.status_code == 200
    assert prediction.json()["correct"] is True

    diagnosis = client.post(
        "/challenge/diagnose",
        json={"diagnosis": "late_frontier_recognition", "attempt": 1},
    )
    assert diagnosis.status_code == 200
    assert diagnosis.json()["accepted"] is True
    assert diagnosis.json()["stage"] == "confirm"

    repair = client.post("/challenge/repair", json={"repair_timing": "frontier_entry"})
    assert repair.status_code == 200
    assert repair.json()["tests_passed"] is True

    evidence = client.post(
        "/evidence",
        json={
            "prediction_correct": True,
            "invariant_preserved": True,
            "cycle_counterexample_passed": True,
            "repair_passed": True,
            "retry_scheduled": True,
        },
    )
    assert evidence.status_code == 200
    assert evidence.json()["status"] == "Demonstrated"


def test_diagnosis_escalates_without_leaking_a_repair() -> None:
    first = client.post("/challenge/diagnose", json={"diagnosis": "wrong_queue_order", "attempt": 1})
    second = client.post("/challenge/diagnose", json={"diagnosis": "wrong_queue_order", "attempt": 2})
    third = client.post("/challenge/diagnose", json={"diagnosis": "wrong_queue_order", "attempt": 3})
    assert first.json()["stage"] == "guide"
    assert second.json()["scaffold_level"] == 2
    assert third.json()["scaffold_level"] == 3
    assert "visited.add" not in third.json()["question"]


def test_confirmation_rejects_non_allowlisted_timing() -> None:
    response = client.post("/challenge/repair", json={"repair_timing": "traversal_end"})
    assert response.status_code == 400


def test_local_browser_origin_is_allowed_for_preflight() -> None:
    response = client.options(
        "/checkpoint",
        headers={
            "Origin": "http://127.0.0.1:3000",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:3000"


def test_only_approved_public_fixture_has_code_context_and_candidate() -> None:
    context = client.get("/code-context/public-graph-traversal")
    assert context.status_code == 200
    assert context.json()["files"][0]["symbols"] == ["bfs"]

    candidate = client.get("/challenge-candidates/public-graph-traversal")
    assert candidate.status_code == 200
    assert candidate.json()[0]["template_id"] == "TRAVERSAL-INVARIANT-02"

    rejected = client.get("/code-context/user-upload")
    assert rejected.status_code == 404
