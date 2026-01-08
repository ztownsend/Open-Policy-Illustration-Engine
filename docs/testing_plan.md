# OPIE Testing Plan (Comprehensive)

OPIE is deterministic, math-first software. The test strategy must prevent
"penny drift" and ordering regressions while keeping failures actionable.

## Goals
- Prevent calculation drift (goldens + invariants).
- Keep output contracts stable across OS/Python versions.
- Make regressions easy to localize (first-diff tooling).
- Cover UI/CLI/API integrations without relying on external services.

## Test Layers

### 1) Unit Tests (fast, isolated)
Scope:
- Money rounding, serialization, time utilities.
- Currency quantization (USD/EUR/BTC) + BTC precision validation.
- Monetary input normalization (request schedules, solve bounds, assumption loaders).
- Assumption parsing (tables, schedules, packs).
- Product hooks (UL/Term/WL/Annuity/Riders).
- Engine edge cases (lapse/grace, loans/withdrawals, solve).
- Reporting currency conversion (post-process only).

Examples:
- `tests/test_money.py`
- `tests/test_serialization.py`
- `tests/test_interest_mode.py`
- `tests/test_withdrawals_loans.py`

### 2) Contract Tests (goldens)
Scope:
- Full ledger outputs for canonical scenarios.
- UL (in-force, lapse, solve, loans/withdrawals).
- Term, WL, annuities (short + longer spans).
- Base currency goldens for USD/EUR/BTC.
- Reporting-currency goldens for at least one example request.

Rules:
- Goldens updated only via `scripts/update_golden.py`.
- Any math change requires `CALC_VERSION` bump and rationale.

### 3) Invariants (logic safety net)
Scope:
- Non-negative values (AV/CSV/loan balance).
- Charge consistency (assessed/paid/shortfall).
- Product-specific invariants (Term expiry, annuity DB=0).
- Monetary-field quantization to the request currency quantum.
- Debug-field quantization (when debug is enabled).

### 4) Integration Tests
Scope:
- CLI commands: `illustrate`, `diff`, `compare`, `pack`, `bundle`, `batch`,
  `conformance`.
- CLI currency/reporting flags (`--currency`, `--reporting-currencies`, `--fx-rate`).
- API endpoints (FastAPI TestClient).
- UI Explorer (HTML/DOM presence + API mount).

### 5) Conformance Suite
Scope:
- Canonical cases run via `conformance/cases.json`.
- Output matches expected golden files exactly.
- JSON report includes summary + diff pointer to first failure.

### 6) Performance & Determinism
Scope:
- Determinism: identical request -> byte-identical output.
- Determinism: reporting ledgers are byte-identical for repeated runs.
- Benchmark smoke for regression awareness (not gating unless enabled).

## Test Data Strategy
- Use small, deterministic examples in `examples/`.
- Include edge cases:
  - lapse boundary months
  - grace period
  - loans/withdrawals ordering
  - WL cash value schedule discontinuity
  - annuity premium stop / long duration

## UI Integration Tests
The UI is static HTML + JS. Tests validate:
- HTML includes required controls (scenario toggles, diff view, exports).
- API is mounted at `/api` and functional.
No browser automation required for MVP.

## CI Expectations
Minimum:
- `uv run pytest`
- `uv run ruff check .` (if configured)

Optional:
- `uv run ruff format --check .`

## Coverage Targets (Guidance)
- Core math and serialization: high.
- Product hooks: moderate (per product).
- CLI/API/UI: smoke coverage for contracts and wiring.

## When to Add Tests
Add tests whenever:
- A new ledger field is introduced.
- Calculation ordering changes.
- A new product or hook path is added.
- A new CLI/API/UI feature is shipped.
