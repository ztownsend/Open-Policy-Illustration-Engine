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
