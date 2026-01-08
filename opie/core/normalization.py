"""Normalization helpers for monetary inputs."""

from __future__ import annotations

from decimal import Decimal
from typing import Mapping

from opie.assumptions.models import (
    AnnuityScenarioAssumptions,
    ScenarioAssumptions,
    Tax7702Assumptions,
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


def normalize_tax_7702(
    tax: Tax7702Assumptions,
    currency_code: CurrencyCode,
) -> Tax7702Assumptions:
    updates: dict[str, Decimal] = {}
    if tax.gpt_guideline_single_premium is not None:
        updates["gpt_guideline_single_premium"] = quantize_money_input(
            tax.gpt_guideline_single_premium,
            currency_code,
            label="tax_7702.gpt_guideline_single_premium",
        )
    if tax.gpt_guideline_level_premium_annual is not None:
        updates["gpt_guideline_level_premium_annual"] = quantize_money_input(
            tax.gpt_guideline_level_premium_annual,
            currency_code,
            label="tax_7702.gpt_guideline_level_premium_annual",
        )
    if tax.cvat_net_single_premium is not None:
        updates["cvat_net_single_premium"] = quantize_money_input(
            tax.cvat_net_single_premium,
            currency_code,
            label="tax_7702.cvat_net_single_premium",
        )
    if tax.cvat_cash_value_adjustment is not None:
        updates["cvat_cash_value_adjustment"] = quantize_money_input(
            tax.cvat_cash_value_adjustment,
            currency_code,
            label="tax_7702.cvat_cash_value_adjustment",
        )
    updates["tolerance"] = quantize_money_input(
        tax.tolerance, currency_code, label="tax_7702.tolerance"
    )
    if not updates:
        return tax
    return tax.model_copy(update=updates)


def _tax_update(
    scenario: ScenarioAssumptions,
    currency_code: CurrencyCode,
) -> dict[str, Tax7702Assumptions]:
    tax = getattr(scenario, "tax_7702", None)
    if tax is None:
        return {}
    return {"tax_7702": normalize_tax_7702(tax, currency_code)}


def normalize_scenario_money(
    scenario: ScenarioAssumptions,
    currency_code: CurrencyCode,
) -> ScenarioAssumptions:
    if isinstance(scenario, ULScenarioAssumptions):
        updates: dict[str, Decimal | dict[int, Decimal] | Tax7702Assumptions] = {
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
        updates.update(_tax_update(scenario, currency_code))
        return scenario.model_copy(update=updates)

    if isinstance(scenario, TermScenarioAssumptions):
        updates: dict[str, Decimal | None] = {}
        if scenario.annual_premium is not None:
            updates["annual_premium"] = quantize_money_input(
                scenario.annual_premium,
                currency_code,
                label="annual_premium",
            )
        updates.update(_tax_update(scenario, currency_code))
        return scenario.model_copy(update=updates)

    if isinstance(scenario, WLScenarioAssumptions):
        updates: dict[str, dict[int, Decimal] | Tax7702Assumptions] = {
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
        updates.update(_tax_update(scenario, currency_code))
        return scenario.model_copy(update=updates)

    if isinstance(scenario, AnnuityScenarioAssumptions):
        updates: dict[str, dict[int, Decimal] | Tax7702Assumptions] = {
            "surrender_charge_schedule": quantize_money_mapping(
                scenario.surrender_charge_schedule,
                currency_code,
                label="surrender_charge_schedule",
            )
        }
        updates.update(_tax_update(scenario, currency_code))
        return scenario.model_copy(update=updates)

    return scenario
