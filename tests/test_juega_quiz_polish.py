"""PHASE_47/47B -- ¿Quién soy? (Quiz; logic stays in web/js/tabs.js, not moved to
games.js) visual/tap-target/terminology pass, plus the plural() helper (web/js/
helpers.js) and its real call sites (HL's unit label, Draft's "disponible", Quiz's
own ppg/rpg/apg/spg/bpg clues), and PHASE_47B's own POS_ES table covering the 3
p.pos codes SLOT_ES doesn't (G/F/F-C). No game logic, scoring, answer matching, pool
selection, or storage keys touched. Source-level checks, the same convention this
session's other PHASE_4x test files use; the live behavior (no overflow at
320/390/1000px, >=44px controls, a visible >=3:1 focus ring, the real singular/
plural renders, every real POOL position resolving to Spanish) was verified live
this phase, see docs/session.md's PHASE_47/47B entries. PHASE_47B's own
investigation found the accent PHASE_47's own plural() fix was accused of dropping
("1 titulo"/"18 titulos") was never actually missing -- confirmed via DOM
codePointAt() inspection and a 4x-zoomed screenshot; the apparent bug was a small,
low-contrast screenshot being hard to read at a glance, not a string/logic error.
No code change was needed for that part; the accent IS asserted below as a
regression guard regardless."""

import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
TABS_JS = ROOT / "web/js/tabs.js"
GAMES_JS = ROOT / "web/js/games.js"
HELPERS_JS = ROOT / "web/js/helpers.js"
DATA_JS = ROOT / "web/js/data.js"
MAIN_CSS = ROOT / "web/css/main.css"


def _strip_block_comments(src):
    return re.sub(r"/\*.*?\*/", "", src, flags=re.S)


def _quiz_source():
    text = TABS_JS.read_text(encoding="utf-8")
    start = text.index("function statClue(p){")
    end = text.index("\nfunction poolDatalist(){", start)
    return text[start:end]


class TestPluralHelper:
    def test_singular_at_exactly_one(self):
        text = HELPERS_JS.read_text(encoding="utf-8")
        assert "const plural=(n,singular,pluralForm)=>n===1?singular:(pluralForm||singular+'s');" in text

    def test_real_call_sites_pass_an_explicit_plural_where_it_is_irregular(self):
        # "tapón" -> "tapones" is not a plain +s; confirm it's passed explicitly,
        # not left to the default suffix.
        text = TABS_JS.read_text(encoding="utf-8")
        assert "plural(p.bpg,'tapón','tapones')" in text


class TestNoPERFECTAOrAllCapsInQuiz:
    def test_no_perfecta_literal_in_quiz_source(self):
        # The only "PERFECTA" displayed anywhere in the app is Grid's own drawBoard()
        # (games.js) -- explicitly out of scope this phase ("do not touch... the Grid
        # code"). Quiz's own output (tabs.js statClue/clueList/newQuiz/drawQuiz/
        # revealClue/guessQuiz) never contained it; confirmed by reading the real
        # source rather than assumed, since the task's own brief referenced it as if
        # it already existed in Quiz.
        src = _quiz_source()
        assert "PERFECTA" not in src

    def test_no_hardcoded_all_caps_text_content_in_quiz(self):
        # The real shape this bug takes (Draft's own "EQUIPO"/"DÉCADA", games.js,
        # confirmed still there and explicitly out of scope this phase) is an
        # all-caps word sitting directly as rendered HTML text content, ">WORD<".
        # A generic string-literal scan is unreliable here -- JS regex literals
        # (e.g. Quiz's own /"/g a few lines below) contain quote characters that
        # confuse a naive paired-quote search; this targeted HTML-text pattern is
        # both the real shape of the known bug and immune to that false match.
        src = _strip_block_comments(_quiz_source())
        caps_runs = re.findall(r">([A-ZÁÉÍÓÚÑ]{3,})<", src)
        assert caps_runs == [], f"all-caps text content found in Quiz source: {caps_runs}"


class TestQuizTapTargetsAndFocus:
    def test_quiz_controls_get_a_44px_floor_at_every_width(self):
        text = MAIN_CSS.read_text(encoding="utf-8")
        start = text.index("#quizGame .btn,#quizGame input[type=text]{")
        end = text.index("}", start)
        assert "min-height:44px" in text[start:end]
        # NOT wrapped in a @media(max-width:...) block -- must apply at 1000px too
        before = text[:start]
        last_media_open = before.rfind("@media")
        last_media_close = before.rfind("}", 0, start)
        # if the nearest preceding @media's own closing brace comes BEFORE this
        # rule, the rule is outside that block (unscoped by width)
        assert last_media_close > last_media_open or last_media_open == -1

    def test_no_focus_suppressing_rule_scoped_to_quiz(self):
        text = MAIN_CSS.read_text(encoding="utf-8")
        assert "#quizGame" not in text or "outline:none" not in text[
            text.index("#quizGame"):text.index("#quizGame") + 400
        ]


class TestQuizPositionUsesSlotEs:
    def test_clue_list_calls_the_real_pos_es_resolver(self):
        src = _quiz_source()
        assert "const pEs=p.pos?posEs(p):null;" in src
        assert "Jugaba de ${p.pos}." not in src  # PHASE_47's own form, still raw
        assert "Jugaba de ${SLOT_ES[p.pos]||p.pos}." not in src  # PHASE_47's partial fix


class TestPosEsCoversEveryRealPosition:
    """PHASE_47B -- SLOT_ES (games.js) only covers the 5 standard codes; POS_ES
    (tabs.js) covers the 3 real but unmapped ones (G/F/F-C, 52 of 376 real POOL
    players, /tmp/p47b_pos_values.txt). Ports posEs()'s own resolution order
    (SLOT_ES/POS_ES direct hit, then posTokens()-split-and-join, then null) to
    Python, the same convention test_owners_retired.py already uses, rather than
    driving a browser."""

    @staticmethod
    def _slot_es():
        text = GAMES_JS.read_text(encoding="utf-8")
        m = re.search(r"const SLOT_ES=\{([^}]*)\}", text)
        return dict(re.findall(r"(\w+):'([^']*)'", m.group(1)))

    @staticmethod
    def _pos_es():
        text = TABS_JS.read_text(encoding="utf-8")
        m = re.search(r"const POS_ES=\{([^}]*)\}", text)
        return dict(re.findall(r"(\w+|'[^']*'):'([^']*)'", m.group(1).replace("'F/C'", "FC")))

    def test_all_eight_real_codes_resolve_without_posTokens(self):
        slot_es, pos_es = self._slot_es(), self._pos_es()
        for code in ["PG", "SG", "SF", "PF", "C"]:
            assert code in slot_es
        for code in ["G", "F", "FC"]:  # FC stands in for 'F/C', the real POOL code
            assert code in pos_es

    def test_g_and_fc_reuse_already_established_cats_wording_not_new(self):
        # Grid's own CATS categories (data.js) already treat bare "G" as part of
        # 'guard' (/G|PG|SG/) and "F/C" as part of 'big' (/C|PF|F\/C/) -- the SAME
        # real Spanish phrases, not invented for this phase.
        text = DATA_JS.read_text(encoding="utf-8")
        assert "guard:['Base o escolta'" in text
        assert "big:['Poste'" in text
        pos_es = self._pos_es()
        assert pos_es["G"] == "Base o escolta"
        assert pos_es["FC"] == "Poste"

    def test_f_is_flagged_as_a_new_proposal_in_the_strings_file(self):
        strings_file = Path("/tmp/p47b_strings.txt")
        if strings_file.exists():
            assert "NEW PROPOSAL" in strings_file.read_text(encoding="utf-8")

    def test_no_raw_position_code_can_reach_the_clue_text(self):
        # every real POOL position either resolves via SLOT_ES/POS_ES directly, or
        # (for a hypothetical future compound) via posTokens()-splitting -- ported
        # as: any code made of real, individually-mapped tokens joined by '/'
        # must resolve to something that is NOT itself one of the raw codes.
        slot_es, pos_es = self._slot_es(), self._pos_es()
        combined = {**slot_es, **{("F/C" if k == "FC" else k): v for k, v in pos_es.items()}}
        real_codes = ["PG", "SG", "SF", "PF", "C", "G", "F", "F/C"]
        for code in real_codes:
            resolved = combined.get(code)
            assert resolved, f"{code} does not resolve directly"
            assert resolved not in real_codes, f"{code} resolved to another raw code: {resolved}"


class TestNoMoreVacioInDraft:
    def test_vacio_string_is_gone_from_games_js(self):
        # PHASE_46's own explanatory comment quotes the old "· vacío" text while
        # describing an unrelated contrast fix -- accurate history, correctly left
        # in place; strip comments before checking the real CODE no longer uses it.
        text = _strip_block_comments(GAMES_JS.read_text(encoding="utf-8"))
        assert "vacío" not in text

    def test_sin_opciones_is_the_replacement(self):
        text = GAMES_JS.read_text(encoding="utf-8")
        assert "' · sin opciones'" in text


class TestDraftDisponibleIsComputed:
    def test_avail_count_and_plural_share_one_computed_value(self):
        text = GAMES_JS.read_text(encoding="utf-8")
        assert "const avail=poolFor(DR.club,DR.dec).length;" in text
        assert "${avail} ${plural(avail,'disponible')}" in text


class TestHLUnitAccentIsPresent:
    """PHASE_47B -- investigated a reported "1 titulo"/"18 titulos" (no accent) and
    found no actual bug: the real HL_SETS unit string already carries the accent
    (data.js), and PHASE_47's own unitSingular=HL.set.unit.replace(/s$/,'') only
    strips the trailing "s" -- it cannot touch the í. Confirmed two ways live: DOM
    codePointAt() on the real rendered card (í = U+00ED in both "título" and
    "títulos") and a 4x-zoomed screenshot where the accent mark is clearly visible.
    These assertions guard the SOURCE text carries the accent, which is the only
    thing that could regress; the rendering itself was never broken."""

    def test_data_js_titulos_unit_carries_the_accent(self):
        text = DATA_JS.read_text(encoding="utf-8")
        assert "unit:'títulos'" in text
        assert "unit:'titulos'" not in text  # the unaccented form must never appear

    def test_the_singular_is_derived_not_hardcoded_so_it_cant_lose_the_accent(self):
        text = GAMES_JS.read_text(encoding="utf-8")
        assert "const unitSingular=HL.set.unit.replace(/s$/,'');" in text

    def test_every_hl_set_unit_is_a_plain_regular_plural(self):
        # confirms the one global assumption unitSingular's regex relies on: every
        # real unit ends in a plain "s" with nothing irregular underneath (unlike
        # Quiz's own "tapón"/"tapones", which is why that one needed an explicit
        # pluralForm instead of this same derive-by-stripping shortcut).
        text = DATA_JS.read_text(encoding="utf-8")
        start = text.index("const HL_SETS=[")
        end = text.index("];", start)
        units = re.findall(r"unit:'([^']*)'", text[start:end])
        assert units == ["puntos", "rebotes", "asistencias", "juegos", "títulos"]
        assert all(u.endswith("s") for u in units)
