# Changelog

All notable changes to OPIE are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [0.2.0] - 2026-03-15

### Added
- **Indexed Universal Life (IUL)** product (`indexed_ul`) with multi-account indexed crediting
- Index strategies: `fixed`, `point_to_point`, `monthly_average`
- Per-account allocation with cap, floor, and participation rate parameters
- `opie compare-strategies` CLI for IUL sensitivity analysis across cap/participation combos
- `credit_interest()` and `benefit_payout()` hooks in ProductHooks protocol
- IUL example request, golden files, and unit tests

### Changed
- Engine is now fully product-agnostic: interest crediting and benefit payouts are hook-driven
- Extracted shared `resolve_premium()` helper to reduce duplication
- SCHEMA_VERSION bumped to 0.3.0

## [0.1.0] - 2026-03-15

### Added
- Core projection engine with deterministic Decimal math and normative ordering
- Products: `simple_ul`, `level_term`, `wl_nonpar`, `annuity_deferred`, `annuity_spia`
- SPIA payout factor tables with `annuity_payment` ledger field
- Two scenarios per illustration: `current` and `guaranteed`
- Premium solve (keep-in-force and target AV modes)
- Death benefit Option 2 (increasing) with corridor uplift
- Withdrawals, loans, grace period, and rider framework
- IRC 7702 checker (GPT + CVAT, report-only)
- Multi-currency support (base + reporting currencies: USD, EUR, BTC)
- CLI: `illustrate`, `diff` (two-file and within-file), `compare`, `batch`, `conformance`, `bundle`, `pack`
- FastAPI endpoint: `POST /v1/illustrations`
- UI Explorer with scenario diff view, column presets, CSV export
- PDF renderer with template and jurisdiction disclosure support
- Conformance runner with environment metadata in reports
- Assumption packs with manifests and validation
- Artifact bundles with checksums and verification
- Golden file test harness with 40+ golden tests
- Python 3.11+ support with CI matrix (3.11, 3.13, 3.14)
- PEP 561 `py.typed` marker and `__version__` export
