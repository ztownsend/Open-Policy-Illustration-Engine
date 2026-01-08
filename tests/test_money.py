from decimal import Decimal

import pytest

from opie.core.currency import CurrencyCode
from opie.core.money import quantize_money, quantize_money_input, quantize_rate


def test_quantize_money_half_up_usd_default() -> None:
    assert quantize_money(Decimal("1.005")) == Decimal("1.01")
    assert quantize_money(Decimal("1.004")) == Decimal("1.00")
    assert quantize_money(Decimal("-1.005")) == Decimal("-1.01")


def test_quantize_money_half_up_eur() -> None:
    assert quantize_money(Decimal("1.005"), CurrencyCode.EUR) == Decimal("1.01")
    assert quantize_money(Decimal("1.004"), CurrencyCode.EUR) == Decimal("1.00")


def test_quantize_money_half_up_btc() -> None:
    assert quantize_money(Decimal("0.000000005"), CurrencyCode.BTC) == Decimal("0.00000001")
    assert quantize_money(Decimal("0.000000004"), CurrencyCode.BTC) == Decimal("0.00000000")


def test_quantize_money_rejects_unknown_currency() -> None:
    with pytest.raises(ValueError):
        quantize_money(Decimal("1"), "DOGE")


def test_quantize_money_input_allows_btc_precision() -> None:
    assert quantize_money_input(Decimal("0.00000001"), CurrencyCode.BTC) == Decimal(
        "0.00000001"
    )


def test_quantize_money_input_rejects_btc_over_precision() -> None:
    with pytest.raises(ValueError):
        quantize_money_input(Decimal("0.000000001"), CurrencyCode.BTC)


def test_quantize_rate_precision() -> None:
    assert quantize_rate(Decimal("0.12345678994")) == Decimal("0.1234567899")
    assert quantize_rate(Decimal("0.12345678995")) == Decimal("0.1234567900")
