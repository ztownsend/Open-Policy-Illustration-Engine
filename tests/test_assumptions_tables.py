from decimal import Decimal

import pytest

from opie.assumptions.tables import coi_lookup, load_coi_table_csv, load_coi_table_json
from opie.core.errors import AssumptionError


def test_load_coi_table_csv(tmp_path) -> None:
    path = tmp_path / "coi.csv"
    path.write_text("age,rate\n35,0.20\n36,0.25\n")
    table = load_coi_table_csv(path)
    assert table[35] == Decimal("0.20")
    assert table[36] == Decimal("0.25")


def test_load_coi_table_csv_requires_headers(tmp_path) -> None:
    path = tmp_path / "coi.csv"
    path.write_text("foo,bar\n35,0.20\n")
    with pytest.raises(AssumptionError):
        load_coi_table_csv(path)


def test_load_coi_table_json(tmp_path) -> None:
    path = tmp_path / "coi.json"
    path.write_text('{"35": "0.20", "36": "0.25"}')
    table = load_coi_table_json(path)
    assert table[35] == Decimal("0.20")


def test_coi_lookup_missing_age() -> None:
    with pytest.raises(AssumptionError):
        coi_lookup({35: Decimal("0.20")}, 40)
