"""CLI entrypoint for OPIE."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import typer

from opie import run_illustration
from opie.cli.compare import compare_command
from opie.cli.conformance import app as conformance_app
from opie.cli.diff import diff_ledgers, diff_within
from opie.cli.io import read_request, write_csv, write_json
from opie.cli.pack import app as pack_app
from opie.cli.batch import run_batch
from opie.cli.bundle import app as bundle_app
from opie.core.types import IllustrationRequest, IllustrationResult

app = typer.Typer(add_completion=False)
app.add_typer(pack_app, name="pack")
app.add_typer(conformance_app, name="conformance")
app.add_typer(bundle_app, name="bundle")


@app.callback()
def main() -> None:
    """OPIE command-line interface."""


@app.command()
def illustrate(
    in_path: Path = typer.Option(..., "--in", exists=True, readable=True),
    out_path: Path = typer.Option(..., "--out"),
    format: str = typer.Option("json", "--format"),
    scenario: str = typer.Option("both", "--scenario"),
    currency: str | None = typer.Option(None, "--currency"),
    reporting_currencies: list[str] | None = typer.Option(None, "--reporting-currencies"),
    fx_rate: list[str] | None = typer.Option(None, "--fx-rate"),
    reporting_include_debug_fields: bool = typer.Option(False, "--reporting-include-debug-fields"),
) -> None:
    if format not in {"json", "csv"}:
        raise typer.BadParameter("format must be json or csv")
    if scenario not in {"current", "guaranteed", "both"}:
        raise typer.BadParameter("scenario must be current, guaranteed, or both")

    request = read_request(in_path)
    overrides: dict[str, object] = {}
    if currency is not None:
        overrides["currency_code"] = currency
    if reporting_currencies:
        if len(reporting_currencies) == 1 and "," in reporting_currencies[0]:
            reporting_currencies = [
                code.strip() for code in reporting_currencies[0].split(",") if code.strip()
            ]
        overrides["reporting_currencies"] = reporting_currencies
    if fx_rate:
        fx_rates: dict[str, Decimal] = {}
        for entry in fx_rate:
            if "=" not in entry:
                raise typer.BadParameter("fx-rate must be in CODE=RATE format")
            code, rate = entry.split("=", 1)
            code = code.strip()
            rate = rate.strip()
            if not code or not rate:
                raise typer.BadParameter("fx-rate must be in CODE=RATE format")
            fx_rates[code] = Decimal(rate)
        overrides["fx_rates"] = fx_rates
    if reporting_include_debug_fields:
        overrides["reporting_include_debug_fields"] = True
    if overrides:
        payload = request.model_dump(mode="python")
        payload.update(overrides)
        request = IllustrationRequest.model_validate(payload)
    result = run_illustration(request)

    if format == "json":
        if scenario == "both":
            payload = result
        else:
            ledgers_by_currency = None
            if result.ledgers_by_currency is not None:
                ledgers_by_currency = {
                    code: {scenario: ledgers[scenario]}
                    for code, ledgers in result.ledgers_by_currency.items()
                }
            payload = IllustrationResult(
                request_id=result.request_id,
                product_code=result.product_code,
                currency_code=result.currency_code,
                ledgers={scenario: result.ledgers[scenario]},
                ledgers_by_currency=ledgers_by_currency,
                metadata=result.metadata,
            )
        write_json(out_path, payload)
        return

    if scenario == "both":
        raise typer.BadParameter("csv format requires a single scenario")
    write_csv(out_path, result.ledgers[scenario])


@app.command()
def diff(
    a: Path = typer.Option(None, "--a", exists=True, readable=True),
    b: Path = typer.Option(None, "--b", exists=True, readable=True),
    within: Path = typer.Option(None, "--within", exists=True, readable=True),
    scenario: str | None = typer.Option(None, "--scenario"),
    scenario_a: str = typer.Option("current", "--scenario-a"),
    scenario_b: str = typer.Option("guaranteed", "--scenario-b"),
    currency: str | None = typer.Option(None, "--currency"),
) -> None:
    if within is not None:
        message = diff_within(within, scenario_a, scenario_b, currency)
    elif a is not None and b is not None:
        message = diff_ledgers(a, b, scenario)
    else:
        raise typer.BadParameter("Provide --a/--b for two-file diff or --within for single-file diff")
    typer.echo(message)


app.command("compare")(compare_command)
app.command("batch")(run_batch)


if __name__ == "__main__":
    app()
