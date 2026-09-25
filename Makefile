SETUP=python3 -m venv .venv

setup:
	python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
	git config core.hooksPath .githooks
	@echo "pre-commit hook enabled (.githooks/pre-commit) — blocks a commit that"
	@echo "changes data/clean/ or the app's data-facing files without a fresh,"
	@echo "fully-staged web/data/ rebuild alongside it."

# Rebuild web/data/ from data/clean/ and stage it — the safe way to close out
# an identity-pipeline change (see .githooks/pre-commit's own header for why
# "just re-add the files I touched" isn't). PHASE_1_SPLIT (docs/specs/
# app_split_spec.md): web/ is the site's own source now, not a copy of
# app/bsn_archivo.html (an archived pointer, see that file) — this target no
# longer touches web/index.html or web/css/js/ at all, only the generated data.
sync-web-data:
	.venv/bin/python -m src.build_web_data
	touch web/.nojekyll
	git add web/data/
	@echo "web/data/ rebuilt and staged — review with 'git status' before committing."

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

fetch-latinbasket:
	.venv/bin/python -m src.fetch_latinbasket

parse-latinbasket:
	.venv/bin/python -m src.parse_latinbasket

build-web-data:
	.venv/bin/python -m src.build_web_data

# The GitHub Pages site root (served from main:/web). PHASE_1_SPLIT
# (docs/specs/app_split_spec.md): web/index.html, web/css/, web/js/ ARE the
# site's own source now — nothing here is generated or copied from anywhere
# else. This target is just the one idempotent housekeeping bit Pages needs
# (a static site with a top-level 'data' folder gets swallowed by Jekyll
# without it) and a readiness echo.
site:
	touch web/.nojekyll
	@echo "web/ ready — Pages source: main branch, /web folder"

test:
	.venv/bin/pytest -q

.PHONY: setup enumerate samples fetch parse verify enumerate-root fetch-pre2007 parse-pre2007 fetch-players fetch-jug05 fetch-jugador05 parse-players reconcile enumerate-games fetch-games parse-games enumerate-historic fetch-historic build-web-data sync-web-data site test
