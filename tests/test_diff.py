import json
from pathlib import Path

from opie.cli.diff import diff_ledgers


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
