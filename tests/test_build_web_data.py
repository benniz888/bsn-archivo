"""PHASE_5 / 5B — unit coverage for the web/data build helpers.
The end-to-end build is exercised by `make build-web-data` + `verify_web_data`
in `make verify`; these pin the value coercion, the crosswalk assert, and the
deterministic JSON writer.
"""

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

    def test_players_index(self):
        pl = json.loads((b.WEB / "index" / "players.json").read_text())
        assert len(pl) == 3303
        assert all(isinstance(p["id"], int) for p in pl)
        assert pl == sorted(pl, key=lambda p: p["id"])

    def test_manifest_counts_match(self):
        man = json.loads((b.WEB / "manifest.json").read_text())
        assert man["counts"]["players"] == 3303
        assert man["counts"]["seasons"] == 98
        assert len(man["source_digest"]) == 64      # sha256 hex

    def test_player_detail_file(self):
        p = json.loads((b.WEB / "players" / "37.json").read_text())
        assert p["name"] == "Carmona Sanchez, Alejandro"
        assert len(p["career"]) == 17
        assert p["career"][0]["franchise_id"]        # team_raw resolved
        assert all(c["games"] is None or isinstance(c["games"], int) for c in p["career"])
        # detail files only for ids in the canonical index
        idx = {x["id"] for x in json.loads((b.WEB / "index" / "players.json").read_text())}
        assert all(int(f.stem) in idx for f in (b.WEB / "players").glob("*.json"))

    def test_player_xwalk(self):
        xw = json.loads((b.WEB / "index" / "player_xwalk.json").read_text())
        assert xw["georgie torres"] == 788           # owner spot-check
        assert xw["jose piculin ortiz"] == 1271
        assert "arnaldo toro" not in xw               # rejected -> none
        idx = {x["id"] for x in json.loads((b.WEB / "index" / "players.json").read_text())}
        assert all(v in idx for v in xw.values())     # every target is a real id
        assert all(k == b._app_norm(k) for k in xw)   # keys already normalised

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
