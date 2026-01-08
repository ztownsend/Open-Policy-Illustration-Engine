from opie.core.types import IllustrationResult, Ledger
from opie.core.versioning import CALC_VERSION, ROUNDING_POLICY_ID, SCHEMA_VERSION


def test_result_metadata_defaults_to_version_constants() -> None:
    result = IllustrationResult(
        request_id="req-1",
        product_code="simple_ul",
        ledgers={"current": Ledger(rows=[])},
    )
    assert result.metadata.calc_version == CALC_VERSION
    assert result.metadata.schema_version == SCHEMA_VERSION
    assert result.metadata.rounding_policy_id == ROUNDING_POLICY_ID
