# Contributing to OPIE

Thanks for your interest in contributing to the Open Policy Illustration Engine!

## Quick Start

```bash
# Clone the repo
git clone https://github.com/<org>/Open-Policy-Illustration-Engine.git
cd Open-Policy-Illustration-Engine

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies
UV_NO_EDITABLE=1 uv sync

# Run tests
UV_NO_SYNC=1 uv run pytest

# Lint
UV_NO_SYNC=1 uv run ruff check .
UV_NO_SYNC=1 uv run ruff format --check .
```

## Development Rules

OPIE is **math-first** software. Small changes can cause "off by a penny in month 47" cascades. Please read `AGENTS.md` before making changes — it covers all the non-negotiable rules.

### The Short Version

1. **No floats.** Use `decimal.Decimal` for all calculations.
2. **Don't reorder operations.** The calculation ordering in the spec is authoritative.
3. **Don't hand-edit golden files.** Update via `python scripts/update_golden.py --request examples/<file>.json --yes`.
4. **Keep diffs small.** One behavior change per PR.
5. **Tests are required.** Every PR must include tests and pass `pytest`.

### Golden File Policy

Golden files (`tests/golden/*.json`) are the output contract. If your change produces different output:

- **Unintentional?** Fix your code until goldens pass without changing them.
- **Intentional?** Regenerate via the script, bump `CALC_VERSION` and/or `SCHEMA_VERSION`, and explain why in your PR description.

### Running Tests

```bash
# All tests
UV_NO_SYNC=1 uv run pytest

# Specific test file
UV_NO_SYNC=1 uv run pytest tests/test_ul_golden.py

# With coverage
UV_NO_SYNC=1 uv run pytest --cov=opie --cov-report=term-missing
```

### Code Style

- Ruff handles linting and formatting (configured in `pyproject.toml`).
- Run `uv run ruff check .` and `uv run ruff format .` before committing.
- Pre-commit hooks are available via `.pre-commit-config.yaml`.

### Where Things Live

| Directory | Purpose |
|-----------|---------|
| `opie/core/` | Engine, types, money, invariants, versioning |
| `opie/products/` | Product hooks (UL, Term, WL, Annuity) |
| `opie/assumptions/` | Scenario models, tables, schedules, packs |
| `opie/cli/` | CLI commands |
| `opie/api/` | FastAPI app |
| `opie/tax/` | IRC 7702 checker |
| `opie_ui/` | UI Explorer |
| `opie_pdf/` | PDF renderer |
| `tests/` | All tests |
| `tests/golden/` | Golden output files (do not hand-edit) |
| `examples/` | Example request JSON files |
| `conformance/` | Conformance test manifest |

### Versioning

- `CALC_VERSION`: Bump when calculation output changes.
- `SCHEMA_VERSION`: Bump when adding/removing fields from the response.
- `ROUNDING_POLICY_ID`: Bump when rounding policy changes.

All version constants live in `opie/core/versioning.py`.

## PR Guidelines

- Keep PRs focused — one logical change per PR.
- Include tests for new behavior.
- If outputs changed, regenerate goldens and explain why.
- Reference any related issue or plan doc.
