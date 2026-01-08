# OPIE

Open Policy Illustration Engine (OPIE) is a deterministic, versioned life-insurance illustration engine that produces stable monthly ledgers across scenarios. The output contract is locked by golden files + invariants.

## Highlights
- Deterministic math with `Decimal` only (no floats)
- Products: `simple_ul`, `level_term`, `wl_nonpar`, `annuity_deferred`, `annuity_spia`
- Scenarios: `current` and `guaranteed`
- Premium solve (keep-in-force or target AV)
- Death benefit Option 2 + corridor uplift (UL)
- Loans, withdrawals, grace period, rider framework
- CLI, FastAPI API, UI Explorer, PDF renderer
- Conformance runner + compare tooling
- Assumption packs, batch NDJSON, artifact bundles

## Quick Start (uv)
1) Install Python (optional; uv can install as needed)
   - `uv python install 3.14`
2) Sync dependencies (non-editable so CLI entrypoint works under Python 3.14)
   - `uv sync --no-editable`
3) Run tests
   - `uv run pytest`
4) Try the CLI
   - `uv run opie --help`
   - `uv run opie illustrate --in examples/ul_simple_request.json --out /tmp/out.json`

## CLI
- Illustrate:
  - `uv run opie illustrate --in examples/ul_simple_request.json --out /tmp/out.json`
- Diff two ledgers:
  - `uv run opie diff --a tests/golden/ul_simple_current.json --b tests/golden/ul_simple_guaranteed.json`
- Compare with max-diff stats:
  - `uv run opie compare --a tests/golden/ul_simple_current.json --b tests/golden/ul_simple_current.json`
- Conformance run:
  - `uv run opie conformance run --manifest conformance/cases.json`
- Batch NDJSON:
  - `uv run opie batch --in /tmp/in.ndjson --out /tmp/out.ndjson`
- Assumption packs:
  - `uv run opie pack list --path /path/to/pack`
  - `uv run opie pack validate --path /path/to/pack`
- Artifact bundles:
  - `uv run opie bundle create --request examples/term_request.json --out /tmp/opie_bundle.zip`
  - `uv run opie bundle verify --bundle /tmp/opie_bundle.zip`

## API
- Run FastAPI:
  - `uv run uvicorn opie.api.app:app --reload`
- Endpoint:
  - `POST /v1/illustrations`

## UI Explorer
- `uv run uvicorn opie_ui.app:app --reload`
- Visit `http://localhost:8000/` (API mounted at `/api`)

## PDF Renderer
- Programmatic use:

```python
from pathlib import Path
import json

from opie import run_illustration
from opie.core.types import IllustrationRequest
from opie_pdf.render import render_pdf

payload = json.loads(Path("examples/term_request.json").read_text())
request = IllustrationRequest.model_validate(payload)
result = run_illustration(request)
render_pdf(result, Path("/tmp/out.pdf"))
```

## Golden Files
Goldens are the output contract.
- Do not hand-edit.
- Update only via:
  - `uv run python scripts/update_golden.py --request examples/ul_simple_request.json --yes`

## Development Commands (Makefile)
- `make sync` -> `uv sync --no-editable`
- `make test` -> `uv run pytest`
- `make lint` -> `uv run ruff check .`
- `make format` / `make format-check`
- `make conformance`
- `make batch`
- `make benchmark`

## Determinism & Versioning
- Outputs include `calc_version`, `schema_version`, and `rounding_policy_id`.
- JSON serialization is stable (sorted keys, Decimal string encoding).

## Docs
- MVP spec: `docs/opie_mvp_spec.md`
- Technical architecture: `docs/opie_technical_architecture.md`
- Roadmaps: `docs/opie_roadmap.md`, `docs/opie-strategic-roadmap.md`
- Code map: `docs/codemap.md`
