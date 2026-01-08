import json
from pathlib import Path

from opie.conformance.runner import run_conformance


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_conformance_runner_passes(tmp_path: Path) -> None:
    root = _repo_root()
    manifest = {
        "cases": [
            {
                "name": "term",
                "request": str(root / "examples" / "term_request.json"),
                "expected_current": str(root / "tests" / "golden" / "term_current.json"),
                "expected_guaranteed": str(root / "tests" / "golden" / "term_guaranteed.json"),
            }
        ]
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, sort_keys=True))

    report = run_conformance(manifest_path)
    assert report.passed is True
    assert report.total_cases == 1
    assert report.failed_cases == 0


def test_conformance_runner_fails(tmp_path: Path) -> None:
    root = _repo_root()
    bad_expected = {"ledger": {"rows": []}}
    bad_path = tmp_path / "bad_expected.json"
    bad_path.write_text(json.dumps(bad_expected, sort_keys=True))

    manifest = {
        "cases": [
            {
                "name": "term",
                "request": str(root / "examples" / "term_request.json"),
                "expected_current": str(bad_path),
                "expected_guaranteed": str(root / "tests" / "golden" / "term_guaranteed.json"),
            }
        ]
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, sort_keys=True))

    report = run_conformance(manifest_path)
    assert report.passed is False
    assert report.failed_cases == 1
    case = report.cases[0]
    assert case.scenarios["current"].passed is False
