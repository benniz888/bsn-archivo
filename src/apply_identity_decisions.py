"""Apply the curated identity decisions to the committed identity CSVs.

Why a script and not `make parse-players`: regenerating rewrites the identity outputs, and the committed
ones carry hand edits (N7, docs/session.md), so a regeneration is not safe at HEAD. This transforms the
rows already in the CSVs, the way apply_career_dedup does, and touches nothing else.

Inputs are two curated files in data/clean:
  player_identity_decisions.csv  merge / not_same verdicts with their evidence, who decided and when
                                 (evidence_es is the Spanish public text; no Wikipedia claim or URL in it)
  player_id_tombstones.csv       retired_id -> survivor_id for every applied merge (retired_name feeds the
                                 redirects the site builds)
For every tombstone: whatever the retired id owns is re-pointed to the survivor (aliases, id_map, bios,
career rows, roster rows, box rows, crosswalk, review queue, jug05 logs); a row identical to one the survivor
already has is dropped and logged in data/interim/player_merge_dropped_rows.csv; the retired canonical row is
removed; the jug05 rows are then refolded with the function merge_jug05 uses. A retired id is never reused.

Idempotent: a second run finds nothing that references a retired id and changes nothing.
Run: python -m src.apply_identity_decisions            (rewrites the CSVs and the logs)
     python -m src.apply_identity_decisions --check    (writes nothing; exit 1 if it would change something,
                                                        exit 2 if the decisions or tombstones are invalid)
A future regeneration reads the same two files and applies apply() to its in-memory tables (not implemented).
"""

from __future__ import annotations

import csv
import re
import sys
from collections import Counter
from pathlib import Path

from src import parse_players as pp

DECISIONS_FILE = "player_identity_decisions.csv"
TOMBSTONES_FILE = "player_id_tombstones.csv"
DROPPED_FILE = "player_merge_dropped_rows.csv"
DECISION_COLUMNS = ["decision_id", "kind", "ids", "survivor_id", "status", "evidence", "evidence_es",
                    "source_doc", "decided_by", "decided_at"]
TOMBSTONE_COLUMNS = ["retired_id", "survivor_id", "decision_id", "retired_name", "retired_at"]
DROPPED_COLUMNS = ["decision_id", "retired_id", "survivor_id", "season", "team_raw", "games", "points",
                   "source_id", "source_url", "retrieved_at", "reason"]
KINDS = {"merge", "not_same"}

# name -> (directory, file name); the crosswalk lives in app/
TABLES = {
    "canonical": ("clean", "players_canonical.csv"),
    "aliases": ("clean", "player_aliases.csv"),
    "id_map": ("clean", "player_id_map.csv"),
    "bios": ("clean", "player_bios.csv"),
    "career": ("clean", "player_career_seasons.csv"),
    "roster": ("clean", "player_roster_latinbasket.csv"),
    "box": ("clean", "game_box_player.csv"),
    "crosswalk": ("app", "player_crosswalk.csv"),
    "review": ("interim", "player_review_queue.csv"),
    "merged_log": ("interim", "jug05_career_merged.csv"),
}


def _dirs(clean_dir=None, interim_dir=None, app_dir=None) -> dict[str, Path]:
    return {"clean": Path(clean_dir or pp.CLEAN_DIR), "interim": Path(interim_dir or pp.INTERIM_DIR),
            "app": Path(app_dir or pp.CLEAN_DIR.parent.parent / "app")}


def _read(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        return list(reader.fieldnames or []), list(reader)


def load_decisions(clean_dir=None) -> list[dict]:
    return _read(Path(clean_dir or pp.CLEAN_DIR) / DECISIONS_FILE)[1]


def load_tombstones(clean_dir=None) -> list[dict]:
    return _read(Path(clean_dir or pp.CLEAN_DIR) / TOMBSTONES_FILE)[1]


def validate(decisions: list[dict], tombstones: list[dict]) -> list[str]:
    """Problems with the curated files; empty when they are consistent."""
    out: list[str] = []
    by_id = {}
    for d in decisions:
        where = f"decision {d['decision_id']}"
        if d["decision_id"] in by_id:
            out.append(f"{where}: duplicate decision_id")
        by_id[d["decision_id"]] = d
        ids = [i for i in d["ids"].split(";") if i]
        if d["kind"] not in KINDS:
            out.append(f"{where}: kind {d['kind']!r} is not one of {sorted(KINDS)}")
        if not all(i.isdigit() for i in ids) or len(set(ids)) != len(ids) or len(ids) < 2:
            out.append(f"{where}: ids must be two or more distinct integers, got {d['ids']!r}")
        if d["kind"] == "merge" and d["survivor_id"] not in ids:
            out.append(f"{where}: a merge needs a survivor_id among its ids")
        if d["kind"] == "not_same" and (d["survivor_id"] or len(ids) != 2):
            out.append(f"{where}: not_same names exactly two ids and no survivor")
        for col in ("evidence", "evidence_es", "source_doc", "decided_by", "decided_at"):
            if not d.get(col, "").strip():
                out.append(f"{where}: {col} is required")
        if re.search(r"wikipedia|https?://", d.get("evidence_es", ""), re.I):
            out.append(f"{where}: evidence_es is public text; no Wikipedia claim or URL (project.md L2)")
    retired: dict[str, str] = {}
    for t in tombstones:
        where = f"tombstone {t['retired_id']}"
        if t["retired_id"] in retired:
            out.append(f"{where}: retired twice")
        retired[t["retired_id"]] = t["survivor_id"]
        d = by_id.get(t["decision_id"])
        if not (t["retired_id"].isdigit() and t["survivor_id"].isdigit()) or t["retired_id"] == t["survivor_id"]:
            out.append(f"{where}: retired_id and survivor_id must be different integers")
        elif d is None or d["kind"] != "merge" or d["survivor_id"] != t["survivor_id"] \
                or t["retired_id"] not in d["ids"].split(";"):
            out.append(f"{where}: decision {t['decision_id']} is not a merge that retires it into {t['survivor_id']}")
        if not t["retired_name"].strip():
            out.append(f"{where}: retired_name is required (the redirects are built from it)")
    for t in tombstones:
        if t["survivor_id"] in retired:
            out.append(f"tombstone {t['retired_id']}: survivor {t['survivor_id']} is itself retired (no chains)")
    for d in decisions:
        if d["kind"] == "not_same":
            a, b = d["ids"].split(";")[:2]
            if retired.get(a, a) == retired.get(b, b):
                out.append(f"decision {d['decision_id']}: {a} and {b} are recorded as not the same person but are merged")
    return out


def _key(r: dict) -> tuple:
    return (r["season"], pp.city_token(r["team_raw"]), r["games"], r["points"])


def apply(tables: dict[str, tuple[list[str], list[dict]]], tombstones: list[dict]):
    """Pure transformation. `tables` maps a name in TABLES to (columns, rows). Returns
    (new tables, dropped-row log, merged pairs, stat conflicts, counts). Rows are copied, never mutated."""
    retired = {t["retired_id"]: t["survivor_id"] for t in tombstones}
    decision = {t["retired_id"]: t["decision_id"] for t in tombstones}
    new = {name: (cols, [dict(r) for r in rows]) for name, (cols, rows) in tables.items()}
    counts: dict[str, int] = {}

    canon_cols, canon = new["canonical"]
    have = {r["bsnpr_id"]: r for r in canon}
    for old, surv in retired.items():
        if surv not in have:
            raise ValueError(f"survivor {surv} of retired id {old} is not a canonical row")
    names = {r["bsnpr_id"]: r["canonical_name"] for r in canon}
    canon[:] = [r for r in canon if r["bsnpr_id"] not in retired]
    counts["canonical rows removed"] = len(have) - len(canon)

    # aliases: re-point in place; the retired canonical name becomes a merged_name alias; duplicates are dropped
    _, aliases = new["aliases"]
    akey = lambda r: (r["bsnpr_id"], r["alias"], r["normalized_alias"], r["alias_type"])
    seen = {akey(r) for r in aliases if r["bsnpr_id"] not in retired}
    kept, moved, dup = [], 0, 0
    for r in aliases:
        if r["bsnpr_id"] in retired:
            r["bsnpr_id"] = retired[r["bsnpr_id"]]
            if r["alias_type"] == "canonical":
                r["alias_type"] = "merged_name"
            if akey(r) in seen:
                dup += 1
                continue
            seen.add(akey(r))
            moved += 1
        kept.append(r)
    aliases[:] = kept
    counts["alias rows re-pointed"], counts["alias rows dropped as duplicates"] = moved, dup

    # id_map, box scores, crosswalk: re-point the id (and the name kept beside it)
    for name in ("id_map", "box", "crosswalk"):
        moved = 0
        for r in new[name][1]:
            if r["bsnpr_id"] in retired:
                r["bsnpr_id"] = retired[r["bsnpr_id"]]
                if "canonical_name" in r:
                    r["canonical_name"] = names[r["bsnpr_id"]]
                moved += 1
        counts[f"{name} rows re-pointed"] = moved

    # bios: one row per id, so a survivor that already has one is a decision for a person, not this script
    _, bios = new["bios"]
    owned = {r["bsnpr_id"] for r in bios if r["bsnpr_id"] not in retired}
    moved = 0
    for r in bios:
        if r["bsnpr_id"] in retired:
            if retired[r["bsnpr_id"]] in owned:
                raise ValueError(f"survivor {retired[r['bsnpr_id']]} already has a bio; merge by hand")
            r["bsnpr_id"] = retired[r["bsnpr_id"]]
            moved += 1
    counts["bios re-pointed"] = moved

    # roster: (id, season, franchise) is unique, so a clash is an error, not something to drop
    _, roster = new["roster"]
    moved = 0
    for r in roster:
        if r["bsnpr_id"] in retired:
            r["bsnpr_id"] = retired[r["bsnpr_id"]]
            moved += 1
    clash = [k for k, n in Counter((r["bsnpr_id"], r["season"], r["franchise_id"]) for r in roster).items() if n > 1]
    if clash:
        raise ValueError(f"roster rows would collide after the merge: {clash[:5]}")
    roster.sort(key=lambda r: (int(r["bsnpr_id"]), int(r["season"]), r["franchise_id"]))
    counts["roster rows re-pointed"] = moved

    # career: re-point in place, drop a row identical (source, season, city, games, points) to one the survivor has
    _, career = new["career"]
    twin = {(r["bsnpr_id"], r["source_id"]) + _key(r) for r in career if r["bsnpr_id"] not in retired}
    kept, dropped, carried = [], [], 0
    for r in career:
        if r["bsnpr_id"] in retired:
            old = r["bsnpr_id"]
            r["bsnpr_id"] = retired[old]
            k = (r["bsnpr_id"], r["source_id"]) + _key(r)
            if k in twin:
                dropped.append({"decision_id": decision[old], "retired_id": old, "survivor_id": r["bsnpr_id"],
                                "season": r["season"], "team_raw": r["team_raw"], "games": r["games"],
                                "points": r["points"], "source_id": r["source_id"], "source_url": r["source_url"],
                                "retrieved_at": r["retrieved_at"],
                                "reason": "identical to a row the survivor already has"})
                continue
            twin.add(k)
            carried += 1
        kept.append(r)
    counts["career rows dropped as identical"], counts["career rows carried to a survivor"] = len(dropped), carried
    before = len(kept)
    kept, merged, conflicts = pp.fold_cross_source_career(kept)
    counts["jug05 rows folded into a survivor's row"] = before - len(kept)
    career[:] = kept

    # interim logs: the review queue keeps its rows but names survivors; the merged log follows the twin row
    _, review = new["review"]
    moved = 0
    for r in review:
        if any(i in retired for i in r["candidate_ids"].split("|")):
            for col in ("candidate_ids", "club_match_ids"):
                seen_ids: list[str] = []
                for i in (x for x in r[col].split("|") if x):
                    i = retired.get(i, i)
                    if i not in seen_ids:
                        seen_ids.append(i)
                r[col] = "|".join(seen_ids)
            r["candidate_names"] = " | ".join(names[i] for i in r["candidate_ids"].split("|") if i in names)
            moved += 1
    counts["review-queue rows re-pointed"] = moved
    _, mlog = new["merged_log"]
    moved = 0
    for r in mlog:
        if r["bsnpr_id"] in retired:
            r["bsnpr_id"] = retired[r["bsnpr_id"]]
            twins = [c for c in career if c["bsnpr_id"] == r["bsnpr_id"] and c["season"] == r["season"]
                     and c["source_id"] == pp.SOURCE_ID and (c["games"], c["points"]) == (r["games"], r["points"])
                     and pp.city_token(c["team_raw"]) == pp.city_token(r["jug05_team_raw"])]
            if twins:
                r["players_source_url"] = twins[0]["source_url"]
            moved += 1
    counts["merged-log rows re-pointed"] = moved
    return new, dropped, merged, conflicts, counts


def _write_if_changed(path: Path, cols: list[str], rows: list[dict], old_rows: list[dict]) -> bool:
    if rows == old_rows:
        return False
    pp._write_csv(path, rows, cols)
    return True


def _write_dropped(path: Path, dropped: list[dict]) -> None:
    logged: dict[tuple, dict] = {}
    if path.exists():
        for r in _read(path)[1]:
            logged[(r["retired_id"], r["season"], r["team_raw"], r["source_url"])] = r
    for r in dropped:
        logged[(r["retired_id"], r["season"], r["team_raw"], r["source_url"])] = {k: str(v) for k, v in r.items()}
    rows = sorted(logged.values(), key=lambda r: (int(r["retired_id"]), int(r["season"]), r["team_raw"]))
    pp._write_csv(path, rows, DROPPED_COLUMNS)


def main(argv: list[str] | None = None) -> int:
    check = "--check" in (sys.argv[1:] if argv is None else argv)
    dirs = _dirs()
    decisions, tombstones = load_decisions(), load_tombstones()
    problems = validate(decisions, tombstones)
    if problems:
        print("[identity] the decisions or tombstones are invalid:\n  " + "\n  ".join(problems))
        return 2
    tables = {name: _read(dirs[d] / f) for name, (d, f) in TABLES.items()}
    new, dropped, merged, conflicts, counts = apply(tables, tombstones)
    changed = [name for name in TABLES if new[name][1] != tables[name][1]]
    summary = "; ".join(f"{k}: {v}" for k, v in counts.items() if v)
    print(f"[identity] {len(tombstones)} tombstones, {len(decisions)} decisions; "
          f"{summary or 'nothing references a retired id'}")
    if check:
        print(f"[identity] would change: {', '.join(changed) if changed else 'nothing'}")
        return 1 if changed or dropped or merged else 0
    for name in changed:
        d, f = TABLES[name]
        if name == "career":
            continue                                   # written below, with the fold's logs
        if name == "merged_log":
            continue
        _write_if_changed(dirs[d] / f, tables[name][0], new[name][1], tables[name][1])
    if "career" in changed or merged:
        pp._write_csv(dirs["clean"] / TABLES["career"][1], new["career"][1], tables["career"][0])
    if "merged_log" in changed:
        pp._write_csv(dirs["interim"] / TABLES["merged_log"][1], new["merged_log"][1], tables["merged_log"][0])
    if "career" in changed or merged or "merged_log" in changed:
        pp.write_career_logs(merged, conflicts)
    if dropped:
        _write_dropped(dirs["interim"] / DROPPED_FILE, dropped)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
