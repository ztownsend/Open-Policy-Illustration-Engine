# OPIE Code Map

A quick orientation to the repository layout and entry points.

## Top Level
- `opie/` - core engine, assumptions, products, CLI, API
- `opie_ui/` - UI Explorer (FastAPI + static HTML)
- `opie_pdf/` - minimal PDF renderer
- `examples/` - example requests used for goldens
- `tests/` - unit tests + golden tests
- `scripts/` - tooling (golden updates, benchmark)
- `conformance/` - canonical cases manifest
- `docs/` - specs, architecture, roadmaps, testing plan

## Core Engine
- `opie/core/engine.py` - monthly loop + scenario runner (normative ordering)
- `opie/core/money.py` - Decimal context + quantize helpers
- `opie/core/types.py` - request/response schema + ledger fields
- `opie/core/invariants.py` - invariant checks
- `opie/core/versioning.py` - CALC/SCHEMA/ROUNDING versions
- `opie/core/ledger.py` - deterministic JSON serialization
- `opie/core/solve.py` - premium solve (binary search)
- `opie/core/errors.py` - `AssumptionError`, `EngineError`, `InvariantViolation`
- `opie/core/time.py` - policy year / attained age utilities

## Products
- `opie/products/base.py` - hook protocols + result types
- `opie/products/registry.py` - `product_code -> hooks` mapping
- `opie/products/ul_simple.py` - Simple UL hooks
- `opie/products/term_level.py` - Level Term hooks
- `opie/products/wl_nonpar.py` - Non-par Whole Life (table-driven)
- `opie/products/annuity_deferred.py` - deferred fixed annuity (toy)
- `opie/products/annuity_spia.py` - SPIA (toy)
- `opie/products/riders/` - rider hooks + example rider

## Assumptions
- `opie/assumptions/models.py` - scenario assumption models
- `opie/assumptions/loaders.py` - loading + normalization
- `opie/assumptions/tables.py` - COI table loading/lookup
- `opie/assumptions/schedules.py` - surrender schedule parsing
- `opie/assumptions/packs.py` - assumption pack manifest + checksum

## Interfaces
- Library: `opie.run_illustration()` in `opie/__init__.py`
- CLI: `opie/cli/main.py`
- API: `opie/api/app.py` (`POST /v1/illustrations`)

## CLI Commands
- `illustrate` - run illustration from request JSON
- `diff` - first-diff report between ledgers
- `compare` - first-diff + max-diff
- `conformance run` - execute canonical cases
- `pack list|validate` - assumption pack tooling
- `batch` - NDJSON batch runner
- `bundle create|verify` - artifact bundles

## Conformance & Comparison
- `opie/conformance/runner.py` - canonical case runner
- `opie/conformance/compare.py` - diff + max-diff stats
- `conformance/cases.json` - canonical cases manifest

## Batch & Bundles
- `opie/batch.py` - NDJSON runner + assumption cache
- `opie/bundle.py` - create/verify bundles

## UI & PDF
- `opie_ui/app.py` - Explorer UI + API mount
- `opie_pdf/render.py` - minimal PDF renderer

## Scripts
- `scripts/update_golden.py` - regenerate golden files
- `scripts/benchmark.py` - basic benchmark harness

## Tests
- `tests/golden/` - output contract files
- `tests/test_*` - unit + golden + CLI/API/UI/PDF tests

## Docs
- `docs/opie_mvp_spec.md` - normative MVP spec for current implementation
- `docs/opie_technical_architecture.md` - module boundaries + extension points
- `docs/opie_roadmap.md` - execution roadmap
- `docs/opie-strategic-roadmap.md` - multi-year vision
- `docs/testing_plan.md` - comprehensive testing plan
