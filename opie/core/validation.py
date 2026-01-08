"""Shared validation helpers for Decimal parsing."""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Any

from pydantic import BeforeValidator


def parse_decimal(value: Any) -> Decimal:
    if value is None:
        raise ValueError("Decimal value is required")
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, str):
        return Decimal(value)
    if isinstance(value, float):
        raise ValueError("Float inputs are not allowed; pass decimals as strings")
    raise TypeError(f"Unsupported decimal type: {type(value)!r}")


DecimalInput = Annotated[Decimal, BeforeValidator(parse_decimal)]
