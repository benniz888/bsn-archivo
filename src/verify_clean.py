"""PHASE_3_PARSE verification — integrity checks over the parsed data/clean/
outputs. Read-only. Exits non-zero if any check fails (V-loop, global [V1–V5]).

Run: `python -m src.verify_clean`   (`make verify`)
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

from src.wayback_cdx import REPO_ROOT
from src.parse_wayback import CLEAN_CATEGORIES, KNOWN_LEADER_SEASONS

CLEAN_DIR = REPO_ROOT / "data" / "clean"
CONFIDENCE_OK = {"verified", "single-source", "disputed"}
PROVENANCE_COLS = ("confidence", "source_id", "source_url", "retrieved_at")


def _read(name: str) -> list[dict]:
    with (CLEAN_DIR / name).open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


class Checker:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.checks = 0

    def check(self, ok: bool, label: str, detail: str = "") -> None:
        self.checks += 1
        if not ok:
            self.failures.append(f"{label}{f' — {detail}' if detail else ''}")

    def report(self) -> int:
        print(f"\n{self.checks} checks, {len(self.failures)} failed")
        for f in self.failures:
            print(f"  FAIL: {f}")
        return 1 if self.failures else 0


def verify_champions(c: Checker) -> None:
    rows = _read("champions_from_bsnpr.csv")
    c.check(bool(rows), "champions: non-empty")

    seasons = [r["season"] for r in rows]
    c.check(len(seasons) == len(set(seasons)), "champions: one row per season",
            f"{len(seasons) - len(set(seasons))} dup seasons")
    c.check(all(re.fullmatch(r"\d{4}(-\d{4})?", s) for s in seasons),
            "champions: season keys are YYYY or YYYY-YYYY (D3 split season)")

    for r in rows:
        tag = f"season {r['season']}"
        for col in PROVENANCE_COLS:
            c.check(bool(r[col]), f"champions: {tag} has {col}")
        c.check(r["confidence"] in CONFIDENCE_OK, f"champions: {tag} confidence valid", r["confidence"])
        if r["no_champion"] == "True":
            c.check(not r["champion_city"] and not r["runner_up_city"],
                    f"champions: {tag} no_champion row has empty champion/runner-up")
            c.check(bool(r["note"]), f"champions: {tag} no_champion row explains why")
        else:
            c.check(bool(r["champion_city"]), f"champions: {tag} has a champion city")
            c.check(r["champion_city"] != r["runner_up_city"] or not r["runner_up_city"],
                    f"champions: {tag} champion != runner-up")

    by_season = {r["season"]: r for r in rows}
    c.check("1953" in by_season and by_season["1953"]["no_champion"] == "True",
            "champions: 1953 carried as no-champion (D6)")
    c.check("1945" in by_season and by_season["1945"]["confidence"] == "disputed",
            "champions: 1945 flagged disputed (D5)")
    c.check("1942" in by_season and "1942-1943" in by_season,
            "champions: 1942 and 1942-1943 both present as distinct keys (D3)")


def verify_leaders(c: Checker) -> None:
    rows = _read("player_season_leaders.csv")
    c.check(bool(rows), "leaders: non-empty")

    seasons = {r["season"] for r in rows}
    c.check(seasons <= KNOWN_LEADER_SEASONS, "leaders: seasons within archived range",
            f"unexpected: {sorted(seasons - KNOWN_LEADER_SEASONS)}")
    c.check(all(cat in CLEAN_CATEGORIES for cat in {r["category"] for r in rows}),
            "leaders: only known categories")

    groups: dict[tuple[str, str], list[dict]] = {}
    for r in rows:
        groups.setdefault((r["season"], r["category"]), []).append(r)

    for (season, category), grp in groups.items():
        tag = f"{season}/{category}"
        ranks = sorted(int(r["rank"]) for r in grp if r["rank"])
        c.check(ranks == list(range(1, len(ranks) + 1)), f"leaders: {tag} ranks contiguous from 1", str(ranks))
        c.check(all(r["player_raw"] for r in grp), f"leaders: {tag} every row has player_raw")
        c.check(all(r["prom"] for r in grp), f"leaders: {tag} every row has prom")
        c.check(len({r["capture_date"] for r in grp}) == 1, f"leaders: {tag} one source capture")
        for r in grp:
            for col in PROVENANCE_COLS:
                c.check(bool(r[col]), f"leaders: {tag} rank {r['rank']} has {col}")
        # NULL != 0 (PC2): the percentage categories must not carry a counting total
        if category in ("tiros_libres_pct", "canastos_3_pct"):
            c.check(all(not r["total"] for r in grp), f"leaders: {tag} pct rows carry made/attempted, not total")
            c.check(all(r["made"] and r["attempted"] for r in grp), f"leaders: {tag} pct rows have made+attempted")


def verify_stats_tracked(c: Checker) -> None:
    rows = _read("seasons_stats_tracked.csv")
    c.check(bool(rows), "stats_tracked: non-empty")
    for r in rows:
        for cat in CLEAN_CATEGORIES:
            c.check(r[cat] in ("0", "1", ""), f"stats_tracked: {r['season']}/{cat} is 0/1/blank", r[cat])
    by_season = {r["season"]: r for r in rows}
    if "1986" in by_season:
        # spec [DECISION] 5 / project D-rules: 1986 did not track blocks, steals,
        # turnovers or offensive rebounds — the empty tables are the signal.
        for cat in ("bloqueos", "cortes_balon", "turnovers", "rebotes_ofensivos"):
            c.check(by_season["1986"][cat] == "0", f"stats_tracked: 1986/{cat} == 0 (era signal)")
        c.check(by_season["1986"]["anotaciones"] == "1", "stats_tracked: 1986/anotaciones == 1")


def verify_coverage_gaps(c: Checker) -> None:
    rows = _read("leader_coverage_gaps.csv")
    covered = {r["season"] for r in rows}
    c.check(covered == KNOWN_LEADER_SEASONS, "gaps: every archived season accounted for",
            f"missing {sorted(KNOWN_LEADER_SEASONS - covered)}")
    c.check(all(r["status"] in ("regular_season", "playoff_only", "not_archived") for r in rows),
            "gaps: status values valid")
    leader_seasons = {r["season"] for r in _read("player_season_leaders.csv")}
    for r in rows:
        if r["status"] == "regular_season":
            c.check(r["season"] in leader_seasons, f"gaps: {r['season']} regular_season has leader rows")
        else:
            c.check(r["season"] not in leader_seasons, f"gaps: {r['season']} {r['status']} has no leader rows")


def verify_pre2007(c: Checker) -> None:
    """PHASE_3C outputs. Skipped cleanly if the parse has not been run."""
    if not (CLEAN_DIR / "historic_scoring_champions.csv").exists():
        return

    scoring = _read("historic_scoring_champions.csv")
    c.check(bool(scoring), "historic_scoring: non-empty")
    seasons = [int(r["season"]) for r in scoring]
    c.check(min(seasons) <= 1950 and max(seasons) >= 2003,
            "historic_scoring: spans ~1948-2004", f"{min(seasons)}-{max(seasons)}")
    for r in scoring:
        tag = f"scoring {r['season']}"
        for col in PROVENANCE_COLS:
            c.check(bool(r[col]), f"historic_scoring: {tag} has {col}")
        c.check(r["confidence"] in CONFIDENCE_OK, f"historic_scoring: {tag} confidence valid")
        c.check(bool(r["player_raw"]), f"historic_scoring: {tag} has player_raw")
        # D4: metric_era must flip at the 1970/71 boundary
        want = "total_points" if int(r["season"]) <= 1970 else "ppg"
        c.check(r["metric_era"] == want, f"historic_scoring: {tag} metric_era == {want} (D4)")
    dyears = [r["season"] for r in scoring if r["confidence"] == "disputed"]
    c.check("1952" in dyears, "historic_scoring: 1952 Feliciano/Santori carried disputed")
    c.check(sum(1 for r in scoring if r["season"] == "1952") == 2,
            "historic_scoring: 1952 has both claimants as rows (PC1)")

    awards = _read("historic_awards.csv")
    c.check({r["award"] for r in awards} <= {"mvp", "rookie", "defensive_player"},
            "historic_awards: known award types only")
    for r in awards:
        for col in PROVENANCE_COLS:
            c.check(bool(r[col]), f"historic_awards: {r['award']} {r['season']} has {col}")

    players = _read("player_season_stats_2001_2004.csv")
    c.check(bool(players), "player_stats_2001_2004: non-empty")
    for r in players:
        tag = f"{r['team_raw']} {r['season']} {r['player_raw']}"
        for col in PROVENANCE_COLS:
            c.check(bool(r[col]), f"player_stats: {tag} has {col}")
        c.check(bool(r["player_raw"]) and r["player_raw"].lower() != "totales",
                f"player_stats: {tag} is a real player row")
        # made <= attempted where both present (PC2: blanks stay blank)
        for made, att, lbl in (("fgm", "fga", "FG"), ("tpm", "tpa", "3P"), ("ftm", "fta", "FT")):
            if r[made] and r[att]:
                c.check(int(r[made]) <= int(r[att]), f"player_stats: {tag} {lbl} made<=att",
                        f"{r[made]}/{r[att]}")
    c.check({r["season"] for r in players} <= {"2000", "2001", "2002", "2003", "2004"},
            "player_stats: seasons in 2000-2004")

    if (CLEAN_DIR / "player_season_leaders_2000_2002.csv").exists():
        lead = _read("player_season_leaders_2000_2002.csv")
        c.check(bool(lead), "leaders_2000_2002: non-empty")
        c.check({r["season"] for r in lead} == {"2000", "2001", "2002"},
                "leaders_2000_2002: exactly seasons 2000-2002")
        groups: dict[tuple, list[dict]] = {}
        for r in lead:
            groups.setdefault((r["season"], r["category"], r["serie"]), []).append(r)
        for k, grp in groups.items():
            ranks = sorted(int(r["rank"]) for r in grp if r["rank"])
            c.check(ranks == list(range(1, len(ranks) + 1)),
                    f"leaders_2000_2002: {k} ranks contiguous from 1")
            for r in grp:
                for col in PROVENANCE_COLS:
                    c.check(bool(r[col]), f"leaders_2000_2002: {k} r{r['rank']} has {col}")
                c.check(bool(r["player_raw"]), f"leaders_2000_2002: {k} r{r['rank']} has player_raw")


def verify_players(c: Checker) -> None:
    """PHASE_3D identity spine. Skipped cleanly if not built."""
    if not (CLEAN_DIR / "players_canonical.csv").exists():
        return
    canon = _read("players_canonical.csv")
    c.check(bool(canon), "players_canonical: non-empty")

    ids = [r["bsnpr_id"] for r in canon]
    c.check(len(ids) == len(set(ids)), "players_canonical: bsnpr_id unique")
    c.check(all(i.isdigit() for i in ids), "players_canonical: bsnpr_id all integer")
    for r in canon:
        tag = f"id {r['bsnpr_id']}"
        c.check(bool(r["canonical_name"]), f"players_canonical: {tag} has canonical_name")
        c.check(r["normalized_name"] == r["normalized_name"].lower(),
                f"players_canonical: {tag} normalized_name is lowercase")
        # normalized_name must be accent-free (D1)
        c.check(not any(ord(ch) > 127 for ch in r["normalized_name"]),
                f"players_canonical: {tag} normalized_name accent-stripped", r["normalized_name"])
        for col in ("confidence", "source_id", "source_url", "retrieved_at"):
            c.check(bool(r[col]), f"players_canonical: {tag} has {col}")
        if r["birth_year"]:
            c.check(re.fullmatch(r"\d{4}", r["birth_year"]) and 1920 <= int(r["birth_year"]) <= 2010,
                    f"players_canonical: {tag} birth_year plausible", r["birth_year"])
        if r["first_season"] and r["last_season"]:
            c.check(int(r["first_season"]) <= int(r["last_season"]),
                    f"players_canonical: {tag} first_season <= last_season")

    aliases = _read("player_aliases.csv")
    canon_ids = set(ids)
    c.check(all(a["bsnpr_id"] in canon_ids for a in aliases),
            "player_aliases: every alias points at a canonical id")
    c.check(all(a["alias_type"] and a["normalized_alias"] for a in aliases),
            "player_aliases: every row has alias_type + normalized_alias")
    c.check(not any(ord(ch) > 127 for a in aliases for ch in a["normalized_alias"]),
            "player_aliases: normalized_alias accent-stripped (D1)")

    idmap = _read("player_id_map.csv")
    c.check(all(m["bsnpr_id"] in canon_ids for m in idmap),
            "player_id_map: every mapping points at a canonical id")
    # D1: nothing in the id map may be a bare name match — method must name its corroboration
    c.check(all("season" in m["match_method"] or "birth" in m["match_method"] for m in idmap),
            "player_id_map: every match is corroborated beyond the name (D1)")
    c.check(all(m["confidence"] in CONFIDENCE_OK for m in idmap),
            "player_id_map: confidence values valid")

    review = _read_interim("player_review_queue.csv")
    c.check(all(r["reason"] for r in review), "review_queue: every row states a reason")
    # a (source, player_raw, season) is either mapped or in review — never both
    mapped_keys = {(m["obs_source"], m["player_raw"], m["club_raw"], m["season"]) for m in idmap}
    review_keys = {(r["obs_source"], r["player_raw"], r["club_raw"], r["season"]) for r in review}
    c.check(not (mapped_keys & review_keys),
            "player_id_map / review_queue: no observation is both mapped and queued",
            f"{len(mapped_keys & review_keys)} overlap")


def _read_interim(name: str) -> list[dict]:
    with (REPO_ROOT / "data" / "interim" / name).open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def verify_games(c: Checker) -> None:
    """PHASE_3E box scores. Skipped cleanly if not built."""
    if not (CLEAN_DIR / "game_box_player.csv").exists():
        return
    box = _read("game_box_player.csv")
    c.check(bool(box), "game_box_player: non-empty")

    canon_ids = set()
    if (CLEAN_DIR / "players_canonical.csv").exists():
        canon_ids = {r["bsnpr_id"] for r in _read("players_canonical.csv")}

    bad_pts = bad_att = 0
    for r in box:
        for col in ("confidence", "source_id", "source_url", "retrieved_at"):
            c.check(bool(r[col]), f"game_box: {r['game_id']} {r['player_raw']} has {col}")
        c.check(bool(r["player_raw"]) and not r["player_raw"].lower().startswith("total"),
                f"game_box: {r['game_id']} row is a real player")
        if r["bsnpr_id"]:
            c.check(r["bsnpr_id"] in canon_ids or not canon_ids,
                    f"game_box: {r['game_id']} bsnpr_id is a real canonical id", r["bsnpr_id"])
        # box-score arithmetic (all cells present)
        if all(r[k] for k in ("fg2m", "fg3m", "ftm", "pts")):
            if int(r["fg2m"]) * 2 + int(r["fg3m"]) * 3 + int(r["ftm"]) != int(r["pts"]):
                bad_pts += 1
        for m, a in (("fg2m", "fg2a"), ("fg3m", "fg3a"), ("ftm", "fta")):
            if r[m] and r[a] and int(r[m]) > int(r[a]):
                bad_att += 1
    c.check(bad_pts == 0, "game_box: 2·FG2 + 3·FG3 + FT == PTS on every full row", f"{bad_pts} bad")
    c.check(bad_att == 0, "game_box: made <= attempted on every full shot line", f"{bad_att} bad")

    res = _read("game_results.csv")
    for r in res:
        c.check(r["team_a_raw"] and r["team_b_raw"] and r["score_a"] and r["score_b"],
                f"game_results: {r['game_id']} has both teams + scores")
    box_games = {r["game_id"] for r in box}
    res_games = {r["game_id"] for r in res}
    c.check(box_games <= res_games or not res,
            "game_box: every game with player rows has a results row")


def verify_reconcile(c: Checker) -> None:
    """PHASE_4. Skipped cleanly if not built."""
    if not (CLEAN_DIR / "reconcile_conflicts.csv").exists():
        return

    fr = _read("franchises.csv")
    fids = {r["franchise_id"] for r in fr}
    c.check(len(fids) == len(fr), "franchises: franchise_id unique")

    conflicts = _read("reconcile_conflicts.csv")
    for r in conflicts:
        tag = f"{r['topic']}/{r['season']}"
        # a conflict names two sides, each with a source and a value, no winner
        c.check(r["source_a"] and r["value_a"] and r["source_b"] and r["value_b"],
                f"conflicts: {tag} has both sides populated")
        c.check(r["source_a"] != r["source_b"], f"conflicts: {tag} two distinct sources")
    ckeys = {(r["topic"], r["season"]) for r in conflicts}
    # after the owner's 2026-09-08 resolutions only 1945 remains a true conflict
    c.check(("champion", "1945") in ckeys, "conflicts: champion 1945 (D5) still flagged")
    for resolved in (("champion", "1936"), ("runner_up", "1968"),
                     ("scoring_champion", "1971"), ("scoring_champion", "1974")):
        c.check(resolved not in ckeys,
                f"conflicts: {resolved[0]} {resolved[1]} was resolved by the owner — not a conflict")

    ch = _read("champions_reconciled.csv")
    STATUSES = {"agree", "conflict", "seed_only", "bsnpr_only", "no_champion"}
    for r in ch:
        tag = f"champions {r['season']}"
        c.check(r["agreement"] in STATUSES, f"{tag}: agreement status valid", r["agreement"])
        for col in ("champion_franchise_id", "runner_up_franchise_id"):
            c.check(not r[col] or r[col] in fids, f"{tag}: {col} is a real franchise", r[col])
        if r["agreement"] == "agree":
            # verified unless an owner resolution assigned its own confidence
            c.check(r["confidence"] in ("verified", "single-source"),
                    f"{tag}: agree row has a valid confidence", r["confidence"])
            if "OWNER" in r["note"]:
                c.check("2026-09-08" in r["note"], f"{tag}: owner resolution is dated")
        if r["agreement"] == "conflict":
            c.check(r["confidence"] == "disputed", f"{tag}: conflict -> disputed")
            c.check(bool(r["note"]), f"{tag}: conflict row explains the disagreement")
    by_season = {r["season"]: r for r in ch}
    c.check(by_season.get("1953", {}).get("agreement") == "no_champion",
            "champions: 1953 reconciled as no_champion (D6)")
    c.check("1942-1943" in by_season and by_season["1942-1943"]["agreement"] == "bsnpr_only",
            "champions: 1942-1943 kept as a distinct bsnpr_only row (D3)")

    sc = _read("scoring_champions_reconciled.csv")
    SC_ST = {"agree", "conflict", "seed_only", "historic_only", "leaders_only",
             "none", "dual_metric_d4"}
    for r in sc:
        c.check(r["agreement"] in SC_ST, f"scoring {r['season']}: agreement status valid", r["agreement"])
        want = "total_points" if int(r["season"]) <= 1970 else "ppg"
        c.check(r["metric_era"] == want, f"scoring {r['season']}: metric_era == {want} (D4)")
        if r["agreement"] == "dual_metric_d4":
            c.check(r["ppg_champion"] and r["total_points_champion"],
                    f"scoring {r['season']}: dual_metric row records both champions")
    by_sc = {r["season"]: r for r in sc}
    for yr in ("1971", "1974"):
        c.check(by_sc.get(yr, {}).get("agreement") == "dual_metric_d4",
                f"scoring {yr}: owner-resolved to dual_metric_d4 (D4 boundary)")


def main() -> int:
    c = Checker()
    verify_champions(c)
    verify_leaders(c)
    verify_stats_tracked(c)
    verify_coverage_gaps(c)
    verify_pre2007(c)
    verify_players(c)
    verify_reconcile(c)
    verify_games(c)
    rc = c.report()
    print("verify:", "PASS" if rc == 0 else "FAIL")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
