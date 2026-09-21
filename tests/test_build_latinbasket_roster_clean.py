"""Unit coverage for src/build_latinbasket_roster_clean.py's pure `promote()`.

Fixtures are minimal hand-built row dicts, not the real 934-row corpus —
same convention as test_parse_latinbasket.py.
"""

from src.build_latinbasket_roster_clean import promote


def _match_row(name_raw, season, tier, candidate_ids, disposition):
    return {
        "season": season, "name_raw": name_raw, "tier": tier,
        "candidate_ids": candidate_ids, "disposition": disposition,
    }


def _raw_row(franchise_id, season, name_raw, **overrides):
    row = {
        "franchise_id": franchise_id, "season": season, "name_raw": name_raw,
        "jersey_number": "23", "height_cm": "198", "position_raw": "G/F",
        "source_url": "http://example/roster", "retrieved_at": "20200101000000",
    }
    row.update(overrides)
    return row


class TestPromote:
    def test_confirmed_row_promotes_with_raw_fields(self):
        match_rows = {"vaqueros_bayamon": [
            _match_row("Jesse Pellot-Rosa", "2016", "2_approx_birth_confirmed", "2354", "confirmed_match"),
        ]}
        raw_idx = {("vaqueros_bayamon", "2016", "Jesse Pellot-Rosa"):
                   _raw_row("vaqueros_bayamon", "2016", "Jesse Pellot-Rosa")}
        out = promote(match_rows, raw_idx)
        assert len(out) == 1
        row = out[0]
        assert row["bsnpr_id"] == "2354"
        assert row["franchise_id"] == "vaqueros_bayamon"
        assert row["jersey_number"] == "23"
        assert row["height_cm"] == "198"
        assert row["position_raw"] == "G/F"
        assert row["source_id"] == "latinbasket"
        assert row["confidence"] == "single-source"

    def test_insufficient_evidence_row_never_promoted(self):
        match_rows = {"cariduros_fajardo": [
            _match_row("Someone Unmatched", "2018", "5_no_canonical_match", "", "insufficient_evidence"),
        ]}
        raw_idx = {("cariduros_fajardo", "2018", "Someone Unmatched"):
                   _raw_row("cariduros_fajardo", "2018", "Someone Unmatched")}
        assert promote(match_rows, raw_idx) == []

    def test_lead_and_distinct_dispositions_never_promoted(self):
        match_rows = {"santeros_aguada": [
            _match_row("Figueroa Carlos Manual", "2016", "4_ambiguous_multi_candidate",
                       "286;333;2631", "lead_for_tier1_triage"),
            _match_row("Raymond Dalmau", "2017", "4_ambiguous_multi_candidate",
                       "1962;1970", "likely_distinct_not_in_canonical"),
        ]}
        raw_idx = {
            ("santeros_aguada", "2016", "Figueroa Carlos Manual"):
                _raw_row("santeros_aguada", "2016", "Figueroa Carlos Manual"),
            ("santeros_aguada", "2017", "Raymond Dalmau"):
                _raw_row("santeros_aguada", "2017", "Raymond Dalmau"),
        }
        assert promote(match_rows, raw_idx) == []

    def test_duplicate_pair_confirmed_row_uses_lower_id(self):
        """Cruz Alvin (73/74), Lopez Ivan (951/952), Rivera Raul (1947/1948) —
        kept confirmed_match by owner decision despite two candidate ids
        (a likely pre-existing canonical duplicate, not a real tie). Written
        deterministically under the lower id, never the higher one."""
        match_rows = {"leones_ponce": [
            _match_row("Cruz Alvin", "2010", "1_exact_birth_confirmed", "74;73", "confirmed_match"),
        ]}
        raw_idx = {("leones_ponce", "2010", "Cruz Alvin"):
                   _raw_row("leones_ponce", "2010", "Cruz Alvin")}
        out = promote(match_rows, raw_idx)
        assert len(out) == 1
        assert out[0]["bsnpr_id"] == "73"

    def test_a_tombstoned_pair_is_written_under_its_survivor(self):
        """73 was merged into 74 (data/clean/player_id_tombstones.csv): the lower id no longer wins."""
        match_rows = {"leones_ponce": [
            _match_row("Cruz Alvin", "2010", "1_exact_birth_confirmed", "74;73", "confirmed_match"),
            _match_row("Lopez Ivan", "2013", "1_exact_birth_confirmed", "951;952", "confirmed_match"),
        ]}
        raw_idx = {("leones_ponce", "2010", "Cruz Alvin"): _raw_row("leones_ponce", "2010", "Cruz Alvin"),
                   ("leones_ponce", "2013", "Lopez Ivan"): _raw_row("leones_ponce", "2013", "Lopez Ivan")}
        out = promote(match_rows, raw_idx, {"73": "74", "951": "952"})
        assert [r["bsnpr_id"] for r in out] == ["74", "952"]
        assert [r["bsnpr_id"] for r in promote(match_rows, raw_idx)] == ["73", "951"]     # default unchanged

    def test_missing_raw_row_is_fatal_not_silently_dropped(self):
        match_rows = {"vaqueros_bayamon": [
            _match_row("Ghost Player", "2016", "1_exact_birth_confirmed", "1", "confirmed_match"),
        ]}
        try:
            promote(match_rows, raw_idx={})
        except SystemExit as exc:
            assert "could not be traced back" in str(exc)
        else:
            raise AssertionError("expected SystemExit when a confirmed row has no raw match")

    def test_null_jersey_number_stays_blank_not_fabricated(self):
        """A real gap in the source (no jersey shown for this player) must
        stay blank in the clean file, never coalesced to 0 or a placeholder
        (PC2)."""
        match_rows = {"vaqueros_bayamon": [
            _match_row("No Jersey Player", "2016", "1_exact_birth_confirmed", "1", "confirmed_match"),
        ]}
        raw_idx = {("vaqueros_bayamon", "2016", "No Jersey Player"):
                   _raw_row("vaqueros_bayamon", "2016", "No Jersey Player", jersey_number="")}
        out = promote(match_rows, raw_idx)
        assert out[0]["jersey_number"] == ""
