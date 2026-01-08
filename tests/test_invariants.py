from decimal import Decimal

import pytest

from opie.core.errors import InvariantViolation
from opie.core.invariants import check_term_invariants, check_ul_invariants
from opie.core.types import Ledger, LedgerRow, PolicyStatus


def _ul_row(**overrides) -> LedgerRow:
    base = dict(
        t=1,
        policy_year=1,
        attained_age=30,
        policy_status=PolicyStatus.IN_FORCE,
        premium=Decimal("100.00"),
        cumulative_premium=Decimal("100.00"),
        death_benefit=Decimal("100000.00"),
        account_value_eop=Decimal("90.00"),
        cash_surrender_value=Decimal("80.00"),
        interest_credited=Decimal("1.00"),
        charges_assessed=Decimal("10.00"),
        charges_paid=Decimal("10.00"),
        charge_shortfall=Decimal("0.00"),
        rider_charges=Decimal("0.00"),
        corridor_uplift=Decimal("0.00"),
        loan_balance=Decimal("0.00"),
    )
    base.update(overrides)
    return LedgerRow(**base)


def _term_row(**overrides) -> LedgerRow:
    base = dict(
        t=1,
        policy_year=1,
        attained_age=40,
        policy_status=PolicyStatus.IN_FORCE,
        premium=Decimal("100.00"),
        cumulative_premium=Decimal("100.00"),
        death_benefit=Decimal("250000.00"),
        charges_assessed=Decimal("0.00"),
        charges_paid=Decimal("0.00"),
        charge_shortfall=Decimal("0.00"),
        rider_charges=Decimal("0.00"),
        corridor_uplift=Decimal("0.00"),
        loan_balance=Decimal("0.00"),
    )
    base.update(overrides)
    return LedgerRow(**base)


def test_ul_invariants_pass() -> None:
    ledger = Ledger(rows=[_ul_row()])
    check_ul_invariants(ledger)


def test_ul_csv_exceeds_av_raises() -> None:
    ledger = Ledger(
        rows=[_ul_row(cash_surrender_value=Decimal("95.00"), account_value_eop=Decimal("90.00"))]
    )
    with pytest.raises(InvariantViolation):
        check_ul_invariants(ledger)


def test_ul_lapse_invariant_raises() -> None:
    ledger = Ledger(
        rows=[_ul_row(policy_status=PolicyStatus.LAPSED, interest_credited=Decimal("1.00"))]
    )
    with pytest.raises(InvariantViolation):
        check_ul_invariants(ledger)


def test_term_expired_db_zero() -> None:
    ledger = Ledger(
        rows=[_term_row(policy_status=PolicyStatus.EXPIRED, death_benefit=Decimal("100.00"))]
    )
    with pytest.raises(InvariantViolation):
        check_term_invariants(ledger)


def test_charge_shortfall_invariant() -> None:
    ledger = Ledger(rows=[_ul_row(charges_paid=Decimal("5.00"), charge_shortfall=Decimal("5.00"))])
    check_ul_invariants(ledger)

    bad_ledger = Ledger(
        rows=[_ul_row(charges_paid=Decimal("4.00"), charge_shortfall=Decimal("5.00"))]
    )
    with pytest.raises(InvariantViolation):
        check_ul_invariants(bad_ledger)


def test_loan_balance_csv_invariant() -> None:
    ledger = Ledger(
        rows=[
            _ul_row(
                account_value_eop=Decimal("100.00"),
                cash_surrender_value=Decimal("50.00"),
                loan_balance=Decimal("40.00"),
            )
        ]
    )
    check_ul_invariants(ledger)

    bad_ledger = Ledger(
        rows=[
            _ul_row(
                account_value_eop=Decimal("100.00"),
                cash_surrender_value=Decimal("70.00"),
                loan_balance=Decimal("40.00"),
            )
        ]
    )
    with pytest.raises(InvariantViolation):
        check_ul_invariants(bad_ledger)
