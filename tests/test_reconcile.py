"""Unit coverage for the pure helpers in src/reconcile.py."""

from src.reconcile import OWNER_RESOLUTIONS, ncity, resolve_city, resolve_seed_name


class TestOwnerResolutions:
    def test_1936_and_1968_resolved_to_agree(self):
        assert OWNER_RESOLUTIONS[("champion", "1936")]["kind"] == "agree"
        assert OWNER_RESOLUTIONS[("runner_up", "1968")]["kind"] == "agree"

    def test_scoring_1971_1974_dual_metric(self):
        assert OWNER_RESOLUTIONS[("scoring_champion", "1971")]["kind"] == "dual_metric"
        assert OWNER_RESOLUTIONS[("scoring_champion", "1974")]["kind"] == "dual_metric"

    def test_1945_has_no_resolution(self):
        assert ("champion", "1945") not in OWNER_RESOLUTIONS


class TestNcity:
    def test_accent_and_case(self):
        assert ncity("Bayamón") == "BAYAMON"

    def test_dots_to_space(self):
        assert ncity("FCLA.MARTIN") == "FCLA MARTIN"

    def test_collapse_space(self):
        assert ncity("  San   German ") == "SAN GERMAN"


class TestResolveCity:
    def test_clean_map(self):
        fid, disp, unmapped = resolve_city("SAN GERMAN", "1942")
        assert fid == "atleticos_san_german" and not disp and not unmapped

    def test_san_juan_default(self):
        assert resolve_city("SAN JUAN", "1930")[0] == "capitalinos_san_juan"

    def test_san_juan_1936_no_longer_a_city_dispute(self):
        # 1936 is handled by OWNER_RESOLUTIONS now, not a CITY_MAP dispute
        fid, disp, unmapped = resolve_city("SAN JUAN", "1936")
        assert fid == "capitalinos_san_juan" and not disp

    def test_san_juan_1945_d5_dispute(self):
        _, disp, _ = resolve_city("SAN JUAN", "1945")
        assert "D5" in disp

    def test_fcla_martin_unmapped_not_dispute(self):
        fid, disp, unmapped = resolve_city("FCLA. MARTIN", "1936")
        assert not fid and not disp and "Fcla. Martin" in unmapped

    def test_unknown_city_unmapped(self):
        fid, disp, unmapped = resolve_city("NOWHERE", "2001")
        assert not fid and not disp and "no city->franchise mapping" in unmapped

    def test_accent_variant(self):
        assert resolve_city("BAYAMÓN", "2020")[0] == "vaqueros_bayamon"


class TestResolveSeedName:
    def test_exact(self):
        assert resolve_seed_name("Atleticos de San German") == "atleticos_san_german"

    def test_accent_insensitive(self):
        assert resolve_seed_name("Atléticos de San Germán") == "atleticos_san_german"

    def test_extra_name(self):
        assert resolve_seed_name("Santos de San Juan") == "santos_san_juan"

    def test_blank(self):
        assert resolve_seed_name("") == ""
