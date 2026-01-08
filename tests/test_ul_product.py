from datetime import date
from decimal import Decimal

import pytest

from opie.assumptions.models import ScenarioSet, ULScenarioAssumptions
from opie.core.engine import ProjectionState
from opie.core.errors import AssumptionError
from opie.core.types import IllustrationRequest
from opie.products.ul_simple import SimpleULHooks


def _ul_request() -> IllustrationRequest:
    scenario = ULScenarioAssumptions(
        crediting_rate_annual=Decimal("0.04"),
        premium_load_pct=Decimal("0.10"),
        monthly_policy_fee=Decimal("5"),
        monthly_per_thousand_admin_fee=Decimal("0.10"),
        coi_table={30: Decimal("0.24")},
        surrender_charge_schedule={1: Decimal("100"), 2: Decimal("80")},
    )
    return IllustrationRequest(
        product_code="simple_ul",
        issue_age=30,
        issue_gender="M",
        risk_class="NT",
        face_amount=Decimal("100000"),
        issue_date=date(2025, 1, 1),
        duration_months=12,
        premium_schedule=[{"start_month": 1, "end_month": 12, "amount": Decimal("100")}],
        scenarios=ScenarioSet(current=scenario, guaranteed=scenario),
    )


def test_ul_premium_and_loads() -> None:
    request = _ul_request()
    hooks = SimpleULHooks()
    state = ProjectionState(
        t=1,
        policy_year=1,
        attained_age=30,
        cumulative_premium=Decimal("0"),
        av_eop_prev=Decimal("0"),
        scenario_name="current",
    )
    result = hooks.premium_and_loads(state, request, request.scenarios.current)
    assert result.premium == Decimal("100.00")
    assert result.premium_load == Decimal("10.00")
    assert result.net_premium_to_av == Decimal("90.00")


def test_ul_monthly_charges_and_nar() -> None:
    request = _ul_request()
    hooks = SimpleULHooks()
    state = ProjectionState(
        t=1,
        policy_year=1,
        attained_age=30,
        cumulative_premium=Decimal("0"),
        av_eop_prev=Decimal("0"),
        scenario_name="current",
    )
    premium_result = hooks.premium_and_loads(state, request, request.scenarios.current)
    charges = hooks.monthly_charges(
        state,
        request,
        request.scenarios.current,
        av_bop=Decimal("1000"),
        premium_result=premium_result,
    )
    assert charges.policy_fee == Decimal("5.00")
    assert charges.admin_fee == Decimal("10.00")
    assert charges.coi_charge == Decimal("1.98")
    assert charges.charges_total == Decimal("16.98")

    nar = hooks.net_amount_at_risk(
        state, request, request.scenarios.current, av_bop=Decimal("120000")
    )
    assert nar == Decimal("0.00")


def test_ul_surrender_charge_schedule() -> None:
    request = _ul_request()
    hooks = SimpleULHooks()
    state = ProjectionState(
        t=2,
        policy_year=1,
        attained_age=30,
        cumulative_premium=Decimal("0"),
        av_eop_prev=Decimal("0"),
        scenario_name="current",
    )
    assert hooks.surrender_charge(state, request, request.scenarios.current, t=2) == Decimal(
        "80.00"
    )
    assert hooks.surrender_charge(state, request, request.scenarios.current, t=5) == Decimal("0.00")


def test_ul_missing_coi_rate_raises() -> None:
    request = _ul_request()
    hooks = SimpleULHooks()
    state = ProjectionState(
        t=1,
        policy_year=1,
        attained_age=99,
        cumulative_premium=Decimal("0"),
        av_eop_prev=Decimal("0"),
        scenario_name="current",
    )
    premium_result = hooks.premium_and_loads(state, request, request.scenarios.current)
    with pytest.raises(AssumptionError):
        hooks.monthly_charges(
            state, request, request.scenarios.current, Decimal("0"), premium_result
        )


def test_ul_death_benefit_option_increasing() -> None:
    request = _ul_request()
    request = request.model_copy(update={"death_benefit_option": "increasing"})
    hooks = SimpleULHooks()
    state = ProjectionState(
        t=1,
        policy_year=1,
        attained_age=30,
        cumulative_premium=Decimal("0"),
        av_eop_prev=Decimal("0"),
        scenario_name="current",
    )
    result = hooks.death_benefit(
        state,
        request,
        request.scenarios.current,
        av_bop=Decimal("0"),
        av_eop=Decimal("5000"),
    )
    assert result.death_benefit == Decimal("105000.00")
    nar = hooks.net_amount_at_risk(
        state, request, request.scenarios.current, av_bop=Decimal("5000")
    )
    assert nar == Decimal("100000.00")


def test_ul_corridor_uplift() -> None:
    scenario = ULScenarioAssumptions(
        crediting_rate_annual=Decimal("0.04"),
        premium_load_pct=Decimal("0.00"),
        monthly_policy_fee=Decimal("0"),
        monthly_per_thousand_admin_fee=Decimal("0"),
        coi_table={30: Decimal("0.00")},
        surrender_charge_schedule={1: Decimal("0")},
        corridor_factors={30: Decimal("2.0")},
    )
    request = IllustrationRequest(
        product_code="simple_ul",
        issue_age=30,
        issue_gender="M",
        risk_class="NT",
        face_amount=Decimal("1000"),
        issue_date=date(2025, 1, 1),
        duration_months=12,
        premium_schedule=[{"start_month": 1, "end_month": 12, "amount": Decimal("0")}],
        scenarios=ScenarioSet(current=scenario, guaranteed=scenario),
    )
    hooks = SimpleULHooks()
    state = ProjectionState(
        t=1,
        policy_year=1,
        attained_age=30,
        cumulative_premium=Decimal("0"),
        av_eop_prev=Decimal("0"),
        scenario_name="current",
    )
    result = hooks.death_benefit(
        state,
        request,
        request.scenarios.current,
        av_bop=Decimal("0"),
        av_eop=Decimal("1000"),
    )
    assert result.corridor_uplift == Decimal("1000.00")
    assert result.death_benefit == Decimal("2000.00")
