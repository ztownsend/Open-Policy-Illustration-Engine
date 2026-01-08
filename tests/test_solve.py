from datetime import date
from decimal import Decimal

from opie.assumptions.models import ScenarioSet, ULScenarioAssumptions
from opie.core.types import IllustrationRequest, SolveConfig
from opie.products.ul_simple import SimpleULHooks
from opie.core.solve import solve_illustration


def _base_request(strategy: str, fee_current: str, fee_guaranteed: str) -> IllustrationRequest:
    current = ULScenarioAssumptions(
        crediting_rate_annual=Decimal("0.00"),
        premium_load_pct=Decimal("0.00"),
        monthly_policy_fee=Decimal(fee_current),
        monthly_per_thousand_admin_fee=Decimal("0"),
        coi_table={30: Decimal("0.00")},
        surrender_charge_schedule={1: Decimal("0")},
    )
    guaranteed = ULScenarioAssumptions(
        crediting_rate_annual=Decimal("0.00"),
        premium_load_pct=Decimal("0.00"),
        monthly_policy_fee=Decimal(fee_guaranteed),
        monthly_per_thousand_admin_fee=Decimal("0"),
        coi_table={30: Decimal("0.00")},
        surrender_charge_schedule={1: Decimal("0")},
    )
    solve = SolveConfig(
        mode="keep_in_force",
        target_month=12,
        min_premium=Decimal("0"),
        max_premium=Decimal("100"),
        iterations=20,
        tolerance=Decimal("0.01"),
        strategy=strategy,
    )
    return IllustrationRequest(
        product_code="simple_ul",
        issue_age=30,
        issue_gender="M",
        risk_class="NT",
        face_amount=Decimal("100000"),
        issue_date=date(2025, 1, 1),
        duration_months=12,
        premium_schedule=[{"start_month": 1, "end_month": 12, "amount": Decimal("0")}],
        scenarios=ScenarioSet(current=current, guaranteed=guaranteed),
        solve=solve,
    )


def test_solve_deterministic() -> None:
    request = _base_request("current_only", "50", "50")
    hooks = SimpleULHooks()
    first = solve_illustration(request, hooks)
    second = solve_illustration(request, hooks)
    assert first.metadata.solve is not None
    assert (
        first.metadata.solve.solved_premiums["current"]
        == second.metadata.solve.solved_premiums["current"]
    )


def test_solve_per_scenario() -> None:
    request = _base_request("per_scenario", "50", "60")
    hooks = SimpleULHooks()
    result = solve_illustration(request, hooks)
    assert result.metadata.solve is not None
    assert result.metadata.solve.solved_premiums["current"] == Decimal("50.00")
    assert result.metadata.solve.solved_premiums["guaranteed"] == Decimal("60.00")
