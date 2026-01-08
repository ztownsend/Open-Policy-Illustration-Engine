from datetime import date
from decimal import Decimal

from opie.assumptions.models import ScenarioSet, ULScenarioAssumptions
from opie.core.engine import run_scenario
from opie.core.types import IllustrationRequest
from opie.products.ul_simple import SimpleULHooks


def test_withdrawals_and_loans_affect_values() -> None:
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
        premium_schedule=[{"start_month": 1, "end_month": 1, "amount": Decimal("100")}],
        scenarios=ScenarioSet(current=scenario, guaranteed=scenario),
        withdrawal_schedule={1: Decimal("40")},
        loan_draw_schedule={1: Decimal("20")},
        loan_repayment_schedule={1: Decimal("5")},
        loan_interest_rate_annual=Decimal("0.12"),
    )
    ledger = run_scenario(request, request.scenarios.current, "current", SimpleULHooks())
    row = ledger.rows[0]

    assert row.withdrawal == Decimal("40.00")
    assert row.loan_draw == Decimal("20.00")
    assert row.loan_repayment == Decimal("5.00")
    assert row.loan_interest == Decimal("0.00")
    assert row.loan_balance == Decimal("15.00")
    assert row.account_value_eop == Decimal("40.00")
    assert row.cash_surrender_value == Decimal("25.00")
