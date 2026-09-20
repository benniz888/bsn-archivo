"""Apply the cross-source career dedup to the committed data/clean/player_career_seasons.csv.

Why a script and not `make parse-players`: regenerating rewrites the identity outputs, and the
committed ones carry hand edits (the 2026-09-14 identity merges, docs/session.md), so a
regeneration is not safe at HEAD. This applies the same function merge_jug05 uses
(parse_players.fold_cross_source_career) to the rows already in the CSV and touches nothing
else in data/clean. See docs/specs/merge_jug05_audit_spec.md (D1-D6).

Deterministic and idempotent: kept rows stay in file order, the two interim logs are sorted,
and a second run finds nothing to merge, so it leaves the CSV and both logs unchanged.
Both logs carry jug05_retrieved_at, the fetch time of the jug05 row, so that provenance
survives the row being dropped from the CSV.

Run: `python -m src.apply_career_dedup`            (rewrites the CSV and the two logs)
     `python -m src.apply_career_dedup --check`    (writes nothing; exit 1 if it would merge)
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
    kept, merged, conflicts = pp.fold_cross_source_career(rows)
    print(f"[career-dedup] {len(rows)} rows -> {len(kept)}; {len(merged)} duplicate rows merged, "
          f"{len(conflicts)} stat conflicts kept as two rows")
    if check:
        return 1 if merged else 0
    if merged:
        pp._write_csv(path, kept, CAREER_COLUMNS)
    pp.write_career_logs(merged, conflicts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
