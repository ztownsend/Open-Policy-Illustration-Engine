"""Simple benchmark for OPIE runs."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from opie import run_illustration  # noqa: E402
from opie.core.types import IllustrationRequest  # noqa: E402


def main(iterations: int = 200) -> None:
    payload = json.loads(Path("examples/ul_simple_request.json").read_text())
    request = IllustrationRequest.model_validate(payload)

    start = time.perf_counter()
    for _ in range(iterations):
        run_illustration(request)
    elapsed = time.perf_counter() - start
    per = elapsed / iterations
    print(f"Iterations: {iterations}")
    print(f"Total seconds: {elapsed:.4f}")
    print(f"Seconds per run: {per:.6f}")


if __name__ == "__main__":
    main()
