"""Product hook interfaces and result contracts."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Protocol

from opie.assumptions.models import ScenarioAssumptions
from opie.core.types import IllustrationRequest, PolicyStatus


@dataclass(frozen=True)
class PremiumResult:
    premium: Decimal
    premium_load: Decimal
    net_premium_to_av: Decimal


@dataclass(frozen=True)
class ChargeResult:
    policy_fee: Decimal
    admin_fee: Decimal
    coi_charge: Decimal
    charges_total: Decimal


@dataclass(frozen=True)
class DeathBenefitResult:
    death_benefit: Decimal
    corridor_uplift: Decimal


ZERO = Decimal("0")


def resolve_premium(schedule: Any, t: int) -> Decimal:
    """Resolve premium amount for month t from a premium schedule."""
    for rule in schedule or []:
        if rule.month is not None and rule.month == t:
            return rule.amount
        if rule.start_month is not None and rule.end_month is not None:
            if rule.start_month <= t <= rule.end_month:
                return rule.amount
    return ZERO


class ProductHooks(Protocol):
    def premium_and_loads(
        self,
        state: Any,
        request: IllustrationRequest,
        scenario: ScenarioAssumptions,
    ) -> PremiumResult: ...

    def monthly_charges(
        self,
        state: Any,
        request: IllustrationRequest,
        scenario: ScenarioAssumptions,
        av_bop: Decimal,
        premium_result: PremiumResult,
    ) -> ChargeResult: ...

    def policy_status(
        self,
        state: Any,
        request: IllustrationRequest,
        scenario: ScenarioAssumptions,
    ) -> PolicyStatus: ...

    def term_fields(
        self,
        state: Any,
        request: IllustrationRequest,
        scenario: ScenarioAssumptions,
    ) -> tuple[int | None, bool | None]: ...

    def death_benefit(
        self,
        state: Any,
        request: IllustrationRequest,
        scenario: ScenarioAssumptions,
        av_bop: Decimal,
        av_eop: Decimal,
    ) -> DeathBenefitResult: ...

    def net_amount_at_risk(
        self,
        state: Any,
        request: IllustrationRequest,
        scenario: ScenarioAssumptions,
        av_bop: Decimal,
    ) -> Decimal: ...

    def surrender_charge(
        self,
        state: Any,
        request: IllustrationRequest,
        scenario: ScenarioAssumptions,
        t: int,
    ) -> Decimal: ...
