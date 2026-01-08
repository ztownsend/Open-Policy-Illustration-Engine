"""Rider registry for deterministic hook lookup."""

from __future__ import annotations

from opie.core.errors import EngineError
from opie.products.riders.examples import FlatMonthlyChargeRider

RIDER_REGISTRY = {
    "flat_charge": FlatMonthlyChargeRider(),
}


def get_rider_hook(rider_code: str):
    try:
        return RIDER_REGISTRY[rider_code]
    except KeyError as exc:
        raise EngineError("Unknown rider_code", values={"rider_code": rider_code}) from exc
