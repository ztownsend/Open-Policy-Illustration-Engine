from __future__ import annotations

from datetime import date
from decimal import Decimal

from opie.assumptions.models import ScenarioSet, TermScenarioAssumptions
from opie.core.engine import ProjectionState
from opie.core.types import IllustrationRequest, PolicyStatus
from opie.products.term_level import LevelTermHooks


def _term_request(modal_factor: Decimal | None = None) -> IllustrationRequest:
    scenario = TermScenarioAssumptions(annual_premium=Decimal("1200"))
    return IllustrationRequest(
        product_code="level_term",
        issue_age=40,
        issue_gender="F",
        risk_class="NT",
        face_amount=Decimal("250000"),
        issue_date=date(2025, 1, 1),
        duration_months=24,
        term_length_months=12,
        modal_factor=modal_factor,
        premium_schedule=None,
        scenarios=ScenarioSet(current=scenario, guaranteed=scenario),
    )


def test_term_policy_status_expiry() -> None:
    request = _term_request()
    hooks = LevelTermHooks()
    in_force_state = ProjectionState(
        t=12,
        policy_year=1,
        attained_age=40,
        cumulative_premium=Decimal("0"),
        av_eop_prev=Decimal("0"),
        scenario_name="current",
    )
    expired_state = ProjectionState(
        t=13,
        policy_year=2,
        attained_age=41,
        cumulative_premium=Decimal("0"),
        av_eop_prev=Decimal("0"),
        scenario_name="current",
    )
    assert (
        hooks.policy_status(in_force_state, request, request.scenarios.current)
        == PolicyStatus.IN_FORCE
    )
    assert (
        hooks.policy_status(expired_state, request, request.scenarios.current)
        == PolicyStatus.EXPIRED
    )


def test_term_premium_from_annual_default_modal() -> None:
    request = _term_request()
    hooks = LevelTermHooks()
    state = ProjectionState(
        t=1,
        policy_year=1,
        attained_age=40,
        cumulative_premium=Decimal("0"),
        av_eop_prev=Decimal("0"),
        scenario_name="current",
    )
    result = hooks.premium_and_loads(state, request, request.scenarios.current)
    assert result.premium == Decimal("100.00")


def test_term_premium_with_modal_factor_override() -> None:
    request = _term_request(modal_factor=Decimal("0.10"))
    hooks = LevelTermHooks()
    state = ProjectionState(
        t=1,
        policy_year=1,
        attained_age=40,
        cumulative_premium=Decimal("0"),
        av_eop_prev=Decimal("0"),
        scenario_name="current",
    )
    result = hooks.premium_and_loads(state, request, request.scenarios.current)
    assert result.premium == Decimal("120.00")
