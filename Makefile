SETUP=python3 -m venv .venv

setup:
	python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

enumerate:
	.venv/bin/python -m src.wayback_cdx

test:
	.venv/bin/pytest -q

.PHONY: setup enumerate test
