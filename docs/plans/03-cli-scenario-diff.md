# CLI Scenario-to-Scenario Diff
Status: planned (2026-01-08)
Owner: TBD

## 1) Summary
Add a CLI path to diff two scenarios within a single illustration result file
(`current` vs `guaranteed`) without requiring separate files.

## 2) Goals
- Provide a CLI option to diff scenarios in one result payload.
- Keep the existing `opie diff` behavior intact for two-file diffs.
- Support base ledgers and optional reporting-currency ledgers.

## 3) Non-goals
- UI changes (already has diff view).
- Changing the diff algorithm or output format.
- Adding network or external tooling.

## 4) Proposed CLI UX
- Extend `opie diff` with:
  - `--within <result.json>` (single file)
  - `--scenario-a current` (default)
  - `--scenario-b guaranteed` (default)
  - `--currency USD|EUR|BTC` (optional; for `ledgers_by_currency`)

## 5) Diff-by-diff plan
1) Update `opie/cli/diff.py` with a helper that extracts two ledgers from a
   single payload (base ledgers by default, or `ledgers_by_currency` when
   `--currency` is provided).
2) Update `opie/cli/main.py` to add the new `--within`, `--scenario-a`,
   `--scenario-b`, and `--currency` options while preserving the existing
   `--a/--b` path.
3) Add tests in `tests/test_diff.py` covering:
   - diffing `current` vs `guaranteed` from a single result payload
   - error when a scenario is missing
   - `--currency` selection when `ledgers_by_currency` is present
4) Update README CLI examples with the new usage.

## 6) Acceptance criteria
- `opie diff --within result.json` prints the first diff between scenarios.
- Proper error messages for missing scenarios or missing currency ledgers.
- No changes to two-file diff output.

## 7) Tests
- Unit/CLI tests in `tests/test_diff.py`.
