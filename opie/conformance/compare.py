"""Comparison helpers for cross-engine diffs."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class MaxDiff:
    t: int
    field: str
    value_a: Any
    value_b: Any
    delta: Decimal


@dataclass(frozen=True)
class ComparisonResult:
    first_diff: str | None
    max_diff: MaxDiff | None


def _to_decimal(value: Any) -> Decimal | None:
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, str):
        try:
            return Decimal(value)
        except InvalidOperation:
            return None
    return None


def _extract_ledger(payload: dict[str, Any], scenario: str | None) -> dict[str, Any]:
    if "ledger" in payload:
        return payload["ledger"]
    if "ledgers" in payload:
        ledgers = payload["ledgers"]
        if scenario is None:
            if len(ledgers) == 1:
                return next(iter(ledgers.values()))
            raise ValueError("scenario must be provided when multiple ledgers are present")
        return ledgers[scenario]
    raise ValueError("payload must include ledger or ledgers")


def compare_payloads(
    payload_a: dict[str, Any],
    payload_b: dict[str, Any],
    *,
    scenario: str | None = None,
) -> ComparisonResult:
    ledger_a = _extract_ledger(payload_a, scenario)
    ledger_b = _extract_ledger(payload_b, scenario)
    rows_a = ledger_a.get("rows", [])
    rows_b = ledger_b.get("rows", [])

    max_len = max(len(rows_a), len(rows_b))
    first_diff: str | None = None
    max_delta: Decimal | None = None
    max_diff: MaxDiff | None = None

    for index in range(max_len):
        if index >= len(rows_a):
            first_diff = first_diff or f"Row missing in A at t={index + 1}"
            break
        if index >= len(rows_b):
            first_diff = first_diff or f"Row missing in B at t={index + 1}"
            break
        row_a = rows_a[index]
        row_b = rows_b[index]
        keys = sorted(set(row_a.keys()) | set(row_b.keys()))
        for key in keys:
            val_a = row_a.get(key)
            val_b = row_b.get(key)
            if val_a != val_b and first_diff is None:
                delta = ""
                dec_a = _to_decimal(val_a)
                dec_b = _to_decimal(val_b)
                if dec_a is not None and dec_b is not None:
                    delta = f" (delta={dec_b - dec_a})"
                first_diff = f"First diff at t={index + 1} field={key}: {val_a} vs {val_b}{delta}"

            dec_a = _to_decimal(val_a)
            dec_b = _to_decimal(val_b)
            if dec_a is None or dec_b is None or dec_a == dec_b:
                continue
            delta_val = dec_b - dec_a
            abs_delta = delta_val.copy_abs()
            if max_delta is None or abs_delta > max_delta:
                max_delta = abs_delta
                max_diff = MaxDiff(
                    t=index + 1,
                    field=key,
                    value_a=val_a,
                    value_b=val_b,
                    delta=delta_val,
                )

    return ComparisonResult(first_diff=first_diff, max_diff=max_diff)


def compare_files(
    path_a: Path,
    path_b: Path,
    *,
    scenario: str | None = None,
) -> ComparisonResult:
    payload_a = json.loads(path_a.read_text())
    payload_b = json.loads(path_b.read_text())
    return compare_payloads(payload_a, payload_b, scenario=scenario)
