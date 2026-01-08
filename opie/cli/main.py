"""CLI entrypoint for OPIE."""

from __future__ import annotations

from pathlib import Path

import typer

from opie import run_illustration
from opie.cli.compare import compare_command
from opie.cli.conformance import app as conformance_app
from opie.cli.diff import diff_ledgers
from opie.cli.io import read_request, write_csv, write_json
from opie.cli.pack import app as pack_app
from opie.cli.batch import run_batch
from opie.cli.bundle import app as bundle_app
from opie.core.types import IllustrationResult

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
) -> None:
    if format not in {"json", "csv"}:
        raise typer.BadParameter("format must be json or csv")
    if scenario not in {"current", "guaranteed", "both"}:
        raise typer.BadParameter("scenario must be current, guaranteed, or both")

    request = read_request(in_path)
    result = run_illustration(request)

    if format == "json":
        if scenario == "both":
            payload = result
        else:
            payload = IllustrationResult(
                request_id=result.request_id,
                product_code=result.product_code,
                ledgers={scenario: result.ledgers[scenario]},
                metadata=result.metadata,
            )
        write_json(out_path, payload)
        return

    if scenario == "both":
        raise typer.BadParameter("csv format requires a single scenario")
    write_csv(out_path, result.ledgers[scenario])


@app.command()
def diff(
    a: Path = typer.Option(..., "--a", exists=True, readable=True),
    b: Path = typer.Option(..., "--b", exists=True, readable=True),
    scenario: str | None = typer.Option(None, "--scenario"),
) -> None:
    message = diff_ledgers(a, b, scenario)
    typer.echo(message)


app.command("compare")(compare_command)
app.command("batch")(run_batch)


if __name__ == "__main__":
    app()
