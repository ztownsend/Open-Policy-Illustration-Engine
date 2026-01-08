from decimal import Decimal

from opie.conformance.compare import compare_payloads


def test_compare_payloads_detects_diffs() -> None:
    payload_a = {"ledger": {"rows": [{"t": 1, "premium": "10.00", "note": "a"}]}}
    payload_b = {"ledger": {"rows": [{"t": 1, "premium": "12.00", "note": "b"}]}}
    result = compare_payloads(payload_a, payload_b)
    assert result.first_diff is not None
    assert "t=1" in result.first_diff
    assert result.max_diff is not None
    assert result.max_diff.field == "premium"
    assert result.max_diff.delta == Decimal("2.00")


def test_compare_payloads_match() -> None:
    payload = {"ledger": {"rows": [{"t": 1, "premium": "10.00"}]}}
    result = compare_payloads(payload, payload)
    assert result.first_diff is None
    assert result.max_diff is None
