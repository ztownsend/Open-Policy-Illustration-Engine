"""CLI I/O helpers for JSON and CSV."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from opie.core.ledger import dumps_json, normalize_for_json
from opie.core.types import IllustrationRequest, Ledger, LedgerRow


def read_request(path: Path) -> IllustrationRequest:
    payload = json.loads(path.read_text())
    return IllustrationRequest.model_validate(payload)


def write_json(path: Path, payload) -> None:
    path.write_text(dumps_json(payload))


def write_csv(path: Path, ledger: Ledger) -> None:
    fieldnames = list(LedgerRow.model_fields.keys())
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in ledger.rows:
            data = row.model_dump(mode="python")
            normalized = normalize_for_json(data)
            writer.writerow(normalized)
