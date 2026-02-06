# Rounding Points Guidance (Code Comments)
Status: planned (2026-01-08)
Owner: TBD

## 1) Summary
Document the exact rounding/quantization points in code comments so future edits
do not silently change ordering or rounding behavior. This is documentation-only
and must not change outputs.

## 2) Goals
- Make rounding points explicit and easy to audit in code.
- Cross-reference the spec section on normative ordering.
- Preserve deterministic behavior and existing goldens.

## 3) Non-goals
- Changing rounding policy, ordering, or quantization points.
- Adding new ledger fields or modifying outputs.
- Updating goldens.

## 4) Touchpoints
- `opie/core/engine.py` (ledger row construction and rounding points)
- `opie/core/money.py` (rounding policy summary)
- Optional: `docs/opie_mvp_spec.md` (pointer to the code comments)

## 5) Diff-by-diff plan
1) Add a structured comment block in `opie/core/engine.py` immediately above
   ledger row construction that lists each rounding point and the fields affected.
2) Add a short, explicit note in `opie/core/money.py` clarifying the difference
   between money quantization and rate quantization, and where rounding points
   are documented in the engine.
3) (Optional) Add a one-paragraph pointer in `docs/opie_mvp_spec.md` linking to
   the code comment for rounding points.

## 6) Acceptance criteria
- No code path changes; output bytes remain identical.
- Rounding points are documented in code adjacent to their application.
- The comment content matches the current spec ordering.

## 7) Tests
- None required (documentation-only).
