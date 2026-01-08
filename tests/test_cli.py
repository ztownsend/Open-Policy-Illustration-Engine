import json
from pathlib import Path

from typer.testing import CliRunner

from opie.cli.main import app


def test_cli_json_output(tmp_path: Path) -> None:
    output_path = tmp_path / "out.json"
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "illustrate",
            "--in",
            "examples/term_request.json",
            "--out",
            str(output_path),
            "--format",
            "json",
            "--scenario",
            "current",
        ],
    )
    assert result.exit_code == 0
    payload = json.loads(output_path.read_text())
    assert payload["product_code"] == "level_term"
    assert "ledgers" in payload


def test_cli_csv_output(tmp_path: Path) -> None:
    output_path = tmp_path / "out.csv"
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "illustrate",
            "--in",
            "examples/term_request.json",
            "--out",
            str(output_path),
            "--format",
            "csv",
            "--scenario",
            "current",
        ],
    )
    assert result.exit_code == 0
    header = output_path.read_text().splitlines()[0]
    assert header.startswith("t,policy_year,attained_age")
