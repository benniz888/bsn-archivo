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


def main() -> int:
    c = Checker()
    verify_champions(c)
    verify_leaders(c)
    verify_stats_tracked(c)
    verify_coverage_gaps(c)
    verify_pre2007(c)
    rc = c.report()
    print("verify:", "PASS" if rc == 0 else "FAIL")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
