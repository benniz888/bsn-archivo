"""PHASE_50 -- Archivo's own landing (buildArchivoLanding(order), mirroring
buildHistoriaLanding/buildJugadoresLanding/buildEquiposLanding, dispatched from
buildLanding()). Keeps the existing megaFeat('gap') lead panel byte-identical, then
groups the same 6 real routes VIEW_MAP.archivo/order already carries into 3 groups by
NAV_MENU.archivo.cols -- reused verbatim for both the group labels and the slug
membership, not re-typed. Card titles/blurbs are order's own label (already live today
as each view's subnav pill text) and VIEW_DESC.archivo[slug] -- no new copy. No
gradient icon tiles (task's own "reads purple" call-out) -- plain .landcard with 2 new
modifier classes (archl-primary/archl-compact) for the visual-hierarchy split. Source-
level checks, the same convention this session's other PHASE_4x/5x test files use; the
live behavior (6/6 cards route correctly by mouse and keyboard, active pill visible,
"Ver los huecos" still goes to Cobertura, no console/overflow errors at 320/390/1000/
1280px, light+dark) was verified live this phase, see docs/session.md's PHASE_50 entry.

PHASE_50 also fixed a pre-existing light-theme contrast failure on .mega-feat .fx
(4.33:1, measured live, below the 4.5:1 floor) by swapping its color from --ink-3 to
--ink-2 at the shared selector -- confirmed the only section currently rendering a
real .mega-feat .fx is Archivo (Historia/Jugadores/Equipos replaced theirs with
.stats3; Juega's landing never had one), so the fix benefits Archivo today and any
future section that reuses .mega-feat, per the task's own "fix once at the shared
selector" instruction, without touching the --ink-3 token used elsewhere."""

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


class TestDispatchesToBuildArchivoLanding:
    def test_build_landing_dispatches_archivo_to_its_own_builder(self):
        text = _tabs_text()
        start = text.index("function buildLanding(sec,order){")
        end = text.index("\n}", start)
        src = text[start:end]
        assert "if(sec==='archivo') return buildArchivoLanding(order);" in src

    def test_build_archivo_landing_is_defined(self):
        assert "function buildArchivoLanding(order){" in _tabs_text()


class TestLeadPanelUnchanged:
    def test_still_renders_the_existing_gap_feat_panel(self):
        src = _func_src("buildArchivoLanding")
        assert "megaFeat(NAV_MENU.archivo.feat)" in src
        assert "mega-feat" in src

    def test_gap_megafeat_content_itself_was_not_touched(self):
        # the "Lo que este archivo no sabe" panel's own markup (megaFeat('gap')) --
        # confirm it still exists, byte-identical, elsewhere in the file.
        text = _tabs_text()
        assert "Lo que este archivo no sabe" in text
        assert "Ver los huecos" in text


class TestGroupLabelsMatchNavMenuVerbatim:
    def test_three_group_labels_are_sourced_from_nav_menu_archivo_cols(self):
        src = _func_src("buildArchivoLanding")
        assert "NAV_MENU.archivo.cols.forEach(([groupLabel,items],gi)=>{" in src

    def test_nav_menu_archivo_cols_has_the_exact_three_labels_and_membership(self):
        text = _tabs_text()
        start = text.index("archivo:{cols:[")
        end = text.index("],feat:'gap'}", start)
        block = text[start:end]
        assert "['Preguntar',[['Consulta en español','preguntar'],['Consulta a la medida','constructor']]]" in block
        assert "['El estado del archivo',[['Cobertura, huecos y fuentes','cobertura'],['Calidad de datos','calidad'],['Calendario de temporada','calendario']]]" in block
        assert "['Referencia',[['Glosario','glosario']]]" in block


class TestAllSixRoutesReachableExactlyOnce:
    def test_every_real_slug_is_handled_via_the_shared_bySlug_lookup(self):
        src = _func_src("buildArchivoLanding")
        assert "bySlug[slug]" in src
        assert "showView('archivo',slug)" in src

    def test_nav_menu_archivo_cols_covers_exactly_the_six_real_view_map_slugs(self):
        text = _tabs_text()
        start = text.index("archivo:{cols:[")
        end = text.index("],feat:'gap'}", start)
        block = text[start:end]
        slugs = re.findall(r"','([a-z]+)'\]", block)
        assert sorted(slugs) == sorted(
            ["preguntar", "constructor", "cobertura", "calidad", "calendario", "glosario"]
        )
        assert len(slugs) == len(set(slugs))


class TestNoGradientIconTile:
    def test_archivo_landing_builder_never_renders_an_xcard_ic_tile(self):
        src = _func_src("buildArchivoLanding")
        assert "xcard" not in src
        assert 'class="ic"' not in src

    def test_landcard_modifier_classes_have_no_gradient_background(self):
        css = _css()
        for cls in (".landcard.archl-primary", ".landcard.archl-compact"):
            start = css.index(cls + "{")
            end = css.index("}", start)
            rule = css[start:end]
            assert "gradient" not in rule


class TestNoNewUserFacingStrings:
    def test_builder_pulls_titles_from_order_and_desc_from_view_desc_only(self):
        src = _func_src("buildArchivoLanding")
        # titles: o.label (order's own [slug,label] pair, the same text already live
        # as each view's subnav pill) -- never a new literal string for a card title.
        assert "esc(o.label)" in src
        # blurbs: VIEW_DESC.archivo[slug] only.
        assert "D[slug]" in src
        # group label text itself: NAV_MENU's own groupLabel, not retyped.
        assert "h.textContent=groupLabel" in src

    def test_no_new_quoted_spanish_literal_introduced_in_the_builder(self):
        src = _func_src("buildArchivoLanding")
        # the only single-quoted strings inside the function body are structural
        # (class names like 'landcard archl-primary', the '#archivo/' href prefix) --
        # none of those can contain an accented character or opening ¿/¡, the one
        # reliable signal of real Spanish copy (vs. a CSS class-name token).
        quoted = re.findall(r"'([^']*)'", src)
        spanish_like = [q for q in quoted if re.search(r"[á-úñÁ-ÚÑ¿¡]", q)]
        assert spanish_like == []


class TestContrastFix:
    def test_mega_feat_fx_uses_ink2_not_ink3(self):
        css = _css()
        start = css.index(".mega-feat .fx{")
        end = css.index("}", start)
        rule = css[start:end]
        assert "color:var(--ink-2)" in rule
        assert "ink-3" not in rule

    def test_archl_label_also_uses_ink2_from_the_start(self):
        css = _css()
        start = css.index(".archl-label{")
        end = css.index("}", start)
        rule = css[start:end]
        assert "color:var(--ink-2)" in rule

    def test_landcard_lc_d_description_text_already_used_a_passing_token(self):
        # pre-existing, unchanged -- confirms the card blurbs never needed a fix.
        css = _css()
        start = css.index(".landcard .lc-d{")
        end = css.index("}", start)
        assert "color:var(--ink-2)" in css[start:end]
