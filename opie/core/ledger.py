"""Ledger serialization helpers with deterministic JSON output."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel


def _normalize_for_json(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, BaseModel):
        return _normalize_for_json(value.model_dump(mode="python"))
    if is_dataclass(value):
        return _normalize_for_json(asdict(value))
    if isinstance(value, dict):
        normalized = {}
        for key, val in value.items():
            if isinstance(key, Enum):
                key_str = key.value
            else:
                key_str = str(key)
            if key_str.startswith("debug_") and val is None:
                continue
            if key_str == "tax_7702_debug" and val is None:
                continue
            normalized[key_str] = _normalize_for_json(val)
        return normalized
    if isinstance(value, (list, tuple)):
        return [_normalize_for_json(item) for item in value]
    return value


def normalize_for_json(value: Any) -> Any:
    return _normalize_for_json(value)


def dumps_json(value: Any) -> str:
    normalized = _normalize_for_json(value)
    return json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
