"""Unit coverage for the pure helpers in src/parse_games.py."""

from src.parse_games import _num_pair, _reb_pair, _season_from_rid, _split_jugador


class TestSeasonFromRid:
    def test_2001(self):
        assert _season_from_rid("BS21001") == 2001

    def test_2008(self):
        assert _season_from_rid("BS28152") == 2008

    def test_junk(self):
        assert _season_from_rid("") is None


class TestNumPair:
    def test_att_made(self):
        assert _num_pair("19-7") == (19, 7)

    def test_spaces(self):
        assert _num_pair(" 52 - 23 ") == (52, 23)

    def test_zero(self):
        assert _num_pair("0-0") == (0, 0)

    def test_blank(self):
        assert _num_pair("") == (None, None)


class TestRebPair:
    def test_slash(self):
        assert _reb_pair("10/15", "/") == (10, 15)

    def test_blank(self):
        assert _reb_pair("nan", "/") == (None, None)


class TestSplitJugador:
    def test_jersey_and_name(self):
        assert _split_jugador("23 Brown, Gerald") == ("23", "Brown, Gerald")

    def test_single_digit(self):
        assert _split_jugador("4 Western, Franklyn") == ("4", "Western, Franklyn")

    def test_no_jersey(self):
        assert _split_jugador("Total:") == ("", "Total:")
