import json
from pathlib import Path

import pytest

from opie.cli.diff import diff_ledgers, diff_within


def test_diff_ledgers_reports_first_difference(tmp_path: Path) -> None:
    a_path = tmp_path / "a.json"
    b_path = tmp_path / "b.json"

    payload_a = {"ledger": {"rows": [{"t": 1, "premium": "100"}, {"t": 2, "premium": "100"}]}}
    payload_b = {"ledger": {"rows": [{"t": 1, "premium": "100"}, {"t": 2, "premium": "120"}]}}

    a_path.write_text(json.dumps(payload_a))
    b_path.write_text(json.dumps(payload_b))

    message = diff_ledgers(a_path, b_path)
    assert "t=2" in message
    assert "premium" in message


def test_diff_within_scenarios(tmp_path: Path) -> None:
    result_path = tmp_path / "result.json"
    payload = {
        "ledgers": {
            "current": {"rows": [{"t": 1, "premium": "100"}, {"t": 2, "premium": "100"}]},
            "guaranteed": {"rows": [{"t": 1, "premium": "100"}, {"t": 2, "premium": "80"}]},
        }
    }
    result_path.write_text(json.dumps(payload))

    message = diff_within(result_path, "current", "guaranteed")
    assert "t=2" in message
    assert "premium" in message


def test_diff_within_no_differences(tmp_path: Path) -> None:
    result_path = tmp_path / "result.json"
    payload = {
        "ledgers": {
            "current": {"rows": [{"t": 1, "premium": "100"}]},
            "guaranteed": {"rows": [{"t": 1, "premium": "100"}]},
        }
    }
    result_path.write_text(json.dumps(payload))

    message = diff_within(result_path, "current", "guaranteed")
    assert message == "No differences found"


def test_diff_within_missing_scenario(tmp_path: Path) -> None:
    result_path = tmp_path / "result.json"
    payload = {"ledgers": {"current": {"rows": [{"t": 1}]}}}
    result_path.write_text(json.dumps(payload))

    with pytest.raises(ValueError, match="guaranteed"):
        diff_within(result_path, "current", "guaranteed")


def test_diff_within_currency(tmp_path: Path) -> None:
    result_path = tmp_path / "result.json"
    payload = {
        "ledgers": {
            "current": {"rows": [{"t": 1, "premium": "100"}]},
            "guaranteed": {"rows": [{"t": 1, "premium": "100"}]},
        },
        "ledgers_by_currency": {
            "EUR": {
                "current": {"rows": [{"t": 1, "premium": "91"}]},
                "guaranteed": {"rows": [{"t": 1, "premium": "85"}]},
            }
        },
    }
    result_path.write_text(json.dumps(payload))

    message = diff_within(result_path, "current", "guaranteed", currency="EUR")
    assert "t=1" in message
    assert "premium" in message


def test_diff_within_missing_currency(tmp_path: Path) -> None:
    result_path = tmp_path / "result.json"
    payload = {"ledgers": {"current": {"rows": []}}}
    result_path.write_text(json.dumps(payload))

    with pytest.raises(ValueError, match="GBP"):
        diff_within(result_path, "current", "guaranteed", currency="GBP")
