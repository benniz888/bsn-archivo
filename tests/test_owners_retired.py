"""PHASE_41 -- Apoderados (buildOwners()) and Retirados (buildRetiredNums()), web/js/tabs.js.
Neither OWNERS nor RETIRED (web/js/data.js) is edited by that redesign; both are read-only
inputs the two builders render differently. Ports the relevant JS logic to Python, the same
convention test_route_slugs.py/test_nick_key.py already use, rather than driving a browser:
(a)/(b) every active F club appears in Apoderados, OWNERS' own 5 first, then the rest, with
the intro numeral computed from the same two counts; (c) Bayamón's retired-number count line
collapses the duplicate 17 into one chip with an "x2" mark, 8 total / 7 distinct; (d) RETIRED
itself is still exactly what PHASE_41A's own read-only source check found and left alone."""

import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_JS = ROOT / "web/js/data.js"
TABS_JS = ROOT / "web/js/tabs.js"


def _franchises():
    """key -> {"name": str, "active": bool}, ported from F (web/js/data.js)."""
    text = DATA_JS.read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r'(\w+):\{name:"([^"]+)"[^}]*?active:(\d)', text):
        out[m.group(1)] = {"name": m.group(2), "active": m.group(3) == "1"}
    return out


def _owners():
    """[(key, owner_name, note)], ported from OWNERS (web/js/tabs.js)."""
    text = TABS_JS.read_text(encoding="utf-8")
    m = re.search(r"const OWNERS=\[(.*?)\n\];", text, re.S)
    rows = re.findall(r"\['(\w+)','([^']*)','([^']*)'\]", m.group(1))
    return rows


def _retired():
    """[(club_name, total, [numbers_as_strings])], ported from RETIRED (web/js/data.js)."""
    text = DATA_JS.read_text(encoding="utf-8")
    m = re.search(r"const RETIRED=\[(.*?)\n\];", text, re.S)
    rows = re.findall(r'\["([^"]+)",(\d+),"([^"]+)"\]', m.group(1))
    return [(name, int(total), nums.split(" · ")) for name, total, nums in rows]


def _count_chips(nums):
    """Port of buildRetiredNums()'s own Map-based count -- groups by occurrence, never
    deletes/dedupes the source list itself."""
    counts = {}
    for n in nums:
        counts[n] = counts.get(n, 0) + 1
    dupes = [(n, c) for n, c in counts.items() if c > 1]
    return counts, dupes


class TestApoderadosShowsAllActiveClubs:
    def test_every_active_club_appears(self):
        F = _franchises()
        active_keys = [k for k, v in F.items() if v["active"]]
        owned_keys = [k for k, _, _ in _owners()]
        unowned_keys = [k for k in active_keys if k not in owned_keys]
        # every owned key is itself an active club (OWNERS is a subset of the active roster)
        assert set(owned_keys) <= set(active_keys)
        # the view's own rendered order is owned ++ unowned, covering all 12
        rendered_order = owned_keys + unowned_keys
        assert set(rendered_order) == set(active_keys)
        assert len(rendered_order) == len(active_keys) == 12

    def test_owned_clubs_come_first_in_owners_own_existing_order(self):
        # _owners() reads OWNERS' own array via regex.findall, which preserves source
        # order by construction -- the real thing to guard is that buildOwners() itself
        # still renders OWNERS.map(...) (ownedCards) before unownedKeys.map(...), not a
        # second, independent ordering.
        text = TABS_JS.read_text(encoding="utf-8")
        fn_start = text.index("function buildOwners(){")
        fn_end = text.index("\n}", fn_start)
        fn_src = text[fn_start:fn_end]
        owned_pos = fn_src.index("const ownedCards=OWNERS.map(")
        unowned_pos = fn_src.index("const unownedCards=unownedKeys.map(")
        join_pos = fn_src.index("${ownedCards}${unownedCards}")
        assert owned_pos < unowned_pos < join_pos


class TestApoderadosIntroIsComputed:
    def test_intro_counts_match_f_and_owners(self):
        F = _franchises()
        active_n = sum(1 for v in F.values() if v["active"])
        owned_n = len(_owners())
        assert active_n == 12
        assert owned_n == 5
        text = TABS_JS.read_text(encoding="utf-8")
        assert "const wOwned=numWordsEs(OWNERS.length), wActive=numWordsEs(activeKeys.length);" in text
        assert "' de los '+wActive" in text
        assert "'clubes tienen apoderado confirmado en el archivo.'" not in text  # no stray hardcode
        assert "clubes tienen apoderado confirmado en el archivo." in text


class TestRetiradosCollapsesDuplicates:
    def test_bayamon_is_8_total_7_distinct_one_double(self):
        rows = _retired()
        bay = next(r for r in rows if r[0] == "Vaqueros de Bayamón")
        _, total, nums = bay
        assert total == 8
        assert len(nums) == 8
        counts, dupes = _count_chips(nums)
        assert len(counts) == 7  # 7 distinct chips rendered
        assert dupes == [("17", 2)]

    def test_guaynabo_is_3_with_no_duplicates(self):
        rows = _retired()
        gua = next(r for r in rows if r[0] == "Mets de Guaynabo")
        _, total, nums = gua
        assert total == 3
        counts, dupes = _count_chips(nums)
        assert len(counts) == 3
        assert dupes == []

    def test_the_app_builds_the_same_count_and_dupe_logic(self):
        text = TABS_JS.read_text(encoding="utf-8")
        assert "r[2].split(' · ').forEach(n=>counts.set(n,(counts.get(n)||0)+1));" in text
        assert "const dupes=[...counts.entries()].filter(([,c])=>c>1);" in text
        assert "se retiró '" in text and "dos veces" in text
        assert "La liga los publica como dígitos, sin nombres — y el archivo no los adivina." in text


class TestRetiredDataItselfIsUnchanged:
    """PHASE_41A's own read-only finding: undeterminable whether Bayamón's duplicate 17 is
    a typo or a real double-retirement, so it stays exactly as recorded -- not guessed at,
    not silently 'fixed' by this redesign."""

    def test_retired_array_values_are_untouched(self):
        rows = _retired()
        assert rows == [
            ("Vaqueros de Bayamón", 8, ["4", "5", "9", "15", "16", "17", "17", "54"]),
            ("Mets de Guaynabo", 3, ["5", "9", "15"]),
        ]
