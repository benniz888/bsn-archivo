"""Drop the jug05 rows that show ANOTHER player's line, in the committed data/clean/player_career_seasons.csv.

A jug05 page can carry a line that belongs to a different player (docs/specs/foreign_slot_check.md): the slot row
follows the `r` URL parameter while the name and history come from another record. Shared lines also occur by
chance, so nothing is detected automatically. The owner decided (2026-09-21) that 5 published rows rest on another
player's line; they are listed by hand, with per-row evidence, in data/interim/jug05_foreign_lines.csv. This applies
that list through parse_players.drop_foreign_rows (the one place that decides) and logs every dropped row, with its
evidence, in data/interim/jug05_foreign_rows.csv. Class b and c rows (the owners, and players with no evidence either
way) are not on the list and stay.

Run it after apply_jug05_relabel (the list gives the relabelled season). Why a script and not `make parse-players`:
regenerating rewrites the identity outputs, whose committed versions carry hand edits (N7). Same pattern as
apply_jug05_relabel and apply_jug05_season_totals: touches nothing else in data/clean. After the drop the season-total
and per-team folds run on what remains, so the conflicts log is recomputed (a dropped row was never in it).

Deterministic and idempotent: a dropped row is gone, so a second run finds nothing to drop and leaves the CSV and the
logs byte-identical. A listed row that is neither in the CSV nor already in the log is a typo: exit 2.

Run: `python -m src.apply_jug05_foreign_rows`           (rewrites the CSV and the logs)
     `python -m src.apply_jug05_foreign_rows --check`   (writes nothing; exit 1 if it would drop, 2 if the list is invalid)
"""

from __future__ import annotations

import csv
import sys

from src import parse_players as pp

CAREER_COLUMNS = ["bsnpr_id", "season", "team_raw", "games", "points",
                  "source_id", "source_url", "retrieved_at"]


def _logged_keys() -> set[tuple]:
    path = pp.INTERIM_DIR / pp.FOREIGN_LOG_FILE
    if not path.exists():
        return set()
    with path.open(encoding="utf-8", newline="") as fh:
        return {(r["bsnpr_id"], r["season"], r["team_raw"], r["games"], r["points"], r["source_url"])
                for r in csv.DictReader(fh)}


def main(argv: list[str] | None = None) -> int:
    check = "--check" in (sys.argv[1:] if argv is None else argv)
    path = pp.CLEAN_DIR / "player_career_seasons.csv"
    with path.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    foreign = pp.load_foreign_rows()
    kept, dropped = pp.drop_foreign_rows(rows, foreign)
    done = {(d["bsnpr_id"], str(d["season"]), d["team_raw"], d["games"], d["points"], d["source_url"]) for d in dropped}
    lost = [f for f in foreign
            if (f["bsnpr_id"], f["season"], f["team_raw"], f["games"], f["points"], f["source_url"]) not in done | _logged_keys()]
    if lost:
        print("[jug05-foreign] listed rows found neither in the career CSV nor in the log:\n  "
              + "\n  ".join(f"{f['bsnpr_id']} {f['season']} {f['team_raw']} {f['games']}/{f['points']}" for f in lost))
        return 2
    kept, totals = pp.fold_season_totals(kept)
    kept, merged, conflicts = pp.fold_cross_source_career(kept)
    print(f"[jug05-foreign] {len(dropped)} foreign rows dropped ({len({d['bsnpr_id'] for d in dropped})} players); "
          f"{len(rows)} rows -> {len(kept)}; {len(totals)} season totals folded, {len(merged)} duplicate rows merged, "
          f"{len(conflicts)} stat conflicts kept as two rows")
    if check:
        return 1 if (dropped or totals or merged) else 0
    if dropped or totals or merged:
        pp._write_csv(path, kept, CAREER_COLUMNS)
    pp.write_foreign_rows_log(dropped)
    pp.write_season_totals_log(totals)
    pp.write_career_logs(merged, conflicts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
