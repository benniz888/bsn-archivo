"""Unit coverage for the D1 name-normalisation + matching helpers in
src/parse_players.py. The end-to-end build is checked by `make parse-players`
+ `make verify`.
"""

from src.parse_players import (
    clean_field, extract_nickname, normalize, norm_key, strip_accents,
    strip_nickname, _load_club_resolver, _J05_BLOCK, _J05_TEAMNUM, merge_jugador05,
    apply_dob_overrides,
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

    def test_dob_settled_suppresses_conflict(self):
        canon = [self._canon(birth_date="4/3/1980", birth_year="1980")]
        r = merge_jugador05(canon, [self._bio()], dob_settled={"1"})
        assert r["dob_conflicts"] == []          # id 1 already adjudicated


class TestDobOverrides:
    def test_applies_only_on_matching_old_value(self, tmp_path, monkeypatch):
        import src.parse_players as P
        (tmp_path / "player_dob_overrides.csv").write_text(
            "bsnpr_id,canonical_name,old_dob,new_dob,confidence,basis\n"
            '1,"A, B",11/1/1981,1/11/1981,high,"swap"\n'
            '2,"C, D",9/9/1990,1/1/1991,low,"stale expected"\n')
        monkeypatch.setattr(P, "INTERIM_DIR", tmp_path)
        canon = [{"bsnpr_id": "1", "birth_date": "11/1/1981", "birth_year": "1981"},
                 {"bsnpr_id": "2", "birth_date": "5/5/1985", "birth_year": "1985"}]
        done = P.apply_dob_overrides(canon)
        assert canon[0]["birth_date"] == "1/11/1981" and canon[0]["birth_year"] == "1981"
        assert canon[1]["birth_date"] == "5/5/1985"   # stale old_dob -> not touched
        assert done == {"1", "2"}                     # both are "settled" for conflict-logging


class TestHistoricSeed:
    def test_title_uniquely_seeds_span(self, tmp_path, monkeypatch):
        import src.parse_players as P
        clean = tmp_path / "clean"; interim = tmp_path / "interim"; app = tmp_path / "app"
        clean.mkdir(); interim.mkdir(); app.mkdir()
        (clean / "historic_scoring_champions.csv").write_text(
            "season,player_raw,team_raw\n1948,RAUL FELICIANO,UPR\n1955,RAUL FELICIANO,UPR\n"
            "1999,ANTHONY FARMER,PONCE\n")
        (clean / "scoring_champions_reconciled.csv").write_text(
            "season,historic_player\n1948,RAUL FELICIANO\n")
        (interim / "player_historic_seed.csv").write_text(
            "observed_name,bsnpr_id,confidence,note\nANTHONY FARMER,172,low,dup pick\n")
        (app / "player_crosswalk.csv").write_text(
            "curated_name,bsnpr_id,verdict\n")
        monkeypatch.setattr(P, "CLEAN_DIR", clean)
        monkeypatch.setattr(P, "INTERIM_DIR", interim)
        monkeypatch.setattr(P, "REPO_ROOT", tmp_path)
        canon = [
            {"bsnpr_id": "1943", "canonical_name": "Feliciano Rodriguez, Raul",
             "first_season": "", "last_season": "", "n_seasons": ""},
            {"bsnpr_id": "171", "canonical_name": "Farmer, Anthony",
             "first_season": "", "last_season": "", "n_seasons": ""},
            {"bsnpr_id": "172", "canonical_name": "Farmer, Anthony",
             "first_season": "", "last_season": "", "n_seasons": ""},
        ]
        aliases = [
            {"bsnpr_id": "1943", "alias": "Feliciano, Raul", "normalized_alias": "feliciano, raul"},
            {"bsnpr_id": "171", "alias": "Farmer, Anthony", "normalized_alias": "farmer, anthony"},
            {"bsnpr_id": "172", "alias": "Farmer, Anthony", "normalized_alias": "farmer, anthony"},
        ]
        n = P.seed_historic_spans(canon, aliases)
        by = {c["bsnpr_id"]: c for c in canon}
        assert (by["1943"]["first_season"], by["1943"]["last_season"]) == ("1948", "1955")
        assert by["1943"]["n_seasons"] == ""                       # not a season count
        # Farmer: two canonical rows share the name -> ambiguous, so the seed
        # override picks 172 and only 172 gets the span
        assert (by["172"]["first_season"], by["172"]["last_season"]) == ("1999", "1999")
        assert by["171"]["first_season"] == ""
        assert n == 2
