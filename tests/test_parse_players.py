"""Unit coverage for the D1 name-normalisation + matching helpers in
src/parse_players.py. The end-to-end build is checked by `make parse-players`
+ `make verify`.
"""

from src.parse_players import (
    clean_field, extract_nickname, normalize, norm_key, strip_accents,
    strip_nickname, _load_club_resolver, _J05_BLOCK, _J05_TEAMNUM, merge_jugador05,
)


class TestCleanField:
    def test_placeholders_become_empty(self):
        for junk in ("nan", "No se sabe", "Estadísticas Jugador", "—", "-", ""):
            assert clean_field(junk) == ""

    def test_real_values_pass_through(self):
        assert clean_field("  Armador ") == "Armador"
        assert clean_field("Puerto Rico") == "Puerto Rico"
        assert clean_field("Buchanan") == "Buchanan"   # contains "nan", not a sentinel


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


class TestJugador05Block:
    TXT = ("Reglas del Torneo Historia Enlaces Foros Jugador PONCE 05 - Casiano , "
           "Eddie Origen: Manhattan, New York Edad: 32 Fecha: 9/20/1972 Altura: 6-3 "
           "Peso: 200 Posición: Escolta Notas Sobresalientes: Vasta experiencia en "
           "el BSN. © 2005 Baloncesto Superior Nacional")

    def test_fields(self):
        m = _J05_BLOCK.search(self.TXT)
        assert m and m.group("ape") == "Casiano" and m.group("nom") == "Eddie"
        team = _J05_TEAMNUM.sub("", m.group("team").strip())
        assert team == "PONCE"
        assert m.group("fecha") == "9/20/1972"
        assert m.group("pos").strip() == "Escolta"
        assert m.group("notas").startswith("Vasta experiencia")

    def test_all_labels_empty(self):
        txt = ("Foros Jugador ISABELA 15 - Rodriguez , Israel Origen: Edad: Fecha: "
               "Altura: 6-0 Peso: 170 Posición: Escolta Notas Sobresalientes: © x")
        m = _J05_BLOCK.search(txt)
        assert m and m.group("origen") == "" and m.group("fecha") == ""
        assert m.group("notas") == ""


class TestMergeJugador05:
    def _canon(self, **kw):
        base = dict(bsnpr_id="1", canonical_name="Perez, Juan", apellidos="Perez",
                    nombre="Juan", birth_date="", birth_year="", birth_city="",
                    nationality="", position="")
        base.update(kw)
        return base

    def _bio(self, **kw):
        base = dict(name="Perez, Juan", apellidos="Perez", nombre="Juan",
                    birth_date="3/4/1980", position="Escolta", birth_city="Ponce, Puerto Rico",
                    nationality="Puerto Rico", roster_team="PONCE", roster_year="2005",
                    jersey="7", notes_es="Buen tirador.", source_url="http://wb/x", retrieved_at="t")
        base.update(kw)
        return base

    def test_fills_only_empty_fields_and_never_mints(self):
        canon = [self._canon()]
        r = merge_jugador05(canon, [self._bio()])
        assert len(canon) == 1                       # no mint
        assert r["matched"] == 1 and r["filled"] >= 3
        assert canon[0]["birth_date"] == "3/4/1980" and canon[0]["position"] == "Escolta"
        assert len(r["bio_rows"]) == 1

    def test_does_not_overwrite_and_flags_dob_conflict(self):
        # same birth year, transposed month/day -> matched, flagged, not overwritten
        canon = [self._canon(birth_date="4/3/1980", birth_year="1980", position="Centro")]
        r = merge_jugador05(canon, [self._bio()])
        assert canon[0]["birth_date"] == "4/3/1980" and canon[0]["position"] == "Centro"
        assert r["dob_conflicts"] and r["dob_conflicts"][0]["jugador05_dob"] == "3/4/1980"

    def test_no_match_goes_to_review(self):
        r = merge_jugador05([self._canon(canonical_name="Otro, Nombre", apellidos="Otro", nombre="Nombre")],
                            [self._bio()])
        assert r["matched"] == 0 and len(r["review_list"]) == 1
