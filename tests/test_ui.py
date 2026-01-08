import json
from pathlib import Path

from fastapi.testclient import TestClient

from opie_ui.app import app


def test_ui_root_serves_html() -> None:
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "OPIE Explorer" in response.text


def test_ui_contains_controls() -> None:
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    html = response.text
    for token in (
        'id="downloadCsv"',
        'id="copyRequest"',
        'id="copyResult"',
        'id="colsCore"',
        'id="colsValue"',
        'id="colsCharges"',
        'id="colsLoans"',
        'id="colsAll"',
        'id="columns"',
        'value="diff"',
    ):
        assert token in html


def test_ui_includes_column_definitions() -> None:
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    html = response.text
    for token in (
        "account_value_mid_raw",
        "charges_total",
        "loan_balance",
        "withdrawal",
        "death_benefit",
    ):
        assert token in html


def test_ui_api_mount() -> None:
    client = TestClient(app)
    payload = json.loads(Path("examples/term_request.json").read_text())
    response = client.post("/api/v1/illustrations", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["product_code"] == "level_term"
    assert "metadata" in data
    assert "ledgers" in data
