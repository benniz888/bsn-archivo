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

  5. JS data-quality (step 6): web/js/data-quality.js holds 1 block -- the file's own "CALIDAD DE
     DATOS" section whole: its state (DQ, DQ_IDX, DISPUTE_IDX, DISPUTED_IDS, DQ_T, DQ_SORT,
     DQ_FILTER -- one `let` statement, moved as-is since splitting it would be reformatting),
     ensureDQ, buildDQ, openDQ, drawDQ, drawDQTable. dqFlag/dqTag/disputeFlag/disputeTag stay in
     player.js (step 5) -- moving them here too would split dqFlag from dqTag and disputeFlag
     from disputeTag, so player.js remains the cleaner home; they now read DQ_IDX/DISPUTE_IDX/
     DISPUTED_IDS across files, an ordinary global read like any other.

  6. JS games (step 7): web/js/games.js holds 2 blocks -- CUADRICULA+TEMPORADA_PERFECTA (axLabel/
     axFull/axMatch/solutions, the grid game's axis logic, through the whole "LA CUADRICULA"
     section, directly into the whole "LA TEMPORADA PERFECTA" section -- merged because they sit
     right next to each other with just a blank line between; CAT_KEYS and GRID_CLUBS, declared
     right before axLabel, stayed in web/index.html -- see the FKEYS gotcha below) and
     SUBE_Y_BAJA (HL + newHL/drawHL/answerHL; HL_SETS itself moved to js/data.js in step 3). A
     fourth game, "Quien soy?" (QZ/statClue/newQuiz/...), sits BETWEEN Temporada Perfecta and
     Sube y baja in the original and was NOT named for this step -- left in web/index.html.

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

  CROSS-FILE ordering (step 4's real gotcha, and again in step 6): fmtLongDate was originally
  followed directly by MESES and DIAS (step 3, now in js/data.js), and only THEN by
  _daysInMonth+fmtArchiveDob. Splitting fmtLongDate and _daysInMonth+fmtArchiveDob into two
  separate helpers.js groups isn't enough on its own -- _daysInMonth+fmtArchiveDob's real
  preceding anchor is DIAS's own closing text, which doesn't exist anywhere in web/index.html any
  more (step 3 already moved it). So groups can't be spliced back file-by-file (all of data.js,
  then all of helpers.js): they have to go back in ONE combined list, `_INSERTION_ORDER`, in the
  TRUE original document order -- data.js's MESES+DIAS group sits between helpers.js's
  fmtLongDate and _daysInMonth+fmtArchiveDob groups in that list, so by the time
  _daysInMonth+fmtArchiveDob's anchor search runs, MESES+DIAS has already been spliced back into
  the working text and the anchor is there to find.

  Step 6 hit the same thing from the other direction: player.js's "DQ-tags" group (step 5) was
  given the anchor "ends right where ensureDQ's own closing brace was" -- true at the time, since
  ensureDQ was still in web/index.html. Once step 6 moved ensureDQ itself into
  js/data-quality.js, that anchor text stopped existing in web/index.html. Fix is the same shape:
  js/data-quality.js's one group ("CALIDAD-DATOS") sits BEFORE player.js's "DQ-tags" group in
  `_INSERTION_ORDER` (matching their true original order in app/bsn_archivo.html), so ensureDQ's
  text is already back in the working reconstruction by the time DQ-tags' anchor search runs.
  `_JS_PLAYER_GROUPS["DQ-tags"]`'s anchor itself did NOT need editing -- only its position in
  `_INSERTION_ORDER` did.

  Step 7 turned up two problems, both worth carrying forward as lessons for later steps -- one an
  anchor-ordering issue like steps 4/6, the other a genuinely different kind of bug:

  - SUBE_Y_BAJA's naive anchor (read off the pre-step-7 web/index.html, where it's the text
    right after "Quien soy?") is the exact same text data.js's "HL_SETS" group is ALSO anchored
    on (guessQuiz's own closing lines -- HL_SETS's true original neighbor once its own header
    moved with it in step 3). Reusing it for SUBE_Y_BAJA would insert both groups at the SAME
    spot -- SUBE_Y_BAJA before HL_SETS, not after, since neither anchor search depends on the
    other having run. Fixed with a different anchor for SUBE_Y_BAJA: HL_SETS's own closing text,
    checked against app/bsn_archivo.html's own byte offset before finalizing, same as steps 4/6.

  - CAT_KEYS and GRID_CLUBS are declared right before axLabel in the original and look like they
    belong with it -- but GRID_CLUBS = FKEYS.filter(...) is a top-level `const`, evaluated the
    instant games.js runs, unlike every other cross-file reference in this split, which is safely
    deferred inside a function body. FKEYS is computed in web/index.html's own inline <script>,
    which loads AFTER games.js -- moving GRID_CLUBS threw ReferenceError: FKEYS is not defined at
    games.js's own load time, which aborted the rest of its top-level execution (GB, DR, HL and
    everything after silently never got initialized). This was NOT caught by a static check or a
    byte-offset comparison -- both would have looked fine, since CAT_KEYS/GRID_CLUBS's true
    position IS right before axLabel. It only showed up in the real-browser offline test, as
    "GB is not defined" and console errors on page load. Fixed by leaving CAT_KEYS and GRID_CLUBS
    in web/index.html and starting the group at axLabel instead (which only reads CATS/F/POOL,
    all inside function bodies -- safe). Lesson: a group's true original TEXT position isn't the
    same question as whether it's safe to move -- a `const`/`let` initializer evaluated at a
    script's own top level needs everything it references to already be loaded, regardless of
    where in the document it originally sat; only function bodies get the "loads before it's
    ever called" pass every other cross-file reference in this split has relied on so far.

  Every group placed so far either has no cross-file dependency or has had one worked out up
  front against app/bsn_archivo.html's own byte offsets (the one file that never changes); the
  mechanism doesn't assume the next step won't need the same care -- or, per step 7, a check of
  what's actually a function body versus a top-level statement.

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
DATA_QUALITY_JS = WEB / "js" / "data-quality.js"
GAMES_JS = WEB / "js" / "games.js"

_LINK_RE = re.compile(r'<link\s+rel="stylesheet"\s+href="([^"?]+)(?:\?v=[0-9a-f]+)?">')


def _script_tag_re(src: str) -> re.Pattern:
    return re.compile(r'<script src="' + re.escape(src) + r'(?:\?v=[0-9a-f]+)?"></script>\n')


_DATA_JS_SCRIPT_TAG_RE = _script_tag_re("js/data.js")
_HELPERS_JS_SCRIPT_TAG_RE = _script_tag_re("js/helpers.js")
_PLAYER_JS_SCRIPT_TAG_RE = _script_tag_re("js/player.js")
_DATA_QUALITY_JS_SCRIPT_TAG_RE = _script_tag_re("js/data-quality.js")
_GAMES_JS_SCRIPT_TAG_RE = _script_tag_re("js/games.js")

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

# STEP 6: web/js/data-quality.js's 1 block -- the whole "CALIDAD DE DATOS" section, including its
# state (one `let` statement: DQ, DQ_IDX, DISPUTE_IDX, DISPUTED_IDS, DQ_T, DQ_SORT, DQ_FILTER).
_JS_DATA_QUALITY_GROUPS = {
    "CALIDAD-DATOS": ('/* ============================================================\n   CALIDAD DE DATOS',
                      "tes ofensivos',free_throws:'tiros libres',free_throw_pct:'% de tiros"
                      " libres'};\n\n"),
}

# STEP 7: web/js/games.js's 2 blocks. CAT_KEYS and GRID_CLUBS did NOT move with
# CUADRICULA+TEMPORADA_PERFECTA even though they're declared right before axLabel in the
# original and look like they belong together: GRID_CLUBS = FKEYS.filter(...) is a top-level
# `const`, evaluated the instant games.js runs -- unlike every other cross-file reference in this
# split, which is safely deferred inside a function body. FKEYS is computed in web/index.html's
# own inline <script>, which loads AFTER games.js, so moving GRID_CLUBS would throw
# ReferenceError: FKEYS is not defined at games.js's own load time and abort the rest of its
# top-level execution (caught by the real-browser test, not a static check -- see the STEP 7
# commit message). CAT_KEYS and GRID_CLUBS both stayed in web/index.html; this group's anchor is
# GRID_CLUBS's own closing text. SUBE_Y_BAJA's anchor is HL_SETS's own closing text (NOT
# guessQuiz's tail, which HL_SETS itself is anchored on).
_JS_GAMES_GROUPS = {
    "CUADRICULA+TEMPORADA_PERFECTA": ('function axLabel(a){',
                                      "FKEYS.filter(k=>POOL.filter(p=>p.c.includes(k)).length>=2);"
                                      "\n\n"),
    "SUBE_Y_BAJA": ('let HL=null;\nfunction newHL(keep){',
                    "unit:'títulos'}\n];\n"),
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
    (_JS_DATA_QUALITY_GROUPS, DATA_QUALITY_JS, "CALIDAD-DATOS"),
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
    (_JS_GAMES_GROUPS, GAMES_JS, "CUADRICULA+TEMPORADA_PERFECTA"),
    (_JS_DATA_GROUPS, DATA_JS, "HL_SETS"),
    (_JS_GAMES_GROUPS, GAMES_JS, "SUBE_Y_BAJA"),
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
                         (_PLAYER_JS_SCRIPT_TAG_RE, PLAYER_JS),
                         (_DATA_QUALITY_JS_SCRIPT_TAG_RE, DATA_QUALITY_JS),
                         (_GAMES_JS_SCRIPT_TAG_RE, GAMES_JS)):
        html, n = tag_re.subn("", html, count=1)
        assert n == 1, f"{path.name} script tag not found -- did index.html change?"

    segments_by_file = {DATA_JS: _js_segments(DATA_JS, _JS_DATA_GROUPS),
                        HELPERS_JS: _js_segments(HELPERS_JS, _JS_HELPERS_GROUPS),
                        PLAYER_JS: _js_segments(PLAYER_JS, _JS_PLAYER_GROUPS),
                        DATA_QUALITY_JS: _js_segments(DATA_QUALITY_JS, _JS_DATA_QUALITY_GROUPS),
                        GAMES_JS: _js_segments(GAMES_JS, _JS_GAMES_GROUPS)}

    for groups, path, name in _INSERTION_ORDER:
        _, anchor = groups[name]
        segment = segments_by_file[path][name]
        assert html.count(anchor) == 1, f"{name}: anchor not unique or missing: {anchor!r}"
        idx = html.index(anchor) + len(anchor)
        html = html[:idx] + segment + html[idx:]

    return html
