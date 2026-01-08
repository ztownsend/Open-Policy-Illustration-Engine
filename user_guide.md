# OPIE System User Guide

OPIE (Open Policy Illustration Engine) is a deterministic, math-first policy illustration engine.
It produces stable monthly ledgers for multiple scenarios using Decimal-only math and locked
calculation ordering.

## Quick start
Run an example illustration from the CLI:

```bash
uv run opie illustrate --in examples/ul_simple_request.json --out /tmp/out.json
```

Run a single scenario and emit CSV:

```bash
uv run opie illustrate --in examples/term_request.json --out /tmp/out.csv --format csv --scenario current
```

## Core concepts
- Determinism: same request => byte-identical output across runs.
- Decimal-only math: do not use floats in requests.
- Normative ordering: calculation order is fixed by spec; do not reorder steps.
- Goldens: output contracts live in `tests/golden/`.

## Supported products
- `simple_ul`
- `level_term`
- `wl_nonpar`
- `annuity_deferred`
- `annuity_spia`

## Request basics
Requests are JSON. Monetary values should be strings to preserve Decimal precision.

Minimal shape:

```json
{
  "product_code": "simple_ul",
  "issue_age": 35,
  "issue_gender": "M",
  "risk_class": "NT",
  "face_amount": "100000",
  "issue_date": "2025-01-01",
  "duration_months": 24,
  "premium_schedule": [{"start_month": 1, "end_month": 24, "amount": "200"}],
  "scenarios": {
    "current": { ... },
    "guaranteed": { ... }
  }
}
```

Example requests live in `examples/`.

## Currency and reporting
- Base currency is per-request: `currency_code` = `USD` | `EUR` | `BTC`.
- Monetary inputs are normalized at validation time to the currency quantum.
- BTC precision is capped at 8 decimals (validation error if higher).
- Optional reporting currencies:
  - `reporting_currencies`: list of target currency codes
  - `fx_rates`: mapping `{currency_code: Decimal}` where `1 base = fx_rates[target]`
  - `reporting_include_debug_fields`: include debug fields in converted ledgers

Converted ledgers appear in `ledgers_by_currency` and do not change base ledger math.

## Output overview
Each result contains:
- `request_id`
- `product_code`
- `currency_code`
- `ledgers`: `{current, guaranteed}`
- optional `ledgers_by_currency`
- `metadata`

Metadata includes:
- `calc_version`, `schema_version`, `rounding_policy_id`
- `currency_code`
- optional `reporting_currencies`, `fx_rates`, `reporting_include_debug_fields`
- optional `tax_7702` (report-only 7702 checks)
- optional `solve`

## Debug output
- Set `request.debug=true` to include debug fields in ledger rows.
- Debug fields are quantized to the base currency and are deterministic.

## Premium solve (UL only)
Use `solve` to find a level premium that keeps the policy in force or targets AV:
- `mode`: `keep_in_force` | `target_av`
- `target_month`, optional `target_av`
- `min_premium`, `max_premium`, `tolerance`, `iterations`
- `strategy`: `current_only` or `per_scenario`

## IRC 7702 checker (report-only)
Optional per-scenario `tax_7702` inputs run GPT/CVAT checks after ledgers are built.
Results appear in `metadata.tax_7702`. This does not change ledger math.
Example request: `examples/ul_simple_7702_request.json`.

## CLI commands (common)
- `illustrate`:
  - `--in`, `--out`
  - `--format json|csv`
  - `--scenario current|guaranteed|both`
  - `--currency`
  - `--reporting-currencies`
  - `--fx-rate CODE=RATE`
  - `--reporting-include-debug-fields`
- `diff`: first-diff between two outputs
- `compare`: diff + max-diff stats
- `batch`: NDJSON batch runner
- `pack`: assumption pack tooling
- `bundle`: artifact bundles
- `conformance run`: canonical case runner

## API (FastAPI)
`POST /v1/illustrations` accepts the same JSON payload as the CLI and returns an
`IllustrationResult` payload.

## Assumptions and packs
Assumptions live under `opie/assumptions/`. Packs are validated and referenced in
conformance tooling and pack utilities.

## Golden files and tests
Goldens are the output contract. Update only via:

```bash
uv run python scripts/update_golden.py --request examples/<file>.json --yes
```

Tests:
- `uv run pytest`
- `uv run ruff check .`

## Troubleshooting
- Validation errors: check monetary fields are strings and match currency precision.
- Golden failures: do not hand-edit goldens; fix code or regenerate intentionally.
- Unsupported product for optional features (e.g., 7702): raises `AssumptionError` with context.
