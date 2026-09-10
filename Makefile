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

fetch-jug05:
	.venv/bin/python -m src.fetch_jug05

fetch-jugador05:
	.venv/bin/python -m src.fetch_jugador05

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

enumerate-historic:
	.venv/bin/python -m src.enumerate_historic_followup

fetch-historic:
	.venv/bin/python -m src.fetch_historic_followup

build-web-data:
	.venv/bin/python -m src.build_web_data

# Assemble the GitHub Pages site root (served from main:/web). The shell is a
# committed byte-copy of app/bsn_archivo.html; `make verify` fails if it drifts.
site:
	cp app/bsn_archivo.html web/index.html
	touch web/.nojekyll
	@echo "web/ ready — Pages source: main branch, /web folder"

test:
	.venv/bin/pytest -q

.PHONY: setup enumerate samples fetch parse verify enumerate-root fetch-pre2007 parse-pre2007 fetch-players fetch-jug05 fetch-jugador05 parse-players reconcile enumerate-games fetch-games parse-games enumerate-historic fetch-historic build-web-data site test
