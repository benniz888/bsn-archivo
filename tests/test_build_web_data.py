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
        assert len(pl) == 3343                       # 3303 league ids + 40 jug05-minted (D-047)
        assert all(isinstance(p["id"], int) for p in pl)
        assert pl == sorted(pl, key=lambda p: p["id"])
        assert sum(1 for p in pl if p["id"] > 990000) == 40

    def test_manifest_counts_match(self):
        man = json.loads((b.WEB / "manifest.json").read_text())
        assert man["counts"]["players"] == 3343
        assert man["counts"]["seasons"] == 98
        assert len(man["source_digest"]) == 64      # sha256 hex

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
        # CSVs before the spec was written).
        stats = b._season_stats()
        pairs = [(pid, season) for pid, seasons in stats.items() for season in seasons]
        assert len(stats) == 154
        assert len(pairs) == 250
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
        assert xw["georgie torres"] == 788           # owner spot-check
        assert xw["jose piculin ortiz"] == 1271
        assert "arnaldo toro" not in xw               # rejected -> none
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


class TestHelpers:
    def test_norm(self):
        assert b._norm("SAN GERMAN") == b._norm("San Germán") == "san german"
        assert b._norm("  Río  Piedras ") == "rio piedras"

    def test_team_resolver(self):
        r = b._team_resolver()
        assert r("SANTURCE") == r("Santurce") == "cangrejeros_santurce"
        assert r("Nowhere") is None

    def test_source_digest_is_stable(self):
        d1 = b._source_digest(["franchises.csv", "franchise_curated.json"])
        d2 = b._source_digest(["franchise_curated.json", "franchises.csv"])
        assert d1 == d2 and len(d1) == 64
