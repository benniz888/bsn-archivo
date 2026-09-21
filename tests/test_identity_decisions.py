"""Curated identity decisions (src/apply_identity_decisions.py). Fixture tests pin the transformation and the
guards; TestCommittedData checks the committed decisions, tombstones and the state the apply script left."""

import csv

import pytest

from src import apply_identity_decisions as apply
from src.parse_players import SOURCE_ID, JUG05_SOURCE_ID
from src.wayback_cdx import REPO_ROOT

TOMB = [{"retired_id": "73", "survivor_id": "74", "decision_id": "D-1", "retired_name": "Cruz, Alvin",
         "retired_at": "2026-09-21"}]
URL73, URL74 = "https://x/jugador.asp?id=73", "https://x/jugador.asp?id=74"


def _career(pid, season, team, games, points, source=SOURCE_ID, url=None):
    return {"bsnpr_id": pid, "season": season, "team_raw": team, "games": games, "points": points,
            "source_id": source, "source_url": url or f"https://x/jugador.asp?id={pid}", "retrieved_at": "t"}


def _tables(**over):
    t = {
        "canonical": (["bsnpr_id", "canonical_name"], [{"bsnpr_id": "73", "canonical_name": "Cruz, Alvin"},
                                                        {"bsnpr_id": "74", "canonical_name": "Cruz Torres, Alvin"}]),
        "aliases": (["bsnpr_id", "alias", "normalized_alias", "alias_type", "source"], [
            {"bsnpr_id": "73", "alias": "Cruz, Alvin", "normalized_alias": "cruz, alvin", "alias_type": "canonical", "source": "s"},
            {"bsnpr_id": "73", "alias": "Cruz, A.", "normalized_alias": "cruz, a.", "alias_type": "initial", "source": "s"},
            {"bsnpr_id": "74", "alias": "Cruz, A.", "normalized_alias": "cruz, a.", "alias_type": "initial", "source": "s"}]),
        "id_map": (["bsnpr_id", "canonical_name"], []),
        "bios": (["bsnpr_id", "notes_es"], []),
        "career": (list(_career("1", "2000", "x", "1", "1")), [
            _career("73", "2000", "Vaqueros, Bayamon", "8", "9", url=URL73),        # identical to 74's: dropped
            _career("73", "2005", "BAYAMON", "24", "211", JUG05_SOURCE_ID, URL73),  # no twin: carried, then a conflict
            _career("74", "2000", "Vaqueros, Bayamon", "8", "9", url=URL74),
            _career("74", "2005", "Vaqueros, Bayamon", "11", "134", url=URL74)]),
        "roster": (["bsnpr_id", "season", "franchise_id"], [{"bsnpr_id": "73", "season": "2010", "franchise_id": "leones_ponce"}]),
        "box": (["bsnpr_id"], []), "crosswalk": (["bsnpr_id", "canonical_name"], []),
        "review": (["candidate_ids", "club_match_ids", "candidate_names"],
                   [{"candidate_ids": "73|74", "club_match_ids": "73|74", "candidate_names": "Cruz, Alvin | Cruz Torres, Alvin"}]),
        "merged_log": (["bsnpr_id", "season", "franchise_id", "games", "points", "players_source_url", "jug05_source_url",
                        "jug05_team_raw", "jug05_retrieved_at"], []),
    }
    t.update(over)
    return t


class TestApply:
    def test_the_retired_id_is_removed_and_what_it_owned_moves_to_the_survivor(self):
        new, dropped, merged, conflicts, counts = apply.apply(_tables(), TOMB)
        assert [r["bsnpr_id"] for r in new["canonical"][1]] == ["74"]
        aliases = {(r["bsnpr_id"], r["alias"], r["alias_type"]) for r in new["aliases"][1]}
        assert aliases == {("74", "Cruz, Alvin", "merged_name"), ("74", "Cruz, A.", "initial")}   # duplicate dropped
        assert new["roster"][1] == [{"bsnpr_id": "74", "season": "2010", "franchise_id": "leones_ponce"}]
        assert new["review"][1][0]["candidate_ids"] == "74" and new["review"][1][0]["club_match_ids"] == "74"
        assert new["review"][1][0]["candidate_names"] == "Cruz Torres, Alvin"
        assert counts["canonical rows removed"] == 1 and counts["alias rows dropped as duplicates"] == 1

    def test_an_identical_career_row_is_dropped_and_logged_and_the_rest_carries_over(self):
        new, dropped, merged, conflicts, counts = apply.apply(_tables(), TOMB)
        assert [(r["retired_id"], r["season"], r["source_url"]) for r in dropped] == [("73", "2000", URL73)]
        assert dropped[0]["decision_id"] == "D-1" and dropped[0]["survivor_id"] == "74"
        rows = {(r["bsnpr_id"], r["season"], r["source_id"]) for r in new["career"][1]}
        assert rows == {("74", "2000", SOURCE_ID), ("74", "2005", SOURCE_ID), ("74", "2005", JUG05_SOURCE_ID)}
        assert len(conflicts) == 1 and (conflicts[0]["games_a"], conflicts[0]["games_b"]) == (11, 24)

    def test_a_jug05_row_identical_to_the_survivors_players_row_is_folded_and_logged(self):
        t = _tables(career=(_tables()["career"][0], [
            _career("73", "1998", "BAYAMON", "9", "12", JUG05_SOURCE_ID, URL73),
            _career("74", "1998", "Vaqueros, Bayamon", "9", "12", url=URL74)]))
        new, dropped, merged, conflicts, counts = apply.apply(t, TOMB)
        assert [(m["bsnpr_id"], m["season"], m["players_source_url"]) for m in merged] == [("74", 1998, URL74)]
        assert len(new["career"][1]) == 1 and conflicts == []

    def test_the_merged_log_follows_the_survivors_twin_row(self):
        log = {"bsnpr_id": "73", "season": "2000", "franchise_id": "vaqueros_bayamon", "games": "8", "points": "9",
               "players_source_url": URL73, "jug05_source_url": "u", "jug05_team_raw": "BAYAMON", "jug05_retrieved_at": "t"}
        t = _tables(merged_log=(_tables()["merged_log"][0], [log]))
        new = apply.apply(t, TOMB)[0]
        assert new["merged_log"][1][0]["bsnpr_id"] == "74" and new["merged_log"][1][0]["players_source_url"] == URL74

    def test_the_inputs_are_not_mutated_and_a_second_pass_changes_nothing(self):
        t = _tables()
        before = {k: [dict(r) for r in rows] for k, (_, rows) in t.items()}
        new = apply.apply(t, TOMB)[0]
        assert {k: rows for k, (_, rows) in t.items()} == before
        again = apply.apply(new, TOMB)
        assert {k: rows for k, (_, rows) in again[0].items()} == {k: rows for k, (_, rows) in new.items()}
        assert again[1] == [] and again[2] == []

    def test_a_survivor_that_already_has_a_bio_is_a_decision_for_a_person(self):
        bios = (["bsnpr_id", "notes_es"], [{"bsnpr_id": "73", "notes_es": "a"}, {"bsnpr_id": "74", "notes_es": "b"}])
        with pytest.raises(ValueError, match="already has a bio"):
            apply.apply(_tables(bios=bios), TOMB)

    def test_roster_rows_that_would_collide_are_an_error_not_silently_dropped(self):
        row = {"bsnpr_id": "74", "season": "2010", "franchise_id": "leones_ponce"}
        roster = (["bsnpr_id", "season", "franchise_id"], [{**row, "bsnpr_id": "73"}, row])
        with pytest.raises(ValueError, match="collide"):
            apply.apply(_tables(roster=roster), TOMB)

    def test_a_survivor_that_is_not_a_canonical_row_is_an_error(self):
        with pytest.raises(ValueError, match="not a canonical row"):
            apply.apply(_tables(), [{**TOMB[0], "survivor_id": "999"}])


def _decision(**kw):
    d = {"decision_id": "D-1", "kind": "merge", "ids": "73;74", "survivor_id": "74", "status": "applied", "evidence": "e",
         "source_doc": "d", "decided_by": "owner", "decided_at": "2026-09-21"}
    d.update(kw)
    return d


class TestValidate:
    def test_a_consistent_pair_of_files_has_no_problems(self):
        assert apply.validate([_decision()], TOMB) == []

    def test_a_tombstone_must_cite_a_merge_that_retires_it(self):
        assert apply.validate([_decision(kind="not_same", survivor_id="")], TOMB)
        assert apply.validate([_decision(survivor_id="73")], TOMB)
        assert apply.validate([], TOMB)

    def test_no_chains_and_no_retiring_twice(self):
        chain = TOMB + [{**TOMB[0], "retired_id": "74", "survivor_id": "75", "decision_id": "D-2"}]
        assert any("itself retired" in p for p in apply.validate([_decision(), _decision(decision_id="D-2", ids="74;75", survivor_id="75")], chain))
        assert any("twice" in p for p in apply.validate([_decision()], TOMB + TOMB))

    def test_a_not_same_pair_can_never_be_merged(self):
        ns = _decision(decision_id="D-2", kind="not_same", ids="73;74", survivor_id="")
        assert any("not the same person" in p for p in apply.validate([_decision(), ns], TOMB))

    def test_evidence_and_provenance_are_required(self):
        assert any("evidence" in p for p in apply.validate([_decision(evidence=" ")], TOMB))
        assert any("decided_by" in p for p in apply.validate([_decision(decided_by="")], TOMB))


def _rd(name, folder="clean"):
    with (REPO_ROOT / "data" / folder / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


class TestCommittedData:
    def test_the_committed_decisions_and_tombstones_are_valid(self):
        decisions, tombs = apply.load_decisions(), apply.load_tombstones()
        assert apply.validate(decisions, tombs) == []
        assert [(d["decision_id"], d["kind"], d["ids"]) for d in decisions] == [
            ("D-ID-001", "merge", "73;74"), ("D-ID-002", "merge", "951;952"),
            ("D-ID-003", "merge", "24;35"), ("D-ID-004", "not_same", "35;273")]
        assert {t["retired_id"]: t["survivor_id"] for t in tombs} == {"73": "74", "951": "952", "24": "35"}

    def test_the_not_same_row_for_35_and_273_carries_its_evidence(self):
        d = next(d for d in apply.load_decisions() if d["kind"] == "not_same")
        for needle in ("20 Santurce games", "jerseys 10 and 7", "1-17", "20-38", "Carlos Alberto Arroyo Bermudez",
                       "7/30/1979", "en.wikipedia.org/wiki/Carlos_Arroyo", "not independently fetched"):
            assert needle in d["evidence"], needle

    def test_no_retired_id_is_left_in_the_identity_files_and_the_apply_script_agrees(self):
        retired = {t["retired_id"] for t in apply.load_tombstones()}
        for name in ("players_canonical.csv", "player_aliases.csv", "player_id_map.csv", "player_bios.csv",
                     "player_career_seasons.csv", "player_roster_latinbasket.csv"):
            assert not [r for r in _rd(name) if r["bsnpr_id"] in retired], name
        assert apply.main(["--check"]) == 0

    def test_player_273_is_untouched(self):
        assert [r["canonical_name"] for r in _rd("players_canonical.csv") if r["bsnpr_id"] == "273"] == ["Arroyo Bermúdez, Carlos A."]
        assert sum(1 for r in _rd("player_career_seasons.csv") if r["bsnpr_id"] == "273") == 10

    def test_the_dropped_rows_are_logged_with_their_provenance(self):
        rows = _rd("player_merge_dropped_rows.csv", "interim")
        assert [(r["retired_id"], r["season"]) for r in rows] == [("73", "2000"), ("73", "2001"), ("73", "2002"), ("951", "2002")]
        assert all(r["source_url"] and r["retrieved_at"] and r["decision_id"] for r in rows)
