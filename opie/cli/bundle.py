"""CLI commands for artifact bundles."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from opie import run_illustration
from opie.bundle import create_bundle, verify_bundle
from opie.core.ledger import dumps_json
from opie.core.types import IllustrationRequest

app = typer.Typer(add_completion=False)


@app.command("create")
def create(
    request_path: Path = typer.Option(..., "--request", exists=True, readable=True),
    out_path: Path = typer.Option(..., "--out"),
) -> None:
    payload = json.loads(request_path.read_text())
    request = IllustrationRequest.model_validate(payload)
    result = run_illustration(request)
    create_bundle(request, result, out_path)


@app.command("verify")
def verify(
    bundle_path: Path = typer.Option(..., "--bundle", exists=True, readable=True),
) -> None:
    result = verify_bundle(bundle_path)
    typer.echo(dumps_json(result))
    if not result.valid:
        raise typer.Exit(code=1)
