from datetime import date
from decimal import Decimal

from opie.assumptions.models import ScenarioSet, ULScenarioAssumptions
from opie.core.engine import run_scenario
from opie.core.types import IllustrationRequest, PolicyStatus
from opie.products.base import ChargeResult, DeathBenefitResult, PremiumResult


class DummyHooks:
    def premium_and_loads(self, state, request, scenario):
        return PremiumResult(
            premium=Decimal("100"),
            premium_load=Decimal("10"),
            net_premium_to_av=Decimal("90"),
        )

    def monthly_charges(self, state, request, scenario, av_bop, premium_result):
        return ChargeResult(
            policy_fee=Decimal("5"),
            admin_fee=Decimal("0"),
            coi_charge=Decimal("0"),
            charges_total=Decimal("5"),
        )

    def policy_status(self, state, request, scenario):
        return PolicyStatus.IN_FORCE

    def term_fields(self, state, request, scenario):
        return None, None

    def death_benefit(self, state, request, scenario, av_bop, av_eop):
        return DeathBenefitResult(death_benefit=Decimal("100000"), corridor_uplift=Decimal("0"))

    def net_amount_at_risk(self, state, request, scenario, av_bop):
        return Decimal("100000")

    def surrender_charge(self, state, request, scenario, t):
        return Decimal("0")


class DummyLapseHooks(DummyHooks):
    def premium_and_loads(self, state, request, scenario):
        return PremiumResult(
            premium=Decimal("0"),
            premium_load=Decimal("0"),
            net_premium_to_av=Decimal("0"),
        )

    def monthly_charges(self, state, request, scenario, av_bop, premium_result):
        return ChargeResult(
            policy_fee=Decimal("200"),
            admin_fee=Decimal("0"),
            coi_charge=Decimal("0"),
            charges_total=Decimal("200"),
        )


class DummyShortfallHooks(DummyHooks):
    def premium_and_loads(self, state, request, scenario):
        if state.t == 1:
            return PremiumResult(
                premium=Decimal("10"),
                premium_load=Decimal("0"),
                net_premium_to_av=Decimal("10"),
            )
        return PremiumResult(
            premium=Decimal("0"),
            premium_load=Decimal("0"),
            net_premium_to_av=Decimal("0"),
        )

    def monthly_charges(self, state, request, scenario, av_bop, premium_result):
        if state.t == 1:
            charges = Decimal("0")
        else:
            charges = Decimal("15")
        return ChargeResult(
            policy_fee=charges,
            admin_fee=Decimal("0"),
            coi_charge=Decimal("0"),
            charges_total=charges,
        )


def _ul_request(duration_months: int) -> IllustrationRequest:
    scenario = ULScenarioAssumptions(
        crediting_rate_annual=Decimal("0.12"),
        premium_load_pct=Decimal("0.06"),
        monthly_policy_fee=Decimal("5"),
        monthly_per_thousand_admin_fee=Decimal("0"),
        coi_table={30: Decimal("0.20")},
        surrender_charge_schedule={1: Decimal("0")},
    )
    return IllustrationRequest(
        product_code="simple_ul",
        issue_age=30,
        issue_gender="M",
        risk_class="NT",
        face_amount=Decimal("100000"),
        issue_date=date(2025, 1, 1),
        duration_months=duration_months,
        premium_schedule=[
            {"start_month": 1, "end_month": duration_months, "amount": Decimal("100")}
        ],
        scenarios=ScenarioSet(current=scenario, guaranteed=scenario),
    )


def test_engine_monthly_progression() -> None:
    request = _ul_request(duration_months=2)
    ledger = run_scenario(request, request.scenarios.current, "current", DummyHooks())

    assert len(ledger.rows) == 2
    first = ledger.rows[0]
    second = ledger.rows[1]

    assert first.account_value_bop == Decimal("0.00")
    assert first.account_value_eop == Decimal("85.85")
    assert second.account_value_bop == Decimal("85.85")


def test_engine_lapse_emits_fatal_month() -> None:
    request = _ul_request(duration_months=12)
    ledger = run_scenario(request, request.scenarios.current, "current", DummyLapseHooks())

    assert len(ledger.rows) == 1
    row = ledger.rows[0]
    assert row.policy_status == PolicyStatus.LAPSED
    assert row.interest_credited == Decimal("0.00")
    assert row.account_value_eop == Decimal("0.00")
    assert row.death_benefit == Decimal("0.00")


def test_engine_charge_shortfall_when_insufficient_funds() -> None:
    scenario = ULScenarioAssumptions(
        crediting_rate_annual=Decimal("0.00"),
        premium_load_pct=Decimal("0.06"),
        monthly_policy_fee=Decimal("5"),
        monthly_per_thousand_admin_fee=Decimal("0"),
        coi_table={30: Decimal("0.20")},
        surrender_charge_schedule={1: Decimal("0")},
    )
    request = IllustrationRequest(
        product_code="simple_ul",
        issue_age=30,
        issue_gender="M",
        risk_class="NT",
        face_amount=Decimal("100000"),
        issue_date=date(2025, 1, 1),
        duration_months=2,
        premium_schedule=[{"start_month": 1, "end_month": 2, "amount": Decimal("100")}],
        scenarios=ScenarioSet(current=scenario, guaranteed=scenario),
    )
    ledger = run_scenario(request, request.scenarios.current, "current", DummyShortfallHooks())
    assert len(ledger.rows) == 2
    row = ledger.rows[1]
    assert row.policy_status == PolicyStatus.LAPSED
    assert row.charges_assessed == Decimal("15.00")
    assert row.charges_paid == Decimal("10.00")
    assert row.charge_shortfall == Decimal("5.00")
