"""Invariant checks for ledgers."""

from __future__ import annotations

from decimal import Decimal

from opie.core.currency import CurrencyCode
from opie.core.errors import EngineError, InvariantViolation
from opie.core.money import quantize_money
from opie.core.types import Ledger, PolicyStatus

ZERO = Decimal("0")
MONEY_FIELDS = (
    "premium",
    "cumulative_premium",
    "death_benefit",
    "account_value_bop",
    "premium_load",
    "net_premium_to_av",
    "policy_fee",
    "coi_charge",
    "admin_fee",
    "charges_total",
    "charges_assessed",
    "charges_paid",
    "charge_shortfall",
    "rider_charges",
    "net_amount_at_risk",
    "account_value_mid_raw",
    "interest_credited",
    "account_value_eop",
    "surrender_charge",
    "cash_surrender_value",
    "corridor_uplift",
    "withdrawal",
    "loan_draw",
    "loan_repayment",
    "loan_interest",
    "loan_balance",
    "debug_av_mid_raw_unrounded",
    "debug_interest_credited_unrounded",
    "debug_account_value_eop_unrounded",
)


def _ensure(condition: bool, message: str, *, t: int | None = None) -> None:
    if not condition:
        raise InvariantViolation(message, t=t)


def _ensure_non_negative(value: Decimal | None, label: str, *, t: int) -> None:
    if value is None:
        return
    _ensure(value >= ZERO, f"{label} negative", t=t)


def _check_charge_invariants(row) -> None:
    if row.charges_assessed is None:
        return
    charges_paid = row.charges_paid or ZERO
    charge_shortfall = row.charge_shortfall or ZERO
    _ensure(charge_shortfall >= ZERO, "charge_shortfall negative", t=row.t)
    _ensure(
        charges_paid + charge_shortfall == row.charges_assessed,
        "charges_assessed != charges_paid + charge_shortfall",
        t=row.t,
    )
    expected = (
        (row.policy_fee or ZERO)
        + (row.admin_fee or ZERO)
        + (row.coi_charge or ZERO)
        + (row.rider_charges or ZERO)
    )
    _ensure(
        row.charges_assessed == expected,
        "charges_assessed != policy_fee + admin_fee + coi_charge + rider_charges",
        t=row.t,
    )
    if row.charges_total is not None:
        _ensure(
            row.charges_total == row.charges_assessed,
            "charges_total != charges_assessed",
            t=row.t,
        )


def _check_premium_invariants(row) -> None:
    _ensure_non_negative(row.premium, "premium", t=row.t)
    _ensure_non_negative(row.premium_load, "premium_load", t=row.t)
    _ensure_non_negative(row.net_premium_to_av, "net_premium_to_av", t=row.t)
    _ensure_non_negative(row.cumulative_premium, "cumulative_premium", t=row.t)


def _check_cash_value_invariants(row) -> None:
    _ensure_non_negative(row.account_value_bop, "account_value_bop", t=row.t)
    _ensure_non_negative(row.account_value_eop, "account_value_eop", t=row.t)
    _ensure_non_negative(row.cash_surrender_value, "cash_surrender_value", t=row.t)
    _ensure_non_negative(row.surrender_charge, "surrender_charge", t=row.t)
    if row.cash_surrender_value is not None and row.account_value_eop is not None:
        _ensure(
            row.cash_surrender_value <= row.account_value_eop,
            "CSV exceeds AV_eop",
            t=row.t,
        )


def _check_withdrawal_loan_fields(row, *, require_zero: bool) -> None:
    fields = {
        "withdrawal": row.withdrawal,
        "loan_draw": row.loan_draw,
        "loan_repayment": row.loan_repayment,
        "loan_interest": row.loan_interest,
        "loan_balance": row.loan_balance,
    }
    for label, value in fields.items():
        if value is None:
            continue
        if require_zero:
            _ensure(value == ZERO, f"{label} must be zero", t=row.t)
        else:
            _ensure_non_negative(value, label, t=row.t)


def _check_money_quantization(ledger: Ledger, *, currency_code: CurrencyCode) -> None:
    for row in ledger.rows:
        for field in MONEY_FIELDS:
            value = getattr(row, field, None)
            if value is None:
                continue
            expected = quantize_money(value, currency_code)
            _ensure(value == expected, f"{field} not quantized", t=row.t)
            _ensure(
                value.as_tuple().exponent == expected.as_tuple().exponent,
                f"{field} not quantized to currency precision",
                t=row.t,
            )


def _check_common_rows(ledger: Ledger, *, currency_code: CurrencyCode) -> None:
    _check_money_quantization(ledger, currency_code=currency_code)
    prev_cumulative: Decimal | None = None
    for row in ledger.rows:
        _check_premium_invariants(row)
        _check_charge_invariants(row)
        _ensure_non_negative(row.rider_charges, "rider_charges", t=row.t)
        _ensure_non_negative(row.corridor_uplift, "corridor_uplift", t=row.t)
        _ensure_non_negative(row.net_amount_at_risk, "net_amount_at_risk", t=row.t)
        if prev_cumulative is not None:
            _ensure(
                row.cumulative_premium >= prev_cumulative,
                "cumulative_premium decreased",
                t=row.t,
            )
        prev_cumulative = row.cumulative_premium


def check_ul_invariants(
    ledger: Ledger, *, currency_code: CurrencyCode = CurrencyCode.USD
) -> None:
    _check_common_rows(ledger, currency_code=currency_code)
    for row in ledger.rows:
        _check_cash_value_invariants(row)
        _check_withdrawal_loan_fields(row, require_zero=False)
        if row.loan_balance is not None and row.account_value_eop is not None:
            _ensure(row.loan_balance >= ZERO, "loan_balance negative", t=row.t)
            _ensure(
                row.cash_surrender_value <= row.account_value_eop - row.loan_balance,
                "CSV exceeds AV_eop minus loan balance",
                t=row.t,
            )
        if row.corridor_uplift is not None:
            _ensure(
                row.death_benefit >= row.corridor_uplift,
                "death_benefit below corridor_uplift",
                t=row.t,
            )
        if row.policy_status == PolicyStatus.LAPSED:
            _ensure(row.interest_credited == ZERO, "interest credited on lapse", t=row.t)
            _ensure(row.account_value_eop == ZERO, "AV_eop not zero on lapse", t=row.t)
            _ensure(row.death_benefit == ZERO, "DB not zero on lapse", t=row.t)


def check_term_invariants(
    ledger: Ledger, *, currency_code: CurrencyCode = CurrencyCode.USD
) -> None:
    _check_common_rows(ledger, currency_code=currency_code)
    for row in ledger.rows:
        _check_withdrawal_loan_fields(row, require_zero=True)
        if row.policy_status == PolicyStatus.EXPIRED:
            _ensure(row.death_benefit == ZERO, "DB not zero on expired term", t=row.t)


def check_wl_invariants(
    ledger: Ledger, *, currency_code: CurrencyCode = CurrencyCode.USD
) -> None:
    _check_common_rows(ledger, currency_code=currency_code)
    for row in ledger.rows:
        _check_cash_value_invariants(row)
        _check_withdrawal_loan_fields(row, require_zero=True)


def check_annuity_invariants(
    ledger: Ledger, *, currency_code: CurrencyCode = CurrencyCode.USD
) -> None:
    _check_common_rows(ledger, currency_code=currency_code)
    for row in ledger.rows:
        _check_cash_value_invariants(row)
        _check_withdrawal_loan_fields(row, require_zero=True)
        _ensure(row.death_benefit == ZERO, "death_benefit must be zero", t=row.t)


def check_invariants(
    product_code: str,
    ledger: Ledger,
    *,
    currency_code: CurrencyCode = CurrencyCode.USD,
) -> None:
    if product_code == "simple_ul":
        check_ul_invariants(ledger, currency_code=currency_code)
        return
    if product_code == "level_term":
        check_term_invariants(ledger, currency_code=currency_code)
        return
    if product_code == "wl_nonpar":
        check_wl_invariants(ledger, currency_code=currency_code)
        return
    if product_code in {"annuity_deferred", "annuity_spia"}:
        check_annuity_invariants(ledger, currency_code=currency_code)
        return
    raise EngineError("Unknown product_code for invariants", product_code=product_code)
