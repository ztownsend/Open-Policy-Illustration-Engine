from datetime import date
from decimal import Decimal

from opie.assumptions.models import ScenarioSet, ULScenarioAssumptions
from opie.core.currency import currency_quantum
from opie.core.engine import run_illustration
from opie.core.ledger import dumps_json
from opie.core.types import IllustrationRequest
from opie.products.ul_simple import SimpleULHooks


def _request(debug: bool) -> IllustrationRequest:
    scenario = ULScenarioAssumptions(
        crediting_rate_annual=Decimal("0.04"),
        premium_load_pct=Decimal("0.06"),
        monthly_policy_fee=Decimal("5"),
        monthly_per_thousand_admin_fee=Decimal("0.10"),
        coi_table={30: Decimal("0.20")},
        surrender_charge_schedule={1: Decimal("0")},
    )
    return IllustrationRequest(
        product_code="simple_ul",
        issue_age=30,
        issue_gender="M",
        risk_class="NT",
        face_amount=Decimal("100000"),
        issue_date=date(2025, 1, 1),
        duration_months=1,
        premium_schedule=[{"start_month": 1, "end_month": 1, "amount": Decimal("100")}],
        scenarios=ScenarioSet(current=scenario, guaranteed=scenario),
        debug=debug,
    )


def test_debug_fields_included_when_enabled() -> None:
    request = _request(debug=True)
    result = run_illustration(request, SimpleULHooks())
    payload = dumps_json(result)
    assert "debug_av_mid_raw_unrounded" in payload
    row = result.ledgers["current"].rows[0]
    expected_exponent = currency_quantum(result.currency_code).as_tuple().exponent
    assert row.debug_av_mid_raw_unrounded is not None
    assert row.debug_interest_credited_unrounded is not None
    assert row.debug_account_value_eop_unrounded is not None
    assert row.debug_av_mid_raw_unrounded.as_tuple().exponent == expected_exponent
    assert row.debug_interest_credited_unrounded.as_tuple().exponent == expected_exponent
    assert row.debug_account_value_eop_unrounded.as_tuple().exponent == expected_exponent


def test_debug_fields_omitted_when_disabled() -> None:
    request = _request(debug=False)
    result = run_illustration(request, SimpleULHooks())
    payload = dumps_json(result)
    assert "debug_av_mid_raw_unrounded" not in payload
