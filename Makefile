UV ?= uv
PYTHON ?= python

.PHONY: sync test lint format format-check conformance ui pdf batch benchmark

sync:
	$(UV) sync --no-editable

test:
	$(UV) run pytest

lint:
	$(UV) run ruff check .

format:
	$(UV) run ruff format .

format-check:
	$(UV) run ruff format --check .

conformance:
	$(UV) run opie conformance run --manifest conformance/cases.json

ui:
	$(UV) run uvicorn opie_ui.app:app --reload

pdf:
	$(UV) run $(PYTHON) -m opie_pdf.render

batch:
	$(UV) run opie batch --in /tmp/opie_batch_in.ndjson --out /tmp/opie_batch_out.ndjson

benchmark:
	$(UV) run $(PYTHON) scripts/benchmark.py
