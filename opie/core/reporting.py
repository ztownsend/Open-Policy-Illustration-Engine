"""Reporting currency conversions for ledgers."""

from __future__ import annotations

from decimal import Decimal

from opie.core.currency import CurrencyCode
from opie.core.money import quantize_money
from opie.core.types import IllustrationRequest, Ledger, LedgerRow

MONETARY_FIELDS = (
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
)

DEBUG_FIELDS = (
    "debug_av_mid_raw_unrounded",
    "debug_interest_credited_unrounded",
    "debug_account_value_eop_unrounded",
)


def _convert_amount(value: Decimal, fx_rate: Decimal, target_currency: CurrencyCode) -> Decimal:
    return quantize_money(value * fx_rate, target_currency)


def convert_ledger(
    ledger: Ledger,
    *,
    fx_rate: Decimal,
    target_currency: CurrencyCode,
    include_debug_fields: bool,
) -> Ledger:
    converted_rows: list[LedgerRow] = []
    for row in ledger.rows:
        data = row.model_dump(mode="python")
        if not include_debug_fields:
            for field in DEBUG_FIELDS:
                data.pop(field, None)
        for field in MONETARY_FIELDS:
            value = data.get(field)
            if value is None:
                continue
            data[field] = _convert_amount(value, fx_rate, target_currency)
        if include_debug_fields:
            for field in DEBUG_FIELDS:
                value = data.get(field)
                if value is None:
                    continue
                data[field] = _convert_amount(value, fx_rate, target_currency)
        converted_rows.append(LedgerRow(**data))
    return Ledger(
        frequency=ledger.frequency,
        rows=converted_rows,
        interest_mode=ledger.interest_mode,
    )


def build_reporting_ledgers(
    request: IllustrationRequest,
    base_ledgers: dict[str, Ledger],
) -> dict[CurrencyCode, dict[str, Ledger]] | None:
    if not request.reporting_currencies:
        return None
    if request.fx_rates is None:
        raise ValueError("fx_rates is required when reporting_currencies is provided")

    ledgers_by_currency: dict[CurrencyCode, dict[str, Ledger]] = {}
    for currency in request.reporting_currencies:
        fx_rate = request.fx_rates.get(currency)
        if fx_rate is None:
            raise ValueError(f"fx_rates missing for reporting currency: {currency.value}")
        ledgers_by_currency[currency] = {
            scenario: convert_ledger(
                ledger,
                fx_rate=fx_rate,
                target_currency=currency,
                include_debug_fields=request.reporting_include_debug_fields,
            )
            for scenario, ledger in base_ledgers.items()
        }
    return ledgers_by_currency
