from datetime import date
from decimal import Decimal

from opie.assumptions.models import ScenarioSet, ULScenarioAssumptions
from opie.core.engine import run_scenario
from opie.core.types import IllustrationRequest, RiderSpec
from opie.products.ul_simple import SimpleULHooks


def test_flat_charge_rider_included_in_charges() -> None:
    scenario = ULScenarioAssumptions(
        crediting_rate_annual=Decimal("0.00"),
        premium_load_pct=Decimal("0.00"),
        monthly_policy_fee=Decimal("0"),
        monthly_per_thousand_admin_fee=Decimal("0"),
        coi_table={30: Decimal("0.00")},
        surrender_charge_schedule={1: Decimal("0")},
    )
    request = IllustrationRequest(
        product_code="simple_ul",
        issue_age=30,
        issue_gender="M",
        risk_class="NT",
        face_amount=Decimal("1000"),
        issue_date=date(2025, 1, 1),
        duration_months=1,
        premium_schedule=[{"start_month": 1, "end_month": 1, "amount": Decimal("10")}],
        scenarios=ScenarioSet(current=scenario, guaranteed=scenario),
        riders=[RiderSpec(rider_code="flat_charge", amount=Decimal("5"))],
    )
    ledger = run_scenario(request, request.scenarios.current, "current", SimpleULHooks())
    row = ledger.rows[0]
    assert row.rider_charges == Decimal("5.00")
    assert row.charges_total == Decimal("5.00")
