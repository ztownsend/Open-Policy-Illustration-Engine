"""Deferred fixed annuity hooks (simplified)."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from opie.assumptions.models import AnnuityScenarioAssumptions, ScenarioAssumptions
from opie.core.errors import AssumptionError
from opie.core.money import quantize_money
from opie.core.types import IllustrationRequest, PolicyStatus
from opie.products.base import ChargeResult, DeathBenefitResult, PremiumResult

ZERO = Decimal("0")


def _require_annuity_scenario(scenario: ScenarioAssumptions) -> AnnuityScenarioAssumptions:
    if not isinstance(scenario, AnnuityScenarioAssumptions):
        raise AssumptionError("Annuity scenario assumptions required")
    return scenario


def _resolve_premium(schedule, t: int) -> Decimal:
    for rule in schedule or []:
        if rule.month is not None and rule.month == t:
            return rule.amount
        if rule.start_month is not None and rule.end_month is not None:
            if rule.start_month <= t <= rule.end_month:
                return rule.amount
    return ZERO


class DeferredAnnuityHooks:
    def premium_and_loads(
        self,
        state: Any,
        request: IllustrationRequest,
        scenario: ScenarioAssumptions,
    ) -> PremiumResult:
        premium = _resolve_premium(request.premium_schedule, state.t)
        currency_code = request.currency_code
        return PremiumResult(
            premium=quantize_money(premium, currency_code),
            premium_load=quantize_money(ZERO, currency_code),
            net_premium_to_av=quantize_money(premium, currency_code),
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
        return PolicyStatus.IN_FORCE

    def term_fields(
        self,
        state: Any,
        request: IllustrationRequest,
        scenario: ScenarioAssumptions,
    ) -> tuple[int | None, bool | None]:
        return None, None

    def death_benefit(
        self,
        state: Any,
        request: IllustrationRequest,
        scenario: ScenarioAssumptions,
        av_bop: Decimal,
        av_eop: Decimal,
    ) -> DeathBenefitResult:
        currency_code = request.currency_code
        return DeathBenefitResult(
            death_benefit=quantize_money(ZERO, currency_code),
            corridor_uplift=quantize_money(ZERO, currency_code),
        )

    def net_amount_at_risk(
        self,
        state: Any,
        request: IllustrationRequest,
        scenario: ScenarioAssumptions,
        av_bop: Decimal,
    ) -> Decimal:
        return quantize_money(ZERO, request.currency_code)

    def surrender_charge(
        self,
        state: Any,
        request: IllustrationRequest,
        scenario: ScenarioAssumptions,
        t: int,
    ) -> Decimal:
        annuity_scenario = _require_annuity_scenario(scenario)
        return quantize_money(
            annuity_scenario.surrender_charge_schedule.get(t, ZERO),
            request.currency_code,
        )
