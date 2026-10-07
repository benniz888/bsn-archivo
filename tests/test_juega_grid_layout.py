"""PHASE_45 -- La Cuadrícula (games.js drawBoard()) layout fixes: mobile overflow,
header text wrapping, crestPlate() on the grid's crest() calls, and the Diaria/Práctica
toggle's tap-target size. Ports the real contrastRatio()/crestPlate() math to Python
(same convention test_owners_retired.py already uses for Equipos) rather than driving a
browser for the 33-franchise check; the live layout (no overflow 320-414px, no mid-word
breaks, the game still playing) was verified live this phase, see docs/session.md's
PHASE_45 entry."""

import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_JS = ROOT / "web/js/data.js"
TABS_JS = ROOT / "web/js/tabs.js"
GAMES_JS = ROOT / "web/js/games.js"
MAIN_CSS = ROOT / "web/css/main.css"


def _franchises():
    """key -> {c1, c2}, ported from F (web/js/data.js)."""
    text = DATA_JS.read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r'(\w+):\{name:"[^"]+"[^}]*?c1:"(#[0-9A-Fa-f]{6})",c2:"(#[0-9A-Fa-f]{6})"', text):
        out[m.group(1)] = {"c1": m.group(2), "c2": m.group(3)}
    return out


def _rel_lum(rgb):
    """Port of relLum() in web/js/tabs.js."""
    def f(v):
        v = v / 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(rgb[0]) + 0.7152 * f(rgb[1]) + 0.0722 * f(rgb[2])


def _hex_rgb(hexstr):
    h = hexstr.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _contrast_ratio(hex_a, hex_b):
    """Port of contrastRatio() in web/js/tabs.js."""
    l1, l2 = _rel_lum(_hex_rgb(hex_a)), _rel_lum(_hex_rgb(hex_b))
    hi, lo = (l1, l2) if l1 > l2 else (l2, l1)
    return (hi + 0.05) / (lo + 0.05)


def _crest_plate(c2):
    """Port of crestPlate()'s own color pick (tabs.js, PHASE_41B): tries a softened
    near-black/off-white tone first (#0B1020/#F4F6FA), on whichever side the pure
    black/white check picked, falling back to the actual pure color only if softening
    itself would drop that club's own c2 under 3:1."""
    pure = "#000000" if _contrast_ratio(c2, "#000000") >= _contrast_ratio(c2, "#FFFFFF") else "#FFFFFF"
    soft = "#0B1020" if pure == "#000000" else "#F4F6FA"
    return soft if _contrast_ratio(c2, soft) >= 3 else pure


class TestGridCrestsUseCrestPlate:
    def test_both_crest_call_sites_are_wrapped_in_crest_plate(self):
        text = GAMES_JS.read_text(encoding="utf-8")
        start = text.index("const gHead=(ax,rowCls)=>{")
        end = text.index("\n  };", start)
        src = text[start:end]
        assert "crest-plate" in src
        assert "crestPlate(ax.k)" in src

    def test_crest_crestsvg_crestplate_functions_themselves_are_untouched(self):
        # crestPlate() still returns a single hex, same PHASE_41B body -- Grid gets a
        # smaller PLATE via CSS, not a changed function.
        text = TABS_JS.read_text(encoding="utf-8")
        start = text.index("function crestPlate(k){")
        end = text.index("\n}", start)
        src = text[start:end]
        assert "function crestPlate(k)" in src
        assert "return contrastRatio(f.c2,soft)>=3?soft:pure;" in src


class TestAllFranchisesClear3to1AgainstTheirPlate:
    def test_every_real_franchise_passes(self):
        F = _franchises()
        assert len(F) == 33
        failures = []
        for k, f in F.items():
            plate = _crest_plate(f["c2"])
            ratio = _contrast_ratio(f["c2"], plate)
            if ratio < 3:
                failures.append((k, ratio))
        assert failures == [], f"clubs failing 3:1: {failures}"

    def test_worst_case_matches_the_known_equipos_floor(self):
        # crestPlate()'s own color math is unchanged by this phase (only the CSS plate
        # SIZE differs for Grid) -- the worst real ratio across all 33 franchises should
        # be the same value PHASE_41B already found for Equipos' 12 active clubs, since
        # Mayagüez (the worst case there) is active and therefore in this 33-club set too.
        F = _franchises()
        worst = min(_contrast_ratio(f["c2"], _crest_plate(f["c2"])) for f in F.values())
        assert abs(worst - 4.34) < 0.01


class TestHeaderTextNeverBreaksMidWord:
    def test_overflow_wrap_anywhere_is_gone(self):
        text = MAIN_CSS.read_text(encoding="utf-8")
        start = text.index(".ghead{")
        end = text.index("}", start)
        assert "overflow-wrap:anywhere" not in text[start:end]

    def test_glabel_uses_a_line_clamp_with_normal_word_wrapping(self):
        text = MAIN_CSS.read_text(encoding="utf-8")
        start = text.index(".ghead .glabel{")
        end = text.index("}", start)
        src = text[start:end]
        assert "-webkit-line-clamp:2" in src
        assert "overflow-wrap:normal" in src
        assert "word-break:normal" in src
        assert "text-overflow:ellipsis" in src

    def test_every_ghead_gets_a_title_with_the_full_name(self):
        text = GAMES_JS.read_text(encoding="utf-8")
        assert 'title="${esc(axFull(ax))}"' in text


class TestGridFitsNarrowViewports:
    def test_mobile_breakpoint_lowers_the_column_floor_and_header_width(self):
        # PHASE_45B: 56px (PHASE_45's own first pass) truncated every club name to ~6
        # characters -- widened to 84px, found live this still clears the 44px cell
        # floor at 320/360/390/414px (checked via real getBoundingClientRect(), not
        # assumed -- see docs/session.md's PHASE_45B entry).
        text = MAIN_CSS.read_text(encoding="utf-8")
        start = text.index("@media(max-width:639px){\n  .gridtable{")
        end = text.index("\n}", start)
        src = text[start:end]
        assert "grid-template-columns:84px repeat(3,minmax(44px,1fr))" in src
        assert "min-width:0" in src

    def test_desktop_gridtable_header_is_widened_to_fit_full_club_names(self):
        # PHASE_45B: 92px truncated every row header ("Cari…", "Atlét…", "Criol…", even
        # "Can…" for Cangrejeros) despite desktop having plenty of real room -- widened
        # to 132px; min-width bumped from 410 to 420 to match the real new natural
        # minimum (132 + 90*3 + 5*3 = 417). max-width:540px (the board's own overall
        # size cap) is unchanged.
        text = MAIN_CSS.read_text(encoding="utf-8")
        assert "grid-template-columns:132px repeat(3,minmax(90px,1fr));gap:5px;\n  min-width:420px;max-width:540px" in text


class TestRowAndColumnHeadersShareOneLayout:
    """PHASE_45B: the task's own instruction ("crest above the label, centered...
    not top-left with the label at bottom-right") removed PHASE_45's row-vs-column
    split entirely -- .ghead.row no longer carries its own flex-direction/alignment
    rules at any width; every header (row or column) uses the same stacked, centered
    layout .ghead itself already defines."""

    def test_ghead_row_no_longer_overrides_flex_direction(self):
        text = MAIN_CSS.read_text(encoding="utf-8")
        assert ".ghead.row{flex-direction:row" not in text
        assert ".ghead.row{flex-direction:column" not in text

    def test_crest_plate_is_recentered_inside_ghead(self):
        # the base .crest-plate (tabs.js-adjacent CSS, PHASE_41B) carries
        # align-self:flex-start for Equipos' own card layout -- without an override
        # here, that same align-self leaks into Grid's .ghead and pins the plate to
        # the header's left edge instead of letting .ghead's own align-items:center
        # apply. Found live (a real bug, not assumed) before this existed.
        text = MAIN_CSS.read_text(encoding="utf-8")
        start = text.index(".ghead .crest-plate{")
        end = text.index("}", start)
        assert "align-self:center" in text[start:end]


class TestModeToggleTapTarget:
    def test_min_height_is_at_least_44px(self):
        text = MAIN_CSS.read_text(encoding="utf-8")
        start = text.index(".gamehead .modebtns button{")
        end = text.index("}", start)
        src = text[start:end]
        m = re.search(r"min-height:(\d+)px", src)
        assert m and int(m.group(1)) >= 44
        m2 = re.search(r"min-width:(\d+)px", src)
        assert m2 and int(m2.group(1)) >= 44

    def test_the_fix_is_scoped_to_grid_not_the_shared_modebtns_class(self):
        # .modebtns is reused by the theme/profile pickers (tabs.js) -- a bare
        # ".modebtns button" rule would have resized those too; confirmed this phase
        # that only the .gamehead-scoped rule carries the size change.
        text = MAIN_CSS.read_text(encoding="utf-8")
        bare_rule = re.search(r"\n\.modebtns button\{([^}]*)\}", text)
        assert bare_rule and "min-height" not in bare_rule.group(1)
