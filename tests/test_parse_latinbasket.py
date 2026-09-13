"""Unit coverage for src/parse_latinbasket.py's pure helpers.

Fixtures are minimal hand-built HTML fragments that reproduce the two real
shapes seen in the archived pages: a single "BSN Standings" table (2014-
2017) and a two-group "BSN Stage Two Standings" table (2018) with a
"Group A" / "Group B" divider row nested inside the same header.
"""

from bs4 import BeautifulSoup

from src.fetch_latinbasket import _is_legacy_asp, _year_of
from src.parse_latinbasket import _extract_table

SINGLE_TABLE_HTML = """
<table class="ctrtbl"><tr><td class="ctrtd">BSN Standings</td></tr>
<tr><td bgcolor="#eef2d2"><table>
<tr><td align="left">&nbsp;1.&nbsp;<a href="http://basketball.latinbasket.com/team/Puerto-Rico/Capitanes_de_Arecibo/2187?Year=2014">Arecibo</a></td>
<td align="right">23-13&nbsp;</td></tr>
<tr><td align="left">&nbsp;2.&nbsp;<a href="http://basketball.latinbasket.com/team/Puerto-Rico/Leones_de_Ponce/1954?Year=2014">Ponce</a></td>
<td align="right">22-14&nbsp;</td></tr>
</table></td></tr></table>
"""

TWO_GROUP_HTML = """
<table class="ctrtbl"><tr><td class="ctrtd">BSN Stage Two Standings</td></tr>
<tr><td bgcolor="#eef2d2"><table>
<tr><td colspan="3" bgcolor="#95c936"><font>Group A</font></td></tr>
<tr><td align="left">1.<a href="http://basketball.latinbasket.com/team/Puerto-Rico/Vaqueros-de-Bayamon/1677?Year=2018">Bayamon</a></td>
<td align="right">4-3</td></tr>
<tr><td align="left">2.<a href="http://basketball.latinbasket.com/team/Puerto-Rico/Leones-de-Ponce/1954?Year=2018">Ponce</a></td>
<td align="right">4-3</td></tr>
<tr><td colspan="3" bgcolor="#95c936"><font>Group B</font></td></tr>
<tr><td align="left">1.<a href="http://basketball.latinbasket.com/team/Puerto-Rico/Capitanes-de-Arecibo/2187?Year=2018">Arecibo</a></td>
<td align="right">4-3</td></tr>
</table></td></tr></table>
"""


class TestExtractTable:
    def test_single_table_basic(self):
        soup = BeautifulSoup(SINGLE_TABLE_HTML, "lxml")
        rows = _extract_table(soup, "BSN Standings")
        assert rows == [(1, "Arecibo", 23, 13, None), (2, "Ponce", 22, 14, None)]

    def test_missing_header_returns_empty(self):
        soup = BeautifulSoup(SINGLE_TABLE_HTML, "lxml")
        assert _extract_table(soup, "Nonexistent Header") == []

    def test_two_group_table_splits_correctly(self):
        """Regression test for the wrapper-row bug: an early version of the
        parser walked every <tr> at any depth, including the intermediate
        wrapper <tr> that contains the whole nested <table> — whose
        concatenated .get_text() false-matched both the group divider check
        and the first team's record, producing a spurious extra row with
        group=None ahead of the real, correctly-grouped rows."""
        soup = BeautifulSoup(TWO_GROUP_HTML, "lxml")
        rows = _extract_table(soup, "BSN Stage Two Standings")
        assert rows == [
            (1, "Bayamon", 4, 3, "a"),
            (2, "Ponce", 4, 3, "a"),
            (1, "Arecibo", 4, 3, "b"),
        ]
        # the specific bug: no row should ever have group=None here
        assert all(g is not None for *_, g in rows)

    def test_dedupes_repeated_team_within_same_group(self):
        html = SINGLE_TABLE_HTML.replace("</table></td></tr></table>",
            '<tr><td align="left">1.<a href="http://basketball.latinbasket.com/team/Puerto-Rico/Capitanes_de_Arecibo/2187?Year=2014">Arecibo</a></td>'
            '<td align="right">99-99</td></tr></table></td></tr></table>')
        soup = BeautifulSoup(html, "lxml")
        rows = _extract_table(soup, "BSN Standings")
        arecibo_rows = [r for r in rows if r[1] == "Arecibo"]
        assert len(arecibo_rows) == 1
        assert arecibo_rows[0] == (1, "Arecibo", 23, 13, None)  # first occurrence wins


class TestYearOf:
    def test_legacy_asp(self):
        assert _year_of("http://www.latinbasket.com:80/Puerto-Rico/basketball-League-BSN_2014.asp") == "2014"

    def test_redesign_aspx_lowercase(self):
        assert _year_of("https://www.latinbasket.com/Puerto-Rico/basketball-league-bsn_2020.aspx") == "2020"


class TestIsLegacyAsp:
    def test_asp_is_legacy(self):
        assert _is_legacy_asp("http://www.latinbasket.com:80/Puerto-Rico/basketball-League-BSN_2014.asp") is True

    def test_aspx_is_not_legacy(self):
        assert _is_legacy_asp("https://www.latinbasket.com/Puerto-Rico/basketball-league-bsn_2020.aspx") is False
