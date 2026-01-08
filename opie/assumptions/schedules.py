"""Surrender schedule parsing and expansion."""

from __future__ import annotations

from decimal import Decimal
from typing import Mapping

from opie.core.errors import AssumptionError


def expand_policy_year_schedule(
    schedule_by_year: Mapping[int, Decimal],
    *,
    duration_months: int | None = None,
) -> dict[int, Decimal]:
    expanded: dict[int, Decimal] = {}
    for year, charge in sorted(schedule_by_year.items()):
        if year < 1:
            raise AssumptionError("policy year must be >= 1", values={"policy_year": year})
        start_month = (year - 1) * 12 + 1
        end_month = year * 12
        for month in range(start_month, end_month + 1):
            if duration_months is not None and month > duration_months:
                break
            expanded[month] = charge
    return expanded


def normalize_month_schedule(schedule_by_month: Mapping[int, Decimal]) -> dict[int, Decimal]:
    normalized: dict[int, Decimal] = {}
    for month, charge in schedule_by_month.items():
        if month < 1:
            raise AssumptionError("month must be >= 1", values={"month": month})
        normalized[int(month)] = charge
    return normalized


def parse_surrender_schedule(
    schedule: Mapping[int, Decimal],
    *,
    mode: str = "month",
    duration_months: int | None = None,
) -> dict[int, Decimal]:
    if mode == "month":
        return normalize_month_schedule(schedule)
    if mode == "year":
        return expand_policy_year_schedule(schedule, duration_months=duration_months)
    raise AssumptionError("mode must be 'month' or 'year'", values={"mode": mode})
