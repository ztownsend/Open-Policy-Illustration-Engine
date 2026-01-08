"""SimpleUL product hooks implementation."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from opie.assumptions.models import ScenarioAssumptions, ULScenarioAssumptions
from opie.core.errors import AssumptionError
from opie.core.money import quantize_money, quantize_rate
from opie.core.types import IllustrationRequest, PolicyStatus
from opie.products.base import ChargeResult, DeathBenefitResult, PremiumResult

ZERO = Decimal("0")
TWELVE = Decimal("12")
THOUSAND = Decimal("1000")


def _require_ul_scenario(scenario: ScenarioAssumptions) -> ULScenarioAssumptions:
    if not isinstance(scenario, ULScenarioAssumptions):
        raise AssumptionError("UL scenario assumptions required")
    return scenario


def _resolve_premium(schedule, t: int) -> Decimal:
    for rule in schedule or []:
        if rule.month is not None and rule.month == t:
            return rule.amount
        if rule.start_month is not None and rule.end_month is not None:
            if rule.start_month <= t <= rule.end_month:
                return rule.amount
    return ZERO


class SimpleULHooks:
    def premium_and_loads(
        self,
        state: Any,
        request: IllustrationRequest,
        scenario: ScenarioAssumptions,
    ) -> PremiumResult:
        ul_scenario = _require_ul_scenario(scenario)
        premium = _resolve_premium(request.premium_schedule, state.t)
        premium_load = premium * ul_scenario.premium_load_pct
        net_premium_to_av = premium - premium_load
        currency_code = request.currency_code
        return PremiumResult(
            premium=quantize_money(premium, currency_code),
            premium_load=quantize_money(premium_load, currency_code),
            net_premium_to_av=quantize_money(net_premium_to_av, currency_code),
        )

    def monthly_charges(
        self,
        state: Any,
        request: IllustrationRequest,
        scenario: ScenarioAssumptions,
        av_bop: Decimal,
        premium_result: PremiumResult,
    ) -> ChargeResult:
        ul_scenario = _require_ul_scenario(scenario)
        policy_fee = ul_scenario.monthly_policy_fee
        admin_fee = ul_scenario.monthly_per_thousand_admin_fee * (request.face_amount / THOUSAND)
        nar = self.net_amount_at_risk(state, request, scenario, av_bop)
        coi_rate_annual = ul_scenario.coi_table.get(state.attained_age)
        if coi_rate_annual is None:
            raise AssumptionError(
                "COI rate missing",
                product_code=request.product_code,
                scenario=getattr(state, "scenario_name", None),
                t=state.t,
                values={"attained_age": state.attained_age},
            )
        monthly_rate = quantize_rate(coi_rate_annual / TWELVE)
        coi_charge = monthly_rate * (nar / THOUSAND)
        charges_total = policy_fee + admin_fee + coi_charge
        currency_code = request.currency_code
        return ChargeResult(
            policy_fee=quantize_money(policy_fee, currency_code),
            admin_fee=quantize_money(admin_fee, currency_code),
            coi_charge=quantize_money(coi_charge, currency_code),
            charges_total=quantize_money(charges_total, currency_code),
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
        ul_scenario = _require_ul_scenario(scenario)
        if request.death_benefit_option == "increasing":
            base_db = request.face_amount + av_eop
        else:
            base_db = request.face_amount

        corridor_uplift = ZERO
        if ul_scenario.corridor_factors is not None:
            factor = ul_scenario.corridor_factors.get(state.attained_age)
            if factor is None:
                raise AssumptionError(
                    "Corridor factor missing",
                    product_code=request.product_code,
                    scenario=getattr(state, "scenario_name", None),
                    t=state.t,
                    values={"attained_age": state.attained_age},
                )
            corridor_db = av_eop * factor
            if corridor_db > base_db:
                corridor_uplift = corridor_db - base_db

        death_benefit = base_db + corridor_uplift
        currency_code = request.currency_code
        return DeathBenefitResult(
            death_benefit=quantize_money(death_benefit, currency_code),
            corridor_uplift=quantize_money(corridor_uplift, currency_code),
        )

    def net_amount_at_risk(
        self,
        state: Any,
        request: IllustrationRequest,
        scenario: ScenarioAssumptions,
        av_bop: Decimal,
    ) -> Decimal:
        if request.death_benefit_option == "increasing":
            nar = request.face_amount
        else:
            nar = request.face_amount - av_bop
            if nar < ZERO:
                nar = ZERO
        return quantize_money(nar, request.currency_code)

    def surrender_charge(
        self,
        state: Any,
        request: IllustrationRequest,
        scenario: ScenarioAssumptions,
        t: int,
    ) -> Decimal:
        ul_scenario = _require_ul_scenario(scenario)
        charge = ul_scenario.surrender_charge_schedule.get(t, ZERO)
        return quantize_money(charge, request.currency_code)
