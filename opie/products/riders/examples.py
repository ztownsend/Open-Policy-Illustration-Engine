"""Example rider implementations."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from opie.assumptions.models import ScenarioAssumptions
from opie.core.money import quantize_money
from opie.core.types import IllustrationRequest, RiderSpec
from opie.products.riders.base import RiderHooks


class FlatMonthlyChargeRider(RiderHooks):
    def monthly_charge(
        self,
        state: Any,
        request: IllustrationRequest,
        scenario: ScenarioAssumptions,
        rider: RiderSpec,
    ) -> Decimal:
        return quantize_money(rider.amount)
