"""FastAPI app for OPIE."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import Response

from opie import run_illustration
from opie.core.ledger import dumps_json
from opie.core.types import IllustrationRequest, IllustrationResult

app = FastAPI(title="OPIE", version="0.1.0")


@app.post("/v1/illustrations", response_model=IllustrationResult)
def create_illustration(request: IllustrationRequest):
    result = run_illustration(request)
    return Response(content=dumps_json(result), media_type="application/json")
