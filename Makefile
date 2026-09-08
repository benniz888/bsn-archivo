SETUP=python3 -m venv .venv

setup:
	python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

enumerate:
	.venv/bin/python -m src.wayback_cdx

samples:
	.venv/bin/python -m src.fetch_samples

fetch:
	.venv/bin/python -m src.fetch_wayback

test:
	.venv/bin/pytest -q

.PHONY: setup enumerate samples fetch test
