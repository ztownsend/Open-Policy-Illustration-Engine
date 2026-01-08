import json
from pathlib import Path

from fastapi.testclient import TestClient

from opie_ui.app import app


def test_ui_root_serves_html() -> None:
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "OPIE Explorer" in response.text


def test_ui_api_mount() -> None:
    client = TestClient(app)
    payload = json.loads(Path("examples/term_request.json").read_text())
    response = client.post("/api/v1/illustrations", json=payload)
    assert response.status_code == 200
