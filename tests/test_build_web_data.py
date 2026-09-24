"""PHASE_5 / 5B — unit coverage for the web/data build helpers.
The end-to-end build is exercised by `make build-web-data` + `verify_web_data`
in `make verify`; these pin the value coercion, the crosswalk assert, and the
deterministic JSON writer.
"""

import csv
import json

import pytest

from src import build_web_data as b


class TestCoerce:
    def test_int(self):
        assert b._int("1974") == 1974
        assert b._int("") is None
        assert b._int(None) is None
        assert b._int("  ") is None
        assert b._int("22.4") is None      # not an int -> None, never 0 (PC2)
        assert b._int("-1") == -1

    def test_float(self):
        assert b._float("22.4") == 22.4
        assert b._float("23.456") == 23.46
        assert b._float("") is None
        assert b._float("x") is None


class TestJdump:
    def test_deterministic_and_sorted(self, tmp_path):
        p = tmp_path / "x.json"
        b._jdump({"b": 1, "a": [3, 1, 2]}, p)
        first = p.read_bytes()
        b._jdump({"a": [3, 1, 2], "b": 1}, p)   # different insertion order
        assert p.read_bytes() == first
        assert p.read_text().startswith('{"a":[3,1,2],"b":1}')
        assert p.read_text().endswith("\n")


class TestCrosswalk:
    def test_loads_and_is_complete(self):
        app_to_fid, fid_to_app = b.load_crosswalk()   # sys.exit on an incomplete map
        assert len(app_to_fid) == 33
        assert app_to_fid["bay"] == "vaqueros_bayamon"
        assert app_to_fid["cac"] == "caciques_humacao"   # 5B-FIX
        assert fid_to_app["osos_manati"] == "man"

    def test_every_app_key_has_curated_fields(self):
        assert b._app_keys() == set(b.load_crosswalk()[0])


class TestBuild:
    """Runs the real build once against data/clean/ and checks the outputs."""

    @staticmethod
    @pytest.fixture(scope="class", autouse=True)
    def _build():
        assert b.main() == 0

    def test_franchises_index(self):
        fr = json.loads((b.WEB / "index" / "franchises.json").read_text())
        assert len(fr) == 33
        bay = next(f for f in fr if f["app_key"] == "bay")
        assert bay["franchise_id"] == "vaqueros_bayamon"
        assert bay["colors"]["src"] == "wiki"
        assert "2020" in bay["titles"] and "2023" in bay["finals_lost"]
        # defunct franchise carries an end year, active carries null
        man = next(f for f in fr if f["app_key"] == "man")
        assert man["status"] == "active" and man["end"] is None
        guy = next(f for f in fr if f["app_key"] == "guy")
        assert guy["status"] == "defunct" and isinstance(guy["end"], int)

    def test_scoring_titles_dual(self):
        st = json.loads((b.WEB / "index" / "scoring_titles.json").read_text())
        d71 = next(r for r in st if r["season"] == 1971)
        assert d71["agreement"] == "dual_metric_d4"
        assert d71["champion"] is None
        assert d71["dual"]["ppg"]["player"] == "Teofilo Cruz"
        assert d71["dual"]["total_points"]["value"] == 566
        # 5D.2 — club on every entry
        assert d71["dual"]["ppg"]["franchise_id"] == "cangrejeros_santurce"
        s67 = next(r for r in st if r["season"] == 1967)
        assert s67["champion"]["club_raw"] == "Capitalinos de San Juan"
        assert s67["champion"]["franchise_id"] == "capitalinos_san_juan"
        resolved = sum(1 for r in st if (r["champion"] or {}).get("franchise_id")
                       or (r["dual"] or {}).get("ppg", {}).get("franchise_id"))
        assert resolved >= 0.9 * len(st)
        # PHASE_3I — historic champions now carry a bsnpr_id (title attestation)
        s48 = next(r for r in st if r["season"] == 1948)
        assert s48["champion"]["player"] == "RAUL FELICIANO"
        assert s48["champion"]["bsnpr_id"] == 1943
        with_id = sum(1 for r in st if (r["champion"] or {}).get("bsnpr_id")
                      or (r["dual"] or {}).get("ppg", {}).get("bsnpr_id"))
        assert with_id >= 0.85 * len(st)

    def test_players_index(self):
        pl = json.loads((b.WEB / "index" / "players.json").read_text())
        # 3303 league ids + 40 jug05-minted (D-047) + 9 pabellon_hof/wikipedia_bsn-minted
        # (D-048/D-049/D-050, 991001-991009) + 2 pabellon_hof-minted (T9.4, 991010-991011:
        # Jimmy Thordsen, Martin Ansa) + 3 wikipedia_bsn-minted (T9.5, 991012-991014:
        # Bonzi Wells, Leon Smith, Tyler Hines) - 1 (991001 Dalmau Perez, Raymond merged
        # into the existing 1962, a duplicate D-048 missed; 2026-09-14 identity fix)
        # - 9 (systematic canonical-file duplicate scan, 2026-09-14: 990017/990018/
        # 990025/990030/990034/990038 (jug05-minted, D-047) and 991005/991006/991011
        # (D-050/T9.4) each confirmed the same person as a pre-existing regular id via
        # exact birth-date match, merged into the regular id in every case)
        # - 1 (990001 Berdiel, Miguel Alí -> the pre-existing 1666, confirmed via an
        # identical career trajectory rather than birth date, same duplicate scan)
        # - 13 (individually reviewed weaker candidates, 2026-09-14: each confirmed via
        # a real (season, city) career-row overlap -- or, for 991004, an exact
        # canonical_name match plus a matching career span -- never on name-token
        # pattern alone. 5 more candidates from the same review (990005/990022/990032/
        # 990033/990035) did NOT clear the bar and stay unmerged, incl. "Lopez, Jose"
        # whose evidence split ambiguously across two different candidates)
        # - 3 (identity merges of 2026-09-21, data/clean/player_id_tombstones.csv: 73 -> 74, 951 -> 952,
        # 24 -> 35; the retired ids stay resolvable through index/player_redirects.json)
        # - 1 (identity merge of 2026-09-22, batch 2 A03: 180 -> 194, same-DOB reversed-surname pair,
        # docs/specs/cluster_evidence_batch2.md)
        # - 3 (identity merge of 2026-09-22, batch 2 A04: 345, 346, 347 -> 344, three consecutive
        # byte-identical enciclopedia rows of 344's own listing, docs/specs/cluster_evidence_batch2.md)
        assert len(pl) == 3326
        assert all(isinstance(p["id"], int) for p in pl)
        assert pl == sorted(pl, key=lambda p: p["id"])
        assert sum(1 for p in pl if p["id"] > 990000) == 30

    def test_manifest_counts_match(self):
        man = json.loads((b.WEB / "manifest.json").read_text())
        assert man["counts"]["players"] == 3326
        assert man["counts"]["seasons"] == 98
        assert len(man["source_digest"]) == 64      # sha256 hex

    def test_player_redirects_follow_the_tombstones(self):
        tombs = b._read("player_id_tombstones.csv")
        red = json.loads((b.WEB / "index" / "player_redirects.json").read_text())
        assert red["ids"] == {t["retired_id"]: int(t["survivor_id"]) for t in tombs}
        # 2 keys per tombstone (bare + -id), except when the retired id's own name-derived slug is
        # identical to its survivor's current slug (J16 A04): the live route already serves that bare
        # URL, so build_player_redirects() skips it and only the -id form is added (1 key, not 2).
        canon = {r["bsnpr_id"]: r["canonical_name"] for r in b._read("players_canonical.csv")}
        expect_slugs = sum(1 if b._slug(t["retired_name"]) == b._slug(canon[t["survivor_id"]]) else 2
                           for t in tombs)
        assert len(red["slugs"]) == expect_slugs == 11
        man = json.loads((b.WEB / "manifest.json").read_text())
        assert man["counts"]["player_redirects"] == len(tombs) == 7
        for t in tombs:                                    # no file for a retired id, one for its survivor
            assert not (b.WEB / "players" / f"{t['retired_id']}.json").exists()
            assert (b.WEB / "players" / f"{t['survivor_id']}.json").exists()

    def test_the_identity_files_are_digest_inputs(self):
        import re as _re
        src = (b.REPO_ROOT / "src" / "build_web_data.py").read_text()
        assert _re.search(r'"player_id_tombstones.csv", "player_identity_decisions.csv"', src)

    def test_player_detail_file(self):
        p = json.loads((b.WEB / "players" / "37.json").read_text())
        assert p["name"] == "Carmona Sanchez, Alejandro"
        assert len(p["career"]) >= 17                # jug05 (D-047) added pre-2007 seasons
        assert p["career"][0]["franchise_id"]        # team_raw resolved
        assert all(c["games"] is None or isinstance(c["games"], int) for c in p["career"])
        # detail files only for ids in the canonical index
        idx = {x["id"] for x in json.loads((b.WEB / "index" / "players.json").read_text())}
        assert all(int(f.stem) in idx for f in (b.WEB / "players").glob("*.json"))

    def test_player_bio_block(self):
        # jugador05.asp enrich-only (PHASE_3H follow-up): a `bio` block appears
        # on exactly the player_bios.csv rows, and carries jugador05 provenance.
        bio_ids = {r["bsnpr_id"] for r in b._read("player_bios.csv")}
        assert bio_ids
        emitted = {f.stem for f in (b.WEB / "players").glob("*.json")
                   if "bio" in json.loads(f.read_text())}
        assert emitted == bio_ids
        sample = json.loads((b.WEB / "players" / f"{sorted(bio_ids, key=int)[0]}.json").read_text())
        assert sample["bio"]["source"] == "wayback_bsnpr_jugador05"
        assert any(u for u in sample["sources"] if "jugador05" in u)

    def test_season_stats_helper(self):
        # season_detail_spec.md §1 — the join/dedup helper, called directly.
        # Numbers match the spec's own overlap check (run against these same
        # CSVs before the spec was written). 154->153 distinct pids / 250->249
        # pairs (2026-09-14): the 990017/580 merge consolidated two id_map
        # observations ("Corales, E." and "Morales, E.", both real aliases of
        # the same person) that were previously counted as two separate
        # stats-linked players into one.
        stats = b._season_stats()
        pairs = [(pid, season) for pid, seasons in stats.items() for season in seasons]
        assert len(stats) == 153
        assert len(pairs) == 249
        assert {season for _, season in pairs} <= {2001, 2002, 2003, 2004}
        pid, seasons = next(iter(stats.items()))
        fields = next(iter(seasons.values()))["fields"]
        assert set(fields) == {"games", "pts", "minutes", "fg", "tp", "ft",
                                "reb", "ast", "stl", "blk", "tov", "ppg"}
        assert set(fields["fg"]) == {"m", "a", "pct"}

    def test_season_stats_attached_to_career(self):
        # every (bsnpr_id, season) the helper produces lands in that
        # player's built career[] row, games/points/stats intact — whether
        # attached to a pre-existing thin row or synthesized fresh (8 of the
        # 250 pairs had no existing row at that season). player_career_
        # seasons.csv itself sometimes carries >1 row for the same player-
        # season (the same team written two ways across Wayback captures,
        # e.g. "BAYAMON" and "Vaqueros, Bayamon" as separate rows) — a pre-
        # existing source quirk, not something this build introduces or
        # fixes; `stats` attaches to whichever row's team_raw actually
        # matched the crosswalk key, and every pair gets exactly one match
        # (verified: 0 misses across all 250).
        stats = b._season_stats()
        for pid, seasons in stats.items():
            d = json.loads((b.WEB / "players" / f"{pid}.json").read_text())
            for season, s in seasons.items():
                rows = [c for c in d["career"] if c["season"] == season]
                assert rows, f"{pid}/{season} missing from career[]"
                matches = [r for r in rows if "stats" in r]
                assert len(matches) == 1, f"{pid}/{season}: expected exactly 1 stats row, got {len(matches)}"
                row = matches[0]
                assert row["stats"] == s["fields"]
                # the two sources can disagree (e.g. one build hit 411 vs 422
                # points for the same player-season) — row.games/points stay
                # whatever player_career_seasons.csv said (never overwritten);
                # the Tier-2 numbers live inside stats.games/stats.pts instead
                assert row["stats"]["games"] == s["games"]
                assert row["stats"]["pts"] == s["points"]
                assert row["team_raw"]

    def test_season_stats_never_fabricated_on_thin_seasons(self):
        # a season the helper has nothing for never gets a `stats` key —
        # not an empty dict, not zeros (PC2: NULL != 0).
        rich_pairs = {(pid, season) for pid, seasons in b._season_stats().items()
                      for season in seasons}
        checked = 0
        ids = [p["id"] for p in json.loads((b.WEB / "index" / "players.json").read_text())]
        for pid in ids:
            d = json.loads((b.WEB / "players" / f"{pid}.json").read_text())
            for c in d["career"]:
                if (str(pid), c["season"]) not in rich_pairs:
                    assert "stats" not in c
                    checked += 1
        assert checked > 0

    def test_latinbasket_roster_helper(self):
        # backlog item 7, Phase D — 744 confirmed rows, same shape as the
        # (bsnpr_id -> [rows]) season_stats helper above.
        roster = b._latinbasket_roster()
        rows = [row for rows in roster.values() for row in rows]
        assert len(rows) == 744
        assert set(rows[0]) == {"season", "franchise_id", "jersey_number",
                                 "height_cm", "position_raw"}
        clean_rows = b._read("player_roster_latinbasket.csv")
        assert {r["bsnpr_id"] for r in clean_rows} == set(roster)

    def test_latinbasket_roster_attached_or_synthesized_in_career(self):
        # every (bsnpr_id, season, franchise_id) the helper produces lands
        # in that player's built career[] with a real `roster` object —
        # whether attached to a pre-existing row or synthesized fresh.
        roster = b._latinbasket_roster()
        checked = 0
        for pid, rows in roster.items():
            d = json.loads((b.WEB / "players" / f"{pid}.json").read_text())
            for rr in rows:
                matches = [c for c in d["career"]
                           if c["season"] == rr["season"] and c["franchise_id"] == rr["franchise_id"]
                           and "roster" in c]
                assert len(matches) == 1, f"{pid}/{rr['season']}/{rr['franchise_id']}: expected 1 roster row"
                assert matches[0]["roster"] == {
                    "jersey_number": rr["jersey_number"], "height_cm": rr["height_cm"],
                    "position_raw": rr["position_raw"],
                }
                checked += 1
        assert checked == 744

    def test_latinbasket_roster_synthesized_row_has_null_games_points(self):
        # a season with no other source is a real, disclosed "no stats"
        # gap, not a fabricated 0 (PC2) — checked directly against the
        # built JSON, not inferred from the code.
        roster = b._latinbasket_roster()
        career_by_pid = {r["bsnpr_id"]: r["season"] for r in b._read("player_career_seasons.csv")}
        found_synthesized = False
        for pid, rows in roster.items():
            d = json.loads((b.WEB / "players" / f"{pid}.json").read_text())
            for rr in rows:
                row = next(c for c in d["career"]
                           if c["season"] == rr["season"] and c["franchise_id"] == rr["franchise_id"])
                if row["team_raw"] is None:  # synthesized, not an enrichment of an existing row
                    assert row["games"] is None
                    assert row["points"] is None
                    found_synthesized = True
        assert found_synthesized

    def test_season_stats_source_digest_input(self):
        # the new source is registered, so the manifest version actually
        # changes if this CSV changes (source_digest's whole reason to exist)
        import inspect
        assert '"player_season_stats_2001_2004.csv"' in inspect.getsource(b.main)

    def test_assets_empty_by_default(self):
        man = json.loads((b.WEB / "manifest.json").read_text())
        assert isinstance(man["assets"], dict)
        assert all(v.startswith(("img/crest/", "img/player/")) for v in man["assets"].values())

    def test_scan_assets_picks_up_a_file(self, tmp_path, monkeypatch):
        root = tmp_path / "web" / "img"
        (root / "crest").mkdir(parents=True)
        (root / "player").mkdir(parents=True)
        (root / "crest" / "rio.svg").write_bytes(b"<svg/>")
        (root / "crest" / "rio.png").write_bytes(b"x")          # priority: png > svg
        (root / "player" / "georgie-torres.jpg").write_bytes(b"x")
        (root / "crest" / "notes.txt").write_text("ignored")
        monkeypatch.setattr(b, "WEB_IMG", root)
        got = b._scan_assets()
        assert got == {
            "img/crest/rio": "img/crest/rio.png",
            "img/player/georgie-torres": "img/player/georgie-torres.jpg",
        }
        assert list(got) == sorted(got)   # deterministic key order

    def test_site_index_matches_shell(self):
        idx = b.WEB.parent / "index.html"
        if not idx.exists():
            pytest.skip("web/index.html not built (make site)")
        assert idx.read_bytes() == (b.APP / "bsn_archivo.html").read_bytes()
        assert (b.WEB.parent / ".nojekyll").exists()

    def test_mvp_index(self):
        mvp = json.loads((b.WEB / "index" / "mvp.json").read_text())
        yrs = [m["season"] for m in mvp]
        assert yrs == sorted(yrs) and len(set(yrs)) == len(yrs)
        assert min(yrs) == 1958 and max(yrs) >= 2003
        by_yr = {m["season"]: m for m in mvp}
        assert by_yr[1973]["player"] == "Neftali Rivera"        # gap year the app lacks
        assert by_yr[1963]["also"] == "Johny Baez"              # genuine disagreement -> footnote
        assert by_yr[1962]["also"] is None                      # "TEO CRUZ" ~ "Teófilo Cruz", not flagged
        assert by_yr[1959]["franchise_id"] == "capitanes_arecibo"

    def test_titlecase(self):
        assert b._titlecase("BILL McCADNEY") == "Bill McCadney"
        assert b._titlecase("NEFTALI RIVERA") == "Neftali Rivera"
        assert b._titlecase("JAVIER ‘TOÑITO’ COLON") == "Javier «Toñito» Colon"

    def test_player_xwalk(self):
        xw = json.loads((b.WEB / "index" / "player_xwalk.json").read_text())
        assert xw["jose piculin ortiz"] == 1271
        assert "arnaldo toro" not in xw               # rejected -> none
        # "Georgie Torres" -> 788 (D-049, 2026-09-13): the original
        # "auto" match's rejection premise was itself wrong -- id 788's
        # canonical name "Torres Dougherty, George" IS the real Georgie
        # Torres's full name (Dougherty a second Spanish-naming surname,
        # confirmed 6-source: en.wikipedia, fiba.basketball, Wikidata
        # Q3760772, El Nuevo Día, RealGM, basketball-reference). Verdict
        # reversed rejected -> review; see player_crosswalk.csv's row and
        # docs/session.md D-049 for the full evidence trail.
        assert xw["georgie torres"] == 788
        idx = {x["id"] for x in json.loads((b.WEB / "index" / "players.json").read_text())}
        assert all(v in idx for v in xw.values())     # every target is a real id
        assert all(k == b._app_norm(k) for k in xw)   # keys already normalised

    def test_historic_champion_seed(self):
        # PHASE_3I — 1948-71 scoring champions: linked in the id map (title
        # attestation) and their canonical career span seeded from title years.
        idm = b._read("player_id_map.csv")
        hist = [m for m in idm if m["obs_source"] == "historic_scoring_champions.csv"]
        assert len(hist) >= 55                       # ~all 58 rows now mapped
        assert all(m["bsnpr_id"] for m in hist)
        rv = list(csv.DictReader(
            (b.WEB.parents[1] / "data" / "interim" / "player_review_queue.csv").open()))
        assert not [r for r in rv if r["obs_source"] == "historic_scoring_champions.csv"]
        fel = next(r for r in b._read("players_canonical.csv") if r["bsnpr_id"] == "1943")
        assert fel["first_season"] == "1948" and fel["last_season"] == "1955"
        tor = next(r for r in b._read("players_canonical.csv") if r["bsnpr_id"] == "788")
        assert (tor["first_season"], tor["last_season"]) == ("1977", "1987")  # Georgie Torres
        # id 507 "León, Edgar" resolves past the id-507/508 norm_key collision
        # (normalized-alias index picks 507) — its span is seeded, 508 untouched
        leon = next(r for r in b._read("players_canonical.csv") if r["bsnpr_id"] == "507")
        assert (leon["first_season"], leon["last_season"]) == ("1988", "1990")

    def test_q4_truncated_and_bare_surname(self):
        # PHASE_3J (identity_spine_spec Q4) — season-gated fallbacks.
        idm = b._read("player_id_map.csv")
        by = {(m["obs_source"], m["player_raw"], m["season"]): m for m in idm}
        # A — trailing quote-clip stripped, then exact + season
        t = by[("player_season_leaders.csv", "Ayuso, Elias 'Lar", "2012")]
        assert t["bsnpr_id"] == "574" and t["match_method"] == "name+season+trunc"
        # A' — trailing partial given token, prefix + season
        a = by[("player_season_leaders.csv", "Avila, Victor Man", "2008")]
        assert a["bsnpr_id"] == "2446" and a["match_method"] == "name+season+trunc"
        # C — bare surname resolved by club + season
        c = by[("player_season_leaders_2000_2002.csv", "Ayuso", "2000")]
        assert c["bsnpr_id"] == "574" and c["match_method"] == "surname+season+club"
        assert c["club_check"] == "confirms"
        n_q4 = sum(1 for m in idm if m["match_method"] in ("name+season+trunc", "surname+season+club"))
        assert n_q4 >= 70

    def test_season_detail_nulls_not_empties(self):
        s = json.loads((b.WEB / "seasons" / "1953.json").read_text())
        assert s["champion"] is None and s["standings"] is None and s["leaders"] is None
        s09 = json.loads((b.WEB / "seasons" / "2009.json").read_text())
        assert s09["standings"]["rows"][0]["w"] >= s09["standings"]["rows"][-1]["w"]
        assert s09["standings"]["complete"] is False   # 114 archived games < 140

    def test_game_box_and_quarters(self):
        g = json.loads((b.WEB / "games" / "2001" / "BS21001.json").read_text())
        assert g["score"] == {"a": 95, "b": 82}
        assert g["quarters"]["a"] == [24, 24, 28, 16]  # trailing 0-0 trimmed
        assert len(g["box"]) == 21
        assert any(row["bsnpr_id"] is None for row in g["box"])   # PC2
        idx = json.loads((b.WEB / "games" / "2001" / "index.json").read_text())
        assert len(idx) == 158 and idx == sorted(idx, key=lambda x: (x["date"] or "", x["game_id"]))

    def test_starting_five(self):
        # keyed by app_key (matching every other web/data file the app fetches
        # directly by its own F[k] key), not the pipeline's franchise_id.
        are = json.loads((b.WEB / "starting_five" / "are.json").read_text())
        assert "2013" not in are            # 57% resolved — below the 60% floor
        assert "2002" in are and are["2002"]["games"] == 47
        players = are["2002"]["players"]
        assert len(players) == 5
        apodaca = next(p for p in players if p["bsnpr_id"] == 2028)
        assert apodaca["position"] == "Escolta" and apodaca["games"] == 47
        # PC2: an unresolved slot stays null, never a guessed id or position
        gaps = [p for p in players if p["bsnpr_id"] is None]
        assert len(gaps) == 2 and all(p["position"] is None and p["name"] for p in gaps)
        assert are["2002"]["resolved"] == 3   # 3 of the 5 in the *final* list, not the per-slot floor stat

    def test_starting_five_never_includes_a_thin_or_unresolvable_team_season(self):
        for fid_path in (b.WEB / "starting_five").glob("*.json"):
            seasons = json.loads(fid_path.read_text())
            for season, rec in seasons.items():
                assert rec["games"] >= b.STARTING_FIVE_MIN_GAMES
                assert len(rec["players"]) == 5
        # J16b: Cayey resolves to toritos_cayey, so its 2002 team-season (30 games) has a file. The 2013
        # merged team-name gap (Humacao-Carolina) is still excluded at the source (no franchise_id to
        # key a file on): confirm it did not leak in under some other franchise's file.
        cay = json.loads((b.WEB / "starting_five" / "cay.json").read_text())
        assert list(cay) == ["2002"] and cay["2002"]["games"] == 30 and len(cay["2002"]["players"]) == 5
        hum = b.WEB / "starting_five" / "hum.json"
        assert not hum.exists() or "2013" not in json.loads(hum.read_text())

    def test_every_app_team_key_has_a_starting_five_file(self):
        # N1: a team page fetches starting_five/<key>.json for every key, so a missing
        # file is a 404 in the console. All 33 keys get one.
        app_to_fid, _ = b.load_crosswalk()
        files = {p.stem for p in (b.WEB / "starting_five").glob("*.json")}
        assert files == set(app_to_fid) and len(files) == 33

    def test_a_team_with_no_starting_five_data_has_an_empty_file(self):
        empty = {p.stem for p in (b.WEB / "starting_five").glob("*.json")
                 if json.loads(p.read_text()) == {}}
        assert {"ate", "man", "hum", "vil"} <= empty          # the four checked in real browsers
        assert not empty & {"are", "bay", "cac"}               # teams with data are never blanked
        manifest = json.loads((b.WEB / "manifest.json").read_text())
        # the manifest still counts teams that have a starting five, not placeholder files
        assert manifest["counts"]["starting_five_files"] == 33 - len(empty)


class TestPlayerRedirects:
    """build_player_redirects() with synthetic data, isolated from the committed CSVs (J16 A04: a retired id
    whose own name-derived slug equals its survivor's current slug needs no bare-form redirect key)."""

    def _write(self, tmp_path, canon_rows, tomb_rows, monkeypatch):
        monkeypatch.setattr(b, "CLEAN", tmp_path)
        monkeypatch.setattr(b, "WEB", tmp_path / "web")
        (tmp_path / "web" / "index").mkdir(parents=True)
        with (tmp_path / "players_canonical.csv").open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["bsnpr_id", "canonical_name"]); w.writeheader(); w.writerows(canon_rows)
        with (tmp_path / "player_id_tombstones.csv").open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["retired_id", "survivor_id", "decision_id", "retired_name",
                                               "retired_at"])
            w.writeheader(); w.writerows(tomb_rows)

    def test_a_retired_id_sharing_its_survivors_exact_name_skips_only_the_bare_key(self, tmp_path, monkeypatch):
        # 344 survives; 345 had the identical canonical name, so its bare slug == 344's own live slug
        self._write(tmp_path,
                    [{"bsnpr_id": "344", "canonical_name": "Travieso Peña, Carmelo"}],
                    [{"retired_id": "345", "survivor_id": "344", "decision_id": "D-X",
                     "retired_name": "Travieso Peña, Carmelo", "retired_at": "2026-09-22"}],
                    monkeypatch)
        path = b.build_player_redirects()
        red = json.loads(path.read_text())
        assert red["ids"] == {"345": 344}
        assert red["slugs"] == {"travieso-pena-carmelo-345": 344}   # bare "travieso-pena-carmelo" skipped

    def test_a_retired_id_with_a_different_name_gets_both_keys(self, tmp_path, monkeypatch):
        self._write(tmp_path,
                    [{"bsnpr_id": "74", "canonical_name": "Cruz Torres, Alvin"}],
                    [{"retired_id": "73", "survivor_id": "74", "decision_id": "D-X",
                     "retired_name": "Cruz, Alvin", "retired_at": "2026-09-22"}],
                    monkeypatch)
        red = json.loads(b.build_player_redirects().read_text())
        assert red["slugs"] == {"cruz-alvin": 74, "cruz-alvin-73": 74}

    def test_a_key_colliding_with_an_unrelated_live_player_still_errors(self, tmp_path, monkeypatch):
        # 74 is the survivor; 999 is a real, unrelated live player who happens to hold the retired
        # id's bare slug -- this must still be caught, not silently skipped
        self._write(tmp_path,
                    [{"bsnpr_id": "74", "canonical_name": "Cruz Torres, Alvin"},
                     {"bsnpr_id": "999", "canonical_name": "Cruz, Alvin"}],
                    [{"retired_id": "73", "survivor_id": "74", "decision_id": "D-X",
                     "retired_name": "Cruz, Alvin", "retired_at": "2026-09-22"}],
                    monkeypatch)
        with pytest.raises(SystemExit, match="cruz-alvin.*retired id 73.*also a live player's slug"):
            b.build_player_redirects()


class TestDisputedSeasonsExcludedFromIndex:
    """build_players_index() with synthetic data (J16 A05): a season flagged in disputed_career_rows.csv
    doesn't count toward first_season/last_season/n_seasons/career_seasons -- but only for a player who has
    at least one flagged row. Everyone else keeps players_canonical.csv's own values, untouched."""

    CANON_FIELDS = ["bsnpr_id", "canonical_name", "normalized_name", "birth_year", "nationality", "position",
                    "first_season", "last_season", "n_seasons", "has_profile"]

    def _write(self, tmp_path, canon_rows, disputed_rows, monkeypatch):
        monkeypatch.setattr(b, "CLEAN", tmp_path)
        monkeypatch.setattr(b, "INTERIM", tmp_path / "interim")
        monkeypatch.setattr(b, "WEB", tmp_path / "web")
        (tmp_path / "web" / "index").mkdir(parents=True)
        (tmp_path / "interim").mkdir()
        with (tmp_path / "players_canonical.csv").open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=self.CANON_FIELDS); w.writeheader(); w.writerows(canon_rows)
        with (tmp_path / "interim" / "disputed_career_rows.csv").open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["bsnpr_id", "season"]); w.writeheader(); w.writerows(disputed_rows)

    def _row(self, pid, name, birth_year, first, last, n, nationality="Puerto Rico", position="Delantero"):
        return {"bsnpr_id": pid, "canonical_name": name, "normalized_name": name.lower(), "birth_year": birth_year,
                "nationality": nationality, "position": position, "first_season": first, "last_season": last,
                "n_seasons": n, "has_profile": "yes"}

    def test_a_player_with_every_row_disputed_gets_no_span_and_zero_counts(self, tmp_path, monkeypatch):
        # mirrors the real id 721: 5 rows, 1965-1969, all flagged
        career = {"1": [{"season": s} for s in (1965, 1966, 1967, 1968, 1969)]}
        self._write(tmp_path, [self._row("1", "Test, Uno", 1980, "1965", "1969", "5")],
                    [{"bsnpr_id": "1", "season": s} for s in (1965, 1966, 1967, 1968, 1969)], monkeypatch)
        p = json.loads(b.build_players_index(career).read_text())[0]
        assert (p["first_season"], p["last_season"], p["n_seasons"], p["career_seasons"]) == (None, None, 0, 0)
        assert p["birth_year"] == 1980 and p["position"] == "Delantero"   # untouched fields stay as-is

    def test_a_player_with_flagged_and_unflagged_rows_keeps_only_the_unflagged_in_the_span(self, tmp_path, monkeypatch):
        career = {"2": [{"season": 2000}, {"season": 2001}, {"season": 2002}]}
        self._write(tmp_path, [self._row("2", "Test, Dos", 1980, "2000", "2002", "3")],
                    [{"bsnpr_id": "2", "season": 2000}, {"bsnpr_id": "2", "season": 2001}], monkeypatch)
        p = json.loads(b.build_players_index(career).read_text())[0]
        assert (p["first_season"], p["last_season"], p["n_seasons"], p["career_seasons"]) == (2002, 2002, 1, 1)

    def test_an_unflagged_player_is_completely_unchanged(self, tmp_path, monkeypatch):
        career = {"3": [{"season": 1990}, {"season": 1991}, {"season": 1992}]}
        self._write(tmp_path, [self._row("3", "Test, Tres", 1970, "1990", "1992", "3")], [], monkeypatch)
        p = json.loads(b.build_players_index(career).read_text())[0]
        assert (p["first_season"], p["last_season"], p["n_seasons"], p["career_seasons"]) == (1990, 1992, 3, 3)

    def test_a_players_canonical_field_that_disagrees_with_the_row_count_is_still_used_when_unflagged(self, tmp_path, monkeypatch):
        # the free-typed n_seasons field can mismatch the real row count (build_players_index's own comment,
        # confirmed on 251 real players) -- an UNFLAGGED player must still get the CSV's own value, not a
        # recount, so this fix never narrows a span it wasn't asked to touch
        career = {"4": [{"season": 1990}]}
        self._write(tmp_path, [self._row("4", "Test, Cuatro", 1970, "1988", "1990", "5")], [], monkeypatch)
        p = json.loads(b.build_players_index(career).read_text())[0]
        assert (p["first_season"], p["last_season"], p["n_seasons"]) == (1988, 1990, 5)   # CSV values, not recomputed
        assert p["career_seasons"] == 1                                                   # this one IS the row count, always

    def test_disputed_seasons_helper_groups_by_id(self, tmp_path, monkeypatch):
        # like every other DQ_INTERIM_LOGS file, disputed_career_rows.csv is always committed and expected
        # to exist -- _read_interim has no "absent -> []" fallback, by the same convention as the rest.
        monkeypatch.setattr(b, "INTERIM", tmp_path)
        with (tmp_path / "disputed_career_rows.csv").open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["bsnpr_id", "season"])
            w.writeheader(); w.writerows([{"bsnpr_id": "1", "season": "1965"}, {"bsnpr_id": "1", "season": "1966"}])
        assert b._disputed_seasons() == {"1": {1965, 1966}}


class TestHelpers:
    def test_norm(self):
        assert b._norm("SAN GERMAN") == b._norm("San Germán") == "san german"
        assert b._norm("  Río  Piedras ") == "rio piedras"

    def test_team_resolver(self):
        r = b._team_resolver()
        assert r("SANTURCE") == r("Santurce") == "cangrejeros_santurce"
        assert r("Nowhere") is None

    def test_team_resolver_manati_is_era_aware(self):
        # Atenienses de Manati (2015-16) and Osos de Manati (2023+) share a city.
        r = b._team_resolver()
        assert r("MANATI", 2015) == r("Manatí", "2016") == "atenienses_manati"
        assert r("MANATI", 2023) == r("Manati", 2024) == r("MANATI", "2030") == "osos_manati"

    def test_team_resolver_unchanged_when_no_override_matches(self):
        r = b._team_resolver()
        # season omitted, non-year, or outside every override: the era-blind map answers
        assert r("MANATI") == r("MANATI", None) == r("MANATI", "unknown") == "osos_manati"
        # 2014 and 2017 are UNVERIFIED (audit F5), so deliberately not overridden.
        assert r("MANATI", 2014) == r("MANATI", 2017) == "osos_manati"
        for row in b._read("city_franchise_map.csv"):
            assert r(row["normalized_city"]) == row["franchise_id"]
            if row["normalized_city"] != "MANATI":
                assert r(row["normalized_city"], 2016) == row["franchise_id"]

    def test_source_digest_is_stable(self):
        d1 = b._source_digest(["franchises.csv", "franchise_curated.json"])
        d2 = b._source_digest(["franchise_curated.json", "franchises.csv"])
        assert d1 == d2 and len(d1) == 64


class TestManatiCareerRows:
    """Audit F1/F2: a wrong Manatí franchise_id also broke the latinbasket
    roster join (keyed on season + franchise_id), leaving one player-season as
    two career rows. Calls the pure career builder, not the built files."""

    MANATI = {"osos_manati", "atenienses_manati"}

    def test_no_player_season_carries_both_manati_franchises(self):
        both = []
        for pid, rows in b.build_career_rows_by_pid().items():
            seen: dict[int, set[str]] = {}
            for r in rows:
                if r["franchise_id"] in self.MANATI:
                    seen.setdefault(r["season"], set()).add(r["franchise_id"])
            both += [(pid, s) for s, fids in seen.items() if len(fids) > 1]
        assert both == []

    def test_2015_2016_career_rows_are_atenienses(self):
        rows = [(pid, r) for pid, rs in b.build_career_rows_by_pid().items() for r in rs
                if r["season"] in (2015, 2016) and r["franchise_id"] in self.MANATI]
        assert rows and all(r["franchise_id"] == "atenienses_manati" for _, r in rows)

    def test_former_duplicates_are_one_populated_row(self):
        career = b.build_career_rows_by_pid()
        for pid, season in [("1094", 2015), ("13011", 2015), ("1995", 2015),
                            ("1739", 2016), ("1995", 2016), ("772", 2016)]:
            rows = [r for r in career[pid]
                    if r["season"] == season and r["franchise_id"] == "atenienses_manati"]
            assert len(rows) == 1, (pid, season)
            assert rows[0]["games"] is not None and rows[0]["points"] is not None, (pid, season)
            assert "roster" in rows[0], (pid, season)


class TestStatsAttach:
    """A Tier-2 stats record is one team's stat line, so it belongs on that team's career row,
    not on whichever row sorts first. Calls the pure builders, not the built files."""

    @staticmethod
    def _row(team, season=2003):
        r = b._team_resolver()
        return {"season": season, "team_raw": team, "franchise_id": r(team.split(",")[-1], season),
                "games": 1, "points": 1}

    def _pick(self, teams, record_team, season=2003):
        rows = [self._row(t, season) for t in teams]
        return b._row_for_stats(rows, record_team, b._team_resolver(), season)["team_raw"]

    def test_a_trade_year_goes_on_the_recorded_team_not_the_first_row(self):
        assert self._pick(["BAYAMON", "MOROVIS"], "Titanes de Morovis") == "MOROVIS"
        assert self._pick(["Maratonistas, Coamo", "Vaqueros, Bayamon"], "Vaqueros de Bayamon") == "Vaqueros, Bayamon"

    def test_the_first_row_still_wins_when_it_is_the_recorded_team(self):
        assert self._pick(["BAYAMON", "MOROVIS"], "Vaqueros de Bayamon") == "BAYAMON"

    def test_one_season_written_two_ways_resolves_to_the_first_spelling(self):
        assert self._pick(["BAYAMON", "COAMO", "Vaqueros, Bayamon"], "Vaqueros de Bayamon") == "BAYAMON"

    def test_a_franchise_the_city_map_lacks_matches_on_the_city(self):
        assert self._pick(["Piratas, Quebradillas", "Toritos, Cayey"], "Toritos de Cayey", 2002) == "Toritos, Cayey"
        assert self._pick(["CAYEY", "Piratas, Quebradillas"], "Toritos de Cayey", 2002) == "CAYEY"

    def test_falls_back_to_the_first_row_with_no_match_or_no_team(self):
        assert self._pick(["BAYAMON", "MOROVIS"], "Cangrejeros de Santurce") == "BAYAMON"
        assert self._pick(["BAYAMON", "MOROVIS"], "") == "BAYAMON"
        assert self._pick(["BAYAMON", "MOROVIS"], None) == "BAYAMON"

    def test_a_single_team_season_is_unchanged(self):
        assert self._pick(["Vaqueros, Bayamon"], "Vaqueros de Bayamon") == "Vaqueros, Bayamon"

    def test_every_stats_record_sits_on_a_row_for_its_own_team_when_one_exists(self):
        career, stats = b.build_career_rows_by_pid(), b._season_stats()
        wrong, checked = [], 0
        for pid, seasons in stats.items():
            for season, rec in seasons.items():
                city = b._norm(b._DE_SPLIT.split(rec["team_raw"], maxsplit=1)[-1])
                rows = [r for r in career[pid] if r["season"] == season and r["team_raw"]]
                carriers = [r for r in rows if "stats" in r]
                if not rows or not any(b._norm(r["team_raw"].split(",")[-1]) == city for r in rows):
                    continue                                   # no row for that team: nothing to match
                checked += 1
                if len(carriers) != 1 or b._norm(carriers[0]["team_raw"].split(",")[-1]) != city:
                    wrong.append((pid, season))
        assert checked > 200 and wrong == []

    @pytest.mark.parametrize("pid, season, city", [
        ("143", 2003, "morovis"), ("1562", 2003, "morovis"), ("217", 2003, "morovis"),
        ("193", 2001, "bayamon"), ("808", 2002, "cayey")])
    def test_the_five_seasons_that_started_this(self, pid, season, city):
        rows = [r for r in b.build_career_rows_by_pid()[pid] if r["season"] == season]
        carriers = [r for r in rows if "stats" in r]
        assert len(rows) > 1 and len(carriers) == 1
        assert b._norm(carriers[0]["team_raw"].split(",")[-1]) == city
