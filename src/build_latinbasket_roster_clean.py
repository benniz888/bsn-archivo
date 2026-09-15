"""Backlog item 7, Phase D (D1) — promote the 744 `confirmed_match` rows
from `data/interim/latinbasket_match_*.csv` into a real clean file.

The 183 `insufficient_evidence` rows, the 6 Tier-1-triage leads, the 3
`likely_distinct_not_in_canonical` rows, and the 1
`likely_same_person_source_discrepancy` row are deliberately never read
here — they stay in `data/interim/`, exactly as scoped (owner, 2026-09-14).

Cross-references each confirmed row back to `data/interim/
latinbasket_roster_raw.csv` (by franchise_id + season + name_raw) to pull
the fields the match CSVs don't carry (jersey number, height, position,
source URL, retrieved-at) — the match CSV only ever recorded identity
evidence, not the roster facts themselves.

**8 of the 744 confirmed rows sit on a known duplicate candidate pair**
(Cruz Alvin `73`/`74`, Lopez Ivan `951`/`952`, Rivera Raul `1947`/`1948`
— all three pairs share an exact birthdate, logged as Tier-1-triage leads,
not resolved here). Each is written under the lower-numbered id,
deterministically, disclosed here rather than silently picked — the real
merge decision belongs to that future triage pass, not to this wiring
step.

Run: `python -m src.build_latinbasket_roster_clean`
"""

from __future__ import annotations

import csv
from pathlib import Path

from src.wayback_cdx import REPO_ROOT

INTERIM_DIR = REPO_ROOT / "data" / "interim"
CLEAN_DIR = REPO_ROOT / "data" / "clean"
OUT_PATH = CLEAN_DIR / "player_roster_latinbasket.csv"

FIELDNAMES = [
    "bsnpr_id", "season", "franchise_id", "jersey_number", "height_cm",
    "position_raw", "name_raw", "source_id", "source_url", "retrieved_at", "confidence",
]

FRANCHISES = [
    "atenienses_manati", "atleticos_san_german", "brujos_guayama", "caciques_humacao",
    "cangrejeros_santurce", "capitanes_arecibo", "cariduros_fajardo", "criollos_caguas",
    "indios_mayaguez", "leones_ponce", "maratonistas_coamo", "mets_guaynabo",
    "piratas_quebradillas", "santeros_aguada", "vaqueros_bayamon",
]


def _load_raw_index() -> dict[tuple[str, str, str], dict]:
    idx: dict[tuple[str, str, str], dict] = {}
    with (INTERIM_DIR / "latinbasket_roster_raw.csv").open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            key = (r["franchise_id"], r["season"], r["name_raw"])
            idx.setdefault(key, r)  # first wins; duplicates checked separately
    return idx


def promote(match_rows_by_franchise: dict[str, list[dict]],
            raw_idx: dict[tuple[str, str, str], dict]) -> list[dict]:
    """Pure selection logic, no file I/O — the part worth unit-testing in
    isolation. `match_rows_by_franchise` is franchise_id -> that franchise's
    rows from `latinbasket_match_<fid>.csv`; `raw_idx` is the
    (franchise_id, season, name_raw) -> row index from
    `latinbasket_roster_raw.csv` (see `_load_raw_index`)."""
    out_rows: list[dict] = []
    duplicate_pair_rows = 0
    unmatched_to_raw = []

    for fid, match_rows in match_rows_by_franchise.items():
        for r in match_rows:
            if r["disposition"] != "confirmed_match":
                continue
            candidate_ids = r["candidate_ids"].split(";")
            if len(candidate_ids) > 1:
                duplicate_pair_rows += 1
            bsnpr_id = min(candidate_ids, key=int)

            raw = raw_idx.get((fid, r["season"], r["name_raw"]))
            if raw is None:
                unmatched_to_raw.append((fid, r["season"], r["name_raw"]))
                continue

            out_rows.append({
                "bsnpr_id": bsnpr_id,
                "season": r["season"],
                "franchise_id": fid,
                "jersey_number": raw.get("jersey_number") or "",
                "height_cm": raw.get("height_cm") or "",
                "position_raw": raw.get("position_raw") or "",
                "name_raw": r["name_raw"],
                "source_id": "latinbasket",
                "source_url": raw["source_url"],
                "retrieved_at": raw["retrieved_at"],
                "confidence": "single-source",
            })

    if unmatched_to_raw:
        raise SystemExit(f"FATAL: {len(unmatched_to_raw)} confirmed rows could not be traced back "
                          f"to a raw roster row: {unmatched_to_raw[:10]}")

    out_rows.sort(key=lambda r: (int(r["bsnpr_id"]), int(r["season"]), r["franchise_id"]))

    # no duplicate (bsnpr_id, season, franchise_id) - a real mid-season trade
    # would be a different franchise_id for the same (bsnpr_id, season), which
    # this key allows; a true dupe would be an identical key twice.
    seen = set()
    dupes = []
    for r in out_rows:
        key = (r["bsnpr_id"], r["season"], r["franchise_id"])
        if key in seen:
            dupes.append(key)
        seen.add(key)
    if dupes:
        raise SystemExit(f"FATAL: {len(dupes)} duplicate (bsnpr_id, season, franchise_id) rows: {dupes[:10]}")

    print(f"[build_latinbasket_roster_clean] {len(out_rows)} rows "
          f"({duplicate_pair_rows} on a known Tier-1-triage duplicate pair, "
          f"written under the lower id)")
    return out_rows


def build() -> list[dict]:
    raw_idx = _load_raw_index()
    match_rows_by_franchise: dict[str, list[dict]] = {}
    for fid in FRANCHISES:
        match_path = INTERIM_DIR / f"latinbasket_match_{fid}.csv"
        with match_path.open(encoding="utf-8") as fh:
            match_rows_by_franchise[fid] = list(csv.DictReader(fh))
    return promote(match_rows_by_franchise, raw_idx)


def main() -> int:
    rows = build()
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(rows)
    print(f"[build_latinbasket_roster_clean] -> {OUT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
