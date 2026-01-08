from datetime import date
from decimal import Decimal

from opie.assumptions.models import ScenarioSet, ULScenarioAssumptions
from opie.core.engine import run_scenario
from opie.core.types import IllustrationRequest
from opie.products.ul_simple import SimpleULHooks


def _request(mode: str) -> IllustrationRequest:
    scenario = ULScenarioAssumptions(
        crediting_rate_annual=Decimal("0.12"),
        premium_load_pct=Decimal("0.00"),
        monthly_policy_fee=Decimal("0"),
        monthly_per_thousand_admin_fee=Decimal("0"),
        coi_table={30: Decimal("0.00")},
        surrender_charge_schedule={1: Decimal("0")},
        interest_mode=mode,
    )
    return IllustrationRequest(
        product_code="simple_ul",
        issue_age=30,
        issue_gender="M",
        risk_class="NT",
        face_amount=Decimal("100000"),
        issue_date=date(2025, 1, 1),
        duration_months=1,
        premium_schedule=[{"start_month": 1, "end_month": 1, "amount": Decimal("100")}],
        scenarios=ScenarioSet(current=scenario, guaranteed=scenario),
    )


def test_interest_mode_changes_crediting() -> None:
    hooks = SimpleULHooks()
    nominal_request = _request("nominal_div_12")
    effective_request = _request("effective_monthly")

    nominal_row = run_scenario(
        nominal_request, nominal_request.scenarios.current, "current", hooks
    ).rows[0]
    effective_row = run_scenario(
        effective_request, effective_request.scenarios.current, "current", hooks
    ).rows[0]

    assert nominal_row.interest_credited != effective_row.interest_credited
