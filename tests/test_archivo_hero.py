"""PHASE_49 -- Archivo's own hero (buildArchivoHero(), mirroring buildHistoriaHero/
buildJugadoresHero/buildEquiposHero/buildJuegaHero, called from finishBoot()) plus the
shared active-subnav-pill-into-view fix (syncSubnav(), web/js/tabs.js, used by all 5
VIEW_SECS sections). h1/lede are reused verbatim from the pre-existing static .phead
(web/index.html:444-448) -- no new Spanish strings, confirmed below. Source-level
checks, the same convention this session's other PHASE_4x test files use; the live
behavior (active pill fully visible at 390px on every Archivo view, no page overflow,
no console errors, no regression on Historia/Jugadores/Equipos/Juega) was verified
live this phase, see docs/session.md's PHASE_49 entry.

PHASE_49B -- the shared .hhero decorative-ring background (web/css/main.css) crossed
behind Archivo's own lede (and grazed the h1) at 1000-1280px, since Archivo's lede runs
close to the hero's full width with no eyebrow row to shorten the box. Fixed by scoping
an override to #archivo only (the other 4 hero sections still use the unmodified
shared .hhero background, confirmed unaffected live): the rings move to a ::before
layer with a px-based mask that hides them entirely below ~900px of hero width and
confines them to a clear strip on the right at 1280px. Verified live, Chromium, light+
dark, 1000/1280px -- no pixel of the ring pattern overlaps the h1/lede text box; mobile
(390px) is untouched (the ::before is display:none below 900px, same as it always was
pre-fix, since the base .hhero rule already drops background-image under 640px)."""

import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
TABS_JS = ROOT / "web/js/tabs.js"
INIT_JS = ROOT / "web/js/init.js"
INDEX_HTML = ROOT / "web/index.html"
MAIN_CSS = ROOT / "web/css/main.css"


def _tabs_text():
    return TABS_JS.read_text(encoding="utf-8")


class TestBuildArchivoHeroExists:
    def test_function_is_defined(self):
        text = _tabs_text()
        assert "function buildArchivoHero(){" in text

    def test_targets_the_real_archivo_phead(self):
        text = _tabs_text()
        start = text.index("function buildArchivoHero(){")
        end = text.index("\n}", start)
        src = text[start:end]
        assert "document.querySelector('#archivo .phead')" in src
        assert "head.classList.add('hhero')" in src

    def test_is_called_from_finish_boot(self):
        text = INIT_JS.read_text(encoding="utf-8")
        assert "buildArchivoHero();" in text
        # wrapped in its own try/catch, same convention as the other 4 heroes
        assert "try{ buildArchivoHero(); }catch(e){" in text


class TestNoNewSpanishStrings:
    """The task's own explicit instruction: reuse the existing h1/lede verbatim, no
    new copy, no eyebrow (an eyebrow was considered and deliberately omitted -- see
    the explanatory comment directly above buildArchivoHero() in tabs.js)."""

    def test_h1_matches_the_original_static_markup_verbatim(self):
        text = _tabs_text()
        start = text.index("function buildArchivoHero(){")
        end = text.index("\n}", start)
        src = text[start:end]
        assert "<h1>El archivo</h1>" in src

    def test_lede_matches_the_original_static_markup_verbatim(self):
        text = _tabs_text()
        start = text.index("function buildArchivoHero(){")
        end = text.index("\n}", start)
        src = text[start:end]
        original_lede = (
            "Pregúntale directamente, o mira qué tiene, qué le falta y de dónde "
            "sale cada dato. Un archivo que esconde sus huecos vale menos que uno "
            "que los enseña."
        )
        assert original_lede in src

    def test_no_eyebrow_div_added_for_archivo(self):
        text = _tabs_text()
        start = text.index("function buildArchivoHero(){")
        end = text.index("\n}", start)
        src = text[start:end]
        assert "eyebrow" not in src


class TestPheadNoLongerBareForArchivo:
    def test_static_phead_still_present_as_the_hero_rewrite_target(self):
        # buildArchivoHero() rewrites #archivo .phead's innerHTML at boot -- the
        # static markup itself doesn't need editing (same precedent as the other 4
        # sections), but it must still exist as the thing the hero builder targets.
        text = INDEX_HTML.read_text(encoding="utf-8")
        assert 'id="archivo"' in text
        assert '<div class="phead">' in text

    def test_phead_gains_hhero_class_only_via_the_builder_not_hardcoded_in_html(self):
        # the static HTML's own .phead has no hhero class baked in -- it's added at
        # runtime by classList.add('hhero'), same mechanism as every other section.
        text = INDEX_HTML.read_text(encoding="utf-8")
        start = text.index('id="archivo"')
        phead_start = text.index('<div class="phead">', start)
        phead_end = text.index(">", phead_start)
        assert "hhero" not in text[phead_start:phead_end]


class TestActiveSubnavPillScrollsIntoView:
    """syncSubnav() (tabs.js) is the single shared implementation used by all 5
    VIEW_SECS sections (historia/jugadores/equipos/juega/archivo) -- the fix lives
    here once, generically, not duplicated per section."""

    @staticmethod
    def _sync_subnav_src():
        text = _tabs_text()
        start = text.index("function syncSubnav(sec,view){")
        end = text.index("\n}", start)
        src = text[start:end]
        return re.sub(r"/\*.*?\*/", "", src, flags=re.S)

    def test_scroll_left_is_computed_not_scroll_into_view(self):
        src = self._sync_subnav_src()
        # the comment explaining the decision mentions it by name -- strip comments
        # first (done in _sync_subnav_src) so only real CODE usage is asserted here
        assert "scrollIntoView" not in src
        assert "nav.scrollTo(" in src
        assert "scrollLeft" in src or "left:target" in src

    def test_respects_reduced_motion(self):
        src = self._sync_subnav_src()
        assert "prefers-reduced-motion" in src
        assert "reduced?'auto':'smooth'" in src

    def test_fix_is_scoped_to_the_shared_subnav_element_not_the_whole_page(self):
        src = self._sync_subnav_src()
        assert "nav.clientWidth" in src
        assert "nav.scrollWidth" in src

    def test_is_shared_across_all_five_view_secs(self):
        text = _tabs_text()
        assert "const VIEW_SECS=['historia','jugadores','equipos','juega','archivo'];" in text
        # only one syncSubnav definition exists -- the fix applies to every section
        assert text.count("function syncSubnav(sec,view){") == 1


class TestNoUnintendedNewDeclarations:
    def test_only_build_archivo_hero_is_new_at_top_level(self):
        import json

        baseline = json.loads(
            (ROOT / "tests/harness/inventory_main_HEAD.json").read_text(encoding="utf-8")
        )
        names = [d["name"] for d in baseline["declarations"] if d["file"] == "web/js/tabs.js"]
        assert names.count("buildArchivoHero") == 1


class TestArchivoHeroArcsConfined:
    """PHASE_49B -- the shared ring background is scoped off for #archivo and replaced
    with a masked ::before layer so it never paints behind the h1/lede text column."""

    @staticmethod
    def _css():
        return MAIN_CSS.read_text(encoding="utf-8")

    def test_archivo_disables_the_shared_full_width_background(self):
        css = self._css()
        assert "#archivo .hhero{background-image:none}" in css

    def test_archivo_gets_its_own_masked_ring_layer(self):
        css = self._css()
        start = css.index("#archivo .hhero::before{")
        end = css.index("}", css.index("mask-image", start)) + 1
        rule = css[start:end]
        assert "repeating-radial-gradient(circle at 100% 0%" in rule
        assert "mask-image:linear-gradient(to right" in rule
        assert "-webkit-mask-image:linear-gradient(to right" in rule

    def test_ring_layer_sits_behind_the_text_not_on_top(self):
        css = self._css()
        start = css.index("#archivo .hhero::before{")
        end = css.index("}", start)
        rule = css[start:end]
        assert "z-index:-1" in rule
        assert "position:absolute" in rule

    def test_ring_layer_is_off_on_mobile_same_as_before_the_fix(self):
        css = self._css()
        assert "@media(max-width:899px){#archivo .hhero::before{display:none}}" in css

    def test_other_hero_sections_keep_the_unscoped_shared_background(self):
        # the base .hhero rule (used by Historia/Jugadores/Equipos/Juega) must be
        # untouched -- only an #archivo-scoped override was added, nothing shared
        # was edited, so the other 4 sections render exactly as before this phase.
        css = self._css()
        assert (
            ".hhero{background-image:repeating-radial-gradient(circle at 100% 0%,"
            "transparent 0 63px,var(--line) 63px 64.5px)}"
        ) in css
