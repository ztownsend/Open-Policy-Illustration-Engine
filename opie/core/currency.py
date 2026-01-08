"""Currency codes and quantization rules."""

from __future__ import annotations

from decimal import Decimal
from enum import StrEnum
from typing import Final


class CurrencyCode(StrEnum):
    USD = "USD"
    EUR = "EUR"
    BTC = "BTC"


CURRENCY_QUANTA: Final[dict[CurrencyCode, Decimal]] = {
    CurrencyCode.USD: Decimal("0.01"),
    CurrencyCode.EUR: Decimal("0.01"),
    CurrencyCode.BTC: Decimal("0.00000001"),
}


def normalize_currency_code(code: CurrencyCode | str) -> CurrencyCode:
    try:
        return CurrencyCode(code)
    except ValueError as exc:
        raise ValueError(f"Unsupported currency_code: {code}") from exc


def currency_quantum(code: CurrencyCode | str) -> Decimal:
    normalized = normalize_currency_code(code)
    return CURRENCY_QUANTA[normalized]
