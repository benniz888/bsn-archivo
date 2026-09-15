"""Backlog item 7, Phase C — match `data/interim/latinbasket_roster_raw.csv`
rows against the canonical player spine, franchise-anchored batch at a time.

**This never merges anything.** D1 ("never on name alone") plus this
session's own lesson (`merge_jugador05`'s blind-accept-on-blank-birth-year
bug, which silently cross-contaminated Piculin Ortiz's identity) means
every candidate here — even the strongest tier — is a *proposal* for the
owner to confirm or reject per batch, the same discipline as
`jug05_xwalk.csv`/`jugador05_xwalk.csv`. Output is a review CSV per
franchise, `data/interim/latinbasket_match_<franchise_id>.csv`; nothing
in `data/clean/` changes here.

**Confidence tiers, weakest evidence loses even at the same candidate
count** (owner requirement, 2026-09-14):
  1_exact_birth_confirmed       - row has an exact 2-digit birth year
                                   (`flat_bo`), one candidate agrees exactly.
  2_approx_birth_confirmed      - row only has an age-derived
                                   `approx_birth_year` (+/-1, `flat_age`/
                                   `widget`), one candidate agrees within
                                   that tolerance. Deliberately a *separate,
                                   weaker* tier from (1), never blended into
                                   it, even though the candidate-count shape
                                   looks identical.
  3_no_birth_data_name_shape    - the canonical candidate has no birth_year
                                   on file at all -> the exact
                                   `merge_jugador05` bug class. Always
                                   forced here regardless of how good the
                                   name match looks.
  4_ambiguous_multi_candidate   - more than one candidate's birth data
                                   agrees (or none have birth data and more
                                   than one name-shape candidate exists).
  5_no_canonical_match          - no candidate at all: a real new-player
                                   mint proposal (the roster-completeness
                                   gap this whole ingest exists to close).

Name matching mirrors `merge_jug05`'s own two-tier design (exact
order/hyphen-insensitive `norm_key`, then a family-surname-prefix +
given-name-first-token fallback for a dropped maternal surname etc.) —
reused directly from `src.parse_players`, not reimplemented, so this
source is held to the same bar as every other one already in the spine.

Run: `python -m src.match_latinbasket_roster <franchise_id> [<franchise_id> ...]`
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict

from src.parse_players import CLEAN_DIR, INTERIM_DIR, normalize, norm_key, _load_club_resolver
from src.wayback_cdx import REPO_ROOT

ROSTER_RAW = INTERIM_DIR / "latinbasket_roster_raw.csv"
FETCH_MANIFEST = INTERIM_DIR / "fetch_manifest_latinbasket_roster.csv"

TIER_ORDER = [
    "1_exact_birth_confirmed",
    "2_approx_birth_confirmed",
    "3_no_birth_data_name_shape",
    "4_ambiguous_multi_candidate",
    "5_no_canonical_match",
]


def _full_birth_year(yy: str, season: int) -> int | None:
    """2-digit source year -> a real 4-digit year, choosing whichever
    century keeps the player's age at a plausible pro-athlete 14-55 for
    this season. Never guesses when neither (or both, tied) century is
    plausible -> returns None rather than a fabricated pick (PC1)."""
    if not yy or not yy.isdigit():
        return None
    yy_i = int(yy)
    options = [1900 + yy_i, 2000 + yy_i]
    plausible = [y for y in options if 14 <= season - y <= 55]
    if len(plausible) == 1:
        return plausible[0]
    if len(plausible) == 2:
        return min(plausible, key=lambda y: abs((season - y) - 27))
    return None


def _load_canon() -> list[dict]:
    with (CLEAN_DIR / "players_canonical.csv").open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _load_career() -> list[dict]:
    with (CLEAN_DIR / "player_career_seasons.csv").open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _load_aliases() -> list[dict]:
    with (CLEAN_DIR / "player_aliases.csv").open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _build_indexes(canon: list[dict]):
    """Real gap found and fixed 2026-09-14 (capitanes_arecibo batch):
    this used to only index `canonical_name` for exact matching, never
    `data/clean/player_aliases.csv` - a 24k-row table this archive's own
    pipeline already maintains for exactly this problem (spelling variants,
    initials, given/family reordering). Confirmed directly: "Cortez, David"
    is a known alias of id 448 (Cortes Ruiz, David) from an earlier-session
    jug05 merge, and a latinbasket "Cortez David"/"David Cortez" sighting
    here was landing as a false no-match purely because the matcher never
    looked at the alias table at all. Aliases only ever add recall (they
    are pre-vetted name strings for a real id, never a new candidate cause
    for concern) so folding them into the same `exact` index is safe."""
    exact: dict[str, list[dict]] = defaultdict(list)
    byfam: dict[str, list[dict]] = defaultdict(list)
    by_id = {c["bsnpr_id"]: c for c in canon}
    for c in canon:
        exact[norm_key(c["canonical_name"])].append(c)
        fam = normalize(c["apellidos"]).split()
        if fam:
            byfam[fam[0]].append(c)
    for a in _load_aliases():
        c = by_id.get(a["bsnpr_id"])
        if not c:
            continue
        key = norm_key(a["alias"])
        if c not in exact[key]:
            exact[key].append(c)
    return exact, byfam


def _family_candidates(byfam, jfam: list[str], jgiv: list[str]) -> list[dict]:
    """Same shape as `merge_jug05._family_name_candidates` — surname-prefix
    (either direction, handles a dropped/added maternal surname) + given
    name's first token. Never used to auto-accept, only to propose."""
    out = []
    for c in byfam.get(jfam[0], []):
        cfam, cgiv = normalize(c["apellidos"]).split(), normalize(c["nombre"]).split()
        if not cfam or not cgiv:
            continue
        if cfam[:len(jfam)] != jfam and jfam[:len(cfam)] != cfam:
            continue
        # jgiv[0] anywhere in cgiv, not just cgiv[0]: a source can render
        # only a secondary given name/nickname (e.g. "Berdiel Ali" for the
        # real "Berdiel Aponte, Miguel Ali") - found 2026-09-14
        # (atleticos_san_german batch) via an exact birth-year match this
        # first-token-only check was silently missing.
        if jgiv[0] not in cgiv:
            continue
        out.append(c)
    return out


def _name_split_candidates(byfam, name_raw: str, name_order: str) -> list[dict]:
    """Try every plausible surname/given-name split point (Spanish naming
    order is not reliably 2-token, D1) and union whatever the family-tier
    finds at each — a real split will surface real candidates; a wrong
    split simply finds nothing more."""
    tokens = [t for t in normalize(name_raw).split() if t]
    if len(tokens) < 2:
        return []
    found: dict[str, dict] = {}
    for k in range(1, len(tokens)):
        if name_order == "surname_first":
            jfam, jgiv = tokens[:len(tokens) - k], tokens[len(tokens) - k:]
        else:
            jgiv, jfam = tokens[:k], tokens[k:]
        if not jfam or not jgiv:
            continue
        for c in _family_candidates(byfam, jfam, jgiv):
            found[c["bsnpr_id"]] = c
    return list(found.values())


def find_candidates(exact, byfam, name_raw: str, name_order: str) -> tuple[list[dict], str]:
    key = norm_key(name_raw)
    if exact.get(key):
        return exact[key], "exact_name"
    fam = _name_split_candidates(byfam, name_raw, name_order)
    if fam:
        return fam, "partial_name"
    return [], "no_match"


def classify_row(row: dict, candidates: list[dict], match_kind: str) -> dict:
    """**Real messaging bug, found and fixed 2026-09-14 (piratas_quebradillas
    batch)**: the two distinct reasons a row can't be confirmed on birth
    data were conflated under one "canonical record has no birth_year"
    note - checked against `players_canonical.csv` directly and found
    several already-reported rows (e.g. id `2560 Ramirez Rivera, Luis S.`,
    birth_year=1986 on file) where the note was simply wrong: the
    *source* row (a `photo_strip`/bench-only entry) had no age/birth
    signal of its own to compare, the canonical record was fine. Doesn't
    change any outcome (both cases still force review, never auto-accept)
    but the owner was being told the wrong reason. Fixed by checking
    source-side signal presence before ever looking at candidates."""
    season = int(row["season"])
    exact_birth = _full_birth_year(row["birth_year_2digit"], season) if row["birth_year_2digit"] else None
    approx_birth = int(row["approx_birth_year"]) if row["approx_birth_year"] else None
    has_source_signal = exact_birth is not None or approx_birth is not None

    if not candidates:
        return {"tier": "5_no_canonical_match", "candidate_ids": "", "candidate_names": "",
                "note": "no existing canonical player matches this name shape at all "
                        "-> new-player mint proposal"}

    def _fmt(cs):
        return "; ".join(f'{c["bsnpr_id"]} {c["canonical_name"]}' for c in cs)

    if not has_source_signal:
        # Can't compare against ANY candidate regardless of what they have on
        # file - a property of this row, not of any one candidate.
        if len(candidates) == 1:
            c = candidates[0]
            has_canon_birth = bool(c.get("birth_year"))
            return {"tier": "3_no_birth_data_name_shape", "candidate_ids": c["bsnpr_id"],
                    "candidate_names": c["canonical_name"],
                    "note": ("name-shape match only; this source row has no age/birth signal of its "
                              "own to compare (a photo_strip/bench-only entry)"
                              + (f" - canon does have birth_year={c['birth_year']} on file, just "
                                 f"nothing on this row to check it against" if has_canon_birth else
                                 " and the canonical record has no birth_year either (the "
                                 "merge_jugador05 bug class)") + " - never auto-accept")}
        return {"tier": "4_ambiguous_multi_candidate", "candidate_ids": ";".join(c["bsnpr_id"] for c in candidates),
                "candidate_names": _fmt(candidates),
                "note": "multiple name-shape candidates and this source row has no age/birth signal "
                        "of its own to pick between them - needs manual review"}

    agreeing, no_birth_data, disagreeing = [], [], []
    for c in candidates:
        cby = int(c["birth_year"]) if c.get("birth_year") else None
        if cby is None:
            no_birth_data.append(c)
        elif exact_birth is not None:
            (agreeing if cby == exact_birth else disagreeing).append(c)
        else:
            (agreeing if abs(cby - approx_birth) <= 1 else disagreeing).append(c)

    if len(agreeing) == 1:
        tier = "1_exact_birth_confirmed" if exact_birth is not None else "2_approx_birth_confirmed"
        return {"tier": tier, "candidate_ids": agreeing[0]["bsnpr_id"],
                "candidate_names": agreeing[0]["canonical_name"],
                "note": f"{match_kind}, birth year agrees"
                        + (f" (source ~{approx_birth}, canon {agreeing[0]['birth_year']}, "
                           f"age-derived +/-1)" if exact_birth is None else "")}
    if len(agreeing) > 1:
        return {"tier": "4_ambiguous_multi_candidate", "candidate_ids": ";".join(c["bsnpr_id"] for c in agreeing),
                "candidate_names": _fmt(agreeing),
                "note": "multiple candidates all agree on birth year - needs manual pick"}
    if len(no_birth_data) == 1 and not disagreeing:
        return {"tier": "3_no_birth_data_name_shape", "candidate_ids": no_birth_data[0]["bsnpr_id"],
                "candidate_names": no_birth_data[0]["canonical_name"],
                "note": "name-shape match only, canonical record has no birth_year to confirm "
                        "or reject with (the merge_jugador05 bug class) - never auto-accept"}
    if len(no_birth_data) > 1 and not disagreeing:
        return {"tier": "4_ambiguous_multi_candidate", "candidate_ids": ";".join(c["bsnpr_id"] for c in no_birth_data),
                "candidate_names": _fmt(no_birth_data),
                "note": "multiple name-shape candidates, none has a birth_year to pick between them "
                        "- needs manual review, not just confirmation of one"}
    if no_birth_data and disagreeing:
        return {"tier": "4_ambiguous_multi_candidate",
                "candidate_ids": ";".join(c["bsnpr_id"] for c in no_birth_data + disagreeing),
                "candidate_names": _fmt(no_birth_data + disagreeing),
                "note": "mixed signal: some name-shape candidates have no birth data, "
                        "others actively disagree - needs manual review"}
    # everyone with a name-shape match actively disagrees on birth year
    return {"tier": "5_no_canonical_match",
            "candidate_ids": "", "candidate_names": "",
            "note": f"name-shape candidate(s) exist but birth year contradicts all of them "
                    f"({_fmt(disagreeing)}) - treated as a different person, new-player mint proposal"}


def _existing_career_overlap(career_index, bsnpr_id: str, franchise_id: str, season: int) -> str:
    return "yes" if (bsnpr_id, franchise_id, season) in career_index else "no"


def build_career_index(career: list[dict], resolve_club) -> set[tuple[str, str, int]]:
    idx = set()
    for r in career:
        fid = resolve_club(r["team_raw"])
        if not fid or not r["season"].isdigit():
            continue
        idx.add((r["bsnpr_id"], fid, int(r["season"])))
    return idx


def load_franchise_page_status(franchise_id: str) -> dict[str, str]:
    """(franchise_id, season) -> 'has_data' | 'no_data' (page fetched fine
    but zero player content), from the fetch manifest vs the parsed raw
    CSV. Keeps a genuinely empty page from ever reading as a franchise-
    season with zero *matched* players in the batch report (owner
    requirement) - it's a data gap, not a match-quality result."""
    fetched_seasons = set()
    with FETCH_MANIFEST.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["franchise_id"] == franchise_id and r["status"] == "ok":
                fetched_seasons.add(r["season"])
    parsed_seasons = set()
    with ROSTER_RAW.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["franchise_id"] == franchise_id:
                parsed_seasons.add(r["season"])
    return {s: ("has_data" if s in parsed_seasons else "no_data") for s in fetched_seasons}


def _load_prior_dispositions(out_path) -> dict[tuple[str, str], tuple[str, str]]:
    """(season, name_raw) -> (disposition, disposition_note) from a
    previous run of this same batch, so re-running the matcher (e.g. after
    a logic change) never silently erases an owner's adjudication - that
    has to be a deliberate re-review, not a side effect of a rerun."""
    prior: dict[tuple[str, str], tuple[str, str]] = {}
    if not out_path.exists():
        return prior
    with out_path.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r.get("disposition"):
                prior[(r["season"], r["name_raw"])] = (r["disposition"], r.get("disposition_note", ""))
    return prior


def run_batch(franchise_id: str) -> None:
    canon = _load_canon()
    career = _load_career()
    exact, byfam = _build_indexes(canon)
    resolve_club = _load_club_resolver()
    career_index = build_career_index(career, resolve_club)

    out_path = INTERIM_DIR / f"latinbasket_match_{franchise_id}.csv"
    prior_dispositions = _load_prior_dispositions(out_path)

    page_status = load_franchise_page_status(franchise_id)
    no_data_seasons = sorted(s for s, v in page_status.items() if v == "no_data")

    with ROSTER_RAW.open(encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if r["franchise_id"] == franchise_id]

    out_rows = []
    tier_counts: dict[str, int] = defaultdict(int)
    for row in rows:
        candidates, match_kind = find_candidates(exact, byfam, row["name_raw"], row["name_order"])
        result = classify_row(row, candidates, match_kind)
        tier_counts[result["tier"]] += 1
        overlap = ""
        if result["candidate_ids"] and ";" not in result["candidate_ids"]:
            overlap = _existing_career_overlap(career_index, result["candidate_ids"],
                                                franchise_id, int(row["season"]))
        disposition, disposition_note = prior_dispositions.get((row["season"], row["name_raw"]), ("", ""))
        out_rows.append({
            "franchise_id": franchise_id, "season": row["season"], "season_source": row["season_source"],
            "template": row["template"], "completeness": row["completeness"],
            "name_raw": row["name_raw"], "name_order": row["name_order"],
            "birth_year_2digit": row["birth_year_2digit"], "age": row["age"],
            "approx_birth_year": row["approx_birth_year"],
            "tier": result["tier"], "candidate_ids": result["candidate_ids"],
            "candidate_names": result["candidate_names"],
            "already_has_season_row": overlap, "note": result["note"],
            "disposition": disposition, "disposition_note": disposition_note,
        })

    out_rows.sort(key=lambda r: (TIER_ORDER.index(r["tier"]), r["season"], r["name_raw"]))
    fieldnames = ["franchise_id", "season", "season_source", "template", "completeness",
                  "name_raw", "name_order", "birth_year_2digit", "age", "approx_birth_year",
                  "tier", "candidate_ids", "candidate_names", "already_has_season_row", "note",
                  "disposition", "disposition_note"]
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(out_rows)

    has_data_seasons = sorted(s for s in page_status if page_status[s] == "has_data")
    print(f"=== {franchise_id} ===")
    print(f"seasons with real roster data: {has_data_seasons}")
    if no_data_seasons:
        print(f"seasons with NO DATA (page fetched, zero player content - excluded above, "
              f"not a 0-match result): {no_data_seasons}")
    print(f"{len(out_rows)} roster rows classified:")
    for t in TIER_ORDER:
        if tier_counts[t]:
            print(f"  {t}: {tier_counts[t]}")
    print(f"-> {out_path.relative_to(REPO_ROOT)}")
    print()


def set_disposition(franchise_id: str, season: str, name_raw: str, disposition: str, note: str = "") -> bool:
    """Records the owner's adjudication on one row of an already-generated
    batch file in place. Never called automatically - an adjudication is a
    human decision, not something this script infers. Returns False if no
    matching row was found (a typo'd name/season, not silently ignored)."""
    out_path = INTERIM_DIR / f"latinbasket_match_{franchise_id}.csv"
    rows = list(csv.DictReader(out_path.open(encoding="utf-8")))
    found = False
    for r in rows:
        if r["season"] == season and r["name_raw"] == name_raw:
            r["disposition"] = disposition
            r["disposition_note"] = note
            found = True
    if found:
        with out_path.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    return found


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: python -m src.match_latinbasket_roster <franchise_id> [...]\n"
              "       python -m src.match_latinbasket_roster --set <franchise_id> <season> "
              "<name_raw> <disposition> [note]", file=sys.stderr)
        return 1
    if argv[0] == "--set":
        fid, season, name_raw, disposition = argv[1], argv[2], argv[3], argv[4]
        note = argv[5] if len(argv) > 5 else ""
        if not set_disposition(fid, season, name_raw, disposition, note):
            print(f"no row found for {fid}/{season}/{name_raw!r}", file=sys.stderr)
            return 1
        return 0
    for fid in argv:
        run_batch(fid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
