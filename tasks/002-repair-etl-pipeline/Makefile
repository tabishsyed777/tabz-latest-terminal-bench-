PY ?= python3
export PYTHONPATH := src

.PHONY: test run clean

test:
	$(PY) -m pytest -q tests/

run:
	$(PY) -m etl.cli --input data/sales.csv --config config/pipeline.yaml --output output/sales_summary.json

clean:
	rm -rf output .pytest_cache
