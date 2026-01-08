import json
from pathlib import Path

from opie import run_illustration
from opie.core.ledger import dumps_json
from opie.core.types import IllustrationRequest

GOLDEN_DIR = Path("tests/golden")


def _load_request(path: Path) -> IllustrationRequest:
    payload = json.loads(path.read_text())
    return IllustrationRequest.model_validate(payload)


def _assert_golden(request_path: Path, base_name: str) -> None:
    request = _load_request(request_path)
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


def test_ul_simple_golden() -> None:
    _assert_golden(Path("examples/ul_simple_request.json"), "ul_simple")


def test_ul_simple_eur_golden() -> None:
    _assert_golden(Path("examples/ul_simple_eur_request.json"), "ul_simple_eur")


def test_ul_simple_btc_golden() -> None:
    _assert_golden(Path("examples/ul_simple_btc_request.json"), "ul_simple_btc")


def test_ul_simple_effective_golden() -> None:
    _assert_golden(Path("examples/ul_simple_effective_request.json"), "ul_simple_effective")


def test_ul_lapse_golden() -> None:
    _assert_golden(Path("examples/ul_lapse_request.json"), "ul_lapse")


def test_ul_simple_7702_golden() -> None:
    _assert_golden(Path("examples/ul_simple_7702_request.json"), "ul_simple_7702")
