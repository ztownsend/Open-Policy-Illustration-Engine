"""IRC 7702 (GPT + CVAT) post-processor."""

from __future__ import annotations

from decimal import Decimal

from opie.assumptions.models import ScenarioAssumptions, Tax7702Assumptions
from opie.core.errors import AssumptionError
from opie.core.money import quantize_money
from opie.core.types import (
    IllustrationRequest,
    Ledger,
    Tax7702DebugRow,
    Tax7702Failure,
    Tax7702Report,
)

ZERO = Decimal("0")
TWELVE = Decimal("12")

SUPPORTED_PRODUCT_CODES = {"simple_ul", "wl_nonpar"}


def _years_elapsed(t: int, *, timing: str) -> Decimal:
    months = t - 1 if timing == "bop" else t
    return Decimal(months) / TWELVE


def _quantize(value: Decimal, request: IllustrationRequest) -> Decimal:
    return quantize_money(value, request.currency_code)


def _tax_enabled(scenario: ScenarioAssumptions) -> Tax7702Assumptions | None:
    tax = getattr(scenario, "tax_7702", None)
    if tax is None or not tax.enabled:
        return None
    return tax


def run_7702_checks(
    ledger: Ledger,
    assumptions: ScenarioAssumptions,
    request: IllustrationRequest,
    *,
    scenario_name: str,
) -> Tax7702Report | None:
    tax = _tax_enabled(assumptions)
    if tax is None:
        return None

    if request.product_code not in SUPPORTED_PRODUCT_CODES:
        raise AssumptionError(
            "7702 checks not supported for product",
            product_code=request.product_code,
            scenario=scenario_name,
        )

    failures: list[Tax7702Failure] = []
    debug_rows: list[Tax7702DebugRow] = []

    include_gpt = tax.test_type in {"gpt", "both"}
    include_cvat = tax.test_type in {"cvat", "both"}

    for row in ledger.rows:
        if include_gpt:
            gsp = tax.gpt_guideline_single_premium
            glp = tax.gpt_guideline_level_premium_annual
            if gsp is None or glp is None:
                raise AssumptionError(
                    "7702 GPT inputs missing",
                    product_code=request.product_code,
                    scenario=scenario_name,
                    t=row.t,
                )
            years_elapsed = _years_elapsed(row.t, timing=tax.gpt_premium_timing)
            glp_limit = glp * years_elapsed
            gpt_limit = gsp if gsp >= glp_limit else glp_limit
            cumulative = row.cumulative_premium or ZERO
            tolerance = tax.tolerance
            if cumulative > gpt_limit + tolerance:
                failures.append(
                    Tax7702Failure(
                        t=row.t,
                        test="gpt",
                        value=_quantize(cumulative, request),
                        limit=_quantize(gpt_limit, request),
                        reason="gpt",
                    )
                )
            if request.debug:
                debug_rows.append(
                    Tax7702DebugRow(
                        t=row.t,
                        test="gpt",
                        value=_quantize(cumulative, request),
                        limit=_quantize(gpt_limit, request),
                    )
                )

        if include_cvat:
            nsp = tax.cvat_net_single_premium
            if nsp is None:
                raise AssumptionError(
                    "7702 CVAT inputs missing",
                    product_code=request.product_code,
                    scenario=scenario_name,
                    t=row.t,
                )
            if tax.cvat_cash_value_basis == "csv":
                cash_value = row.cash_surrender_value
            elif tax.cvat_cash_value_basis == "av_eop":
                cash_value = row.account_value_eop
            else:
                if row.account_value_eop is None:
                    cash_value = None
                else:
                    adjustment = tax.cvat_cash_value_adjustment or ZERO
                    cash_value = row.account_value_eop + adjustment

            if cash_value is None:
                raise AssumptionError(
                    "7702 CVAT cash value missing",
                    product_code=request.product_code,
                    scenario=scenario_name,
                    t=row.t,
                )

            tolerance = tax.tolerance
            if cash_value > nsp + tolerance:
                failures.append(
                    Tax7702Failure(
                        t=row.t,
                        test="cvat",
                        value=_quantize(cash_value, request),
                        limit=_quantize(nsp, request),
                        reason="cvat",
                    )
                )
            if request.debug:
                debug_rows.append(
                    Tax7702DebugRow(
                        t=row.t,
                        test="cvat",
                        value=_quantize(cash_value, request),
                        limit=_quantize(nsp, request),
                    )
                )
            corridor_factors = (
                tax.corridor_factors
                if tax.corridor_factors is not None
                else getattr(assumptions, "corridor_factors", None)
            )
            if corridor_factors is not None:
                factor = corridor_factors.get(row.attained_age)
                if factor is None:
                    raise AssumptionError(
                        "7702 corridor factor missing",
                        product_code=request.product_code,
                        scenario=scenario_name,
                        t=row.t,
                        values={"attained_age": row.attained_age},
                    )
                corridor_min_db = cash_value * factor
                death_benefit = row.death_benefit
                if death_benefit is None:
                    raise AssumptionError(
                        "7702 corridor death benefit missing",
                        product_code=request.product_code,
                        scenario=scenario_name,
                        t=row.t,
                    )
                if death_benefit < corridor_min_db:
                    failures.append(
                        Tax7702Failure(
                            t=row.t,
                            test="cvat",
                            value=_quantize(death_benefit, request),
                            limit=_quantize(corridor_min_db, request),
                            reason="corridor",
                        )
                    )

    first_failure_t = min((failure.t for failure in failures), default=None)
    status = "fail" if failures else "pass"

    return Tax7702Report(
        test_type=tax.test_type,
        status=status,
        first_failure_t=first_failure_t,
        failures=failures,
        tax_7702_debug=debug_rows if request.debug else None,
    )
