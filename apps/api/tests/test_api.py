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
    checkpoint = client.post("/checkpoint", json={"policy_mode": "bounded_snippets", "plan": PLAN})
    assert checkpoint.status_code == 200
    assert checkpoint.json()["card"]["snippet"] is not None

    prediction = client.post("/challenge/predict", json={"predicted_frontier": ["B", "C"]})
    assert prediction.status_code == 200
    assert prediction.json()["correct"] is True

    repair = client.post("/challenge/repair", json={"repair_id": "mark_visited_on_enqueue"})
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


def test_repair_rejects_non_allowlisted_input() -> None:
    response = client.post("/challenge/repair", json={"repair_id": "arbitrary-code"})
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
