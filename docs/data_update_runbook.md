# Data update runbook

`make data-update` is the one command for turning the committed data into a verified `web/data/`. It does not fetch anything, does not parse raw pages and never commits.

## When to run it
- After any change under `data/clean/`, `src/display_names.py`, `src/apply_game_name_repair.py` or `src/build_web_data.py`.
- Before a commit that touches data, to see exactly what would change.
- After pulling, to confirm the checkout is consistent (expect all green and a zero diff).

## Check or apply
- `make data-update` (check, the default). Works on copies in a temp directory and **writes nothing to a tracked file**. Prints the report: row counts per dataset, name quality, mojibake scan, Javier González rows, the bsnpr_id digest, Cruz/Morales flags, and the diff it would make (files and rows), then runs the full test suite. `--skip-tests` skips the suite for a quick look.
- `make data-update ARGS=--apply`. Needs a clean tree under `data/clean`, `data/raw` and `web/data`. Repeats every check; only if all pass does it write (the game-name overlay, then `build_web_data`), run `update_asset_hashes` and the full suite, and write `docs/audits/data_update_report.md`. Then review `git status` and commit by explicit path (the pre-commit hook rebuilds `web/data` and rejects a stale one).
- Exit code: 0 all green, 1 a check failed (one line each on stderr), 2 usage error or a refused command.

## What a failure means
| Check | Meaning | Do |
|---|---|---|
| preflight / tree | uncommitted data changes (apply only) | commit or stash, re-run |
| game-name overlay | mojibake the overlay cannot repair | `python -m src.apply_game_name_repair`, then fix the decoder or the row |
| override list | an override has no source row, or the count moved | cite a `data/clean/*.csv:line` or remove it |
| verify_clean | an integrity check over `data/clean` or `web/data` failed | `make verify`, fix the first failure |
| build_web_data | the build raised in the temp dir | `make build-web-data` for the traceback |
| mojibake scan | non-zero count | an encoding regression; compare with `docs/audits/phase72_audit.md` item 3 |
| Gonzalez unassigned | not 84 | a row was assigned or added; review, then update `EXPECTED_GONZALEZ_UNASSIGNED` |
| bsnpr_id digest | a box row outside the three repaired names changed | a bsnpr_id moved; revert, or update `BOX_UNRELATED_*` if intended |
| name quality | an ALL-CAPS name the display layer does not handle | extend `src/display_names.py` (evidence for any override) |
| pytest | a test failed | `.venv/bin/python -m pytest -q` |

If `--apply` fails after it started writing, nothing is committed: inspect `git status` and restore with `git checkout -- data/clean web`.

## What never to run
- `make parse-players` and `make sync-web-data`: not idempotent at HEAD (N7); they re-mint ids that were merged by hand. The pipeline refuses them.
- `make parse-games`: a re-parse moves 365 unrelated `bsnpr_id` values. Damaged names are repaired by the overlay, which rewrites only those rows.
- Anything that edits `data/raw/` (immutable, PC5) or fetches from the network without being asked (PC6).
