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


def test_annuity_deferred_golden() -> None:
    _assert_golden(Path("examples/annuity_deferred_request.json"), "annuity_deferred")


def test_annuity_deferred_long_golden() -> None:
    _assert_golden(Path("examples/annuity_deferred_long_request.json"), "annuity_deferred_long")


def test_annuity_spia_golden() -> None:
    _assert_golden(Path("examples/annuity_spia_request.json"), "annuity_spia")


def test_annuity_spia_long_golden() -> None:
    _assert_golden(Path("examples/annuity_spia_long_request.json"), "annuity_spia_long")
