"""PHASE_72A -- web-layer data fixes (docs/audits/phase72_audit.md, owner decisions D1, D5, D6, D7).

Static checks read the shipped files; the browser checks use tests/harness/phase72a_probe.mjs, which loads
web/ in Chromium and reads the site's own globals (needs node + playwright-core, PLAYWRIGHT_CORE=<dir> or
any */node_modules/playwright-core under /private/tmp; those tests skip with a stated reason otherwise).
"""
import glob
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TABS = (ROOT / "web/js/tabs.js").read_text(encoding="utf-8")
INIT = (ROOT / "web/js/init.js").read_text(encoding="utf-8")
GAMES = (ROOT / "web/js/games.js").read_text(encoding="utf-8")
PLAYER = (ROOT / "web/js/player.js").read_text(encoding="utf-8")
DATA = (ROOT / "web/js/data.js").read_text(encoding="utf-8")
INDEX = (ROOT / "web/index.html").read_text(encoding="utf-8")
FOOTNOTE = "El porcentaje indica cuántos de cuatro datos (campeón, subcampeón, campeón de anotación y MVP) tiene el archivo por cada temporada de la década."
ALL_UI = TABS + INIT + GAMES + PLAYER + DATA + INDEX


@pytest.fixture(scope="module")
def probe():
    node = shutil.which("node")
    env = os.environ.get("PLAYWRIGHT_CORE")
    hits = sorted(glob.glob("/private/tmp/**/node_modules/playwright-core/index.js", recursive=True))
    core = env if env and (Path(env) / "index.js").exists() else (str(Path(hits[0]).parent) if hits else None)
    if not node or not core:
        pytest.skip("needs node and playwright-core (set PLAYWRIGHT_CORE=<dir>)")
    res = subprocess.run([node, str(ROOT / "tests/harness/phase72a_probe.mjs")],
                         env={**os.environ, "PLAYWRIGHT_CORE": core}, capture_output=True, text=True, timeout=180)
    assert res.returncode == 0, res.stderr[-2000:]
    out = json.loads(res.stdout)
    assert out["pageErrors"] == [], out["pageErrors"]
    return out


class TestD1Rebounds:
    def test_rodriguez_career_rebounds_is_not_a_record_in_source_or_overlay(self):
        assert '["Rebounds, career"' not in TABS
        assert "['Rebotes de carrera'" not in INDEX

    def test_other_rodriguez_records_are_untouched(self):
        assert "['Rebotes en una temporada','380','Rubén Rodríguez'" in INDEX
        assert "['Puntos en una temporada','810','Rubén Rodríguez'" in INDEX

    def test_butler_flag_is_wired_to_the_rebounds_table_only(self):
        assert "SIN CONFIRMAR" in TABS
        assert "LEAD_CAT==='rebounds'&&v==='Mario Butler'" in TABS

    def test_butler_rebound_claims_carry_sin_confirmar(self):
        assert "con 8,236 (sin confirmar)" in TABS
        assert "máximo reboteador histórico (sin confirmar)" in INDEX
        assert "'Máximo reboteador histórico (sin confirmar)'" in INDEX

    def test_leaders_data_row_is_not_edited(self):
        assert '[1,"Mario Butler","C","1980–2008",8236,779,10.6]' in TABS
        assert '[2,"Rubén Rodríguez","F/C","1969–1991",6178,631,9.8]' in TABS

    def test_browser_flag_shows_for_butler_rebounds_only(self, probe):
        assert "SIN CONFIRMAR" in probe["leadersRebounds"]
        assert probe["leadersRebounds"].count("SIN CONFIRMAR") == 1
        assert "SIN CONFIRMAR" not in probe["leadersPoints"]
        assert "Rebotes de carrera" not in probe["records"]
        assert len(probe["records"]) == 10


class TestD5Overlay:
    def _keys(self, name):
        i = INDEX.index(f"const {name}={{")
        j = INDEX.index("\n  };", i)
        return re.findall(r"^\s*'([^']+)':", INDEX[i:j], re.M)

    def _data_names(self, pattern):
        return re.findall(pattern, DATA)

    def test_bio_es_keys_all_match_a_pool_name_in_data_js(self):
        pool = set(re.findall(r'\{n:"([^"]+)"', DATA[DATA.index("const POOL=["):DATA.index("const VENUES")]))
        missing = [k for k in self._keys("BIO_ES") if k not in pool]
        assert missing == []

    def test_every_data_js_bio_has_an_overlay_key(self):
        seg = DATA[DATA.index("const POOL=["):DATA.index("const VENUES")]
        with_bio = set(re.findall(r'n:"([^"]+)"[^{}]*?,b:"', seg, re.S))
        assert with_bio - set(self._keys("BIO_ES")) == set()

    def test_hof_and_nba_overlays_cover_exactly_the_source_names(self):
        hof_src = set(re.findall(r'^ \{n:"([^"]+)"', DATA[DATA.index("const HOF=["):DATA.index("const RETIRED")], re.M))
        hof_es = set(re.findall(r"^\s*'([^']+)':\{", INDEX[INDEX.index("const HOF_ES={"):INDEX.index("setBy(HOF,'n',HOF_ES)")], re.M))
        assert hof_src == hof_es
        nba_src = set(re.findall(r'^\s*\["([^"]+)","', TABS[TABS.index("const NBA_PLAYERS=["):TABS.index("];", TABS.index("const NBA_PLAYERS=["))], re.M))
        nba_es = set(re.findall(r"^\s*\['([^']+)',", INDEX[INDEX.index("const NBA_ES=["):INDEX.index("NBA_PLAYERS.splice")], re.M))
        nba_es |= set(re.findall(r"\['([^']+)','[^']+'\]", INDEX[INDEX.index("const NBA_ES=["):INDEX.index("NBA_PLAYERS.splice")]))
        assert nba_src == nba_es

    def test_browser_no_english_reaches_the_runtime_tables(self, probe):
        assert probe["englishBios"] == []
        assert probe["englishRoles"] == []
        assert probe["englishNba"] == []

    def test_browser_piculin_bio_is_spanish(self, probe):
        assert probe["piculin"] == "«Piculín». Llegó a la NBA y volvió a casa a terminar."


class TestD7Labels:
    def test_no_variant_of_the_two_awards_remains_in_shipped_ui_text(self):
        # the English literals in RECENT (dead data, not rendered) and the masked English bio are out of scope
        ui = TABS + INIT + GAMES + PLAYER + INDEX
        for bad in ("Defensa del Año", "Defensor del año", "Jugador Defensivo del Año", "Sexto hombre del año", "Sexto hombre"):
            assert bad not in ui, bad

    def test_forms_in_use(self):
        assert "defensive_player:'Defensor del Año'" in TABS
        assert "'Fue Sexto Hombre en 2026.'" in INDEX
        assert "'Fue Defensor del Año en 2026.'" in INDEX

    def test_browser_award_labels(self, probe):
        assert probe["seasonAw"]["defensive_player"] == "Defensor del Año"
        assert set(probe["sa"]) >= {"Defensor del Año", "Sexto Hombre"}


class TestD6Coverage:
    def test_no_typed_percentages_remain(self):
        for src in (TABS, INIT):
            assert not re.search(r"\['\d{4}s',\d+,'", src)
        assert "estimación editorial" not in ALL_UI
        assert FOOTNOTE in TABS

    def test_browser_coverage_is_derived_from_the_data(self, probe):
        cov = probe["coverage"]
        assert [c[0] for c in cov] == [f"{d}s" for d in range(1930, 2030, 10)][: len(cov)]
        assert len(cov) == 10
        assert all(0 <= c[1] <= 100 for c in cov)
        for label, pct, text in cov:
            nums = [tuple(map(int, m)) for m in re.findall(r"(\d+)/(\d+)", text)]
            assert len(nums) == 4 and len({n for _, n in nums}) == 1
            total = nums[0][1]
            assert pct == round(100 * sum(h for h, _ in nums) / (4 * total))
        first = cov[0][2]
        assert first.startswith("Campeón 10/10 · Subcampeón ")          # 1930s: champions on file for all ten seasons
        assert "Anotación 0/10" in first and "MVP 0/10" in first      # and nothing else
        assert "/7" in cov[-1][2]                                      # the 2020s decade has 7 seasons on file
        assert "estimación" not in probe["coverageHtml"]
        assert FOOTNOTE in probe["coverageHtml"]


class TestDerivedNumbers:
    def test_literals_are_gone(self):
        assert "98.ª" not in TABS
        assert "let FIN_YEAR=2026" not in TABS
        assert "(2024, 2025, 2026)" not in TABS
        assert "3.303" not in PLAYER.split("Todo el archivo")[1][:900]
        assert "const LAST=2026" not in INDEX and "y<=2026" not in INDEX

    def test_browser_values(self, probe):
        assert probe["last"] == 2026
        assert probe["years"] == [1930, 2026, 97]
        assert probe["finYear"] == 2026
        assert probe["finLabel"] == "Finales juego a juego (2024, 2025, 2026)"

    def test_titles_sentence_reads_the_franchise(self):
        assert "F.sge.won.length" in TABS
