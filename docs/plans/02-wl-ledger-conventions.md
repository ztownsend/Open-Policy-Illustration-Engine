# Whole Life Ledger Conventions
Status: planned (2026-01-08)
Owner: TBD

## 1) Summary
Explicitly document how Whole Life (WL) cash value and surrender value schedules
are interpreted at the monthly ledger level (step vs interpolation) to match
current implementation.

## 2) Goals
- Clarify that WL schedules are month-indexed and not interpolated.
- Document error behavior when schedule entries are missing.
- Preserve existing WL outputs and goldens.

## 3) Non-goals
- Changing WL calculations or ordering.
- Adding new WL features.
- Updating goldens.

## 4) Touchpoints
- `docs/opie_mvp_spec.md` (WL assumptions + ledger rules)
- `opie/products/wl_nonpar.py` (inline comment pointer)
- Optional: `docs/opie_technical_architecture.md`

## 5) Diff-by-diff plan
1) Update the WL section in `docs/opie_mvp_spec.md` to state:
   - schedules are month-indexed
   - no interpolation is performed
   - missing month entries are errors
   - surrender charge is computed as `CV - SV` (clipped at zero)
2) Add a short comment in `opie/products/wl_nonpar.py` referencing the spec
   section to make the convention discoverable in code.
3) (Optional) Add a small unit test asserting that missing WL schedule entries
   raise `AssumptionError` for clarity.

## 6) Acceptance criteria
- WL schedule interpretation is explicit in the spec.
- No code behavior changes; goldens remain unchanged.

## 7) Tests
- Optional small unit test; otherwise documentation-only.
