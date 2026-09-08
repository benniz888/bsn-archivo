SETUP=python3 -m venv .venv

setup:
	python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

enumerate:
	.venv/bin/python -m src.wayback_cdx

samples:
	.venv/bin/python -m src.fetch_samples

fetch:
	.venv/bin/python -m src.fetch_wayback

parse:
	.venv/bin/python -m src.parse_wayback

verify:
	.venv/bin/python -m src.verify_clean

enumerate-root:
	.venv/bin/python -m src.enumerate_root

fetch-pre2007:
	.venv/bin/python -m src.fetch_pre2007

parse-pre2007:
	.venv/bin/python -m src.parse_pre2007

fetch-players:
	.venv/bin/python -m src.fetch_players

parse-players:
	.venv/bin/python -m src.parse_players

reconcile:
	.venv/bin/python -m src.reconcile

enumerate-games:
	.venv/bin/python -m src.enumerate_games

fetch-games:
	.venv/bin/python -m src.fetch_games

parse-games:
	.venv/bin/python -m src.parse_games

test:
	.venv/bin/pytest -q

.PHONY: setup enumerate samples fetch parse verify enumerate-root fetch-pre2007 parse-pre2007 fetch-players parse-players reconcile enumerate-games fetch-games parse-games test
