"""PHASE_65 fixup -- every explore card on a page has its own icon (static check, no browser).
The rendered check (icons actually in the DOM, gap, columns, no empty slot) is in test_player_ring_overlap.py."""
import re
from pathlib import Path

TABS = (Path(__file__).resolve().parent.parent / "web/js/tabs.js").read_text(encoding="utf-8")


def _icons(name):
    body = TABS[TABS.index(f"const {name}={{"):]
    body = body[:body.index("};")]
    return dict(re.findall(r"(\w+):'([^']+)'", body))


def test_historia_cards_do_not_share_an_icon():
    icons = _icons("HISTORIA_XICON")
    assert set(icons) == {"cinta", "titulos", "dinastias", "finales", "premios", "refuerzos", "temporadas"}
    assert len(set(icons.values())) == len(icons)


def test_jugadores_cards_do_not_share_an_icon():
    icons = _icons("JUGADORES_XICON")
    assert set(icons) == {"buscar", "comparar", "lideres", "records", "salon", "nba", "dirigentes", "canchas"}
    assert len(set(icons.values())) == len(icons)
