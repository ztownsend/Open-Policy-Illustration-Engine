"""Regenerate golden files from example requests."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from opie import run_illustration  # noqa: E402
from opie.core.ledger import dumps_json  # noqa: E402
from opie.core.types import IllustrationRequest  # noqa: E402


def _base_name(request_path: Path) -> str:
    stem = request_path.stem
    if stem.endswith("_request"):
        return stem[: -len("_request")]
    return stem


def main() -> int:
    parser = argparse.ArgumentParser(description="Update OPIE golden files.")
    parser.add_argument("--request", action="append", required=True, help="Path to request JSON")
    parser.add_argument("--yes", action="store_true", help="Confirm overwrite")
    args = parser.parse_args()

    if not args.yes:
        raise SystemExit("Refusing to overwrite goldens without --yes")

    golden_dir = Path("tests/golden")
    golden_dir.mkdir(parents=True, exist_ok=True)

    for request_arg in args.request:
        request_path = Path(request_arg)
        payload = json.loads(request_path.read_text())
        request = IllustrationRequest.model_validate(payload)
        result = run_illustration(request)

        base_name = _base_name(request_path)
        for scenario in ("current", "guaranteed"):
            output = {
                "product_code": result.product_code,
                "scenario": scenario,
                "metadata": result.metadata,
                "ledger": result.ledgers[scenario],
            }
            output_path = golden_dir / f"{base_name}_{scenario}.json"
            output_text = dumps_json(output)
            output_path.write_text(output_text)
            print(f"Wrote {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
