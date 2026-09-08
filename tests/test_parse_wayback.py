"""Unit coverage for the pure parse helpers in src/parse_wayback.py.

The end-to-end parse itself is exercised by `make parse` + `make verify` against
the real raw captures; these tests pin the tricky string/encoding logic.
"""

import pandas as pd
import pytest

from src.parse_wayback import (
    classify_leader_table,
    clean_equipo,
    decode_html,
    parse_season_cell,
    split_annotation,
    split_player_cell,
    to_float,
    to_int,
    wayback_ts_to_date,
    _season_complete,
)

KNOWN_CITIES = {"SAN JUAN", "CANOVANAS", "PONCE", "VEGA BAJA"}


class TestDecodeHtml:
    def test_utf8(self):
        assert decode_html("Añasco".encode("utf-8")) == "Añasco"

    def test_latin1_spanish(self):
        assert decode_html("PEÑUELAS".encode("latin-1")) == "PEÑUELAS"

    def test_utf8_with_one_bad_byte_when_page_declares_utf8(self):
        raw = b'<meta charset="utf-8">A\xc3\x91O ' + b"\x81" + b" SAN GERM\xc3\x81N"
        out = decode_html(raw)
        assert "AÑO" in out and "GERMÁN" in out

    def test_never_raises(self):
        assert isinstance(decode_html(b"\xff\xfe\x81\x9d"), str)


class TestNumbers:
    @pytest.mark.parametrize("raw,exp", [("19", 19), ("1.0", 1), ("453", 453), ("", None),
                                         ("nan", None), ("-", None), ("x", None)])
    def test_to_int(self, raw, exp):
        assert to_int(raw) == exp

    @pytest.mark.parametrize("raw,exp", [("23.8", 23.8), ("88.6", 88.6), ("", None), ("-", None)])
    def test_to_float(self, raw, exp):
        assert to_float(raw) == exp

    def test_zero_stays_zero_but_blank_is_none(self):
        # PC2: a real 0 is data; a blank is NULL
        assert to_int("0") == 0
        assert to_int("") is None


class TestSeasonCell:
    def test_plain_year(self):
        assert parse_season_cell("1966") == "1966"

    def test_split_season_kept(self):
        assert parse_season_cell("1942-1943") == "1942-1943"

    def test_strips_spaces_in_split(self):
        assert parse_season_cell("1942 - 1943") == "1942-1943"

    def test_ts_to_date(self):
        assert wayback_ts_to_date("20170804230003") == "2017-08-04"


class TestCleanEquipo:
    def test_normal(self):
        assert clean_equipo("SAN GERMAN") == ("SAN GERMAN", "", False)

    def test_asterisk_marks_no_champion(self):
        city, note, no_champ = clean_equipo("* NO SE TERMINÓ (PONCE VS SAN GERMAN)")
        assert city is None and no_champ is True
        assert "NO SE TERMIN" in note

    def test_bare_asterisk(self):
        assert clean_equipo("*")[2] is True


class TestSplitAnnotation:
    def test_known_city_untouched(self):
        assert split_annotation("SAN JUAN", KNOWN_CITIES) == ("SAN JUAN", "")

    def test_annotation_split_off_when_tail_is_a_city(self):
        city, note = split_annotation("COPA OLIMPICA - CANOVANAS", KNOWN_CITIES)
        assert city == "CANOVANAS"
        assert "COPA OLIMPICA" in note

    def test_unknown_left_whole(self):
        assert split_annotation("TORTUGUERO", KNOWN_CITIES) == ("TORTUGUERO", "")


class TestClassifyLeaderTable:
    def _cols(self, *mid):
        return ["#", "Jugador", "JJ", *mid, "Prom"]

    def test_anotaciones(self):
        assert classify_leader_table(self._cols("Tot")) == ("anotaciones", "per_game", "Tot", True)

    def test_rebotes(self):
        cat, kind, _, known = classify_leader_table(self._cols("Def", "Off", "Tot"))
        assert (cat, kind, known) == ("rebotes", "per_game", True)

    def test_free_throw_pct_is_percentage(self):
        cat, kind, _, _ = classify_leader_table(self._cols("TLI", "TLA"))
        assert (cat, kind) == ("tiros_libres_pct", "percentage")

    def test_unknown_signature_kept_but_flagged(self):
        cat, kind, cols, known = classify_leader_table(self._cols("SCP"))
        assert known is False and kind == "unknown" and cat == "cat_scp" and cols == "SCP"

    def test_not_a_leader_table(self):
        assert classify_leader_table(["AÑO", "EQUIPO", "DIRIGENTE"]) is None


class TestSplitPlayerCell:
    def test_club_with_city(self):
        assert split_player_cell("Figueroa, Angel Luis (Capitanes, Arecibo)") == (
            "Figueroa, Angel Luis", "Capitanes, Arecibo")

    def test_empty_club(self):
        assert split_player_cell("Melendez, Wilfredo ()") == ("Melendez, Wilfredo", "")

    def test_truncated_nickname_bleeds_into_name(self):
        # the ragged reality — resolve later (D1), never at ingest
        assert split_player_cell("Morales, Mario 'Qui (Mets)") == ("Morales, Mario 'Qui", "Mets")

    def test_no_parens(self):
        assert split_player_cell("Frazer, Rolando") == ("Frazer, Rolando", "")


class TestSeasonComplete:
    def test_capture_after_season_year_is_complete(self):
        assert _season_complete("1986", "20170804230003") is True

    def test_autumn_capture_same_year_is_complete(self):
        assert _season_complete("2021", "20211026051849") is True

    def test_midseason_capture_is_not(self):
        assert _season_complete("2013", "20130526035153") is False
