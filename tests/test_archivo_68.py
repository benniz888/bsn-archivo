"""PHASE_68 -- Archivo/Historia/Jugadores fixes: counts read from data, A01 claim, tap targets, scroll cue,
links on existing hash routes. Static checks only; the live behavior is verified in Chromium and WebKit separately."""

import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
TABS = (ROOT / "web/js/tabs.js").read_text(encoding="utf-8")
CSS = (ROOT / "web/css/main.css").read_text(encoding="utf-8")
HTML = (ROOT / "web/index.html").read_text(encoding="utf-8")
SHIPPED_JS = "".join((ROOT / "web/js" / n).read_text(encoding="utf-8") for n in ("tabs.js", "init.js", "helpers.js", "player.js", "data-quality.js"))


def _strip_comments(src):
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    return re.sub(r"(?m)^\s*//.*$", "", src)


CODE = _strip_comments(TABS)


class TestCountsFromData:
    def test_no_hardcoded_97_seasons_in_shipped_js_or_html(self):
        assert not re.search(r"\b97 temporadas", _strip_comments(SHIPPED_JS) + HTML)

    def test_qb_labels_have_no_fixed_counts(self):
        assert "Franquicias (32)" not in CODE
        assert "39 recuperados" not in CODE and "(39" not in CODE
        assert "Líderes de carrera (30)" not in CODE and "Récords de la liga (11)" not in CODE
        assert "get label(){ return 'Franquicias ('+FKEYS.length+')'; }" in CODE
        assert "MVP_YEARS.length+' recuperados)'" in CODE

    def test_historia_header_is_filled_from_years(self):
        assert 'id="histCount"' in HTML and 'id="titleLede"' in HTML
        assert "YEARS.length+' temporadas'" in CODE

    def test_dynasty_note_has_no_fixed_club_or_years(self):
        assert "Bayamón 2025–26 es la primera desde Ponce" not in CODE
        assert "Bayamón lleva la delantera" not in HTML

    def test_sources_card_range_and_retired_counts_derived(self):
        assert "Campeones 1930–2025" not in CODE
        assert "Bayamón (8) y Guaynabo (3)" not in CODE


class TestA01Claim:
    def test_no_2011_wall_claim_remains(self):
        for needle in ("Antes de 2011", "anterior a 2011", "el muro real"):
            assert needle not in CODE, needle

    def test_landing_claim_comes_from_manifest(self):
        i = CODE.index("if(k==='gap')")
        block = CODE[i:i + 900]
        assert "MANIFEST.counts.seasons_with_leaders" in block and "2011" not in block

    def test_player_warning_comes_from_manifest(self):
        assert "'Este archivo tiene líderes por temporada en '+MANIFEST.counts.seasons_with_leaders" in CODE


class TestTapTargets:
    def _rule(self, selector_start):
        m = re.search(r"(?m)^" + re.escape(selector_start) + r"[^{]*\{([^}]*)\}", CSS)
        assert m, selector_start
        return m.group(1)

    def test_controls_chips_buttons_have_44px_min(self):
        tail = CSS[CSS.index("PHASE_68 (redesign-v3): tap targets"):]
        assert "input[type=search],input[type=text],select,textarea{min-height:44px}" in tail
        assert ".chip,.btn,.subtab button{min-height:44px}" in tail
        assert ".thbtn{min-width:44px}" in tail

    def test_existing_44px_rules_kept(self):
        assert "min-height:44px" in self._rule(".thbtn")
        assert "min-height:44px" in self._rule(".cellbtn")
        assert ".cell{min-height:44px" in CSS

    def test_ribbon_cells_fit_44px_at_desktop(self):
        m = re.search(r"\.ribbon\{display:grid;grid-template-columns:repeat\(20,1fr\);gap:4px;min-width:(\d+)px", CSS)
        assert m and int(m.group(1)) >= 20 * 44 + 19 * 4


class TestScrollCue:
    def test_shared_helper_exists_as_property_not_top_level_name(self):
        assert "buildTable.cue=function(wrap)" in CODE
        assert not re.search(r"(?m)^(function|const|let|var)\s+(cue|tableCue)\b", CODE)

    def test_cue_wraps_container_and_toggles_more_r(self):
        i = CODE.index("buildTable.cue=function")
        body = CODE[i:i + 1400]
        assert "'tblbox'" in body and "more-r" in body and "ResizeObserver" in body

    def test_cue_applied_to_hand_built_scrollers(self):
        assert CODE.count("buildTable.cue") >= 6

    def test_cue_css_fade_and_chevron(self):
        assert ".tblbox.more-r::after" in CSS and ".tblbox.more-r::before" in CSS
        assert "overflow:auto" in CSS[CSS.index(".tblwrap{position:relative"):][:200]


class TestLinksUseExistingRoutes:
    def test_season_table_and_lists_link_to_hash_routes(self):
        assert 'href="#historia/temporada/${v}"' in CODE
        assert 'href="#equipos/equipo/${k}"' in CODE
        assert 'href="#jugadores/jugador/${playerSlug(pl.name)}"' in CODE

    def test_no_new_route_names(self):
        for m in re.finditer(r'href="#([a-z]+)/([a-z]+)', CODE):
            assert (m.group(1), m.group(2)) in {
                ("historia", "temporada"), ("equipos", "equipo"), ("jugadores", "jugador"), ("archivo", "calidad"),
                ("archivo", "preguntar"), ("jugadores", "comparar"),
            }, m.group(0)


class TestAskDeepLink:
    def test_applyhash_branch_reuses_router(self):
        assert "if(a==='archivo' && b==='preguntar' && c)" in CODE
        assert "setHash('archivo/preguntar'" in CODE


class TestContrastFixes:
    def _lum(self, h):
        h = h.lstrip("#")
        c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        a = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
        return 0.2126 * a[0] + 0.7152 * a[1] + 0.0722 * a[2]

    def _cr(self, a, b):
        x, y = self._lum(a), self._lum(b)
        return (max(x, y) + 0.05) / (min(x, y) + 0.05)

    def test_bronze_badge_clears_4_5_at_both_gradient_stops(self):
        m = re.search(r"\.bar-row\.rk3 \.rk\{background:linear-gradient\(135deg,(#\w{6}),(#\w{6})\);color:(#\w{6})\}", CSS)
        assert m
        for stop in m.group(1, 2):
            assert self._cr(m.group(3), stop) >= 4.5, stop

    def test_finals_matrix_dark_red_cells_use_deep_red(self):
        assert ':root:not([data-theme="light"]) .matrix td.cellv.hi{background:var(--rojo-deep)}' in CSS
        assert self._cr("#ffffff", "#8E1119") >= 4.5


class TestStringsApproved:
    def test_no_draft_markers_and_s7_final(self):
        assert "DRAFT wording" not in TABS
        assert "'Campeones de la década de '+d" in TABS
