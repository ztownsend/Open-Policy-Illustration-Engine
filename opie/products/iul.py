"""Indexed Universal Life (IUL) product hooks.

IUL extends SimpleUL with multi-account indexed crediting. All other
behavior (premium/loads, charges, DB, NAR, surrender) is inherited.

Interest crediting flow:
  For each index account:
    1. Compute the account's monthly rate based on strategy type
    2. Multiply by the account's share of av_mid (allocation × av_mid)
    3. Sum across all accounts for total interest credited

Strategy types:
  - fixed: rate = fixed_rate / 12
  - point_to_point: rate = min(max(illustrated × participation, floor), cap) / 12
  - monthly_average: rate = min(max(illustrated × participation, floor), cap) / 12
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from opie.assumptions.models import IULScenarioAssumptions, IndexAccount, ScenarioAssumptions
from opie.core.errors import AssumptionError
from opie.core.money import quantize_rate
from opie.core.types import IllustrationRequest
from opie.products.ul_simple import SimpleULHooks

ZERO = Decimal("0")
TWELVE = Decimal("12")


def _account_monthly_rate(account: IndexAccount) -> Decimal:
    """Compute monthly crediting rate for a single index account."""
    if account.strategy_type == "fixed":
        return quantize_rate(account.fixed_rate / TWELVE)

    # Indexed strategies: point_to_point, monthly_average
    raw = account.illustrated_rate * account.participation
    capped = min(raw, account.cap)
    floored = max(capped, account.floor)
    return quantize_rate(floored / TWELVE)


def _require_iul_scenario(scenario: ScenarioAssumptions) -> IULScenarioAssumptions:
    if not isinstance(scenario, IULScenarioAssumptions):
        raise AssumptionError("IUL scenario assumptions required")
    return scenario


class IndexedULHooks(SimpleULHooks):
    """IUL hooks — inherits all UL behavior, overrides interest crediting."""

    def credit_interest(
        self,
        state: Any,
        request: IllustrationRequest,
        scenario: ScenarioAssumptions,
        av_mid: Decimal,
    ) -> Decimal:
        iul_scenario = _require_iul_scenario(scenario)
        total_interest = ZERO
        for account in iul_scenario.index_accounts:
            account_av = av_mid * account.allocation
            monthly_rate = _account_monthly_rate(account)
            total_interest += account_av * monthly_rate
        return total_interest
