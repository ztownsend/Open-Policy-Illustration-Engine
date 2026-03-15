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

**Status note (2026-03-15):** All phases 0–15 are complete. Plans 01–06 closed.
CI tests pass on Python 3.11/3.13/3.14.

---

## Milestone map (human-friendly)
- **v0.1**: MVP engine + UL/Term + two scenarios + CLI/API + goldens
- **v0.2**: Debug/diff tooling + better error messages + table packs v0
- **v0.3**: Premium solve + DB Option 2
- **v0.4**: Loans/withdrawals + rider framework
- **v0.5**: Whole Life + starter annuity
- **v0.6**: UI explorer + PDF renderer (separate module)
- **v0.7**: Batch mode + artifact bundles + conformance suite
- **v1.0**: Stable contracts + PyPI package + contributor onboarding

Strategic phases 16+ (post-v1.0) are captured later in this roadmap.

---

## Status overview (2026-03-15)

| Phase | Theme | Status |
| --- | --- | --- |
| 0 | Foundation | Complete |
| 1 | MVP Engine | Complete |
| 2 | Developer Experience | Complete |
| 3 | UL Realism | Complete |
| 4 | Premium Solve | Complete |
| 5 | DB Options & Corridor | Complete |
| 6 | Withdrawals & Loans | Complete |
| 7 | Riders | Complete |
| 8 | Whole Life | Complete |
| 9 | Annuities | Complete (SPIA payouts added) |
| 10 | Assumption Packs | Complete |
| 11 | Conformance Suite | Complete (env metadata added) |
| 12 | UI Explorer | Complete |
| 13 | PDF Renderer | Complete (template + disclosure support) |
| 14 | Batch & Benchmarks | Complete |
| 15 | Bundles | Complete |
| 16+ | Strategic Phases | Not started |

---

# Phase 0 — Repo foundation and “make it boring”
**Goal:** predictable tooling, deterministic outputs, contribution safety rails.

## 0.1 Tooling + CI
**Deliverables**
- [x] `pyproject.toml` with dependencies and tooling config
- [x] `ruff` (lint/format), `pytest`
- [x] `.pre-commit-config.yaml`
- [x] GitHub Actions workflow: lint + tests

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
- [x] Add versioning module:
  - `CALC_VERSION`
  - `SCHEMA_VERSION`
  - `ROUNDING_POLICY_ID`
- [x] Result metadata includes these values
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
- [x] Decimal serialization policy (recommend: stringify Decimals)
- [x] Sorted JSON keys, stable output formatting
- [x] Shared serializer used by CLI and API

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
- [x] `IllustrationRequest` and `IllustrationResult` Pydantic models
- [x] `Ledger`, `LedgerRow` models with UL + Term optional fields
- [x] Input normalization (Decisions: Decimal parsing, required defaults)

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
- [x] Decimal context
- [x] `quantize_money()` (currency-aware), `quantize_rate()`
- [x] Explicit rounding points guidance (documented in engine.py and money.py)

**Files**
- `opie/core/money.py`

**Tests**
- unit tests for rounding behavior

---

## 1.3 Assumptions loading (COI + surrender schedule)
**Deliverables**
- [x] COI table loader (CSV + JSON)
- [x] Surrender schedule parser (month map + year map expanded to months)
- [x] Scenario models for UL and Term

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
- [x] `ProductHooks` Protocol (premium+loads, charges, DB)
- [x] UL-only hooks (NAR, surrender)
- [x] Product registry mapping `product_code -> hooks`

**Files**
- `opie/products/base.py`
- `opie/products/registry.py`

**Tests**
- registry lookup tests

---

## 1.5 Core engine (scenario runner + monthly loop)
**Deliverables**
- [x] Engine implements normative ordering from spec:
  - AV_bop → premium/load → charges → AV_mid_raw → lapse check → interest → AV_eop → CSV → emit
- [x] Lapse semantics: emit fatal month row, stop
- [x] Scenario runner: run `current` + `guaranteed`

**Files**
- `opie/core/engine.py`
- `opie/core/time.py`

**Tests**
- minimal engine unit tests (no goldens yet)

---

## 1.6 Implement `SimpleUL` product
**Deliverables**
- [x] UL hooks implement:
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
- [x] Term hooks implement:
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
- [x] Invariants checks for UL:
  - AV_eop >= 0
  - CSV <= AV_eop
  - cumulative premium monotone
  - lapse row semantics: interest=0, AV_eop=0, DB=0
- [x] Invariants checks for Term:
  - DB=0 when expired
  - cumulative premium monotone

**Files**
- `opie/core/invariants.py`

**Tests**
- invariants tests with representative ledgers

---

## 1.9 Golden fixtures + golden test harness
**Deliverables**
- [x] Example requests in `examples/`
  - UL stays in force
  - UL lapses mid-projection
  - Term
- [x] Golden outputs for:
  - UL in-force: current + guaranteed
  - UL lapse: current + guaranteed
  - Term: current + guaranteed
- [x] Golden test harness:
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
- [x] Library:
  - `opie.run_illustration()` exported from `opie/__init__.py`
- [x] CLI:
  - `opie illustrate --in --out --format json|csv`
- [x] FastAPI:
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
- [x] Exception classes:
  - `AssumptionError`, `InvariantViolation`, `EngineError`
- [x] Errors include scenario + month `t` + key values

**Files**
- `opie/core/errors.py`
- update engine/assumptions to raise these

**Tests**
- verify error payload content

---

## 2.2 Ledger diff tooling
**Deliverables**
- [x] `opie diff --a ledgerA.json --b ledgerB.json`
  - first month/field difference
  - numeric delta
- [x] scenario-to-scenario diff within one result (`opie diff --within`)

**Files**
- `opie/cli/diff.py`
- `opie/cli/main.py` (subcommand wiring)

**Tests**
- known-diff fixture test

---

## 2.3 Debug trace mode (light)
**Deliverables**
- [x] Optional request flag `debug=true` to emit extra fields:
  - unquantized intermediates (or selected ones)
- [x] Trace mode must not change base outputs unless explicitly enabled

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
- [x] Support `interest_mode`:
  - `nominal_div_12`
  - `effective_monthly`
- [x] Mode recorded in metadata and/or scenario assumptions

**Files**
- `opie/assumptions/models.py`
- `opie/core/engine.py`

**Tests**
- goldens for each mode (at least one example)

---

## 3.2 Grace period semantics (minimal)
**Deliverables**
- [x] `grace_months` config (default 0)
- [x] Lapse only after grace exhausted
- [x] Still emit “fatal month” row where lapse resolves

**Files**
- `opie/core/engine.py`
- `opie/core/types.py`

**Tests**
- grace boundary tests + goldens

---

## 3.3 Charge assessed vs paid (optional but powerful)
**Deliverables**
- [x] Add fields:
  - `charges_assessed`
  - `charges_paid`
  - `charge_shortfall`
- [x] Keep ordering deterministic

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
- [x] Solve modes:
  - keep in force through month N
  - hit target AV at month N
- [x] Deterministic iteration count / tolerance
- [x] Output solver metadata

**Files**
- `opie/core/solve.py`
- `opie/core/types.py`

**Tests**
- solver determinism tests
- golden solve examples

---

## 4.2 Scenario solve strategy options
**Deliverables**
- [x] Config:
  - solve in current, illustrate both
  - solve per scenario
- [x] Explicit output labels

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
- [x] DB option switch
- [x] NAR updated accordingly
- [x] Goldens updated

**Files**
- `opie/products/ul_simple.py`
- `opie/core/types.py`

---

## 5.2 Corridor approximation (optional module)
**Deliverables**
- [x] Optional corridor table by age
- [x] DB uplift to satisfy corridor
- [x] Output fields indicating uplift

**Files**
- `opie/assumptions/tables.py`
- `opie/products/ul_simple.py`

---

# Phase 6 — Withdrawals and loans (v0.4)
**Goal:** path-dependent money moves.

## 6.1 Withdrawals
**Deliverables**
- [x] withdrawal schedule month→amount
- [x] declared ordering
- [x] new ledger fields

**Files**
- `opie/core/types.py`
- `opie/core/engine.py`
- `examples/*`, goldens

---

## 6.2 Loans (basic)
**Deliverables**
- [x] loan balance, loan interest
- [x] repayments schedule
- [x] CSV impacted by loan

**Files**
- `opie/core/types.py`
- `opie/core/engine.py`

---

# Phase 7 — Riders framework (v0.4)
**Goal:** composability.

## 7.1 Rider hook interface + stacking
**Deliverables**
- [x] `RiderHooks` with deterministic ordering
- [x] example rider: simple flat monthly charge rider

**Files**
- `opie/products/riders/base.py`
- `opie/products/riders/examples.py`
- engine wiring

---

# Phase 8 — Whole Life (WL) (v0.5)
**Goal:** prove engine supports a different product family.

## 8.1 Non-par WL (simplified)
**Deliverables**
- [x] WL product with table-driven CV and SV
- [x] monthly ledger conventions declared (step, no interpolation)

**Files**
- `opie/products/wl_nonpar.py`
- assumptions tables as needed

---

# Phase 9 — Annuities starter set (v0.5)
**Goal:** broaden domain coverage.

## 9.1 Deferred fixed annuity (simple)
- [x] accumulation value + surrender charge

## 9.2 SPIA (toy)
- [x] payout factor tables + payment schedule ledger

---

# Phase 10 — Assumption packs + provenance (v0.2–v0.6)
**Goal:** portable assumptions with checksums and licensing clarity.

## 10.1 Assumption pack format v0
**Deliverables**
- [x] `pack.json` manifest:
  - name, version, license, source, checksum
- [x] CLI validate and list pack contents

**Files**
- `opie/assumptions/packs.py`
- `opie/cli/pack.py`

---

# Phase 11 — Conformance suite + cross-engine comparison (v0.7)
**Goal:** OPIE becomes an audit-friendly standard.

## 11.1 Conformance test runner
- [x] canonical cases + expected outputs
- [x] publish results for forks/plugins (env metadata in reports)

## 11.2 Comparison harness
- [x] first-diff reports + max-diff stats

---

# Phase 12 — UI Explorer (v0.6)
**Goal:** a demo that makes people “get it” instantly.
- [x] scenario toggle
- [x] diff view
- [x] lapse highlight
- [x] request builder and export

(Recommended as a separate `opie-ui/` package or sibling repo.)

---

# Phase 13 — PDF renderer (separate package)
**Goal:** formatting only, no math.
- [x] `opie-pdf` consumes `IllustrationResult` JSON
- [x] templates and disclosures per jurisdiction

---

# Phase 14 — Batch mode + performance (v0.7)
**Goal:** run at scale.
- [x] NDJSON input/output
- [x] streaming execution
- [x] assumption context caching
- [x] benchmarks

---

# Phase 15 — Artifact bundles + verification
**Goal:** reproducibility.
- [x] bundle: request + assumptions manifest + result + checksums
- [x] `opie bundle create/verify`

---

# Phase 16 — SPIA Completion (post-v1.0)
**Goal:** finish the payout story.

### Objectives
- Production-quality SPIA implementation
- Multiple annuity forms and period certain options
- Joint life calculations

### Deliverables
- [ ] Mortality table framework (SOA tables, custom tables)
- [ ] Life-only SPIA
- [ ] Life with period certain (5, 10, 15, 20 year)
- [ ] Joint and survivor (50%, 75%, 100% continuation)
- [ ] Refund options (cash refund, installment refund)
- [ ] Modal payment factors (monthly, quarterly, semi-annual, annual)
- [ ] Cost-of-living adjustment (COLA) riders
- [ ] Commutation calculations
- [ ] SPIA golden tests against actuarial standards

### Success criteria
- SPIA payout factors match published SOA calculations
- Joint life calculations validated against industry tools

---

# Phase 17 — Indexed Products
**Goal:** support indexed crediting strategies without full stochastic modeling.

### Objectives
- Support indexed crediting strategies without full stochastic modeling
- Demonstrate IUL and FIA illustration patterns

### Products
- Indexed UL (IUL): point-to-point, monthly average, cap/floor/participation
- Fixed Indexed Annuity (FIA): similar crediting, accumulation focus

### Deliverables
**Index crediting framework**
- [ ] Index strategy abstraction
- [ ] Strategy types: point-to-point, monthly sum, monthly average, performance trigger
- [ ] Cap, floor, participation rate, spread parameters
- [ ] Segment tracking (for multi-year strategies)
- [ ] Index term lengths (1-year, 2-year, etc.)
- [ ] Crediting frequency options

**IUL-specific**
- [ ] Multiple index accounts + fixed account
- [ ] Account allocation tracking
- [ ] Automatic rebalancing rules
- [ ] Bonus crediting with vesting schedules
- [ ] Multiplier/booster strategies
- [ ] Indexed loan crediting

**FIA-specific**
- [ ] Accumulation value mechanics
- [ ] Free withdrawal provisions
- [ ] Market value adjustment (MVA)
- [ ] Guaranteed minimum accumulation benefit (GMAB)
- [ ] Income rider value tracking

**Illustration support**
- [ ] Hypothetical rate illustrations (AG49 lookback concept)
- [ ] Historical index performance loading
- [ ] Backtesting harness
- [ ] Scenario comparison (illustrated vs. 0% vs. max)

### Success criteria
- IUL illustration with S&P 500 point-to-point runs correctly
- Can show impact of different cap/participation combinations
- FIA accumulation matches carrier examples

---

# Phase 18 — Expanded Riders
**Goal:** complete the rider ecosystem.

### Objectives
- Comprehensive rider library covering common market offerings
- Rider interaction rules and stacking validation

### Core life riders
- [ ] Waiver of Premium (WP) — disability-triggered
- [ ] Waiver of Cost of Insurance (WCOI)
- [ ] Accidental Death Benefit (ADB)
- [ ] Guaranteed Insurability Option (GIO)
- [ ] Term rider (on permanent base)
- [ ] Children's term rider
- [ ] Spouse term rider

### Accelerated benefit riders
- [ ] Terminal illness rider
- [ ] Chronic illness rider
- [ ] Critical illness rider
- [ ] Long-term care (LTC) rider — simplified version

### UL-specific riders
- [ ] Overloan protection rider
- [ ] No-lapse guarantee rider (secondary guarantee)
- [ ] Persistency bonus rider
- [ ] Return of premium rider

### Annuity riders (living benefits)
- [ ] Guaranteed Lifetime Withdrawal Benefit (GLWB)
- [ ] Guaranteed Minimum Income Benefit (GMIB)
- [ ] Guaranteed Minimum Withdrawal Benefit (GMWB)
- [ ] Death benefit step-up rider

### Rider framework enhancements
- [ ] Rider eligibility rules engine
- [ ] Rider interaction/conflict detection
- [ ] Rider cost allocation methods
- [ ] Rider-specific disclosure generation
- [ ] Rider comparison tools

### Success criteria
- 20+ riders implemented
- Rider stacking produces correct combined charges
- Living benefit riders track benefit base correctly

---

# Phase 19 — Compliance & Regulation
**Goal:** make it official.

### Objectives
- NAIC Model Regulation compliance for illustrations
- State-specific variation handling
- Disclosure and narrative generation

### NAIC illustration model regulation
- [ ] Basic illustration format requirements
- [ ] Guaranteed vs. non-guaranteed column separation
- [ ] Required numeric summaries (policy years 1, 5, 10, 20, age 65, age 70, maturity)
- [ ] Policy summary page generation
- [ ] Narrative disclosure templates
- [ ] Annual report/in-force illustration format

### AG49 (indexed products)
- [ ] Maximum illustrated rate calculations
- [ ] Benchmark index account requirements
- [ ] AG49-A geometric mean calculations
- [ ] AG49-B fixed bonus limitations
- [ ] Lookback rate calculations (25-year, 10-year)
- [ ] Annual AG49 rate update process

### IRC 7702 (tax qualification)
- [ ] Cash value accumulation test (CVAT)
- [ ] Guideline premium test (GPT)
- [ ] 7-pay test for MEC determination
- [ ] Corridor percentages by age
- [ ] Guideline single premium (GSP)
- [ ] Guideline level premium (GLP)
- [ ] Material change tracking

### State variations
- [ ] State-specific disclosure requirements matrix
- [ ] New York Regulation 60 compliance
- [ ] California-specific requirements
- [ ] Texas-specific requirements
- [ ] State configuration registry
- [ ] Multi-state illustration generation
- [ ] State approval status tracking

### Suitability & best interest
- [ ] Suitability questionnaire data model
- [ ] Best interest recommendation documentation
- [ ] Replacement illustration requirements
- [ ] Comparative illustration format

### Deliverables
- [ ] Compliance rule engine
- [ ] NAIC illustration format output
- [ ] AG49 rate calculator
- [ ] 7702 test calculator
- [ ] State variation configuration
- [ ] Disclosure template system (Jinja2 or similar)
- [ ] Compliance test suite against NAIC examples
- [ ] Compliance validation API endpoint

### Success criteria
- Generate NAIC-compliant illustration PDF for UL
- AG49 illustrated rates match manual calculations
- Can configure for NY vs. CA disclosure differences
- 7702 tests match carrier calculations

---

# Phase 20 — International
**Goal:** global reach.

### Objectives
- Support major international insurance markets
- Localization and regulatory compliance outside US

### Markets (priority order)
**Tier 1: English-speaking**
- [ ] Canada — OSFI requirements, CLHIA guidelines
- [ ] United Kingdom — FCA requirements, Solvency II illustrations
- [ ] Australia — APRA requirements, FSC standards

**Tier 2: Europe**
- [ ] Germany — BaFin requirements
- [ ] France — ACPR requirements
- [ ] Netherlands — DNB requirements
- [ ] EU-wide — IDD disclosure requirements, PRIIPs KID

**Tier 3: Asia-Pacific**
- [ ] Japan — FSA requirements
- [ ] Singapore — MAS requirements
- [ ] Hong Kong — IA requirements

**Tier 4: Emerging markets**
- [ ] India — IRDAI requirements
- [ ] Brazil — SUSEP requirements
- [ ] South Africa — FSCA requirements

### Localization framework
- [x] Multi-currency support (base + reporting)
- [ ] Currency conversion and display
- [ ] Date format localization
- [ ] Number format localization
- [ ] Language/translation framework (i18n)
- [ ] Right-to-left (RTL) support
- [ ] Timezone handling

### International product variations
- [ ] With-profits / participating products (UK style)
- [ ] Unit-linked products (EU/UK)
- [ ] Endowment products
- [ ] Takaful (Islamic insurance) framework

### Regulatory mapping
- [ ] Regulatory requirement database
- [ ] Cross-jurisdiction comparison tools
- [ ] Regulatory update tracking
- [ ] Jurisdiction-specific disclosure templates

### Success criteria
- Full compliance in 3+ non-US jurisdictions
- Multi-language support for 5+ languages
- International product types validated by local actuaries

---

# Phase 21 — Adjacent Domains
**Goal:** expand the footprint.

### Objectives
- Apply OPIE patterns to related insurance domains
- Build bridges to adjacent financial services

### Health insurance
- [ ] Health insurance illustration framework
- [ ] Premium rate-up illustrations
- [ ] Benefit period projections
- [ ] Long-term care standalone products
- [ ] Medicare supplement illustrations
- [ ] ACA plan comparisons

### Disability income
- [ ] DI illustration engine
- [ ] Benefit period and elimination period modeling
- [ ] Residual disability calculations
- [ ] Cost-of-living riders
- [ ] Future increase options

### Property & casualty (stretch)
- [ ] Premium projection framework
- [ ] Multi-year rate projections
- [ ] Deductible analysis
- [ ] Coverage comparison tools

### Retirement planning integration
- [ ] Retirement income projections
- [ ] Social Security optimization
- [ ] Pension vs. lump sum analysis
- [ ] Tax-efficient withdrawal sequencing
- [ ] Monte Carlo retirement scenarios

### Financial planning bridges
- [ ] Financial planning software integrations (eMoney, MoneyGuidePro, RightCapital)
- [ ] CRM integrations (Salesforce, Redtail)
- [ ] Portfolio management integrations
- [ ] Estate planning integration

### Success criteria
- Health and DI illustration engines production-ready
- 3+ financial planning integrations live
- Retirement planning module validated by CFPs

---

# Phase 22 — Industry Standard
**Goal:** change the industry.

### Objectives
- OPIE as the expected foundation for illustration systems
- Regulatory recognition and potential adoption
- Academic and research integration

### Regulatory engagement
- [ ] NAIC working group participation
- [ ] ACLI task force engagement
- [ ] SOA research partnership
- [ ] AAA practice council collaboration
- [ ] State insurance department outreach program
- [ ] Comment letters on illustration regulation updates
- [ ] OPIE as reference implementation in regulatory guidance
- [ ] Regulatory sandbox participation

### Standards development
- [ ] ACORD integration and mapping
- [ ] Industry data standard contributions
- [ ] Open illustration format proposal
- [ ] API standardization initiative
- [ ] Cross-vendor interoperability specs

### Academic integration
- [ ] University curriculum partnerships
- [ ] Actuarial exam preparation materials
- [ ] Research paper: Open Standards for Insurance Illustrations
- [ ] Academic journal publications
- [ ] Student competition sponsorship
- [ ] PhD research collaborations

### Innovation & research
- [ ] Stochastic illustration framework
- [ ] Monte Carlo scenario generation
- [ ] Machine learning for assumption setting
- [ ] Behavioral modeling (lapse, utilization)
- [ ] Climate risk integration
- [ ] Real-time illustration APIs
- [ ] Embedded insurance illustration widgets
- [ ] Blockchain attestation (experimental)

### Industry adoption metrics
- [ ] Carrier adoption tracking
- [ ] Vendor integration tracking
- [ ] Market share estimation
- [ ] Industry survey and benchmarking
- [ ] Case study documentation

### Success criteria
- NAIC references OPIE in guidance documents
- 10+ carriers using OPIE in production
- SOA publishes OPIE-based research
- OPIE taught in 5+ university actuarial programs
- Industry standard proposal submitted to ACORD

---

# Cross-cutting concerns (ongoing)

## Documentation
- [x] README and quick start
- [ ] API reference (auto-generated from OpenAPI)
- [ ] Product implementation guide
- [ ] Assumption specification guide
- [ ] Calculation methodology whitepaper
- [ ] Contributor guide
- [ ] Architecture decision records (ADRs)
- [ ] Changelog and migration guides
- [ ] Video tutorials
- [ ] Interactive examples (Jupyter notebooks)

## Security
- [ ] Dependency vulnerability scanning (Dependabot, Snyk)
- [ ] Security policy and disclosure process
- [ ] OWASP compliance review
- [ ] Penetration testing (annual)
- [ ] SOC 2 Type II (for hosted offering)
- [ ] Input validation hardening
- [ ] Rate limiting for API
- [ ] Secrets management patterns
- [ ] Data encryption at rest and in transit

## Performance
- [ ] Continuous benchmark suite
- [ ] Profiling and optimization cycles
- [ ] Memory usage optimization
- [ ] Startup time optimization
- [ ] Caching strategy refinement
- [ ] Lazy loading for large assumption sets
- [ ] Database query optimization
- [ ] CDN for static assets

## Quality
- [ ] Code coverage targets (>90%)
- [ ] Mutation testing
- [ ] Fuzz testing for parsers
- [ ] Load testing
- [ ] Chaos engineering (for hosted)
- [ ] Accessibility compliance (WCAG for UI)

---

## Appendix: Product coverage matrix

| Product | Phase | Status | Complexity |
| --- | --- | --- | --- |
| Level Term | 1 | Done | Low |
| Simple UL | 1 | Done | Medium |
| Non-Par Whole Life | 8 | Done | Medium |
| Deferred Fixed Annuity | 9 | Done | Medium |
| SPIA | 16 | Partial | Medium |
| Indexed UL | 17 | Planned | High |
| Fixed Indexed Annuity | 17 | Planned | High |
| Variable UL | Future | Planned | Very High |
| Variable Annuity | Future | Planned | Very High |
| Participating WL | Future | Planned | High |

---

## Appendix: Rider coverage matrix

| Rider | Phase | Status |
| --- | --- | --- |
| Basic rider framework | 7 | Done |
| Waiver of Premium | 18 | Planned |
| Accidental Death Benefit | 18 | Planned |
| Term Rider | 18 | Planned |
| Guaranteed Insurability | 18 | Planned |
| LTC Rider | 18 | Planned |
| Overloan Protection | 18 | Planned |
| No-Lapse Guarantee | 18 | Planned |
| GLWB | 18 | Planned |
| GMIB | 18 | Planned |

---

## Appendix: Regulatory coverage matrix

| Regulation | Jurisdiction | Phase | Status |
| --- | --- | --- | --- |
| NAIC Model Illustration Reg | US (Model) | 19 | Planned |
| AG49/49-A/49-B | US (NAIC) | 19 | Planned |
| IRC 7702 | US (Federal) | 19 | Planned |
| Reg 60 | New York | 19 | Planned |
| FCA Requirements | UK | 20 | Planned |
| Solvency II | EU | 20 | Planned |
| OSFI Guidelines | Canada | 20 | Planned |
| IDD | EU | 20 | Planned |

---

## Appendix: Integration targets

| System Type | Examples | Phase | Status |
| --- | --- | --- | --- |
| Financial Planning | eMoney, MoneyGuidePro | 21 | Planned |

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
