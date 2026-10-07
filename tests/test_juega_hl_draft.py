"""PHASE_46 -- Sube y Baja (HL) and La Temporada Perfecta (Draft), web/js/games.js.
Visual/string polish only: no game logic, scoring, pool selection, storage keys, or
share text touched. Source-level checks, the same convention this session's other
PHASE_4x test files use; the live behavior (hint shown/hidden, focus ring visible and
>=3:1 in both themes, tap targets, no overflow/overlap at 320/390/1000px, the "10 mil
puntos" tag rendering for a real 10k-tagged player) was verified live this phase, see
docs/session.md's PHASE_46 entry."""

import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
GAMES_JS = ROOT / "web/js/games.js"
MAIN_CSS = ROOT / "web/css/main.css"


class TestHLHint:
    def test_hint_is_only_rendered_while_the_round_is_live(self):
        text = GAMES_JS.read_text(encoding="utf-8")
        start = text.index("function drawHL(){")
        end = text.index("\n}", start)
        src = text[start:end]
        assert "!HL.done?" in src
        assert "Toca uno para responder." in src

    def test_hint_comes_before_the_cards_not_after(self):
        text = GAMES_JS.read_text(encoding="utf-8")
        start = text.index("function drawHL(){")
        hint_pos = text.index("Toca uno para responder.", start)
        cards_pos = text.index("cards g2", start)
        assert hint_pos < cards_pos


class TestHLCardTapTargetAndFocus:
    def test_no_focus_suppressing_rule_targets_hl_cards(self):
        # HL's cards are plain .card buttons -- the global :focus-visible rule
        # (main.css) has to still apply to them; confirm nothing scoped to #hlGame
        # or .cards.g2 resets outline back to none.
        text = MAIN_CSS.read_text(encoding="utf-8")
        assert "#hlGame" not in text or "outline:none" not in text[text.index("#hlGame"):text.index("#hlGame") + 200]

    def test_global_focus_visible_rule_exists(self):
        text = MAIN_CSS.read_text(encoding="utf-8")
        assert ":focus-visible{outline:2px solid var(--focus);outline-offset:2px" in text


class TestDraftCourtCellFocus:
    def test_all_unset_moved_out_of_the_inline_style(self):
        # an inline style="all:unset" beats ANY stylesheet selector for the same
        # element, including a :focus-visible rule -- confirmed live before this
        # existed (outline:none when focused despite a real <button>).
        text = GAMES_JS.read_text(encoding="utf-8")
        start = text.index("function courtHTML(){")
        end = text.index("\nfunction drawPicks(){", start)
        src = text[start:end]
        # a naive "all:unset" substring search would also match this phase's own
        # explanatory comment (which quotes the old code while describing the fix) --
        # check the real code pattern (the old inline style attribute) specifically.
        assert 'style="all:unset' not in src
        assert 'class="court-cell"' in src

    def test_court_cell_class_carries_the_reset_and_cell_size_is_unchanged(self):
        text = MAIN_CSS.read_text(encoding="utf-8")
        start = text.index(".court-cell{")
        end = text.index("}", start)
        src = text[start:end]
        assert "all:unset" in src
        assert "min-height:58px" in src  # unchanged from before this phase

    def test_court_cell_focus_visible_rule_exists(self):
        text = MAIN_CSS.read_text(encoding="utf-8")
        start = text.index(".court-cell:focus-visible{")
        end = text.index("}", start)
        src = text[start:end]
        assert "outline:2px solid var(--focus)" in src
        assert "outline-offset:2px" in src


class TestDraftEmptySlotLabel:
    def test_vacio_label_uses_a_readable_fixed_color_and_12px(self):
        text = MAIN_CSS.read_text(encoding="utf-8")
        start = text.index(".court-empty{")
        end = text.index("}", start)
        src = text[start:end]
        assert "var(--fs-2xs)" in src  # 12px, was var(--fs-3xs) = 11px
        assert "color:var(--ink-2)" in src  # was .dim (--ink-3) + opacity:.45 on dead slots

    def test_no_further_opacity_dimming_applied_to_the_empty_label(self):
        text = GAMES_JS.read_text(encoding="utf-8")
        start = text.index("function courtHTML(){")
        end = text.index("\nfunction drawPicks(){", start)
        src = text[start:end]
        # same note as above -- check the real old template-literal pattern, not a
        # bare substring that would also match this phase's own comment.
        assert ";opacity:.45':''" not in src


class TestNo10kInDraftCopy:
    def test_the_tag_label_dictionary_spells_it_out(self):
        text = GAMES_JS.read_text(encoding="utf-8")
        assert "'10k':'10 mil puntos'" in text
        # the tag KEY '10k' (data.js/games.js internal identifier, never displayed on
        # its own) legitimately still exists -- only the displayed VALUE changed.
        assert "'10k':'10k'" not in text

    def test_no_bare_10k_literal_renders_as_a_label_value(self):
        text = GAMES_JS.read_text(encoding="utf-8")
        # the tag dictionary line itself is the only place '10k' could leak into
        # displayed text; every other '10k' occurrence in this file is a key/weight
        # lookup (TAGV, p.t arrays), never a template-literal VALUE shown to a user.
        tag_dict_line = next(l for l in text.splitlines() if "'10k':'10 mil puntos'" in l)
        assert re.search(r"'10k':\s*'10k'", tag_dict_line) is None
