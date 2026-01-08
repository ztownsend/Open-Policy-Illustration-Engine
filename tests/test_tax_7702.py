from datetime import date
from decimal import Decimal

import pytest

from opie import run_illustration
from opie.assumptions.models import (
    ScenarioSet,
    Tax7702Assumptions,
    TermScenarioAssumptions,
    ULScenarioAssumptions,
)
from opie.core.errors import AssumptionError
from opie.core.ledger import dumps_json
from opie.core.types import IllustrationRequest, Ledger, LedgerRow, PolicyStatus
from opie.tax.irc_7702 import run_7702_checks


def _ul_request(*, scenario: ULScenarioAssumptions, debug: bool = False) -> IllustrationRequest:
    return IllustrationRequest(
        product_code="simple_ul",
        issue_age=30,
        issue_gender="M",
        risk_class="NT",
        face_amount=Decimal("100000"),
        issue_date=date(2025, 1, 1),
        duration_months=12,
        premium_schedule=[{"month": 1, "amount": Decimal("100")}],
        scenarios=ScenarioSet(current=scenario, guaranteed=scenario),
        debug=debug,
    )


def _ledger(*, rows: list[LedgerRow]) -> Ledger:
    return Ledger(rows=rows)


def _row(
    *,
    t: int,
    cumulative_premium: Decimal,
    cash_surrender_value: Decimal,
    account_value_eop: Decimal,
    death_benefit: Decimal,
    attained_age: int = 35,
) -> LedgerRow:
    return LedgerRow(
        t=t,
        policy_year=1,
        attained_age=attained_age,
        policy_status=PolicyStatus.IN_FORCE,
        premium=cumulative_premium,
        cumulative_premium=cumulative_premium,
        death_benefit=death_benefit,
        account_value_eop=account_value_eop,
        cash_surrender_value=cash_surrender_value,
    )


def test_gpt_timing_bop_vs_eop() -> None:
    tax_bop = Tax7702Assumptions(
        enabled=True,
        test_type="gpt",
        gpt_guideline_single_premium=Decimal("0"),
        gpt_guideline_level_premium_annual=Decimal("1200"),
        gpt_premium_timing="bop",
    )
    tax_eop = tax_bop.model_copy(update={"gpt_premium_timing": "eop"})

    scenario_bop = ULScenarioAssumptions(
        crediting_rate_annual=Decimal("0.04"),
        premium_load_pct=Decimal("0.01"),
        monthly_policy_fee=Decimal("1"),
        monthly_per_thousand_admin_fee=Decimal("0"),
        coi_table={30: Decimal("0.20")},
        surrender_charge_schedule={1: Decimal("0")},
        tax_7702=tax_bop,
    )
    scenario_eop = scenario_bop.model_copy(update={"tax_7702": tax_eop})

    rows = [
        _row(
            t=1,
            cumulative_premium=Decimal("10.00"),
            cash_surrender_value=Decimal("0.00"),
            account_value_eop=Decimal("0.00"),
            death_benefit=Decimal("100000.00"),
        )
    ]

    request = _ul_request(scenario=scenario_bop)
    ledger = _ledger(rows=rows)
    report_bop = run_7702_checks(ledger, scenario_bop, request, scenario_name="current")
    assert report_bop.status == "fail"
    assert report_bop.first_failure_t == 1

    request_eop = _ul_request(scenario=scenario_eop)
    report_eop = run_7702_checks(ledger, scenario_eop, request_eop, scenario_name="current")
    assert report_eop.status == "pass"
    assert report_eop.first_failure_t is None


def test_gpt_tolerance_boundary_passes() -> None:
    tax = Tax7702Assumptions(
        enabled=True,
        test_type="gpt",
        gpt_guideline_single_premium=Decimal("100"),
        gpt_guideline_level_premium_annual=Decimal("0"),
        tolerance=Decimal("0.01"),
    )
    scenario = ULScenarioAssumptions(
        crediting_rate_annual=Decimal("0.04"),
        premium_load_pct=Decimal("0.01"),
        monthly_policy_fee=Decimal("1"),
        monthly_per_thousand_admin_fee=Decimal("0"),
        coi_table={30: Decimal("0.20")},
        surrender_charge_schedule={1: Decimal("0")},
        tax_7702=tax,
    )
    row = _row(
        t=1,
        cumulative_premium=Decimal("100.01"),
        cash_surrender_value=Decimal("0.00"),
        account_value_eop=Decimal("0.00"),
        death_benefit=Decimal("100000.00"),
    )
    report = run_7702_checks(
        _ledger(rows=[row]), scenario, _ul_request(scenario=scenario), scenario_name="current"
    )
    assert report.status == "pass"
    assert report.failures == []


def test_cvat_basis_csv_av_eop_custom() -> None:
    tax_csv = Tax7702Assumptions(
        enabled=True,
        test_type="cvat",
        cvat_net_single_premium=Decimal("150"),
        cvat_cash_value_basis="csv",
    )
    tax_av = tax_csv.model_copy(update={"cvat_cash_value_basis": "av_eop"})
    tax_custom = tax_csv.model_copy(
        update={"cvat_cash_value_basis": "custom", "cvat_cash_value_adjustment": Decimal("20")}
    )

    scenario = ULScenarioAssumptions(
        crediting_rate_annual=Decimal("0.04"),
        premium_load_pct=Decimal("0.01"),
        monthly_policy_fee=Decimal("1"),
        monthly_per_thousand_admin_fee=Decimal("0"),
        coi_table={30: Decimal("0.20")},
        surrender_charge_schedule={1: Decimal("0")},
        tax_7702=tax_csv,
    )

    row = _row(
        t=1,
        cumulative_premium=Decimal("0.00"),
        cash_surrender_value=Decimal("200.00"),
        account_value_eop=Decimal("140.00"),
        death_benefit=Decimal("100000.00"),
    )

    report_csv = run_7702_checks(
        _ledger(rows=[row]), scenario, _ul_request(scenario=scenario), scenario_name="current"
    )
    assert report_csv.status == "fail"
    assert report_csv.failures[0].value == Decimal("200.00")

    scenario_av = scenario.model_copy(update={"tax_7702": tax_av})
    report_av = run_7702_checks(
        _ledger(rows=[row]), scenario_av, _ul_request(scenario=scenario_av), scenario_name="current"
    )
    assert report_av.status == "pass"

    scenario_custom = scenario.model_copy(update={"tax_7702": tax_custom})
    report_custom = run_7702_checks(
        _ledger(rows=[row]),
        scenario_custom,
        _ul_request(scenario=scenario_custom),
        scenario_name="current",
    )
    assert report_custom.status == "fail"
    assert report_custom.failures[0].value == Decimal("160.00")


def test_cvat_corridor_failure() -> None:
    tax = Tax7702Assumptions(
        enabled=True,
        test_type="cvat",
        cvat_net_single_premium=Decimal("1000"),
        cvat_cash_value_basis="csv",
        corridor_factors={35: Decimal("2")},
    )
    scenario = ULScenarioAssumptions(
        crediting_rate_annual=Decimal("0.04"),
        premium_load_pct=Decimal("0.01"),
        monthly_policy_fee=Decimal("1"),
        monthly_per_thousand_admin_fee=Decimal("0"),
        coi_table={30: Decimal("0.20")},
        surrender_charge_schedule={1: Decimal("0")},
        tax_7702=tax,
    )
    row = _row(
        t=1,
        cumulative_premium=Decimal("0.00"),
        cash_surrender_value=Decimal("100.00"),
        account_value_eop=Decimal("100.00"),
        death_benefit=Decimal("150.00"),
    )
    report = run_7702_checks(
        _ledger(rows=[row]), scenario, _ul_request(scenario=scenario), scenario_name="current"
    )
    assert report.status == "fail"
    assert report.failures[0].reason == "corridor"


def test_debug_rows_emitted_when_enabled() -> None:
    tax = Tax7702Assumptions(
        enabled=True,
        test_type="gpt",
        gpt_guideline_single_premium=Decimal("0"),
        gpt_guideline_level_premium_annual=Decimal("1200"),
    )
    scenario = ULScenarioAssumptions(
        crediting_rate_annual=Decimal("0.04"),
        premium_load_pct=Decimal("0.01"),
        monthly_policy_fee=Decimal("1"),
        monthly_per_thousand_admin_fee=Decimal("0"),
        coi_table={30: Decimal("0.20")},
        surrender_charge_schedule={1: Decimal("0")},
        tax_7702=tax,
    )
    rows = [
        _row(
            t=1,
            cumulative_premium=Decimal("10.00"),
            cash_surrender_value=Decimal("0.00"),
            account_value_eop=Decimal("0.00"),
            death_benefit=Decimal("100000.00"),
        ),
        _row(
            t=2,
            cumulative_premium=Decimal("20.00"),
            cash_surrender_value=Decimal("0.00"),
            account_value_eop=Decimal("0.00"),
            death_benefit=Decimal("100000.00"),
        ),
    ]
    request = _ul_request(scenario=scenario, debug=True)
    report = run_7702_checks(_ledger(rows=rows), scenario, request, scenario_name="current")
    assert report.tax_7702_debug is not None
    assert len(report.tax_7702_debug) == 2


def test_unsupported_product_raises() -> None:
    tax = Tax7702Assumptions(
        enabled=True,
        test_type="gpt",
        gpt_guideline_single_premium=Decimal("100"),
        gpt_guideline_level_premium_annual=Decimal("100"),
    )
    term_scenario = TermScenarioAssumptions(tax_7702=tax)
    request = IllustrationRequest(
        product_code="level_term",
        issue_age=40,
        issue_gender="F",
        risk_class="NT",
        face_amount=Decimal("100000"),
        issue_date=date(2025, 1, 1),
        duration_months=12,
        term_length_months=12,
        premium_schedule=[{"month": 1, "amount": Decimal("100")}],
        scenarios=ScenarioSet(current=term_scenario, guaranteed=term_scenario),
    )
    with pytest.raises(AssumptionError):
        run_illustration(request)


def test_run_illustration_includes_tax_report() -> None:
    tax = Tax7702Assumptions(
        enabled=True,
        test_type="gpt",
        gpt_guideline_single_premium=Decimal("150"),
        gpt_guideline_level_premium_annual=Decimal("1000"),
    )
    scenario = ULScenarioAssumptions(
        crediting_rate_annual=Decimal("0.04"),
        premium_load_pct=Decimal("0.01"),
        monthly_policy_fee=Decimal("1"),
        monthly_per_thousand_admin_fee=Decimal("0"),
        coi_table={30: Decimal("0.20")},
        surrender_charge_schedule={1: Decimal("0")},
        tax_7702=tax,
    )
    result = run_illustration(_ul_request(scenario=scenario))
    assert result.metadata.tax_7702 is not None
    assert "current" in result.metadata.tax_7702
    assert "guaranteed" in result.metadata.tax_7702


def test_tax_7702_debug_omitted_when_debug_false() -> None:
    tax = Tax7702Assumptions(
        enabled=True,
        test_type="gpt",
        gpt_guideline_single_premium=Decimal("150"),
        gpt_guideline_level_premium_annual=Decimal("1000"),
    )
    scenario = ULScenarioAssumptions(
        crediting_rate_annual=Decimal("0.04"),
        premium_load_pct=Decimal("0.01"),
        monthly_policy_fee=Decimal("1"),
        monthly_per_thousand_admin_fee=Decimal("0"),
        coi_table={30: Decimal("0.20")},
        surrender_charge_schedule={1: Decimal("0")},
        tax_7702=tax,
    )
    result = run_illustration(_ul_request(scenario=scenario, debug=False))
    payload = dumps_json(result)
    assert "tax_7702_debug" not in payload


def test_gpt_limit_uses_max_of_gsp_and_glp() -> None:
    tax = Tax7702Assumptions(
        enabled=True,
        test_type="gpt",
        gpt_guideline_single_premium=Decimal("100"),
        gpt_guideline_level_premium_annual=Decimal("1200"),
        gpt_premium_timing="eop",
    )
    scenario = ULScenarioAssumptions(
        crediting_rate_annual=Decimal("0.04"),
        premium_load_pct=Decimal("0.01"),
        monthly_policy_fee=Decimal("1"),
        monthly_per_thousand_admin_fee=Decimal("0"),
        coi_table={30: Decimal("0.20")},
        surrender_charge_schedule={1: Decimal("0")},
        tax_7702=tax,
    )
    row = _row(
        t=12,
        cumulative_premium=Decimal("1300.00"),
        cash_surrender_value=Decimal("0.00"),
        account_value_eop=Decimal("0.00"),
        death_benefit=Decimal("100000.00"),
    )
    report = run_7702_checks(
        _ledger(rows=[row]), scenario, _ul_request(scenario=scenario), scenario_name="current"
    )
    assert report.status == "fail"
    assert report.failures[0].limit == Decimal("1200.00")


def test_both_tests_fail_when_either_fails() -> None:
    tax = Tax7702Assumptions(
        enabled=True,
        test_type="both",
        gpt_guideline_single_premium=Decimal("150"),
        gpt_guideline_level_premium_annual=Decimal("1000"),
        cvat_net_single_premium=Decimal("100"),
        cvat_cash_value_basis="csv",
    )
    scenario = ULScenarioAssumptions(
        crediting_rate_annual=Decimal("0.04"),
        premium_load_pct=Decimal("0.01"),
        monthly_policy_fee=Decimal("1"),
        monthly_per_thousand_admin_fee=Decimal("0"),
        coi_table={30: Decimal("0.20")},
        surrender_charge_schedule={1: Decimal("0")},
        tax_7702=tax,
    )
    row = _row(
        t=1,
        cumulative_premium=Decimal("200.00"),
        cash_surrender_value=Decimal("50.00"),
        account_value_eop=Decimal("50.00"),
        death_benefit=Decimal("100000.00"),
    )
    report = run_7702_checks(
        _ledger(rows=[row]), scenario, _ul_request(scenario=scenario), scenario_name="current"
    )
    assert report.status == "fail"
    assert report.failures[0].test == "gpt"


def test_first_failure_t_is_earliest_across_tests() -> None:
    tax = Tax7702Assumptions(
        enabled=True,
        test_type="both",
        gpt_guideline_single_premium=Decimal("150"),
        gpt_guideline_level_premium_annual=Decimal("1000"),
        cvat_net_single_premium=Decimal("100"),
        cvat_cash_value_basis="csv",
    )
    scenario = ULScenarioAssumptions(
        crediting_rate_annual=Decimal("0.04"),
        premium_load_pct=Decimal("0.01"),
        monthly_policy_fee=Decimal("1"),
        monthly_per_thousand_admin_fee=Decimal("0"),
        coi_table={30: Decimal("0.20")},
        surrender_charge_schedule={1: Decimal("0")},
        tax_7702=tax,
    )
    rows = [
        _row(
            t=1,
            cumulative_premium=Decimal("200.00"),
            cash_surrender_value=Decimal("50.00"),
            account_value_eop=Decimal("50.00"),
            death_benefit=Decimal("100000.00"),
        ),
        _row(
            t=2,
            cumulative_premium=Decimal("250.00"),
            cash_surrender_value=Decimal("200.00"),
            account_value_eop=Decimal("200.00"),
            death_benefit=Decimal("100000.00"),
        ),
    ]
    report = run_7702_checks(
        _ledger(rows=rows), scenario, _ul_request(scenario=scenario), scenario_name="current"
    )
    assert report.status == "fail"
    assert report.first_failure_t == 1


def test_tax_7702_disabled_returns_none() -> None:
    tax = Tax7702Assumptions(enabled=False, test_type="gpt")
    scenario = ULScenarioAssumptions(
        crediting_rate_annual=Decimal("0.04"),
        premium_load_pct=Decimal("0.01"),
        monthly_policy_fee=Decimal("1"),
        monthly_per_thousand_admin_fee=Decimal("0"),
        coi_table={30: Decimal("0.20")},
        surrender_charge_schedule={1: Decimal("0")},
        tax_7702=tax,
    )
    report = run_7702_checks(
        _ledger(rows=[]), scenario, _ul_request(scenario=scenario), scenario_name="current"
    )
    assert report is None


def test_cvat_cash_value_missing_raises() -> None:
    tax = Tax7702Assumptions(
        enabled=True,
        test_type="cvat",
        cvat_net_single_premium=Decimal("100"),
        cvat_cash_value_basis="csv",
    )
    scenario = ULScenarioAssumptions(
        crediting_rate_annual=Decimal("0.04"),
        premium_load_pct=Decimal("0.01"),
        monthly_policy_fee=Decimal("1"),
        monthly_per_thousand_admin_fee=Decimal("0"),
        coi_table={30: Decimal("0.20")},
        surrender_charge_schedule={1: Decimal("0")},
        tax_7702=tax,
    )
    row = LedgerRow(
        t=1,
        policy_year=1,
        attained_age=35,
        policy_status=PolicyStatus.IN_FORCE,
        premium=Decimal("0.00"),
        cumulative_premium=Decimal("0.00"),
        death_benefit=Decimal("100000.00"),
        cash_surrender_value=None,
        account_value_eop=Decimal("0.00"),
    )
    with pytest.raises(AssumptionError):
        run_7702_checks(
            _ledger(rows=[row]), scenario, _ul_request(scenario=scenario), scenario_name="current"
        )


def test_custom_basis_requires_account_value() -> None:
    tax = Tax7702Assumptions(
        enabled=True,
        test_type="cvat",
        cvat_net_single_premium=Decimal("100"),
        cvat_cash_value_basis="custom",
        cvat_cash_value_adjustment=Decimal("10"),
    )
    scenario = ULScenarioAssumptions(
        crediting_rate_annual=Decimal("0.04"),
        premium_load_pct=Decimal("0.01"),
        monthly_policy_fee=Decimal("1"),
        monthly_per_thousand_admin_fee=Decimal("0"),
        coi_table={30: Decimal("0.20")},
        surrender_charge_schedule={1: Decimal("0")},
        tax_7702=tax,
    )
    row = LedgerRow(
        t=1,
        policy_year=1,
        attained_age=35,
        policy_status=PolicyStatus.IN_FORCE,
        premium=Decimal("0.00"),
        cumulative_premium=Decimal("0.00"),
        death_benefit=Decimal("100000.00"),
        cash_surrender_value=Decimal("0.00"),
        account_value_eop=None,
    )
    with pytest.raises(AssumptionError):
        run_7702_checks(
            _ledger(rows=[row]), scenario, _ul_request(scenario=scenario), scenario_name="current"
        )


def test_corridor_factors_fallback_to_scenario() -> None:
    tax = Tax7702Assumptions(
        enabled=True,
        test_type="cvat",
        cvat_net_single_premium=Decimal("1000"),
        cvat_cash_value_basis="csv",
    )
    scenario = ULScenarioAssumptions(
        crediting_rate_annual=Decimal("0.04"),
        premium_load_pct=Decimal("0.01"),
        monthly_policy_fee=Decimal("1"),
        monthly_per_thousand_admin_fee=Decimal("0"),
        coi_table={30: Decimal("0.20")},
        surrender_charge_schedule={1: Decimal("0")},
        corridor_factors={35: Decimal("2")},
        tax_7702=tax,
    )
    row = _row(
        t=1,
        cumulative_premium=Decimal("0.00"),
        cash_surrender_value=Decimal("100.00"),
        account_value_eop=Decimal("100.00"),
        death_benefit=Decimal("150.00"),
    )
    report = run_7702_checks(
        _ledger(rows=[row]), scenario, _ul_request(scenario=scenario), scenario_name="current"
    )
    assert report.status == "fail"
    assert report.failures[0].reason == "corridor"


def test_debug_rows_include_gpt_and_cvat_for_both() -> None:
    tax = Tax7702Assumptions(
        enabled=True,
        test_type="both",
        gpt_guideline_single_premium=Decimal("150"),
        gpt_guideline_level_premium_annual=Decimal("1000"),
        cvat_net_single_premium=Decimal("100"),
        cvat_cash_value_basis="csv",
    )
    scenario = ULScenarioAssumptions(
        crediting_rate_annual=Decimal("0.04"),
        premium_load_pct=Decimal("0.01"),
        monthly_policy_fee=Decimal("1"),
        monthly_per_thousand_admin_fee=Decimal("0"),
        coi_table={30: Decimal("0.20")},
        surrender_charge_schedule={1: Decimal("0")},
        tax_7702=tax,
    )
    rows = [
        _row(
            t=1,
            cumulative_premium=Decimal("10.00"),
            cash_surrender_value=Decimal("0.00"),
            account_value_eop=Decimal("0.00"),
            death_benefit=Decimal("100000.00"),
        ),
        _row(
            t=2,
            cumulative_premium=Decimal("20.00"),
            cash_surrender_value=Decimal("0.00"),
            account_value_eop=Decimal("0.00"),
            death_benefit=Decimal("100000.00"),
        ),
    ]
    request = _ul_request(scenario=scenario, debug=True)
    report = run_7702_checks(_ledger(rows=rows), scenario, request, scenario_name="current")
    tests = {entry.test for entry in report.tax_7702_debug}
    assert tests == {"gpt", "cvat"}
    assert len(report.tax_7702_debug) == 4
