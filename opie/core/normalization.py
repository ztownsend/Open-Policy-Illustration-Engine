"""Normalization helpers for monetary inputs."""

from __future__ import annotations

from decimal import Decimal
from typing import Mapping

from opie.assumptions.models import (
    AnnuityScenarioAssumptions,
    ScenarioAssumptions,
    TermScenarioAssumptions,
    ULScenarioAssumptions,
    WLScenarioAssumptions,
)
from opie.core.currency import CurrencyCode
from opie.core.money import quantize_money_input


def quantize_money_mapping(
    values: Mapping[int, Decimal],
    currency_code: CurrencyCode,
    *,
    label: str,
) -> dict[int, Decimal]:
    return {
        int(key): quantize_money_input(value, currency_code, label=f"{label}[{key}]")
        for key, value in values.items()
    }


def normalize_scenario_money(
    scenario: ScenarioAssumptions,
    currency_code: CurrencyCode,
) -> ScenarioAssumptions:
    if isinstance(scenario, ULScenarioAssumptions):
        return scenario.model_copy(
            update={
                "monthly_policy_fee": quantize_money_input(
                    scenario.monthly_policy_fee,
                    currency_code,
                    label="monthly_policy_fee",
                ),
                "monthly_per_thousand_admin_fee": quantize_money_input(
                    scenario.monthly_per_thousand_admin_fee,
                    currency_code,
                    label="monthly_per_thousand_admin_fee",
                ),
                "surrender_charge_schedule": quantize_money_mapping(
                    scenario.surrender_charge_schedule,
                    currency_code,
                    label="surrender_charge_schedule",
                ),
            }
        )

    if isinstance(scenario, TermScenarioAssumptions):
        updates: dict[str, Decimal | None] = {}
        if scenario.annual_premium is not None:
            updates["annual_premium"] = quantize_money_input(
                scenario.annual_premium,
                currency_code,
                label="annual_premium",
            )
        return scenario.model_copy(update=updates)

    if isinstance(scenario, WLScenarioAssumptions):
        return scenario.model_copy(
            update={
                "cash_value_schedule": quantize_money_mapping(
                    scenario.cash_value_schedule,
                    currency_code,
                    label="cash_value_schedule",
                ),
                "surrender_value_schedule": quantize_money_mapping(
                    scenario.surrender_value_schedule,
                    currency_code,
                    label="surrender_value_schedule",
                ),
            }
        )

    if isinstance(scenario, AnnuityScenarioAssumptions):
        return scenario.model_copy(
            update={
                "surrender_charge_schedule": quantize_money_mapping(
                    scenario.surrender_charge_schedule,
                    currency_code,
                    label="surrender_charge_schedule",
                )
            }
        )

    return scenario
