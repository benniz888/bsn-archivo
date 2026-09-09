"""Unit coverage for the D1 name-normalisation + matching helpers in
src/parse_players.py. The end-to-end build is checked by `make parse-players`
+ `make verify`.
"""

from src.parse_players import (
    extract_nickname, normalize, norm_key, strip_accents, strip_nickname,
    _load_club_resolver,
)


class TestStripAccents:
    def test_spanish(self):
        assert strip_accents("Álamo López Ángel") == "Alamo Lopez Angel"

    def test_enye(self):
        assert strip_accents("Peñuelas") == "Penuelas"


class TestNormalize:
    def test_lower_accent_punct(self):
        assert normalize("Álamo López, Ángel 'Junito'") == "alamo lopez, angel junito"

    def test_initial_form(self):
        assert normalize("Ayuso, E.") == "ayuso, e"

    def test_collapses_space(self):
        assert normalize("  Cruz   Torres ,  Alvin ") == "cruz torres , alvin"


class TestNormKey:
    def test_order_insensitive(self):
        assert norm_key("Ayuso Carrillo, Elias") == norm_key("Elias Ayuso Carrillo")

    def test_comma_insensitive(self):
        assert norm_key("Carmona, Alejandro") == norm_key("Alejandro Carmona")


class TestNickname:
    def test_extract_single_quote(self):
        assert extract_nickname("Ayuso Carrillo, Elias 'Larry'") == "Larry"

    def test_extract_curly(self):
        assert extract_nickname("Acevedo, Angel ‘Mutombo’") == "Mutombo"

    def test_none(self):
        assert extract_nickname("Carmona Sanchez, Alejandro") == ""

    def test_strip(self):
        assert strip_nickname("Ayuso Carrillo, Elias 'Larry'") == "Ayuso Carrillo, Elias"

    def test_strip_keeps_plain(self):
        assert strip_nickname("Carmona Sanchez, Alejandro") == "Carmona Sanchez, Alejandro"


class TestClubResolver:
    """PHASE_3F — club_raw -> stable franchise key, consistent across the many
    representations (5-char code, 'Nick de City', 'Nick, City', bare). Runs
    against the real data/clean/ code+city+franchise maps."""

    R = staticmethod(_load_club_resolver())

    def test_five_char_code(self):
        assert self.R("QUEBR") == self.R("Piratas de Quebradillas")

    def test_two_letter_code(self):
        assert self.R("SA") == self.R("Cangrejeros de Santurce")

    def test_city_and_full_name_agree(self):
        assert self.R("PONCE") == self.R("Leones de Ponce") != ""

    def test_nick_city_matches_career_comma_form(self):
        # observation "Nick de City" vs career-table "Nick, City"
        assert self.R("Vaqueros de Bayamon") == self.R("Vaqueros, Bayamon")

    def test_bare_unambiguous_nickname(self):
        assert self.R("Vaqueros") == self.R("Vaqueros de Bayamon")

    def test_empty(self):
        assert self.R("") == ""

    def test_unknown_is_stable_not_crash(self):
        assert isinstance(self.R("Fictional de Nowhere"), str)
