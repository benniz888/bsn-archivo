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
        assert len(app_to_fid) == 32
        assert app_to_fid["bay"] == "vaqueros_bayamon"
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
        assert len(fr) == 32
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

    def test_source_digest_is_stable(self):
        d1 = b._source_digest(["franchises.csv", "franchise_curated.json"])
        d2 = b._source_digest(["franchise_curated.json", "franchises.csv"])
        assert d1 == d2 and len(d1) == 64
