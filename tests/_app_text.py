"""PHASE_1_SPLIT. app_text() reconstructs app/bsn_archivo.html's exact original text from the
split web/ tree, so every existing test that used to scan APP.read_text() keeps working unchanged
(swap that call for app_text()), and the split's own byte-compare checks can keep proving nothing
was lost or reordered along the way. Two splices happen, in this order:

  1. CSS (step 2): <link rel="stylesheet" href="css/main.css"> back to <style>...</style>. The
     <style> tag's own newline belongs to the tag, not the content, so it's put back here.

  2. JS data (step 3): web/js/data.js holds 13 blocks of hand-curated constants (18 named consts:
     F, RECENT, HOF, RETIRED, REF_RULES, ON_THIS_DAY, POOL, VENUES, FIVE_2026, SEASON_STATE,
     POOL_2026, POOL_RGM, POOL_PATCH, PLAYERS_NEW, MESES, DIAS, CATS, HL_SETS -- a few pairs sit
     right next to each other in the original with nothing but a blank line between, so they moved
     as one merged block), cut out of web/index.html's inline <script> and reassembled ahead of it.
     They were NOT contiguous in the original -- the 13 blocks are scattered across ~6000 lines,
     with other constants (ARENAS, STONE, NEWS, POOL_BSN26, MVP_YEARS, OWNERS, ...) and even a few
     bare statements (F.agu.ru.push(2026) and friends, between POOL and VENUES) sitting in the
     gaps and staying in web/index.html untouched. Getting the boundaries right took reading each
     one: a leading comment almost always describes the block that FOLLOWS it, not the one before
     -- e.g. the comment right before `const VENUES` is VENUES' own header, but the comment right
     before `const VENUE_NOTES` (which never moved) is VENUE_NOTES' header, even though both sit
     in the same run of text right after POOL. A naive "cut up to the next declaration" rule gets
     this wrong; _JS_DATA_GROUPS below is the result of doing it by hand and proving each boundary
     (see the STEP 3 commit message / session notes for how).

     Reconstruction works by anchors, not line numbers: `preceding_anchor` is exact original text
     that survives, byte for byte, in web/index.html immediately before where a group used to sit
     -- the group goes back in right after it. `group_start_marker` is the exact text data.js's
     block begins with, used to cut data.js back into its 13 pieces (each runs up to the next
     marker, or EOF for the last one).

Replaced entirely once app/bsn_archivo.html becomes the archived pointer (step 11/12).
"""
import re

from src.wayback_cdx import REPO_ROOT

WEB = REPO_ROOT / "web"
INDEX = WEB / "index.html"
DATA_JS = WEB / "js" / "data.js"

_LINK_RE = re.compile(r'<link\s+rel="stylesheet"\s+href="([^"?]+)(?:\?v=[0-9a-f]+)?">')
_DATA_JS_SCRIPT_TAG_RE = re.compile(r'<script src="js/data\.js(?:\?v=[0-9a-f]+)?"></script>\n')

# group_start_marker is the exact PREFIX text (long enough to be unique in data.js) each block
# begins with -- for a block with its own header comment, that's the comment's start, not the
# `const NAME` line, since the comment belongs to this block (see the module docstring).
_JS_DATA_GROUPS = [
    ('const F = {\n  bay:{name:"Vaque',
     'id="bottombar" role="tablist" aria-label="Navegación principal"></div>\n<script>\n'),
    ('const RECENT=[\n {year:"2026",l',
     '["J. J. Barea","Started in the BSN."]\n];\n\n'),
    ('const RETIRED=[\n ["Vaqueros de',
     '["Mario Morales","Mario Morales Coliseum · Guaynabo","Home of the Mets."]\n];\n\n'),
    ('/* ---------- on this day ----',
     " juegos. Se fijan fechas, se revisa el formato y se mueven los refuerzos.'}\n];\n\n"),
    ('/* ============================================================\n   PLA',
     'https://play.google.com/store/apps/details?id=io.genius.bsnpr","Built on Genius Sports."]'
     '\n];\n\n'),
    ('/* The league app lists these ',
     "F.agu.coach = 'Rafael «Pachy» Cruz';\nF.cag.coach = 'Wilhelmus Caanen';\n"
     "F.san.coach = '—';\n\n"),
    ("const FIVE_2026 = [\n  ['Travis",
     "['Excelencia Arbitral','Jorge Vázquez','—','']\n];\n"),
    ('/* Reference points for the of',
     "'Tras los 25 puntos del quinto juego.','quote']\n];\n\n"),
    ("const POOL_PATCH = {\n  'Gary B",
     '"pos":"C","posSrc":"perfil","hi":[2026,0]}];\n\n'),
    ('/* ---- Jugadores recuperados ',
     "['agu','Wilson López','']\n];\n\n"),
    ("const MESES=['enero','febrero'",
     "  return parseInt(p[2],10)+' de '+(m||p[1])+' de '+p[0];\n}\n"),
    ('/* ============================================================\n   CAT',
     'function pick(a){return a[Math.floor(Math.random()*a.length)];}\n\n'),
    ('/* ============================================================\n   SUB',
     "$('#qMsg').className='msg bad';\n  }\n}\n\n"),
]


def _js_data_segments() -> list[str]:
    """Splits web/js/data.js back into its 13 original blocks, in original document order."""
    text = DATA_JS.read_text(encoding="utf-8")
    starts = [text.index(marker) for marker, _ in _JS_DATA_GROUPS]
    assert starts == sorted(starts), "data.js blocks are out of order"
    bounds = starts + [len(text)]
    return [text[bounds[i]:bounds[i + 1]] for i in range(len(starts))]


def app_text() -> str:
    html = INDEX.read_text(encoding="utf-8")

    def sub_link(m):
        path = WEB / m.group(1)
        return "<style>\n" + path.read_text(encoding="utf-8") + "</style>"

    html = _LINK_RE.sub(sub_link, html)

    new_html, n = _DATA_JS_SCRIPT_TAG_RE.subn("", html, count=1)
    assert n == 1, "js/data.js script tag not found -- did index.html change?"
    html = new_html

    segments = _js_data_segments()
    for (_, anchor), segment in zip(_JS_DATA_GROUPS, segments):
        assert html.count(anchor) == 1, f"anchor not unique or missing: {anchor!r}"
        idx = html.index(anchor) + len(anchor)
        html = html[:idx] + segment + html[idx:]

    return html
