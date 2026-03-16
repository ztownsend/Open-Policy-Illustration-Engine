"""Non-par Whole Life product hooks (simplified).

WL ledger conventions (see docs/opie_mvp_spec.md):
  - Cash value and surrender value schedules are month-indexed (keyed by t).
  - No interpolation is performed; values are used as-is for each month.
  - Missing month entries are errors (raise AssumptionError with context).
  - Surrender charge = max(0, cash_value - surrender_value).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from opie.assumptions.models import ScenarioAssumptions, WLScenarioAssumptions
from opie.core.errors import AssumptionError
from opie.core.money import quantize_money
from opie.core.types import IllustrationRequest, PolicyStatus
from opie.products.base import ChargeResult, DeathBenefitResult, PremiumResult

ZERO = Decimal("0")


def _require_wl_scenario(scenario: ScenarioAssumptions) -> WLScenarioAssumptions:
    if not isinstance(scenario, WLScenarioAssumptions):
        raise AssumptionError("WL scenario assumptions required")
    return scenario


class WLNonParHooks:
    def premium_and_loads(
        self,
        state: Any,
        request: IllustrationRequest,
        scenario: ScenarioAssumptions,
    ) -> PremiumResult:
        wl_scenario = _require_wl_scenario(scenario)
        target_av = wl_scenario.cash_value_schedule.get(state.t)
        if target_av is None:
            raise AssumptionError(
                "Cash value missing",
                product_code=request.product_code,
                scenario=getattr(state, "scenario_name", None),
                t=state.t,
            )
        net_premium_to_av = target_av - state.av_eop_prev
        if net_premium_to_av < ZERO:
            raise AssumptionError(
                "Cash value schedule decreases",
                product_code=request.product_code,
                scenario=getattr(state, "scenario_name", None),
                t=state.t,
            )
        currency_code = request.currency_code
        return PremiumResult(
            premium=quantize_money(net_premium_to_av, currency_code),
            premium_load=quantize_money(ZERO, currency_code),
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
            death_benefit=quantize_money(request.face_amount, currency_code),
            corridor_uplift=quantize_money(ZERO, currency_code),
        )

    def net_amount_at_risk(
        self,
        state: Any,
        request: IllustrationRequest,
        scenario: ScenarioAssumptions,
        av_bop: Decimal,
    ) -> Decimal:
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
        wl_scenario = _require_wl_scenario(scenario)
        cash_value = wl_scenario.cash_value_schedule.get(t)
        surrender_value = wl_scenario.surrender_value_schedule.get(t)
        if cash_value is None or surrender_value is None:
            raise AssumptionError(
                "Missing WL schedule",
                product_code=request.product_code,
                scenario=getattr(state, "scenario_name", None),
                t=t,
            )
        charge = cash_value - surrender_value
        if charge < ZERO:
            charge = ZERO
        return quantize_money(charge, request.currency_code)

    def credit_interest(
        self,
        state: Any,
        request: IllustrationRequest,
        scenario: ScenarioAssumptions,
        av_mid: Decimal,
    ) -> Decimal:
        return ZERO

    def benefit_payout(
        self,
        state: Any,
        request: IllustrationRequest,
        scenario: ScenarioAssumptions,
    ) -> Decimal:
        return ZERO
