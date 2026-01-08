"""Invariant checks for ledgers."""

from __future__ import annotations

from decimal import Decimal

from opie.core.errors import EngineError, InvariantViolation
from opie.core.types import Ledger, PolicyStatus

ZERO = Decimal("0")


def _ensure(condition: bool, message: str, *, t: int | None = None) -> None:
    if not condition:
        raise InvariantViolation(message, t=t)


def check_ul_invariants(ledger: Ledger) -> None:
    prev_cumulative: Decimal | None = None
    for row in ledger.rows:
        if row.account_value_eop is not None:
            _ensure(row.account_value_eop >= ZERO, "AV_eop negative", t=row.t)
        if row.cash_surrender_value is not None and row.account_value_eop is not None:
            _ensure(
                row.cash_surrender_value <= row.account_value_eop, "CSV exceeds AV_eop", t=row.t
            )
        if row.loan_balance is not None and row.account_value_eop is not None:
            _ensure(row.loan_balance >= ZERO, "loan_balance negative", t=row.t)
            _ensure(
                row.cash_surrender_value <= row.account_value_eop - row.loan_balance,
                "CSV exceeds AV_eop minus loan balance",
                t=row.t,
            )
        if row.corridor_uplift is not None:
            _ensure(row.corridor_uplift >= ZERO, "corridor_uplift negative", t=row.t)
            _ensure(
                row.death_benefit >= row.corridor_uplift,
                "death_benefit below corridor_uplift",
                t=row.t,
            )
        if row.charges_assessed is not None:
            charges_paid = row.charges_paid or ZERO
            charge_shortfall = row.charge_shortfall or ZERO
            _ensure(charge_shortfall >= ZERO, "charge_shortfall negative", t=row.t)
            _ensure(
                charges_paid + charge_shortfall == row.charges_assessed,
                "charges_assessed != charges_paid + charge_shortfall",
                t=row.t,
            )
        if row.rider_charges is not None:
            _ensure(row.rider_charges >= ZERO, "rider_charges negative", t=row.t)
        if prev_cumulative is not None:
            _ensure(
                row.cumulative_premium >= prev_cumulative, "cumulative_premium decreased", t=row.t
            )
        prev_cumulative = row.cumulative_premium

        if row.policy_status == PolicyStatus.LAPSED:
            _ensure(row.interest_credited == ZERO, "interest credited on lapse", t=row.t)
            _ensure(row.account_value_eop == ZERO, "AV_eop not zero on lapse", t=row.t)
            _ensure(row.death_benefit == ZERO, "DB not zero on lapse", t=row.t)


def check_term_invariants(ledger: Ledger) -> None:
    prev_cumulative: Decimal | None = None
    for row in ledger.rows:
        if prev_cumulative is not None:
            _ensure(
                row.cumulative_premium >= prev_cumulative, "cumulative_premium decreased", t=row.t
            )
        prev_cumulative = row.cumulative_premium

        if row.charges_assessed is not None:
            charges_paid = row.charges_paid or ZERO
            charge_shortfall = row.charge_shortfall or ZERO
            _ensure(charge_shortfall >= ZERO, "charge_shortfall negative", t=row.t)
            _ensure(
                charges_paid + charge_shortfall == row.charges_assessed,
                "charges_assessed != charges_paid + charge_shortfall",
                t=row.t,
            )

        if row.policy_status == PolicyStatus.EXPIRED:
            _ensure(row.death_benefit == ZERO, "DB not zero on expired term", t=row.t)


def check_invariants(product_code: str, ledger: Ledger) -> None:
    if product_code == "simple_ul":
        check_ul_invariants(ledger)
        return
    if product_code == "level_term":
        check_term_invariants(ledger)
        return
    raise EngineError("Unknown product_code for invariants", product_code=product_code)
