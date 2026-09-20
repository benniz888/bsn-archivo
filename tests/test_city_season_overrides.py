"""Season-scoped city overrides: loader validation, lookup boundaries, and the
contract that both city -> franchise resolvers read the same data (audit F9)."""

import pytest

from src import build_web_data as b
from src import parse_players as pp
from src.city_season_overrides import OVERRIDES_FILE, load_overrides, override_for
from src.wayback_cdx import REPO_ROOT

REAL = REPO_ROOT / "data" / "clean" / OVERRIDES_FILE
HEADER = "city,season_start,season_end,franchise_id,evidence\n"


def _load(tmp_path, body, norm=str.lower):
    p = tmp_path / "overrides.csv"
    p.write_text(HEADER + body, encoding="utf-8")
    return load_overrides(p, norm)


class TestLoader:
    def test_closed_and_open_ended_ranges(self, tmp_path):
        ov = _load(tmp_path, "MANATI,2015,2016,a,why\nMANATI,2023,,b,why\n")
        assert ov == {"manati": [(2015, 2016, "a"), (2023, None, "b")]}

    def test_city_key_uses_the_callers_normalizer(self, tmp_path):
        ov = _load(tmp_path, "MANATÍ,2015,2016,a,why\n", norm=b._norm)
        assert list(ov) == ["manati"]

    @pytest.mark.parametrize("body, msg", [
        ("MANATI,2015,2016,a,\n", "required"),                 # PC3: no evidence
        ("MANATI,2015,2016,,why\n", "required"),
        (",2015,2016,a,why\n", "required"),
        ("MANATI,20x5,2016,a,why\n", "must be years"),
        ("MANATI,2015,20x6,a,why\n", "must be years"),
        ("MANATI,2016,2015,a,why\n", "before"),
        ("MANATI,2015,2016,a,why\nMANATI,2016,2017,b,why\n", "overlapping"),
        ("MANATI,2015,,a,why\nMANATI,2023,,b,why\n", "overlapping"),  # open range swallows the next
    ])
    def test_rejects_bad_rows(self, tmp_path, body, msg):
        with pytest.raises(ValueError, match=msg):
            _load(tmp_path, body)

    def test_rejects_missing_column(self, tmp_path):
        p = tmp_path / "overrides.csv"
        p.write_text("city,season_start,franchise_id,evidence\nMANATI,2015,a,why\n", encoding="utf-8")
        with pytest.raises(ValueError, match="missing columns"):
            load_overrides(p, str.lower)


class TestLookup:
    OV = {"manati": [(2015, 2016, "a"), (2023, None, "b")]}

    @pytest.mark.parametrize("season, want", [
        (2014, None), (2015, "a"), (2016, "a"), (2017, None),
        (2022, None), (2023, "b"), (2099, "b"), ("2015", "a"), (" 2016 ", "a"),
    ])
    def test_boundaries(self, season, want):
        assert override_for(self.OV, "manati", season) == want

    @pytest.mark.parametrize("season", [None, "", "unknown", "1942-1943"])
    def test_missing_or_non_year_season_never_matches(self, season):
        assert override_for(self.OV, "manati", season) is None

    def test_unknown_city(self):
        assert override_for(self.OV, "ponce", 2015) is None


class TestRealOverrides:
    def test_every_override_targets_a_real_franchise(self):
        known = {r["franchise_id"] for r in b._read("franchises.csv")}
        ov = load_overrides(REAL, b._norm)      # also proves the file has no overlaps
        assert {fid for spans in ov.values() for *_, fid in spans} <= known

    def test_only_archive_supported_manati_ranges(self):
        # 2014 and 2017 are UNVERIFIED (audit F5); widening needs a source.
        assert load_overrides(REAL, b._norm) == {
            "manati": [(2015, 2016, "atenienses_manati"), (2023, None, "osos_manati")]}


class TestResolversAgree:
    """build_web_data._team_resolver and parse_players._load_club_resolver read
    the same override data, so they cannot disagree about an era."""

    @pytest.mark.parametrize("raw", ["MANATI", "Manati", "PONCE", "SANTURCE", "HUMACAO"])
    @pytest.mark.parametrize("season", [None, 2014, 2015, 2016, 2017, 2023, 2024])
    def test_bare_city_agrees(self, raw, season):
        assert b._team_resolver()(raw, season) == pp._load_club_resolver()(raw, season)

    def test_club_resolver_is_era_aware_for_bare_city(self):
        club = pp._load_club_resolver()
        assert club("MANATI", 2016) == "atenienses_manati"
        assert club("MANATI", 2023) == "osos_manati"
        assert club("MANATI") == "osos_manati"          # season omitted: unchanged

    def test_nickname_form_resolves_to_atenienses_with_or_without_season(self):
        club = pp._load_club_resolver()
        assert club("Atenienses, Manati") == club("Atenienses, Manati", 2016) == "atenienses_manati"

    def test_every_real_manati_career_row_agrees(self):
        web, club = b._team_resolver(), pp._load_club_resolver()
        rows = [r for r in b._read("player_career_seasons.csv") if "manat" in r["team_raw"].lower()]
        assert rows
        for r in rows:
            season = int(r["season"])
            assert (web(r["team_raw"].split(",")[-1], season) == club(r["team_raw"], season)
                    == "atenienses_manati"), r
