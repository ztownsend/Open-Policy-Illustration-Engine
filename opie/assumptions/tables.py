"""COI table loading and lookup utilities."""

from __future__ import annotations

import csv
import json
from decimal import Decimal
from pathlib import Path
from typing import Mapping

from opie.core.errors import AssumptionError
from opie.core.validation import parse_decimal


def load_coi_table_csv(path: str | Path) -> dict[int, Decimal]:
    path = Path(path)
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if (
            reader.fieldnames is None
            or "age" not in reader.fieldnames
            or "rate" not in reader.fieldnames
        ):
            raise AssumptionError("CSV must include age and rate columns")
        table: dict[int, Decimal] = {}
        for row in reader:
            age_raw = row.get("age")
            rate_raw = row.get("rate")
            if age_raw is None or rate_raw is None:
                raise AssumptionError("CSV rows must include age and rate")
            age = int(age_raw)
            table[age] = parse_decimal(rate_raw)
        return table


def load_coi_table_json(path: str | Path) -> dict[int, Decimal]:
    path = Path(path)
    data = json.loads(path.read_text())
    if not isinstance(data, Mapping):
        raise AssumptionError("COI JSON must be an object mapping age to rate")
    table: dict[int, Decimal] = {}
    for key, value in data.items():
        table[int(key)] = parse_decimal(value)
    return table


def coi_lookup(table: Mapping[int, Decimal], attained_age: int) -> Decimal:
    try:
        return table[attained_age]
    except KeyError as exc:
        raise AssumptionError("COI rate missing", values={"attained_age": attained_age}) from exc
