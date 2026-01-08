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


def test_cli_reporting_currency_output(tmp_path: Path) -> None:
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
            "--reporting-currencies",
            "EUR",
            "--fx-rate",
            "EUR=0.5",
        ],
    )
    assert result.exit_code == 0
    payload = json.loads(output_path.read_text())
    assert "ledgers_by_currency" in payload
    assert "EUR" in payload["ledgers_by_currency"]
    assert "current" in payload["ledgers_by_currency"]["EUR"]


def test_cli_reporting_currencies_comma_split(tmp_path: Path) -> None:
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
            "--reporting-currencies",
            "EUR,BTC",
            "--fx-rate",
            "EUR=0.5",
            "--fx-rate",
            "BTC=0.0001",
        ],
    )
    assert result.exit_code == 0
    payload = json.loads(output_path.read_text())
    assert "EUR" in payload["ledgers_by_currency"]
    assert "BTC" in payload["ledgers_by_currency"]


def test_cli_currency_override(tmp_path: Path) -> None:
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
            "--currency",
            "BTC",
        ],
    )
    assert result.exit_code == 0
    payload = json.loads(output_path.read_text())
    assert payload["currency_code"] == "BTC"


def test_cli_fx_rate_requires_code_rate_format(tmp_path: Path) -> None:
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
            "--reporting-currencies",
            "EUR",
            "--fx-rate",
            "EUR",
        ],
    )
    assert result.exit_code != 0
    assert "CODE=RATE" in result.output
