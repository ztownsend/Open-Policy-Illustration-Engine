"""Pydantic models for OPIE request/response structures."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from opie.assumptions.models import (
    AnnuityScenarioAssumptions,
    ScenarioSet,
    TermScenarioAssumptions,
    ULScenarioAssumptions,
    WLScenarioAssumptions,
)
from opie.core.currency import CurrencyCode
from opie.core.money import quantize_money_input
from opie.core.normalization import normalize_scenario_money, quantize_money_mapping
from opie.core.validation import DecimalInput
from .versioning import CALC_VERSION, ROUNDING_POLICY_ID, SCHEMA_VERSION


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class IssueGender(StrEnum):
    M = "M"
    F = "F"


class PolicyStatus(StrEnum):
    IN_FORCE = "in_force"
    LAPSED = "lapsed"
    EXPIRED = "expired"


class PremiumScheduleEntry(StrictBaseModel):
    month: int | None = None
    start_month: int | None = None
    end_month: int | None = None
    amount: DecimalInput

    @model_validator(mode="after")
    def _validate_shape(self) -> "PremiumScheduleEntry":
        if self.month is not None:
            if self.start_month is not None or self.end_month is not None:
                raise ValueError("Use either month or start/end month, not both")
            if self.month < 1:
                raise ValueError("month must be >= 1")
            return self
        if self.start_month is None or self.end_month is None:
            raise ValueError("start_month and end_month are required for range entries")
        if self.start_month < 1 or self.end_month < 1:
            raise ValueError("start_month and end_month must be >= 1")
        if self.end_month < self.start_month:
            raise ValueError("end_month must be >= start_month")
        return self


class RiderSpec(StrictBaseModel):
    rider_code: str
    amount: DecimalInput


class SolveConfig(StrictBaseModel):
    mode: Literal["keep_in_force", "target_av"]
    target_month: int
    target_av: DecimalInput | None = None
    min_premium: DecimalInput = Decimal("0")
    max_premium: DecimalInput = Decimal("10000")
    iterations: int = 32
    tolerance: DecimalInput = Decimal("0.01")
    strategy: Literal["current_only", "per_scenario"] = "current_only"

    @field_validator("target_month")
    @classmethod
    def _validate_target_month(cls, value: int) -> int:
        if value < 1:
            raise ValueError("target_month must be >= 1")
        return value

    @field_validator("iterations")
    @classmethod
    def _validate_iterations(cls, value: int) -> int:
        if value < 1:
            raise ValueError("iterations must be >= 1")
        return value

    @model_validator(mode="after")
    def _validate_mode(self) -> "SolveConfig":
        if self.mode == "target_av" and self.target_av is None:
            raise ValueError("target_av is required for target_av mode")
        if self.mode == "keep_in_force" and self.target_av is not None:
            raise ValueError("target_av must be omitted for keep_in_force mode")
        if self.min_premium > self.max_premium:
            raise ValueError("min_premium must be <= max_premium")
        return self


class IllustrationRequest(StrictBaseModel):
    product_code: Literal[
        "simple_ul", "level_term", "wl_nonpar", "annuity_deferred", "annuity_spia"
    ]
    currency_code: CurrencyCode = CurrencyCode.USD
    reporting_currencies: list[CurrencyCode] | None = None
    fx_rates: dict[CurrencyCode, DecimalInput] | None = None
    reporting_include_debug_fields: bool = False
    issue_age: int
    issue_gender: IssueGender
    risk_class: str
    face_amount: DecimalInput
    issue_date: date
    duration_months: int
    premium_schedule: list[PremiumScheduleEntry] | None = None
    scenarios: ScenarioSet
    debug: bool = False
    grace_months: int = 0
    solve: SolveConfig | None = None
    withdrawal_schedule: dict[int, DecimalInput] | None = None
    loan_draw_schedule: dict[int, DecimalInput] | None = None
    loan_repayment_schedule: dict[int, DecimalInput] | None = None
    loan_interest_rate_annual: DecimalInput | None = Decimal("0")
    riders: list[RiderSpec] | None = None

    # UL-specific
    death_benefit_option: Literal["level", "increasing"] | None = "level"
    minimum_account_value_floor: DecimalInput | None = Decimal("0")

    # Term-specific
    term_length_months: int | None = None
    modal_factor: DecimalInput | None = None

    @field_validator("issue_age", "duration_months")
    @classmethod
    def _validate_positive_ints(cls, value: int) -> int:
        if value < 1:
            raise ValueError("value must be >= 1")
        return value

    @field_validator("grace_months")
    @classmethod
    def _validate_grace_months(cls, value: int) -> int:
        if value < 0:
            raise ValueError("grace_months must be >= 0")
        return value

    @model_validator(mode="after")
    def _validate_by_product(self) -> "IllustrationRequest":
        if self.product_code == "simple_ul":
            if self.term_length_months is not None:
                raise ValueError("term_length_months is not valid for simple_ul")
            if self.premium_schedule is None or len(self.premium_schedule) == 0:
                raise ValueError("premium_schedule is required for simple_ul")
            if not isinstance(self.scenarios.current, ULScenarioAssumptions) or not isinstance(
                self.scenarios.guaranteed, ULScenarioAssumptions
            ):
                raise ValueError("UL scenarios are required for simple_ul")
            return self

        if self.product_code == "level_term":
            if self.death_benefit_option is not None and self.death_benefit_option != "level":
                raise ValueError("death_benefit_option is not valid for level_term")
            if self.term_length_months is None:
                raise ValueError("term_length_months is required for level_term")
            if not isinstance(self.scenarios.current, TermScenarioAssumptions) or not isinstance(
                self.scenarios.guaranteed, TermScenarioAssumptions
            ):
                raise ValueError("Term scenarios are required for level_term")
            if self.premium_schedule is None:
                if (
                    self.scenarios.current.annual_premium is None
                    or self.scenarios.guaranteed.annual_premium is None
                ):
                    raise ValueError("annual_premium is required when premium_schedule is absent")
            return self

        if self.product_code == "wl_nonpar":
            if self.death_benefit_option is not None and self.death_benefit_option != "level":
                raise ValueError("death_benefit_option is not valid for wl_nonpar")
            if self.term_length_months is not None:
                raise ValueError("term_length_months is not valid for wl_nonpar")
            if not isinstance(self.scenarios.current, WLScenarioAssumptions) or not isinstance(
                self.scenarios.guaranteed, WLScenarioAssumptions
            ):
                raise ValueError("WL scenarios are required for wl_nonpar")
            return self

        if self.product_code in {"annuity_deferred", "annuity_spia"}:
            if self.death_benefit_option is not None and self.death_benefit_option != "level":
                raise ValueError("death_benefit_option is not valid for annuity products")
            if self.term_length_months is not None:
                raise ValueError("term_length_months is not valid for annuity products")
            if not isinstance(self.scenarios.current, AnnuityScenarioAssumptions) or not isinstance(
                self.scenarios.guaranteed, AnnuityScenarioAssumptions
            ):
                raise ValueError("Annuity scenarios are required for annuity products")
            return self

        raise ValueError("Unsupported product_code")

    @model_validator(mode="after")
    def _validate_reporting_currencies(self) -> "IllustrationRequest":
        if not self.reporting_currencies:
            return self

        if self.fx_rates is None:
            raise ValueError("fx_rates is required when reporting_currencies is provided")

        unique_currencies = list(dict.fromkeys(self.reporting_currencies))
        if len(unique_currencies) != len(self.reporting_currencies):
            self.reporting_currencies = unique_currencies

        missing = [
            currency for currency in self.reporting_currencies if currency not in self.fx_rates
        ]
        if missing:
            missing_codes = ", ".join([code.value for code in missing])
            raise ValueError(f"fx_rates missing for reporting currencies: {missing_codes}")
        return self

    @model_validator(mode="after")
    def _normalize_monetary_inputs(self) -> "IllustrationRequest":
        currency_code = self.currency_code

        self.face_amount = quantize_money_input(
            self.face_amount, currency_code, label="face_amount"
        )

        if self.premium_schedule:
            normalized_schedule = []
            for entry in self.premium_schedule:
                if entry.month is not None:
                    label = f"premium_schedule[{entry.month}].amount"
                elif entry.start_month is not None and entry.end_month is not None:
                    label = f"premium_schedule[{entry.start_month}-{entry.end_month}].amount"
                else:
                    label = "premium_schedule.amount"
                normalized_schedule.append(
                    entry.model_copy(
                        update={
                            "amount": quantize_money_input(entry.amount, currency_code, label=label)
                        }
                    )
                )
            self.premium_schedule = normalized_schedule

        if self.withdrawal_schedule:
            self.withdrawal_schedule = quantize_money_mapping(
                self.withdrawal_schedule,
                currency_code,
                label="withdrawal_schedule",
            )
        if self.loan_draw_schedule:
            self.loan_draw_schedule = quantize_money_mapping(
                self.loan_draw_schedule,
                currency_code,
                label="loan_draw_schedule",
            )
        if self.loan_repayment_schedule:
            self.loan_repayment_schedule = quantize_money_mapping(
                self.loan_repayment_schedule,
                currency_code,
                label="loan_repayment_schedule",
            )

        if self.minimum_account_value_floor is not None:
            self.minimum_account_value_floor = quantize_money_input(
                self.minimum_account_value_floor,
                currency_code,
                label="minimum_account_value_floor",
            )

        if self.riders:
            self.riders = [
                rider.model_copy(
                    update={
                        "amount": quantize_money_input(
                            rider.amount,
                            currency_code,
                            label=f"riders[{rider.rider_code}].amount",
                        )
                    }
                )
                for rider in self.riders
            ]

        if self.solve is not None:
            solve_updates = {
                "min_premium": quantize_money_input(
                    self.solve.min_premium, currency_code, label="solve.min_premium"
                ),
                "max_premium": quantize_money_input(
                    self.solve.max_premium, currency_code, label="solve.max_premium"
                ),
                "tolerance": quantize_money_input(
                    self.solve.tolerance, currency_code, label="solve.tolerance"
                ),
            }
            if self.solve.target_av is not None:
                solve_updates["target_av"] = quantize_money_input(
                    self.solve.target_av, currency_code, label="solve.target_av"
                )
            self.solve = self.solve.model_copy(update=solve_updates)

        self.scenarios = ScenarioSet(
            current=normalize_scenario_money(self.scenarios.current, currency_code),
            guaranteed=normalize_scenario_money(self.scenarios.guaranteed, currency_code),
        )

        return self


class SolveMetadata(StrictBaseModel):
    mode: str
    target_month: int
    target_av: Decimal | None = None
    iterations: int
    tolerance: Decimal
    strategy: str
    solved_premiums: dict[str, Decimal]


class Tax7702Failure(StrictBaseModel):
    t: int
    test: Literal["gpt", "cvat"]
    value: Decimal
    limit: Decimal
    reason: str


class Tax7702DebugRow(StrictBaseModel):
    t: int
    test: Literal["gpt", "cvat"]
    value: Decimal
    limit: Decimal


class Tax7702Report(StrictBaseModel):
    test_type: Literal["gpt", "cvat", "both"]
    status: Literal["pass", "fail"]
    first_failure_t: int | None
    failures: list[Tax7702Failure]
    tax_7702_debug: list[Tax7702DebugRow] | None = None


class IllustrationMetadata(StrictBaseModel):
    calc_version: str
    schema_version: str
    rounding_policy_id: str
    currency_code: CurrencyCode
    reporting_currencies: list[CurrencyCode] | None = None
    fx_rates: dict[CurrencyCode, Decimal] | None = None
    reporting_include_debug_fields: bool | None = None
    tax_7702: dict[str, Tax7702Report] | None = None
    solve: SolveMetadata | None = None


def build_metadata(
    request: "IllustrationRequest | None" = None,
    *,
    tax_7702: dict[str, Tax7702Report] | None = None,
    solve: SolveMetadata | None = None,
) -> IllustrationMetadata:
    if request is None:
        return IllustrationMetadata(
            calc_version=CALC_VERSION,
            schema_version=SCHEMA_VERSION,
            rounding_policy_id=ROUNDING_POLICY_ID,
            currency_code=CurrencyCode.USD,
            tax_7702=tax_7702,
            solve=solve,
        )
    return IllustrationMetadata(
        calc_version=CALC_VERSION,
        schema_version=SCHEMA_VERSION,
        rounding_policy_id=ROUNDING_POLICY_ID,
        currency_code=request.currency_code,
        reporting_currencies=request.reporting_currencies,
        fx_rates=request.fx_rates,
        reporting_include_debug_fields=(
            request.reporting_include_debug_fields if request.reporting_currencies else None
        ),
        tax_7702=tax_7702,
        solve=solve,
    )


class LedgerRow(StrictBaseModel):
    t: int
    policy_year: int
    attained_age: int
    policy_status: PolicyStatus
    premium: Decimal
    cumulative_premium: Decimal
    death_benefit: Decimal

    account_value_bop: Decimal | None = None
    premium_load: Decimal | None = None
    net_premium_to_av: Decimal | None = None
    policy_fee: Decimal | None = None
    coi_charge: Decimal | None = None
    admin_fee: Decimal | None = None
    charges_total: Decimal | None = None
    charges_assessed: Decimal | None = None
    charges_paid: Decimal | None = None
    charge_shortfall: Decimal | None = None
    rider_charges: Decimal | None = None
    net_amount_at_risk: Decimal | None = None
    account_value_mid_raw: Decimal | None = None
    interest_credited: Decimal | None = None
    account_value_eop: Decimal | None = None
    surrender_charge: Decimal | None = None
    cash_surrender_value: Decimal | None = None
    corridor_uplift: Decimal | None = None
    withdrawal: Decimal | None = None
    loan_draw: Decimal | None = None
    loan_repayment: Decimal | None = None
    loan_interest: Decimal | None = None
    loan_balance: Decimal | None = None

    term_month: int | None = None
    coverage_in_force: bool | None = None

    debug_av_mid_raw_unrounded: Decimal | None = None
    debug_interest_credited_unrounded: Decimal | None = None
    debug_account_value_eop_unrounded: Decimal | None = None


class Ledger(StrictBaseModel):
    frequency: Literal["monthly"] = "monthly"
    rows: list[LedgerRow]
    interest_mode: str | None = None


class IllustrationResult(StrictBaseModel):
    request_id: str
    product_code: str
    currency_code: CurrencyCode
    ledgers: dict[str, Ledger]
    ledgers_by_currency: dict[CurrencyCode, dict[str, Ledger]] | None = None
    metadata: IllustrationMetadata = Field(default_factory=build_metadata)
