"""Ledger diff tooling."""

from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


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


def diff_within(
    path: Path,
    scenario_a: str = "current",
    scenario_b: str = "guaranteed",
    currency: str | None = None,
) -> str:
    """Diff two scenarios within a single result file."""
    payload = _load_json(path)
    if currency is not None:
        lbc = payload.get("ledgers_by_currency")
        if lbc is None or currency not in lbc:
            raise ValueError(f"No ledgers_by_currency for currency '{currency}'")
        container = lbc[currency]
    else:
        container = payload.get("ledgers")
        if container is None:
            raise ValueError("payload must include ledgers")
    if scenario_a not in container:
        raise ValueError(f"Scenario '{scenario_a}' not found in result")
    if scenario_b not in container:
        raise ValueError(f"Scenario '{scenario_b}' not found in result")
    ledger_a = container[scenario_a]
    ledger_b = container[scenario_b]
    return _diff_rows(ledger_a, ledger_b)


def diff_ledgers(path_a: Path, path_b: Path, scenario: str | None = None) -> str:
    payload_a = _load_json(path_a)
    payload_b = _load_json(path_b)
    ledger_a = _extract_ledger(payload_a, scenario)
    ledger_b = _extract_ledger(payload_b, scenario)
    return _diff_rows(ledger_a, ledger_b)


def _diff_rows(ledger_a: dict[str, Any], ledger_b: dict[str, Any]) -> str:
    rows_a = ledger_a.get("rows", [])
    rows_b = ledger_b.get("rows", [])
    max_len = max(len(rows_a), len(rows_b))

    for index in range(max_len):
        if index >= len(rows_a):
            return f"Row missing in A at t={index + 1}"
        if index >= len(rows_b):
            return f"Row missing in B at t={index + 1}"
        row_a = rows_a[index]
        row_b = rows_b[index]
        keys = sorted(set(row_a.keys()) | set(row_b.keys()))
        for key in keys:
            val_a = row_a.get(key)
            val_b = row_b.get(key)
            if val_a != val_b:
                delta = ""
                dec_a = _to_decimal(val_a)
                dec_b = _to_decimal(val_b)
                if dec_a is not None and dec_b is not None:
                    delta = f" (delta={dec_b - dec_a})"
                return f"First diff at t={index + 1} field={key}: {val_a} vs {val_b}{delta}"
    return "No differences found"
