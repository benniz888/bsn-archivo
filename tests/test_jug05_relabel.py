"""The jug05 newest-season slot (docs/specs/jug05_offset_check.md). jug05.asp labels its newest season "2005" on
every capture and overwrote the figures under it between the captures of 2006-02-24 and 2006-05-28, so a row
labelled 2005 on a later capture is the season jugador.asp files under 2006. parse_players.jug05_season is the one
rule; src/apply_jug05_relabel.py applies it to the committed CSV. Fixture tests pin the rule and the script;
TestCommittedData pins the numbers on the committed files (145 relabelled, 100 folded, 767 merged). The season-total fold that followed (13 rows, 107 -> 94
conflicts) is pinned in tests/test_jug05_season_totals.py."""

import csv
import json
import re
import shutil

import pytest

from src import apply_jug05_relabel as apply
from src import parse_players as pp
from src.parse_players import JUG05_SOURCE_ID, SOURCE_ID, fold_cross_source_career, jug05_capture_ts, jug05_season
from src.wayback_cdx import REPO_ROOT

RAW = REPO_ROOT / "data" / "raw" / "players" / "jug05"
OLD, NEW = "20060224", "20060528"                      # the last old capture and the first new one


def _url(day, kind="jug05.asp?r=1"):
    return f"https://web.archive.org/web/{day}120000id_/http://www.bsnpr.com/{kind}"


def _row(pid, season, team, games, points, source=SOURCE_ID, day="20080401"):
    return {"bsnpr_id": str(pid), "season": str(season), "team_raw": team, "games": str(games), "points": str(points),
            "source_id": source, "source_url": _url(day, f"x/{pid}/{season}/{team}"), "retrieved_at": "t"}


def _jug(pid, season, team, games, points, day):
    return _row(pid, season, team, games, points, source=JUG05_SOURCE_ID, day=day)


class TestRule:
    def test_the_slot_label_flips_with_the_capture_date(self):
        assert jug05_season(2005, "20060224015224") == 2005          # the last old capture
        assert jug05_season(2005, "20060528213551") == 2006          # the first new one
        assert jug05_season(2005, "20070404120000") == 2006

    def test_the_cutoff_lies_between_the_two_captures(self):
        assert "20060224015224" < pp.JUG05_SLOT_FLIP < "20060528213551"

    def test_no_capture_with_a_2005_row_lies_between_the_two(self):
        """Any cutoff in the gap gives the same rows: the only jug05 captures between the two dates (2006-04-27)
        carry no row labelled 2005."""
        if not RAW.exists():
            pytest.skip("raw captures not present")
        between = []
        for meta in RAW.glob("*.meta.json"):
            ts = json.loads(meta.read_text(encoding="utf-8"))["wayback_timestamp"]
            if "20060224015224" < ts < "20060528213551":
                between.append(_html_of(meta))
        assert between, "the gap is expected to hold the two captures of 2006-04-27"
        for html in between:
            rows = _page_rows(html)
            assert rows and not [r for r in rows if r[0] == 2005]

    def test_only_the_slot_label_moves(self):
        for label in (1980, 2001, 2003, 2004):
            assert jug05_season(label, "20061208000000") == label
        assert jug05_season(2005, "") == 2005                        # no timestamp: the label stands

    def test_the_timestamp_comes_from_the_wayback_url(self):
        assert jug05_capture_ts("https://web.archive.org/web/20060528213551id_/http://www.bsnpr.com:80/jug05.asp?r=1") == "20060528213551"
        assert jug05_capture_ts("http://example.org/no-timestamp") == "" and jug05_capture_ts(None) == ""


class TestParseJug05:
    """parse_jug05 on two real captures of one player (Dalmau, Raymond): the page says 2005 both times."""

    @pytest.fixture
    def raw(self, tmp_path, monkeypatch):
        if not RAW.exists():
            pytest.skip("raw captures not present")
        monkeypatch.setattr(pp, "RAW_DIR", tmp_path)
        (tmp_path / "jug05").mkdir()

        def put(prefix):
            for f in RAW.glob(f"{prefix}*"):
                shutil.copy(f, tmp_path / "jug05" / f.name)
        return put

    def test_an_old_capture_keeps_2005(self, raw):
        raw("2OVDH3OQ5Q")                                            # captured 2006-02-24
        career = pp.parse_jug05()[0]["career"]
        assert (2005, "SANTURCE", 27, 392) in career and not any(r[0] == 2006 for r in career)

    def test_a_new_capture_files_the_same_label_under_2006(self, raw):
        raw("UO3MLGLVHW")                                            # captured 2006-05-28
        career = pp.parse_jug05()[0]["career"]
        assert (2006, "SANTURCE", 22, 264) in career and not any(r[0] == 2005 for r in career)


class TestRelabel:
    def test_a_new_capture_row_is_relabelled_and_the_log_says_when(self):
        rows = [_jug(74, 2005, "BAYAMON", 24, 211, NEW)]
        out, log = apply.relabel(rows)
        assert out[0]["season"] == "2006" and rows[0]["season"] == "2005"        # the input is not mutated
        assert list(log[0]) == apply.RELABELED_COLUMNS
        assert (log[0]["bsnpr_id"], log[0]["old_season"], log[0]["new_season"], log[0]["capture_date"]) == ("74", "2005", "2006", "2006-05-28")
        assert log[0]["source_url"] == rows[0]["source_url"]

    def test_an_old_capture_row_a_players_row_and_other_seasons_are_left_alone(self):
        rows = [_jug(1, 2005, "BAYAMON", 1, 1, OLD), _row(2, 2005, "Vaqueros, Bayamon", 1, 1, day=NEW),
                _jug(3, 2004, "BAYAMON", 1, 1, NEW), _jug(4, 2006, "BAYAMON", 1, 1, NEW)]
        out, log = apply.relabel(rows)
        assert out == rows and log == []

    def test_both_rows_of_a_two_team_slot_move(self):
        rows = [_jug(9, 2005, "CAGUAS", 5, 39, NEW), _jug(9, 2005, "BAYAMON", 19, 155, NEW)]
        assert [r["season"] for r in apply.relabel(rows)[0]] == ["2006", "2006"]

    def test_relabelling_twice_changes_nothing(self):
        once, log = apply.relabel([_jug(74, 2005, "BAYAMON", 24, 211, NEW)])
        twice, log2 = apply.relabel(once)
        assert twice == once and log and log2 == []

    def test_the_fold_then_folds_the_identical_row_and_keeps_the_conflict_and_the_rest(self):
        rows = [_row(74, 2005, "Vaqueros, Bayamon", 11, 134), _row(74, 2006, "Vaqueros, Bayamon", 24, 211),
                _jug(74, 2005, "BAYAMON", 24, 211, NEW),                       # = the ficha's 2006 row: folded
                _row(20, 2006, "Criollos, Caguas", 5, 39), _jug(20, 2005, "CAGUAS", 24, 194, NEW),   # differs: a conflict
                _jug(30, 2005, "PONCE", 3, 4, NEW),                            # no twin: stays, filed under 2006
                _jug(40, 2005, "ARECIBO", 8, 8, OLD), _row(40, 2005, "Capitanes, Arecibo", 8, 8)]   # old capture: folds at 2005
        relabelled, log = apply.relabel(rows)
        kept, merged, conflicts = fold_cross_source_career(relabelled)
        assert len(log) == 3 and len(kept) == len(rows) - 2
        assert sorted((m["bsnpr_id"], m["season"]) for m in merged) == [("40", 2005), ("74", 2006)]
        assert [(c["bsnpr_id"], c["season"], (c["games_a"], c["games_b"])) for c in conflicts] == [("20", 2006, (5, 24))]
        assert ("30", "2006") in {(r["bsnpr_id"], r["season"]) for r in kept}
        assert ("74", "2005", "11") in {(r["bsnpr_id"], r["season"], r["games"]) for r in kept}   # the ficha's 2005 stands

    def test_a_trade_with_two_franchises_is_not_folded(self):
        rows = [_row(5, 2006, "Vaqueros, Bayamon", 6, 3), _jug(5, 2005, "GUAYNABO", 9, 43, NEW)]
        kept, merged, conflicts = fold_cross_source_career(apply.relabel(rows)[0])
        assert merged == [] and len(kept) == 2 and [c["bsnpr_id"] for c in conflicts] == []   # different cities: not a pair

    def test_the_provenance_log_is_history(self, tmp_path):
        first = [{"bsnpr_id": "74", "old_season": "2005", "new_season": "2006", "capture_date": "2006-05-28",
                  "source_url": "u", "team_raw": "BAYAMON", "games": "24", "points": "211"}]
        apply.write_relabel_log(first, interim_dir=tmp_path)
        before = (tmp_path / apply.RELABELED_FILE).read_bytes()
        apply.write_relabel_log([], interim_dir=tmp_path)                      # a second run relabels nothing
        assert (tmp_path / apply.RELABELED_FILE).read_bytes() == before


def _rd(name, folder):
    with (REPO_ROOT / "data" / folder / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


class TestCommittedData:
    def test_145_rows_were_relabelled_and_logged_with_their_capture_date(self):
        log = _rd(apply.RELABELED_FILE, "interim")
        assert len(log) == 145 and list(log[0]) == apply.RELABELED_COLUMNS
        assert {(r["old_season"], r["new_season"]) for r in log} == {("2005", "2006")}
        assert min(r["capture_date"] for r in log) == "2006-05-28" and len({r["bsnpr_id"] for r in log}) == 145
        assert all(jug05_capture_ts(r["source_url"]) >= pp.JUG05_SLOT_FLIP for r in log)

    def test_no_jug05_row_labelled_2005_comes_from_a_new_capture_any_more(self):
        rows = _rd("player_career_seasons.csv", "clean")
        assert not [r for r in rows if r["source_id"] == JUG05_SOURCE_ID and r["season"] == "2005"
                    and jug05_capture_ts(r["source_url"]) >= pp.JUG05_SLOT_FLIP]
        assert len(rows) == 5683                                              # 5,796 before: 100 folded, then 13 season totals
        assert sum(1 for r in rows if r["source_id"] == JUG05_SOURCE_ID and r["season"] == "2006") == 33   # 45, 12 of them season totals

    def test_the_fold_logged_100_more_pairs_and_left_the_conflicts_the_totals_fold_did_not_take(self):
        merged, conflicts = _rd("jug05_career_merged.csv", "interim"), _rd("jug05_career_conflicts.csv", "interim")
        assert len(merged) == 767 and sum(1 for r in merged if r["season"] == "2006") == 100
        assert sum(1 for r in merged if r["season"] == "2005") == 4          # the pre-flip pairs are unchanged
        assert len(conflicts) == 94                                            # 107 after the relabel, minus 13 season totals
        assert sorted({(int(r["season"]), sum(1 for c in conflicts if c["season"] == r["season"])) for r in conflicts}) == [
            (2000, 17), (2001, 51), (2002, 18), (2003, 3), (2005, 3), (2006, 2)]

    def test_the_apply_script_finds_nothing_left_to_do(self):
        assert apply.main(["--check"]) == 0

    def test_every_relabelled_row_is_on_its_raw_capture_under_the_label_2005(self):
        if not RAW.exists():
            pytest.skip("raw captures not present")
        log = _rd(apply.RELABELED_FILE, "interim")
        want = {r["source_url"] for r in log}
        seen = {}
        for meta in RAW.glob("*.meta.json"):
            m = json.loads(meta.read_text(encoding="utf-8"))
            if m["raw_wayback_url"] in want:
                seen[m["raw_wayback_url"]] = _page_rows(_html_of(meta))
        assert set(seen) == want
        for r in log:
            assert (2005, r["team_raw"], int(r["games"]), int(r["points"])) in seen[r["source_url"]], r


def _html_of(meta):
    """The capture a .meta.json describes: <name>.html.meta.json sits next to <name>.html."""
    return pp.decode_html((meta.parent / meta.name[:-len(".meta.json")]).read_bytes())


def _page_rows(html):
    """The (label, team, games, points) rows of one jug05 page, read with parse_jug05's own patterns."""
    from bs4 import BeautifulSoup
    txt = " ".join(BeautifulSoup(html, "html.parser").get_text(" ").split())
    cm = pp._J5_CAR.search(txt)
    out = []
    for r in (pp._J5_ROW.finditer(cm.group(1)) if cm else []):
        toks = re.findall(r"\d+\.\d+|\d+%|\d+", r.group(3))
        if len(toks) >= 3 and re.fullmatch(r"\d+\.\d+", toks[-1]) and toks[-3].isdigit() and toks[-2].isdigit():
            out.append((int(r.group(1)), pp.squish(r.group(2)), int(toks[-3]), int(toks[-2])))
    return out
