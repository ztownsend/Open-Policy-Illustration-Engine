"""Decimal context and rounding helpers.

Rounding policy summary:
  - Money fields use quantize_money() → currency-specific quantum
    (USD/EUR = 0.01, BTC = 0.00000001).
  - Rate fields use quantize_rate() → 10 decimal places (RATE_QUANT).
  - Rounding mode is ROUND_HALF_UP everywhere.
  - Rounding points in the engine are documented in opie/core/engine.py
    above ledger-row construction.
"""

from __future__ import annotations

from decimal import Context, Decimal, ROUND_HALF_UP

from opie.core.currency import CurrencyCode, currency_quantum, normalize_currency_code

DECIMAL_CONTEXT = Context(prec=28, rounding=ROUND_HALF_UP, Emin=-999999, Emax=999999)
ROUNDING_MODE = ROUND_HALF_UP

RATE_QUANT = Decimal("0.0000000001")


def quantize_money(
    value: Decimal,
    currency_code: CurrencyCode | str = CurrencyCode.USD,
) -> Decimal:
    quant = currency_quantum(currency_code)
    return value.quantize(quant, rounding=ROUNDING_MODE, context=DECIMAL_CONTEXT)


def quantize_money_input(
    value: Decimal,
    currency_code: CurrencyCode | str,
    *,
    label: str | None = None,
) -> Decimal:
    normalized_code = normalize_currency_code(currency_code)
    if normalized_code == CurrencyCode.BTC:
        if value.as_tuple().exponent < -8:
            prefix = f"{label} " if label else ""
            raise ValueError(f"{prefix}must have at most 8 decimal places for BTC")
    return quantize_money(value, normalized_code)


def quantize_rate(value: Decimal) -> Decimal:
    return value.quantize(RATE_QUANT, rounding=ROUNDING_MODE, context=DECIMAL_CONTEXT)
