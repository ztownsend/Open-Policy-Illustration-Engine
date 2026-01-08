"""CLI command for NDJSON batch execution."""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from opie.batch import BatchRunner


def run_batch(
    in_path: Path | None = typer.Option(None, "--in", exists=True, readable=True),
    out_path: Path | None = typer.Option(None, "--out"),
    schedule_mode: str = typer.Option("month", "--schedule-mode"),
) -> None:
    runner = BatchRunner(schedule_mode=schedule_mode)
    in_stream = in_path.open() if in_path is not None else sys.stdin
    out_stream = out_path.open("w") if out_path is not None else sys.stdout
    try:
        runner.run(in_stream, out_stream)
    finally:
        if in_path is not None:
            in_stream.close()
        if out_path is not None:
            out_stream.close()
