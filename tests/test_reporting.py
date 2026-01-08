from datetime import date
from decimal import Decimal

import pytest

from opie import run_illustration
from opie.assumptions.models import ScenarioSet, TermScenarioAssumptions, ULScenarioAssumptions
from opie.core.currency import CurrencyCode
from opie.core.money import quantize_money
from opie.core.types import IllustrationRequest, PolicyStatus


def _term_request_with_reporting(
    *,
    fx_rate: Decimal = Decimal("0.5"),
) -> IllustrationRequest:
    scenario = TermScenarioAssumptions()
    return IllustrationRequest(
        product_code="level_term",
        issue_age=40,
        issue_gender="F",
        risk_class="NT",
        face_amount=Decimal("100"),
        issue_date=date(2025, 1, 1),
        duration_months=1,
        term_length_months=1,
        premium_schedule=[{"month": 1, "amount": Decimal("10")}],
        scenarios=ScenarioSet(current=scenario, guaranteed=scenario),
        reporting_currencies=[CurrencyCode.EUR],
        fx_rates={CurrencyCode.EUR: fx_rate},
    )


def _ul_request_with_debug(*, include_debug_fields: bool) -> IllustrationRequest:
    scenario = ULScenarioAssumptions(
        crediting_rate_annual=Decimal("0.00"),
        premium_load_pct=Decimal("0.00"),
        monthly_policy_fee=Decimal("0"),
        monthly_per_thousand_admin_fee=Decimal("0"),
        coi_table={30: Decimal("0.00")},
        surrender_charge_schedule={1: Decimal("0")},
    )
    return IllustrationRequest(
        product_code="simple_ul",
        issue_age=30,
        issue_gender="M",
        risk_class="NT",
        face_amount=Decimal("1000"),
        issue_date=date(2025, 1, 1),
        duration_months=1,
        premium_schedule=[{"month": 1, "amount": Decimal("10")}],
        scenarios=ScenarioSet(current=scenario, guaranteed=scenario),
        debug=True,
        reporting_currencies=[CurrencyCode.EUR],
        fx_rates={CurrencyCode.EUR: Decimal("2")},
        reporting_include_debug_fields=include_debug_fields,
    )


def test_reporting_requires_fx_rates() -> None:
    payload = {
        "product_code": "level_term",
        "issue_age": 40,
        "issue_gender": "F",
        "risk_class": "NT",
        "face_amount": "100",
        "issue_date": "2025-01-01",
        "duration_months": 1,
        "term_length_months": 1,
        "premium_schedule": [{"month": 1, "amount": "10"}],
        "reporting_currencies": ["EUR"],
        "scenarios": {"current": {}, "guaranteed": {}},
    }
    with pytest.raises(ValueError):
        IllustrationRequest.model_validate(payload)


def test_reporting_requires_rate_for_each_currency() -> None:
    payload = {
        "product_code": "level_term",
        "issue_age": 40,
        "issue_gender": "F",
        "risk_class": "NT",
        "face_amount": "100",
        "issue_date": "2025-01-01",
        "duration_months": 1,
        "term_length_months": 1,
        "premium_schedule": [{"month": 1, "amount": "10"}],
        "reporting_currencies": ["EUR", "BTC"],
        "fx_rates": {"EUR": "0.5"},
        "scenarios": {"current": {}, "guaranteed": {}},
    }
    with pytest.raises(ValueError):
        IllustrationRequest.model_validate(payload)


def test_reporting_not_requested_returns_none() -> None:
    scenario = TermScenarioAssumptions()
    request = IllustrationRequest(
        product_code="level_term",
        issue_age=40,
        issue_gender="F",
        risk_class="NT",
        face_amount=Decimal("100"),
        issue_date=date(2025, 1, 1),
        duration_months=1,
        term_length_months=1,
        premium_schedule=[{"month": 1, "amount": Decimal("10")}],
        scenarios=ScenarioSet(current=scenario, guaranteed=scenario),
    )
    result = run_illustration(request)
    assert result.ledgers_by_currency is None


def test_reporting_allows_base_currency_with_fx_rate() -> None:
    scenario = TermScenarioAssumptions()
    request = IllustrationRequest(
        product_code="level_term",
        issue_age=40,
        issue_gender="F",
        risk_class="NT",
        face_amount=Decimal("100"),
        issue_date=date(2025, 1, 1),
        duration_months=1,
        term_length_months=1,
        premium_schedule=[{"month": 1, "amount": Decimal("10")}],
        scenarios=ScenarioSet(current=scenario, guaranteed=scenario),
        reporting_currencies=[CurrencyCode.USD],
        fx_rates={CurrencyCode.USD: Decimal("1")},
    )
    result = run_illustration(request)
    base_row = result.ledgers["current"].rows[0]
    converted_row = result.ledgers_by_currency[CurrencyCode.USD]["current"].rows[0]
    assert converted_row.premium == base_row.premium


def test_reporting_converts_monetary_fields() -> None:
    request = _term_request_with_reporting(fx_rate=Decimal("0.5"))
    result = run_illustration(request)
    ledger = result.ledgers_by_currency[CurrencyCode.EUR]["current"]
    row = ledger.rows[0]
    assert row.premium == Decimal("5.00")
    assert row.death_benefit == Decimal("50.00")
    assert row.policy_status == PolicyStatus.IN_FORCE
    assert result.metadata.reporting_currencies == [CurrencyCode.EUR]
    assert result.metadata.fx_rates == {CurrencyCode.EUR: Decimal("0.5")}
    assert result.metadata.reporting_include_debug_fields is False


def test_reporting_preserves_non_monetary_fields() -> None:
    request = _term_request_with_reporting(fx_rate=Decimal("0.5"))
    result = run_illustration(request)
    base_row = result.ledgers["current"].rows[0]
    converted_row = result.ledgers_by_currency[CurrencyCode.EUR]["current"].rows[0]

    assert converted_row.policy_status == base_row.policy_status
    assert converted_row.term_month == base_row.term_month
    assert converted_row.coverage_in_force == base_row.coverage_in_force


def test_reporting_debug_fields_omitted_by_default() -> None:
    request = _ul_request_with_debug(include_debug_fields=False)
    result = run_illustration(request)
    ledger = result.ledgers_by_currency[CurrencyCode.EUR]["current"]
    row = ledger.rows[0]
    assert row.debug_av_mid_raw_unrounded is None
    assert row.debug_interest_credited_unrounded is None


def test_reporting_debug_fields_included_and_converted() -> None:
    request = _ul_request_with_debug(include_debug_fields=True)
    result = run_illustration(request)
    base_row = result.ledgers["current"].rows[0]
    converted_row = result.ledgers_by_currency[CurrencyCode.EUR]["current"].rows[0]

    expected_av_mid = quantize_money(
        base_row.debug_av_mid_raw_unrounded * Decimal("2"),
        CurrencyCode.EUR,
    )
    expected_eop = quantize_money(
        base_row.debug_account_value_eop_unrounded * Decimal("2"),
        CurrencyCode.EUR,
    )
    assert converted_row.debug_av_mid_raw_unrounded == expected_av_mid
    assert converted_row.debug_account_value_eop_unrounded == expected_eop


def test_reporting_multiple_currencies() -> None:
    scenario = TermScenarioAssumptions()
    request = IllustrationRequest(
        product_code="level_term",
        issue_age=40,
        issue_gender="F",
        risk_class="NT",
        face_amount=Decimal("100"),
        issue_date=date(2025, 1, 1),
        duration_months=1,
        term_length_months=1,
        premium_schedule=[{"month": 1, "amount": Decimal("10")}],
        scenarios=ScenarioSet(current=scenario, guaranteed=scenario),
        reporting_currencies=[CurrencyCode.EUR, CurrencyCode.BTC],
        fx_rates={
            CurrencyCode.EUR: Decimal("0.5"),
            CurrencyCode.BTC: Decimal("0.0001"),
        },
    )
    result = run_illustration(request)
    assert CurrencyCode.EUR in result.ledgers_by_currency
    assert CurrencyCode.BTC in result.ledgers_by_currency

    eur_row = result.ledgers_by_currency[CurrencyCode.EUR]["current"].rows[0]
    btc_row = result.ledgers_by_currency[CurrencyCode.BTC]["current"].rows[0]
    assert eur_row.premium == Decimal("5.00")
    assert btc_row.premium == quantize_money(Decimal("10") * Decimal("0.0001"), CurrencyCode.BTC)


def test_reporting_dedupes_currency_list() -> None:
    payload = {
        "product_code": "level_term",
        "issue_age": 40,
        "issue_gender": "F",
        "risk_class": "NT",
        "face_amount": "100",
        "issue_date": "2025-01-01",
        "duration_months": 1,
        "term_length_months": 1,
        "premium_schedule": [{"month": 1, "amount": "10"}],
        "reporting_currencies": ["EUR", "EUR", "BTC"],
        "fx_rates": {"EUR": "0.5", "BTC": "0.0001"},
        "scenarios": {"current": {}, "guaranteed": {}},
    }
    request = IllustrationRequest.model_validate(payload)
    assert request.reporting_currencies == [CurrencyCode.EUR, CurrencyCode.BTC]
