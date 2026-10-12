"""PHASE_69 -- legal pages, footer, self-hosted fonts, accessibility fixes, delete-my-data control.

Static checks only (no browser): the rendered behaviour (focus moves to the h1, the skip link shows on
focus, the wipe really empties storage, no request leaves the origin) is verified in Chromium and WebKit
by the harness described in docs/audits/phase69_plan.md section 6. These tests keep the facts that the
public text depends on from drifting: if a new localStorage key, a third-party request or a placeholder
appears, one of them fails and the privacy / credits text has to be revisited.
"""
import re
from pathlib import Path

from tests.test_no_emoji_in_web import scan as emoji_scan

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
HTML = (WEB / "index.html").read_text(encoding="utf-8")
CSS = (WEB / "css" / "main.css").read_text(encoding="utf-8")
TABS = (WEB / "js" / "tabs.js").read_text(encoding="utf-8")
SW = (WEB / "sw.js").read_text(encoding="utf-8")
TEXT_SUFFIXES = {".html", ".js", ".css", ".json", ".webmanifest", ".svg", ".txt", ".xml"}
PAGES = ["privacidad", "terminos", "accesibilidad", "creditos"]
INTER = "inter-latin-opsz-normal-5.3.0.woff2"
OSWALD = "oswald-latin-wght-normal-5.3.0.woff2"


def _section(sid):
    m = re.search(r'<section id="%s"(.*?)</section>' % sid, HTML, re.S)
    assert m, f"#{sid} section missing from web/index.html"
    return m.group(0)


def _footer():
    m = re.search(r'<footer class="foot">.*?</footer>', HTML, re.S)
    assert m, "footer missing"
    return m.group(0)


def _text(fragment):
    return re.sub(r"<[^>]+>", "", fragment)


# ---- fonts -------------------------------------------------------------------------------------

def test_no_google_fonts_or_preconnect_anywhere_in_web():
    hits = []
    for p in WEB.rglob("*"):
        if p.is_file() and p.suffix in TEXT_SUFFIXES:
            t = p.read_text(encoding="utf-8", errors="ignore")
            for needle in ("googleapis", "gstatic", "preconnect"):
                if needle in t:
                    hits.append(f"{p.relative_to(ROOT)}: {needle}")
    assert not hits, hits


def test_font_and_licence_files_exist():
    for name, magic in ((INTER, b"wOF2"), (OSWALD, b"wOF2")):
        f = WEB / "fonts" / name
        assert f.is_file(), name
        assert f.read_bytes()[:4] == magic, f"{name} is not woff2"
    assert 72_000 <= (WEB / "fonts" / INTER).stat().st_size <= 74_000
    assert 28_000 <= (WEB / "fonts" / OSWALD).stat().st_size <= 29_000
    for lic in ("OFL-Inter.txt", "OFL-Oswald.txt"):
        t = (WEB / "fonts" / lic).read_text(encoding="utf-8")
        assert "SIL OPEN FONT LICENSE" in t.upper(), lic
    assert "Inter Project Authors" in (WEB / "fonts" / "OFL-Inter.txt").read_text(encoding="utf-8")
    assert "Oswald Project Authors" in (WEB / "fonts" / "OFL-Oswald.txt").read_text(encoding="utf-8")


def test_two_font_face_rules_swap_no_italic():
    faces = re.findall(r"@font-face\{[^}]*\}", CSS)
    assert len(faces) == 2, faces
    assert {re.search(r"font-family:'(\w+)'", f).group(1) for f in faces} == {"Inter", "Oswald"}
    for f in faces:
        assert "font-display:swap" in f
        assert "font-style:normal" in f
        url = re.search(r"url\(\.\./fonts/([^)]+)\)", f).group(1)
        assert (WEB / "fonts" / url).is_file(), url


def test_preloads_match_font_face_files_and_carry_crossorigin():
    preloads = re.findall(r'<link rel="preload"[^>]*>', HTML)
    hrefs = sorted(re.search(r'href="fonts/([^"]+)"', p).group(1) for p in preloads)
    assert hrefs == sorted([INTER, OSWALD])
    for p in preloads:
        assert "crossorigin" in p and 'as="font"' in p and 'type="font/woff2"' in p


def test_service_worker_shell_v3_precaches_fonts_and_routes_them():
    assert "const SHELL = 'bsn-shell-v3'" in SW
    assert "bsn-shell-v2" not in SW.split("const SHELL")[1].split("\n")[0]
    precache = SW.split("const PRECACHE = [")[1].split("];")[0]
    assert INTER in precache and OSWALD in precache
    assert "pathname.includes('/fonts/')" in SW


def test_shipped_text_needs_no_latin_ext_letter():
    """Only the latin subset is shipped. A letter in the latin-ext blocks would render in a fallback face:
    add a latin-ext subset (and its preload / precache / test updates) the day this fails."""
    rx = re.compile("[Ā-İĲ-őŔ-ɏḀ-ỿⱠ-Ɀ꜠-ꟿ]")
    hits = []
    for p in WEB.rglob("*"):
        if p.is_file() and p.suffix in TEXT_SUFFIXES:
            m = rx.search(p.read_text(encoding="utf-8", errors="ignore"))
            if m:
                hits.append(f"{p.relative_to(ROOT)}: U+{ord(m.group()):04X}")
    assert not hits, hits


# ---- pages, router, footer ---------------------------------------------------------------------

def test_four_panels_exist_hidden_with_one_h1_each():
    for sid in PAGES:
        sec = _section(sid)
        assert re.match(r'<section id="%s" hidden role="tabpanel" aria-label="[^"]+"' % sid, sec), sid
        assert len(re.findall(r"<h1[ >]", sec)) == 1, sid


def test_router_knows_the_four_panels():
    panels = re.search(r"const PANELS=(.*);", TABS).group(1)
    for sid in PAGES:
        assert f"'{sid}'" in panels, sid


def test_footer_legal_nav_and_links():
    foot = _footer()
    nav = re.search(r'<nav class="footlegal" aria-label="Información legal">(.*?)</nav>', foot, re.S)
    assert nav, "footer legal nav missing"
    hrefs = re.findall(r'href="#(\w+)"', nav.group(1))
    assert hrefs == PAGES
    labels = re.findall(r">([^<]+)</a>", nav.group(1))
    assert labels == ["Privacidad", "Términos", "Accesibilidad", "Créditos"]
    ids = set(re.findall(r'<section id="(\w+)"', HTML))
    for h in re.findall(r'href="#(\w+)"', HTML):
        assert h in ids or h in {"main"}, f"#{h} does not resolve to a section"


def test_footer_text_is_the_approved_text():
    foot = _text(_footer())
    assert "Google" not in foot
    assert "Proyecto independiente. No es un sitio oficial del BSN. No está afiliado ni respaldado por el Baloncesto Superior Nacional ni por sus equipos." in foot
    assert "Las tipografías se sirven desde este mismo sitio." in foot
    assert "¿Ves un error o quieres que retiremos algo?" in foot
    assert ('href="mailto:benniz.8008@gmail.com" target="_blank"') not in HTML


def test_footer_link_targets_are_44px():
    assert re.search(r"\.footlegal a\{[^}]*min-height:44px", CSS)
    assert re.search(r"\.foot p a\{[^}]*padding:14px", CSS)


def test_every_blank_target_has_noopener():
    for m in re.finditer(r"<a [^>]*target=\"_blank\"[^>]*>", HTML):
        assert "noopener" in m.group(0), m.group(0)


def test_no_placeholder_text_in_legal_panels_footer_perfil_inicio():
    parts = {sid: _text(_section(sid)) for sid in PAGES}
    parts["footer"] = _text(_footer())
    parts["perfil"] = _text(_section("perfil"))
    for name, t in parts.items():
        for bad in ("DRAFT", "CONFIRMAR", "PENDIENTE", "[FECHA", "[DUE"):
            assert bad not in t, (name, bad)
        assert not re.search(r"\[[^\]]*\]", t), (name, re.findall(r"\[[^\]]*\]", t))
    assert not re.search(r"\b(DRAFT|CONFIRMAR|PENDIENTE)\b", HTML.replace("SIN CONFIRMAR", ""))


def test_no_emoji_in_new_markup():
    for sid in PAGES:
        assert not list(emoji_scan(_section(sid))), sid
    assert not list(emoji_scan(_footer()))


def test_owner_decisions_are_in_the_text():
    priv, terms = _text(_section("privacidad")), _text(_section("terminos"))
    assert "12 de octubre de 2026" in priv and "12 de octubre de 2026" in terms
    assert "Nosotros no vemos esos registros." in priv
    assert "Se queda hasta que lo borres tú." in priv
    assert "Cada día el sitio elimina" not in priv  # not true: pruning runs when the site is opened
    assert "Ver, descargar y borrar lo que se guarda." in priv
    assert "«Borrar todos los datos de este dispositivo» elimina todo lo que el sitio guarda" in priv
    assert "lo controlas tú desde Perfil o desde tu navegador" in priv
    assert "hecho por un aficionado y para aficionados" in terms
    assert "No vendemos nada" not in terms
    assert "Lo revisaremos." in terms and "Lo revisamos y respondemos" not in terms
    assert "con todos los derechos reservados" in terms
    assert "No es un sitio oficial del BSN. No está afiliado ni respaldado" in terms


def test_creditos_wikipedia_attribution_and_changes_sentence():
    sec = _section("creditos")
    t = _text(sec)
    assert "https://creativecommons.org/licenses/by-sa/4.0/" in sec
    assert "CC BY-SA 4.0" in t and "Creative Commons Atribución-CompartirIgual 4.0 Internacional" in t
    assert "Se hicieron cambios." in t
    assert "no han sido revisados ni respaldados por Wikipedia ni por sus autores" in t
    assert "https://es.wikipedia.org/" in sec and "https://en.wikipedia.org/" in sec
    assert "Marca e íconos. El logotipo y los íconos de El Archivo son creación de bennizpr." in t
    assert "RealGM" not in t and "latinbasket" not in t.lower()
    assert "fonts/OFL-Inter.txt" in sec and "fonts/OFL-Oswald.txt" in sec


def test_wikipedia_article_links_exist_in_the_repo_sources():
    """L51: every article link in Créditos must already appear in the project's own records (no invented URLs)."""
    sec = _section("creditos")
    links = re.findall(r'href="https://((?:en|es)\.wikipedia\.org/wiki/[^"]+)"', sec)
    assert len(links) >= 10
    corpus = ""
    for base in (ROOT / "web" / "data", ROOT / "data" / "clean", ROOT / "docs", ROOT / "src"):
        for p in base.rglob("*"):
            if p.is_file() and p.suffix in {".json", ".csv", ".md", ".py"}:
                corpus += p.read_text(encoding="utf-8", errors="ignore")
    for l in links:
        assert l in corpus, f"{l} is not in any repo source record"


def test_accesibilidad_lists_match_what_shipped():
    t = _text(_section("accesibilidad"))
    shipped = t.split("Lo que aún falla")[0]
    gaps = t.split("Lo que aún falla")[1]
    # fixes that ship in PHASE_69 are listed as working, not as gaps
    assert "Saltar al contenido" in shipped
    assert "el foco del teclado pasa al título de la página nueva" in shipped
    assert "Puedes ampliar la pantalla con los dedos" in shipped
    for fixed in ("enlace para saltar", "no se mueve al título", "no se puede ampliar", "no tiene contorno"):
        assert fixed not in gaps, fixed
    # known gaps that remain are said out loud
    assert "mismo en todas las pantallas" in gaps
    assert "pendientes de verificar" in gaps
    assert "lectores de pantalla" in gaps and "no todos tienen descripción" in gaps
    assert "huecos" in gaps
    assert "No afirmamos que el sitio las cumpla por completo." in t


# ---- accessibility fixes -----------------------------------------------------------------------

def test_viewport_allows_zoom():
    vp = re.search(r'<meta name="viewport" content="([^"]+)"', HTML).group(1)
    assert "maximum-scale" not in vp and "user-scalable" not in vp


def test_skip_link_is_first_and_targets_main():
    body = HTML.split("<body>")[1].lstrip()
    assert body.startswith('<a class="skip" href="#main"')
    assert ">Saltar al contenido</a>" in body.split("</a>")[0] + "</a>"
    assert '<main class="wrap" id="main" tabindex="-1">' in HTML
    # the hash router would send "#main" to Inicio, so the click handler must cancel navigation
    assert "event.preventDefault()" in body.split("</a>")[0]
    assert re.search(r"\.skip\{[^}]*position:fixed", CSS)
    assert re.search(r"\.skip:focus\{[^}]*top:", CSS)


def test_route_change_moves_focus_to_the_heading():
    fn = TABS.split("function _showPanel(")[1].split("\n}\n")[0]
    assert "querySelectorAll('h1')" in fn and "tabIndex=-1" in fn and "focus({preventScroll:true})" in fn
    assert "classList.contains('gone')" in fn  # not while the splash is still up
    assert re.search(r'h1\[tabindex="-1"\]:focus\{outline:none\}|h1\[tabindex="-1"\]:focus,', CSS)


def test_cell_focus_ring_is_not_suppressed():
    assert not re.search(r"\.cell:hover,\.cell:focus-visible\{[^}]*outline:none", CSS)
    assert re.search(r"\.cell:focus-visible\{outline:2px solid var\(--focus\)", CSS)


# ---- storage inventory and the delete control --------------------------------------------------

DOCUMENTED_KEYS = {"theme", "club", "profile", "recent", "hlbest", "streak", "quiz:recent"}
DOCUMENTED_PREFIXES = ("grid:", "data:")


def test_every_storage_key_in_the_code_is_documented_in_the_privacy_table():
    """The privacy table lists what the browser stores. A new ST key must be added to the table (and here)."""
    found = set()
    for p in (WEB / "js").glob("*.js"):
        t = p.read_text(encoding="utf-8")
        for m in re.finditer(r"ST\.(?:get|json|set|setJSON|del)\(\s*(['\"`])([^'\"`$]+)", t):
            found.add(m.group(2))
    undocumented = {k for k in found
                    if k not in DOCUMENTED_KEYS and not k.startswith(DOCUMENTED_PREFIXES)}
    assert not undocumented, f"undocumented storage keys: {sorted(undocumented)}"
    priv = _text(_section("privacidad"))
    for phrase in ("Tema", "Club favorito", "Nombre opcional", "Últimos jugadores y clubes",
                   "Progreso de los juegos", "Copia de los datos del archivo", "service worker"):
        assert phrase in priv, phrase


def test_perfil_delete_control_strings_and_behaviour():
    for s in ("Borrar todos los datos de este dispositivo",
              "¿Borrar todo lo que este sitio guarda en tu dispositivo? No se puede deshacer.",
              "Borrar todo", "Cancelar",
              "Listo. Se borraron los datos de este dispositivo."):
        assert s in TABS, s
    body = TABS.split("function buildProfile")[1].split("function exportProfile")[0]
    assert not re.search(r"\bconfirm\(", body)  # inline confirmation, not a browser dialog
    assert "indexOf('bsn:')===0" in body and "removeItem" in body
    assert "caches.delete" in body and "'bsn-data'" in body and "'bsn-shell'" in body
    assert "unregister()" in body
    assert "location.reload" not in body  # no reload: see the comment above the wipe handler
    assert "e.key==='Escape'" in body
    assert re.search(r"\.btn\.b44\{[^}]*min-height:44px", CSS)
    for s in ("Qué se guarda en este navegador y cómo borrarlo:",):
        assert s in TABS
    perfil = _text(_section("perfil"))
    assert "Lo que guardas aquí se queda en este navegador. No hay cuentas y este sitio no recibe tus datos." in perfil
    assert "no hay servidor" not in perfil


def test_inicio_and_archivo_links_to_creditos():
    assert 'Sobre este archivo: <a href="#creditos">Créditos y fuentes</a> · <a href="#privacidad">Privacidad</a>' in HTML
    assert '<a href="#creditos">Licencias y créditos completos.</a>' in HTML
