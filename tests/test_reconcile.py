"""Unit coverage for the pure helpers in src/reconcile.py, plus a drift guard
tying the generator's output to the committed CSVs."""

import csv
import shutil

import pytest

import src.reconcile as rc
from src.reconcile import (FRANCHISE_EVENTS, FRANCHISE_SOURCES, FRANCHISES, OWNER_RESOLUTIONS,
                           ncity, resolve_city, resolve_seed_name)
from src.wayback_cdx import REPO_ROOT

REPO_CLEAN = REPO_ROOT / "data" / "clean"
_INPUTS = ("bsn_champions_by_season.csv", "champions_from_bsnpr.csv",
           "historic_scoring_champions.csv", "bsn_scoring_champions.csv",
           "player_season_leaders.csv")
_OUTPUTS = ("franchises.csv", "franchise_events.csv", "city_franchise_map.csv",
            "club_code_map.csv", "champions_reconciled.csv",
            "scoring_champions_reconciled.csv", "reconcile_conflicts.csv")


def _rows(path):
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


@pytest.fixture(scope="module")
def regenerated(tmp_path_factory):
    """One full reconcile run into a temp dir, never over data/clean."""
    out = tmp_path_factory.mktemp("reconcile_out")
    for name in _INPUTS:
        shutil.copy(REPO_CLEAN / name, out / name)
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(rc, "CLEAN", out)
        assert rc.main() == 0
    return out


class TestGeneratorMatchesCommittedCsvs:
    """The committed CSVs are the source of truth (owner decision 2026-09-19:
    commit 77a3aae edited them by hand, so the generator had drifted). If this
    fails, either a CSV was hand-edited or reconcile.py changed without the
    other. Compared as parsed rows so redundant CSV quoting is not drift."""

    @pytest.mark.parametrize("name", _OUTPUTS)
    def test_output_matches(self, regenerated, name):
        assert _rows(regenerated / name) == _rows(REPO_CLEAN / name)


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


class TestHumacaoLineage:
    """D-045: the 2005-19 Humacao chain and the 2021 Grises expansion are two
    franchises. Pinned individually so a failure names the drifted fact."""

    def test_humacao_city_is_caciques_with_no_dispute(self):
        fid, disp, unmapped = resolve_city("HUMACAO", "2010")
        assert fid == "caciques_humacao" and not disp and not unmapped

    def test_caciques_is_a_named_franchise(self):
        assert resolve_seed_name("Caciques de Humacao") == "caciques_humacao"
        assert FRANCHISES["caciques_humacao"][2] == "2005"

    def test_grises_is_the_2021_expansion(self):
        _, _, founded, status = FRANCHISES["grises_humacao"]
        assert founded == "2021" and "criollos_caguas" in status

    def test_grises_to_criollos_dated_2024_not_2023(self):
        renames = [e for e in FRANCHISE_EVENTS
                   if e[2] == "grises_humacao" and e[3] == "criollos_caguas"]
        assert [(e[1], e[4]) for e in renames] == [("2024", "verified")]

    def test_toritos_to_caciques_2005_event(self):
        assert any(e[:4] == ("relocated_renamed", "2005", "toritos_cayey", "caciques_humacao")
                   for e in FRANCHISE_EVENTS)


class TestAteniensesRelocation:
    """N5: Atenienses de Manati did not disappear in 2017, it moved to Fajardo.
    Pinned individually so a failure names the drifted fact."""

    def test_status_is_a_relocation_to_fajardo(self):
        assert FRANCHISES["atenienses_manati"][3] == "relocated 2017 -> Fajardo"

    def test_status_keeps_exactly_one_four_digit_year(self):
        # build_franchises() derives `end` from every digit in the status; any
        # other digit would silently fall back to the curated end.
        status = FRANCHISES["atenienses_manati"][3]
        assert "".join(ch for ch in status if ch.isdigit()) == "2017"

    def test_founded_is_kept(self):
        assert FRANCHISES["atenienses_manati"][2] == "2014"

    def test_source_records_provenance_and_that_urls_were_not_fetched(self):
        src = FRANCHISE_SOURCES["atenienses_manati"]
        assert "2026-09-20" in src and "not independently fetched" in src
        for part in ("primerahora.com", "wikipedia:Cariduros_de_Fajardo",
                     "wikipedia:2016_Baloncesto_Superior_Nacional_season",
                     "wikipedia:2017_Baloncesto_Superior_Nacional_season"):
            assert part in src

    def test_regenerated_franchise_row(self, regenerated):
        row = next(r for r in _rows(regenerated / "franchises.csv")
                   if r["franchise_id"] == "atenienses_manati")
        assert row["status"] == "relocated 2017 -> Fajardo" and row["founded"] == "2014"
        assert row["source"] == FRANCHISE_SOURCES["atenienses_manati"]


class TestSeedSourceOverrides:
    """F8: the 2024 runner-up was confirmed from the 2024 season page."""

    SEASON_PAGE = "en.wikipedia.org/wiki/2024_Baloncesto_Superior_Nacional_season"

    def test_2024_credits_the_season_page_and_keeps_the_runner_up(self, regenerated):
        row = next(r for r in _rows(regenerated / "champions_reconciled.csv")
                   if r["season"] == "2024")
        assert row["sources"] == self.SEASON_PAGE
        assert row["champion_franchise_id"] == "criollos_caguas"
        assert row["runner_up_franchise_id"] == "osos_manati"

    def test_no_other_season_cites_the_2024_page(self, regenerated):
        others = [r["season"] for r in _rows(regenerated / "champions_reconciled.csv")
                  if r["season"] != "2024" and self.SEASON_PAGE in r["sources"]]
        assert others == []

    def test_seed_csv_cell_agrees(self):
        seed = next(r for r in _rows(REPO_CLEAN / "bsn_champions_by_season.csv")
                    if r["season"] == "2024")
        assert seed["source"] == self.SEASON_PAGE
