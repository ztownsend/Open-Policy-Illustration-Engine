"""Scenario assumption models for OPIE."""

from __future__ import annotations

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict

from opie.core.validation import DecimalInput


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ULScenarioAssumptions(StrictBaseModel):
    crediting_rate_annual: DecimalInput
    premium_load_pct: DecimalInput
    monthly_policy_fee: DecimalInput
    monthly_per_thousand_admin_fee: DecimalInput = Decimal("0")
    coi_table: dict[int, DecimalInput]
    surrender_charge_schedule: dict[int, DecimalInput]
    interest_mode: Literal["nominal_div_12", "effective_monthly"] = "nominal_div_12"
    corridor_factors: dict[int, DecimalInput] | None = None


class TermScenarioAssumptions(StrictBaseModel):
    annual_premium: DecimalInput | None = None
    term_modal_factor: DecimalInput | None = None


class WLScenarioAssumptions(StrictBaseModel):
    cash_value_schedule: dict[int, DecimalInput]
    surrender_value_schedule: dict[int, DecimalInput]


class AnnuityScenarioAssumptions(StrictBaseModel):
    crediting_rate_annual: DecimalInput
    surrender_charge_schedule: dict[int, DecimalInput]


ScenarioAssumptions = (
    ULScenarioAssumptions
    | TermScenarioAssumptions
    | WLScenarioAssumptions
    | AnnuityScenarioAssumptions
)


class ScenarioSet(StrictBaseModel):
    current: ScenarioAssumptions
    guaranteed: ScenarioAssumptions
