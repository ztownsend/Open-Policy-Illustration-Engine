# AGENTS.md — OPIE (Open Policy Illustration Engine)
This file tells coding agents (Codex) and humans how to work on OPIE safely.

OPIE is **math-first** software. Small changes can cause “off by a penny in month 47” cascades.
Treat the output contract as sacred.

---

## 0) Project intent in one sentence
OPIE is a **deterministic, versioned policy illustration engine** that produces **stable monthly ledgers** under multiple scenarios, with correctness locked by **golden files + invariants**.

---

## 1) Non-negotiables (do not violate)

### 1.1 Determinism
- **No floats** in calculations. Use `decimal.Decimal`.
- The same request must produce **byte-identical** normalized output across runs and platforms.
- JSON output must be stable (sorted keys, stable Decimal encoding).
- On Python 3.14, prefer non-editable installs for the CLI entrypoint
  (`UV_NO_EDITABLE=1 uv sync`).

### 1.2 Normative ordering
The calculation ordering in the spec is **authoritative**. Do not reorder operations “for readability.”
If you truly must change ordering, treat it as a breaking change:
- bump `CALC_VERSION`
- update `docs/opie_mvp_spec.md`
- regenerate goldens intentionally

### 1.3 Golden file policy
Golden files are the output contract.
- Do **not** hand-edit golden JSON.
- Update only via `scripts/update_golden.py` (or the approved CLI wrapper).
- Every intentional output change must come with a rationale in the PR description.

### 1.4 Engine purity
`opie/core/engine.py` must remain:
- product-agnostic
- deterministic
- free of I/O
- free of network calls
- free of hidden global state

All product variability must live behind product hooks.

---

## 2) Where things live (mental map)

### Core
- `opie/core/engine.py` — monthly loop, scenario runner, lapse semantics, ordering
- `opie/core/money.py` — Decimal context, rounding, quantize functions
- `opie/core/types.py` — request/response schema (Pydantic), ledger fields
- `opie/core/invariants.py` — invariants and validation helpers
- `opie/core/versioning.py` — `CALC_VERSION`, `SCHEMA_VERSION`, `ROUNDING_POLICY_ID`

### Products
- `opie/products/base.py` — `ProductHooks` Protocol and hook result contracts
- `opie/products/ul_simple.py` — SimpleUL hooks
- `opie/products/term_level.py` — LevelTerm hooks
- `opie/products/wl_nonpar.py` — Non-par Whole Life hooks
- `opie/products/annuity_deferred.py` — Deferred annuity hooks
- `opie/products/annuity_spia.py` — SPIA hooks (toy)
- `opie/products/riders/*` — Rider hooks + registry
- `opie/products/registry.py` — product_code → hooks mapping

### Assumptions
- `opie/assumptions/models.py` — scenario models
- `opie/assumptions/tables.py` — COI table load + lookup
- `opie/assumptions/schedules.py` — surrender schedules
- `opie/assumptions/loaders.py` — loading/validation/normalization
- `opie/assumptions/packs.py` — pack manifest + validation

### Interfaces
- `opie/__init__.py` — exports `run_illustration()`
- `opie/cli/main.py` — CLI entrypoint
- `opie/api/app.py` — FastAPI app
- `opie_ui/app.py` — UI Explorer
- `opie_pdf/render.py` — PDF renderer

### Tests / Goldens
- `tests/golden/*` — committed expected outputs
- `tests/test_*` — golden tests, invariants tests, determinism tests
- `scripts/update_golden.py` — the ONLY supported way to regenerate goldens
- `conformance/cases.json` — canonical conformance manifest

---

## 3) Working style: PR-sized diffs only
OPIE should be developed in **small, reviewable increments**.

A “good” diff:
- changes one behavior or one module boundary
- includes tests
- passes CI
- has an explainable reason for any output change

A “bad” diff:
- changes ordering/rounding implicitly
- mixes product logic into the engine
- updates goldens without explaining why
- introduces float math or non-deterministic behavior

---

## 4) Standard workflow (agents must follow)

### 4.1 Before coding
1) Read:
   - `docs/opie_mvp_spec.md`
   - `docs/opie_technical_architecture.md`
   - `docs/opie_roadmap.md` (for sequencing)
   - `docs/testing_plan.md`
2) Identify which work item you’re implementing and its acceptance criteria.

### 4.2 Implement
- Make the smallest change that satisfies the work item.
- Keep engine/product/assumptions boundaries clean.

### 4.3 Tests
You must add or update tests in the same diff:
- unit tests for new logic
- invariants if new ledger fields or new paths
- golden updates only if outputs intentionally changed

### 4.4 Run commands locally
Run (at minimum):
- `uv run pytest`

If configured:
- `uv run ruff check .`
- `uv run ruff format .`

### 4.5 If outputs changed
Decide whether the change is:
- **Unintentional** → fix code until goldens pass without changing goldens
- **Intentional** → regenerate goldens via script and bump versions

Never “just update goldens” to make tests pass.

---

## 5) Output contracts, schema changes, and versioning

### 5.1 Adding a ledger field
If you add a new ledger field:
- Add it to `opie/core/types.py`
- Ensure it is deterministically populated
- Add at least one invariant or golden coverage
- Update `SCHEMA_VERSION` if the external schema changes

### 5.2 Changing math / ordering / rounding
Any change to:
- ordering
- rounding points
- floors
- lapse semantics
is a **calculation behavior change**.

Required steps:
1) Bump `CALC_VERSION` (and/or `ROUNDING_POLICY_ID` if rounding policy changed)
2) Update spec/docs that describe the changed behavior
3) Regenerate goldens intentionally
4) Ensure determinism test still passes

### 5.3 Backwards compatibility stance
- OPIE is allowed to evolve, but changes must be explicit and versioned.
- If you break schema: bump `SCHEMA_VERSION`.
- If you break calculation output: bump `CALC_VERSION`.

---

## 6) Numeric rules (do not improvise)

### 6.1 Decimal usage
- Use `Decimal` everywhere for:
  - money
  - rates
  - intermediate values
- Never convert to float for convenience.

### 6.2 Rounding
- Monetary fields are typically quantized to cents via `quantize_money()`.
- Rates use `quantize_rate()` or remain high-precision Decimals.
- Lapse check uses the documented rule (see spec); do not change without version bump.

### 6.3 Ordering is part of correctness
Do not refactor calculation steps into different order even if the final algebra looks equivalent.
Illustration engines are plagued by “equivalent but different” conventions. We avoid that by being explicit.

---

## 7) Error handling expectations

### 7.1 Error types
Prefer explicit exception classes (e.g., `AssumptionError`, `InvariantViolation`, `EngineError`).

### 7.2 Error messages must include context
Whenever possible, include:
- product_code
- scenario
- month index `t`
- the offending value(s)

This is essential for debugging golden diffs.

---

## 8) Golden tests: how to update safely

### 8.1 Update goldens
Use:
- `python scripts/update_golden.py --request examples/<file>.json --yes`

The script should:
- regenerate the expected outputs deterministically
- overwrite the correct golden files
- print a summary of changes (first diff month/field if possible)

### 8.2 What to do when a golden test fails
1) Identify the first month where the ledger differs.
2) Check:
   - premium/load ordering
   - charge ordering
   - rounding points
   - lapse boundary semantics
3) Fix root cause, rerun tests.
4) Only update goldens if the change is intended and versioned.

---

## 9) Performance rules (MVP posture)
- Do not optimize at the expense of determinism.
- Avoid micro-optimizations that change rounding frequency or ordering.
- If performance work is needed, add benchmarks and demonstrate equivalence.

---

## 10) Interface rules (CLI and API)
- Library API (`run_illustration`) must stay pure: no file I/O, no logging by default.
- CLI and API can log summary metadata but must not log full request bodies by default.
- API must enforce reasonable request size limits (as configured).

---

## 11) “Do not do” list (common ways agents break this project)
- Don’t introduce floats “temporarily.”
- Don’t reformat JSON in a way that changes key ordering or Decimal encoding.
- Don’t change ordering during “cleanup refactors.”
- Don’t move product logic into the engine.
- Don’t update goldens without:
  - a clear rationale
  - version bumps
  - and passing determinism tests

---

## 12) Suggested commands and development targets
Minimum:
- `pytest`

Recommended (if configured):
- `ruff check .`
- `ruff format .`

Interfaces:
- `uv run opie --help`
- `uv run opie illustrate --in examples/ul_simple_request.json --out /tmp/out.json`
- `uv run opie conformance run --manifest conformance/cases.json`
- `uv run uvicorn opie.api.app:app --reload`

---

## 13) Roadmap execution rule
If you’re working from `docs/roadmap.md`:
- implement **one work item at a time**
- do not skip ahead
- if a work item requires new files, add them in that item’s diff
- keep diffs small and tests green throughout

---

## 14) If you are unsure
When ambiguity arises, prefer:
1) what’s written in `docs/opie_mvp_spec.md`
2) then `docs/opie_technical_architecture.md`
3) then existing golden outputs and invariants

If you must choose a convention, **write it down** (spec + metadata) and lock it with tests.
