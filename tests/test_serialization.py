from decimal import Decimal

from opie.core.ledger import dumps_json


def test_dumps_json_is_stable_and_stringifies_decimals() -> None:
    payload = {
        "b": Decimal("1.00"),
        "a": {"d": Decimal("2"), "c": 1},
    }
    assert dumps_json(payload) == '{"a":{"c":1,"d":"2"},"b":"1.00"}'


def test_dumps_json_deterministic() -> None:
    payload = {"x": [Decimal("0.10"), Decimal("0.20")], "y": "ok"}
    first = dumps_json(payload)
    second = dumps_json(payload)
    assert first == second
