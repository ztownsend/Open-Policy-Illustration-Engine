import json
from pathlib import Path

from opie import run_illustration
from opie.core.ledger import dumps_json
from opie.core.types import IllustrationRequest


def test_run_illustration_is_deterministic() -> None:
    payload = json.loads(Path("examples/ul_simple_request.json").read_text())
    request = IllustrationRequest.model_validate(payload)
    first = dumps_json(run_illustration(request))
    second = dumps_json(run_illustration(request))
    assert first == second
