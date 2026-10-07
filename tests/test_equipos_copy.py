"""PHASE_40/40B -- Equipos' own landing copy (web/js/tabs.js buildEquiposHero()/
buildEquiposLanding(), web/index.html's static .phead fallback). Two things checked here
without a browser: (a) the PHASE_39-flagged "veinte" bug and PHASE_40B's "completo" trim
never reappear in Equipos' own copy; (b) the #3 stat's gap clause (" -- falta el de
{year}" / " -- faltan {n}") is driven by the SAME source the stat's own number is --
F's own won:[...] arrays in web/js/data.js, the static data champOf (web/index.html) is
built from -- not a second, independently-typed year or count that could drift from it.
The live app also runs hydrate()'s franchises.json overlay (init.js), which only ever
UNIONS more won-years in, never removes any baked-in ones -- confirmed live, PHASE_40B --
so this static-only port is a lower bound on championed years, never an overcount."""

import re

from tests._web_text import web_text

DATA_JS = __import__("pathlib").Path(__file__).parent.parent / "web/js/data.js"
TABS_JS = __import__("pathlib").Path(__file__).parent.parent / "web/js/tabs.js"


def _static_champ_years():
    """Port of deriveChampions()'s champOf build (web/index.html), reading F's own
    won:[...] literals directly out of web/js/data.js -- not a separate recomputation."""
    text = DATA_JS.read_text(encoding="utf-8")
    years = set()
    for m in re.finditer(r"won:\[([^\]]*)\]", text):
        years.update(int(y) for y in m.group(1).split(",") if y.strip())
    return years


def _missing_years():
    years_range = range(1930, 2027)  # YEARS=[];for(let y=1930;y<=2026;y++) -- web/index.html
    champ = _static_champ_years()
    return [y for y in years_range if y not in champ]


class TestEquiposStat3GapClause:
    def test_missing_years_are_exactly_1953(self):
        assert _missing_years() == [1953]

    def test_the_app_builds_the_gap_clause_from_the_same_champof_source(self):
        text = TABS_JS.read_text(encoding="utf-8")
        assert "const titlesN=Object.keys(champOf).length;" in text
        assert "const missingYears=YEARS.filter(y=>!(y in champOf));" in text
        assert "' — falta el de '+missingYears[0]" in text
        assert "' — faltan '+missingYears.length" in text


class TestEquiposCopyNeverSaysCompletoOrVeinte:
    def test_no_equipos_copy_contains_completo_or_veinte(self):
        text = web_text()
        head_idx = text.index('<section id="equipos"')
        next_idx = text.index('<section id="jugadores"')
        equipos_static = text[head_idx:next_idx]
        assert "completo" not in equipos_static.lower()
        assert "veinte" not in equipos_static.lower()

        tabs_text = TABS_JS.read_text(encoding="utf-8")
        hero_start = tabs_text.index("function buildEquiposHero(")
        hero_end = tabs_text.index("\n}", hero_start)
        hero_src = tabs_text[hero_start:hero_end]
        assert "completo" not in hero_src
        assert "veinte" not in hero_src

        landing_start = tabs_text.index("function buildEquiposLanding(")
        landing_end = tabs_text.index("\n}", landing_start)
        landing_src = tabs_text[landing_start:landing_end]
        assert "completo" not in landing_src
        assert "veinte" not in landing_src

        viewdesc_start = tabs_text.index("const VIEW_DESC={")
        equipos_start = tabs_text.index("equipos:{", viewdesc_start)
        archivo_start = tabs_text.index("archivo:{", equipos_start)
        viewdesc_equipos_src = tabs_text[equipos_start:archivo_start]
        assert "completo" not in viewdesc_equipos_src
        assert "veinte" not in viewdesc_equipos_src
