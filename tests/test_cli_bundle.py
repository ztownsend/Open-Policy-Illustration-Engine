import json
from pathlib import Path

from typer.testing import CliRunner

from opie.cli.main import app


def test_cli_bundle_create_and_verify(tmp_path: Path) -> None:
    bundle_path = tmp_path / "bundle.zip"
    runner = CliRunner()
    create_result = runner.invoke(
        app,
        [
            "bundle",
            "create",
            "--request",
            "examples/term_request.json",
            "--out",
            str(bundle_path),
        ],
    )
    assert create_result.exit_code == 0

    verify_result = runner.invoke(
        app,
        [
            "bundle",
            "verify",
            "--bundle",
            str(bundle_path),
        ],
    )
    assert verify_result.exit_code == 0
    payload = json.loads(verify_result.stdout)
    assert payload["valid"] is True
