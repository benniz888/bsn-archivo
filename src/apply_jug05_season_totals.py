"""Fold the jug05 rows that are a player's SEASON TOTAL, in the committed data/clean/player_career_seasons.csv.

In the slot labelled 2005 jug05.asp mostly shows one row for the whole season of a player who changed team, while
jugador.asp (the ficha) has one row per team; the per-team fold paired that total with one team's partial row and
reported a conflict (docs/specs/jug05_sumrow_check.md). parse_players.fold_season_totals is the one place that
decides: a jug05 row whose games AND points both equal the sum of the players-source rows of the same player-season
(at least two rows, no blank figure, and not equal to a single team row) is corroboration of the season. It is
removed from the CSV and logged in data/interim/jug05_season_totals.csv with the per-team rows it sums; the
per-team rows stay. Then the existing per-team fold runs, so the conflicts log is recomputed from what remains.

Run it after apply_jug05_relabel (the rule reads the seasons that one files rows under). Why a script and not
`make parse-players`: regenerating rewrites the identity outputs, whose committed versions carry hand edits (N7).
Same pattern as apply_career_dedup and apply_jug05_relabel: touches nothing else in data/clean.

Deterministic and idempotent: a folded row is gone, so a second run finds nothing to fold and leaves the CSV and
the three logs byte-identical.

Run: `python -m src.apply_jug05_season_totals`           (rewrites the CSV and the logs)
     `python -m src.apply_jug05_season_totals --check`   (writes nothing; exit 1 if it would fold anything)
"""

from __future__ import annotations

import csv
import sys

from src import parse_players as pp

CAREER_COLUMNS = ["bsnpr_id", "season", "team_raw", "games", "points",
                  "source_id", "source_url", "retrieved_at"]


def main(argv: list[str] | None = None) -> int:
    check = "--check" in (sys.argv[1:] if argv is None else argv)
    path = pp.CLEAN_DIR / "player_career_seasons.csv"
    with path.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    kept, totals = pp.fold_season_totals(rows)
    kept, merged, conflicts = pp.fold_cross_source_career(kept)
    print(f"[jug05-season-totals] {len(totals)} season totals folded; {len(rows)} rows -> {len(kept)}; "
          f"{len(merged)} duplicate rows merged, {len(conflicts)} stat conflicts kept as two rows")
    if check:
        return 1 if (totals or merged) else 0
    if totals or merged:
        pp._write_csv(path, kept, CAREER_COLUMNS)
    pp.write_season_totals_log(totals)
    pp.write_career_logs(merged, conflicts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
