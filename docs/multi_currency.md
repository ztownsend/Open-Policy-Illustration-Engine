# Multi-Currency

OPIE supports a single **base currency** per illustration request and optional
**reporting-currency** ledgers derived after the base ledgers are finalized.
Reporting conversion is post-processing only and does not affect engine math,
ordering, or rounding points.

## Supported Currencies
Base and reporting currencies are limited to the MVP set:

| Currency | Quantum |
| --- | --- |
| USD | 0.01 |
| EUR | 0.01 |
| BTC | 0.00000001 |

## Request Fields
Multi-currency behavior is controlled by these request fields:

- `currency_code`: Base currency for all monetary inputs/outputs. Defaults to `USD`.
- `reporting_currencies`: Optional list of currency codes to emit converted ledgers.
- `fx_rates`: Optional mapping of currency code to Decimal where
  `1 base_currency = fx_rates[target]`.
  When `reporting_currencies` is provided, `fx_rates` must include every target currency.
- `reporting_include_debug_fields`: When `true`, debug monetary fields are converted
  and included in `ledgers_by_currency`. When `false`, debug fields are omitted.

Example:
```json
{
  "currency_code": "EUR",
  "reporting_currencies": ["USD", "BTC"],
  "fx_rates": {"USD": "1.08", "BTC": "0.000021"}
}
```

## Output Shape
- `ledgers` are always in the base currency.
- `ledgers_by_currency` is present only when `reporting_currencies` is provided.
  It mirrors the base ledger structure per scenario.
- `metadata.currency_code` echoes the base currency, and metadata includes
  `reporting_currencies`, `fx_rates`, and `reporting_include_debug_fields`
  when reporting is requested.

## Conversion Rules
- Monetary inputs are normalized to the base currency quantum at validation time.
- BTC inputs must have at most 8 decimal places; higher precision is invalid.
- Reporting conversion uses: `amount * fx_rate` then quantizes to the target currency quantum.
- Non-monetary fields are copied as-is into reporting ledgers.

## CLI Examples
Run a base-currency illustration:
```
uv run opie illustrate --in examples/term_request.json --out /tmp/out.json --currency EUR
```

Add a reporting currency:
```
uv run opie illustrate --in examples/term_request.json --out /tmp/out.json \
  --reporting-currencies USD --fx-rate USD=1.08
```

## Notes
- One base currency per request; mixed-base inputs are not supported.
- Reporting ledgers are derived after the base ledger is finalized and do not
  affect determinism of the base output.
- Currency behavior is fully specified in `docs/opie_mvp_spec.md`.
