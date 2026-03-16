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


class IndexAccount(StrictBaseModel):
    """A single account within an IUL policy."""

    name: str
    allocation: DecimalInput
    strategy_type: Literal["fixed", "point_to_point", "monthly_average"]
    # Fixed account params
    fixed_rate: DecimalInput | None = None
    # Indexed account params
    illustrated_rate: DecimalInput | None = None
    cap: DecimalInput | None = None
    floor: DecimalInput | None = None
    participation: DecimalInput | None = None

    @model_validator(mode="after")
    def _validate_strategy_params(self) -> "IndexAccount":
        if self.strategy_type == "fixed":
            if self.fixed_rate is None:
                raise ValueError("fixed_rate is required for fixed strategy")
        else:
            if self.illustrated_rate is None:
                raise ValueError("illustrated_rate is required for indexed strategies")
            if self.cap is None:
                raise ValueError("cap is required for indexed strategies")
            if self.floor is None:
                raise ValueError("floor is required for indexed strategies")
            if self.participation is None:
                raise ValueError("participation is required for indexed strategies")
            if self.cap < self.floor:
                raise ValueError("cap must be >= floor")
            if self.participation <= Decimal("0"):
                raise ValueError("participation must be > 0")
        return self


class IULScenarioAssumptions(ULScenarioAssumptions):
    """IUL extends UL assumptions with index account definitions.

    crediting_rate_annual is inherited but ignored — IUL uses per-account
    rates from index_accounts instead. Set to 0 in requests.
    """

    index_accounts: list[IndexAccount]

    @model_validator(mode="after")
    def _validate_allocations(self) -> "IULScenarioAssumptions":
        if not self.index_accounts:
            raise ValueError("index_accounts must not be empty")
        total = sum(a.allocation for a in self.index_accounts)
        if total != Decimal("1"):
            raise ValueError(f"index_accounts allocations must sum to 1.0, got {total}")
        return self


class AnnuityScenarioAssumptions(StrictBaseModel):
    crediting_rate_annual: DecimalInput
    surrender_charge_schedule: dict[int, DecimalInput]
    spia_payout_factors: dict[int, DecimalInput] | None = None
    tax_7702: Tax7702Assumptions | None = None


ScenarioAssumptions = (
    ULScenarioAssumptions
    | TermScenarioAssumptions
    | WLScenarioAssumptions
    | IULScenarioAssumptions
    | AnnuityScenarioAssumptions
)


class ScenarioSet(StrictBaseModel):
    current: ScenarioAssumptions
    guaranteed: ScenarioAssumptions
