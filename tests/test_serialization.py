from decimal import Decimal

from opie.core.currency import CurrencyCode

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


def test_dumps_json_omits_null_debug_fields() -> None:
    payload = {"debug_alpha": None, "debug_beta": "1", "keep": 2}
    assert dumps_json(payload) == '{"debug_beta":"1","keep":2}'


def test_dumps_json_stringifies_enum_dict_keys() -> None:
    payload = {CurrencyCode.EUR: {"value": Decimal("1.00")}}
    assert dumps_json(payload) == '{"EUR":{"value":"1.00"}}'
