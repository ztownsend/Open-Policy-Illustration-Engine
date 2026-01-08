# Plan: IRC 7702 (GPT + CVAT) Checker

Status: implemented (2026-01-08)
Created: 2026-01-08
Owner: OPIE

## 1) Applicability & test election
- Applies to cash-value life products (simple_ul, wl_nonpar if applicable).
- If enabled for an unsupported product_code, raise AssumptionError with product_code and scenario.
- `test_type` is an election at issue; it must be stable for the projection.
- If `test_type = "both"`, run both checks and set overall status to `fail` if either test fails (pass only if both pass).

## 2) Purpose
Add a deterministic, report-only IRC 7702 qualification checker that can evaluate both:
- GPT: Guideline Premium Test
- CVAT: Cash Value Accumulation Test

The checker must not change the ledger math or ordering. It only reads a completed ledger and produces a pass/fail report with first-failure context.

## 3) Scope
In scope (MVP for checker):
- UL-style products with cash values (simple_ul, wl_nonpar if applicable)
- Monthly evaluation using existing ledger fields
- GPT and CVAT checks, each selectable or both
- Deterministic outputs suitable for goldens and invariants

Out of scope (explicitly deferred):
- Full actuarial calculation of guideline premiums or NSP (inputs are provided)
- MEC 7-pay test
- Material change handling (face/premium changes, benefit changes)
- Complex rider integrations or underwriting changes
- Regulatory/legal compliance guarantees

## 4) Design principles
- Deterministic, Decimal-only math
- No changes to engine ordering
- All logic lives outside core engine (post-process on ledger)
- Report-only: do not auto-adjust premiums or death benefits

## 5) Inputs (proposed schema additions)
Add a 7702 block to scenario assumptions (per scenario so it is fully explicit and deterministic):

```
Tax7702Assumptions:
  enabled: bool
  test_type: "gpt" | "cvat" | "both"
  gpt_guideline_single_premium: Decimal | null
  gpt_guideline_level_premium_annual: Decimal | null
  gpt_premium_timing: "bop" | "eop"  # when premiums are counted in the test
  cvat_net_single_premium: Decimal | null
  cvat_cash_value_basis: "csv" | "av_eop" | "custom"
  cvat_cash_value_adjustment: Decimal | null  # optional additive adjustment
  corridor_factors: dict[int, Decimal] | null  # may reuse existing corridor_factors
  tolerance: Decimal  # comparison tolerance, default 0.00
```

Notes:
- Guideline premium amounts (GSP, GLP) and CVAT NSP are provided by inputs and treated as authoritative.
- The checker does not compute GSP, GLP, or NSP. That is actuarial pre-work.
- If `enabled=false`, the checker is a no-op.

## 6) Outputs (report-only)
Add a per-scenario report in result metadata (not per-row unless debug is requested):

```
Tax7702Report:
  test_type: "gpt" | "cvat" | "both"
  status: "pass" | "fail"
  first_failure_t: int | null
  failures: list[Tax7702Failure]

Tax7702Failure:
  t: int
  test: "gpt" | "cvat"
  value: Decimal
  limit: Decimal
  reason: str
```

Optional debug (only when request.debug == true):
- Include a `tax_7702_debug` list with per-month values and limits.

This adds schema surface area and must bump `SCHEMA_VERSION` when implemented.

## 7) Calculation rules (deterministic)
Common rules:
- Use `Decimal` only.
- Comparison is `value > limit + tolerance`.
- Use `quantize_money()` for values and limits stored in the report.
- Never mutate ledger values.

### 7.1 GPT (Guideline Premium Test)
Inputs:
- `gpt_guideline_single_premium` (GSP)
- `gpt_guideline_level_premium_annual` (GLP)
- `gpt_premium_timing`

Definitions:
- `cumulative_premium_t`: use ledger `cumulative_premium` at month t.
- `years_elapsed`: `(t - 1) / 12` if premiums are counted at BOP, else `t / 12` for EOP.
- `glp_limit_t`: `GLP * years_elapsed`
- `gpt_limit_t`: `max(GSP, glp_limit_t)`

Check:
- If `cumulative_premium_t > gpt_limit_t + tolerance`, mark GPT failure.
- Record the first month that fails.

Notes:
- This is a deterministic monthly approximation. The exact statutory timing (anniversary vs. pro-rata) is an open question; see section 11.

### 7.2 CVAT (Cash Value Accumulation Test)
Inputs:
- `cvat_net_single_premium` (NSP)
- `cvat_cash_value_basis`
- `cvat_cash_value_adjustment`

Definitions:
- `cash_value_t`:
  - `csv`: use ledger `cash_surrender_value`
  - `av_eop`: use ledger `account_value_eop`
  - `custom`: use `account_value_eop + cvat_cash_value_adjustment`
- `cvat_limit_t`: `NSP` (static in MVP)

Check:
- If `cash_value_t > cvat_limit_t + tolerance`, mark CVAT failure.

Notes:
- A static NSP is a simplification. If NSP varies by duration or face changes, provide a schedule input (deferred).

### 7.3 Corridor alignment (optional check)
If `corridor_factors` is present:
- `corridor_min_db_t = cash_value_t * corridor_factor(attained_age)`
- If `death_benefit < corridor_min_db_t`, add a failure with reason `corridor`.

This does not modify the death benefit. It only reports.

## 8) Integration points
Proposed new module:
- `opie/tax/irc_7702.py`
  - `run_7702_checks(ledger, assumptions, request) -> Tax7702Report`

Call site:
- Post-process in `run_illustration()` or the reporting post-processor (`opie/core/reporting.py`) after the ledger is built.

No changes to `opie/core/engine.py` ordering.

## 9) Testing plan
Unit tests:
- GPT limit selection (GSP vs. GLP) with BOP vs. EOP timing.
- GPT tolerance handling (value == limit + tolerance is pass).
- CVAT basis selection (csv, av_eop, custom) with adjustment.
- CVAT tolerance handling and corridor failure behavior.

Integration tests:
- `run_illustration()` returns per-scenario report when enabled.
- Unsupported product with enabled 7702 assumptions raises AssumptionError.
- Debug mode includes per-month `tax_7702_debug` payload.

Golden/determinism:
- Add a new example request that includes 7702 assumptions and expected report.
- Ensure ledger rows are unchanged; only metadata changes.
- Determinism test produces byte-identical output.

## 10) Versioning
- Adding new output fields requires `SCHEMA_VERSION` bump.
- If any rounding or ordering changes are required (not expected here), bump `CALC_VERSION`.

## 11) Open questions / decisions needed
- Exact statutory timing for GPT limit (annual vs. pro-rata monthly).
- Definition of cash value for CVAT (CSV vs. AV vs. AV + loan adjustments).
- Treatment of loans and withdrawals for GPT/CVAT.
- Treatment of face amount or benefit changes (material change rules).
- Whether corridor factors for 7702 should be distinct from current corridor proxy.
- Whether NSP should be static or duration-based schedule.

## 12) Milestone breakdown (PR-sized)
1) Add schema models for Tax7702Assumptions and Tax7702Report.
2) Implement `opie/tax/irc_7702.py` with GPT + CVAT checks.
3) Wire report generation into `run_illustration()` (post-ledger).
4) Add tests + goldens, bump versions as required.

## 13) Acceptance criteria
- 7702 checks run only when enabled and only for cash-value products.
- For each scenario, the report is deterministic and includes pass/fail with first-failure context.
- `test_type = "both"` fails if either test fails, and reports both sets of failures.
- No change to engine ordering or ledger math; ledger rows remain identical for existing examples.
- JSON output remains stable and deterministic across runs.
- All unit, integration, and golden tests pass.
