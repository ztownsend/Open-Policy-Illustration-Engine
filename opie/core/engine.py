"""Core projection engine for OPIE."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256

from opie.assumptions.models import ScenarioAssumptions
from opie.core.errors import EngineError
from opie.core.ledger import dumps_json
from opie.core.money import quantize_money, quantize_rate
from opie.core.time import attained_age_for_month, policy_year_for_month
from opie.core.types import IllustrationRequest, IllustrationResult, Ledger, LedgerRow, PolicyStatus
from opie.products.base import ProductHooks
from opie.products.riders.registry import get_rider_hook

ZERO = Decimal("0")
ONE = Decimal("1")
TWELVE = Decimal("12")


@dataclass(frozen=True)
class ProjectionState:
    t: int
    policy_year: int
    attained_age: int
    cumulative_premium: Decimal
    av_eop_prev: Decimal
    scenario_name: str


def _monthly_rate(scenario: ScenarioAssumptions) -> Decimal:
    annual_rate = getattr(scenario, "crediting_rate_annual", ZERO)
    mode = getattr(scenario, "interest_mode", "nominal_div_12")
    if mode == "effective_monthly":
        monthly_rate = (ONE + annual_rate).ln() / TWELVE
        monthly_rate = monthly_rate.exp() - ONE
    else:
        monthly_rate = annual_rate / TWELVE
    return quantize_rate(monthly_rate)


def _request_id(request: IllustrationRequest) -> str:
    payload = request.model_dump(mode="python", exclude={"debug"})
    if payload.get("solve") is None:
        payload.pop("solve", None)
    digest = sha256(dumps_json(payload).encode("utf-8")).hexdigest()
    return digest[:12]


def _schedule_amount(schedule: dict[int, Decimal] | None, t: int) -> Decimal:
    if not schedule:
        return ZERO
    return schedule.get(t, ZERO)


def run_scenario(
    request: IllustrationRequest,
    scenario: ScenarioAssumptions,
    scenario_name: str,
    hooks: ProductHooks,
) -> Ledger:
    rows: list[LedgerRow] = []
    av_eop_prev = ZERO
    cumulative_premium = ZERO
    grace_counter = 0
    loan_balance_prev = ZERO
    loan_rate_annual = request.loan_interest_rate_annual or ZERO
    loan_monthly_rate = quantize_rate(loan_rate_annual / TWELVE)

    for t in range(1, request.duration_months + 1):
        policy_year = policy_year_for_month(t)
        attained_age = attained_age_for_month(request.issue_age, t)
        state = ProjectionState(
            t=t,
            policy_year=policy_year,
            attained_age=attained_age,
            cumulative_premium=cumulative_premium,
            av_eop_prev=av_eop_prev,
            scenario_name=scenario_name,
        )

        av_bop = av_eop_prev
        premium_result = hooks.premium_and_loads(state, request, scenario)
        charges = hooks.monthly_charges(state, request, scenario, av_bop, premium_result)
        net_amount_at_risk = hooks.net_amount_at_risk(state, request, scenario, av_bop)
        policy_status = hooks.policy_status(state, request, scenario)
        term_month, coverage_in_force = hooks.term_fields(state, request, scenario)

        cumulative_premium = cumulative_premium + premium_result.premium

        rider_charges = ZERO
        if request.riders:
            for rider in sorted(request.riders, key=lambda item: item.rider_code):
                hook = get_rider_hook(rider.rider_code)
                rider_charges += hook.monthly_charge(state, request, scenario, rider)

        charges_assessed = charges.charges_total + rider_charges
        available_for_charges = av_bop + premium_result.net_premium_to_av
        if available_for_charges < ZERO:
            charges_paid = ZERO
        elif available_for_charges >= charges_assessed:
            charges_paid = charges_assessed
        else:
            charges_paid = available_for_charges
        charge_shortfall = charges_assessed - charges_paid

        av_mid_raw = av_bop + premium_result.net_premium_to_av - charges_assessed

        if av_mid_raw < ZERO:
            grace_counter += 1
            if grace_counter <= request.grace_months:
                interest_credited = ZERO
                av_eop_pre = ZERO
                lapsed = False
            else:
                policy_status = PolicyStatus.LAPSED
                interest_credited = ZERO
                av_eop_pre = ZERO
                lapsed = True
        else:
            grace_counter = 0
            floor = request.minimum_account_value_floor or ZERO
            av_mid = av_mid_raw if av_mid_raw > floor else floor
            interest_credited = av_mid * _monthly_rate(scenario)
            av_eop_pre = av_mid + interest_credited
            lapsed = False

        if lapsed:
            withdrawal = ZERO
            loan_draw = ZERO
            loan_repayment = ZERO
            loan_interest = ZERO
            loan_balance = ZERO
            av_eop = av_eop_pre
            surrender_charge = ZERO
            cash_surrender_value = ZERO
            death_benefit = ZERO
            corridor_uplift = ZERO
        else:
            withdrawal = _schedule_amount(request.withdrawal_schedule, t)
            loan_draw = _schedule_amount(request.loan_draw_schedule, t)
            loan_repayment = _schedule_amount(request.loan_repayment_schedule, t)

            loan_interest = loan_balance_prev * loan_monthly_rate
            loan_balance = loan_balance_prev + loan_draw + loan_interest - loan_repayment
            if loan_balance < ZERO:
                loan_balance = ZERO

            av_after_withdrawal = av_eop_pre - withdrawal
            if av_after_withdrawal < ZERO:
                av_after_withdrawal = ZERO
            av_after_loan = av_after_withdrawal - loan_draw
            if av_after_loan < ZERO:
                av_after_loan = ZERO

            av_eop = av_after_loan
            surrender_charge = hooks.surrender_charge(state, request, scenario, t)
            cash_surrender_value = av_eop - surrender_charge - loan_balance
            if cash_surrender_value < ZERO:
                cash_surrender_value = ZERO
            db_result = hooks.death_benefit(state, request, scenario, av_bop, av_eop)
            death_benefit = db_result.death_benefit
            corridor_uplift = db_result.corridor_uplift

        av_eop_quantized = quantize_money(av_eop)

        row = LedgerRow(
            t=t,
            policy_year=policy_year,
            attained_age=attained_age,
            policy_status=policy_status,
            premium=quantize_money(premium_result.premium),
            cumulative_premium=quantize_money(cumulative_premium),
            death_benefit=quantize_money(death_benefit),
            account_value_bop=quantize_money(av_bop),
            premium_load=quantize_money(premium_result.premium_load),
            net_premium_to_av=quantize_money(premium_result.net_premium_to_av),
            policy_fee=quantize_money(charges.policy_fee),
            coi_charge=quantize_money(charges.coi_charge),
            admin_fee=quantize_money(charges.admin_fee),
            charges_total=quantize_money(charges_assessed),
            charges_assessed=quantize_money(charges_assessed),
            charges_paid=quantize_money(charges_paid),
            charge_shortfall=quantize_money(charge_shortfall),
            rider_charges=quantize_money(rider_charges),
            net_amount_at_risk=quantize_money(net_amount_at_risk),
            account_value_mid_raw=quantize_money(av_mid_raw),
            interest_credited=quantize_money(interest_credited),
            account_value_eop=av_eop_quantized,
            surrender_charge=quantize_money(surrender_charge),
            cash_surrender_value=quantize_money(cash_surrender_value),
            corridor_uplift=quantize_money(corridor_uplift),
            withdrawal=quantize_money(withdrawal),
            loan_draw=quantize_money(loan_draw),
            loan_repayment=quantize_money(loan_repayment),
            loan_interest=quantize_money(loan_interest),
            loan_balance=quantize_money(loan_balance),
            term_month=term_month,
            coverage_in_force=coverage_in_force,
            debug_av_mid_raw_unrounded=av_mid_raw if request.debug else None,
            debug_interest_credited_unrounded=interest_credited if request.debug else None,
            debug_account_value_eop_unrounded=av_eop if request.debug else None,
        )
        rows.append(row)

        av_eop_prev = av_eop_quantized
        loan_balance_prev = quantize_money(loan_balance)
        if lapsed:
            break

    return Ledger(rows=rows, interest_mode=getattr(scenario, "interest_mode", None))


def run_illustration(request: IllustrationRequest, hooks: ProductHooks) -> IllustrationResult:
    ledgers = {}
    for scenario_name in ("current", "guaranteed"):
        scenario = getattr(request.scenarios, scenario_name)
        ledgers[scenario_name] = run_scenario(request, scenario, scenario_name, hooks)

    if not ledgers:
        raise EngineError("No scenarios executed", product_code=request.product_code)

    return IllustrationResult(
        request_id=_request_id(request),
        product_code=request.product_code,
        ledgers=ledgers,
    )
