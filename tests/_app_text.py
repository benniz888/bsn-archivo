"""PHASE_1_SPLIT. app_text() reconstructs app/bsn_archivo.html's exact original text from the
split web/ tree, so every existing test that used to scan APP.read_text() keeps working unchanged
(swap that call for app_text()), and the split's own byte-compare checks can keep proving nothing
was lost or reordered along the way. Splices happen in this order:

  1. CSS (step 2): <link rel="stylesheet" href="css/main.css"> back to <style>...</style>. The
     <style> tag's own newline belongs to the tag, not the content, so it's put back here.

  2. JS data (step 3): web/js/data.js holds 13 blocks of hand-curated constants (18 named consts:
     F, RECENT, HOF, RETIRED, REF_RULES, ON_THIS_DAY, POOL, VENUES, FIVE_2026, SEASON_STATE,
     POOL_2026, POOL_RGM, POOL_PATCH, PLAYERS_NEW, MESES, DIAS, CATS, HL_SETS -- a few pairs sit
     right next to each other in the original with nothing but a blank line between, so they moved
     as one merged block), cut out of web/index.html's inline <script> and reassembled ahead of it.

  3. JS helpers (step 4): web/js/helpers.js holds 7 blocks -- the file's own "HELPERS" section
     ($, el, esc, slug, norm, num, dash, pct), the two routing functions that aren't tab-specific
     UI (showTab, then setHash+showView together), the file's own "STORAGE" section plus DATA's
     adjacent header (MEM, ST, DATA), the DOB formatter split in two -- fmtLongDate on its own,
     then separately _daysInMonth+fmtArchiveDob -- and the file's own "SEEDING" section
     (mulberry32, EPOCH, todayStamp, puzzleNo, seededShuffle, pick).

  4. JS player (step 5): web/js/player.js holds 2 blocks -- the "JUGADORES" archive-index run
     (buildPlayerIndex through renderArchiveCard, minus the shared state those functions read/
     write, which stayed behind), and the disputed-row tag/tooltip formatters (dqFlag, dqTag,
     disputeFlag, disputeTag). Both are simple contiguous cuts, no merged/split groups this step.

  None of these were contiguous in the original -- steps 3 and 4 both cut blocks out of a script
  that runs ~7000 lines, with everything else (other constants, tab-specific UI code, even a few
  bare statements like F.agu.ru.push(2026) between POOL and VENUES) staying in web/index.html,
  untouched, in its original relative order. Getting each boundary right took reading the actual
  text: a leading comment almost always describes the block that FOLLOWS it, not the one before
  -- e.g. the comment right before `const VENUES` is VENUES' own header, but the comment right
  before `const VENUE_NOTES` (which never moved) is VENUE_NOTES' header, even though both sit in
  the same run of text right after POOL; step 4's showTab has its own header 3 lines above the
  NAVIGATION section's own header, which belongs to VIEW_SECS (never moved) instead. A naive "cut
  up to the next declaration" rule gets this wrong every time; the *_GROUPS lists below are the
  result of doing it by hand and proving each boundary (see the STEP 3/4 commit messages).

  CROSS-FILE ordering (step 4's real gotcha): fmtLongDate was originally followed directly by
  MESES and DIAS (step 3, now in js/data.js), and only THEN by _daysInMonth+fmtArchiveDob.
  Splitting fmtLongDate and _daysInMonth+fmtArchiveDob into two separate helpers.js groups isn't
  enough on its own -- _daysInMonth+fmtArchiveDob's real preceding anchor is DIAS's own closing
  text, which doesn't exist anywhere in web/index.html any more (step 3 already moved it). So
  groups can't be spliced back file-by-file (all of data.js, then all of helpers.js): they have
  to go back in ONE combined list, `_INSERTION_ORDER`, in the TRUE original document order --
  data.js's MESES+DIAS group sits between helpers.js's fmtLongDate and _daysInMonth+fmtArchiveDob
  groups in that list, so by the time _daysInMonth+fmtArchiveDob's anchor search runs, MESES+DIAS
  has already been spliced back into the working text and the anchor is there to find. Every
  other group this step happens to have no such cross-file dependency, but the mechanism doesn't
  assume that going forward -- future steps just extend `_INSERTION_ORDER` in the right spot.

  Reconstruction works by anchors, not line numbers: `preceding_anchor` is exact original text
  that survives, byte for byte, in the *working* reconstruction so far, immediately before where
  a group used to sit -- the group goes back in right after it. `group_start_marker` is the exact
  text the split-out file's own block begins with, used to cut that file back into its original
  pieces (each runs up to the next marker in the SAME file, or EOF for the last one).

Replaced entirely once app/bsn_archivo.html becomes the archived pointer (step 11/12).
"""
import re

from src.wayback_cdx import REPO_ROOT

WEB = REPO_ROOT / "web"
INDEX = WEB / "index.html"
DATA_JS = WEB / "js" / "data.js"
HELPERS_JS = WEB / "js" / "helpers.js"
PLAYER_JS = WEB / "js" / "player.js"

_LINK_RE = re.compile(r'<link\s+rel="stylesheet"\s+href="([^"?]+)(?:\?v=[0-9a-f]+)?">')


def _script_tag_re(src: str) -> re.Pattern:
    return re.compile(r'<script src="' + re.escape(src) + r'(?:\?v=[0-9a-f]+)?"></script>\n')


_DATA_JS_SCRIPT_TAG_RE = _script_tag_re("js/data.js")
_HELPERS_JS_SCRIPT_TAG_RE = _script_tag_re("js/helpers.js")
_PLAYER_JS_SCRIPT_TAG_RE = _script_tag_re("js/player.js")

# group_start_marker is the exact PREFIX text (long enough to be unique in its file) each block
# begins with -- for a block with its own header comment, that's the comment's start, not the
# `const NAME` line, since the comment belongs to this block (see the module docstring). Each
# dict is keyed the same way, by that marker, so _INSERTION_ORDER can reference entries by name
# without repeating the marker text.

_JS_DATA_GROUPS = {
    "F": ('const F = {\n  bay:{name:"Vaque',
          'id="bottombar" role="tablist" aria-label="Navegación principal"></div>\n<script>\n'),
    "RECENT+HOF": ('const RECENT=[\n {year:"2026",l',
                   '["J. J. Barea","Started in the BSN."]\n];\n\n'),
    "RETIRED+REF_RULES": ('const RETIRED=[\n ["Vaqueros de',
                          '["Mario Morales","Mario Morales Coliseum · Guaynabo","Home of the Mets."]'
                          '\n];\n\n'),
    "ON_THIS_DAY": ('/* ---------- on this day ----',
                    " juegos. Se fijan fechas, se revisa el formato y se mueven los refuerzos.'}"
                    "\n];\n\n"),
    "POOL": ('/* ============================================================\n   PLA',
             'https://play.google.com/store/apps/details?id=io.genius.bsnpr",'
             '"Built on Genius Sports."]\n];\n\n'),
    "VENUES": ('/* The league app lists these ',
               "F.agu.coach = 'Rafael «Pachy» Cruz';\nF.cag.coach = 'Wilhelmus Caanen';\n"
               "F.san.coach = '—';\n\n"),
    "FIVE_2026": ("const FIVE_2026 = [\n  ['Travis",
                  "['Excelencia Arbitral','Jorge Vázquez','—','']\n];\n"),
    "SEASON_STATE+POOL_2026+POOL_RGM": ('/* Reference points for the of',
                                        "'Tras los 25 puntos del quinto juego.','quote']\n];\n\n"),
    "POOL_PATCH": ("const POOL_PATCH = {\n  'Gary B",
                   '"pos":"C","posSrc":"perfil","hi":[2026,0]}];\n\n'),
    "PLAYERS_NEW": ('/* ---- Jugadores recuperados ',
                    "['agu','Wilson López','']\n];\n\n"),
    "MESES+DIAS": ("const MESES=['enero','febrero'",
                   "  return parseInt(p[2],10)+' de '+(m||p[1])+' de '+p[0];\n}\n"),
    "CATS": ('/* ============================================================\n   CAT',
             'function pick(a){return a[Math.floor(Math.random()*a.length)];}\n\n'),
    "HL_SETS": ('/* ============================================================\n   SUB',
                "$('#qMsg').className='msg bad';\n  }\n}\n\n"),
}

# STEP 4: web/js/helpers.js's 7 blocks, same convention. fmtLongDate and daysInMonth+ArchDob are
# separate groups (see the module docstring for why): daysInMonth+ArchDob's anchor is DIAS's own
# text, which lives in data.js, not web/index.html -- resolved by _INSERTION_ORDER below, not by
# this dict alone.
_JS_HELPERS_GROUPS = {
    "HELPERS": ('/* ============================================================\n   HELPERS',
                'if(p.ppg!=null && p.ppg>=20) f+=.2;\n  return f;\n}\n\n'),
    "showTab": ('/* Public nav entry',
                "window.scrollTo({top:0,behavior:smooth?'smooth':'auto'});\n  }\n  return changed;"
                "\n}\n\n"),
    "setHash+showView": ('function setHash(h){',
                         "['historia','jugadores','equipos','juega','archivo'];\nlet VIEW_NOW={};"
                         "\nlet HASH_ECHO=null;\n"),
    "STORAGE+DATA": ('/* ============================================================\n   STORAGE',
                     "Los años treinta son el 20% porque solo hay campeones.</p>';\n}\n"),
    "fmtLongDate": ('function fmtLongDate(iso){',
                    'worth reading even if you go no further.\n'
                    '   ============================================================ */\n'),
    "daysInMonth+ArchDob": ('/* Archive DOBs are stored M/D/YYYY',
                            "const DIAS=['domingo','lunes','martes','miércoles','jueves',"
                            "'viernes','sábado'];\n\n"),
    "SEEDING": ('/* ============================================================\n   SEEDING',
                'else if(mq.addListener) mq.addListener(onChange);\n  }\n}\n\n'),
}

# STEP 5: web/js/player.js's 2 blocks. The "JUGADORES" section's own state (PINDEX, PXWALK,
# PALL, PSLUG, MVP_ID, MANIFEST, ...) stayed in web/index.html -- loadPlayerExtra, buildMVPYears,
# hydrate() and others read/write it too, so it isn't archive-player-page-exclusive; only the
# functions moved. Same for ensureDQ()/DQ_IDX/DISPUTE_IDX (openDQ, the Archivo/calidad tab, needs
# them too) -- only the pure dqFlag/dqTag/disputeFlag/disputeTag formatters moved.
_JS_PLAYER_GROUPS = {
    "JUGADORES-archive": ('function buildPlayerIndex(){',
                          'to the deployed reality; MANIFEST.counts feeds the numbers. */\n'
                          'let MANIFEST=null, DATA_TEXT=false;\n'),
    "DQ-tags": ('/* the conflict a career row belongs to',
               "if(!DISPUTE_IDX.has(k)) DISPUTE_IDX.set(k,[]);\n    DISPUTE_IDX.get(k).push(r);"
               "\n  });\n  return DQ;\n}\n"),
}

# The TRUE original document order, across BOTH files, derived from where each group's marker
# appears in app/bsn_archivo.html (the one file that never moves). Everything is in data.js order
# then helpers.js order EXCEPT the one real interleave: fmtLongDate, then MESES+DIAS, then
# daysInMonth+ArchDob -- see the module docstring.
_INSERTION_ORDER = [
    (_JS_DATA_GROUPS, DATA_JS, "F"),
    (_JS_DATA_GROUPS, DATA_JS, "RECENT+HOF"),
    (_JS_DATA_GROUPS, DATA_JS, "RETIRED+REF_RULES"),
    (_JS_DATA_GROUPS, DATA_JS, "ON_THIS_DAY"),
    (_JS_DATA_GROUPS, DATA_JS, "POOL"),
    (_JS_DATA_GROUPS, DATA_JS, "VENUES"),
    (_JS_DATA_GROUPS, DATA_JS, "FIVE_2026"),
    (_JS_DATA_GROUPS, DATA_JS, "SEASON_STATE+POOL_2026+POOL_RGM"),
    (_JS_DATA_GROUPS, DATA_JS, "POOL_PATCH"),
    (_JS_DATA_GROUPS, DATA_JS, "PLAYERS_NEW"),
    (_JS_PLAYER_GROUPS, PLAYER_JS, "JUGADORES-archive"),
    (_JS_PLAYER_GROUPS, PLAYER_JS, "DQ-tags"),
    (_JS_HELPERS_GROUPS, HELPERS_JS, "HELPERS"),
    (_JS_HELPERS_GROUPS, HELPERS_JS, "showTab"),
    (_JS_HELPERS_GROUPS, HELPERS_JS, "setHash+showView"),
    (_JS_HELPERS_GROUPS, HELPERS_JS, "STORAGE+DATA"),
    (_JS_HELPERS_GROUPS, HELPERS_JS, "fmtLongDate"),
    (_JS_DATA_GROUPS, DATA_JS, "MESES+DIAS"),
    (_JS_HELPERS_GROUPS, HELPERS_JS, "daysInMonth+ArchDob"),
    (_JS_HELPERS_GROUPS, HELPERS_JS, "SEEDING"),
    (_JS_DATA_GROUPS, DATA_JS, "CATS"),
    (_JS_DATA_GROUPS, DATA_JS, "HL_SETS"),
]


def _js_segments(path, groups: dict) -> dict[str, str]:
    """Splits a split-out JS file back into its named original blocks."""
    text = path.read_text(encoding="utf-8")
    items = list(groups.items())
    starts = [text.index(marker) for _, (marker, _anchor) in items]
    assert starts == sorted(starts), f"{path.name} blocks are out of order"
    bounds = starts + [len(text)]
    return {name: text[bounds[i]:bounds[i + 1]] for i, (name, _) in enumerate(items)}


def app_text() -> str:
    html = INDEX.read_text(encoding="utf-8")

    def sub_link(m):
        path = WEB / m.group(1)
        return "<style>\n" + path.read_text(encoding="utf-8") + "</style>"

    html = _LINK_RE.sub(sub_link, html)

    for tag_re, path in ((_DATA_JS_SCRIPT_TAG_RE, DATA_JS), (_HELPERS_JS_SCRIPT_TAG_RE, HELPERS_JS),
                         (_PLAYER_JS_SCRIPT_TAG_RE, PLAYER_JS)):
        html, n = tag_re.subn("", html, count=1)
        assert n == 1, f"{path.name} script tag not found -- did index.html change?"

    segments_by_file = {DATA_JS: _js_segments(DATA_JS, _JS_DATA_GROUPS),
                        HELPERS_JS: _js_segments(HELPERS_JS, _JS_HELPERS_GROUPS),
                        PLAYER_JS: _js_segments(PLAYER_JS, _JS_PLAYER_GROUPS)}

    for groups, path, name in _INSERTION_ORDER:
        _, anchor = groups[name]
        segment = segments_by_file[path][name]
        assert html.count(anchor) == 1, f"{name}: anchor not unique or missing: {anchor!r}"
        idx = html.index(anchor) + len(anchor)
        html = html[:idx] + segment + html[idx:]

    return html
