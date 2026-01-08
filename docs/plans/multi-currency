# Multi-Currency Spec (USD, EUR, BTC)
Status: draft
Owner: TBD

## 1) Summary
Add first-class currency support so OPIE can run illustrations in a declared base currency (USD, EUR, or BTC) with deterministic, currency-specific rounding. Optional reporting-currency conversion is a post-processing step that does not alter engine ordering or math.

## 2) Goals
- Support a per-request base currency (USD, EUR, BTC).
- Apply currency-specific quantization at the same rounding points as today.
- Preserve determinism (Decimal-only, stable JSON, no external FX).
- Keep engine purity: no I/O, no network, no hidden state.

## 3) Non-goals
- Real-time FX rates or live market integration.
- Mixing multiple base currencies inside a single request (all amounts are in one base currency).
- Reworking product math, ordering, or lapse semantics.
- Crypto wallet/chain semantics (BTC is just another currency code).

## 4) Definitions
- Base currency: the currency for all monetary inputs and outputs for a request.
- Reporting currency: an optional additional currency for converted ledgers.
- Currency quantum: smallest unit used for quantization.
- FX rate: Decimal rate defined as "1 base unit = rate target units".

## 5) Currency policy (authoritative)
Currency codes are explicit and closed at MVP:
- USD: quantum 0.01 (2 decimals)
- EUR: quantum 0.01 (2 decimals)
- BTC: quantum 0.00000001 (8 decimals)

Rounding mode is unchanged (ROUND_HALF_UP). Currency quantization is the only new variable.

## 6) Schema changes (phase 1: base currency)
### 6.1 Request
Add to `IllustrationRequest`:
- `currency_code: Literal["USD", "EUR", "BTC"] = "USD"`

Rules:
- All monetary inputs (face amount, premiums, fees, schedules, withdrawals, loan amounts, etc.) are in `currency_code`.
- All assumption schedules that express money are in `currency_code`.

### 6.2 Result + metadata
Add to `IllustrationResult` (top-level):
- `currency_code: str`

Add to `IllustrationMetadata`:
- `currency_code: str`

Notes:
- This is an external schema change; bump `SCHEMA_VERSION`.
- Defaulting to USD preserves existing request files.

## 7) Rounding + normalization rules
### 7.1 Quantization helper
Replace `quantize_money(value)` with `quantize_money(value, currency_code)` using the currency quantum table.

### 7.2 Monetary field list (must be quantized)
Any field representing money is quantized using the base currency quantum at the same rounding points as today, including:
- Inputs: face_amount, premium_schedule.amount, fees/loads, surrender schedules, loan/withdrawal schedules
- Ledger: premium, cumulative_premium, death_benefit, account_value_bop, premium_load, net_premium_to_av, policy_fee,
  coi_charge, admin_fee, charges_total, charges_assessed, charges_paid, charge_shortfall, rider_charges, net_amount_at_risk,
  account_value_mid_raw, interest_credited, account_value_eop, surrender_charge, cash_surrender_value, corridor_uplift,
  withdrawal, loan_draw, loan_repayment, loan_interest, loan_balance, and debug monetary fields

### 7.3 Rate precision
Rate handling remains unchanged (`quantize_rate` / high precision). Rates are currency-neutral.

### 7.4 Normalization timing
Monetary inputs are normalized to the base currency quantum at validation/load time (request and assumptions). Engine math uses normalized values only.

### 7.5 BTC precision rule
BTC inputs must be at most 8 decimal places. If more precision is provided, validation fails (do not round).

## 8) FX conversions (phase 2: reporting currencies)
Include converting ledgers to additional currencies without altering base calculations.

### 8.1 Request additions
- `reporting_currencies: list[Literal["USD", "EUR", "BTC"]] | None`
- `fx_rates: dict[str, DecimalInput] | None`
- `reporting_include_debug_fields: bool = False`

Rules:
- `fx_rates` is keyed by target currency code.
- Each entry is a Decimal rate defined as: `1 base_currency = fx_rates[target]`.
- `fx_rates` must contain every currency in `reporting_currencies`.
- `reporting_include_debug_fields` controls whether debug fields are included and converted in `ledgers_by_currency`.

### 8.2 Output addition
Add optional field to `IllustrationResult`:
- `ledgers_by_currency: dict[str, dict[str, Ledger]] | None`

Rules:
- `ledgers` remains the base currency output.
- `ledgers_by_currency[code][scenario]` mirrors the base ledger structure.
- Conversion happens after the base ledger is finalized, preserving engine ordering.
- All monetary fields are converted with `amount * fx_rate` then quantized to the target currency quantum.
- Rates and non-monetary fields are copied unchanged.
- If `reporting_include_debug_fields` is false, debug fields are omitted from `ledgers_by_currency` rows.
- If true, debug monetary fields are converted and included.

### 8.3 Determinism
FX conversion uses Decimal only. No external fetches; rates are request inputs and are included in metadata for traceability.

## 9) Versioning and compatibility
- `SCHEMA_VERSION` bump for new request/metadata fields.
- `ROUNDING_POLICY_ID` bump if the quantization logic changes (e.g., currency table introduction).
- `CALC_VERSION` bump only if ordering or rounding points change.
- Existing USD requests should produce identical ledgers when `currency_code` defaults to USD.

## 10) Acceptance criteria
- Requests that omit `currency_code` default to USD, and produce byte-identical output to current goldens.
- Requests with `currency_code` set to USD/EUR/BTC validate and run end-to-end.
- `IllustrationResult.currency_code` and `IllustrationMetadata.currency_code` match the request base currency.
- All monetary fields are quantized to the base currency quantum at existing rounding points.
- BTC inputs with >8 decimal places are rejected with a clear validation error.
- Reporting-currency outputs require complete `fx_rates`; missing rates are validation errors.
- `ledgers_by_currency` (when requested) is derived post-calculation and does not affect base `ledgers`.
- `reporting_include_debug_fields` controls debug field inclusion in converted ledgers.
- Determinism: same input yields byte-identical output across runs and platforms.

## 11) Tests + goldens
- Unit tests for currency quantization (USD/EUR 2 decimals, BTC 8 decimals).
- Invariant: all monetary ledger fields are quantized to the base currency quantum.
- Golden files for at least one product in each currency (USD/EUR/BTC).
- Determinism test: same input, same output bytes across runs for each currency.

### 11.1 Test cases (explicit)
- USD default: omit `currency_code`, expect `currency_code=USD` in result + metadata and byte-identical output to existing USD goldens.
- EUR rounding: input premium `1.005` should quantize to `1.01`; `1.004` should quantize to `1.00` (ROUND_HALF_UP, 2 decimals).
- BTC precision accept: `0.00000001` accepted; BTC precision reject: `0.000000001` rejected at validation.
- BTC rounding: `0.000000005` quantizes to `0.00000001` (ROUND_HALF_UP, 8 decimals).
- FX conversion: base USD with `reporting_currencies=["EUR"]` and `fx_rates={"EUR": 0.91}` produces `ledgers_by_currency["EUR"]` with monetary fields converted and quantized; non-monetary fields unchanged.
- FX debug flag off: debug fields are absent in `ledgers_by_currency` rows.
- FX debug flag on: debug monetary fields are converted and present.
- FX missing rate: `reporting_currencies=["EUR"]` with no `fx_rates["EUR"]` is a validation error.
- Determinism: repeated runs of the same input are byte-identical in base and reporting ledgers.

## 12) CLI/API impacts
- CLI: add `--currency` (default USD); optional `--reporting-currencies` and `--fx-rate` for phase 2.
- API: accept and validate `currency_code`, return it in metadata.
- No logging of full request bodies (unchanged rule).

## 13) Work items (small diffs)
1) Add currency enums + currency quantum table; update `quantize_money` signature; add unit tests.
2) Add `currency_code` to request + metadata; default to USD; update schema tests; bump `SCHEMA_VERSION` and `ROUNDING_POLICY_ID`.
3) Update normalization to quantize monetary inputs using currency quantum; add invariant for quantized money.
4) Add currency-specific goldens (USD/EUR/BTC) for one UL and one Term example.
5) Add reporting currencies + FX conversion post-processor + tests + goldens.

## 14) Decisions
- FX rates are request-level (not scenario-specific).
- Debug field conversion for reporting currencies is controlled by `reporting_include_debug_fields`.
