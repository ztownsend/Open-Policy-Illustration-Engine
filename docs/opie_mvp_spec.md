# Open Policy Illustration Engine (OPIE) - Spec (Current Implementation)

> A deterministic, versioned policy illustration engine that produces stable month-by-month ledgers under multiple scenarios.

---

## 1) Purpose
OPIE generates policy ledgers/illustrations for life insurance and annuity products given:
- Policy inputs (issue age, face amount, premiums, term, etc.)
- Assumptions (COI tables, loads/fees, crediting rates, surrender charges)
- Scenario definitions (`current` and `guaranteed`)

Outputs are structured ledgers suitable for UI rendering, exports (JSON/CSV), and regression testing (golden files).

---

## 2) Scope (Implemented)
**Functional**
- Monthly ledgers for supported products.
- Two scenarios: `current` and `guaranteed`.
- Deterministic request/response schema with versioned metadata.
- Lapse/grace semantics and deterministic stop conditions.

**Engineering**
- Decimal-only math; no floats.
- Stable JSON serialization (sorted keys, Decimal strings).
- Golden file tests + invariants.
- CLI, FastAPI, UI Explorer, PDF renderer.
- Conformance runner, compare tooling, batch NDJSON, assumption packs, artifact bundles.

---

## 3) Non-Goals (Still Out of Scope)
- Jurisdiction-specific illustration regulation compliance (NAIC, AG49, etc.).
- Participating dividends and dividend options (PUA, OYT).
- IUL/VUL features (index crediting strategies, separate accounts).
- Complex underwriting impacts beyond risk class.
- Guideline premium test / tax qualification logic beyond corridor proxy.
- Policy admin/billing workflows and e-signature flows.

---

## 4) Products Supported
### `simple_ul` (Universal Life-like account value)
- Premiums increase Account Value (AV).
- Monthly deductions: premium load, policy fee, COI, admin fee.
- Interest crediting (nominal/12 or effective monthly).
- Death benefit options: level or increasing (Option 2: Face + AV).
- Surrender charge schedule.

### `level_term`
- Premium schedule or annual premium.
- No cash value.
- Term expiry tracking.

### `wl_nonpar` (simplified)
- Table-driven cash value (CV) and surrender value (SV).
- Premium derived from CV schedule deltas.

### `annuity_deferred` (toy)
- Accumulation value with interest crediting and surrender charges.

### `annuity_spia` (toy)
- Single premium with simplified accumulation fields (no payout schedule yet).

---

## 5) Scenarios
OPIE runs each request under exactly these two scenarios:
- `current`
- `guaranteed`

Each scenario carries its own assumptions. The output contains one ledger per scenario.

---

## 6) Request Model (IllustrationRequest)
**Common fields**
- `product_code`: `simple_ul` | `level_term` | `wl_nonpar` | `annuity_deferred` | `annuity_spia`
- `issue_age`: integer
- `issue_gender`: `M` | `F`
- `risk_class`: string
- `face_amount`: Decimal
- `issue_date`: ISO date
- `duration_months`: integer
- `premium_schedule`: list of premium rules (month or start/end range)
- `scenarios`: `current` + `guaranteed` assumptions
- `debug`: bool (emit debug fields)
- `grace_months`: integer (UL lapse grace)

**UL-specific**
- `death_benefit_option`: `level` | `increasing`
- `minimum_account_value_floor`: Decimal

**Term-specific**
- `term_length_months`: integer
- `modal_factor`: optional Decimal

**Solve (optional)**
- `solve.mode`: `keep_in_force` | `target_av`
- `solve.target_month`: integer
- `solve.target_av`: Decimal (required for `target_av` mode)
- `solve.min_premium`, `solve.max_premium`, `solve.iterations`, `solve.tolerance`
- `solve.strategy`: `current_only` | `per_scenario`

**Withdrawals / Loans (optional)**
- `withdrawal_schedule`: `{month: amount}`
- `loan_draw_schedule`: `{month: amount}`
- `loan_repayment_schedule`: `{month: amount}`
- `loan_interest_rate_annual`: Decimal

**Riders (optional)**
- `riders`: list of `{rider_code, amount}`

---

## 7) Assumptions Model (Per Scenario)
### UL Assumptions
- `crediting_rate_annual`
- `premium_load_pct`
- `monthly_policy_fee`
- `monthly_per_thousand_admin_fee`
- `coi_table` (attained age -> annual rate per $1,000)
- `surrender_charge_schedule` (month -> charge)
- `interest_mode`: `nominal_div_12` | `effective_monthly`
- `corridor_factors` (optional)

### Term Assumptions
- `annual_premium` (if no premium schedule)
- `term_modal_factor` (optional)

### WL Assumptions
- `cash_value_schedule` (month -> CV)
- `surrender_value_schedule` (month -> SV)

### Annuity Assumptions
- `crediting_rate_annual`
- `surrender_charge_schedule`

---

## 8) Normative Ordering (Engine)
Monthly ordering is authoritative:
1) AV BOP
2) Premium + load
3) Charges (policy fee, admin, COI, riders)
4) AV mid (raw)
5) Lapse / grace logic
6) Interest crediting
7) AV EOP
8) Surrender charge -> CSV
9) Emit ledger row

**Lapse semantics**
- If `AV_mid_raw < 0`, policy lapses in month `t`.
- Fatal month row is emitted with `AV_eop = 0` and `status = lapsed`.
- Grace months allow temporary deficit before lapse.

---

## 9) Optional Features: Riders, Loans, Withdrawals, Solve
**Riders**
- Rider charges are added after base charges and included in `charges_assessed`.
- Rider ordering is deterministic (registry order).

**Loans and withdrawals (current implementation: UL only)**
- Interest is credited before withdrawals/loans.
- Loan interest accrues on the prior loan balance before repayment.
- AV is reduced by withdrawal and loan draw.
- CSV is computed after surrender charge and loan balance.

**Premium solve (simple_ul only)**
- Binary search over a level premium applied to months `1..duration_months`.
- `keep_in_force` targets survival to `target_month`.
- `target_av` targets `account_value_eop` at `target_month`.
- Strategy `current_only` solves once and applies to both scenarios; `per_scenario` solves separately.

---

## 10) Output Model (IllustrationResult)
- `request_id` (deterministic hash of normalized request)
- `product_code`
- `ledgers`: `{current, guaranteed}`
- `metadata`: `calc_version`, `schema_version`, `rounding_policy_id`, optional `solve` metadata

**LedgerRow (selected fields)**
- `t`, `policy_year`, `attained_age`, `policy_status`
- `premium`, `cumulative_premium`, `death_benefit`
- `account_value_bop`, `account_value_mid_raw`, `account_value_eop`
- `charges_total`, `charges_assessed`, `charges_paid`, `charge_shortfall`
- `net_amount_at_risk`, `corridor_uplift`
- `interest_credited`
- `surrender_charge`, `cash_surrender_value`
- `withdrawal`, `loan_draw`, `loan_repayment`, `loan_interest`, `loan_balance`
- `rider_charges`

(Additional fields exist for term month, coverage flag, debug columns, etc.)

---

## 11) Determinism & Serialization
- All calculations use `Decimal`.
- JSON output is stable (sorted keys, Decimal string encoding).
- Any calculation change requires a `CALC_VERSION` bump and golden updates.

---

## 12) Interfaces & Tooling
- Library API: `opie.run_illustration()`
- CLI: `opie illustrate`, `diff`, `compare`, `batch`, `pack`, `conformance`, `bundle`
- FastAPI: `POST /v1/illustrations`
- UI Explorer: `opie_ui.app`
- PDF renderer: `opie_pdf.render`
- Golden update script: `scripts/update_golden.py`

---

## 13) Testing & Contracts
- Golden files are the output contract and must be regenerated via the script.
- Invariants guard against logical drift (CSV > AV, negative loan balance, etc.).
- Conformance runner checks canonical cases.
