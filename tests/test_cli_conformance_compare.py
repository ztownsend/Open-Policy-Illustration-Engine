import json
from pathlib import Path

from typer.testing import CliRunner

from opie.cli.main import app


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_conformance_cli_run(tmp_path: Path) -> None:
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

    runner = CliRunner()
    result = runner.invoke(app, ["conformance", "run", "--manifest", str(manifest_path)])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["passed"] is True


def test_compare_cli() -> None:
    root = _repo_root()
    runner = CliRunner()
    ok_result = runner.invoke(
        app,
        [
            "compare",
            "--a",
            str(root / "tests" / "golden" / "ul_simple_current.json"),
            "--b",
            str(root / "tests" / "golden" / "ul_simple_current.json"),
        ],
    )
    assert ok_result.exit_code == 0
    ok_payload = json.loads(ok_result.stdout)
    assert ok_payload["first_diff"] is None

    diff_result = runner.invoke(
        app,
        [
            "compare",
            "--a",
            str(root / "tests" / "golden" / "ul_simple_current.json"),
            "--b",
            str(root / "tests" / "golden" / "ul_simple_guaranteed.json"),
        ],
    )
    assert diff_result.exit_code == 1
    diff_payload = json.loads(diff_result.stdout)
    assert diff_payload["first_diff"] is not None
