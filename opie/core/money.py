"""Decimal context and rounding helpers."""

from __future__ import annotations

from decimal import Context, Decimal, ROUND_HALF_UP

DECIMAL_CONTEXT = Context(prec=28, rounding=ROUND_HALF_UP, Emin=-999999, Emax=999999)
ROUNDING_MODE = ROUND_HALF_UP

MONEY_QUANT = Decimal("0.01")
RATE_QUANT = Decimal("0.0000000001")


def quantize_money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANT, rounding=ROUNDING_MODE, context=DECIMAL_CONTEXT)


def quantize_rate(value: Decimal) -> Decimal:
    return value.quantize(RATE_QUANT, rounding=ROUNDING_MODE, context=DECIMAL_CONTEXT)
