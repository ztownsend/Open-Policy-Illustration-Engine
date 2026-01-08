"""CLI command for comparing ledger outputs."""

from __future__ import annotations

from pathlib import Path

import typer

from opie.conformance.compare import compare_files
from opie.core.ledger import dumps_json


def compare_command(
    a: Path = typer.Option(..., "--a", exists=True, readable=True),
    b: Path = typer.Option(..., "--b", exists=True, readable=True),
    scenario: str | None = typer.Option(None, "--scenario"),
) -> None:
    result = compare_files(a, b, scenario=scenario)
    typer.echo(dumps_json(result))
    if result.first_diff is not None:
        raise typer.Exit(code=1)
