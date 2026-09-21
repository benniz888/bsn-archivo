"""jug05 season totals (docs/specs/jug05_sumrow_check.md). A jug05 row that equals the SUM of the players-source
rows of the same player-season is corroboration of the season, not a conflict: it is folded out and logged, the
per-team rows stay. Fixture tests pin the rule and the script; TestCommittedData pins the committed numbers
(13 folded; career CSV 5,678 after the 5 foreign rows of tests/test_jug05_foreign_rows.py, conflicts 94 on 71
players, merged 767, trade pairs 241 after J16b)."""

import csv

from src import apply_jug05_season_totals as apply
from src import parse_players as pp
from src.parse_players import (JUG05_SOURCE_ID, SEASON_TOTALS_COLUMNS, SOURCE_ID, fold_cross_source_career,
                               fold_season_totals, write_season_totals_log)
from src.wayback_cdx import REPO_ROOT


def _row(pid, season, team, games, points, source=SOURCE_ID):
    return {"bsnpr_id": str(pid), "season": str(season), "team_raw": team, "games": str(games), "points": str(points),
            "source_id": source, "source_url": f"http://wb/{source}/{pid}", "retrieved_at": "t"}


def _jug(pid, season, team, games, points):
    return _row(pid, season, team, games, points, source=JUG05_SOURCE_ID)


TWO_TEAMS = [_row(1995, 2006, "Criollos, Caguas", 5, 39), _row(1995, 2006, "Vaqueros, Bayamon", 19, 155)]


class TestRule:
    def test_a_jug05_row_equal_to_the_sum_of_two_team_rows_is_a_season_total(self):
        rows = TWO_TEAMS + [_jug(1995, 2006, "CAGUAS", 24, 194)]
        kept, totals = fold_season_totals(rows)
        assert kept == TWO_TEAMS                                                # the per-team rows stay
        assert len(totals) == 1 and list(totals[0]) == SEASON_TOTALS_COLUMNS
        t = totals[0]
        assert (t["bsnpr_id"], t["season"], t["jug05_team_raw"], t["jug05_games"], t["jug05_points"]) == ("1995", 2006, "CAGUAS", 24, 194)
        assert t["ficha_rows"] == "Criollos, Caguas 5/39 | Vaqueros, Bayamon 19/155"
        assert (t["ficha_games_sum"], t["ficha_points_sum"]) == (24, 194)

    def test_games_and_points_must_both_match(self):
        for g, p in ((24, 195), (25, 194)):
            rows = TWO_TEAMS + [_jug(1995, 2006, "CAGUAS", g, p)]
            assert fold_season_totals(rows)[0] == rows

    def test_one_team_row_is_not_a_sum(self):
        rows = [TWO_TEAMS[0], _jug(1995, 2006, "CAGUAS", 5, 39)]
        assert fold_season_totals(rows)[0] == rows                              # left to the ordinary fold: identical, merged

    def test_a_second_row_of_zero_zero_does_not_make_a_total(self):
        rows = [_row(1442, 2002, "Toritos, Cayey", 9, 154), _row(1442, 2002, "Atleticos, San German", 0, 0),
                _jug(1442, 2002, "CAYEY", 9, 154)]
        kept, totals = fold_season_totals(rows)
        assert kept == rows and totals == []
        again, merged, conflicts = fold_cross_source_career(kept)
        assert len(merged) == 1 and conflicts == [] and len(again) == 2         # it stays a merged pair

    def test_a_blank_figure_is_never_summed_as_zero(self):
        rows = [_row(1, 2006, "A", 5, ""), _row(1, 2006, "B", 19, 155), _jug(1, 2006, "A", 24, 155)]
        assert fold_season_totals(rows)[0] == rows

    def test_only_a_jug05_row_is_ever_folded_and_other_seasons_are_left_alone(self):
        rows = TWO_TEAMS + [_row(1995, 2006, "Total", 24, 194), _jug(1995, 2005, "CAGUAS", 24, 194)]
        assert fold_season_totals(rows)[0] == rows

    def test_the_input_is_not_mutated_and_a_second_pass_finds_nothing(self):
        rows = TWO_TEAMS + [_jug(1995, 2006, "CAGUAS", 24, 194)]
        before = [dict(r) for r in rows]
        kept, _ = fold_season_totals(rows)
        assert rows == before and fold_season_totals(kept)[1] == []

    def test_it_runs_before_the_fold_so_the_total_is_not_reported_as_a_conflict(self):
        rows = TWO_TEAMS + [_jug(1995, 2006, "CAGUAS", 24, 194)]
        assert len(fold_cross_source_career(rows)[2]) == 1                      # the per-team fold alone: a conflict
        kept, _ = fold_season_totals(rows)
        assert fold_cross_source_career(kept)[2] == []

    def test_the_log_is_history(self, tmp_path):
        _, totals = fold_season_totals(TWO_TEAMS + [_jug(1995, 2006, "CAGUAS", 24, 194)])
        write_season_totals_log(totals, interim_dir=tmp_path)
        first = (tmp_path / "jug05_season_totals.csv").read_bytes()
        write_season_totals_log([], interim_dir=tmp_path)                       # a second run folds nothing
        assert (tmp_path / "jug05_season_totals.csv").read_bytes() == first


def _rd(name, folder):
    with (REPO_ROOT / "data" / folder / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


class TestCommittedData:
    def test_13_season_totals_are_logged_with_the_rows_they_sum(self):
        log = _rd("jug05_season_totals.csv", "interim")
        assert len(log) == 13 and list(log[0]) == SEASON_TOTALS_COLUMNS
        assert sorted(int(r["bsnpr_id"]) for r in log) == [151, 193, 284, 763, 777, 808, 870, 932, 985, 1284, 1462, 1995, 2067]
        assert sum(1 for r in log if r["season"] == "2006") == 12 and sum(1 for r in log if r["season"] == "2005") == 1
        for r in log:
            assert (r["jug05_games"], r["jug05_points"]) == (r["ficha_games_sum"], r["ficha_points_sum"])
            assert len(r["ficha_rows"].split(" | ")) >= 2 and r["jug05_source_url"] and r["jug05_retrieved_at"]

    def test_the_career_csv_lost_those_13_rows_and_no_team_row(self):
        rows = _rd("player_career_seasons.csv", "clean")
        assert len(rows) == 5678                                                # 5,696 before the totals, then 5 foreign rows
        for t in _rd("jug05_season_totals.csv", "interim"):
            mine = [r for r in rows if r["bsnpr_id"] == t["bsnpr_id"] and r["season"] == t["season"]]
            assert not [r for r in mine if r["source_id"] == JUG05_SOURCE_ID and r["team_raw"] == t["jug05_team_raw"]]
            assert len([r for r in mine if r["source_id"] == SOURCE_ID]) >= 2

    def test_the_conflicts_are_94_on_71_players_and_the_merged_log_is_untouched(self):
        conflicts, merged = _rd("jug05_career_conflicts.csv", "interim"), _rd("jug05_career_merged.csv", "interim")
        assert len(conflicts) == 94 and len({c["bsnpr_id"] for c in conflicts}) == 71 and len(merged) == 767
        assert {"81", "1066"} <= {c["bsnpr_id"] for c in conflicts if c["season"] == "2006"}
        assert sum(1 for c in conflicts if c["season"] in ("2000", "2001", "2002", "2003")) == 89
        assert {("1442", "2002"), ("1512", "2000")} <= {(m["bsnpr_id"], m["season"]) for m in merged}

    def test_trade_pairs_are_241_after_cayey_was_mapped(self):   # 233 before J16b, 235 before the foreign rows
        rows = _rd("player_career_seasons.csv", "clean")
        site = pp._load_site_franchise_resolver()
        by_pair = {}
        for r in rows:
            fid = site(r["team_raw"], int(r["season"]))
            if fid:
                by_pair.setdefault((r["bsnpr_id"], r["season"]), set()).add(fid)
        assert sum(1 for f in by_pair.values() if len(f) >= 2) == 241

    def test_the_apply_script_finds_nothing_left_to_do(self):
        assert apply.main(["--check"]) == 0


class TestWiring:
    def test_merge_and_main_hand_the_season_totals_to_the_fold_and_the_writer(self):
        import inspect
        merge, main = inspect.getsource(pp.merge_jug05), inspect.getsource(pp.main)
        assert merge.index("fold_season_totals(kept)") < merge.index("fold_cross_source_career(kept)")
        assert 'j05["season_totals"]' in main and "write_season_totals_log(jug05_season_totals)" in main
