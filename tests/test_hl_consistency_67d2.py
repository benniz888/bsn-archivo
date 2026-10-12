"""PHASE_67D2 -- Sube y Baja never builds a question from a LEADERS row whose total/games disagrees
with its listed average (tolerance 0.15, same rule as the quiz clues), and never pairs equal or
near-equal values (gap must be >= max(1, 2% of the larger)).

tests/harness/hl_probe.mjs drives the site's own newHL() in Chromium; skips without node +
playwright-core (PLAYWRIGHT_CORE=<dir>, or any */node_modules/playwright-core under /private/tmp).
"""

import glob
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TABS_JS = (ROOT / "web/js/tabs.js").read_text(encoding="utf-8")


def _core():
    env = os.environ.get("PLAYWRIGHT_CORE")
    if env and (Path(env) / "index.js").exists():
        return env
    hits = sorted(glob.glob("/private/tmp/**/node_modules/playwright-core/index.js", recursive=True))
    return str(Path(hits[0]).parent) if hits else None


def _leaders():
    """LEADERS rows parsed from the source: {category: [(name, total, games, avg)]}."""
    block = TABS_JS[TABS_JS.index("const LEADERS={"):TABS_JS.index("const MVP_REPEAT")]
    out = {}
    for cat in ("points", "rebounds", "assists"):
        part = block[block.index(cat + ":["):]
        part = part[:part.index("]]") + 2]
        out[cat] = [(n, int(t), int(g), float(a)) for n, t, g, a in
                    re.findall(r'\[\d+,"([^"]+)","[^"]*","[^"]*",(\d+),(\d+),([\d.]+)\]', part)]
    return out


def test_dalmau_assists_row_is_the_only_inconsistent_row():
    bad = {(c, n) for c, rows in _leaders().items() for n, t, g, a in rows if abs(t / g - a) > 0.15}
    assert bad == {("assists", "Raymond Dalmau")}


@pytest.fixture(scope="module")
def probe():
    node, core = shutil.which("node"), _core()
    if not node or not core:
        pytest.skip("needs node and playwright-core (set PLAYWRIGHT_CORE=<dir>)")
    res = subprocess.run([node, str(ROOT / "tests/harness/hl_probe.mjs")], env={**os.environ, "PLAYWRIGHT_CORE": core},
                         capture_output=True, text=True, timeout=180)
    assert res.returncode == 0, res.stderr[-2000:]
    out = json.loads(res.stdout)
    assert out["errors"] == []
    return out


def test_failing_row_is_not_an_option(probe):
    rows = {s["label"]: s["rows"] for s in probe["sets"]}
    assert "Raymond Dalmau" not in [r[0] for r in rows["asistencias de carrera"]]
    assert len(rows["asistencias de carrera"]) == 9
    # his other categories are consistent and stay
    assert "Raymond Dalmau" in [r[0] for r in rows["puntos de carrera"]]
    assert "Raymond Dalmau" in [r[0] for r in rows["rebotes de carrera"]]


def test_no_built_question_uses_the_failing_row(probe):
    for p in probe["pairs"]:
        if p["label"] == "asistencias de carrera":
            assert "Raymond Dalmau" not in (p["a"][0], p["b"][0])


def test_pairs_are_never_equal_or_near_equal(probe):
    assert {p["label"] for p in probe["pairs"]} == {s["label"] for s in probe["sets"]}
    for p in probe["pairs"]:
        (na, va), (nb, vb) = p["a"][:2], p["b"][:2]
        assert na != nb
        assert abs(va - vb) >= max(1, 0.02 * max(va, vb))
