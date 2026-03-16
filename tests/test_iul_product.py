from __future__ import annotations

from decimal import Decimal

import pytest

from opie.assumptions.models import IULScenarioAssumptions, IndexAccount
from opie.core.money import quantize_rate
from opie.products.iul import _account_monthly_rate

TWELVE = Decimal("12")


def test_fixed_account_rate() -> None:
    account = IndexAccount(
        name="Fixed",
        allocation=Decimal("1"),
        strategy_type="fixed",
        fixed_rate=Decimal("0.03"),
    )
    rate = _account_monthly_rate(account)
    assert rate == quantize_rate(Decimal("0.03") / TWELVE)


def test_point_to_point_rate_with_cap() -> None:
    account = IndexAccount(
        name="PTP",
        allocation=Decimal("1"),
        strategy_type="point_to_point",
        illustrated_rate=Decimal("0.12"),
        cap=Decimal("0.10"),
        floor=Decimal("0"),
        participation=Decimal("1"),
    )
    rate = _account_monthly_rate(account)
    # 12% × 1.0 participation = 12%, capped at 10%
    assert rate == quantize_rate(Decimal("0.10") / TWELVE)


def test_point_to_point_rate_with_floor() -> None:
    account = IndexAccount(
        name="PTP",
        allocation=Decimal("1"),
        strategy_type="point_to_point",
        illustrated_rate=Decimal("-0.05"),
        cap=Decimal("0.10"),
        floor=Decimal("0"),
        participation=Decimal("1"),
    )
    rate = _account_monthly_rate(account)
    # -5% floored at 0%
    assert rate == Decimal("0")


def test_point_to_point_rate_with_participation() -> None:
    account = IndexAccount(
        name="PTP",
        allocation=Decimal("1"),
        strategy_type="point_to_point",
        illustrated_rate=Decimal("0.08"),
        cap=Decimal("0.12"),
        floor=Decimal("0"),
        participation=Decimal("0.80"),
    )
    rate = _account_monthly_rate(account)
    # 8% × 0.80 = 6.4%, within cap/floor
    assert rate == quantize_rate(Decimal("0.064") / TWELVE)


def test_allocation_must_sum_to_one() -> None:
    with pytest.raises(ValueError, match="sum to 1.0"):
        IULScenarioAssumptions(
            crediting_rate_annual=Decimal("0"),
            premium_load_pct=Decimal("0.05"),
            monthly_policy_fee=Decimal("10"),
            coi_table={40: Decimal("5")},
            surrender_charge_schedule={1: Decimal("0")},
            index_accounts=[
                IndexAccount(
                    name="Fixed",
                    allocation=Decimal("0.30"),
                    strategy_type="fixed",
                    fixed_rate=Decimal("0.03"),
                ),
                IndexAccount(
                    name="PTP",
                    allocation=Decimal("0.30"),
                    strategy_type="point_to_point",
                    illustrated_rate=Decimal("0.07"),
                    cap=Decimal("0.10"),
                    floor=Decimal("0"),
                    participation=Decimal("1"),
                ),
            ],
        )


def test_cap_must_be_gte_floor() -> None:
    with pytest.raises(ValueError, match="cap must be >= floor"):
        IndexAccount(
            name="Bad",
            allocation=Decimal("1"),
            strategy_type="point_to_point",
            illustrated_rate=Decimal("0.05"),
            cap=Decimal("0.02"),
            floor=Decimal("0.05"),
            participation=Decimal("1"),
        )


def test_participation_must_be_positive() -> None:
    with pytest.raises(ValueError, match="participation must be > 0"):
        IndexAccount(
            name="Bad",
            allocation=Decimal("1"),
            strategy_type="point_to_point",
            illustrated_rate=Decimal("0.05"),
            cap=Decimal("0.10"),
            floor=Decimal("0"),
            participation=Decimal("0"),
        )


def test_empty_accounts_rejected() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        IULScenarioAssumptions(
            crediting_rate_annual=Decimal("0"),
            premium_load_pct=Decimal("0.05"),
            monthly_policy_fee=Decimal("10"),
            coi_table={40: Decimal("5")},
            surrender_charge_schedule={1: Decimal("0")},
            index_accounts=[],
        )
