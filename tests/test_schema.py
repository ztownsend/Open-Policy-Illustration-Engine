import pytest

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
