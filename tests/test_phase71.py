"""PHASE_71 -- social preview, per-route titles, contrast, ARIA, label-in-name, crawl files, service worker.

Static checks read web/ directly; the browser checks run tests/harness/phase71_probe.mjs (Chromium AND WebKit,
390 and 1000px) and skip with a stated reason when node or playwright-core is missing (same convention as
test_player_ring_overlap.py)."""
import glob
import json
import os
import re
import shutil
import struct
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
INDEX = (WEB / "index.html").read_text(encoding="utf-8")
CSS = (WEB / "css" / "main.css").read_text(encoding="utf-8")


def _meta(attr, name):
    m = re.search(r'<meta %s="%s" content="([^"]*)"' % (attr, re.escape(name)), INDEX)
    return m.group(1) if m else None


# ---------- P01 social preview ----------
def test_open_graph_and_twitter_tags():
    assert _meta("property", "og:title") == "El Archivo"
    assert _meta("name", "twitter:title") == "El Archivo"
    assert _meta("property", "og:type") == "website"
    assert _meta("property", "og:url") == "https://elarchivopr.com/"
    assert _meta("property", "og:image") == "https://elarchivopr.com/img/brand/og.png"
    assert _meta("name", "twitter:image") == "https://elarchivopr.com/img/brand/og.png"
    assert _meta("property", "og:locale") == "es_PR"
    assert _meta("property", "og:site_name") == "El Archivo"
    assert _meta("name", "twitter:card") == "summary_large_image"
    desc = _meta("name", "description")
    assert desc and _meta("property", "og:description") == desc and _meta("name", "twitter:description") == desc


def test_canonical_link():
    assert '<link rel="canonical" href="https://elarchivopr.com/">' in INDEX


def test_og_image_exists_is_1200x630_and_under_300_kb():
    p = WEB / "img" / "brand" / "og.png"
    assert p.exists()
    assert p.stat().st_size < 300 * 1024
    head = p.read_bytes()[:24]
    assert head[:8] == b"\x89PNG\r\n\x1a\n"
    w, h = struct.unpack(">II", head[16:24])
    assert (w, h) == (1200, 630)


# ---------- P06 contrast ----------
def _lum(hexc):
    h = hexc.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    f = lambda v: v / 12.92 if v <= .03928 else ((v + .055) / 1.055) ** 2.4
    return .2126 * f(c[0]) + .7152 * f(c[1]) + .0722 * f(c[2])


def _ratio(a, b):
    x, y = sorted([_lum(a), _lum(b)], reverse=True)
    return (x + .05) / (y + .05)


def _light_token(name):
    block = CSS[CSS.index('[data-theme="light"]{'):]
    block = block[:block.index("\n}")]
    return re.search(r"--%s:\s*(#[0-9A-Fa-f]{6})" % name, block).group(1)


def test_light_ink_3_is_4_5_on_every_light_surface_it_sits_on():
    ink3 = _light_token("ink-3")
    for surface in ("raise", "card", "night"):   # --raise is the darkest surface text sits on
        assert _ratio(ink3, _light_token(surface)) >= 4.5, (surface, ink3)
    assert ink3.upper() == "#566888"
    assert _ratio(ink3, _light_token("raise")) >= 4.59      # 4.60:1 on the darkest surface, was 4.33


def test_temporada_perfecta_labels_clear_4_5_in_both_themes():
    games = (WEB / "js" / "games.js").read_text(encoding="utf-8")
    assert not re.search(r"(?<![-\w])color:#(E8B23A|9B6BE0)", games)       # text colour; the card borders keep their hues
    flag_light = _light_token("flag-ink")
    assert _ratio(flag_light, "#FFFFFF") >= 4.5                      # EQUIPO, light, on the white card
    assert _ratio("#7E4ACB", "#FFFFFF") >= 4.5                       # DÉCADA, light
    assert "[data-theme=\"light\"] .dr-lab.dec{color:#7E4ACB}" in CSS
    assert _ratio("#9B6BE0", "#0C1428") >= 4.5                       # DÉCADA, dark, on --card
    assert '[data-theme="light"] .dr-lab.eq{color:var(--flag-ink)}' in CSS
    assert ".dr-lab.eq{color:#E8B23A}" in CSS and _ratio("#E8B23A", "#0C1428") >= 4.5    # EQUIPO, dark: unchanged amber


# ---------- P07 aria-selected on plain buttons ----------
def test_perfil_toggle_buttons_use_aria_pressed_not_aria_selected():
    src = (WEB / "js" / "tabs.js").read_text(encoding="utf-8")
    start = src.index("function buildProfile()")
    body = src[start:start + 6000]
    assert "aria-selected" not in body
    assert "setTheme('${v}')\" aria-pressed=" in body                       # the 3 theme buttons share one template
    assert 'onclick="showPrimer()" aria-pressed=' in body and 'onclick="dismissPrimer()" aria-pressed=' in body
    assert '.modebtns button[aria-pressed="true"]' in CSS


# ---------- P09 crawl files and 404 ----------
def test_robots_sitemap_and_404_exist():
    robots = (WEB / "robots.txt").read_text()
    assert "User-agent: *" in robots and "Allow: /" in robots
    assert "Sitemap: https://elarchivopr.com/sitemap.xml" in robots
    sm = (WEB / "sitemap.xml").read_text()
    assert sm.count("<loc>") == 1 and "<loc>https://elarchivopr.com/</loc>" in sm and "<lastmod>2026-10-12</lastmod>" in sm
    assert "#" not in sm
    assert (WEB / "404.html").exists()


def test_404_page_is_spanish_self_contained_and_accessible():
    t = (WEB / "404.html").read_text(encoding="utf-8")
    assert '<html lang="es">' in t
    assert t.count("<h1>") == 1 and "<h1>No encontramos esa página</h1>" in t
    assert "Puede que el enlace esté mal escrito o que la página ya no exista." in t
    assert ">Ir a Inicio</a>" in t and "min-height:44px" in t
    assert "bsn:theme" in t and "prefers-color-scheme: light" in t
    assert "focus-visible" in t and "prefers-reduced-motion" in t
    # no third-party request: every absolute URL would be a violation (fonts, scripts, images are root-relative)
    assert not re.search(r"https?://", t)
    assert not re.search(r"//[a-z0-9.-]+\.[a-z]{2,}", t.replace("</", ""))


# ---------- P10 service worker ----------
def test_service_worker_registers_without_http_cache_and_checks_for_updates():
    assert "register('sw.js',{updateViaCache:'none'})" in INDEX
    assert ".then(r=>r.update())" in INDEX


def test_asset_hashes_in_index_are_current():
    """A changed css/js file without a new ?v= hash never reaches users inside the 10-minute HTTP cache; the
    pre-commit hook (.githooks/pre-commit) blocks that commit, and this fails the suite before it gets there."""
    import hashlib
    for m in re.finditer(r'(?:href="(css/[^"?]+)|src="(js/[^"?]+))\?v=([0-9a-f]+)"', INDEX):
        rel = m.group(1) or m.group(2)
        assert hashlib.sha256((WEB / rel).read_bytes()).hexdigest()[:12] == m.group(3), rel


# ---------- P03 ----------
def test_layout_shift_sources_are_hidden_while_the_splash_is_up():
    assert "body:has(#splash:not(.gone))" in CSS
    for sel in (".hubpair", ".liga", ".legalrow", ".foot", "#bottombar"):
        assert sel in CSS[CSS.index("body:has(#splash:not(.gone))"):]


# ---------- P12 / P11 ----------
def test_bottom_bar_is_inside_a_named_nav_and_scroll_blocks_are_focusable():
    assert "nv.className='bbnav'; nv.setAttribute('aria-label','Secciones')" in (WEB / "js" / "tabs.js").read_text(encoding="utf-8")
    assert 'tabindex="0" role="group" aria-label="Tabla de datos, desplazable"' in INDEX
    assert "@media(min-width:860px){.bbnav{display:none}}" in CSS
    assert "wrap.setAttribute('role','region')" not in (WEB / "js" / "tabs.js").read_text(encoding="utf-8")


# ---------- browser checks ----------
def _find_playwright_core():
    env = os.environ.get("PLAYWRIGHT_CORE")
    if env and (Path(env) / "index.js").exists():
        return env
    hits = sorted(glob.glob("/private/tmp/**/node_modules/playwright-core/index.js", recursive=True))
    return str(Path(hits[0]).parent) if hits else None


@pytest.fixture(scope="module")
def probe():
    node = shutil.which("node")
    core = _find_playwright_core()
    if not node or not core:
        pytest.skip("needs node and playwright-core (set PLAYWRIGHT_CORE=<dir>)")
    res = subprocess.run([node, str(ROOT / "tests" / "harness" / "phase71_probe.mjs")],
                         env={**os.environ, "PLAYWRIGHT_CORE": core}, capture_output=True, text=True, timeout=900)
    assert res.returncode == 0, res.stderr[-2000:]
    return json.loads(res.stdout)


EXPECTED_TITLES = {
    "inicio": "El Archivo",
    "historia": "Historia · El Archivo",
    "historia/cinta": "La cinta · El Archivo",
    "historia/titulos": "Títulos · El Archivo",
    "jugadores": "Jugadores · El Archivo",
    "jugadores/buscar": "Buscar · El Archivo",
    "jugadores/lideres": "Líderes de carrera · El Archivo",
    "jugadores/records": "Récords · El Archivo",
    "jugadores/comparar": "Comparar · El Archivo",
    "jugadores/salon": "Salón · El Archivo",
    "equipos": "Equipos · El Archivo",
    "juega": "Juega · El Archivo",
    "archivo": "Archivo · El Archivo",
    "archivo/preguntar": "Preguntar · El Archivo",
    "archivo/constructor": "A la medida · El Archivo",
    "archivo/cobertura": "Cobertura y fuentes · El Archivo",
    "archivo/calidad": "Calidad de datos · El Archivo",
    "perfil": "Perfil · El Archivo",
    "privacidad": "Política de privacidad · El Archivo",
    "terminos": "Términos de uso · El Archivo",
    "accesibilidad": "Declaración de accesibilidad · El Archivo",
    "creditos": "Créditos y fuentes · El Archivo",
}


def test_every_route_has_its_own_title_in_both_engines(probe):
    seen = {t["cfg"] for t in probe["titles"]}
    assert seen == {"chromium/1000", "webkit/390"}
    for t in probe["titles"]:
        if t["h"] in EXPECTED_TITLES:
            assert t["title"] == EXPECTED_TITLES[t["h"]], (t["cfg"], t["h"])
        else:   # game views, player page, team page: titled by visible label, never the old shared title
            assert t["title"].endswith(" · El Archivo") and not t["title"].startswith("Baloncesto"), (t["cfg"], t["h"], t["title"])
    by = {(t["cfg"], t["h"]): t["title"] for t in probe["titles"]}
    assert len({v for (c, h), v in by.items() if c == "chromium/1000"}) == len({h for (c, h) in by if c == "chromium/1000"})


def test_player_and_team_pages_are_titled_by_name(probe):
    for t in probe["titles"]:
        if t["h"] == "jugadores/jugador/jose-piculin-ortiz":
            assert "Piculín" in t["title"] and t["title"].endswith(" · El Archivo"), t
        if t["h"] == "equipos/equipo/bay":
            assert t["title"] == "Vaqueros de Bayamón · El Archivo", t


def test_title_follows_in_app_navigation_and_back(probe):
    for b in probe["back"]:
        s = dict(b["seq"])
        assert s["start"] == "El Archivo"
        assert s["historia"] == "Historia · El Archivo"
        assert s["cinta"] == "La cinta · El Archivo"
        assert s["team"] == "Vaqueros de Bayamón · El Archivo"
        assert s["back1"] == "La cinta · El Archivo"
        assert s["back2"] == "Historia · El Archivo"
        assert s["back3"] == "El Archivo"


def test_no_aria_selected_on_non_tab_elements(probe):
    assert probe["ariaSelected"]
    for r in probe["ariaSelected"]:
        assert r["bad"] == [], r


def test_accessible_names_contain_the_visible_text(probe):
    checked = 0
    for r in probe["labelInName"]:
        for i in r["items"]:
            vis, name = i["vis"].lower(), i["name"].lower()
            assert vis in name, (r["cfg"], i)
            checked += 1
    assert checked >= 4 * 2     # header mark on every checked page + 4 game tiles on the Juega hub


def test_no_console_errors_or_horizontal_overflow(probe):
    assert probe["errors"] == []
    assert [o for o in probe["overflow"] if o["over"]] == []


# ---------- 44px tap targets (Perfil toggles, short legal links) ----------
def test_perfil_toggles_and_short_legal_links_have_44px_minimum():
    assert re.search(r"\.profctl \.modebtns button\{[^}]*min-height:44px[^}]*min-width:44px", CSS)
    assert re.search(r"\.legal a,\.legalrow a,\.profnote a\{[^}]*padding:14px 7px;margin:-14px -7px", CSS)
