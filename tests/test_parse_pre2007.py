"""Unit coverage for the pure helpers in src/parse_pre2007.py.

The full parse is exercised by `make parse-pre2007` + `make verify` against the
real captures; these pin the fiddly bits.
"""

from bs4 import BeautifulSoup

from src.parse_pre2007 import (
    _PRE_CATEGORY, _PRE_ROW, _db_error, _section_for, _split_att_made, _team_and_season,
)


class TestPreLeaderRow:
    def test_full_name_with_club_code(self):
        m = _PRE_ROW.match(" 1.  Ayuso, Larry               (SAN G)    26      580      22.3")
        assert m.groups() == ("1", "Ayuso, Larry", "SAN G", "26", "580", "22.3")

    def test_surname_only(self):
        m = _PRE_ROW.match(" 3.  Simpson        (CAROL)    28      566      20.2")
        assert m.group(2) == "Simpson" and m.group(3) == "CAROL"

    def test_multi_stat_middle(self):
        m = _PRE_ROW.match(" 1.  Davis, Nick   (MOROV)    22    294   104   398   18.1")
        assert m.group(4) == "22" and m.group(5).split() == ["294", "104", "398"]

    def test_category_signature(self):
        assert _PRE_CATEGORY[("TP",)] == ("anotaciones", "per_game")
        assert _PRE_CATEGORY[("TLI", "TLA")] == ("tiros_libres_pct", "percentage")


class TestSplitAttMade:
    def test_att_first_made_second(self):
        assert _split_att_made("151-90") == (151, 90)

    def test_spaces(self):
        assert _split_att_made(" 32 - 18 ") == (32, 18)

    def test_zero(self):
        assert _split_att_made("0-0") == (0, 0)

    def test_blank(self):
        assert _split_att_made("") == (None, None)

    def test_garbage(self):
        assert _split_att_made("nan") == (None, None)


class TestDbError:
    def test_adodb(self):
        assert _db_error("<html>ADODB.Field error '800a0bcd'</html>") is True

    def test_bof_eof(self):
        assert _db_error("Either BOF or EOF is True") is True

    def test_clean_page(self):
        assert _db_error("<table><tr><td>PUNTOS ACUMULADOS</td></tr></table>") is False


class TestSectionFor:
    def _t(self, heading):
        html = f"<p>{heading}</p><table><tr><td>x</td></tr></table>"
        return BeautifulSoup(html, "html.parser").find("table")

    def test_scoring(self):
        assert _section_for(self._t("CAMPEONES ANOTADORES DEL BALONCESTO")) == "scoring"

    def test_mvp(self):
        assert _section_for(self._t("JUGADOR MAS VALIOSO BALONCESTO SUPERIOR NACIONAL")) == "mvp"

    def test_rookie_accent_insensitive(self):
        assert _section_for(self._t("NOVATO DEL AÑO BALONCESTO")) == "rookie"

    def test_none_when_no_heading(self):
        assert _section_for(self._t("Some unrelated caption")) is None


class TestTeamAndSeason:
    def test_heading(self):
        soup = BeautifulSoup("<h1>Vaqueros de Bayamon 2001</h1> Serie: Serie Regular", "html.parser")
        team, season, serie = _team_and_season(soup)
        assert team == "Vaqueros de Bayamon" and season == "2001" and serie == "Serie Regular"

    def test_no_match(self):
        assert _team_and_season(BeautifulSoup("<p>nothing here</p>", "html.parser")) == ("", "", "")
