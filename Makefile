UV ?= uv
PYTHON ?= python
UV_NO_EDITABLE ?= 1

export UV_NO_EDITABLE

.PHONY: help sync test lint format format-check conformance ui pdf batch benchmark

help: ## Show available targets
	@awk 'BEGIN {FS=":.*## "}; /^[a-zA-Z_-]+:.*## / {printf "%-16s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

sync: ## Sync dependencies (non-editable by default)
	$(UV) sync

test: ## Run tests
	$(UV) run pytest

lint: ## Run ruff lint
	$(UV) run ruff check .

format: ## Format with ruff
	$(UV) run ruff format .

format-check: ## Check formatting
	$(UV) run ruff format --check .

conformance: ## Run canonical conformance cases
	$(UV) run opie conformance run --manifest conformance/cases.json

ui: ## Run the UI explorer
	$(UV) run uvicorn opie_ui.app:app --reload

pdf: ## Render a PDF (programmatic entrypoint)
	$(UV) run $(PYTHON) -m opie_pdf.render

batch: ## Run batch NDJSON example
	$(UV) run opie batch --in /tmp/opie_batch_in.ndjson --out /tmp/opie_batch_out.ndjson

benchmark: ## Run benchmark script
	$(UV) run $(PYTHON) scripts/benchmark.py
