"""PHASE_44 -- Juega's own hero (buildJuegaHero(), web/js/tabs.js) and landing fixes
(drawStreak(), web/js/games.js; the stagebar generated once in buildJuegaViews() instead
of 4 static copies in web/index.html). Source-level checks, the same convention this
session's other PHASE_4x test files use, rather than driving a browser -- the live
behavior (clean context: strip hidden; seeded context: strip shown with the heading;
back button/Escape both still close the active game) was verified live this phase, see
docs/session.md's PHASE_44 entry."""

from pathlib import Path

ROOT = Path(__file__).parent.parent
TABS_JS = ROOT / "web/js/tabs.js"
GAMES_JS = ROOT / "web/js/games.js"
INDEX_HTML = ROOT / "web/index.html"


class TestJuegaHeroLedeIsComputed:
    def test_the_count_word_comes_from_games_length_not_a_literal(self):
        text = TABS_JS.read_text(encoding="utf-8")
        start = text.index("function buildJuegaHero(){")
        end = text.index("\n}", start)
        src = text[start:end]
        assert "const wn=numWordsEs(GAMES.length);" in src
        assert "wn[0].toUpperCase()+wn.slice(1)" in src
        # the literal count word itself must never appear hardcoded in this function
        assert "Cuatro" not in src

    def test_the_hero_is_wired_into_boot_like_the_other_three(self):
        text = (ROOT / "web/js/init.js").read_text(encoding="utf-8")
        assert "buildJuegaHero();" in text


class TestStreakStripHiddenUntilPlayed:
    def test_draw_streak_early_returns_empty_when_played_is_zero(self):
        text = GAMES_JS.read_text(encoding="utf-8")
        start = text.index("function drawStreak(){")
        end = text.index("\n}", start)
        src = text[start:end]
        assert "if(!st.played){ host.innerHTML=''; return; }" in src

    def test_draw_streak_shows_the_grid_specific_heading_when_shown(self):
        text = GAMES_JS.read_text(encoding="utf-8")
        start = text.index("function drawStreak(){")
        end = text.index("\n}", start)
        src = text[start:end]
        assert '<h4 class="sub">Tu racha en La Cuadrícula</h4>' in src

    def test_storage_note_is_independent_of_the_strip(self):
        text = GAMES_JS.read_text(encoding="utf-8")
        # drawStorageNote() still only checks ST.wrote, never the streak object
        start = text.index("function drawStorageNote(){")
        end = text.index("\n}", start)
        src = text[start:end]
        assert "ST.wrote" in src
        assert "streak" not in src


class TestBackButtonGeneratedOnce:
    def test_the_button_markup_appears_exactly_once_in_tabs_js(self):
        # text.count() alone would also match this file's own PHASE_44 comment, which
        # quotes the label while explaining the change -- counting the real button
        # markup (not just the bare label string) is the actual thing to guard.
        text = TABS_JS.read_text(encoding="utf-8")
        assert text.count('onclick="closeGame()">‹ Juegos</button>') == 1

    def test_no_stage_in_index_html_has_its_own_static_stagebar(self):
        text = INDEX_HTML.read_text(encoding="utf-8")
        assert "stagebar" not in text
        assert "‹ Juegos" not in text

    def test_build_juega_views_generates_one_stagebar_per_stage(self):
        text = TABS_JS.read_text(encoding="utf-8")
        start = text.index("function buildJuegaViews(panel){")
        end = text.index("\nfunction buildViews(){", start)
        src = text[start:end]
        assert "const bar=el('div','stagebar');" in src
        assert "onclick=\"closeGame()\">‹ Juegos</button>" in src
        assert "s.insertBefore(bar,s.firstChild);" in src
