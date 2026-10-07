"""PHASE_52A -- Archivo layout polish, 3 named fixes, no new user-facing strings.

1. A la medida (#archivo/constructor): Desde/Hasta used to be two separate .field
   children of .filters -- at 390px Contiene+Desde paired up but Hasta, alone, had
   nothing left to wrap beside and landed on its own row (found live: both rendered at
   120px, not their own inline max-width:104px, since .filters>*'s min-width:120px won
   that conflict). Wrapped in one new .qb-range div (buildQB(), tabs.js) so they're one
   flex item from .filters' own point of view -- always wrap together, confirmed live
   (both now render together at 390/320/1000/1280). The result table's uneven row
   heights were any wide ("name") column wrapping onto several lines when its content
   ran long -- the temporadas dataset's own Nota column is the worst offender, long
   enough on some years to wrap while sitting scrolled out of view at phone width,
   inflating just that one row with no visible cause. Capped to a single line
   (#qbResult td.name, scoped -- buildTable()'s own shared rule used by every other
   table in the app is untouched); the full text is never removed from the DOM (still
   selectable, still in the unchanged CSV export) and a native title tooltip is added
   via a MutationObserver set up once in buildQB(), local to that closure, covering
   both runQB()'s own re-renders and buildTable()'s internal sort-click re-render from
   one observer -- confirmed live: titles appear only on cells that actually truncate,
   both before and after a sort click. Row heights confirmed live: before, a
   representative 15-row sample ranged 27.5-125px; after, every row is 27.5px, at
   every checked width/theme.

2. Calendario (#archivo/calendario): the table (FIN REG./PLAYOFFS included) is wider
   than the 390px viewport -- buildTable()'s own .tblwrap already scrolls (overflow:
   auto, confirmed live: scrollWidth 633 vs clientWidth 356 at 390px, not a hard clip),
   but nothing signalled that, so the columns were reachable in principle and
   undiscoverable in practice. An inline block in buildCalendar(), run once right after
   its own buildTable() call, toggles a scoped (#calendarBox only) CSS fade and a
   conditional tabIndex. A real bug surfaced and was fixed during this same phase:
   buildCalendar() runs once, eagerly, from the BOOT list, while the Calendario view is
   still [hidden] -- a hidden element's scrollWidth/clientWidth are both 0, so a plain
   call (or a window 'resize' listener, which never fires just because a hidden element
   becomes visible) permanently concluded "not scrollable" even once the view was later
   shown. Fixed with a ResizeObserver on the wrapper itself, which does fire the moment
   a hidden element's box goes from 0x0 to its real size -- confirmed live: tabIndex
   was -1 on first real page load before this fix, 0 after.

3. Cobertura (#archivo/cobertura): the decade-tile grid (auto-fit, minmax(112px,1fr))
   landed on whatever column count fit the available row width, with no regard for
   COVERAGE's own real length -- a 7+3 orphan row at >=900px, a 3+3+3+1 orphan row at
   390px. A local best(n,min,max) helper inside buildCoverage() picks the largest
   divisor of n within [min,max] if one exists, else falls back to a balanced
   ceiling-division split; buildCoverage() computes it fresh from COVERAGE.length on
   every call (never a literal tile count anywhere in the CSS) and sets 2 custom
   properties inline on .covergrid, read by a narrow-width default rule and a >=900px
   media query. For today's real n=10 this resolves to a clean 2x5 grid at narrow
   widths and 5x2 at >=900px, confirmed live, zero empty cells either tier, at
   320/390/900/1000/1280px.

All 3 fixes are implemented as LOCAL functions/inline blocks, not new top-level
declarations -- the task's own explicit instruction this phase was "do not touch
tests/harness/inventory_main_HEAD.json", so the only way to keep that baseline valid
(476, unchanged) was to add zero new top-level names. Confirmed: a fresh inventory run
this phase still reports 476, matching the untouched baseline file exactly.

No horizontal page scroll: confirmed live, Playwright/Chromium, all 3 views, at
320/390/1000/1280px, light+dark (8 combinations x 3 views = 24 checks, all 0 overflow)
-- see docs/session.md's PHASE_52A entry and /tmp/p52_after.json. This suite's own
convention throughout this engagement is source-level checks in pytest with live
rendering verified separately via the project's Node/Playwright harness (no Python
Playwright binding is installed in this venv -- requirements.txt confirmed); the tests
below follow that same pattern."""

import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
TABS_JS = ROOT / "web/js/tabs.js"
MAIN_CSS = ROOT / "web/css/main.css"


def _tabs_text():
    return TABS_JS.read_text(encoding="utf-8")


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
    """Standing regression guard, same algorithm every PHASE_5x test file in this
    session carries -- re-asserted here since this phase touches main.css again."""

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


class TestZeroNewTopLevelDeclarations:
    """The task's own explicit instruction: do not touch tests/harness/
    inventory_main_HEAD.json. The only way that stays valid is adding nothing new at
    column 0 -- confirmed here directly against the frozen baseline file itself,
    the same JSON the project's own inventory.py tool and src.verify_clean both
    read, rather than just trusting the refactor was complete."""

    def test_no_new_top_level_function_names_from_this_phase(self):
        import json

        baseline = json.loads(
            (ROOT / "tests/harness/inventory_main_HEAD.json").read_text(encoding="utf-8")
        )
        names = {d["name"] for d in baseline["declarations"]}
        # the 3 names this phase's work is built around must NOT appear as their own
        # top-level declarations -- they're local now (a const arrow fn, an inline
        # block, and a MutationObserver callback), all scoped inside an existing
        # top-level function.
        for leaked in ("bestColumnCount", "calScrollAffordance", "qbApplyTruncationTitles"):
            assert leaked not in names

    def test_baseline_file_was_not_edited_this_phase(self):
        import subprocess

        diff = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        ).stdout
        assert "tests/harness/inventory_main_HEAD.json" not in diff.splitlines()


class TestQBRangeGrouping:
    def test_desde_and_hasta_are_wrapped_in_one_qb_range_div(self):
        src = _func_src("buildQB")
        assert '<div class="qb-range">' in src
        assert 'for="qbfrom">Desde' in src
        assert 'for="qbto">Hasta' in src
        range_start = src.index('<div class="qb-range">')
        wrapper_html = src[range_start : src.index("qbclub", range_start)]
        assert 'id="qbfrom"' in wrapper_html
        assert 'id="qbto"' in wrapper_html

    def test_qb_range_is_scoped_to_qbcontrols(self):
        css = _css()
        assert "#qbControls .qb-range{" in css
        assert "#qbControls .qb-range .field{" in css

    def test_qb_range_inputs_get_a_44px_floor(self):
        css = _css()
        start = css.index("#qbControls .qb-range input{")
        end = css.index("}", start)
        assert "min-height:44px" in css[start:end]

    def test_no_unscoped_qb_range_selector(self):
        css = _css()
        assert re.search(r"(?<!#qbControls )\.qb-range\{", css) is None


class TestQBResultRowUniformity:
    def test_wide_columns_are_capped_to_one_line_scoped_to_qbresult(self):
        css = _css()
        assert "#qbResult td.name{" in css
        start = css.index("#qbResult td.name{")
        end = css.index("}", start)
        rule = css[start:end]
        assert "white-space:nowrap" in rule
        assert "text-overflow:ellipsis" in rule
        assert "overflow:hidden" in rule

    def test_does_not_touch_the_shared_buildtable_td_name_rule(self):
        css = _css()
        assert "td.name{white-space:normal;min-width:150px;font-weight:600}" in css

    def test_truncation_titles_use_a_local_mutationobserver_in_buildqb(self):
        src = _func_src("buildQB")
        assert "new MutationObserver(" in src
        assert "scrollWidth>td.clientWidth" in src
        assert "td.title=" in src
        assert "removeAttribute('title')" in src
        assert "childList:true,subtree:true" in src

    def test_observer_is_attached_to_the_real_qbresult_element(self):
        src = _func_src("buildQB")
        assert ".observe($('#qbResult')" in src


class TestCalendarioScrollAffordance:
    def test_affordance_is_scoped_to_calendarbox(self):
        css = _css()
        assert "#calendarBox .tblwrap.has-more-right::after{" in css
        assert "#calendarBox .tblwrap:focus-visible{" in css
        assert re.search(r"(?<!#calendarBox )\.tblwrap\.has-more-right", css) is None

    def test_fade_is_empty_generated_content_not_real_text(self):
        css = _css()
        start = css.index("#calendarBox .tblwrap.has-more-right::after{")
        end = css.index("}", start)
        assert 'content:""' in css[start:end]

    def test_tabindex_is_conditional_on_actually_overflowing(self):
        src = _func_src("buildCalendar")
        assert "scrollWidth>wrap.clientWidth" in src
        assert "wrap.tabIndex=scrollable?0:-1" in src

    def test_uses_resizeobserver_not_a_plain_resize_listener(self):
        # the real bug this phase found and fixed: buildCalendar() runs once, eagerly,
        # while the view is still [hidden] (0x0), and a window 'resize' listener never
        # fires just because a hidden element later becomes visible.
        src = _func_src("buildCalendar")
        assert "new ResizeObserver(update).observe(wrap)" in src
        assert "addEventListener('resize'" not in src

    def test_affordance_block_runs_after_the_calendario_buildtable_call(self):
        src = _func_src("buildCalendar")
        buildtable_idx = src.index("buildTable(host,")
        observer_idx = src.index("new ResizeObserver(update).observe(wrap)")
        assert buildtable_idx < observer_idx


class TestCoberturaGridComputed:
    def test_best_helper_is_local_to_build_coverage_not_top_level(self):
        text = _tabs_text()
        assert "function bestColumnCount(" not in text
        src = _func_src("buildCoverage")
        assert "const best=(n,min,max)=>{" in src

    def test_build_coverage_computes_from_coverage_length_not_a_literal(self):
        src = _func_src("buildCoverage")
        assert "COVERAGE.length" in src
        assert "best(n,2,4)" in src
        assert "best(n,4,7)" in src

    def test_css_reads_the_computed_custom_properties_not_a_fixed_count(self):
        css = _css()
        assert "repeat(var(--cov-cols-narrow),1fr)" in css
        assert "repeat(var(--cov-cols-wide),1fr)" in css
        assert "@media(min-width:900px){.covergrid{grid-template-columns:repeat(var(--cov-cols-wide),1fr)}}" in css

    def test_helper_prefers_the_largest_exact_divisor_in_range(self):
        # port of the real local best() logic -- confirms the algorithm itself,
        # independent of what COVERAGE.length happens to be today.
        def best(n, lo, hi):
            for c in range(hi, lo - 1, -1):
                if n % c == 0:
                    return c
            rows = -(-n // hi)  # ceil
            return min(hi, -(-n // rows))

        assert best(10, 2, 4) == 2
        assert best(10, 4, 7) == 5
        # a prime n (no exact divisor in range) must still return something in range
        assert best(11, 2, 4) == 4
        assert 4 <= best(11, 4, 7) <= 7


class TestNoNewUserFacingStrings:
    def test_build_qb_template_text_nodes_are_unchanged_by_the_restructuring(self):
        # the .qb-range restructuring moved Desde/Hasta's markup around but must not
        # have reworded or retyped either label -- checked directly against the
        # original strings (">Desde<"/">Hasta<" as real rendered text, not a generic
        # accented-character scan, since neither word carries an accent to detect).
        src = _func_src("buildQB")
        assert '<label for="qbfrom">Desde</label>' in src
        assert '<label for="qbto">Hasta</label>' in src
        # and no OTHER quoted Spanish-looking string was introduced by this phase's
        # own new code (the MutationObserver block) -- that part of the function is
        # pure JS/CSS-selector text, so it should contain no accented character at all.
        obs_start = src.index("new MutationObserver(")
        obs_end = src.index("runQB();", obs_start)
        assert re.search(r"[á-úñÁ-ÚÑ¿¡]", src[obs_start:obs_end]) is None

    def test_build_coverage_new_lines_introduce_no_spanish(self):
        src = _func_src("buildCoverage")
        new_lines = "\n".join(
            line for line in src.splitlines()
            if "best(" in line or "--cov-cols" in line or "const best=" in line or "for(let c=" in line
        )
        assert re.search(r"[á-úñÁ-ÚÑ¿¡]", new_lines) is None

    def test_build_coverage_tile_template_itself_is_unchanged(self):
        # the per-tile template (decade label / bar / phrase) -- PHASE_52B only
        # touched the note sentence below the grid, checked separately, in
        # tests/test_archivo_polish_b.py.
        text = _tabs_text()
        assert (
            '<div class="cov"><div class="cy">${esc(c[0])}</div>\n'
            "    <div class=\"cb\"><div class=\"cf\" style=\"width:${c[1]}%;"
            "background:${c[1]>60?'var(--ok)':c[1]>40?'var(--azul)':'var(--rojo)'}\"></div></div>\n"
            '    <div class="cl">${esc(c[2])}</div></div>'
        ) in text

    def test_no_new_quoted_spanish_literal_in_the_phase52a_css(self):
        css = _css()
        start = css.index("/* PHASE_52A (owner-approved, redesign-v2): A la medida's own Desde/Hasta pair")
        end = css.index("background:var(--deep)}", css.index("#calendarBox .tblwrap.has-more-right")) + len(
            "background:var(--deep)}"
        )
        block = css[start:end]
        code_only = re.sub(r"/\*.*?\*/", "", block, flags=re.S)
        assert re.search(r"[á-úñÁ-ÚÑ¿¡]", code_only) is None
