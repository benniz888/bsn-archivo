"""The Calidad de datos view (docs/specs/data_quality_view_spec.md): web/data/index/data_quality.json is built
from the recorded logs only. These tests derive every count from the source CSVs, pin the public Spanish
decision text, and check that the app applies the totals rule the owner ruled on (both rows of a conflicted
season stay out of the career totals). The browser checks live in docs/session.md."""

import csv
import json
import re

import pytest

from src import apply_identity_decisions as apply
from src import build_web_data as bwd
from src.wayback_cdx import REPO_ROOT

WEB = REPO_ROOT / "web" / "data"
DQ = WEB / "index" / "data_quality.json"
APP = REPO_ROOT / "app" / "bsn_archivo.html"


def _csv(folder, name):
    with (REPO_ROOT / "data" / folder / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


@pytest.fixture(scope="module")
def dq():
    return json.loads(DQ.read_text(encoding="utf-8"))


def _player(pid):
    return json.loads((WEB / "players" / f"{pid}.json").read_text(encoding="utf-8"))


class TestCountsComeFromTheLogs:
    def test_every_count_equals_its_source_row_count(self, dq):
        n = dq["counts"]
        conflicts = _csv("interim", "jug05_career_conflicts.csv")
        merged = _csv("interim", "jug05_career_merged.csv")
        corrections = _csv("interim", "player_dob_overrides.csv")
        assert n["stat_conflicts"] == len(dq["conflicts"]) == len(conflicts) == 94
        assert n["stat_conflict_players"] == len({r["bsnpr_id"] for r in conflicts}) == 71
        assert n["merged_pairs"] == len(merged) == 767 and n["merged_players"] == len({r["bsnpr_id"] for r in merged}) == 130
        assert sum(n["merged_by_season"].values()) == 767 and min(n["merged_by_season"]) == "1980" and max(n["merged_by_season"]) == "2006"
        assert n["dropped_rows"] == len(_csv("interim", "player_merge_dropped_rows.csv")) == 4
        assert n["decisions"] == len(dq["decisions"]) == 4 and n["tombstones"] == len(_csv("clean", "player_id_tombstones.csv")) == 3
        assert n["dob_open"] == len(dq["dob_open"]) == len(_csv("interim", "jugador05_dob_conflicts.csv")) == 5
        assert (n["dob_corrections"], n["dob_corrections_high"], n["dob_corrections_low"]) == (10, 9, 1) == (len(corrections), 9, 1)

    def test_conflicts_by_season(self, dq):
        assert dq["counts"]["conflicts_by_season"] == {"2000": 17, "2001": 51, "2002": 18, "2003": 3, "2005": 3, "2006": 2}

    def test_the_manifest_counts_the_conflicts(self):
        assert json.loads((WEB / "manifest.json").read_text(encoding="utf-8"))["counts"]["data_quality"] == 94

    def test_no_conflict_has_two_equal_sides(self, dq):
        both_equal = [c for c in dq["conflicts"] if c["a"]["games"] == c["b"]["games"] and c["a"]["points"] == c["b"]["points"]]
        assert both_equal == []
        games_eq = sum(c["a"]["games"] == c["b"]["games"] for c in dq["conflicts"])
        points_eq = sum(c["a"]["points"] == c["b"]["points"] for c in dq["conflicts"])
        assert (games_eq, points_eq, len(dq["conflicts"]) - games_eq - points_eq) == (21, 19, 54)


class TestConflictRowsAreTheRowsOnThePlayerPage:
    def test_alvin_cruz_2005_is_no_longer_a_conflict(self, dq):
        """It was: jug05's "2005" row (24/211) is the ficha's 2006 row under the capture-relative label
        (docs/specs/jug05_offset_check.md). After the relabel it folds into 2006 and the ficha's 2005 row stands."""
        assert [c for c in dq["conflicts"] if c["id"] == 74] == []
        rows = [(r["season"], r["games"], r["points"]) for r in _player(74)["career"] if r["season"] in (2005, 2006)]
        assert rows == [(2005, 11, 134), (2006, 24, 211)]

    def test_each_conflict_side_is_exactly_one_career_row_in_the_player_file(self, dq):
        for c in dq["conflicts"]:
            rows = _player(c["id"])["career"]
            for k in ("a", "b"):
                hit = [r for r in rows if r["season"] == c["season"] and r["franchise_id"] == c["franchise_id"]
                       and (r["games"], r["points"], r["team_raw"]) == (c[k]["games"], c[k]["points"], c[k]["team"])]
                assert len(hit) == 1, (c["id"], c["season"], k)

    def test_every_source_is_an_internet_archive_capture(self, dq):
        assert all(c[k]["url"].startswith("https://web.archive.org/web/") for c in dq["conflicts"] for k in ("a", "b"))

    def test_the_totals_rule_alvin_cruz_and_the_double_count(self, dq):
        def totals(pid):
            rows = _player(pid)["career"]
            flagged = set()
            for c in (c for c in dq["conflicts"] if c["id"] == pid):
                for i, r in enumerate(rows):
                    if r["season"] == c["season"] and r["franchise_id"] == c["franchise_id"] and any(
                            (r["games"], r["points"], r["team_raw"]) == (c[k]["games"], c[k]["points"], c[k]["team"]) for k in "ab"):
                        flagged.add(i)
            kept = [r for i, r in enumerate(rows) if i not in flagged]
            return (sum(r["points"] or 0 for r in kept), sum(r["games"] or 0 for r in kept),
                    sum(r["points"] or 0 for r in rows), sum(r["games"] or 0 for r in rows), len(flagged))
        assert totals(74) == (2119, 373, 2119, 373, 0)            # 1,985 / 362 while the 2005 row was a conflict
        assert totals(1995) == (4339, 460, 4339, 460, 0)          # was 4,300 / 455 while jug05's 24/194 (= 5/39 + 19/155) was a conflict
        # every conflict flags exactly two rows
        for pid in {c["id"] for c in dq["conflicts"]}:
            assert totals(pid)[4] == 2 * sum(1 for c in dq["conflicts"] if c["id"] == pid)


class TestOnlyRecordedFactsAndSpanishText:
    def test_the_public_decision_text_is_the_owner_approved_wording(self, dq):
        text = {d["id"]: d["text_es"] for d in dq["decisions"]}
        assert text["D-ID-001"] == ("Cinco de las seis filas del ID 73 son idénticas a las del ID 74. Ambas fichas tienen la misma "
                                    "fecha de nacimiento (24 de abril de 1982). El listado de bsnpr.com dejó de incluir el ID 73 "
                                    "en 2008 y ningún juego tiene ambos IDs.")
        assert text["D-ID-002"] == ("La única fila del ID 951 es idéntica a la de 2002 del ID 952. El listado de bsnpr.com dejó de "
                                    "incluir el ID 951 en 2008 y ningún juego tiene ambos IDs.")
        assert text["D-ID-003"] == ("El ID 24 es la ficha vacía del ID 35: misma fecha de nacimiento en el listado de 2007 de "
                                    "bsnpr.com y el mismo número de camiseta (11) en 76 de las 77 capturas de la enciclopedia.")
        assert text["D-ID-004"] == ("Los IDs 35 y 273 aparecen juntos en 20 juegos de Santurce (2001-03), con camisetas distintas "
                                    "(10 y 7) y minutos distintos. Son personas distintas y no se unen.")

    def test_only_the_four_recorded_decisions_are_published(self, dq):
        assert [(d["id"], d["kind"], d["ids"], d["survivor_id"]) for d in dq["decisions"]] == [
            ("D-ID-001", "merge", [73, 74], 74), ("D-ID-002", "merge", [951, 952], 952),
            ("D-ID-003", "merge", [24, 35], 35), ("D-ID-004", "not_same", [35, 273], None)]
        assert set(dq) == {"schema_version", "counts", "conflicts", "decisions", "dob_open", "season_totals", "relabeled",
                      "foreign_rows"}   # no heuristic classes, no stub twins

    def test_no_wikipedia_claim_or_url_and_never_the_word_error(self):
        text = DQ.read_text(encoding="utf-8")
        assert not re.search(r"wikipedia", text, re.I) and not re.search(r"\berror\b", text, re.I)
        # a capture URL embeds the original bsnpr.com address; every URL must be an archive capture
        assert not re.findall(r'(?<!/)https?://(?!web\.archive\.org/web/)', text.replace("id_/http://", "id_/"))

    def test_the_decisions_csv_keeps_its_attribution_and_gains_the_public_column(self):
        rows = _csv("clean", "player_identity_decisions.csv")
        assert list(rows[0]) == apply.DECISION_COLUMNS and "evidence_es" in apply.DECISION_COLUMNS
        d4 = next(r for r in rows if r["decision_id"] == "D-ID-004")
        assert "en.wikipedia.org/wiki/Carlos_Arroyo" in d4["evidence"] and "wikipedia" not in d4["evidence_es"].lower()

    def test_birth_dates_are_shown_as_recorded(self, dq):
        assert [(d["id"], d["canonical"], d["jugador05"]) for d in dq["dob_open"]] == [
            (139, "6/21/1975", "6/9/1975"), (812, "1/29/1982", "1/30/1982"), (911, "7/3/1973", "8/3/1973"),
            (2016, "5/7/1973", "7/5/1973"), (2090, "5/28/1975", "3/28/1975")]
        assert "dob_corrections" in dq["counts"] and "corrections" not in dq          # a count, not a list

    def test_validate_requires_the_spanish_text_and_refuses_a_wikipedia_claim_in_it(self):
        d = {"decision_id": "D-1", "kind": "merge", "ids": "73;74", "survivor_id": "74", "status": "applied", "evidence": "e",
             "evidence_es": "Texto.", "source_doc": "d", "decided_by": "owner", "decided_at": "2026-09-21"}
        tomb = [{"retired_id": "73", "survivor_id": "74", "decision_id": "D-1", "retired_name": "x", "retired_at": "t"}]
        assert apply.validate([d], tomb) == []
        assert any("evidence_es" in p for p in apply.validate([{**d, "evidence_es": ""}], tomb))
        assert any("Wikipedia" in p for p in apply.validate([{**d, "evidence_es": "Según Wikipedia."}], tomb))


class TestDigest:
    def test_an_interim_log_is_a_digest_input(self, tmp_path, monkeypatch):
        for name in ("CLEAN", "APP", "INTERIM"):
            (tmp_path / name).mkdir()
            monkeypatch.setattr(bwd, name, tmp_path / name)
        (tmp_path / "CLEAN" / "a.csv").write_text("x\n")
        (tmp_path / "INTERIM" / "log.csv").write_text("1\n")
        before = bwd._source_digest(["a.csv", "log.csv"])
        (tmp_path / "INTERIM" / "log.csv").write_text("2\n")
        assert bwd._source_digest(["a.csv", "log.csv"]) != before

    def test_clean_wins_over_app_over_interim(self, tmp_path, monkeypatch):
        for name in ("CLEAN", "APP", "INTERIM"):
            (tmp_path / name).mkdir()
            monkeypatch.setattr(bwd, name, tmp_path / name)
        (tmp_path / "INTERIM" / "f.csv").write_text("interim\n")
        (tmp_path / "APP" / "f.csv").write_text("app\n")
        (tmp_path / "CLEAN" / "f.csv").write_text("clean\n")
        d = bwd._source_digest(["f.csv"])
        (tmp_path / "INTERIM" / "f.csv").write_text("changed\n")
        (tmp_path / "APP" / "f.csv").write_text("changed\n")
        assert bwd._source_digest(["f.csv"]) == d

    def test_the_five_logs_exist_and_are_listed(self):
        assert bwd.DQ_INTERIM_LOGS == ["jug05_career_conflicts.csv", "jug05_career_merged.csv", "player_merge_dropped_rows.csv",
                                       "jugador05_dob_conflicts.csv", "player_dob_overrides.csv",
                                       "jug05_season_totals.csv", "jug05_relabeled_rows.csv", "jug05_foreign_rows.csv"]
        assert all((REPO_ROOT / "data" / "interim" / n).exists() for n in bwd.DQ_INTERIM_LOGS)


class TestTheAppView:
    def _block(self):
        text = APP.read_text(encoding="utf-8")
        return text, text[text.index("CALIDAD DE DATOS — #archivo/calidad"):text.index("async function loadPlayerExtra(")]

    def test_menu_view_and_lede(self):
        text, _ = self._block()
        assert "['Calidad de datos','calidad']" in text and "['Calidad de datos',['calidad','Calidad de datos']]" in text
        assert ("Dónde las fuentes no coinciden y qué hicimos con cada caso. El archivo muestra las dos cifras; "
                "no escoge una a ojo.") in text
        assert "if(sec==='archivo'&&now==='calidad') openDQ();" in text and "['calidad de datos',buildDQ]" in text

    def test_the_view_never_says_error_and_names_no_wikipedia(self):
        text, block = self._block()
        view = text[text.index('<h3 class="sec">Calidad de datos</h3>'):text.index('<h3 class="sec">Calendario y cobertura')]
        for s in (block, view):
            assert not re.search(r"\berror\b", s, re.I) and "wikipedia" not in s.lower()

    def test_totals_exclude_both_rows_of_a_conflicted_season_and_say_so(self):
        text, _ = self._block()
        assert "const fl=car.map(c=>dqFlag(id,c));" in text
        assert "car.forEach((c,i)=>{ if(fl[i]) return; if(c.points!=null)tp+=c.points;" in text
        assert "Totales sin ${nConf} temporada${nConf===1?'':'s'} con fuentes en conflicto" in text
        assert "ver Calidad de datos" in text
        assert "const [d]=await Promise.all([DATA.get('players/'+id+'.json'), ensureDQ()]);" in text

    def test_birth_dates_stay_in_the_recorded_format(self):
        text, _ = self._block()
        assert "formato M/D/AAAA" in text and "fmtLongDate(x.decided_at)" in text
        assert "MESES" not in text[text.index("function drawDQ("):text.index("function drawDQTable(")].replace("fmtLongDate", "")

    def test_the_web_copy_is_a_byte_copy(self):
        assert (REPO_ROOT / "web" / "index.html").read_bytes() == APP.read_bytes()


class TestSeasonTotalsAndRelabelNotes:
    """The two notes in the view and the rows behind them (docs/specs/data_quality_view_spec.md sections 7 and 8)."""

    def test_the_counts_and_the_published_rows(self, dq):
        n = dq["counts"]
        assert n["season_totals"] == len(dq["season_totals"]) == len(_csv("interim", "jug05_season_totals.csv")) == 13
        assert n["relabeled"] == len(dq["relabeled"]) == len(_csv("interim", "jug05_relabeled_rows.csv")) == 145
        assert {(r["old_season"], r["new_season"]) for r in dq["relabeled"]} == {(2005, 2006)}
        assert min(r["capture_date"] for r in dq["relabeled"]) == "2006-05-28"

    def test_each_season_total_is_the_sum_of_per_team_rows_that_stay(self, dq):
        for t in dq["season_totals"]:
            assert len(t["ficha"]) >= 2 and len({f["team"] for f in t["ficha"]}) >= 2      # a player who changed team
            assert (sum(f["games"] for f in t["ficha"]), sum(f["points"] for f in t["ficha"])) == (
                t["jug05"]["games"], t["jug05"]["points"]) == (t["sum"]["games"], t["sum"]["points"])
            rows = [r for r in _player(t["id"])["career"] if r["season"] == t["season"]]
            for f in t["ficha"]:
                assert any((r["team_raw"], r["games"], r["points"]) == (f["team"], f["games"], f["points"]) for r in rows)
            assert not any(r["team_raw"] == t["jug05"]["team"] for r in rows)                # the total left the file
        assert [t["id"] for t in dq["season_totals"]] == [151, 193, 284, 763, 777, 808, 870, 932, 985, 1284, 1462, 1995, 2067]

    def test_the_two_notes_read_as_approved_and_are_driven_by_the_counts(self):
        text = APP.read_text(encoding="utf-8")
        assert ("En ${nf(c.season_totals)} casos la fila de jug05 es el total de la temporada de un jugador que cambió de "
                "equipo. El archivo conserva las filas por equipo y registra el total como corroboración.") in text
        assert ("En las capturas de jug05 a partir de mayo de 2006, la temporada más reciente conserva la etiqueta 2005. "
                "En 100 de ${nf(c.relabeled)} filas las cifras coinciden con la temporada 2006 de la ficha del jugador. "
                "Reasignamos las ${nf(c.relabeled)} a 2006 y publicamos el registro.") in text
        assert "c.season_totals?" in text and "c.relabeled?" in text

    def test_ids_81_and_1066_and_the_2000_2003_conflicts_stay_conflicts(self, dq):
        assert {81, 1066} <= {c["id"] for c in dq["conflicts"] if c["season"] == 2006}
        assert sum(1 for c in dq["conflicts"] if 2000 <= c["season"] <= 2003) == 89

    def test_the_100_in_the_relabel_note_is_the_relabelled_rows_that_equal_a_ficha_2006_row(self, dq):
        ficha = {}
        for r in _csv("clean", "player_career_seasons.csv"):
            if r["source_id"] == "wayback_bsnpr_players" and r["season"] == "2006":
                ficha.setdefault(r["bsnpr_id"], set()).add((r["games"], r["points"]))
        rows = _csv("interim", "jug05_relabeled_rows.csv")
        assert len(rows) == 145
        assert sum(1 for r in rows if (r["games"], r["points"]) in ficha.get(r["bsnpr_id"], ())) == 100


class TestForeignRowsNote:
    """The note about jug05 rows that showed another player's line (docs/specs/foreign_slot_check.md)."""

    def test_the_counts_and_the_published_rows(self, dq):
        n = dq["counts"]
        assert n["foreign_rows"] == len(dq["foreign_rows"]) == len(_csv("interim", "jug05_foreign_rows.csv")) == 5
        assert sorted((r["id"], r["season"], r["team"], r["games"], r["points"]) for r in dq["foreign_rows"]) == [
            (4, 2006, "BAYAMON", 24, 211), (49, 2001, "COAMO", 11, 18), (49, 2001, "PONCE", 3, 0),
            (313, 2006, "GUAYAMA", 9, 6), (1208, 2006, "GUAYNABO", 9, 43)]
        assert len({r["id"] for r in dq["foreign_rows"]}) == 4
        assert all(r["evidence"].strip() and r["owner_name"] and r["url"].startswith("https://web.archive.org/") for r in dq["foreign_rows"])

    def test_each_foreign_row_is_gone_and_is_a_row_of_the_owner(self, dq):
        for r in dq["foreign_rows"]:
            mine = [(x["season"], x["team_raw"], x["games"], x["points"]) for x in _player(r["id"])["career"]]
            assert (r["season"], r["team"], r["games"], r["points"]) not in mine
            theirs = [(x["season"], x["games"], x["points"]) for x in _player(r["owner_id"])["career"]]
            assert (r["season"], r["games"], r["points"]) in theirs

    def test_the_note_reads_as_approved_and_is_driven_by_the_counts(self):
        text = APP.read_text(encoding="utf-8")
        assert ("En ${nf(c.foreign_rows)} filas de ${nf(new Set((d.foreign_rows||[]).map(x=>x.id)).size)} jugadores, una página de "
                "jug05 mostraba la línea de otro jugador. Las quitamos de la ficha y de los totales y publicamos el registro. "
                "No podemos detectar los casos cuyo dueño no tiene captura.") in text
        assert "c.foreign_rows?" in text

