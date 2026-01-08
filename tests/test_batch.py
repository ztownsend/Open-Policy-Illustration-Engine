import io
import json
from pathlib import Path

from opie.batch import BatchRunner


def test_batch_runner_ndjson() -> None:
    payload = json.loads(Path("examples/term_request.json").read_text())
    payload2 = dict(payload)
    payload2["issue_age"] = payload["issue_age"] + 1

    ndjson = "\n".join([json.dumps(payload), json.dumps(payload2), ""])
    runner = BatchRunner()
    output = io.StringIO()
    stats = runner.run(io.StringIO(ndjson), output)

    lines = [line for line in output.getvalue().splitlines() if line.strip()]
    assert len(lines) == 2
    first = json.loads(lines[0])
    assert first["product_code"] == "level_term"
    assert stats.processed == 2
    assert stats.cache_misses == 1
    assert stats.cache_hits == 1
