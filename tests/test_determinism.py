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


def test_reporting_ledgers_are_deterministic() -> None:
    payload = json.loads(Path("examples/term_request.json").read_text())
    payload["reporting_currencies"] = ["EUR"]
    payload["fx_rates"] = {"EUR": "0.91"}
    request = IllustrationRequest.model_validate(payload)
    first = dumps_json(run_illustration(request))
    second = dumps_json(run_illustration(request))
    assert first == second
