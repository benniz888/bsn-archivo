"""PHASE_67B -- La Temporada Perfecta difficulty (Option C, threshold 240), web/js/games.js.
Pins the win mapping by extracting the real `winsFor` closure from finishDraft and running
it in node, so the test exercises the shipped expression, not a copy."""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
GAMES_JS = ROOT / "web/js/games.js"
SRC = GAMES_JS.read_text(encoding="utf-8")

needs_node = pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")


def _wins(totals, K=None, S=None):
    m = re.search(r"const winsFor=t=>[^\n]+;", SRC)
    assert m, "winsFor closure not found in finishDraft"
    k = re.search(r"let CAL_K=(\d+), CAL_S=(\d+);", SRC)
    K = int(k.group(1)) if K is None else K
    S = int(k.group(2)) if S is None else S
    js = f"const K={K},S={S};{m.group(0)}console.log(JSON.stringify({json.dumps(totals)}.map(winsFor)));"
    out = subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


@needs_node
class TestWinsMapping:
    def test_calibration_constants(self):
        assert "let CAL_K=130, CAL_S=36;" in SRC

    def test_threshold_240_is_a_perfect_season(self):
        assert _wins([240, 240.0, 300, 1000]) == [34, 34, 34, 34]

    def test_33_win_band_is_236_to_240(self):
        assert _wins([236, 237.5, 239, 239.99]) == [33, 33, 33, 33]

    def test_235_is_at_most_32(self):
        assert _wins([235, 235.99])[0] <= 32
        assert _wins([235.99])[0] <= 32

    def test_results_step_32_33_34_with_no_gap(self):
        w = _wins([i * 0.25 for i in range(0, 1201)])
        assert {32, 33, 34} <= set(w)
        assert sorted(set(w)) == list(range(min(w), 35))

    def test_non_perfect_seasons_are_capped_at_33(self):
        # a curve that would give 34 everywhere must still stop at 33 below the gate
        assert _wins([239.99, 200, 150], K=0, S=1) == [33, 33, 33]

    def test_curve_is_monotonic(self):
        totals = [i * 0.5 for i in range(0, 801)]
        w = _wins(totals)
        assert all(b >= a for a, b in zip(w, w[1:]))
        assert w[0] <= 1 and w[-1] == 34
        assert all(0 <= x <= 34 for x in w)


class TestVerdictAndShare:
    def test_unsourced_record_clause_is_gone(self):
        assert "29-5" not in SRC
        assert "Bayamón 1993" not in SRC

    def test_30_plus_verdict_makes_no_historical_claim(self):
        assert "Mejor que cualquier temporada real" not in SRC
        assert "wins>=30?'Cuatro derrotas o menos.'" in SRC

    def test_perfect_verdict_is_neutral(self):
        assert "Temporada perfecta. 34 victorias, ninguna derrota." in SRC

    def test_share_text_is_just_record_and_roster(self):
        start = SRC.index("function shareDraft(w){")
        src = SRC[start:SRC.index("\n}", start)]
        assert "${w}-${34-w}" in src
