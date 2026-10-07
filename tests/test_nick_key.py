"""PHASE_36 -- nickKey(), the nickname-aware merge key buildPlayerIndex() (web/js/player.js) uses
instead of plain norm() for its own Map key only. norm()/slug() strip the «»""'' PUNCTUATION a
quoted nickname sits in, never the nickname WORD itself, so "Mario «Quijote» Morales" and "Mario
Morales" used to land on two different PINDEX cards for the same real person (PHASE_35 survey:
exactly two such pairs existed, Mario Morales and Federico "Fico" López). Port of nickKey()/
stripNick() to Python, the same way test_route_slugs.py ports slug(), so the rule can be checked
without a browser; the real merge (PINDEX size, Buscar/Comparar/Salón/player-page surfaces) is
checked live -- see docs/session.md's PHASE_36 entry."""

import re
import unicodedata

from tests._web_text import web_text


def strip_nick(s):
    """Port of stripNick() in web/js/helpers.js."""
    s = re.sub(r"«[^»]*»|\"[^\"]*\"|'[^']*'", " ", str(s))
    return re.sub(r"\s+", " ", s).strip()


def norm(s):
    """Port of norm() in web/js/helpers.js (same as test_route_slugs.py's own slug()-adjacent use,
    reproduced here rather than imported so this file has no cross-test-module dependency)."""
    s = unicodedata.normalize("NFD", str(s).lower())
    s = re.sub(r"[̀-ͯ]", "", s)
    s = re.sub(r"[«»\"'.]", "", s)
    return s.strip()


def nick_key(s):
    """Port of nickKey() in web/js/helpers.js."""
    return norm(strip_nick(s))


class TestNickKeyMergesExactlyThePhase35Pairs:
    def test_mario_morales_merges_with_the_nickname_form(self):
        assert nick_key("Mario Morales") == nick_key("Mario «Quijote» Morales") == "mario morales"

    def test_federico_lopez_merges_with_the_nickname_form(self):
        assert nick_key("Federico López") == nick_key('Federico "Fico" López') == "federico lopez"
        # the real app uses guillemets for this one too (data.js); straight quotes are also
        # accepted since stripNick() matches either -- both forms must merge.
        assert nick_key("Federico López") == nick_key("Federico «Fico» López")

    def test_anza_froilan_jr_does_not_merge(self):
        # PHASE_35 signal (b): a Jr./Sr. suffix is evidence of two different real people
        # (father/son), not a duplicate -- nickKey() must never fold it away. Confirmed this is
        # the one real PALL pair the suffix signal found; it must stay two distinct keys.
        assert nick_key("Anza, Froilan") != nick_key("Anza, Froilan jr.")

    def test_a_plain_name_with_no_quoted_segment_is_unchanged_by_stripping(self):
        # the overwhelming majority of names: nickKey() must behave identically to norm() when
        # there is nothing to strip, so every other PINDEX entry is completely unaffected.
        for name in ("Georgie Torres", "Raymond Dalmau", "A.D. Vassallo", "Juan Pérez"):
            assert nick_key(name) == norm(name)

    def test_the_python_port_matches_the_real_app_source(self):
        text = web_text()
        assert "const stripNick=s=>String(s).replace(/«[^»]*»|\"[^\"]*\"|'[^']*'/g,' ').replace(/\\s+/g,' ').trim();" in text
        assert "const nickKey=s=>norm(stripNick(s));" in text
