# OPIE Strategic Roadmap
**Open Policy Illustration Engine**

A multi-year vision for building the open-source standard for life insurance policy illustrations.

---

## Vision

OPIE becomes the reference implementation for life insurance illustrations—the way SQLite is for embedded databases or OpenSSL is for cryptography. Carriers, vendors, regulators, and educators all use OPIE as a shared foundation, reducing duplicated effort across the industry while improving transparency and auditability.

---

## Status (as of 2026-01-08)
- **Completed**: Phase 1 MVP engine; Phase 3 UL completeness; baseline batch/pack/bundle tooling; conformance runner + comparison tools; UI Explorer; minimal PDF renderer.
- **Partially complete**: Phase 0 foundations (mypy/type-check missing), Phase 2 debugging (scenario-to-scenario diff missing), Phase 4 product breadth (WL + annuities simplified; SPIA payout/annuitization pending), Phase 6 riders (framework only), Phase 7 compliance (no NAIC/AG49), Phase 8 enterprise features (no parallelism/governance), Phase 9 platform & ecosystem (marketplace/certification pending).
- **Not started**: Phase 5 indexed products; Phase 10 industry standard adoption.
---

## Milestone Summary

| Phase | Timeline | Theme | Key Deliverable |
|-------|----------|-------|-----------------|
| **0** | Month 1 | Foundation | Reproducible builds, deterministic outputs |
| **1** | Months 2-3 | MVP | Simple UL + Term, CLI/API, golden tests |
| **2** | Months 4-5 | Developer Experience | Debug tooling, error taxonomy, diff utilities |
| **3** | Months 6-8 | UL Completeness | Premium solve, DB options, loans/withdrawals |
| **4** | Months 9-12 | Product Breadth | Whole Life, SPIA, deferred annuity |
| **5** | Year 2 Q1-Q2 | Indexed Products | IUL, FIA with cap/floor/participation |
| **6** | Year 2 Q3-Q4 | Riders & Modularity | Rider framework, common riders, plugin architecture |
| **7** | Year 3 Q1-Q2 | Compliance & Regulation | NAIC illustration regs, state variations, disclosure generation |
| **8** | Year 3 Q3-Q4 | Enterprise Features | Multi-tenant, batch processing, assumption governance |
| **9** | Year 4 | Platform & Ecosystem | Marketplace, certification, commercial extensions |
| **10** | Year 5+ | Industry Standard | Regulatory adoption, international expansion, adjacent domains |

---

## Phase 0 — Foundation
**Timeline:** Month 1
**Theme:** Make it boring

### Objectives
- Deterministic, reproducible outputs (same inputs → same outputs, always)
- CI/CD pipeline with lint, type-check, test
- Versioning strategy for calculations, schemas, and rounding policies
- Decimal arithmetic with explicit rounding points

### Deliverables
- [x] Project scaffolding (pyproject.toml, ruff, pytest)
- [ ] mypy configuration
- [x] Pre-commit hooks and GitHub Actions
- [x] `CALC_VERSION`, `SCHEMA_VERSION`, `ROUNDING_POLICY_ID` module
- [x] Deterministic JSON serialization (Decimals as strings, sorted keys)
- [x] Time/month indexing utilities
- [x] Custom exception hierarchy

### Success Criteria
- `pytest` passes on macOS, Linux, Windows
- Two runs of the same code produce byte-identical output
- New contributors can `make dev && make test` in under 2 minutes

---

## Phase 1 — MVP Engine
**Timeline:** Months 2-3
**Theme:** Ship something real

### Objectives
- Demonstrate the core engine pattern with two products
- Establish the product-as-configuration architecture
- Lock down outputs with golden file tests

### Products
- **Simple UL**: Account value, COI, loads, surrender charges, DB Option 1
- **Level Term**: Premium schedule, term expiry, no cash value

### Deliverables
- [x] Pydantic request/response models
- [x] Money and rounding module
- [x] Assumptions loading (COI tables, surrender schedules)
- [x] Product hook interface and registry
- [x] Core engine (monthly loop with normative ordering)
- [x] Simple UL implementation
- [x] Level Term implementation
- [x] Invariants module (AV ≥ 0, CSV ≤ AV, etc.)
- [x] Golden file test harness + initial fixtures
- [x] Library API: `opie.run_illustration()`
- [x] CLI: `opie illustrate --in request.json --out ledger.json`
- [x] FastAPI: `POST /v1/illustrations`
- [x] README with examples

### Success Criteria
- Can illustrate a UL policy from age 35 to 85 with monthly granularity
- Golden tests catch any calculation drift
- API returns OpenAPI schema that validates

---

## Phase 2 — Developer Experience
**Timeline:** Months 4-5
**Theme:** Make debugging trivial

### Objectives
- When two ledgers differ, pinpoint exactly where and why
- Structured errors that include month, scenario, and key values
- Optional debug trace for intermediate calculations

### Deliverables
- [x] Error taxonomy: `AssumptionError`, `EngineError`, `InvariantViolation`
- [x] Errors include context (scenario, month t, field values)
- [x] `opie diff` command: first divergence, numeric delta, field-by-field
- [x] Debug trace mode (debug fields emitted when requested)
- [ ] Scenario-to-scenario diff within a single result
- [x] Improved validation error messages

### Success Criteria
- A penny difference in month 47 produces a clear error message pointing to that month
- `opie diff a.json b.json` outputs actionable diagnostics

---

## Phase 3 — UL Completeness
**Timeline:** Months 6-8
**Theme:** Real-world UL features

### Objectives
- Premium solve ("what premium keeps this in force to age 90?")
- Death benefit options
- Policy loans and withdrawals
- Grace period and lapse mechanics

### Deliverables
- [x] Interest conversion modes (nominal vs. effective)
- [x] Grace period semantics (configurable months before lapse)
- [x] Charges assessed vs. charges paid tracking
- [x] Premium solve framework (binary search, deterministic)
- [x] Solve modes: keep in force through month N, target AV at month N
- [x] Solve strategies: solve in current vs. solve per scenario
- [x] DB Option 2 (increasing: Face + AV)
- [x] Corridor approximation (optional 7702 proxy)
- [x] Withdrawals with ordering rules
- [x] Policy loans: loan balance, loan interest, repayments
- [x] CSV impact from loans

### Success Criteria
- Can solve for level premium to keep UL in force to age 100 under guaranteed assumptions
- Loan mechanics match carrier illustrations for test cases

---

## Phase 4 — Product Breadth
**Timeline:** Months 9-12
**Theme:** Beyond UL

### Objectives
- Prove the engine architecture supports fundamentally different products
- Expand into accumulation and payout products

### Products
- **Non-Par Whole Life**: Table-driven CV/SV, premium modes, paid-up values
- **Deferred Fixed Annuity**: Accumulation value, surrender schedule, annuitization options
- **Single Premium Immediate Annuity (SPIA)**: Payout factors, payment schedule, period certain

### Deliverables
- [x] Whole Life product implementation (simplified, table-driven)
- [ ] WL-specific ledger fields (paid-up additions placeholder)
- [x] Deferred annuity accumulation engine (basic)
- [ ] Annuitization value calculation
- [ ] SPIA payout ledger (payout schedule not yet implemented; current SPIA is accumulation-only)
- [ ] Mortality table loading (for SPIA factors)
- [x] Product comparison harness (compare tooling)

### Success Criteria
- WL illustration matches sample carrier output for basic case
- SPIA shows monthly payout schedule for life with 10-year certain

---

## Phase 5 — Indexed Products
**Timeline:** Year 2, Q1-Q2
**Theme:** The hard stuff

### Objectives
- Support indexed crediting strategies without full stochastic modeling
- Demonstrate IUL and FIA illustration patterns

### Products
- **Indexed UL (IUL)**: Point-to-point, monthly average, cap/floor/participation
- **Fixed Indexed Annuity (FIA)**: Similar crediting, accumulation focus

### Deliverables
- [ ] Index crediting strategy framework
- [ ] Strategy types: point-to-point, monthly sum, monthly average
- [ ] Cap, floor, participation rate, spread parameters
- [ ] Segment tracking (for multi-year strategies)
- [ ] Hypothetical rate illustrations (AG49 concept)
- [ ] Index account + fixed account allocation
- [ ] Bonus crediting (with vesting schedules)
- [ ] IUL product implementation
- [ ] FIA product implementation
- [ ] Backtesting harness (historical index returns)

### Success Criteria
- IUL illustration with S&P 500 point-to-point strategy runs correctly
- Can show impact of different cap/participation combinations

### Regulatory Note
AG49 (and AG49-A, AG49-B) compliance is Phase 7. This phase builds the mechanics; compliance comes later.

---

## Phase 6 — Riders & Modularity
**Timeline:** Year 2, Q3-Q4
**Theme:** Composability

### Objectives
- Riders as composable add-ons, not product forks
- Plugin architecture for external contributions
- Common riders that work across products

### Rider Framework
- Rider hook interface with deterministic ordering
- Charge injection, benefit modification, ledger field additions
- Rider-specific assumptions and tables

### Common Riders
- [ ] Waiver of Premium (WP)
- [ ] Accidental Death Benefit (ADB)
- [ ] Term rider (on permanent base)
- [ ] Guaranteed Insurability Option (GIO)
- [ ] Long-Term Care rider (LTC) — simplified
- [ ] Return of Premium rider
- [ ] Overloan Protection rider

### Plugin Architecture
- [ ] Plugin discovery and registration
- [ ] Versioned plugin API
- [ ] Plugin isolation (plugins can't break core)
- [ ] Plugin testing harness
- [ ] Example plugins repository

### Deliverables
- [x] `RiderHooks` protocol
- [x] Rider registry and stacking rules
- [ ] 7+ common rider implementations
- [ ] Plugin loader and API
- [ ] Plugin development guide
- [ ] `opie-contrib` repository for community plugins

### Success Criteria
- Can add WP rider to UL without modifying core engine
- Third-party plugin loads and runs without core changes

---

## Phase 7 — Compliance & Regulation
**Timeline:** Year 3, Q1-Q2
**Theme:** Make it official

### Objectives
- NAIC Model Regulation compliance for illustrations
- State-specific variation handling
- Disclosure and narrative generation

### NAIC Illustration Model Regulation
- [ ] Basic illustration format requirements
- [ ] Guaranteed vs. non-guaranteed column separation
- [ ] Required numeric summaries
- [ ] Policy summary page generation
- [ ] Narrative disclosure templates

### AG49 (Indexed Products)
- [ ] Maximum illustrated rate calculations
- [ ] Benchmark index account requirements
- [ ] AG49-A and AG49-B updates
- [ ] Lookback rate calculations

### State Variations
- [ ] State-specific disclosure requirements
- [ ] State-specific product rules
- [ ] State configuration registry
- [ ] Multi-state illustration generation

### Deliverables
- [ ] Compliance rule engine
- [ ] NAIC illustration format output
- [ ] AG49 rate calculator
- [ ] State variation configuration
- [ ] Disclosure template system
- [x] PDF generation (minimal `opie-pdf` prototype)
- [ ] Compliance test suite against NAIC examples

### Success Criteria
- Generate NAIC-compliant illustration PDF for UL
- AG49 illustrated rates match manual calculations
- Can configure for NY vs. CA disclosure differences

---

## Phase 8 — Enterprise Features
**Timeline:** Year 3, Q3-Q4
**Theme:** Scale and governance

### Objectives
- Support carrier-scale workloads
- Assumption governance and audit trails
- Multi-tenant deployment patterns

### Batch Processing
- [x] NDJSON streaming input/output
- [ ] Parallel execution (process pool)
- [ ] Progress reporting and resumption
- [ ] Memory-efficient large batch handling
- [ ] Benchmark suite (illustrations per second)
- [x] Basic benchmark script

### Assumption Governance
- [x] Assumption pack format with manifests
- [x] Pack versioning and checksums
- [ ] Pack signing (optional)
- [ ] Assumption lineage tracking
- [ ] Effective dating for assumption changes
- [ ] Assumption comparison tools

### Audit & Reproducibility
- [x] Artifact bundles (request + assumptions + result + checksums)
- [x] Bundle verification tool
- [ ] Calculation audit log
- [ ] Determinism certification tests

### Multi-Tenant
- [ ] Tenant-isolated assumption stores
- [ ] Tenant-specific product configurations
- [ ] Rate limiting and quotas
- [ ] Usage metering hooks

### Deliverables
- [x] `opie batch` command
- [x] Assumption pack tooling
- [x] Artifact bundle format and tools
- [ ] Multi-tenant API patterns
- [ ] Performance benchmarks and optimization guide
- [ ] Kubernetes deployment examples

### Success Criteria
- Process 10,000 illustrations per minute on commodity hardware
- Artifact bundle from 2024 reproduces identical output in 2027

---

## Phase 9 — Platform & Ecosystem
**Timeline:** Year 4
**Theme:** Build the community

### Objectives
- Sustainable open-source ecosystem
- Commercial extensions without fragmenting the core
- Certification and conformance programs

### Conformance Suite
- [x] Canonical test cases with expected outputs
- [x] Conformance test runner
- [ ] Conformance badge for passing implementations
- [x] Cross-engine comparison tools
- [ ] Public conformance results dashboard

### Plugin Marketplace
- [ ] Plugin registry and discovery
- [ ] Plugin quality tiers (community, verified, certified)
- [ ] Plugin dependency management
- [ ] Commercial plugin licensing support

### Certification Program
- [ ] OPIE Certified Developer curriculum
- [ ] OPIE Certified Implementation criteria
- [ ] Certification exam and badge
- [ ] Certified implementation directory

### Commercial Ecosystem
- [ ] Dual licensing strategy (Apache 2.0 + commercial)
- [ ] Enterprise support tier definition
- [ ] Partner program for vendors
- [ ] Hosted OPIE service (optional SaaS offering)

### UI & Tools
- [x] OPIE Explorer (web-based illustration viewer, minimal)
- [ ] Assumption editor UI
- [ ] Product configurator UI
- [x] Scenario comparison visualization (basic diff view)
- [ ] Embeddable illustration widget

### Deliverables
- [ ] Conformance suite v1.0
- [ ] Plugin marketplace infrastructure
- [ ] Certification program materials
- [x] OPIE Explorer web application (minimal)
- [ ] Partner onboarding documentation

### Success Criteria
- 5+ third-party plugins in marketplace
- 3+ carriers using OPIE in production
- 100+ certified developers

---

## Phase 10 — Industry Standard
**Timeline:** Year 5+
**Theme:** Change the industry

### Objectives
- OPIE as the expected foundation for illustration systems
- Regulatory recognition and potential adoption
- International expansion

### Regulatory Engagement
- [ ] NAIC working group participation
- [ ] ACLI coordination
- [ ] State insurance department outreach
- [ ] Comment letters on illustration regulation updates
- [ ] OPIE as reference implementation in regulatory guidance

### International Expansion
- [ ] UK (Solvency II illustrations)
- [ ] Canada (OSFI requirements)
- [ ] Australia (APRA requirements)
- [ ] EU (IDD disclosure requirements)
- [ ] Localization framework (currency, language, date formats)

### Adjacent Domains
- [ ] Health insurance illustrations
- [ ] Disability income illustrations
- [ ] Annuity income projections
- [ ] Retirement planning integrations
- [ ] P&C policy projections (stretch)

### Research & Innovation
- [ ] Stochastic illustration framework
- [ ] Monte Carlo scenario generation
- [ ] Machine learning for assumption setting
- [ ] Real-time illustration APIs
- [ ] Blockchain-based illustration attestation (experimental)

### Deliverables
- [ ] International product modules
- [ ] Regulatory engagement documentation
- [ ] Adjacent domain specifications
- [ ] Research paper: "Open Standards for Insurance Illustrations"
- [ ] Academic partnerships

### Success Criteria
- NAIC references OPIE in guidance
- 2+ international jurisdictions supported
- Academic citations of OPIE in actuarial literature

---

## Cross-Cutting Concerns

### Documentation (Ongoing)
- [x] README and quick start
- [x] Code map
- [ ] API reference (auto-generated)
- [ ] Product implementation guide
- [ ] Assumption specification guide
- [x] Calculation methodology documentation
- [ ] Contributor guide
- [ ] Architecture decision records (ADRs)
- [ ] Changelog and migration guides

### Security (Ongoing)
- [ ] Dependency vulnerability scanning
- [ ] Security policy and disclosure process
- [ ] Input validation hardening
- [ ] Rate limiting for API
- [ ] Secrets management patterns

### Performance (Ongoing)
- [ ] Benchmark suite
- [x] Basic benchmark script
- [ ] Profiling and optimization
- [ ] Memory usage optimization
- [ ] Caching strategies
- [ ] Lazy loading for large assumption sets

### Community (Ongoing)
- [ ] Code of conduct
- [ ] Contributing guidelines
- [ ] Issue and PR templates
- [ ] Discussion forums
- [ ] Regular release cadence
- [ ] Community calls / office hours

---

## Appendix: Product Coverage Matrix

| Product | Phase | Complexity | Notes |
|---------|-------|------------|-------|
| Level Term | 1 | Low | Baseline product |
| Simple UL | 1 | Medium | Core engine demo |
| Non-Par Whole Life | 4 | Medium | Table-driven |
| Deferred Fixed Annuity | 4 | Medium | Accumulation |
| SPIA | 4 | Low | Toy accumulation only; payout schedule TBD |
| Indexed UL | 5 | High | Multiple strategies |
| Fixed Indexed Annuity | 5 | High | Similar to IUL |
| Variable UL | Future | Very High | Separate accounts, fund selection |
| Variable Annuity | Future | Very High | Similar to VUL |
| Participating WL | Future | High | Dividends, paid-up additions |
| GLWB/GMIB Riders | Future | Very High | Living benefit guarantees |

---

## Appendix: Assumption Types

| Assumption | Phase | Format | Notes |
|------------|-------|--------|-------|
| COI Table | 1 | JSON/CSV | By age, gender, class |
| Surrender Schedule | 1 | JSON | By policy year |
| Crediting Rates | 1 | Inline | Current and guaranteed |
| Loads/Fees | 1 | Inline | Premium load, policy fee, admin fee |
| Mortality Table | 4 | JSON/CSV | For SPIA, VUL |
| Index Parameters | 5 | JSON | Cap, floor, participation, spread |
| Dividend Scale | Future | JSON | For par WL |
| Fund Returns | Future | JSON | For VUL/VA |
| Lapse Rates | Future | JSON | For persistency modeling |

---

## Appendix: Regulatory References

| Regulation | Jurisdiction | Phase | Relevance |
|------------|--------------|-------|-----------|
| NAIC Model Illustration Reg | US (Model) | 7 | Core compliance |
| AG49 | US (NAIC) | 7 | IUL illustrations |
| AG49-A | US (NAIC) | 7 | IUL updates |
| AG49-B | US (NAIC) | 7 | IUL benchmark |
| Reg 60 (NY) | New York | 7 | State-specific |
| IRC §7702 | US (Federal) | 3 | Corridor/guideline |
| Solvency II | EU/UK | 10 | International |
| OSFI Guidelines | Canada | 10 | International |

---

## Appendix: Integration Targets

| System | Phase | Integration Type |
|--------|-------|------------------|
| Policy Admin Systems | 8 | API consumer |
| CRM/Distribution | 8 | Embedded widget |
| E-App Platforms | 8 | API + PDF |
| Compliance Systems | 7 | Batch export |
| Data Warehouses | 8 | Batch export |
| Actuarial Models | 9 | Assumption sync |
| Financial Planning Tools | 10 | API |
