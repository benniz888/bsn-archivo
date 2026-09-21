"""Cross-source career dedup (docs/specs/merge_jug05_audit_spec.md, D1-D6).

Fixture tests pin the rule; TestCommittedData pins the numbers on the committed files
(767 merged, 107 stat conflicts, 235 trade pairs, player 1995 one row per year). 665 and 125 before the
identity merges of 2026-09-21 (73 -> 74 folded two more jug05 rows and added one conflict); 667, 126 and 276 before
the jug05 relabel (src/apply_jug05_relabel.py: 100 more rows folded, 33 conflicts gone, 14 new ones, 41 trade pairs
were the mislabel).
"""

import csv
import inspect
import random
import shutil

import pytest

from src import apply_career_dedup as apply
from src import parse_players as pp
from src.parse_players import (CAREER_CONFLICT_COLUMNS, CAREER_MERGED_COLUMNS, JUG05_SOURCE_ID,
                               SOURCE_ID, city_token, fold_cross_source_career, merge_jug05)
from src.wayback_cdx import REPO_ROOT

REPO_CLEAN = REPO_ROOT / "data" / "clean"
REPO_INTERIM = REPO_ROOT / "data" / "interim"


def _row(pid, season, team, games, points, source=SOURCE_ID):
    return {"bsnpr_id": str(pid), "season": season, "team_raw": team, "games": games,
            "points": points, "source_id": source, "source_url": f"http://wb/{source}/{pid}/{season}",
            "retrieved_at": "t"}


def _jug(pid, season, team, games, points):
    return _row(pid, season, team, games, points, source=JUG05_SOURCE_ID)


class TestCityToken:
    def test_both_spellings_share_the_city(self):
        assert city_token("Criollos, Caguas") == city_token("CAGUAS") == "caguas"

    def test_accents_and_case(self):
        assert city_token("Vaqueros, Bayamón") == city_token("BAYAMON") == "bayamon"

    def test_blank(self):
        assert city_token("") == city_token(None) == ""


class TestFold:
    def test_identical_stats_merge_and_the_players_row_survives(self):
        rows = [_jug(1995, 2002, "CAGUAS", 23, 53), _row(1995, 2002, "Criollos, Caguas", 23, 53)]
        kept, merged, conflicts = fold_cross_source_career(rows)
        assert [r["source_id"] for r in kept] == [SOURCE_ID] and kept[0]["team_raw"] == "Criollos, Caguas"
        assert conflicts == [] and len(merged) == 1
        m = merged[0]
        assert list(m) == CAREER_MERGED_COLUMNS
        assert (m["bsnpr_id"], m["season"], m["franchise_id"]) == ("1995", 2002, "criollos_caguas")
        assert (m["games"], m["points"], m["jug05_team_raw"]) == (23, 53, "CAGUAS")
        assert m["jug05_retrieved_at"] == "t"          # the fetch time of the row that is being dropped
        assert m["players_source_url"] == rows[1]["source_url"] and m["jug05_source_url"] == rows[0]["source_url"]

    def test_a_city_the_map_lacks_merges_with_a_blank_franchise(self):
        rows = [_row(50, 1993, "Tiburones, Nowhere", 33, 248), _jug(50, 1993, "NOWHERE", 33, 248)]
        kept, merged, _ = fold_cross_source_career(rows)
        assert len(kept) == 1 and merged[0]["franchise_id"] == ""

    def test_aguadilla_cabo_rojo_and_villalba_merge_with_their_franchise(self):
        # J16a: the city map names them now, so the merged pair carries the franchise the site shows.
        for pid, team, bare, fid in ((50, "Tiburones, Aguadilla", "AGUADILLA", "tiburones_aguadilla"),
                                     (51, "Tainos, Cabo Rojo", "CABO ROJO", "tainos_cabo_rojo"),
                                     (52, "Avancinos, Villalba", "VILLALBA", "avancinos_villalba")):
            kept, merged, _ = fold_cross_source_career([_row(pid, 1993, team, 33, 248), _jug(pid, 1993, bare, 33, 248)])
            assert len(kept) == 1 and merged[0]["franchise_id"] == fid, team

    def test_different_stats_stay_two_rows_and_both_lines_are_logged(self):
        rows = [_row(37, 2005, "Vaqueros, Bayamon", 28, 408), _jug(37, 2005, "BAYAMON", 13, 253)]
        kept, merged, conflicts = fold_cross_source_career(rows)
        assert len(kept) == 2 and merged == []
        c = conflicts[0]
        assert list(c) == CAREER_CONFLICT_COLUMNS
        assert (c["team_raw_a"], c["games_a"], c["points_a"]) == ("Vaqueros, Bayamon", 28, 408)
        assert (c["team_raw_b"], c["games_b"], c["points_b"]) == ("BAYAMON", 13, 253)
        assert (c["source_id_a"], c["source_id_b"]) == (SOURCE_ID, JUG05_SOURCE_ID)
        assert c["jug05_retrieved_at"] == "t"          # row b is the jug05 row

    def test_retrieved_at_is_blank_when_the_jug05_row_has_none(self):
        stamped = _jug(1, 2002, "CAGUAS", 23, 53)
        stamped["retrieved_at"] = ""
        assert fold_cross_source_career([_row(1, 2002, "Criollos, Caguas", 23, 53), stamped])[1][0]["jug05_retrieved_at"] == ""
        del stamped["retrieved_at"]
        assert fold_cross_source_career([_row(1, 2002, "Criollos, Caguas", 23, 53), stamped])[1][0]["jug05_retrieved_at"] == ""
        conflict = _jug(2, 2001, "SANTURCE", 12, 26)
        conflict["retrieved_at"] = ""
        assert fold_cross_source_career([_row(2, 2001, "Cangrejeros, Santurce", 12, 14), conflict])[2][0]["jug05_retrieved_at"] == ""

    def test_the_log_column_lists_are_pinned(self):
        assert CAREER_MERGED_COLUMNS == [
            "bsnpr_id", "season", "franchise_id", "games", "points",
            "players_source_url", "jug05_source_url", "jug05_team_raw", "jug05_retrieved_at"]
        assert CAREER_CONFLICT_COLUMNS == [
            "bsnpr_id", "season", "city_token",
            "team_raw_a", "source_id_a", "games_a", "points_a", "source_url_a",
            "team_raw_b", "source_id_b", "games_b", "points_b", "source_url_b", "jug05_retrieved_at"]

    def test_two_franchises_in_one_season_are_never_merged(self):
        rows = [_row(37, 2016, "Atenienses, Manati", 11, 139), _row(37, 2016, "Brujos, Guayama", 26, 378),
                _jug(37, 2016, "GUAYAMA", 26, 378)]
        kept, merged, _ = fold_cross_source_career(rows)
        assert {r["team_raw"] for r in kept} == {"Atenienses, Manati", "Brujos, Guayama"}
        assert len(merged) == 1 and merged[0]["jug05_team_raw"] == "GUAYAMA"

    def test_a_trade_with_identical_stats_in_two_cities_is_not_confused(self):
        rows = [_row(9, 2001, "Cangrejeros, Santurce", 12, 14), _jug(9, 2001, "MAYAGUEZ", 12, 14)]
        kept, merged, conflicts = fold_cross_source_career(rows)
        assert len(kept) == 2 and merged == [] and conflicts == []

    def test_rows_of_one_source_are_never_folded_into_each_other(self):
        rows = [_row(5, 2002, "Leones, Ponce", 10, 20), _row(5, 2002, "PONCE", 10, 20)]
        kept, merged, conflicts = fold_cross_source_career(rows)
        assert len(kept) == 2 and merged == [] and conflicts == []

    def test_two_named_franchises_in_one_city_are_never_folded(self):
        rows = [_row(8, 2016, "Atenienses, Manati", 30, 300), _jug(8, 2016, "Osos, Manati", 30, 300)]
        kept, merged, conflicts = fold_cross_source_career(rows)
        assert len(kept) == 2 and merged == [] and conflicts == []

    def test_a_bare_city_is_no_evidence_against_a_named_row(self):
        # the resolver maps "GUAYNABO" to the city-map franchise and "Conquistadores, Guaynabo" to
        # its own nickname key; that mismatch is the resolver's limit, not a second team
        rows = [_row(3, 1988, "Conquistadores, Guaynabo", 20, 100), _jug(3, 1988, "GUAYNABO", 20, 100)]
        kept, merged, _ = fold_cross_source_career(rows)
        assert len(kept) == 1 and len(merged) == 1

    def test_a_blank_stat_is_not_a_zero(self):
        blank = [_row(4, 2003, "Leones, Ponce", None, None), _jug(4, 2003, "PONCE", 0, 0)]
        kept, merged, conflicts = fold_cross_source_career(blank)
        assert len(kept) == 2 and merged == [] and len(conflicts) == 1
        both_blank = [_row(4, 2003, "Leones, Ponce", None, None), _jug(4, 2003, "PONCE", None, None)]
        assert len(fold_cross_source_career(both_blank)[0]) == 1

    def test_csv_strings_and_memory_ints_decide_the_same(self):
        as_ints = [_row(1, 2002, "Criollos, Caguas", 23, 53), _jug(1, 2002, "CAGUAS", 23, 53)]
        as_strs = [{**r, "season": str(r["season"]), "games": str(r["games"]), "points": str(r["points"])}
                   for r in as_ints]
        assert len(fold_cross_source_career(as_ints)[0]) == len(fold_cross_source_career(as_strs)[0]) == 1

    def test_input_order_does_not_change_the_result(self):
        rows = [_row(1, 2002, "Criollos, Caguas", 23, 53), _jug(1, 2002, "CAGUAS", 23, 53),
                _row(2, 2001, "Cangrejeros, Santurce", 12, 14), _jug(2, 2001, "SANTURCE", 12, 26),
                _row(3, 1993, "Tiburones, Aguadilla", 33, 248), _jug(3, 1993, "AGUADILLA", 33, 248)]
        base = fold_cross_source_career(rows)
        shuffled = rows[:]
        random.Random(7).shuffle(shuffled)
        got = fold_cross_source_career(shuffled)
        key = lambda r: (r["bsnpr_id"], r["season"], r["team_raw"])
        assert sorted(base[0], key=key) == sorted(got[0], key=key)
        assert base[1] == got[1] and base[2] == got[2]

    def test_folding_twice_changes_nothing(self):
        rows = [_row(1, 2002, "Criollos, Caguas", 23, 53), _jug(1, 2002, "CAGUAS", 23, 53),
                _row(2, 2001, "Cangrejeros, Santurce", 12, 14), _jug(2, 2001, "SANTURCE", 12, 26)]
        kept, merged, conflicts = fold_cross_source_career(rows)
        again_kept, again_merged, again_conflicts = fold_cross_source_career(kept)
        assert again_kept == kept and again_merged == [] and again_conflicts == conflicts

    def test_the_input_is_not_mutated(self):
        rows = [_row(1, 2002, "Criollos, Caguas", 23, 53), _jug(1, 2002, "CAGUAS", 23, 53)]
        before = [dict(r) for r in rows]
        fold_cross_source_career(rows)
        assert rows == before


class TestMergeJug05:
    def test_merge_jug05_folds_and_reports(self):
        canon = [dict(bsnpr_id="1", canonical_name="Perez, Juan", apellidos="Perez", nombre="Juan",
                      birth_date="", birth_year="")]
        career = [_row(1, 2002, "Criollos, Caguas", 23, 53)]
        jug = [dict(name="Perez, Juan", apellidos="Perez", nombre="Juan", birth_date="", position="",
                    career=[(2002, "CAGUAS", 23, 53), (2003, "CAGUAS", 25, 199)],
                    source_url="http://wb/jug05/1", retrieved_at="t")]
        res = merge_jug05(canon, career, jug)
        assert [(r["season"], r["team_raw"]) for r in career] == [(2002, "Criollos, Caguas"), (2003, "CAGUAS")]
        assert len(res["merged"]) == 1 and res["conflicts"] == []
        assert res["career_rows"] == 1            # the 2003 row is new; the 2002 duplicate is not counted

    def test_merge_jug05_keeps_a_stat_conflict_as_two_rows(self):
        canon = [dict(bsnpr_id="1", canonical_name="Perez, Juan", apellidos="Perez", nombre="Juan",
                      birth_date="", birth_year="")]
        career = [_row(1, 2005, "Vaqueros, Bayamon", 28, 408)]
        jug = [dict(name="Perez, Juan", apellidos="Perez", nombre="Juan", birth_date="", position="",
                    career=[(2005, "BAYAMON", 13, 253)], source_url="http://wb/jug05/1", retrieved_at="t")]
        res = merge_jug05(canon, career, jug)
        assert len(career) == 2 and res["merged"] == [] and len(res["conflicts"]) == 1

    def test_the_exact_repeat_guard_still_skips_the_same_row_twice(self):
        canon = [dict(bsnpr_id="1", canonical_name="Perez, Juan", apellidos="Perez", nombre="Juan",
                      birth_date="", birth_year="")]
        career = []
        page = dict(name="Perez, Juan", apellidos="Perez", nombre="Juan", birth_date="", position="",
                    career=[(2002, "CAGUAS", 23, 53)], source_url="http://wb/jug05/1", retrieved_at="t")
        merge_jug05(canon, career, [page, dict(page)])
        assert len(career) == 1


class TestApplyScript:
    @pytest.fixture
    def repo(self, tmp_path, monkeypatch):
        clean, interim = tmp_path / "clean", tmp_path / "interim"
        clean.mkdir()
        interim.mkdir()
        for name in ("city_franchise_map.csv", "franchises.csv", "club_code_map.csv",
                     "city_franchise_season_overrides.csv"):
            shutil.copy(REPO_CLEAN / name, clean / name)
        monkeypatch.setattr(pp, "CLEAN_DIR", clean)
        monkeypatch.setattr(pp, "INTERIM_DIR", interim)
        rows = [_row(1995, 2002, "Criollos, Caguas", 23, 53), _jug(1995, 2002, "CAGUAS", 23, 53),
                _row(2, 2001, "Cangrejeros, Santurce", 12, 14), _jug(2, 2001, "SANTURCE", 12, 26),
                _row(50, 1993, "Tiburones, Nowhere", 33, 248), _jug(50, 1993, "NOWHERE", 33, 248)]
        with (clean / "player_career_seasons.csv").open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=apply.CAREER_COLUMNS)
            w.writeheader()
            w.writerows(rows)
        return clean, interim

    def _files(self, clean, interim):
        return {p.name: p.read_bytes() for p in (clean / "player_career_seasons.csv",
                interim / "jug05_career_merged.csv", interim / "jug05_career_conflicts.csv")}

    def test_check_writes_nothing_and_reports_pending_work(self, repo, capsys):
        clean, interim = repo
        before = (clean / "player_career_seasons.csv").read_bytes()
        assert apply.main(["--check"]) == 1
        assert (clean / "player_career_seasons.csv").read_bytes() == before
        assert list(interim.iterdir()) == []

    def test_apply_merges_logs_and_is_idempotent(self, repo):
        clean, interim = repo
        assert apply.main([]) == 0
        with (clean / "player_career_seasons.csv").open(encoding="utf-8") as fh:
            kept = list(csv.DictReader(fh))
        assert [(r["bsnpr_id"], r["team_raw"]) for r in kept] == [
            ("1995", "Criollos, Caguas"), ("2", "Cangrejeros, Santurce"), ("2", "SANTURCE"),
            ("50", "Tiburones, Nowhere")]
        with (interim / "jug05_career_merged.csv").open(encoding="utf-8") as fh:
            merged = list(csv.DictReader(fh))
        assert [(r["bsnpr_id"], r["franchise_id"], r["jug05_team_raw"]) for r in merged] == [
            ("50", "", "NOWHERE"), ("1995", "criollos_caguas", "CAGUAS")]   # sorted by int player id
        assert {r["jug05_retrieved_at"] for r in merged} == {"t"}
        with (interim / "jug05_career_conflicts.csv").open(encoding="utf-8") as fh:
            conflicts = list(csv.DictReader(fh))
        assert len(conflicts) == 1 and conflicts[0]["jug05_retrieved_at"] == "t"
        first = self._files(clean, interim)
        assert apply.main([]) == 0                       # second run
        assert self._files(clean, interim) == first      # nothing changed, the merged log is not emptied
        assert apply.main(["--check"]) == 0


@pytest.fixture(scope="module")
def committed():
    with (REPO_CLEAN / "player_career_seasons.csv").open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    with (REPO_INTERIM / "jug05_career_merged.csv").open(encoding="utf-8", newline="") as fh:
        merged = list(csv.DictReader(fh))
    with (REPO_INTERIM / "jug05_career_conflicts.csv").open(encoding="utf-8", newline="") as fh:
        conflicts = list(csv.DictReader(fh))
    return rows, merged, conflicts


class TestCommittedData:
    def test_player_1995_has_one_criollos_row_for_2002_to_2004(self, committed):
        rows = committed[0]
        for season in ("2002", "2003", "2004"):
            mine = [r for r in rows if r["bsnpr_id"] == "1995" and r["season"] == season]
            assert [(r["team_raw"], r["source_id"]) for r in mine] == [("Criollos, Caguas", SOURCE_ID)], season

    def test_the_pairs_were_merged_and_logged(self, committed):
        _, merged, _ = committed
        assert len(merged) == 767
        assert list(merged[0]) == CAREER_MERGED_COLUMNS
        assert sum(1 for r in merged if r["franchise_id"] == "") == 19    # Cayey, deferred (J16b)
        assert all(r["jug05_retrieved_at"] for r in merged)               # every dropped row keeps its fetch time

    def test_the_stat_conflicts_remain_as_two_rows_and_are_logged(self, committed):
        rows, _, conflicts = committed
        assert len(conflicts) == 107 and list(conflicts[0]) == CAREER_CONFLICT_COLUMNS
        assert all((c["games_a"], c["points_a"]) != (c["games_b"], c["points_b"]) for c in conflicts)
        assert all(c["jug05_retrieved_at"] for c in conflicts)
        for c in conflicts:
            both = [r for r in rows if r["bsnpr_id"] == c["bsnpr_id"] and r["season"] == c["season"]
                    and r["team_raw"] in (c["team_raw_a"], c["team_raw_b"])]
            assert len(both) == 2, c

    def test_folding_the_committed_csv_again_merges_nothing(self, committed):
        rows, _, conflicts = committed
        kept, merged, again = fold_cross_source_career(rows)
        assert merged == [] and len(kept) == len(rows) and len(again) == len(conflicts) == 107

    def test_trade_pairs(self, committed):
        """276 before the relabel. 41 of them were the mislabel: a jug05 row labelled 2005 that was really the
        player's 2006 season at his 2006 team looked like a 2005 trade against the ficha's 2005 team (42 pairs
        went, 1 came: player 1208 in 2006, a jug05 Guaynabo row against a ficha Bayamon row). No trade pair is
        ever folded (D3); only the season a jug05 row is filed under changed."""
        rows = committed[0]
        site = pp._load_site_franchise_resolver()
        by_pair = {}
        for r in rows:
            fid = site(r["team_raw"], int(r["season"]))
            if fid:
                by_pair.setdefault((r["bsnpr_id"], r["season"]), set()).add(fid)
        assert sum(1 for f in by_pair.values() if len(f) >= 2) == 235

    def test_no_false_merges(self, committed):
        rows, merged, _ = committed
        resolve_club, site = pp._load_club_resolver(), pp._load_site_franchise_resolver()
        for m in merged:
            twins = [r for r in rows if r["bsnpr_id"] == m["bsnpr_id"] and r["season"] == m["season"]
                     and r["source_id"] == SOURCE_ID and city_token(r["team_raw"]) == city_token(m["jug05_team_raw"])
                     and r["source_url"] == m["players_source_url"]]
            assert len(twins) == 1, m
            t = twins[0]
            assert (t["games"], t["points"]) == (m["games"], m["points"]), m       # identical stats
            assert m["franchise_id"] == site(t["team_raw"], int(t["season"])), m
            season = int(t["season"])
            fa = pp._named_franchise(t, season, resolve_club)
            fb = pp._named_franchise({"team_raw": m["jug05_team_raw"]}, season, resolve_club)
            assert not (fa and fb and fa != fb), m                                  # never two named franchises


class TestLogWriter:
    """write_career_logs is what main() calls. main() cannot be run here (regenerating is unsafe at
    HEAD, the identity outputs carry hand edits), so this drives the same writer from the committed
    data: the current CSV plus the jug05 rows the merged log records."""

    def test_the_writer_reproduces_the_committed_logs(self, committed, tmp_path):
        rows, merged, conflicts = committed
        dropped = [{"bsnpr_id": m["bsnpr_id"], "season": m["season"], "team_raw": m["jug05_team_raw"],
                    "games": m["games"], "points": m["points"], "source_id": JUG05_SOURCE_ID,
                    "source_url": m["jug05_source_url"], "retrieved_at": m["jug05_retrieved_at"]}
                   for m in merged]
        _, got_merged, got_conflicts = fold_cross_source_career(rows + dropped)
        assert len(got_merged) == 767 and len(got_conflicts) == 107
        pp.write_career_logs(got_merged, got_conflicts, interim_dir=tmp_path)
        with (tmp_path / "jug05_career_merged.csv").open(encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            assert reader.fieldnames == CAREER_MERGED_COLUMNS
            out_merged = list(reader)
        with (tmp_path / "jug05_career_conflicts.csv").open(encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            assert reader.fieldnames == CAREER_CONFLICT_COLUMNS
            out_conflicts = list(reader)
        assert len(out_merged) == 767 and sum(1 for r in out_merged if r["franchise_id"] == "") == 19
        assert len(out_conflicts) == 107
        assert out_merged == merged and out_conflicts == conflicts       # the committed files, row for row

    def test_writing_twice_does_not_empty_the_merged_log(self, committed, tmp_path):
        _, merged, conflicts = committed
        pp.write_career_logs(merged, conflicts, interim_dir=tmp_path)
        first = (tmp_path / "jug05_career_merged.csv").read_bytes()
        pp.write_career_logs([], conflicts, interim_dir=tmp_path)
        assert (tmp_path / "jug05_career_merged.csv").read_bytes() == first

    def test_main_hands_the_merge_result_to_the_writer(self):
        # main() itself is not run in tests; pin the wiring so it cannot be dropped unnoticed
        src = inspect.getsource(pp.main)
        assert 'j05["merged"]' in src and 'j05["conflicts"]' in src
        assert "write_career_logs(jug05_merged, jug05_conflicts)" in src
