"""PHASE_51 -- Calidad de datos tap targets (#archivo/calidad) and the Archivo hero
arcs staying inside the hero box at desktop widths.

Scope A: the survey found ~393-413 controls under 44px on #archivo/calidad (drawDQ/
drawDQTable, web/js/data-quality.js) -- player-name buttons, year chips, Ficha/jug05
ratio links, CSV buttons, filter inputs/select, the "filas idénticas" disclosure, plus
the inline "Calidad de datos" link on Cobertura (#sourcesBox, buildSources() in
tabs.js). Fixed with #dqBox-/#sourcesBox-scoped CSS only (no JS/markup change, same
tables/columns/data/sort/filter/copy) -- verified live this phase, see docs/session.md's
PHASE_51 entry: 406-416 offenders before, 0 after, at 320/390/1000px, light+dark,
measured by bounding-box against the real rendered page.

Scope B: live measurement during this phase found the actual root cause of the
"arcs sweep past the hero" bug was NOT the PHASE_49B mask -- it was a pre-existing
comment in main.css (`--ink*/--rojo`, PHASE_11's own block, lines unrelated to any
Archivo-specific work) containing the literal substring `*/`, which closed that CSS
comment early and silently dropped the very next rule, `.hhero{overflow:hidden}`, from
every browser's parsed stylesheet -- confirmed live via the real CSSOM (document.
styleSheets), not assumed. With overflow never actually hidden, the hero's own ::before
ring layer (PHASE_49B) was never actually being clipped to the hero box, on ANY section,
not just Archivo. Fixing the one-character comment typo restores overflow:hidden
everywhere .hhero is used -- the existing clip-to-box behavior the CSS already asked
for starts working, no new clip-path or duplicate containment rule needed. Regression-
checked live that Historia/Jugadores/Equipos/Juega's own heroes are unaffected (still
render correctly, no console errors, same ring pattern just now also correctly
contained, which they never visibly needed before since their own lede text is shorter/
narrower than Archivo's)."""

import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
MAIN_CSS = ROOT / "web/css/main.css"
TABS_JS = ROOT / "web/js/tabs.js"
DQ_JS = ROOT / "web/js/data-quality.js"


def _css():
    return MAIN_CSS.read_text(encoding="utf-8")


class TestNoStrayStarSlashInAnyComment:
    """Regression guard for the root cause found this phase: a CSS comment containing
    the literal substring '*/' silently truncates and drops the next rule, with no
    error thrown anywhere. Counts every '/* ... */' pair via the same first-match
    algorithm a real CSS tokenizer uses, and asserts the total number of closing '*/'
    sequences in the file exactly equals the number of comments found that way -- any
    extra '*/' (embedded inside what should have been comment prose) throws this off."""

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
        total_close_markers = text.count("*/")
        assert total_close_markers == n, (
            f"{total_close_markers} '*/' sequences found but only {n} real comments -- "
            "a comment likely contains a literal '*/' that closes it early"
        )

    def test_the_specific_phase11_token_list_no_longer_contains_the_literal(self):
        text = _css()
        assert "--ink*/--rojo" not in text
        assert "--sp-*/--fs-*" not in text


class TestHheroOverflowHiddenRuleIsReal:
    def test_overflow_hidden_rule_present_immediately_before_background_rule(self):
        text = _css()
        assert ".hhero{position:relative;padding:var(--sp-6) 0 var(--sp-3);overflow:hidden}" in text


class TestCalidadScopedToDqBox:
    def test_every_new_calidad_rule_is_scoped_under_dqbox(self):
        css = _css()
        start = css.index("/* PHASE_51")
        end = css.index("/* ---------- controls ---------- */", start)
        block = css[start:end]
        rule_selectors = re.findall(r"(?:^|\})\s*([^{/\n][^{]*)\{", block)
        bad = [s.strip() for s in rule_selectors if not s.strip().startswith("#dqBox") and not s.strip().startswith("#sourcesBox")]
        assert bad == [], f"unscoped selector(s) found in the PHASE_51 block: {bad}"

    def test_does_not_touch_the_shared_buildtable_or_tblwrap_base_rules(self):
        css = _css()
        start = css.index("/* PHASE_51")
        end = css.index("/* ---------- controls ---------- */", start)
        block = css[start:end]
        # the shared, unscoped selectors every other section's tables also use --
        # none of them may appear as a BARE top-level selector (only preceded by
        # "#dqBox " / "#sourcesBox ") in this new block. re.search with a negative
        # lookbehind, not a plain substring check, since "#dqBox .btn{" legitimately
        # CONTAINS the substring ".btn{" as part of a correctly-scoped selector.
        for bare in (r"\.tblwrap\{", r"\.btn\{", r"\.filters\{", r"(?<![\w-])th\{", r"(?<![\w-])td\{"):
            pattern = r"(?<!#dqBox )(?<!#sourcesBox )" + bare
            match = re.search(pattern, block)
            assert match is None, f"found unscoped shared selector near {block[max(0,match.start()-20):match.end()] if match else ''!r}"

    def test_player_name_and_csv_buttons_get_44px_min_height(self):
        css = _css()
        assert "#dqBox .btn{display:inline-flex;align-items:center;min-height:44px" in css

    def test_year_buttons_get_44px_both_dimensions(self):
        css = _css()
        start = css.index("#dqBox td.num button{")
        end = css.index("}", start)
        rule = css[start:end]
        assert "min-height:44px" in rule
        assert "min-width:44px" in rule

    def test_ratio_links_get_44px_both_dimensions_and_stay_right_aligned(self):
        css = _css()
        start = css.index("#dqBox td.num a{")
        end = css.index("}", start)
        rule = css[start:end]
        assert "min-height:44px" in rule
        assert "min-width:44px" in rule
        assert "justify-content:flex-end" in rule

    def test_sort_headers_get_taller_padding_and_a_min_width(self):
        css = _css()
        start = css.index("#dqBox th.sortable{")
        end = css.index("}", start)
        rule = css[start:end]
        assert "min-width:44px" in rule

    def test_filter_inputs_and_select_get_44px_min_height(self):
        css = _css()
        assert "#dqBox .filters input,#dqBox .filters select{min-height:44px}" in css

    def test_disclosure_summary_gets_44px_min_height(self):
        css = _css()
        assert "#dqBox details>summary{display:flex;align-items:center;min-height:44px" in css


class TestCoberturaLinkFixed:
    def test_the_named_link_is_targeted_by_href_not_a_broad_selector(self):
        css = _css()
        assert '#sourcesBox p.muted a[href="#archivo/calidad"]{' in css

    def test_fix_uses_padding_plus_equal_negative_margin_not_inline_flex(self):
        # PHASE_51D: the first pass (inline-flex + min-height:44px) grew the
        # surrounding <p>'s own line box (36px -> 62px at 320/390px, found live) --
        # replaced with inline-block + padding + an equal, opposite margin, which
        # keeps the link's own border box (what getBoundingClientRect measures and
        # what clicks hit-test against) at 44px tall without the element contributing
        # that extra height to the paragraph's own flow.
        css = _css()
        start = css.index('#sourcesBox p.muted a[href="#archivo/calidad"]{')
        end = css.index("}", start)
        rule = css[start:end]
        assert "display:inline-block" in rule
        assert "display:inline-flex" not in rule
        assert "min-height" not in rule
        m_pad = re.search(r"padding:(\d+)px 0", rule)
        m_mar = re.search(r"margin:(-\d+)px 0", rule)
        assert m_pad and m_mar, f"expected padding:Npx 0 and margin:-Npx 0 in {rule!r}"
        assert int(m_mar.group(1)) == -int(m_pad.group(1)), "margin must exactly cancel padding"

    def test_padding_plus_line_height_reaches_the_44px_floor(self):
        # the paragraph's own line-height is 18px (confirmed live, both themes,
        # every checked width) -- 2x this rule's own padding + 18 must be >= 44.
        css = _css()
        start = css.index('#sourcesBox p.muted a[href="#archivo/calidad"]{')
        end = css.index("}", start)
        rule = css[start:end]
        pad = int(re.search(r"padding:(\d+)px 0", rule).group(1))
        assert pad * 2 + 18 >= 44

    def test_the_two_other_similar_links_on_a_player_page_are_untouched(self):
        # seasonTotalsNote() (tabs.js) has 2 near-identical "ver Calidad de datos"
        # links on a DIFFERENT view (a player's Resumen/Temporadas tab) -- the task
        # named only the Cobertura one; these stay exactly as they were.
        text = TABS_JS.read_text(encoding="utf-8")
        assert text.count('<a href="#archivo/calidad">ver Calidad de datos</a>') == 2


class TestNoNewUserFacingStrings:
    def test_data_quality_js_source_is_byte_unchanged(self):
        # PHASE_51 is CSS-only for Scope A -- drawDQ/drawDQTable/btn/pair all keep
        # their exact existing copy; nothing here should differ from before the phase.
        text = DQ_JS.read_text(encoding="utf-8")
        assert "Cifras que no coinciden" in text
        assert "Las diferencias entre fuentes" not in text  # that sentence lives in tabs.js, not here

    def test_no_quoted_spanish_literal_in_the_phase51_css_block(self):
        css = _css()
        start = css.index("/* PHASE_51")
        end = css.index("/* ---------- controls ---------- */", start)
        # strip comments first -- the block's own explanatory prose is English with
        # Spanish quotes IN comments only ("filas idénticas" etc.), never real CSS.
        code_only = re.sub(r"/\*.*?\*/", "", css[start:end], flags=re.S)
        assert re.search(r"[á-úñÁ-ÚÑ¿¡]", code_only) is None


class TestHeroPaddingNeutralizedPositionAndOverflowKept:
    """PHASE_51E -- owner decision: keep every section's hero at its pre-*/-fix height.
    position:relative/overflow:hidden stay (the Archivo arc layer and its clipping both
    depend on them); only the now-restored padding is zeroed back out, via a later
    override rule rather than editing the original .hhero rule body (task's own explicit
    instruction) -- real browser measurement confirmed computed padding is 0px and
    height matches the pre-fix baseline for all 5 sections at 390/1000px, see
    docs/session.md's PHASE_51E entry and /tmp/p51e_hero_table.out; the checks here are
    the source-level guards that the two rules exist in the right shape and order."""

    def test_original_hhero_rule_is_byte_unchanged_and_keeps_position_and_overflow(self):
        css = _css()
        assert ".hhero{position:relative;padding:var(--sp-6) 0 var(--sp-3);overflow:hidden}" in css

    def test_a_later_override_zeroes_the_padding_back_out(self):
        css = _css()
        base_idx = css.index(".hhero{position:relative;padding:var(--sp-6) 0 var(--sp-3);overflow:hidden}")
        override_idx = css.index(".hhero{padding:0}")
        assert override_idx > base_idx, "the padding:0 override must come AFTER the base rule to win the cascade"

    def test_override_rule_does_not_redeclare_position_or_overflow(self):
        # the override's only job is padding -- position:relative/overflow:hidden must
        # keep coming from the original (unedited) rule, not be duplicated here.
        css = _css()
        start = css.index(".hhero{padding:0}")
        end = css.index("}", start) + 1
        rule = css[start:end]
        assert rule == ".hhero{padding:0}"

    def test_override_comment_contains_no_premature_star_slash(self):
        css = _css()
        start = css.index("/* PHASE_51E")
        end = css.index(".hhero{padding:0}")
        comment = css[start:end]
        # the comment's own closing "*/" is the last thing before the rule -- strip it
        # and confirm no OTHER "*/" hides earlier in the prose (this phase's whole
        # reason for existing was exactly that class of bug).
        assert comment.rstrip().endswith("*/")
        body = comment.rstrip()[:-2]
        assert "*/" not in body
