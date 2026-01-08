from decimal import Decimal

import pytest

from opie.core.currency import CurrencyCode
from opie.core.types import IllustrationRequest


def test_ul_request_validates() -> None:
    payload = {
        "product_code": "simple_ul",
        "issue_age": 35,
        "issue_gender": "M",
        "risk_class": "NT",
        "face_amount": "250000",
        "issue_date": "2025-01-01",
        "duration_months": 120,
        "premium_schedule": [{"start_month": 1, "end_month": 120, "amount": "150"}],
        "scenarios": {
            "current": {
                "crediting_rate_annual": "0.04",
                "premium_load_pct": "0.06",
                "monthly_policy_fee": "5",
                "monthly_per_thousand_admin_fee": "0.10",
                "coi_table": {"35": "0.20"},
                "surrender_charge_schedule": {"1": "100"},
            },
            "guaranteed": {
                "crediting_rate_annual": "0.03",
                "premium_load_pct": "0.06",
                "monthly_policy_fee": "5",
                "monthly_per_thousand_admin_fee": "0.10",
                "coi_table": {"35": "0.25"},
                "surrender_charge_schedule": {"1": "150"},
            },
        },
        "death_benefit_option": "level",
        "minimum_account_value_floor": "0",
    }

    request = IllustrationRequest.model_validate(payload)
    assert request.product_code == "simple_ul"
    assert request.issue_age == 35
    assert request.currency_code == CurrencyCode.USD


def test_ul_request_allows_increasing_db_option() -> None:
    payload = {
        "product_code": "simple_ul",
        "issue_age": 35,
        "issue_gender": "M",
        "risk_class": "NT",
        "face_amount": "250000",
        "issue_date": "2025-01-01",
        "duration_months": 120,
        "premium_schedule": [{"start_month": 1, "end_month": 120, "amount": "150"}],
        "scenarios": {
            "current": {
                "crediting_rate_annual": "0.04",
                "premium_load_pct": "0.06",
                "monthly_policy_fee": "5",
                "monthly_per_thousand_admin_fee": "0.10",
                "coi_table": {"35": "0.20"},
                "surrender_charge_schedule": {"1": "100"},
            },
            "guaranteed": {
                "crediting_rate_annual": "0.03",
                "premium_load_pct": "0.06",
                "monthly_policy_fee": "5",
                "monthly_per_thousand_admin_fee": "0.10",
                "coi_table": {"35": "0.25"},
                "surrender_charge_schedule": {"1": "150"},
            },
        },
        "death_benefit_option": "increasing",
        "minimum_account_value_floor": "0",
    }

    request = IllustrationRequest.model_validate(payload)
    assert request.death_benefit_option == "increasing"
    assert request.currency_code == CurrencyCode.USD


def test_term_request_requires_term_length() -> None:
    payload = {
        "product_code": "level_term",
        "issue_age": 40,
        "issue_gender": "F",
        "risk_class": "NT",
        "face_amount": "100000",
        "issue_date": "2025-01-01",
        "duration_months": 120,
        "term_length_months": 120,
        "premium_schedule": [{"month": 1, "amount": "100"}],
        "scenarios": {
            "current": {"annual_premium": "1200"},
            "guaranteed": {"annual_premium": "1200"},
        },
    }

    request = IllustrationRequest.model_validate(payload)
    assert request.product_code == "level_term"
    assert request.currency_code == CurrencyCode.USD


def test_float_inputs_are_rejected() -> None:
    payload = {
        "product_code": "simple_ul",
        "issue_age": 35,
        "issue_gender": "M",
        "risk_class": "NT",
        "face_amount": 250000.25,
        "issue_date": "2025-01-01",
        "duration_months": 120,
        "premium_schedule": [{"start_month": 1, "end_month": 120, "amount": "150"}],
        "scenarios": {
            "current": {
                "crediting_rate_annual": "0.04",
                "premium_load_pct": "0.06",
                "monthly_policy_fee": "5",
                "monthly_per_thousand_admin_fee": "0.10",
                "coi_table": {"35": "0.20"},
                "surrender_charge_schedule": {"1": "100"},
            },
            "guaranteed": {
                "crediting_rate_annual": "0.03",
                "premium_load_pct": "0.06",
                "monthly_policy_fee": "5",
                "monthly_per_thousand_admin_fee": "0.10",
                "coi_table": {"35": "0.25"},
                "surrender_charge_schedule": {"1": "150"},
            },
        },
    }

    with pytest.raises(ValueError):
        IllustrationRequest.model_validate(payload)


def test_wl_request_validates() -> None:
    payload = {
        "product_code": "wl_nonpar",
        "issue_age": 45,
        "issue_gender": "F",
        "risk_class": "NT",
        "face_amount": "100000",
        "issue_date": "2025-01-01",
        "duration_months": 12,
        "premium_schedule": [{"start_month": 1, "end_month": 12, "amount": "0"}],
        "scenarios": {
            "current": {
                "cash_value_schedule": {"1": "100"},
                "surrender_value_schedule": {"1": "90"},
            },
            "guaranteed": {
                "cash_value_schedule": {"1": "100"},
                "surrender_value_schedule": {"1": "90"},
            },
        },
    }
    request = IllustrationRequest.model_validate(payload)
    assert request.product_code == "wl_nonpar"
    assert request.currency_code == CurrencyCode.USD


def test_annuity_request_validates() -> None:
    payload = {
        "product_code": "annuity_deferred",
        "issue_age": 60,
        "issue_gender": "M",
        "risk_class": "NT",
        "face_amount": "0",
        "issue_date": "2025-01-01",
        "duration_months": 12,
        "premium_schedule": [{"start_month": 1, "end_month": 1, "amount": "10000"}],
        "scenarios": {
            "current": {"crediting_rate_annual": "0.03", "surrender_charge_schedule": {"1": "0"}},
            "guaranteed": {
                "crediting_rate_annual": "0.03",
                "surrender_charge_schedule": {"1": "0"},
            },
        },
    }
    request = IllustrationRequest.model_validate(payload)
    assert request.product_code == "annuity_deferred"
    assert request.currency_code == CurrencyCode.USD


def test_request_allows_currency_code() -> None:
    payload = {
        "product_code": "level_term",
        "issue_age": 40,
        "issue_gender": "F",
        "risk_class": "NT",
        "face_amount": "100000",
        "issue_date": "2025-01-01",
        "duration_months": 120,
        "term_length_months": 120,
        "premium_schedule": [{"month": 1, "amount": "100"}],
        "currency_code": "EUR",
        "scenarios": {
            "current": {"annual_premium": "1200"},
            "guaranteed": {"annual_premium": "1200"},
        },
    }

    request = IllustrationRequest.model_validate(payload)
    assert request.currency_code == CurrencyCode.EUR


def test_request_rejects_unknown_currency_code() -> None:
    payload = {
        "product_code": "level_term",
        "issue_age": 40,
        "issue_gender": "F",
        "risk_class": "NT",
        "face_amount": "100000",
        "issue_date": "2025-01-01",
        "duration_months": 120,
        "term_length_months": 120,
        "premium_schedule": [{"month": 1, "amount": "100"}],
        "currency_code": "DOGE",
        "scenarios": {
            "current": {"annual_premium": "1200"},
            "guaranteed": {"annual_premium": "1200"},
        },
    }

    with pytest.raises(ValueError):
        IllustrationRequest.model_validate(payload)


def test_request_normalizes_monetary_inputs_by_currency() -> None:
    payload = {
        "product_code": "simple_ul",
        "issue_age": 35,
        "issue_gender": "M",
        "risk_class": "NT",
        "face_amount": "250000",
        "issue_date": "2025-01-01",
        "duration_months": 120,
        "currency_code": "EUR",
        "premium_schedule": [{"start_month": 1, "end_month": 120, "amount": "1.005"}],
        "scenarios": {
            "current": {
                "crediting_rate_annual": "0.04",
                "premium_load_pct": "0.06",
                "monthly_policy_fee": "1.005",
                "monthly_per_thousand_admin_fee": "0.10",
                "coi_table": {"35": "0.20"},
                "surrender_charge_schedule": {"1": "100"},
            },
            "guaranteed": {
                "crediting_rate_annual": "0.03",
                "premium_load_pct": "0.06",
                "monthly_policy_fee": "1.005",
                "monthly_per_thousand_admin_fee": "0.10",
                "coi_table": {"35": "0.25"},
                "surrender_charge_schedule": {"1": "150"},
            },
        },
        "death_benefit_option": "level",
        "minimum_account_value_floor": "0",
    }

    request = IllustrationRequest.model_validate(payload)
    assert request.currency_code == CurrencyCode.EUR
    assert request.premium_schedule[0].amount == Decimal("1.01")
    assert request.scenarios.current.monthly_policy_fee == Decimal("1.01")
    assert request.scenarios.guaranteed.monthly_policy_fee == Decimal("1.01")


def test_btc_precision_accepts_eight_decimals() -> None:
    payload = {
        "product_code": "level_term",
        "issue_age": 40,
        "issue_gender": "F",
        "risk_class": "NT",
        "face_amount": "0.00000001",
        "issue_date": "2025-01-01",
        "duration_months": 12,
        "term_length_months": 12,
        "currency_code": "BTC",
        "premium_schedule": [{"month": 1, "amount": "0.00000001"}],
        "scenarios": {
            "current": {"annual_premium": "0.00000001"},
            "guaranteed": {"annual_premium": "0.00000001"},
        },
    }

    request = IllustrationRequest.model_validate(payload)
    assert request.currency_code == CurrencyCode.BTC
    assert request.face_amount == Decimal("0.00000001")


def test_btc_precision_rejects_more_than_eight_decimals() -> None:
    payload = {
        "product_code": "level_term",
        "issue_age": 40,
        "issue_gender": "F",
        "risk_class": "NT",
        "face_amount": "0.000000001",
        "issue_date": "2025-01-01",
        "duration_months": 12,
        "term_length_months": 12,
        "currency_code": "BTC",
        "premium_schedule": [{"month": 1, "amount": "0.00000001"}],
        "scenarios": {
            "current": {"annual_premium": "0.00000001"},
            "guaranteed": {"annual_premium": "0.00000001"},
        },
    }

    with pytest.raises(ValueError):
        IllustrationRequest.model_validate(payload)


def test_request_normalizes_withdrawal_and_loan_schedules() -> None:
    payload = {
        "product_code": "level_term",
        "issue_age": 40,
        "issue_gender": "F",
        "risk_class": "NT",
        "face_amount": "100000",
        "issue_date": "2025-01-01",
        "duration_months": 12,
        "term_length_months": 12,
        "currency_code": "EUR",
        "premium_schedule": [{"month": 1, "amount": "100"}],
        "withdrawal_schedule": {"1": "1.005"},
        "loan_draw_schedule": {"1": "2.005"},
        "loan_repayment_schedule": {"1": "3.005"},
        "scenarios": {
            "current": {"annual_premium": "1200"},
            "guaranteed": {"annual_premium": "1200"},
        },
    }

    request = IllustrationRequest.model_validate(payload)
    assert request.withdrawal_schedule[1] == Decimal("1.01")
    assert request.loan_draw_schedule[1] == Decimal("2.01")
    assert request.loan_repayment_schedule[1] == Decimal("3.01")


def test_request_normalizes_solve_fields_by_currency() -> None:
    payload = {
        "product_code": "simple_ul",
        "issue_age": 35,
        "issue_gender": "M",
        "risk_class": "NT",
        "face_amount": "250000",
        "issue_date": "2025-01-01",
        "duration_months": 12,
        "currency_code": "EUR",
        "premium_schedule": [{"month": 1, "amount": "100"}],
        "solve": {
            "mode": "target_av",
            "target_month": 6,
            "target_av": "1.005",
            "min_premium": "1.005",
            "max_premium": "2.005",
            "tolerance": "0.005",
        },
        "scenarios": {
            "current": {
                "crediting_rate_annual": "0.04",
                "premium_load_pct": "0.06",
                "monthly_policy_fee": "5",
                "monthly_per_thousand_admin_fee": "0.10",
                "coi_table": {"35": "0.20"},
                "surrender_charge_schedule": {"1": "100"},
            },
            "guaranteed": {
                "crediting_rate_annual": "0.03",
                "premium_load_pct": "0.06",
                "monthly_policy_fee": "5",
                "monthly_per_thousand_admin_fee": "0.10",
                "coi_table": {"35": "0.25"},
                "surrender_charge_schedule": {"1": "150"},
            },
        },
        "death_benefit_option": "level",
        "minimum_account_value_floor": "0",
    }

    request = IllustrationRequest.model_validate(payload)
    assert request.solve.min_premium == Decimal("1.01")
    assert request.solve.max_premium == Decimal("2.01")
    assert request.solve.tolerance == Decimal("0.01")
    assert request.solve.target_av == Decimal("1.01")
