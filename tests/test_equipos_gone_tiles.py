"""PHASE_42 item A -- tileGone() (web/js/tabs.js), the Desaparecidas-only tile renderer.
tile()'s own name line is f.name.split(' de ')[0] -- the mascot word only, so "Gallitos
de la UPR" and "Gallitos de Isabela" both used to render as just "Gallitos", the one real
collision among the 21 defunct clubs. tileGone() adds a computed city + active-years line,
straight from F (web/js/data.js), nothing hardcoded per club. Ports the computation to
Python, the same convention test_route_slugs.py/test_nick_key.py already use."""

import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_JS = ROOT / "web/js/data.js"
TABS_JS = ROOT / "web/js/tabs.js"


def _franchises():
    """key -> {name, city, founded, end, active}, ported from F (web/js/data.js)."""
    text = DATA_JS.read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(
        r'(\w+):\{name:"([^"]+)"[^}]*?city:"([^"]+)"[^}]*?founded:(\d+),active:(\d)(?:,end:(\d+))?',
        text,
    ):
        key, name, city, founded, active, end = m.groups()
        out[key] = {
            "name": name,
            "city": city,
            "founded": int(founded),
            "active": active == "1",
            "end": int(end) if end else None,
        }
    return out


def _tile_gone_label(f):
    """Port of tileGone()'s own name + secondary-line computation."""
    short_name = f["name"].split(" de ")[0]
    bits = []
    if f["city"]:
        bits.append(f["city"])
    start, end = f["founded"], f["end"]
    yrs = ""
    if start is not None and end is not None:
        yrs = str(start) if start == end else f"{start}–{end}"
    elif start is not None:
        yrs = str(start)
    elif end is not None:
        yrs = str(end)
    if yrs:
        bits.append(yrs)
    return short_name, " · ".join(bits)


class TestAllDefunctTilesRender:
    def test_there_are_exactly_21_defunct_clubs(self):
        F = _franchises()
        defunct = [k for k, v in F.items() if not v["active"]]
        assert len(defunct) == 21

    def test_every_defunct_club_has_a_non_empty_secondary_line(self):
        F = _franchises()
        for k, f in F.items():
            if f["active"]:
                continue
            name, sub = _tile_gone_label(f)
            assert name
            assert sub, f"{k} ({f['name']}) got no secondary line at all"


class TestNoTwoGoneTilesCollide:
    def test_name_plus_secondary_line_is_unique_across_all_21(self):
        F = _franchises()
        labels = []
        for k, f in F.items():
            if f["active"]:
                continue
            labels.append((k, _tile_gone_label(f)))
        seen = {}
        collisions = []
        for k, label in labels:
            if label in seen:
                collisions.append((seen[label], k, label))
            seen[label] = k
        assert collisions == [], f"colliding tiles: {collisions}"

    def test_the_known_gallitos_pair_is_now_distinguished(self):
        F = _franchises()
        upr = _tile_gone_label(F["upr"])
        isa = _tile_gone_label(F["isa"])
        assert upr[0] == isa[0] == "Gallitos"
        assert upr[1] != isa[1]


class TestAppMatchesThisRule:
    def test_tile_gone_computes_from_f_not_hardcoded_strings(self):
        text = TABS_JS.read_text(encoding="utf-8")
        start = text.index("function tileGone(k){")
        end = text.index("\n}", start)
        src = text[start:end]
        assert "if(f.city) bits.push(esc(f.city));" in src
        assert "const start=f.founded, end=f.end;" in src
        assert "start+'–'+end" in src

    def test_tile_itself_is_unchanged_and_still_drives_activos(self):
        text = TABS_JS.read_text(encoding="utf-8")
        assert ".map(tile).join('')" in text  # Activos still uses the original tile()
        assert ".map(tileGone).join('')" in text  # Desaparecidas uses the new one
