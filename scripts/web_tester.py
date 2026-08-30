"""Local web page for manually trying Evidence Engine's MCP tools.

Replaces the raw terminal REPL (try_it_yourself.py) with a small local
web page: no challenge_token to copy-paste (kept server-side in memory
between calls, the same way a real ChatGPT/Codex session would carry it
across turns), no raw tool docstrings dumped to the screen, no EOF
markers for multi-line text -- just buttons and textareas.

This is a dev/QA convenience tool, not the product. The real product
surface is inside ChatGPT/Codex (docs/VISION.md); this exists only
because that connection isn't available yet (docs/IMPLEMENTATION_PLAN.md
Phase 1, spikes 1/2) and a terminal REPL was a worse way to check things
by hand in the meantime.

Run it via apps/api's own uv-managed environment:

    cd apps/api && uv run python3 ../../scripts/web_tester.py

Then open http://localhost:8791 in a browser.
"""

from __future__ import annotations

import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "apps" / "api"
PORT = 8791

# Server-side session state -- this is exactly what a real ChatGPT/Codex
# session would hold in its own conversation context between turns. A
# human using the web page never sees or handles it.
_session: ClientSession | None = None
_challenge_token: str | None = None
_default_workspace_id = "web-session"


async def _call(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    assert _session is not None, "MCP session not started"
    result = await _session.call_tool(tool_name, arguments)
    if result.is_error:
        message = "Tool error"
        for block in result.content:
            text = getattr(block, "text", None)
            if text:
                message = text
                break
        return {"error": message}
    payload_text = result.content[0].text  # type: ignore[union-attr]
    payload: dict[str, Any] = json.loads(payload_text)
    return payload


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    global _session
    server = StdioServerParameters(
        command="uv",
        args=["run", "python3", "-m", "app.mcp_server"],
        cwd=str(API_DIR),
    )
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            _session = session
            yield
    _session = None


app = FastAPI(lifespan=_lifespan)


class StartChallengeBody(BaseModel):
    topic: str


class PredictBody(BaseModel):
    predicted_frontier: list[str]


class DiagnoseBody(BaseModel):
    diagnosis: str
    attempt: int


class RepairBody(BaseModel):
    repair_source: str


class MaterialBody(BaseModel):
    filename: str
    text: str


class RemoveMaterialBody(BaseModel):
    filename: str


class AskBody(BaseModel):
    question: str


@app.post("/api/start_challenge")
async def start_challenge(body: StartChallengeBody) -> JSONResponse:
    global _challenge_token
    result = await _call("start_challenge", {"topic": body.topic})
    if "challenge_token" in result:
        _challenge_token = result["challenge_token"]
    return JSONResponse(
        {
            "objective": result.get("objective"),
            "start_node": result.get("start_node"),
            "expected_first_frontier": result.get("expected_first_frontier"),
            "error": result.get("error"),
            "have_token": _challenge_token is not None,
        }
    )


@app.post("/api/predict")
async def predict(body: PredictBody) -> JSONResponse:
    if _challenge_token is None:
        return JSONResponse({"error": "Start a challenge first."})
    result = await _call(
        "submit_prediction",
        {"challenge_token": _challenge_token, "predicted_frontier": body.predicted_frontier},
    )
    return JSONResponse(result)


@app.post("/api/diagnose")
async def diagnose(body: DiagnoseBody) -> JSONResponse:
    if _challenge_token is None:
        return JSONResponse({"error": "Start a challenge first."})
    result = await _call(
        "submit_diagnosis",
        {"challenge_token": _challenge_token, "diagnosis": body.diagnosis, "attempt": body.attempt},
    )
    return JSONResponse(result)


@app.post("/api/repair")
async def repair(body: RepairBody) -> JSONResponse:
    if _challenge_token is None:
        return JSONResponse({"error": "Start a challenge first."})
    result = await _call(
        "submit_repair", {"challenge_token": _challenge_token, "repair_source": body.repair_source}
    )
    return JSONResponse(result)


@app.post("/api/add_material")
async def add_material(body: MaterialBody) -> JSONResponse:
    result = await _call(
        "add_course_material",
        {"workspace_id": _default_workspace_id, "filename": body.filename, "text": body.text},
    )
    return JSONResponse(result)


@app.get("/api/list_materials")
async def list_materials() -> JSONResponse:
    result = await _call("list_workspace_materials", {"workspace_id": _default_workspace_id})
    return JSONResponse(result)


@app.post("/api/remove_material")
async def remove_material(body: RemoveMaterialBody) -> JSONResponse:
    result = await _call(
        "remove_material", {"workspace_id": _default_workspace_id, "filename": body.filename}
    )
    return JSONResponse(result)


@app.post("/api/ask")
async def ask(body: AskBody) -> JSONResponse:
    result = await _call("answer_from_materials", {"workspace_id": _default_workspace_id, "question": body.question})
    return JSONResponse(result)


_PAGE = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Evidence Engine -- try it</title>
<style>
  body { font-family: -apple-system, sans-serif; max-width: 720px; margin: 40px auto; padding: 0 16px; color: #1a1a1a; }
  h1 { font-size: 20px; }
  h2 { font-size: 15px; margin-top: 36px; border-bottom: 1px solid #ddd; padding-bottom: 6px; }
  p.note { color: #666; font-size: 13px; }
  label { display: block; margin-top: 10px; font-size: 13px; font-weight: 600; }
  input[type=text], textarea { width: 100%; box-sizing: border-box; padding: 8px; font-family: inherit; font-size: 14px; border: 1px solid #ccc; border-radius: 4px; }
  textarea { font-family: ui-monospace, monospace; min-height: 100px; }
  button { margin-top: 10px; padding: 8px 16px; font-size: 14px; border: none; border-radius: 4px; background: #2563eb; color: white; cursor: pointer; }
  button:hover { background: #1d4ed8; }
  .result { margin-top: 10px; padding: 10px; border-radius: 4px; font-size: 14px; white-space: pre-wrap; }
  .result.ok { background: #ecfdf5; border: 1px solid #a7f3d0; }
  .result.err { background: #fef2f2; border: 1px solid #fecaca; }
  .section { padding: 12px 16px; border: 1px solid #e5e5e5; border-radius: 8px; margin-top: 8px; }
</style>
</head>
<body>
<h1>Evidence Engine -- try it yourself</h1>
<p class="note">This is a local dev/QA convenience page, not the real product -- Evidence Engine's actual home is inside a ChatGPT or Codex conversation (see docs/VISION.md). No token to manage here; it's kept server-side, the same way a real chat session would hold it.</p>

<h2>Code-repair practice</h2>
<div class="section">
  <label>Topic</label>
  <input type="text" id="topic" value="graph traversal">
  <button onclick="startChallenge()">Start challenge</button>
  <div id="challenge-result"></div>

  <label>Predicted frontier (comma-separated)</label>
  <input type="text" id="prediction" value="B, C">
  <button onclick="predict()">Submit prediction</button>
  <div id="predict-result"></div>

  <label>Diagnosis</label>
  <textarea id="diagnosis">the traversal marks nodes visited when dequeued instead of enqueued, so a node can enter the frontier twice</textarea>
  <label>Attempt number</label>
  <input type="text" id="attempt" value="1">
  <button onclick="diagnose()">Submit diagnosis</button>
  <div id="diagnose-result"></div>

  <label>Repair source</label>
  <textarea id="repair" style="min-height:180px">from collections import deque


def bfs(graph, start):
    frontier = deque([start])
    visited = {start}
    order = []
    while frontier:
        node = frontier.popleft()
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                frontier.append(neighbor)
    return order</textarea>
  <button onclick="repair()">Submit repair</button>
  <div id="repair-result"></div>
</div>

<h2>Study workspace</h2>
<div class="section">
  <label>Filename</label>
  <input type="text" id="filename" value="notes.txt">
  <label>Material text</label>
  <textarea id="material-text">Breadth-first search marks nodes visited when they enter the frontier.</textarea>
  <button onclick="addMaterial()">Add material</button>
  <div id="material-result"></div>

  <button onclick="listMaterials()">List materials</button>
  <div id="list-result"></div>

  <label>Remove filename</label>
  <input type="text" id="remove-filename" value="notes.txt">
  <button onclick="removeMaterial()">Remove material</button>
  <div id="remove-result"></div>

  <label>Question</label>
  <input type="text" id="question" value="when are nodes marked visited?">
  <button onclick="ask()">Ask</button>
  <div id="ask-result"></div>
</div>

<script>
async function post(url, body) {
  const res = await fetch(url, { method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body || {}) });
  return res.json();
}
async function get(url) {
  const res = await fetch(url);
  return res.json();
}
function show(id, data) {
  const el = document.getElementById(id);
  const isErr = !!data.error;
  el.className = "result " + (isErr ? "err" : "ok");
  el.textContent = JSON.stringify(data, null, 2);
}
async function startChallenge() {
  const topic = document.getElementById("topic").value;
  show("challenge-result", await post("/api/start_challenge", { topic }));
}
async function predict() {
  const predicted_frontier = document.getElementById("prediction").value.split(",").map(s => s.trim());
  show("predict-result", await post("/api/predict", { predicted_frontier }));
}
async function diagnose() {
  const diagnosis = document.getElementById("diagnosis").value;
  const attempt = parseInt(document.getElementById("attempt").value, 10);
  show("diagnose-result", await post("/api/diagnose", { diagnosis, attempt }));
}
async function repair() {
  const repair_source = document.getElementById("repair").value;
  show("repair-result", await post("/api/repair", { repair_source }));
}
async function addMaterial() {
  const filename = document.getElementById("filename").value;
  const text = document.getElementById("material-text").value;
  show("material-result", await post("/api/add_material", { filename, text }));
}
async function listMaterials() {
  show("list-result", await get("/api/list_materials"));
}
async function removeMaterial() {
  const filename = document.getElementById("remove-filename").value;
  show("remove-result", await post("/api/remove_material", { filename }));
}
async function ask() {
  const question = document.getElementById("question").value;
  show("ask-result", await post("/api/ask", { question }));
}
</script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return _PAGE


def main() -> None:
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")


if __name__ == "__main__":
    main()
