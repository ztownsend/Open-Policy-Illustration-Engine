# OPIE Technical Architecture
**Open Policy Illustration Engine (OPIE)**  
*A deterministic, testable policy-illustration engine with library + CLI + API surfaces.*

This document is written to be consumable by:
- **Humans**: clear mental model, boundaries, and extension points
- **Codex/agents**: explicit file layout, contracts, invariants, and “how to change safely” procedures

---

## 0) TL;DR (for fast readers and agents)

- The **engine** is a pure, deterministic projection loop that:
  - runs **two scenarios** (`current`, `guaranteed`)
  - enforces **ordering**, **rounding**, and **lapse semantics**
  - produces a **ledger** (rows)
- **Products** are plugins via a small hook interface (charges, NAR, surrender schedule, DB).
- **Assumptions** load from JSON/CSV into strongly-typed models.
- Tests use **golden ledgers** + **invariants** to prevent “penny drift.”

If you change math, you must:
1) add/adjust unit tests
2) run `pytest`
3) if intentional, update golden files with the dedicated script/command
4) re-run `pytest` and ensure invariants pass

---

## 1) Design Principles

### 1.1 Determinism is a feature
- All calculations use `decimal.Decimal` (no floats).
- Rounding is centralized, explicit, and versioned.
- Order of operations is **normative** (see Spec §8.2).

### 1.2 Products are configuration + hooks, not forks
The engine is stable; products implement hooks with minimal surface area.

### 1.3 Outputs are stable contracts
- Pydantic models define request/response.
- JSON output must be stable across OS/Python versions (sorted keys, normalized Decimals).

### 1.4 Test strategy favors regression safety
- Golden files capture full ledgers.
- Invariants catch logical errors that golden files might miss (e.g., CSV > AV).

---

## 2) Component Overview

### 2.1 High-level components
- **Core Engine** (`opie/core/engine.py`)
- **Product Implementations** (`opie/products/*`)
- **Assumptions + Tables** (`opie/assumptions/*`)
- **Interfaces**
  - Library function (`opie/__init__.py` or `opie/core/api.py`)
  - CLI (`opie/cli/main.py`)
  - FastAPI (`opie/api/app.py`)
- **Testing**
  - Golden ledgers (`tests/golden/*`)
  - Invariants (`opie/core/invariants.py`)
  - Example fixtures (`examples/*`)

### 2.2 Data flow (conceptual)

```
IllustrationRequest
   │
   ├─ validate + normalize (Pydantic + Decimal normalization)
   │
   ├─ for scenario in {current, guaranteed}:
   │     ├─ build ScenarioContext (assumptions + tables)
   │     ├─ run Engine(product_hooks, context, request)
   │     └─ produce Ledger(rows)
   │
   └─ IllustrationResult(ledgers + metadata)
```

---

## 3) Repository Layout (authoritative)

```
opie/
  __init__.py                 # exports run_illustration()
  core/
    types.py                  # request/response models, enums, shared dataclasses
    money.py                  # Decimal context, rounding helpers, quantize policy
    time.py                   # month indexing, policy year, attained age utilities
    engine.py                 # projection loop + scenario runner
    ledger.py                 # ledger row building, serialization helpers
    invariants.py             # invariant checks; raise with context on violation
    versioning.py             # calc_version, rounding_policy_id, schema version
  products/
    base.py                   # ProductHooks protocol + shared helpers
    ul_simple.py              # SimpleUL hooks
    term_level.py             # LevelTerm hooks
  assumptions/
    models.py                 # scenario assumption models (UL + Term)
    tables.py                 # COI table loading/lookup
    schedules.py              # surrender schedule parsing
    loaders.py                # load request+assumptions from JSON/CSV
  api/
    app.py                    # FastAPI app + route(s)
    http_models.py            # request/response wrappers if needed
  cli/
    main.py                   # CLI entrypoint (Typer recommended)
    io.py                     # read/write JSON/CSV, normalization
tests/
  golden/
    ul_simple_current.json
    ul_simple_guaranteed.json
    ul_lapse_current.json
    ul_lapse_guaranteed.json
    term_current.json
    term_guaranteed.json
  test_ul_golden.py
  test_term_golden.py
  test_invariants.py
  test_determinism.py
examples/
  ul_simple_request.json
  ul_lapse_request.json
  term_request.json
scripts/
  update_golden.py            # controlled golden update tool (intentional changes)
```

**Note:** Keep `engine.py` free of product-specific logic. All product variability lives behind hooks.

---

## 4) Core Domain Model

### 4.1 Core models (Pydantic)
Defined in `opie/core/types.py`.

- `IllustrationRequest`
- `ScenarioAssumptions` (per scenario)
- `IllustrationResult`
- `Ledger`, `LedgerRow` (with union-like UL/Term optional fields)

### 4.2 Internal calculation state
Defined as lightweight dataclasses in `opie/core/engine.py` to avoid accidental schema coupling:

- `ProjectionState`
  - `t`
  - `policy_year`
  - `attained_age`
  - `status`
  - `av_eop_prev` (UL only)
  - `cumulative_premium`

- `ScenarioContext`
  - scenario name
  - validated assumptions
  - table lookups (COI)
  - rounding policy

---

## 5) Engine Architecture

### 5.1 Engine responsibilities
The engine must:
- execute the **normative ordering**
- apply **floors** and **rounding**
- run **lapse semantics**
- produce **ledger rows** that match the public schema
- validate **invariants** (optionally per-row during run)

### 5.2 Normative ordering (owned by engine)
The engine’s monthly steps are:

1) compute BOP values  
2) apply premium and loads  
3) compute charges (via hooks)  
4) compute `AV_mid_raw`  
5) lapse check  
6) interest crediting  
7) EOP and CSV  
8) emit row

This ordering must not vary by product.

### 5.3 Lapse semantics (owned by engine)
- If `AV_mid_raw < 0`, lapse occurs **in month t**.
- The engine **emits the fatal month** row:
  - `AV_mid_raw` negative
  - `interest = 0`
  - `AV_eop = 0`
  - status `lapsed`
- The engine stops projection after month `t` (MVP).

Products do not implement lapse logic.

---

## 6) Product Plugin Interface (Hooks)

Defined in `opie/products/base.py` as a `Protocol` (or ABC).

### 6.1 Required hooks (MVP)

- `premium_and_loads(state, request, scenario) -> PremiumResult`
- `monthly_charges(state, request, scenario, av_bop, premium_result) -> ChargeResult`
- `death_benefit(state, request, scenario, av_bop, av_eop) -> Decimal`

### 6.2 UL-only hooks
- `net_amount_at_risk(state, request, scenario, av_bop) -> Decimal`
- `surrender_charge(state, request, scenario, t) -> Decimal`

### 6.3 Hook output contracts
`PremiumResult`:
- `premium`
- `premium_load`
- `net_premium_to_av`

`ChargeResult`:
- `policy_fee`
- `admin_fee`
- `coi_charge`
- `charges_total`
- (optional) fields for later extensions

**Contract rules**
- Hooks must return Decimals already normalized to engine precision.
- Hooks must be pure functions of their inputs (no global state, no I/O).

---

## 7) Assumptions & Tables

### 7.1 COI table
- Loaded from CSV/JSON in `opie/assumptions/tables.py`.
- In-memory representation:
  - `dict[int, Decimal]` mapping attained age -> annual COI rate per $1,000
- Lookup must:
  - raise a clear error if age out of range
  - be deterministic
  - optionally support interpolation later (not MVP)

### 7.2 Surrender schedule
- Parsed by `opie/assumptions/schedules.py`.
- MVP allows:
  - explicit month → charge map
  - or policy-year map expanded to months

### 7.3 Scenario composition
`opie/assumptions/models.py` defines:
- `ULScenarioAssumptions`
- `TermScenarioAssumptions`

`opie/assumptions/loaders.py`:
- validates and normalizes incoming JSON into these models

---

## 8) Money, Precision, and Serialization

### 8.1 Decimal context
Centralized in `opie/core/money.py`:
- `DECIMAL_CONTEXT` (precision)
- `ROUNDING_MODE` (default `ROUND_HALF_UP`)
- `quantize_money(x) -> Decimal` (cents)
- `quantize_rate(x) -> Decimal` (high precision)

### 8.2 Rounding policy
MVP recommended:
- Use unrounded `AV_mid_raw` for lapse check.
- Round ledger fields at emission time.

This prevents accidental “lapse one month earlier” behavior caused by rounding.

### 8.3 JSON normalization
To keep golden files stable:
- serialize Decimals as strings (recommended) OR exact quantized numbers
- sort keys in JSON output
- stable ordering for lists (already stable)

Implement in `opie/core/ledger.py` or `opie/cli/io.py`.

---

## 9) Interface Surfaces

### 9.1 Library
`opie.run_illustration(request: IllustrationRequest) -> IllustrationResult`

- pure function interface
- no I/O
- no global mutation

### 9.2 CLI
`opie illustrate --in examples/ul_simple_request.json --out out.json --format json`

Responsibilities:
- read request JSON
- validate and run
- write JSON/CSV
- exit non-zero on validation or invariant failure

### 9.3 FastAPI
`POST /v1/illustrations`

Responsibilities:
- parse request body
- call `run_illustration`
- return JSON response
- convert errors into structured HTTP errors (400 validation, 422 schema, 500 internal)

---

## 10) Error Handling

### 10.1 Error types
Define explicit exceptions in `opie/core/types.py` or `opie/core/errors.py`:

- `ValidationError` (schema/inputs)
- `AssumptionError` (missing COI age, bad schedule)
- `InvariantViolation` (post-run assertion failure)
- `EngineError` (unexpected)

### 10.2 Error messages
Errors must include:
- product_code
- scenario
- month index `t` if applicable
- the specific offending value(s)

This is critical for debugging golden diffs (“off by a penny in month 47”).

---

## 11) Testing Architecture

### 11.1 Golden tests
- Each product/scenario has golden JSON in `tests/golden/`.
- `test_ul_golden.py` loads request fixture, runs engine, compares normalized output to golden.

Comparison must:
- normalize decimals
- allow stable ordering
- show useful diff on failure (pytest diff output)

### 11.2 Invariant tests
`test_invariants.py` validates:
- `AV_eop >= 0`
- `CSV <= AV_eop`
- monotone cumulative premium
- lapse row semantics (interest=0, AV_eop=0, DB=0)

### 11.3 Determinism tests
`test_determinism.py`:
- same request run twice produces identical JSON (byte-for-byte after normalization)

### 11.4 Updating golden files (controlled)
Golden files must only be updated via `scripts/update_golden.py` (or a CLI flag).
The script must:
- print a summary of what changed
- require an explicit `--yes` confirmation flag (for local dev)
- never run in CI

---

## 12) Versioning and Compatibility

### 12.1 Calculation versioning
`opie/core/versioning.py` provides:
- `CALC_VERSION` (semver)
- `ROUNDING_POLICY_ID`
- `SCHEMA_VERSION`

Any change to:
- ordering
- rounding points
- lapse semantics
must bump at least `CALC_VERSION` minor (or major if breaking).

### 12.2 Output metadata
Every `IllustrationResult` includes:
- `calc_version`
- `rounding_policy_id`
- `schema_version`

Golden files should include these fields so changes are explicit.

---

## 13) Observability (minimal, MVP)

### 13.1 Structured logging
- Library: no logging by default (caller decides).
- CLI/API: log request_id, product_code, scenario, duration, runtime.

### 13.2 Tracing (future)
Add OpenTelemetry later; not required for MVP.

---

## 14) Security and Compliance (MVP posture)

- OPIE is a calculator; it should not store PII.
- API should:
  - enforce request size limits
  - avoid echoing sensitive inputs in error messages
- Do not log full request bodies by default.

---

## 15) Build & Run (recommended defaults)

### 15.1 Tooling
Recommended:
- Python 3.12+
- `pytest`
- `ruff` (lint/format)
- `mypy` (optional MVP)
- `fastapi` + `uvicorn`
- `typer` for CLI

### 15.2 Commands (targets you should implement)
- `pytest`
- `python -m opie.cli.main illustrate --in examples/ul_simple_request.json --out /tmp/out.json`
- `uvicorn opie.api.app:app --reload`

Optional `Makefile`:
- `make test`
- `make lint`
- `make fmt`
- `make run-api`
- `make update-golden`

---

## 16) Extension Guide (how to add a new product)

1) Create `opie/products/<new_product>.py`
2) Implement `ProductHooks` interface
3) Register product code → hooks in a single registry, e.g. `opie/products/registry.py`
4) Add example request in `examples/`
5) Add golden files in `tests/golden/`
6) Add/extend invariants if new fields are added
7) Run full suite; update golden files only if intentional

---

## 17) Codex/Agent Working Rules (do not skip)

When implementing changes:
- Keep the engine pure; do not add product-specific branching in `engine.py`.
- Any new ledger field must:
  - be added to schema models
  - be serialized deterministically
  - have at least one invariant test or golden coverage
- Any numeric change must come with:
  - a test that fails before change and passes after
  - updated golden files via the golden updater (only if change is intended)

When debugging a golden diff:
- Identify first month where divergence occurs.
- Inspect:
  - premium/load ordering
  - charge ordering
  - rounding point
  - lapse check boundary
- Fix root cause, not symptoms.

---

## Appendix A: Minimal sequence diagram (UL month)

```
Engine.run_month(t)
  AV_bop <- prev AV_eop
  prem <- product.premium_and_loads(...)
  charges <- product.monthly_charges(..., AV_bop, prem)
  AV_mid_raw <- AV_bop + prem.net - charges.total
  if AV_mid_raw < 0: emit lapsed row; stop
  AV_mid <- max(0, AV_mid_raw)
  interest <- i_month * AV_mid
  AV_eop <- AV_mid + interest
  surrender <- product.surrender_charge(t)
  CSV <- max(0, AV_eop - surrender)
  DB <- product.death_benefit(...)
  emit row
```
