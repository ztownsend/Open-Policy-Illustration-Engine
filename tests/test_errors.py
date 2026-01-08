from datetime import date
from decimal import Decimal

import pytest

from opie.assumptions.models import ScenarioSet, ULScenarioAssumptions
from opie.core.engine import ProjectionState
from opie.core.errors import AssumptionError, InvariantViolation
from opie.core.invariants import check_ul_invariants
from opie.core.types import IllustrationRequest, Ledger, LedgerRow, PolicyStatus
from opie.products.ul_simple import SimpleULHooks


def test_assumption_error_includes_context() -> None:
    scenario = ULScenarioAssumptions(
        crediting_rate_annual=Decimal("0.04"),
        premium_load_pct=Decimal("0.10"),
        monthly_policy_fee=Decimal("5"),
        monthly_per_thousand_admin_fee=Decimal("0.10"),
        coi_table={30: Decimal("0.24")},
        surrender_charge_schedule={1: Decimal("100")},
    )
    request = IllustrationRequest(
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
    with pytest.raises(AssumptionError) as excinfo:
        hooks.monthly_charges(
            state, request, request.scenarios.current, Decimal("0"), premium_result
        )
    message = str(excinfo.value)
    assert "product_code=simple_ul" in message
    assert "scenario=current" in message
    assert "t=1" in message
    assert "attained_age" in message


def test_invariant_violation_includes_t() -> None:
    ledger = Ledger(
        rows=[
            LedgerRow(
                t=2,
                policy_year=1,
                attained_age=30,
                policy_status=PolicyStatus.LAPSED,
                premium=Decimal("0"),
                cumulative_premium=Decimal("0"),
                death_benefit=Decimal("1"),
                account_value_eop=Decimal("0"),
                interest_credited=Decimal("1"),
            )
        ]
    )
    with pytest.raises(InvariantViolation) as excinfo:
        check_ul_invariants(ledger)
    assert "t=2" in str(excinfo.value)
