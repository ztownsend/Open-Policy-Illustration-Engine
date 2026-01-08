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
from opie.core.currency import CurrencyCode
from opie.core.normalization import normalize_scenario_money
from opie.core.errors import AssumptionError


def load_ul_assumptions(
    data: dict[str, Any],
    *,
    schedule_mode: str = "month",
    duration_months: int | None = None,
    currency_code: CurrencyCode = CurrencyCode.USD,
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
    scenario = ULScenarioAssumptions.model_validate(payload)
    return normalize_scenario_money(scenario, currency_code)


def load_term_assumptions(
    data: dict[str, Any],
    *,
    currency_code: CurrencyCode = CurrencyCode.USD,
) -> TermScenarioAssumptions:
    scenario = TermScenarioAssumptions.model_validate(data)
    return normalize_scenario_money(scenario, currency_code)


def load_wl_assumptions(
    data: dict[str, Any],
    *,
    currency_code: CurrencyCode = CurrencyCode.USD,
) -> WLScenarioAssumptions:
    scenario = WLScenarioAssumptions.model_validate(data)
    return normalize_scenario_money(scenario, currency_code)


def load_annuity_assumptions(
    data: dict[str, Any],
    *,
    currency_code: CurrencyCode = CurrencyCode.USD,
) -> AnnuityScenarioAssumptions:
    payload = dict(data)
    if "surrender_charge_schedule" in payload:
        raw_schedule = payload["surrender_charge_schedule"]
        if not isinstance(raw_schedule, dict):
            raise AssumptionError("surrender_charge_schedule must be an object mapping")
        schedule = {int(key): value for key, value in raw_schedule.items()}
        payload["surrender_charge_schedule"] = parse_surrender_schedule(schedule)
    scenario = AnnuityScenarioAssumptions.model_validate(payload)
    return normalize_scenario_money(scenario, currency_code)


def load_scenario_set(
    product_code: str,
    data: dict[str, Any],
    *,
    schedule_mode: str = "month",
    duration_months: int | None = None,
    currency_code: CurrencyCode = CurrencyCode.USD,
) -> ScenarioSet:
    if product_code == "simple_ul":
        current = load_ul_assumptions(
            data.get("current", {}),
            schedule_mode=schedule_mode,
            duration_months=duration_months,
            currency_code=currency_code,
        )
        guaranteed = load_ul_assumptions(
            data.get("guaranteed", {}),
            schedule_mode=schedule_mode,
            duration_months=duration_months,
            currency_code=currency_code,
        )
        return ScenarioSet(current=current, guaranteed=guaranteed)

    if product_code == "level_term":
        current = load_term_assumptions(data.get("current", {}), currency_code=currency_code)
        guaranteed = load_term_assumptions(data.get("guaranteed", {}), currency_code=currency_code)
        return ScenarioSet(current=current, guaranteed=guaranteed)

    if product_code == "wl_nonpar":
        current = load_wl_assumptions(data.get("current", {}), currency_code=currency_code)
        guaranteed = load_wl_assumptions(data.get("guaranteed", {}), currency_code=currency_code)
        return ScenarioSet(current=current, guaranteed=guaranteed)

    if product_code in {"annuity_deferred", "annuity_spia"}:
        current = load_annuity_assumptions(
            data.get("current", {}), currency_code=currency_code
        )
        guaranteed = load_annuity_assumptions(
            data.get("guaranteed", {}), currency_code=currency_code
        )
        return ScenarioSet(current=current, guaranteed=guaranteed)

    raise AssumptionError("Unsupported product_code", values={"product_code": product_code})
