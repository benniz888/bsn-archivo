"""PHASE_66 -- Equipos: per-club accents, jersey SVG, claim rewordings, no new top-level names.
Static checks only (no browser); the live behavior is verified in Chromium and WebKit separately."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
TABS = (ROOT / "web/js/tabs.js").read_text(encoding="utf-8")
DATA = (ROOT / "web/js/data.js").read_text(encoding="utf-8")
CSS = (ROOT / "web/css/main.css").read_text(encoding="utf-8")


def _lum(rgb):
    f = lambda v: (v / 255 / 12.92) if v / 255 <= 0.03928 else ((v / 255 + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(rgb[0]) + 0.7152 * f(rgb[1]) + 0.0722 * f(rgb[2])


def _cr(a, b):
    x, y = _lum(a), _lum(b)
    return (max(x, y) + 0.05) / (min(x, y) + 0.05)


def _safe(rgb, bg, minimum, to):
    c, t = rgb, 0.0
    while _cr(c, bg) < minimum and t < 1:
        t += 0.05
        c = [round(v + (to[i] - v) * t) for i, v in enumerate(rgb)]
    return c


def _clubs():
    return re.findall(r'\n\s+(\w+):\{name:"[^"]+".*?c1:"(#[0-9A-Fa-f]{6})"', DATA)


class TestAccentGuard:
    def test_card_and_ink_constants_match_main_css(self):
        # accent() hardcodes the two card backgrounds and the light ink; they must be the tokens.
        assert "--card:#0C1428" in CSS and "--card:#FFFFFF" in CSS and "--ink:#0B1730" in CSS
        assert "const D=[12,20,40], L=[255,255,255], INK_D=[255,255,255], INK_L=[11,23,48];" in TABS

    def test_every_club_clears_text_and_graphic_ratios_in_both_themes(self):
        clubs = _clubs()
        assert len(clubs) == 33
        for k, hexv in clubs:
            rgb = [int(hexv[i:i + 2], 16) for i in (1, 3, 5)]
            for bg, ink in (([12, 20, 40], [255, 255, 255]), ([255, 255, 255], [11, 23, 48])):
                assert _cr(_safe(rgb, bg, 4.5, ink), bg) >= 4.5, k
                assert _cr(_safe(rgb, bg, 3, ink), bg) >= 3, k


class TestJerseySvg:
    def _block(self):
        a = TABS.index("buildRetiredNums.block=")
        return TABS[a:TABS.index("/* ====", a)]

    def test_generic_drawing_only(self):
        b = self._block()
        assert "<image" not in b and "href" not in b and "<img" not in b
        assert b.count("<text") == 1  # the number only
        assert 'role="img" aria-label="Camiseta con el número ${esc(n)}"' in b  # accessible name per jersey
        assert "Colores aproximados" in b

    def test_number_only_tags_and_label(self):
        b = self._block()
        assert "Números retirados, según el archivo:" in b
        assert "eq-jtag" not in b  # the number is on the jersey; no duplicate caption

    def test_retired_data_untouched(self):
        assert '["Vaqueros de Bayamón",8,"4 · 5 · 9 · 15 · 16 · 17 · 17 · 54"]' in DATA
        assert '["Mets de Guaynabo",3,"5 · 9 · 15"]' in DATA
        assert "Santurce" not in DATA[DATA.index("const RETIRED=["):DATA.index("const REF_RULES")]


class TestApprovedRewordings:
    def test_colors_tag(self):
        assert "Colores verificados" not in TABS
        assert "Colores de Wikipedia" in TABS

    def test_man_lore(self):
        assert "El único club activo sin título — el más joven de la liga.'" in TABS
        assert "fanaticada" not in TABS[TABS.index("const TEAM_LORE"):TABS.index("const TOWN_LORE")].split("man:")[1].split("gua:")[0]

    def test_san_town_lore(self):
        assert "negros libres" not in TABS
        assert "es un barrio de San Juan. Se llamó Cangrejos" in TABS

    def test_no_vague_press_attribution_in_equipos_code(self):
        a = TABS.index("function showTeam(")
        assert "según la prensa" not in TABS[a:a + 20000].lower()


class TestSignatureStatIsComputed:
    def test_built_from_f_and_champof_not_typed(self):
        a = TABS.index("PHASE_66 (owner-approved): per-club page.")
        src = TABS[a:TABS.index("host.innerHTML=`", a)]
        assert "const wonY=f.won.slice()" in src and "YEARS.filter(y=>!(y in champOf))" in src
        assert not re.search(r"\b19[3-9]\d–19[3-9]\d\b", src)  # no hand-typed year spans


class TestNoNewTopLevelNames:
    def test_tabs_js_adds_no_top_level_declarations(self):
        base = json.loads((ROOT / "tests/harness/inventory_main_HEAD.json").read_text(encoding="utf-8"))
        old = {d["name"] for d in base["declarations"] if d["file"] == "web/js/tabs.js"}
        now = set()
        for line in TABS.splitlines():
            m = re.match(r"^(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(", line) or re.match(
                r"^(?:const|let|var)\s+([A-Za-z_$][\w$]*)", line)
            if m:
                now.add(m.group(1))
        assert now - old == set()


class TestStartingFiveCourt:
    def _src(self):
        a = TABS.index("function sfFit(")
        return TABS[a:TABS.index("async function loadStartingFive")]

    def test_names_wrap_in_given_name_first_order_without_ellipsis(self):
        src = self._src()
        assert "…" not in src and "truncated" not in src
        assert "p.name.slice(ci+1).trim()+' '+p.name.slice(0,ci).trim()" in src
        assert "sin confirmar" in src and "toUpperCase()" in src

    def test_line_art_court_has_no_fill_and_no_green(self):
        css = CSS[CSS.index(".sf-court{"):CSS.index(".sf-seg button:focus-visible")]
        assert "var(--court)" not in css and "gradient" not in css
        assert re.search(r"\.sf-court svg\{[^}]*background:var\(--card\)", css)
        assert ".sf-ring.dash" in css and "stroke-dasharray" in css

    def test_position_number_rings_and_year_tabs(self):
        src = self._src()
        assert "Armador:1,Escolta:2,Alero:3,Delantero:4,Centro:5" in src
        assert 'class="sf-seg" role="group" aria-label="Temporada"' in src
        assert "aria-pressed=" in src and "aria-selected" not in src
        assert "min-height:44px" in CSS[CSS.index(".sf-seg button{"):CSS.index(".sf-seg button:first-child")]

    def test_no_plates_lines_are_continuous_and_text_has_a_halo(self):
        src = self._src()
        assert "sf-plate" not in src and "sf-plate" not in CSS
        css = CSS[CSS.index(".sf-court{"):CSS.index(".sf-seg button:focus-visible")]
        assert "paint-order:stroke" in css and "stroke:var(--card)" in css
        assert re.search(r"\.sf-ln\{[^}]*stroke-opacity:\.\d+", css)
        for shape in ('M10 10H350V352H10Z', 'M150 10V120H210V10', 'cx="180" cy="120" r="28"',
                      'M30 10V80A150 150 0 0 0 330 80V10'):
            assert shape in src  # outer line, key, center circle and the whole three-point arc

    def test_text_stays_inside_the_court_with_room_below_the_lowest_label(self):
        src = self._src()
        zones = json.loads(re.search(r"const SF_ZONE=(\{.*?\});", TABS).group(1).replace("Armador", '"Armador"')
                           .replace("Escolta", '"Escolta"').replace("Alero", '"Alero"')
                           .replace("Delantero", '"Delantero"').replace("Centro", '"Centro"'))
        for name, (cx, cy) in zones.items():
            half = 15 * 7.4 / 2  # the widest line sfFit allows, generously
            assert cx - half >= 10 + 6 and cx + half <= 350 - 6, name
        cy, lines = zones["Armador"][1], 2
        y_ppg = cy + 32 + 13 * (lines - 1) + 14 + 12
        assert y_ppg + 8 <= 352 - 6 and 'viewBox="0 0 360 362"' in src

    def test_text_colors_clear_4_5_on_the_halo_color_in_both_themes(self):
        def tok(block, name):
            return re.search(name + r":(#[0-9A-Fa-f]{6})", block).group(1)
        dark = CSS[:CSS.index('[data-theme="light"]{')]
        light = CSS[CSS.index('[data-theme="light"]{'):]
        for blk in (dark, light):
            card = tok(blk, "--card")
            for t in ("--ink", "--ink-2", "--ink-3", "--bad-ink"):
                rgb = lambda h: [int(h[i:i + 2], 16) for i in (1, 3, 5)]
                assert _cr(rgb(tok(blk, t)), rgb(card)) >= 4.5, (t, card)

    def test_hidden_list_gives_the_court_a_text_equivalent(self):
        src = self._src()
        assert '<ul class="sr">' in src and "puntos por juego" in src and 'role="img"' in src


class TestHeroHasNoDecorativeOverlap:
    """Geometry probe (Chromium and WebKit, 390 and 1000px, dark and light) on Santurce, Bayamon and a
    defunct club: no decorative element in the club hero may intersect text. Skips when node or
    playwright-core is missing (same convention as test_player_ring_overlap.py)."""

    def test_probe(self):
        import os, shutil, subprocess, glob
        import pytest
        node = shutil.which("node")
        hits = sorted(glob.glob("/private/tmp/**/node_modules/playwright-core/index.js", recursive=True))
        core = os.environ.get("PLAYWRIGHT_CORE") or (str(Path(hits[0]).parent) if hits else None)
        if not node or not core:
            pytest.skip("needs node and playwright-core (set PLAYWRIGHT_CORE=<dir>)")
        res = subprocess.run([node, str(ROOT / "tests/harness/eq_hero_probe.mjs")],
                             env={**os.environ, "PLAYWRIGHT_CORE": core}, capture_output=True, text=True, timeout=600)
        assert res.returncode == 0, res.stderr[-2000:]
        out = json.loads(res.stdout)
        assert out["errors"] == [], out["errors"][:5]
        assert len(out["results"]) == 3 * 8  # 3 clubs x 2 engines x 2 widths x 2 themes
        bad = [r for r in out["results"] if r["overlaps"]]
        assert bad == [], bad[:3]
