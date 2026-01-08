"""Batch NDJSON runner with assumption caching."""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import IO, Any

from opie import run_illustration
from opie.assumptions.loaders import load_scenario_set
from opie.core.ledger import dumps_json
from opie.core.types import IllustrationRequest


@dataclass
class BatchStats:
    processed: int = 0
    cache_hits: int = 0
    cache_misses: int = 0


class BatchRunner:
    def __init__(self, *, schedule_mode: str = "month") -> None:
        self.schedule_mode = schedule_mode
        self._scenario_cache: dict[tuple[str, str], Any] = {}
        self.stats = BatchStats()

    def _cache_key(self, product_code: str, scenarios: dict[str, Any]) -> tuple[str, str]:
        scenarios_key = json.dumps(
            scenarios,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
        return product_code, scenarios_key

    def _build_request(self, payload: dict[str, Any]) -> IllustrationRequest:
        product_code = payload.get("product_code")
        if not isinstance(product_code, str):
            raise ValueError("product_code must be provided")
        scenarios_payload = payload.get("scenarios", {})
        cache_key = self._cache_key(product_code, scenarios_payload)
        scenario_set = self._scenario_cache.get(cache_key)
        if scenario_set is None:
            scenario_set = load_scenario_set(
                product_code,
                scenarios_payload,
                schedule_mode=self.schedule_mode,
                duration_months=payload.get("duration_months"),
            )
            self._scenario_cache[cache_key] = scenario_set
            self.stats.cache_misses += 1
        else:
            self.stats.cache_hits += 1
        request_payload = dict(payload)
        request_payload["scenarios"] = scenario_set
        return IllustrationRequest.model_validate(request_payload)

    def run(self, in_stream: IO[str], out_stream: IO[str]) -> BatchStats:
        for line in in_stream:
            stripped = line.strip()
            if not stripped:
                continue
            payload = json.loads(stripped)
            request = self._build_request(payload)
            result = run_illustration(request)
            out_stream.write(dumps_json(result))
            out_stream.write("\n")
            self.stats.processed += 1
        return self.stats
