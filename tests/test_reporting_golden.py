import json
from pathlib import Path

from opie import run_illustration
from opie.core.currency import CurrencyCode
from opie.core.ledger import dumps_json
from opie.core.types import IllustrationRequest

GOLDEN_DIR = Path("tests/golden")


def test_term_reporting_eur_golden() -> None:
    request_path = Path("examples/term_reporting_request.json")
    payload = json.loads(request_path.read_text())
    request = IllustrationRequest.model_validate(payload)
    result = run_illustration(request)

    for scenario in ("current", "guaranteed"):
        payload = {
            "product_code": result.product_code,
            "scenario": scenario,
            "currency_code": "EUR",
            "metadata": result.metadata,
            "ledger": result.ledgers_by_currency[CurrencyCode.EUR][scenario],
        }
        expected = (GOLDEN_DIR / f"term_reporting_eur_{scenario}.json").read_text()
        assert dumps_json(payload) == expected
