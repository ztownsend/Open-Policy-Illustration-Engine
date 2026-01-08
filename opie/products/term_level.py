"""LevelTerm product hooks implementation."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from opie.assumptions.models import ScenarioAssumptions, TermScenarioAssumptions
from opie.core.errors import AssumptionError
from opie.core.money import quantize_money
from opie.core.types import IllustrationRequest, PolicyStatus
from opie.products.base import ChargeResult, DeathBenefitResult, PremiumResult

ZERO = Decimal("0")
TWELVE = Decimal("12")


def _require_term_scenario(scenario: ScenarioAssumptions) -> TermScenarioAssumptions:
    if not isinstance(scenario, TermScenarioAssumptions):
        raise AssumptionError("Term scenario assumptions required")
    return scenario


def _resolve_premium(
    request: IllustrationRequest, scenario: TermScenarioAssumptions, t: int
) -> Decimal:
    if request.premium_schedule:
        for rule in request.premium_schedule:
            if rule.month is not None and rule.month == t:
                return rule.amount
            if rule.start_month is not None and rule.end_month is not None:
                if rule.start_month <= t <= rule.end_month:
                    return rule.amount
        return ZERO

    if scenario.annual_premium is None:
        return ZERO

    modal_factor = request.modal_factor or scenario.term_modal_factor
    if modal_factor is None:
        modal_factor = Decimal("1") / TWELVE
    return scenario.annual_premium * modal_factor


class LevelTermHooks:
    def premium_and_loads(
        self,
        state: Any,
        request: IllustrationRequest,
        scenario: ScenarioAssumptions,
    ) -> PremiumResult:
        term_scenario = _require_term_scenario(scenario)
        premium = _resolve_premium(request, term_scenario, state.t)
        currency_code = request.currency_code
        return PremiumResult(
            premium=quantize_money(premium, currency_code),
            premium_load=quantize_money(ZERO, currency_code),
            net_premium_to_av=quantize_money(ZERO, currency_code),
        )

    def monthly_charges(
        self,
        state: Any,
        request: IllustrationRequest,
        scenario: ScenarioAssumptions,
        av_bop: Decimal,
        premium_result: PremiumResult,
    ) -> ChargeResult:
        currency_code = request.currency_code
        return ChargeResult(
            policy_fee=quantize_money(ZERO, currency_code),
            admin_fee=quantize_money(ZERO, currency_code),
            coi_charge=quantize_money(ZERO, currency_code),
            charges_total=quantize_money(ZERO, currency_code),
        )

    def policy_status(
        self,
        state: Any,
        request: IllustrationRequest,
        scenario: ScenarioAssumptions,
    ) -> PolicyStatus:
        term_length = request.term_length_months or 0
        if state.t > term_length:
            return PolicyStatus.EXPIRED
        return PolicyStatus.IN_FORCE

    def term_fields(
        self,
        state: Any,
        request: IllustrationRequest,
        scenario: ScenarioAssumptions,
    ) -> tuple[int | None, bool | None]:
        status = self.policy_status(state, request, scenario)
        return state.t, status == PolicyStatus.IN_FORCE

    def death_benefit(
        self,
        state: Any,
        request: IllustrationRequest,
        scenario: ScenarioAssumptions,
        av_bop: Decimal,
        av_eop: Decimal,
    ) -> DeathBenefitResult:
        if state.t > (request.term_length_months or 0):
            death_benefit = ZERO
        else:
            death_benefit = request.face_amount
        currency_code = request.currency_code
        return DeathBenefitResult(
            death_benefit=quantize_money(death_benefit, currency_code),
            corridor_uplift=quantize_money(ZERO, currency_code),
        )

    def net_amount_at_risk(
        self,
        state: Any,
        request: IllustrationRequest,
        scenario: ScenarioAssumptions,
        av_bop: Decimal,
    ) -> Decimal:
        if state.t > (request.term_length_months or 0):
            return quantize_money(ZERO, request.currency_code)
        return quantize_money(request.face_amount, request.currency_code)

    def surrender_charge(
        self,
        state: Any,
        request: IllustrationRequest,
        scenario: ScenarioAssumptions,
        t: int,
    ) -> Decimal:
        return quantize_money(ZERO, request.currency_code)
