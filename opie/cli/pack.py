"""CLI commands for assumption packs."""

from __future__ import annotations

from pathlib import Path

import typer

from opie.assumptions.packs import load_manifest, resolve_pack_root, validate_pack
from opie.core.errors import AssumptionError
from opie.core.ledger import dumps_json

app = typer.Typer(add_completion=False)


def _resolve_root(path: Path) -> Path:
    try:
        return resolve_pack_root(path)
    except AssumptionError as exc:
        raise typer.BadParameter(str(exc)) from exc


@app.command("list")
def list_pack(
    path: Path = typer.Option(..., "--path", exists=True, readable=True),
) -> None:
    root = _resolve_root(path)
    manifest = load_manifest(root)
    payload = {"manifest": manifest, "files": validate_pack(root).files}
    typer.echo(dumps_json(payload))


@app.command("validate")
def validate(
    path: Path = typer.Option(..., "--path", exists=True, readable=True),
) -> None:
    root = _resolve_root(path)
    result = validate_pack(root)
    payload = {
        "valid": result.valid,
        "expected_checksum": result.manifest.checksum,
        "computed_checksum": result.computed_checksum,
        "files": result.files,
    }
    typer.echo(dumps_json(payload))
    if not result.valid:
        raise typer.Exit(code=1)
