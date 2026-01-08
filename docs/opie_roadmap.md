# OPIE Roadmap (Repo-Ready, Agent-Executable)
**Open Policy Illustration Engine (OPIE)**  
This roadmap is designed to be dropped into `docs/roadmap.md` and executed incrementally by humans and coding agents (Codex). It is intentionally explicit about boundaries, file touchpoints, tests, and “definition of done.”

> Companion docs (recommended to keep alongside this file):
> - `docs/opie_mvp_spec.md` — MVP requirements and normative ordering
> - `docs/opie_technical_architecture.md` — module boundaries and hook interfaces

---

## How to use this roadmap

### Execution model
- Work **phase-by-phase** in order.
- Each phase is broken into **PR-sized diffs** (“Work Items”).
- For each work item:
  1) implement
  2) write/adjust tests
  3) run `pytest`
  4) fix failures
  5) only then move to next work item

### Definition of Done (DoD) for every work item
- [ ] Code compiles / imports
- [ ] `pytest` passes
- [ ] Lint passes (if configured)
- [ ] Any new ledger fields are:
  - [ ] in schema models
  - [ ] deterministically serialized
  - [ ] covered by golden files or invariants
- [ ] If outputs changed intentionally:
  - [ ] golden files updated only via the golden update tool/script
  - [ ] change recorded in `CALC_VERSION` and/or policy IDs as required

### Golden file policy (non-negotiable)
- Golden files are **the contract** for outputs.
- Never hand-edit goldens. Update via:
  - `python scripts/update_golden.py --request examples/<...>.json --yes`
- CI must fail if outputs drift.

---

## Milestone map (human-friendly)
- **v0.1**: MVP engine + UL/Term + two scenarios + CLI/API + goldens
- **v0.2**: Debug/diff tooling + better error messages + table packs v0
- **v0.3**: Premium solve + DB Option 2
- **v0.4**: Loans/withdrawals + rider framework
- **v0.5**: Whole Life + starter annuity
- **v0.6**: UI explorer + PDF renderer (separate module)
- **v0.7**: Batch mode + artifact bundles + conformance suite
- **v1.0**: Stable contracts + plugin ecosystem + governance

---

# Phase 0 — Repo foundation and “make it boring”
**Goal:** predictable tooling, deterministic outputs, contribution safety rails.

## 0.1 Tooling + CI
**Deliverables**
- [ ] `pyproject.toml` with dependencies and tooling config
- [ ] `ruff` (lint/format), `pytest`
- [ ] `.pre-commit-config.yaml`
- [ ] GitHub Actions workflow: lint + tests

**Files**
- `pyproject.toml`
- `.pre-commit-config.yaml`
- `.github/workflows/ci.yml`
- `Makefile` (optional)

**Acceptance criteria**
- `pytest` passes on macOS + Linux in CI
- `ruff check .` passes

---

## 0.2 Project metadata + versioning
**Deliverables**
- [ ] Add versioning module:
  - `CALC_VERSION`
  - `SCHEMA_VERSION`
  - `ROUNDING_POLICY_ID`
- [ ] Result metadata includes these values
- [x] Result metadata includes `currency_code`

**Files**
- `opie/core/versioning.py`
- `opie/core/types.py` (response metadata)
- Tests updated accordingly

**Acceptance criteria**
- every `IllustrationResult` includes versions
- goldens include versions (so changes are explicit)

---

## 0.3 Deterministic JSON serialization conventions
**Deliverables**
- [ ] Decimal serialization policy (recommend: stringify Decimals)
- [ ] Sorted JSON keys, stable output formatting
- [ ] Shared serializer used by CLI and API

**Files**
- `opie/core/ledger.py` (or `opie/cli/io.py`)
- tests for stable serialization

**Acceptance criteria**
- “run twice” determinism test passes byte-for-byte after normalization

---

# Phase 1 — MVP engine: SimpleUL + LevelTerm with locked semantics (v0.1)
**Goal:** implement the MVP spec exactly and lock it down with goldens.

## 1.1 Schema models (request/response) + validation
**Deliverables**
- [ ] `IllustrationRequest` and `IllustrationResult` Pydantic models
- [ ] `Ledger`, `LedgerRow` models with UL + Term optional fields
- [ ] Input normalization (Decisions: Decimal parsing, required defaults)

**Files**
- `opie/core/types.py`

**Tests**
- schema validation tests (good/bad payloads)

**Acceptance criteria**
- requests validate and normalize cleanly
- schema errors are readable

---

## 1.2 Money + rounding policy module
**Deliverables**
- [ ] Decimal context
- [x] `quantize_money()` (currency-aware), `quantize_rate()`
- [ ] Explicit rounding points guidance (document in code)

**Files**
- `opie/core/money.py`

**Tests**
- unit tests for rounding behavior

---

## 1.3 Assumptions loading (COI + surrender schedule)
**Deliverables**
- [ ] COI table loader (CSV + JSON)
- [ ] Surrender schedule parser (month map + year map expanded to months)
- [ ] Scenario models for UL and Term

**Files**
- `opie/assumptions/models.py`
- `opie/assumptions/tables.py`
- `opie/assumptions/schedules.py`
- `opie/assumptions/loaders.py`

**Tests**
- table load tests (missing ages, bad formats)
- schedule expansion tests

---

## 1.4 Product hook interface
**Deliverables**
- [ ] `ProductHooks` Protocol (premium+loads, charges, DB)
- [ ] UL-only hooks (NAR, surrender)
- [ ] Product registry mapping `product_code -> hooks`

**Files**
- `opie/products/base.py`
- `opie/products/registry.py`

**Tests**
- registry lookup tests

---

## 1.5 Core engine (scenario runner + monthly loop)
**Deliverables**
- [ ] Engine implements normative ordering from spec:
  - AV_bop → premium/load → charges → AV_mid_raw → lapse check → interest → AV_eop → CSV → emit
- [ ] Lapse semantics: emit fatal month row, stop
- [ ] Scenario runner: run `current` + `guaranteed`

**Files**
- `opie/core/engine.py`
- `opie/core/time.py`

**Tests**
- minimal engine unit tests (no goldens yet)

---

## 1.6 Implement `SimpleUL` product
**Deliverables**
- [ ] UL hooks implement:
  - premium schedule resolution
  - loads/fees
  - NAR = max(0, face - AV_bop)
  - COI = (annual/12) * (NAR/1000)
  - surrender charge schedule
  - DB Option 1 (level)

**Files**
- `opie/products/ul_simple.py`

**Tests**
- unit tests for charges and NAR
- at least one lapse boundary test

---

## 1.7 Implement `LevelTerm` product
**Deliverables**
- [ ] Term hooks implement:
  - premium schedule resolution (and/or annual premium + modal factor)
  - status in_force/expired based on term length
  - DB as face when in force

**Files**
- `opie/products/term_level.py`

**Tests**
- unit tests for term expiry boundary

---

## 1.8 Invariants module
**Deliverables**
- [ ] Invariants checks for UL:
  - AV_eop >= 0
  - CSV <= AV_eop
  - cumulative premium monotone
  - lapse row semantics: interest=0, AV_eop=0, DB=0
- [ ] Invariants checks for Term:
  - DB=0 when expired
  - cumulative premium monotone

**Files**
- `opie/core/invariants.py`

**Tests**
- invariants tests with representative ledgers

---

## 1.9 Golden fixtures + golden test harness
**Deliverables**
- [ ] Example requests in `examples/`
  - UL stays in force
  - UL lapses mid-projection
  - Term
- [ ] Golden outputs for:
  - UL in-force: current + guaranteed
  - UL lapse: current + guaranteed
  - Term: current + guaranteed
- [ ] Golden test harness:
  - normalize output (decimal formatting, key ordering)
  - compare to golden files with useful diffs

**Files**
- `examples/*.json`
- `tests/golden/*.json`
- `tests/test_ul_golden.py`
- `tests/test_term_golden.py`
- `scripts/update_golden.py`

**Acceptance criteria**
- goldens pass on CI
- output is byte-stable across platforms

---

## 1.10 Interfaces: library export, CLI, FastAPI
**Deliverables**
- [ ] Library:
  - `opie.run_illustration()` exported from `opie/__init__.py`
- [ ] CLI:
  - `opie illustrate --in --out --format json|csv`
- [ ] FastAPI:
  - `POST /v1/illustrations`

**Files**
- `opie/__init__.py`
- `opie/cli/main.py`
- `opie/cli/io.py`
- `opie/api/app.py`

**Tests**
- smoke tests for CLI (subprocess or direct call)
- API tests (FastAPI TestClient)

---

# Phase 2 — Debug-first tooling and error hardening (v0.2)
**Goal:** make it trivial to locate and explain divergences.

## 2.1 Error taxonomy + structured messages
**Deliverables**
- [ ] Exception classes:
  - `AssumptionError`, `InvariantViolation`, `EngineError`
- [ ] Errors include scenario + month `t` + key values

**Files**
- `opie/core/errors.py`
- update engine/assumptions to raise these

**Tests**
- verify error payload content

---

## 2.2 Ledger diff tooling
**Deliverables**
- [ ] `opie diff --a ledgerA.json --b ledgerB.json`
  - first month/field difference
  - numeric delta
- [ ] optional: scenario-to-scenario diff within one result

**Files**
- `opie/cli/diff.py`
- `opie/cli/main.py` (subcommand wiring)

**Tests**
- known-diff fixture test

---

## 2.3 Debug trace mode (light)
**Deliverables**
- [ ] Optional request flag `debug=true` to emit extra fields:
  - unquantized intermediates (or selected ones)
- [ ] Trace mode must not change base outputs unless explicitly enabled

**Files**
- `opie/core/engine.py`
- `opie/core/types.py` (debug flag + debug fields)

**Tests**
- debug output appears only when enabled

---

# Phase 3 — UL realism upgrades without product sprawl (v0.2–v0.3)
**Goal:** improve realism while keeping scope contained.

## 3.1 Interest conversion modes
**Deliverables**
- [ ] Support `interest_mode`:
  - `nominal_div_12`
  - `effective_monthly`
- [ ] Mode recorded in metadata and/or scenario assumptions

**Files**
- `opie/assumptions/models.py`
- `opie/core/engine.py`

**Tests**
- goldens for each mode (at least one example)

---

## 3.2 Grace period semantics (minimal)
**Deliverables**
- [ ] `grace_months` config (default 0)
- [ ] Lapse only after grace exhausted
- [ ] Still emit “fatal month” row where lapse resolves

**Files**
- `opie/core/engine.py`
- `opie/core/types.py`

**Tests**
- grace boundary tests + goldens

---

## 3.3 Charge assessed vs paid (optional but powerful)
**Deliverables**
- [ ] Add fields:
  - `charges_assessed`
  - `charges_paid`
  - `charge_shortfall`
- [ ] Keep ordering deterministic

**Files**
- `opie/core/types.py`
- `opie/core/engine.py`

**Tests**
- invariants around shortfall; goldens updated intentionally

---

# Phase 4 — Premium solve (v0.3)
**Goal:** deterministic solver to answer “what premium keeps policy in force.”

## 4.1 Solve framework (binary search)
**Deliverables**
- [ ] Solve modes:
  - keep in force through month N
  - hit target AV at month N
- [ ] Deterministic iteration count / tolerance
- [ ] Output solver metadata

**Files**
- `opie/core/solve.py`
- `opie/core/types.py`

**Tests**
- solver determinism tests
- golden solve examples

---

## 4.2 Scenario solve strategy options
**Deliverables**
- [ ] Config:
  - solve in current, illustrate both
  - solve per scenario
- [ ] Explicit output labels

**Files**
- `opie/core/solve.py`
- `opie/core/types.py`

**Tests**
- golden coverage for both strategies

---

# Phase 5 — DB Option 2 + corridor approximation (v0.3–v0.4)
**Goal:** expand UL feature set while preserving engine invariants.

## 5.1 DB Option 2 (increasing)
**Deliverables**
- [ ] DB option switch
- [ ] NAR updated accordingly
- [ ] Goldens updated

**Files**
- `opie/products/ul_simple.py`
- `opie/core/types.py`

---

## 5.2 Corridor approximation (optional module)
**Deliverables**
- [ ] Optional corridor table by age
- [ ] DB uplift to satisfy corridor
- [ ] Output fields indicating uplift

**Files**
- `opie/assumptions/tables.py`
- `opie/products/ul_simple.py`

---

# Phase 6 — Withdrawals and loans (v0.4)
**Goal:** path-dependent money moves.

## 6.1 Withdrawals
**Deliverables**
- [ ] withdrawal schedule month→amount
- [ ] declared ordering
- [ ] new ledger fields

**Files**
- `opie/core/types.py`
- `opie/core/engine.py`
- `examples/*`, goldens

---

## 6.2 Loans (basic)
**Deliverables**
- [ ] loan balance, loan interest
- [ ] repayments schedule
- [ ] CSV impacted by loan

**Files**
- `opie/core/types.py`
- `opie/core/engine.py`

---

# Phase 7 — Riders framework (v0.4)
**Goal:** composability.

## 7.1 Rider hook interface + stacking
**Deliverables**
- [ ] `RiderHooks` with deterministic ordering
- [ ] example rider: simple flat monthly charge rider

**Files**
- `opie/products/riders/base.py`
- `opie/products/riders/examples.py`
- engine wiring

---

# Phase 8 — Whole Life (WL) (v0.5)
**Goal:** prove engine supports a different product family.

## 8.1 Non-par WL (simplified)
**Deliverables**
- [ ] WL product with table-driven CV and SV
- [ ] monthly ledger conventions declared (interpolation vs step)

**Files**
- `opie/products/wl_nonpar.py`
- assumptions tables as needed

---

# Phase 9 — Annuities starter set (v0.5)
**Goal:** broaden domain coverage.

## 9.1 Deferred fixed annuity (simple)
- accumulation value + surrender charge

## 9.2 SPIA (toy)
- payout factor tables + payment schedule ledger

---

# Phase 10 — Assumption packs + provenance (v0.2–v0.6)
**Goal:** portable assumptions with checksums and licensing clarity.

## 10.1 Assumption pack format v0
**Deliverables**
- [ ] `pack.json` manifest:
  - name, version, license, source, checksum
- [ ] CLI validate and list pack contents

**Files**
- `opie/assumptions/packs.py`
- `opie/cli/pack.py`

---

# Phase 11 — Conformance suite + cross-engine comparison (v0.7)
**Goal:** OPIE becomes an audit-friendly standard.

## 11.1 Conformance test runner
- canonical cases + expected outputs
- publish results for forks/plugins

## 11.2 Comparison harness
- first-diff reports + max-diff stats

---

# Phase 12 — UI Explorer (v0.6)
**Goal:** a demo that makes people “get it” instantly.
- scenario toggle
- diff view
- lapse highlight
- request builder and export

(Recommended as a separate `opie-ui/` package or sibling repo.)

---

# Phase 13 — PDF renderer (separate package)
**Goal:** formatting only, no math.
- `opie-pdf` consumes `IllustrationResult` JSON
- templates and disclosures per jurisdiction (optional)

---

# Phase 14 — Batch mode + performance (v0.7)
**Goal:** run at scale.
- NDJSON input/output
- streaming execution
- assumption context caching
- benchmarks

---

# Phase 15 — Artifact bundles + verification
**Goal:** reproducibility.
- bundle: request + assumptions manifest + result + checksums
- `opie bundle create/verify`

---

# Phase 16+ — Long tail (tax tests, IUL, VUL, ALM-linked crediting, etc.)
This is intentionally deferred until:
- core engine is stable
- plugin ecosystem exists
- conformance suite is mature

---

## Appendix: PR naming convention (recommended)
Use:
- `P0.1-tooling-ci`
- `P1.5-engine-core`
- `P1.9-goldens`
- `P4.1-premium-solve`

---

## Appendix: Standard commands (recommended)
- `pytest`
- `ruff check .`
- `ruff format .`
- `python -m opie.cli.main illustrate --in examples/ul_simple_request.json --out /tmp/out.json`
- `uvicorn opie.api.app:app --reload`
