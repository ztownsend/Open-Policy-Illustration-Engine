"""Scenario assumption models for OPIE."""

from __future__ import annotations

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator

from opie.core.validation import DecimalInput


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Tax7702Assumptions(StrictBaseModel):
    enabled: bool = False
    test_type: Literal["gpt", "cvat", "both"] = "gpt"
    gpt_guideline_single_premium: DecimalInput | None = None
    gpt_guideline_level_premium_annual: DecimalInput | None = None
    gpt_premium_timing: Literal["bop", "eop"] = "bop"
    cvat_net_single_premium: DecimalInput | None = None
    cvat_cash_value_basis: Literal["csv", "av_eop", "custom"] = "csv"
    cvat_cash_value_adjustment: DecimalInput | None = None
    corridor_factors: dict[int, DecimalInput] | None = None
    tolerance: DecimalInput = Decimal("0")

    @model_validator(mode="after")
    def _validate_requirements(self) -> "Tax7702Assumptions":
        if not self.enabled:
            return self
        if self.test_type in {"gpt", "both"}:
            if (
                self.gpt_guideline_single_premium is None
                or self.gpt_guideline_level_premium_annual is None
            ):
                raise ValueError(
                    "gpt_guideline_single_premium and gpt_guideline_level_premium_annual are required"
                )
        if self.test_type in {"cvat", "both"} and self.cvat_net_single_premium is None:
            raise ValueError("cvat_net_single_premium is required")
        return self


class ULScenarioAssumptions(StrictBaseModel):
    crediting_rate_annual: DecimalInput
    premium_load_pct: DecimalInput
    monthly_policy_fee: DecimalInput
    monthly_per_thousand_admin_fee: DecimalInput = Decimal("0")
    coi_table: dict[int, DecimalInput]
    surrender_charge_schedule: dict[int, DecimalInput]
    interest_mode: Literal["nominal_div_12", "effective_monthly"] = "nominal_div_12"
    corridor_factors: dict[int, DecimalInput] | None = None
    tax_7702: Tax7702Assumptions | None = None


class TermScenarioAssumptions(StrictBaseModel):
    annual_premium: DecimalInput | None = None
    term_modal_factor: DecimalInput | None = None
    tax_7702: Tax7702Assumptions | None = None


class WLScenarioAssumptions(StrictBaseModel):
    cash_value_schedule: dict[int, DecimalInput]
    surrender_value_schedule: dict[int, DecimalInput]
    tax_7702: Tax7702Assumptions | None = None


class AnnuityScenarioAssumptions(StrictBaseModel):
    crediting_rate_annual: DecimalInput
    surrender_charge_schedule: dict[int, DecimalInput]
    spia_payout_factors: dict[int, DecimalInput] | None = None
    tax_7702: Tax7702Assumptions | None = None


ScenarioAssumptions = (
    ULScenarioAssumptions
    | TermScenarioAssumptions
    | WLScenarioAssumptions
    | AnnuityScenarioAssumptions
)


class ScenarioSet(StrictBaseModel):
    current: ScenarioAssumptions
    guaranteed: ScenarioAssumptions
