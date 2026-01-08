"""Premium solve framework for OPIE."""

from __future__ import annotations

from decimal import Decimal

from opie.core.engine import _request_id, run_scenario
from opie.core.errors import EngineError
from opie.core.money import quantize_money
from opie.core.reporting import build_reporting_ledgers
from opie.core.types import (
    IllustrationRequest,
    IllustrationResult,
    Ledger,
    PolicyStatus,
    PremiumScheduleEntry,
    SolveMetadata,
    build_metadata,
)
from opie.products.base import ProductHooks

ZERO = Decimal("0")
TWO = Decimal("2")


def _premium_schedule_for_request(
    request: IllustrationRequest, premium: Decimal
) -> list[PremiumScheduleEntry]:
    return [
        PremiumScheduleEntry(
            start_month=1,
            end_month=request.duration_months,
            amount=quantize_money(premium, request.currency_code),
        )
    ]


def _run_with_premium(
    request: IllustrationRequest,
    scenario_name: str,
    hooks: ProductHooks,
    premium: Decimal,
) -> Ledger:
    scenario = getattr(request.scenarios, scenario_name)
    override = request.model_copy(
        update={"premium_schedule": _premium_schedule_for_request(request, premium)}
    )
    return run_scenario(override, scenario, scenario_name, hooks)


def _evaluate_keep_in_force(ledger: Ledger, target_month: int) -> bool:
    if len(ledger.rows) < target_month:
        return False
    row = ledger.rows[target_month - 1]
    return row.policy_status == PolicyStatus.IN_FORCE


def _evaluate_target_av(ledger: Ledger, target_month: int, target_av: Decimal) -> Decimal:
    if len(ledger.rows) < target_month:
        return Decimal("-1") * target_av
    row = ledger.rows[target_month - 1]
    if row.account_value_eop is None:
        return Decimal("-1") * target_av
    return row.account_value_eop - target_av


def _solve_for_scenario(
    request: IllustrationRequest,
    scenario_name: str,
    hooks: ProductHooks,
) -> Decimal:
    solve = request.solve
    if solve is None:
        raise EngineError("Solve configuration missing", product_code=request.product_code)
    if request.product_code != "simple_ul":
        raise EngineError(
            "Solve is only supported for simple_ul", product_code=request.product_code
        )

    low = solve.min_premium
    high = solve.max_premium

    for _ in range(solve.iterations):
        mid = (low + high) / TWO
        ledger = _run_with_premium(request, scenario_name, hooks, mid)
        if solve.mode == "keep_in_force":
            in_force = _evaluate_keep_in_force(ledger, solve.target_month)
            if in_force:
                high = mid
            else:
                low = mid
        else:
            target_av = solve.target_av or ZERO
            diff = _evaluate_target_av(ledger, solve.target_month, target_av)
            if diff >= ZERO:
                high = mid
            else:
                low = mid

    return quantize_money(high, request.currency_code)


def solve_illustration(request: IllustrationRequest, hooks: ProductHooks) -> IllustrationResult:
    if request.solve is None:
        raise EngineError("Solve configuration missing", product_code=request.product_code)

    solve = request.solve
    strategy = solve.strategy
    ledgers: dict[str, Ledger] = {}
    solved_premiums: dict[str, Decimal] = {}

    if strategy == "current_only":
        premium = _solve_for_scenario(request, "current", hooks)
        solved_premiums["current"] = premium
        for scenario_name in ("current", "guaranteed"):
            ledgers[scenario_name] = _run_with_premium(request, scenario_name, hooks, premium)
    elif strategy == "per_scenario":
        for scenario_name in ("current", "guaranteed"):
            premium = _solve_for_scenario(request, scenario_name, hooks)
            solved_premiums[scenario_name] = premium
            ledgers[scenario_name] = _run_with_premium(request, scenario_name, hooks, premium)
    else:
        raise EngineError(
            "Unknown solve strategy",
            product_code=request.product_code,
            values={"strategy": strategy},
        )

    solve_meta = SolveMetadata(
        mode=solve.mode,
        target_month=solve.target_month,
        target_av=solve.target_av,
        iterations=solve.iterations,
        tolerance=solve.tolerance,
        strategy=strategy,
        solved_premiums=solved_premiums,
    )
    metadata = build_metadata(request, solve=solve_meta)

    ledgers_by_currency = build_reporting_ledgers(request, ledgers)
    return IllustrationResult(
        request_id=_request_id(request),
        product_code=request.product_code,
        currency_code=request.currency_code,
        ledgers=ledgers,
        ledgers_by_currency=ledgers_by_currency,
        metadata=metadata,
    )
