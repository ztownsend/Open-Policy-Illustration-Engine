"""Loading and normalization utilities for assumptions."""

from __future__ import annotations

from typing import Any

from opie.assumptions.models import (
    AnnuityScenarioAssumptions,
    ScenarioSet,
    TermScenarioAssumptions,
    ULScenarioAssumptions,
    WLScenarioAssumptions,
)
from opie.assumptions.schedules import parse_surrender_schedule
from opie.core.errors import AssumptionError


def load_ul_assumptions(
    data: dict[str, Any],
    *,
    schedule_mode: str = "month",
    duration_months: int | None = None,
) -> ULScenarioAssumptions:
    payload = dict(data)
    if "surrender_charge_schedule" in payload:
        raw_schedule = payload["surrender_charge_schedule"]
        if not isinstance(raw_schedule, dict):
            raise AssumptionError("surrender_charge_schedule must be an object mapping")
        schedule = {int(key): value for key, value in raw_schedule.items()}
        payload["surrender_charge_schedule"] = parse_surrender_schedule(
            schedule,
            mode=schedule_mode,
            duration_months=duration_months,
        )
    return ULScenarioAssumptions.model_validate(payload)


def load_term_assumptions(data: dict[str, Any]) -> TermScenarioAssumptions:
    return TermScenarioAssumptions.model_validate(data)


def load_wl_assumptions(data: dict[str, Any]) -> WLScenarioAssumptions:
    return WLScenarioAssumptions.model_validate(data)


def load_annuity_assumptions(data: dict[str, Any]) -> AnnuityScenarioAssumptions:
    payload = dict(data)
    if "surrender_charge_schedule" in payload:
        raw_schedule = payload["surrender_charge_schedule"]
        if not isinstance(raw_schedule, dict):
            raise AssumptionError("surrender_charge_schedule must be an object mapping")
        schedule = {int(key): value for key, value in raw_schedule.items()}
        payload["surrender_charge_schedule"] = parse_surrender_schedule(schedule)
    return AnnuityScenarioAssumptions.model_validate(payload)


def load_scenario_set(
    product_code: str,
    data: dict[str, Any],
    *,
    schedule_mode: str = "month",
    duration_months: int | None = None,
) -> ScenarioSet:
    if product_code == "simple_ul":
        current = load_ul_assumptions(
            data.get("current", {}),
            schedule_mode=schedule_mode,
            duration_months=duration_months,
        )
        guaranteed = load_ul_assumptions(
            data.get("guaranteed", {}),
            schedule_mode=schedule_mode,
            duration_months=duration_months,
        )
        return ScenarioSet(current=current, guaranteed=guaranteed)

    if product_code == "level_term":
        current = load_term_assumptions(data.get("current", {}))
        guaranteed = load_term_assumptions(data.get("guaranteed", {}))
        return ScenarioSet(current=current, guaranteed=guaranteed)

    if product_code == "wl_nonpar":
        current = load_wl_assumptions(data.get("current", {}))
        guaranteed = load_wl_assumptions(data.get("guaranteed", {}))
        return ScenarioSet(current=current, guaranteed=guaranteed)

    if product_code in {"annuity_deferred", "annuity_spia"}:
        current = load_annuity_assumptions(data.get("current", {}))
        guaranteed = load_annuity_assumptions(data.get("guaranteed", {}))
        return ScenarioSet(current=current, guaranteed=guaranteed)

    raise AssumptionError("Unsupported product_code", values={"product_code": product_code})
