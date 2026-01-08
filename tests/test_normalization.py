from decimal import Decimal

import pytest

from opie.assumptions.loaders import load_annuity_assumptions, load_ul_assumptions
from opie.assumptions.models import (
    AnnuityScenarioAssumptions,
    TermScenarioAssumptions,
    ULScenarioAssumptions,
    WLScenarioAssumptions,
)
from opie.core.currency import CurrencyCode
from opie.core.normalization import normalize_scenario_money


def test_normalize_ul_scenario_money_quantizes_fields() -> None:
    scenario = ULScenarioAssumptions(
        crediting_rate_annual=Decimal("0.04"),
        premium_load_pct=Decimal("0.01"),
        monthly_policy_fee=Decimal("1.005"),
        monthly_per_thousand_admin_fee=Decimal("0.105"),
        coi_table={30: Decimal("0.20")},
        surrender_charge_schedule={1: Decimal("1.005")},
    )
    normalized = normalize_scenario_money(scenario, CurrencyCode.EUR)
    assert normalized.monthly_policy_fee == Decimal("1.01")
    assert normalized.monthly_per_thousand_admin_fee == Decimal("0.11")
    assert normalized.surrender_charge_schedule[1] == Decimal("1.01")


def test_normalize_term_scenario_money_quantizes_annual_premium() -> None:
    scenario = TermScenarioAssumptions(
        annual_premium=Decimal("1.005"),
        term_modal_factor=Decimal("1.0"),
    )
    normalized = normalize_scenario_money(scenario, CurrencyCode.EUR)
    assert normalized.annual_premium == Decimal("1.01")
    assert normalized.term_modal_factor == Decimal("1.0")


def test_normalize_wl_scenario_money_quantizes_schedules() -> None:
    scenario = WLScenarioAssumptions(
        cash_value_schedule={1: Decimal("1.005")},
        surrender_value_schedule={1: Decimal("2.005")},
    )
    normalized = normalize_scenario_money(scenario, CurrencyCode.EUR)
    assert normalized.cash_value_schedule[1] == Decimal("1.01")
    assert normalized.surrender_value_schedule[1] == Decimal("2.01")


def test_normalize_annuity_scenario_money_quantizes_schedule() -> None:
    scenario = AnnuityScenarioAssumptions(
        crediting_rate_annual=Decimal("0.03"),
        surrender_charge_schedule={1: Decimal("1.005")},
    )
    normalized = normalize_scenario_money(scenario, CurrencyCode.EUR)
    assert normalized.surrender_charge_schedule[1] == Decimal("1.01")


def test_load_ul_assumptions_rejects_btc_over_precision() -> None:
    payload = {
        "crediting_rate_annual": "0.04",
        "premium_load_pct": "0.01",
        "monthly_policy_fee": "0.000000001",
        "monthly_per_thousand_admin_fee": "0",
        "coi_table": {"30": "0.20"},
        "surrender_charge_schedule": {"1": "0"},
    }
    with pytest.raises(ValueError):
        load_ul_assumptions(payload, currency_code=CurrencyCode.BTC)


def test_load_annuity_assumptions_quantizes_schedule() -> None:
    payload = {
        "crediting_rate_annual": "0.03",
        "surrender_charge_schedule": {"1": "1.005"},
    }
    scenario = load_annuity_assumptions(payload, currency_code=CurrencyCode.EUR)
    assert scenario.surrender_charge_schedule[1] == Decimal("1.01")
