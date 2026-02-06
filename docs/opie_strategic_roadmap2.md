# OPIE Strategic Roadmap
**Open Policy Illustration Engine**

A multi-year vision for building the open-source standard for life insurance policy illustrations.

> NOTE: This strategic roadmap has been consolidated into `docs/opie_roadmap.md`.
> This file is retained for historical reference.

---

## Vision

OPIE becomes the reference implementation for life insurance illustrations—the way SQLite is for embedded databases or OpenSSL is for cryptography. Carriers, vendors, regulators, and educators all use OPIE as a shared foundation, reducing duplicated effort across the industry while improving transparency and auditability.

---

## Status Overview

### ✅ Completed

| Phase | Theme | Status |
|-------|-------|--------|
| 0 | Foundation | ✅ Complete |
| 1 | MVP Engine | ✅ Complete |
| 2 | Developer Experience | ✅ Complete |
| 3 | UL Realism | ✅ Complete |
| 4 | Premium Solve | ✅ Complete |
| 5 | DB Options & Corridor | ✅ Complete |
| 6 | Withdrawals & Loans | ✅ Complete |
| 7 | Riders | ✅ Complete |
| 8 | Whole Life | ✅ Complete |
| 9 | Annuities | ⚠️ Partial (SPIA toy only) |
| 10 | Assumption Packs | ✅ Complete |
| 11 | Conformance Suite | ✅ Complete |
| 12 | UI Explorer | ✅ Complete |
| 13 | PDF Renderer | ✅ Complete |
| 14 | Batch & Benchmarks | ✅ Complete |
| 15 | Bundles | ✅ Complete |

### 🔲 Remaining

| Phase | Theme | Status |
|-------|-------|--------|
| 16 | SPIA Completion | 🔲 Not started |
| 17 | Indexed Products | 🔲 Not started |
| 18 | Expanded Riders | 🔲 Not started |
| 19 | Compliance & Regulation | 🔲 Not started |
| 20 | International | 🔲 Not started |
| 21 | Adjacent Domains | 🔲 Not started |
| 22 | Industry Standard | 🔲 Not started |

---

## Completed Phases (Reference)

<details>
<summary>Phase 0 — Foundation ✅</summary>

- Deterministic, reproducible outputs
- CI/CD pipeline (lint, type-check, test)
- Versioning (`CALC_VERSION`, `SCHEMA_VERSION`, `ROUNDING_POLICY_ID`)
- Decimal arithmetic with explicit rounding points
- Deterministic JSON serialization

</details>

<details>
<summary>Phase 1 — MVP Engine ✅</summary>

- Pydantic request/response models
- Money and rounding module
- Assumptions loading (COI tables, surrender schedules)
- Product hook interface and registry
- Core engine (monthly loop with normative ordering)
- Simple UL implementation
- Level Term implementation
- Invariants module
- Golden file test harness
- Library API, CLI, FastAPI

</details>

<details>
<summary>Phase 2 — Developer Experience ✅</summary>

- Error taxonomy (`AssumptionError`, `EngineError`, `InvariantViolation`)
- `opie diff` command
- Debug trace mode

</details>

<details>
<summary>Phase 3 — UL Realism ✅</summary>

- Interest conversion modes (nominal vs. effective)
- Grace period semantics
- Charges assessed vs. charges paid tracking

</details>

<details>
<summary>Phase 4 — Premium Solve ✅</summary>

- Solve framework (binary search, deterministic)
- Solve modes: keep in force, target AV
- Solve strategies: current vs. per-scenario

</details>

<details>
<summary>Phase 5 — DB Options & Corridor ✅</summary>

- DB Option 2 (increasing: Face + AV)
- Corridor approximation (7702 proxy)

</details>

<details>
<summary>Phase 6 — Withdrawals & Loans ✅</summary>

- Withdrawals with ordering rules
- Policy loans: balance, interest, repayments
- CSV impact from loans

</details>

<details>
<summary>Phase 7 — Riders ✅</summary>

- Rider hook interface
- Rider registry and stacking
- Initial rider implementations

</details>

<details>
<summary>Phase 8 — Whole Life ✅</summary>

- Non-Par WL with table-driven CV/SV
- WL-specific ledger fields

</details>

<details>
<summary>Phase 9 — Annuities ⚠️ Partial</summary>

- ✅ Deferred fixed annuity
- ⚠️ SPIA (toy implementation only)

</details>

<details>
<summary>Phase 10 — Assumption Packs ✅</summary>

- Pack format with manifests
- Pack versioning and checksums
- CLI tooling

</details>

<details>
<summary>Phase 11 — Conformance Suite ✅</summary>

- Canonical test cases
- Conformance runner
- Cross-engine comparison

</details>

<details>
<summary>Phase 12 — UI Explorer ✅</summary>

- Web-based illustration viewer

</details>

<details>
<summary>Phase 13 — PDF Renderer ✅</summary>

- PDF generation from IllustrationResult

</details>

<details>
<summary>Phase 14 — Batch & Benchmarks ✅</summary>

- Batch processing
- Performance benchmarks

</details>

<details>
<summary>Phase 15 — Bundles ✅</summary>

- Artifact bundles (request + assumptions + result + checksums)
- Bundle verification

</details>

---

## Phase 16 — SPIA Completion
**Theme:** Finish the payout story

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

### Success Criteria
- SPIA payout factors match published SOA calculations
- Joint life calculations validated against industry tools

---

## Phase 17 — Indexed Products
**Theme:** The hard stuff

### Objectives
- Support indexed crediting strategies without full stochastic modeling
- Demonstrate IUL and FIA illustration patterns

### Products
- **Indexed UL (IUL)**: Point-to-point, monthly average, cap/floor/participation
- **Fixed Indexed Annuity (FIA)**: Similar crediting, accumulation focus

### Deliverables

#### Index Crediting Framework
- [ ] Index strategy abstraction
- [ ] Strategy types: point-to-point, monthly sum, monthly average, performance trigger
- [ ] Cap, floor, participation rate, spread parameters
- [ ] Segment tracking (for multi-year strategies)
- [ ] Index term lengths (1-year, 2-year, etc.)
- [ ] Crediting frequency options

#### IUL-Specific
- [ ] Multiple index accounts + fixed account
- [ ] Account allocation tracking
- [ ] Automatic rebalancing rules
- [ ] Bonus crediting with vesting schedules
- [ ] Multiplier/booster strategies
- [ ] Indexed loan crediting

#### FIA-Specific
- [ ] Accumulation value mechanics
- [ ] Free withdrawal provisions
- [ ] Market value adjustment (MVA)
- [ ] Guaranteed minimum accumulation benefit (GMAB)
- [ ] Income rider value tracking

#### Illustration Support
- [ ] Hypothetical rate illustrations (AG49 lookback concept)
- [ ] Historical index performance loading
- [ ] Backtesting harness
- [ ] Scenario comparison (illustrated vs. 0% vs. max)

### Success Criteria
- IUL illustration with S&P 500 point-to-point runs correctly
- Can show impact of different cap/participation combinations
- FIA accumulation matches carrier examples

---

## Phase 18 — Expanded Riders
**Theme:** Complete the rider ecosystem

### Objectives
- Comprehensive rider library covering common market offerings
- Rider interaction rules and stacking validation

### Core Life Riders
- [ ] Waiver of Premium (WP) — disability-triggered
- [ ] Waiver of Cost of Insurance (WCOI)
- [ ] Accidental Death Benefit (ADB)
- [ ] Guaranteed Insurability Option (GIO)
- [ ] Term rider (on permanent base)
- [ ] Children's term rider
- [ ] Spouse term rider

### Accelerated Benefit Riders
- [ ] Terminal illness rider
- [ ] Chronic illness rider
- [ ] Critical illness rider
- [ ] Long-term care (LTC) rider — simplified version

### UL-Specific Riders
- [ ] Overloan protection rider
- [ ] No-lapse guarantee rider (secondary guarantee)
- [ ] Persistency bonus rider
- [ ] Return of premium rider

### Annuity Riders (Living Benefits)
- [ ] Guaranteed Lifetime Withdrawal Benefit (GLWB)
- [ ] Guaranteed Minimum Income Benefit (GMIB)
- [ ] Guaranteed Minimum Withdrawal Benefit (GMWB)
- [ ] Death benefit step-up rider

### Rider Framework Enhancements
- [ ] Rider eligibility rules engine
- [ ] Rider interaction/conflict detection
- [ ] Rider cost allocation methods
- [ ] Rider-specific disclosure generation
- [ ] Rider comparison tools

### Success Criteria
- 20+ riders implemented
- Rider stacking produces correct combined charges
- Living benefit riders track benefit base correctly

---

## Phase 19 — Compliance & Regulation
**Theme:** Make it official

### Objectives
- NAIC Model Regulation compliance for illustrations
- State-specific variation handling
- Disclosure and narrative generation

### NAIC Illustration Model Regulation
- [ ] Basic illustration format requirements
- [ ] Guaranteed vs. non-guaranteed column separation
- [ ] Required numeric summaries (policy years 1, 5, 10, 20, age 65, age 70, maturity)
- [ ] Policy summary page generation
- [ ] Narrative disclosure templates
- [ ] Annual report/in-force illustration format

### AG49 (Indexed Products)
- [ ] Maximum illustrated rate calculations
- [ ] Benchmark index account requirements
- [ ] AG49-A geometric mean calculations
- [ ] AG49-B fixed bonus limitations
- [ ] Lookback rate calculations (25-year, 10-year)
- [ ] Annual AG49 rate update process

### IRC §7702 (Tax Qualification)
- [ ] Cash value accumulation test (CVAT)
- [ ] Guideline premium test (GPT)
- [ ] 7-pay test for MEC determination
- [ ] Corridor percentages by age
- [ ] Guideline single premium (GSP)
- [ ] Guideline level premium (GLP)
- [ ] Material change tracking

### State Variations
- [ ] State-specific disclosure requirements matrix
- [ ] New York Regulation 60 compliance
- [ ] California-specific requirements
- [ ] Texas-specific requirements
- [ ] State configuration registry
- [ ] Multi-state illustration generation
- [ ] State approval status tracking

### Suitability & Best Interest
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

### Success Criteria
- Generate NAIC-compliant illustration PDF for UL
- AG49 illustrated rates match manual calculations
- Can configure for NY vs. CA disclosure differences
- 7702 tests match carrier calculations

---

## Phase 20 — International
**Theme:** Global reach

### Objectives
- Support major international insurance markets
- Localization and regulatory compliance outside US

### Markets (Priority Order)

#### Tier 1: English-Speaking
- [ ] **Canada** — OSFI requirements, CLHIA guidelines
- [ ] **United Kingdom** — FCA requirements, Solvency II illustrations
- [ ] **Australia** — APRA requirements, FSC standards

#### Tier 2: Europe
- [ ] **Germany** — BaFin requirements
- [ ] **France** — ACPR requirements
- [ ] **Netherlands** — DNB requirements
- [ ] **EU-wide** — IDD disclosure requirements, PRIIPs KID

#### Tier 3: Asia-Pacific
- [ ] **Japan** — FSA requirements
- [ ] **Singapore** — MAS requirements
- [ ] **Hong Kong** — IA requirements

#### Tier 4: Emerging Markets
- [ ] **India** — IRDAI requirements
- [ ] **Brazil** — SUSEP requirements
- [ ] **South Africa** — FSCA requirements

### Localization Framework
- [ ] Multi-currency support
- [ ] Currency conversion and display
- [ ] Date format localization
- [ ] Number format localization
- [ ] Language/translation framework (i18n)
- [ ] Right-to-left (RTL) support
- [ ] Timezone handling

### International Product Variations
- [ ] With-profits / participating products (UK style)
- [ ] Unit-linked products (EU/UK)
- [ ] Endowment products
- [ ] Takaful (Islamic insurance) framework

### Regulatory Mapping
- [ ] Regulatory requirement database
- [ ] Cross-jurisdiction comparison tools
- [ ] Regulatory update tracking
- [ ] Jurisdiction-specific disclosure templates

### Success Criteria
- Full compliance in 3+ non-US jurisdictions
- Multi-language support for 5+ languages
- International product types validated by local actuaries

---

## Phase 21 — Adjacent Domains
**Theme:** Expand the footprint

### Objectives
- Apply OPIE patterns to related insurance domains
- Build bridges to adjacent financial services

### Health Insurance
- [ ] Health insurance illustration framework
- [ ] Premium rate-up illustrations
- [ ] Benefit period projections
- [ ] Long-term care standalone products
- [ ] Medicare supplement illustrations
- [ ] ACA plan comparisons

### Disability Income
- [ ] DI illustration engine
- [ ] Benefit period and elimination period modeling
- [ ] Residual disability calculations
- [ ] Cost-of-living riders
- [ ] Future increase options

### Property & Casualty (Stretch)
- [ ] Premium projection framework
- [ ] Multi-year rate projections
- [ ] Deductible analysis
- [ ] Coverage comparison tools

### Retirement Planning Integration
- [ ] Retirement income projections
- [ ] Social Security optimization
- [ ] Pension vs. lump sum analysis
- [ ] Tax-efficient withdrawal sequencing
- [ ] Monte Carlo retirement scenarios

### Financial Planning Bridges
- [ ] Financial planning software integrations (eMoney, MoneyGuidePro, RightCapital)
- [ ] CRM integrations (Salesforce, Redtail)
- [ ] Portfolio management integrations
- [ ] Estate planning integration

### Success Criteria
- Health and DI illustration engines production-ready
- 3+ financial planning integrations live
- Retirement planning module validated by CFPs

---

## Phase 22 — Industry Standard
**Theme:** Change the industry

### Objectives
- OPIE as the expected foundation for illustration systems
- Regulatory recognition and potential adoption
- Academic and research integration

### Regulatory Engagement
- [ ] NAIC working group participation
- [ ] ACLI task force engagement
- [ ] SOA research partnership
- [ ] AAA practice council collaboration
- [ ] State insurance department outreach program
- [ ] Comment letters on illustration regulation updates
- [ ] OPIE as reference implementation in regulatory guidance
- [ ] Regulatory sandbox participation

### Standards Development
- [ ] ACORD integration and mapping
- [ ] Industry data standard contributions
- [ ] Open illustration format proposal
- [ ] API standardization initiative
- [ ] Cross-vendor interoperability specs

### Academic Integration
- [ ] University curriculum partnerships
- [ ] Actuarial exam preparation materials
- [ ] Research paper: "Open Standards for Insurance Illustrations"
- [ ] Academic journal publications
- [ ] Student competition sponsorship
- [ ] PhD research collaborations

### Innovation & Research
- [ ] Stochastic illustration framework
- [ ] Monte Carlo scenario generation
- [ ] Machine learning for assumption setting
- [ ] Behavioral modeling (lapse, utilization)
- [ ] Climate risk integration
- [ ] Real-time illustration APIs
- [ ] Embedded insurance illustration widgets
- [ ] Blockchain attestation (experimental)

### Industry Adoption Metrics
- [ ] Carrier adoption tracking
- [ ] Vendor integration tracking
- [ ] Market share estimation
- [ ] Industry survey and benchmarking
- [ ] Case study documentation

### Success Criteria
- NAIC references OPIE in guidance documents
- 10+ carriers using OPIE in production
- SOA publishes OPIE-based research
- OPIE taught in 5+ university actuarial programs
- Industry standard proposal submitted to ACORD

---

## Cross-Cutting Concerns

### Documentation (Ongoing)
- [ ] README and quick start
- [ ] API reference (auto-generated from OpenAPI)
- [ ] Product implementation guide
- [ ] Assumption specification guide
- [ ] Calculation methodology whitepaper
- [ ] Contributor guide
- [ ] Architecture decision records (ADRs)
- [ ] Changelog and migration guides
- [ ] Video tutorials
- [ ] Interactive examples (Jupyter notebooks)

### Security (Ongoing)
- [ ] Dependency vulnerability scanning (Dependabot, Snyk)
- [ ] Security policy and disclosure process
- [ ] OWASP compliance review
- [ ] Penetration testing (annual)
- [ ] SOC 2 Type II (for hosted offering)
- [ ] Input validation hardening
- [ ] Rate limiting for API
- [ ] Secrets management patterns
- [ ] Data encryption at rest and in transit

### Performance (Ongoing)
- [ ] Continuous benchmark suite
- [ ] Profiling and optimization cycles
- [ ] Memory usage optimization
- [ ] Startup time optimization
- [ ] Caching strategy refinement
- [ ] Lazy loading for large assumption sets
- [ ] Database query optimization
- [ ] CDN for static assets

### Quality (Ongoing)
- [ ] Code coverage targets (>90%)
- [ ] Mutation testing
- [ ] Fuzz testing for parsers
- [ ] Load testing
- [ ] Chaos engineering (for hosted)
- [ ] Accessibility compliance (WCAG for UI)

---

## Appendix: Product Coverage Matrix

| Product | Phase | Status | Complexity |
|---------|-------|--------|------------|
| Level Term | 1 | ✅ Done | Low |
| Simple UL | 1 | ✅ Done | Medium |
| Non-Par Whole Life | 8 | ✅ Done | Medium |
| Deferred Fixed Annuity | 9 | ✅ Done | Medium |
| SPIA | 16 | ⚠️ Partial | Medium |
| Indexed UL | 17 | 🔲 Planned | High |
| Fixed Indexed Annuity | 17 | 🔲 Planned | High |
| Variable UL | Future | 🔲 Planned | Very High |
| Variable Annuity | Future | 🔲 Planned | Very High |
| Participating WL | Future | 🔲 Planned | High |

---

## Appendix: Rider Coverage Matrix

| Rider | Phase | Status |
|-------|-------|--------|
| Basic rider framework | 7 | ✅ Done |
| Waiver of Premium | 18 | 🔲 Planned |
| Accidental Death Benefit | 18 | 🔲 Planned |
| Term Rider | 18 | 🔲 Planned |
| Guaranteed Insurability | 18 | 🔲 Planned |
| LTC Rider | 18 | 🔲 Planned |
| Overloan Protection | 18 | 🔲 Planned |
| No-Lapse Guarantee | 18 | 🔲 Planned |
| GLWB | 18 | 🔲 Planned |
| GMIB | 18 | 🔲 Planned |

---

## Appendix: Regulatory Coverage Matrix

| Regulation | Jurisdiction | Phase | Status |
|------------|--------------|-------|--------|
| NAIC Model Illustration Reg | US (Model) | 19 | 🔲 Planned |
| AG49/49-A/49-B | US (NAIC) | 19 | 🔲 Planned |
| IRC §7702 | US (Federal) | 19 | 🔲 Planned |
| Reg 60 | New York | 19 | 🔲 Planned |
| FCA Requirements | UK | 20 | 🔲 Planned |
| Solvency II | EU | 20 | 🔲 Planned |
| OSFI Guidelines | Canada | 20 | 🔲 Planned |
| IDD | EU | 20 | 🔲 Planned |

---

## Appendix: Integration Targets

| System Type | Examples | Phase | Status |
|-------------|----------|-------|--------|
| Financial Planning | eMoney, MoneyGuidePro | 21 | 🔲 Planned |
