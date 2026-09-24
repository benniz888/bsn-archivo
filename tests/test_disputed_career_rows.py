"""Career rows that conflict with the player's OWN birth_date on the same bsnpr.com page (J16 A05,
docs/specs/cluster_evidence_a05.md). A hand-curated list (data/interim/disputed_career_rows.csv) says which
published rows are flagged; nothing is detected automatically, and unlike jug05_foreign_lines.csv (a row known
to belong to someone else, dropped), a disputed row is NOT dropped -- it stays in player_career_seasons.csv
untouched. check_disputed_rows only confirms the list still matches; the app (data_quality.json, dqDisputed)
does the marking. Fixture tests pin the rule; TestCommittedData pins the committed list (5 rows, id 721 only)."""

import csv

from src import parse_players as pp
from src.parse_players import DISPUTED_ROWS_FILE, check_disputed_rows, load_disputed_rows
from src.wayback_cdx import REPO_ROOT


def _career(pid, season, team, games, points, url="http://wb/x"):
    return {"bsnpr_id": str(pid), "season": str(season), "team_raw": team, "games": str(games), "points": str(points),
            "source_id": "wayback_bsnpr_players", "source_url": url, "retrieved_at": "t"}


def _disputed(pid, season, team, games, points, url="http://wb/x"):
    return {"bsnpr_id": str(pid), "season": str(season), "team_raw": team, "games": str(games), "points": str(points),
            "source_url": url, "capture_date": "2007-08-28", "evidence": "e", "evidence_es": "es",
            "source_doc": "d", "decided_by": "owner", "decided_at": "2026-09-24"}


ROW = _career(721, 1965, "Capitanes, Arecibo", 13, 32)


class TestRule:
    def test_a_matching_listed_row_reports_no_problem(self):
        assert check_disputed_rows([ROW], [_disputed(721, 1965, "Capitanes, Arecibo", 13, 32)]) == []

    def test_the_row_is_never_removed_or_changed(self):
        career = [ROW, _career(721, 1966, "Capitanes, Arecibo", 10, 12)]
        before = [dict(r) for r in career]
        check_disputed_rows(career, [_disputed(721, 1965, "Capitanes, Arecibo", 13, 32)])
        assert career == before                                             # pure: nothing mutated, nothing dropped

    def test_every_part_of_the_key_must_match_or_it_is_reported(self):
        for other in (_disputed(722, 1965, "Capitanes, Arecibo", 13, 32), _disputed(721, 1966, "Capitanes, Arecibo", 13, 32),
                      _disputed(721, 1965, "Otro, Equipo", 13, 32), _disputed(721, 1965, "Capitanes, Arecibo", 14, 32),
                      _disputed(721, 1965, "Capitanes, Arecibo", 13, 33),
                      _disputed(721, 1965, "Capitanes, Arecibo", 13, 32, url="http://wb/other")):
            assert len(check_disputed_rows([ROW], [other])) == 1

    def test_a_stale_entry_is_reported_not_silently_ignored(self):
        problems = check_disputed_rows([], [_disputed(721, 1965, "Capitanes, Arecibo", 13, 32)])
        assert len(problems) == 1 and "disputed_career_rows" in problems[0] and "721/1965" in problems[0]

    def test_an_absent_list_loads_empty_and_reports_nothing(self, tmp_path):
        assert load_disputed_rows(interim_dir=tmp_path) == []
        assert check_disputed_rows([ROW], []) == []


class TestWiring:
    def test_main_checks_the_list_after_the_id_map_and_exits_on_a_problem(self):
        import inspect
        main = inspect.getsource(pp.main)
        assert "check_disputed_rows(career, load_disputed_rows())" in main
        assert main.index("build_id_map(canon, aliases, career)") < main.index("check_disputed_rows(career, load_disputed_rows())")
        assert "sys.exit(\"! \" + \"\\n! \".join(disputed_problems))" in main


def _rd(name, folder):
    with (REPO_ROOT / "data" / folder / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


class TestCommittedData:
    def test_the_curated_list_has_5_rows_all_for_721_with_evidence(self):
        lst = _rd(DISPUTED_ROWS_FILE, "interim")
        assert len(lst) == 5 and {r["bsnpr_id"] for r in lst} == {"721"}
        assert sorted(int(r["season"]) for r in lst) == [1965, 1966, 1967, 1968, 1969]
        for r in lst:
            assert r["evidence"].strip() and r["evidence_es"].strip() and r["source_url"].startswith("https://web.archive.org/")
            assert "wikipedia" not in r["evidence_es"].lower() and "error" not in r["evidence_es"].lower()
            assert "equivocad" not in r["evidence_es"].lower()

    def test_the_list_still_matches_the_committed_career_csv(self):
        career = _rd("player_career_seasons.csv", "clean")
        assert check_disputed_rows(career, _rd(DISPUTED_ROWS_FILE, "interim")) == []

    def test_the_rows_are_still_in_the_career_csv_untouched(self):
        rows = _rd("player_career_seasons.csv", "clean")
        mine = sorted((r["season"], r["games"], r["points"]) for r in rows if r["bsnpr_id"] == "721")
        assert mine == [("1965", "13", "32"), ("1966", "10", "12"), ("1967", "18", "44"), ("1968", "10", "12"), ("1969", "16", "74")]

    def test_722_is_not_listed_it_has_no_career_rows(self):
        rows = _rd("player_career_seasons.csv", "clean")
        assert [r for r in rows if r["bsnpr_id"] == "722"] == []
