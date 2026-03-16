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
from opie.core.money import quantize_money, quantize_rate
from opie.core.types import IllustrationRequest
from opie.products.ul_simple import SimpleULHooks

ZERO = Decimal("0")
TWELVE = Decimal("12")

# Sentinel for "no debug detail" — avoids None ambiguity
_NO_DETAIL: list[dict[str, str]] = []


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
    """IUL hooks — inherits all UL behavior, overrides interest crediting.

    After credit_interest() is called, last_account_detail contains the
    per-account breakdown (populated only when request.debug is True).
    """

    def __init__(self) -> None:
        self.last_account_detail: list[dict[str, str]] = _NO_DETAIL

    def credit_interest(
        self,
        state: Any,
        request: IllustrationRequest,
        scenario: ScenarioAssumptions,
        av_mid: Decimal,
    ) -> Decimal:
        iul_scenario = _require_iul_scenario(scenario)
        total_interest = ZERO
        detail: list[dict[str, str]] = []
        currency_code = request.currency_code
        for account in iul_scenario.index_accounts:
            account_av = av_mid * account.allocation
            monthly_rate = _account_monthly_rate(account)
            account_interest = account_av * monthly_rate
            total_interest += account_interest
            if request.debug:
                detail.append(
                    {
                        "name": account.name,
                        "allocation": str(account.allocation),
                        "strategy": account.strategy_type,
                        "monthly_rate": str(quantize_rate(monthly_rate)),
                        "interest": str(quantize_money(account_interest, currency_code)),
                    }
                )
        self.last_account_detail = detail if request.debug else _NO_DETAIL
        return total_interest
