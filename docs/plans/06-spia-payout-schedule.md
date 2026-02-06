# SPIA Payout Factors + Payment Schedule Ledger
Status: planned (2026-01-08)
Owner: TBD

## 1) Summary
Upgrade the SPIA (toy) implementation to support payout factor tables and a
monthly payment schedule reflected in the ledger.

## 2) Goals
- Add payout factor tables to assumptions (per scenario).
- Emit a deterministic monthly payment amount in the ledger.
- Keep engine ordering explicit and deterministic.

## 3) Non-goals
- Mortality/longevity modeling.
- Complex rider interactions or tax treatment.
- External data fetching or live rates.

## 4) Proposed data model (minimal)
- Add `spia_payout_factors: dict[int, DecimalInput]` to
  `AnnuityScenarioAssumptions` keyed by attained age.
- Add optional request fields:
  - `payout_start_month: int = 1`
  - `payout_end_month: int | None` (default to `duration_months`)
- Add ledger field: `annuity_payment` (Decimal).

## 5) Ordering decision (explicit)
Proposed ordering for SPIA payment:
1) Premium and charges (existing)
2) Interest crediting (existing)
3) **SPIA payout** (new; subtract from AV after interest)
4) Surrender charge / CSV (existing)

If this ordering is adopted, treat as a calculation change and bump
`CALC_VERSION`. Adding the new ledger field requires `SCHEMA_VERSION` bump.

## 6) Diff-by-diff plan
1) **Schema + spec**
   - Add `annuity_payment` to `LedgerRow` and update schema tests.
   - Add request fields (`payout_start_month`, `payout_end_month`) and validate.
   - Update `docs/opie_mvp_spec.md` with SPIA payout rules and ordering.
   - Bump `SCHEMA_VERSION` (and `CALC_VERSION` if ordering changes).
2) **Assumptions**
   - Extend `AnnuityScenarioAssumptions` with `spia_payout_factors`.
   - Update loaders and validation (missing factor for attained age -> error).
3) **Engine + product hooks**
   - Add a new optional hook (e.g., `benefit_payout`) to `ProductHooks` with
     default zero for non-annuity products.
   - Call the hook at the chosen ordering point and emit `annuity_payment`.
   - Implement SPIA payout amount in `opie/products/annuity_spia.py`:
     `payment = base_premium * factor / 12`, applied for months in range.
4) **Tests + goldens**
   - Unit tests for factor lookup and payment schedule.
   - Add at least one SPIA golden with payouts (current + guaranteed).
   - Determinism tests for payout outputs.
5) **Docs + examples**
   - Add/update an example request to show payout factors.
   - Document CLI usage in README.

## 7) Acceptance criteria
- SPIA ledgers include `annuity_payment` for payout months.
- Payouts are deterministic and quantized to currency quantum.
- Missing factor entries produce clear validation errors.
- Goldens updated intentionally with version bumps.

## 8) Open questions
- Should payout factors be per $1 premium or per $1,000 premium?
- Should payout start immediately (month 1) or allow deferral?
