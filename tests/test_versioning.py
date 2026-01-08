from opie.core.currency import CurrencyCode
from opie.core.types import IllustrationResult, Ledger
from opie.core.versioning import CALC_VERSION, ROUNDING_POLICY_ID, SCHEMA_VERSION


def test_result_metadata_defaults_to_version_constants() -> None:
    result = IllustrationResult(
        request_id="req-1",
        product_code="simple_ul",
        currency_code=CurrencyCode.USD,
        ledgers={"current": Ledger(rows=[])},
    )
    assert result.metadata.calc_version == CALC_VERSION
    assert result.metadata.schema_version == SCHEMA_VERSION
    assert result.metadata.rounding_policy_id == ROUNDING_POLICY_ID
    assert result.metadata.currency_code == CurrencyCode.USD
    assert result.metadata.reporting_currencies is None
    assert result.metadata.fx_rates is None
    assert result.metadata.reporting_include_debug_fields is None
    assert result.metadata.tax_7702 is None
