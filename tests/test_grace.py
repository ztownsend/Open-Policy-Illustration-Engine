from datetime import date
from decimal import Decimal

from opie.assumptions.models import ScenarioSet, ULScenarioAssumptions
from opie.core.engine import run_scenario
from opie.core.types import IllustrationRequest, PolicyStatus
from opie.products.base import ChargeResult, DeathBenefitResult, PremiumResult


class NegativeHooks:
    def premium_and_loads(self, state, request, scenario):
        return PremiumResult(
            premium=Decimal("0"), premium_load=Decimal("0"), net_premium_to_av=Decimal("0")
        )

    def monthly_charges(self, state, request, scenario, av_bop, premium_result):
        return ChargeResult(
            policy_fee=Decimal("100"),
            admin_fee=Decimal("0"),
            coi_charge=Decimal("0"),
            charges_total=Decimal("100"),
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


def test_grace_period_delays_lapse() -> None:
    scenario = ULScenarioAssumptions(
        crediting_rate_annual=Decimal("0.00"),
        premium_load_pct=Decimal("0.00"),
        monthly_policy_fee=Decimal("0"),
        monthly_per_thousand_admin_fee=Decimal("0"),
        coi_table={30: Decimal("0.00")},
        surrender_charge_schedule={1: Decimal("0")},
    )
    request = IllustrationRequest(
        product_code="simple_ul",
        issue_age=30,
        issue_gender="M",
        risk_class="NT",
        face_amount=Decimal("100000"),
        issue_date=date(2025, 1, 1),
        duration_months=3,
        premium_schedule=[{"start_month": 1, "end_month": 3, "amount": Decimal("0")}],
        scenarios=ScenarioSet(current=scenario, guaranteed=scenario),
        grace_months=1,
    )

    ledger = run_scenario(request, request.scenarios.current, "current", NegativeHooks())
    assert len(ledger.rows) == 2
    assert ledger.rows[0].policy_status == PolicyStatus.IN_FORCE
    assert ledger.rows[1].policy_status == PolicyStatus.LAPSED
