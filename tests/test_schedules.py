from decimal import Decimal

import pytest

from opie.assumptions.schedules import (
    expand_policy_year_schedule,
    normalize_month_schedule,
    parse_surrender_schedule,
)
from opie.core.errors import AssumptionError


def test_expand_policy_year_schedule_with_duration() -> None:
    schedule = {1: Decimal("100"), 2: Decimal("50")}
    expanded = expand_policy_year_schedule(schedule, duration_months=15)
    assert expanded[1] == Decimal("100")
    assert expanded[12] == Decimal("100")
    assert expanded[13] == Decimal("50")
    assert expanded[15] == Decimal("50")
    assert 16 not in expanded


def test_normalize_month_schedule_rejects_bad_month() -> None:
    with pytest.raises(AssumptionError):
        normalize_month_schedule({0: Decimal("10")})


def test_parse_surrender_schedule_mode_validation() -> None:
    with pytest.raises(AssumptionError):
        parse_surrender_schedule({1: Decimal("10")}, mode="bad")
