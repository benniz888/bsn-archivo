"""Repair mojibake player names in the committed data/clean/game_box_player.csv.

Why an overlay and not `make parse-games`: a control re-parse at HEAD changes 365 unrelated
`bsnpr_id` values (the identity spine moved after the games were parsed), so regenerating would
move far more than the three damaged names (docs/audits/phase72_audit.md, item 3). This touches
only rows whose `player_raw` is mojibake (UTF-8 bytes read as cp1252, "JosÃ©"):
  * `player_raw` is repaired by reversing that mis-decode, only when the round trip is exact;
  * `bsnpr_id` is filled on those rows only, only when it is blank and the parser's own resolver
    (`parse_games._resolve`: alias match + the season inside the player's career span) returns
    exactly one id. A row the resolver cannot settle stays blank; nothing is guessed.
Every other row is written back byte for byte (the CSV round-trips identically).

Idempotent: a second run finds no mojibake and changes nothing.

Run: `python -m src.apply_game_name_repair`           (check mode: prints the plan, writes nothing)
     `python -m src.apply_game_name_repair --apply`   (rewrites data/clean/game_box_player.csv)
Exit status in check mode is 1 when a repair is pending.
"""

from __future__ import annotations

import csv
import sys

from src import parse_games as pg
from src.parse_wayback import _write_csv

PATH = pg.CLEAN / "game_box_player.csv"


def unmojibake(value: str) -> str | None:
    """The repaired string, or None when `value` is not mojibake or the round trip is not exact."""
    if "Ã" not in value and "Â" not in value:
        return None
    try:
        fixed = value.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return None
    return fixed if fixed != value else None


def repair(rows: list[dict], resolver) -> tuple[list[dict], list[dict]]:
    """Return (new rows, change log). Input rows are not modified."""
    out, log = [], []
    for r in rows:
        fixed = unmojibake(r["player_raw"])
        if fixed is None:
            out.append(r)
            continue
        new = dict(r, player_raw=fixed)
        new_id = ""
        if not r["bsnpr_id"]:
            new_id = pg._resolve(fixed, int(r["season"]), *resolver)
            new["bsnpr_id"] = new_id
        out.append(new)
        log.append({"game_id": r["game_id"], "season": r["season"], "team_raw": r["team_raw"],
                    "before": r["player_raw"], "after": fixed,
                    "id_before": r["bsnpr_id"], "id_after": new["bsnpr_id"]})
    return out, log


def main(argv: list[str] | None = None) -> int:
    apply = "--apply" in (sys.argv[1:] if argv is None else argv)
    with PATH.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    new_rows, log = repair(rows, pg._load_resolver())
    by_name: dict[tuple, int] = {}
    for c in log:
        k = (c["before"], c["after"], c["id_after"] or "(unresolved)")
        by_name[k] = by_name.get(k, 0) + 1
    print(f"[game-name-repair] {len(rows)} rows; {len(log)} rows to repair")
    for (b, a, i), n in sorted(by_name.items()):
        print(f"  {n:4d}  {b!r} -> {a!r}  bsnpr_id {i}")
    if not apply:
        return 1 if log else 0
    if log:
        _write_csv(PATH, new_rows, pg.BOX_COLS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
