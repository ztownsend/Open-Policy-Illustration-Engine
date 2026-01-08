import json
from pathlib import Path

from opie import run_illustration
from opie.core.ledger import dumps_json
from opie.core.types import IllustrationRequest

GOLDEN_DIR = Path("tests/golden")


def _assert_golden(request_path: Path, base_name: str) -> None:
    payload = json.loads(request_path.read_text())
    request = IllustrationRequest.model_validate(payload)
    result = run_illustration(request)

    for scenario in ("current", "guaranteed"):
        payload = {
            "product_code": result.product_code,
            "scenario": scenario,
            "metadata": result.metadata,
            "ledger": result.ledgers[scenario],
        }
        expected = (GOLDEN_DIR / f"{base_name}_{scenario}.json").read_text()
        assert dumps_json(payload) == expected


def test_term_golden() -> None:
    _assert_golden(Path("examples/term_request.json"), "term")


def test_term_eur_golden() -> None:
    _assert_golden(Path("examples/term_eur_request.json"), "term_eur")


def test_term_btc_golden() -> None:
    _assert_golden(Path("examples/term_btc_request.json"), "term_btc")
