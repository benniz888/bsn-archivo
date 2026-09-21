"""Relabel the jug05 career rows whose season label is the capture-relative "2005" slot, then fold.

jug05.asp keeps one slot for the newest season, labelled "2005" on every capture; the source overwrote it in
place between the captures of 2006-02-24 and 2006-05-28, so on a later capture the row labelled 2005 holds the
figures jugador.asp files under 2006 (docs/specs/jug05_offset_check.md). parse_players.jug05_season is the one
place that says which season such a row belongs to. This applies it to the rows already in the committed
data/clean/player_career_seasons.csv (the capture date is the Wayback timestamp in each row's source_url), then
runs the same fold merge_jug05 uses (parse_players.fold_cross_source_career), so a relabelled row that is identical
to the ficha's 2006 row is dropped and logged, and one that differs stays as two rows and is logged as a conflict.

Why a script and not `make parse-players`: regenerating rewrites the identity outputs, and the committed ones
carry hand edits (N7, docs/session.md). Same pattern as apply_career_dedup: touches nothing else in data/clean.

Writes, besides the CSV: data/interim/jug05_relabeled_rows.csv, one row per relabelled row with its old and new
season, capture date and source_url (history: a second run keeps it), and the two fold logs
(jug05_career_merged.csv, jug05_career_conflicts.csv).

Deterministic and idempotent: a relabelled row no longer carries the label, so a second run finds nothing to
relabel or fold and leaves the CSV and the logs byte-identical.

Run: `python -m src.apply_jug05_relabel`           (rewrites the CSV and the logs)
     `python -m src.apply_jug05_relabel --check`   (writes nothing; exit 1 if it would relabel or fold)
"""

from __future__ import annotations

import csv
import sys

from src import parse_players as pp

CAREER_COLUMNS = ["bsnpr_id", "season", "team_raw", "games", "points",
                  "source_id", "source_url", "retrieved_at"]
RELABELED_FILE = "jug05_relabeled_rows.csv"
RELABELED_COLUMNS = ["bsnpr_id", "old_season", "new_season", "capture_date", "source_url",
                     "team_raw", "games", "points"]


def _capture_date(ts: str) -> str:
    return f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}" if len(ts) >= 8 else ""


def relabel(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """(rows with the jug05 season labels resolved, one log row per relabelled row). Pure: the input rows are
    not mutated. Only a jug05 row is ever relabelled, and only through pp.jug05_season."""
    out: list[dict] = []
    log: list[dict] = []
    for r in rows:
        if r["source_id"] == pp.JUG05_SOURCE_ID:
            ts = pp.jug05_capture_ts(r["source_url"])
            new = pp.jug05_season(int(r["season"]), ts)
            if new != int(r["season"]):
                log.append({"bsnpr_id": r["bsnpr_id"], "old_season": r["season"], "new_season": str(new),
                            "capture_date": _capture_date(ts), "source_url": r["source_url"],
                            "team_raw": r["team_raw"], "games": r["games"], "points": r["points"]})
                r = {**r, "season": str(new)}
        out.append(r)
    return out, log


def write_relabel_log(log: list[dict], interim_dir=None) -> None:
    """History, like the merged log: rows relabelled now are ADDED to those already logged, since a relabelled
    row no longer carries its old season and a second run must not empty the file."""
    path = (interim_dir or pp.INTERIM_DIR) / RELABELED_FILE
    logged: dict[tuple, dict] = {}
    if path.exists():
        with path.open(encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                logged[(r["bsnpr_id"], r["old_season"], r["team_raw"], r["source_url"])] = r
    for r in log:
        logged[(r["bsnpr_id"], r["old_season"], r["team_raw"], r["source_url"])] = r
    pp._write_csv(path, sorted(logged.values(), key=lambda r: (
        int(r["bsnpr_id"]), int(r["old_season"]), r["team_raw"], r["source_url"])), RELABELED_COLUMNS)


def main(argv: list[str] | None = None) -> int:
    check = "--check" in (sys.argv[1:] if argv is None else argv)
    path = pp.CLEAN_DIR / "player_career_seasons.csv"
    with path.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    relabelled, log = relabel(rows)
    kept, merged, conflicts = pp.fold_cross_source_career(relabelled)
    print(f"[jug05-relabel] {len(log)} rows relabelled; {len(rows)} rows -> {len(kept)}; "
          f"{len(merged)} duplicate rows merged, {len(conflicts)} stat conflicts kept as two rows")
    if check:
        return 1 if (log or merged) else 0
    if log or merged:
        pp._write_csv(path, kept, CAREER_COLUMNS)
    write_relabel_log(log)
    pp.write_career_logs(merged, conflicts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
