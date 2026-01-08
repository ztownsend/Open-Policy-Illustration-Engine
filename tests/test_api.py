import json
from pathlib import Path

from fastapi.testclient import TestClient

from opie.api.app import app


def test_api_smoke() -> None:
    payload = json.loads(Path("examples/term_request.json").read_text())
    client = TestClient(app)
    response = client.post("/v1/illustrations", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["product_code"] == "level_term"
    assert "metadata" in data
