"""CLI commands for conformance runs."""

from __future__ import annotations

from pathlib import Path

import typer

from opie.conformance.runner import run_conformance
from opie.core.ledger import dumps_json

app = typer.Typer(add_completion=False)


@app.command("run")
def run(
    manifest: Path = typer.Option(..., "--manifest", exists=True, readable=True),
    out: Path | None = typer.Option(None, "--out"),
) -> None:
    report = run_conformance(manifest)
    output = dumps_json(report)
    if out is not None:
        out.write_text(output)
    else:
        typer.echo(output)
    if not report.passed:
        raise typer.Exit(code=1)
