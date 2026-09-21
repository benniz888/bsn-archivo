"""jug05 rows that show ANOTHER player's line (docs/specs/foreign_slot_check.md). A hand-curated list with per-row
evidence (data/interim/jug05_foreign_lines.csv) says which published rows go; nothing is detected automatically.
Fixture tests pin the rule and the script; TestCommittedData pins the committed numbers (5 rows, 4 players, career CSV
5,678, trade pairs 233 then and 241 after J16b, the class b and c rows and the other 2005/2006 rows untouched)."""

import csv

from src import apply_jug05_foreign_rows as apply
from src import parse_players as pp
from src.parse_players import (FOREIGN_LOG_COLUMNS, JUG05_SOURCE_ID, SOURCE_ID, drop_foreign_rows, load_foreign_rows,
                               write_foreign_rows_log)
from src.wayback_cdx import REPO_ROOT


def _row(pid, season, team, games, points, source=JUG05_SOURCE_ID, url="http://wb/x"):
    return {"bsnpr_id": str(pid), "season": str(season), "team_raw": team, "games": str(games), "points": str(points),
            "source_id": source, "source_url": url, "retrieved_at": "t"}


def _listed(pid, season, team, games, points, url="http://wb/x"):
    return {"bsnpr_id": str(pid), "season": str(season), "team_raw": team, "games": str(games), "points": str(points),
            "source_url": url, "capture_date": "2006-09-17", "owner_id": "74", "owner_name": "Cruz Torres, Alvin",
            "evidence": "e", "evidence_es": "es"}


ROW = _row(4, 2006, "BAYAMON", 24, 211)


class TestRule:
    def test_a_listed_row_is_dropped_and_logged_with_its_evidence(self):
        kept, dropped = drop_foreign_rows([ROW, _row(4, 2004, "COAMO", 15, 10)], [_listed(4, 2006, "BAYAMON", 24, 211)])
        assert [r["season"] for r in kept] == ["2004"]
        assert len(dropped) == 1 and list(dropped[0]) == FOREIGN_LOG_COLUMNS
        d = dropped[0]
        assert (d["bsnpr_id"], d["season"], d["games"], d["points"], d["owner_id"], d["retrieved_at"]) == ("4", 2006, "24", "211", "74", "t")

    def test_every_part_of_the_key_must_match(self):
        for other in (_listed(5, 2006, "BAYAMON", 24, 211), _listed(4, 2005, "BAYAMON", 24, 211), _listed(4, 2006, "PONCE", 24, 211),
                      _listed(4, 2006, "BAYAMON", 25, 211), _listed(4, 2006, "BAYAMON", 24, 212),
                      _listed(4, 2006, "BAYAMON", 24, 211, url="http://wb/other")):
            assert drop_foreign_rows([ROW], [other])[0] == [ROW]

    def test_only_a_jug05_row_is_ever_dropped(self):
        ficha = _row(4, 2006, "BAYAMON", 24, 211, source=SOURCE_ID)
        assert drop_foreign_rows([ficha], [_listed(4, 2006, "BAYAMON", 24, 211)])[0] == [ficha]

    def test_the_other_rows_of_the_season_stay(self):
        rows = [ROW, _row(4, 2006, "COAMO", 3, 4, url="http://wb/y"), _row(74, 2006, "BAYAMON", 24, 211, source=SOURCE_ID)]
        assert drop_foreign_rows(rows, [_listed(4, 2006, "BAYAMON", 24, 211)])[0] == rows[1:]

    def test_the_input_is_not_mutated_and_a_second_pass_finds_nothing(self):
        rows = [ROW]
        kept, _ = drop_foreign_rows(rows, [_listed(4, 2006, "BAYAMON", 24, 211)])
        assert rows == [ROW] and drop_foreign_rows(kept, [_listed(4, 2006, "BAYAMON", 24, 211)])[1] == []

    def test_the_log_is_history(self, tmp_path):
        _, dropped = drop_foreign_rows([ROW], [_listed(4, 2006, "BAYAMON", 24, 211)])
        write_foreign_rows_log(dropped, interim_dir=tmp_path)
        first = (tmp_path / pp.FOREIGN_LOG_FILE).read_bytes()
        write_foreign_rows_log([], interim_dir=tmp_path)                        # a second run drops nothing
        assert (tmp_path / pp.FOREIGN_LOG_FILE).read_bytes() == first

    def test_an_absent_list_drops_nothing(self, tmp_path):
        assert load_foreign_rows(interim_dir=tmp_path) == []


class TestWiring:
    def test_merge_reads_the_list_before_the_season_totals_and_the_fold(self):
        import inspect
        merge, main = inspect.getsource(pp.merge_jug05), inspect.getsource(pp.main)
        order = [merge.index(x) for x in ("drop_foreign_rows(career, load_foreign_rows())", "fold_season_totals(kept)",
                                          "fold_cross_source_career(kept)")]
        assert order == sorted(order)
        assert 'j05["foreign_rows"]' in main and "write_foreign_rows_log(jug05_foreign_rows)" in main


def _rd(name, folder):
    with (REPO_ROOT / "data" / folder / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


class TestCommittedData:
    def test_the_curated_list_has_per_row_evidence(self):
        lst = _rd(pp.FOREIGN_INPUT_FILE, "interim")
        assert len(lst) == 5 and {r["bsnpr_id"] for r in lst} == {"4", "313", "1208", "49"}
        for r in lst:
            assert r["evidence"].strip() and r["evidence_es"].strip() and r["owner_id"] and r["capture_date"] and r["source_url"]
            assert "wikipedia" not in r["evidence_es"].lower() and "error" not in r["evidence_es"].lower()

    def test_5_rows_were_dropped_and_logged_for_4_players(self):
        log = _rd(pp.FOREIGN_LOG_FILE, "interim")
        assert len(log) == 5 and list(log[0]) == FOREIGN_LOG_COLUMNS and len({r["bsnpr_id"] for r in log}) == 4
        assert sorted((r["bsnpr_id"], r["season"], r["team_raw"], r["games"], r["points"]) for r in log) == [
            ("1208", "2006", "GUAYNABO", "9", "43"), ("313", "2006", "GUAYAMA", "9", "6"), ("4", "2006", "BAYAMON", "24", "211"),
            ("49", "2001", "COAMO", "11", "18"), ("49", "2001", "PONCE", "3", "0")]
        assert all(r["retrieved_at"] for r in log)
        assert sum(int(r["points"]) for r in log) == 278 and sum(int(r["games"]) for r in log) == 56

    def test_the_career_csv_lost_exactly_those_rows(self):
        rows = _rd("player_career_seasons.csv", "clean")
        assert len(rows) == 5678                                                # 5,683 before
        for r in _rd(pp.FOREIGN_LOG_FILE, "interim"):
            assert not [x for x in rows if (x["bsnpr_id"], x["season"], x["team_raw"], x["games"], x["points"], x["source_url"]) ==
                        (r["bsnpr_id"], r["season"], r["team_raw"], r["games"], r["points"], r["source_url"])]

    def test_the_other_rows_of_the_four_players_are_untouched(self):
        rows = _rd("player_career_seasons.csv", "clean")
        mine = lambda pid: sorted((r["season"], r["team_raw"], r["games"], r["points"]) for r in rows if r["bsnpr_id"] == pid)
        assert mine("4") == [("1999", "COAMO", "8", "6"), ("2000", "COAMO", "2", "7"), ("2002", "COAMO", "16", "39"), ("2004", "COAMO", "15", "10")]
        assert mine("313") == []
        assert mine("1208") == [("2006", "Vaqueros, Bayamon", "6", "3")]
        assert [r for r in mine("49") if r[0] == "2001"] == [("2001", "CAGUAS", "7", "19"), ("2001", "Criollos, Caguas", "6", "19")]
        assert len(mine("49")) == 10

    def test_class_b_and_c_rows_stay(self):
        rows = _rd("player_career_seasons.csv", "clean")
        has = lambda pid, s, t, g, p: any((r["bsnpr_id"], r["season"], r["team_raw"], r["games"], r["points"]) == (pid, s, t, g, p) for r in rows)
        assert has("74", "2006", "Vaqueros, Bayamon", "24", "211")               # class b: the owner of BAYAMON 24/211
        assert has("2000", "2006", "Brujos, Guayama", "9", "6")                  # class b
        assert has("1912", "2006", "GUAYNABO", "9", "43")                        # class c: Allen
        assert has("990032", "2006", "HUMACAO", "4", "8")                        # class c: Saez

    def test_the_apply_script_finds_nothing_left_to_do(self):
        assert apply.main(["--check"]) == 0
