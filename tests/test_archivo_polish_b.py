"""PHASE_52B -- 2 approved Spanish-string changes, plus a layout-only fix to
Calendario's "Temporada por temporada" table. No other user-visible text changed
(confirmed by grepping the full diff for added/removed lines containing a Spanish-
accented character -- see docs/session.md's PHASE_52B entry for the exact list, which
must be exactly these 2 changes).

1. Preguntar's #askInput placeholder (web/index.html) shortened from the 3-clause
   example ("¿Quién ganó en 1971?  ·  títulos de Bayamón  ·  líder de anotación 1987")
   to just the first clause ("¿Quién ganó en 1971?") -- the other 2 clauses still
   exist, unchanged, as 2 of the 14 ASK_EXAMPLES chips rendered below the input
   (confirmed live, PHASE_52A's own follow-up check already found this).

2. Cobertura's note under the decade grid (buildCoverage(), tabs.js) gets one new
   clause ("una estimación editorial de") and its own "20%" literal is now derived
   from COVERAGE[0][1] instead of being a second, independently-typed copy of the
   same number already sitting in the data array -- the rendered text is unchanged
   today (COVERAGE[0][1] is still 20) but the two values can no longer drift apart.

3. Calendario's Formato column (#calendarBox) -- the shared td.name rule's own
   min-width:150px let the real Formato text (up to 91 characters) wrap onto as many
   as 6 lines at 390px (measured live via Range.getClientRects() line-counting, not
   guessed from row height: 5/3/6 lines for the table's 3 real rows), inflating that
   row far past its single-line neighbors. Scoped to #calendarBox, widened to 350px --
   confirmed live, same line-counting method, down to at most 2 lines (2/2/2) at
   320/390px, with rows now uniform (47px each) and no word ever clipped (text-
   overflow is never set on this rule, only white-space:normal, inherited from the
   shared rule, continues to wrap). PHASE_52A's own scroll-fade/tabIndex mechanism
   (scrollWidth grew from 633 to 833 at 390px) re-verified working after the width
   change: still toggles on/off correctly based on real overflow at every checked
   width, visible focus ring unchanged."""

import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
TABS_JS = ROOT / "web/js/tabs.js"
INDEX_HTML = ROOT / "web/index.html"
MAIN_CSS = ROOT / "web/css/main.css"


def _tabs_text():
    return TABS_JS.read_text(encoding="utf-8")


def _html():
    return INDEX_HTML.read_text(encoding="utf-8")


def _css():
    return MAIN_CSS.read_text(encoding="utf-8")


def _func_src(name):
    text = _tabs_text()
    start = text.index(f"function {name}(")
    depth = 0
    i = text.index("{", start)
    j = i
    while True:
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                break
        j += 1
    return text[start : j + 1]


class TestNoStrayStarSlashStillHolds:
    def test_star_slash_count_matches_real_comment_count(self):
        text = _css()
        i = 0
        n = 0
        while True:
            start = text.find("/*", i)
            if start == -1:
                break
            end = text.find("*/", start + 2)
            assert end != -1, f"unclosed comment starting at offset {start}"
            n += 1
            i = end + 2
        assert text.count("*/") == n


class TestAskPlaceholder:
    def test_placeholder_is_shortened_to_just_the_first_clause(self):
        html = _html()
        assert 'placeholder="¿Quién ganó en 1971?"' in html

    def test_old_three_clause_placeholder_is_gone(self):
        html = _html()
        assert "títulos de Bayamón  ·  líder de anotación 1987" not in html

    def test_aria_label_on_askinput_is_unchanged(self):
        # only the visible placeholder was approved to change -- the input's own
        # accessible name (a short, different, pre-existing string) must still be
        # exactly what it always was.
        html = _html()
        assert 'aria-label="Pregunta al archivo"' in html

    def test_the_two_dropped_clauses_still_exist_as_ask_examples_chips(self):
        text = _tabs_text()
        start = text.index("const ASK_EXAMPLES=[")
        end = text.index("];", start)
        block = text[start:end]
        assert "'títulos de Bayamón'" in block
        assert "'líder de anotación 1987'" in block
        assert "'¿Quién ganó en 1971?'" in block


class TestCoberturaNote:
    def test_new_note_wording_is_present(self):
        src = _func_src("buildCoverage")
        assert "una estimación editorial de cuánto de lo que uno querría saber" in src

    def test_old_note_wording_is_gone(self):
        src = _func_src("buildCoverage")
        assert "El porcentaje es cuánto de lo que uno querría saber" not in src

    def test_20_percent_is_derived_from_coverage_not_a_second_literal(self):
        src = _func_src("buildCoverage")
        assert "${COVERAGE[0][1]}%" in src
        # the literal "20" must not appear a second time in this function as its own
        # independent copy of the same number (COVERAGE's own array literal, read
        # elsewhere in the file, is the only place "20" is allowed to be typed).
        note_line = next(line for line in src.splitlines() if "estimación editorial" in line)
        assert "20%" not in note_line

    def test_coverage_zero_one_is_still_the_real_1930s_twenty_value(self):
        # confirms the derivation points at the right cell -- if COVERAGE's own
        # shape ever changes this would catch a silent mismatch.
        text = _tabs_text()
        start = text.index("const COVERAGE=[")
        first_entry_end = text.index("]", start)
        first_entry = text[start : first_entry_end + 1]
        assert "'1930s',20," in first_entry.replace(" ", "")


class TestCalendarioRowUniformity:
    def test_formato_min_width_is_scoped_to_calendarbox(self):
        css = _css()
        assert "#calendarBox td.name{min-width:350px}" in css
        assert re.search(r"(?<!#calendarBox )td\.name\{min-width:350px\}", css) is None

    def test_does_not_touch_the_shared_td_name_min_width(self):
        css = _css()
        assert "td.name{white-space:normal;min-width:150px;font-weight:600}" in css

    def test_no_text_overflow_ellipsis_on_the_calendario_rule(self):
        # the task's own explicit instruction: wrap, never clip, this column's words.
        css = _css()
        start = css.index("#calendarBox td.name{min-width:350px}")
        end = css.index("}", start) + 1
        rule = css[start:end]
        assert "text-overflow" not in rule
        assert "white-space:nowrap" not in rule

    def test_vertical_align_top_is_scoped_to_calendarbox_too(self):
        css = _css()
        assert "#calendarBox td{vertical-align:top}" in css
        assert re.search(r"(?<!#calendarBox )td\{vertical-align:top\}", css) is None


class TestNoOtherSpanishTextChanged:
    def test_build_qb_still_has_only_desde_hasta(self):
        # standing guard from PHASE_52A, re-checked here since this phase also
        # touched tabs.js -- confirms the restructuring wasn't reworded as a side
        # effect of this phase's own edits.
        src = _func_src("buildQB")
        assert '<label for="qbfrom">Desde</label>' in src
        assert '<label for="qbto">Hasta</label>' in src

    def test_calendario_formato_css_block_introduces_no_new_spanish(self):
        css = _css()
        start = css.index("/* PHASE_52B (owner-approved, redesign-v2): at 390px the Formato column")
        end = css.index("#calendarBox td{vertical-align:top}") + len("#calendarBox td{vertical-align:top}")
        block = css[start:end]
        code_only = re.sub(r"/\*.*?\*/", "", block, flags=re.S)
        assert re.search(r"[á-úñÁ-ÚÑ¿¡]", code_only) is None
