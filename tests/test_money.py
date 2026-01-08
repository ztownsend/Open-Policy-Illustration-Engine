from decimal import Decimal

from opie.core.money import quantize_money, quantize_rate


def test_quantize_money_half_up() -> None:
    assert quantize_money(Decimal("1.005")) == Decimal("1.01")
    assert quantize_money(Decimal("1.004")) == Decimal("1.00")
    assert quantize_money(Decimal("-1.005")) == Decimal("-1.01")


def test_quantize_rate_precision() -> None:
    assert quantize_rate(Decimal("0.12345678994")) == Decimal("0.1234567899")
    assert quantize_rate(Decimal("0.12345678995")) == Decimal("0.1234567900")
