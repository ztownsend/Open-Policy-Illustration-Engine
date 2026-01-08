"""Rider hook interfaces."""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Protocol

from opie.assumptions.models import ScenarioAssumptions
from opie.core.types import IllustrationRequest, RiderSpec


class RiderHooks(Protocol):
    def monthly_charge(
        self,
        state: Any,
        request: IllustrationRequest,
        scenario: ScenarioAssumptions,
        rider: RiderSpec,
    ) -> Decimal: ...
