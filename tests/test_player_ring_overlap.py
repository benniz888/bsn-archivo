"""PHASE_65 -- visual regression for the decorative rings in the player stat tiles (#jugadores).

Geometry, not pixels: tests/harness/ring_overlap_probe.mjs loads the real site in Chromium AND WebKit at
390 and 1000px in dark and light, and for every tile with a circular ::before/::after decoration compares
the circle with the INK rectangles of the tile's text (Range rects). It fails if any decorative circle
overlaps a label or number, if the content is not painted above the circle, if label/number contrast
drops under 4.5:1, if the rendered Historia/Jugadores text contains an emoji, if a phone landing hides its
first explore card behind the bottom tabs, or if the page logs a console error.
Skips with a stated reason when node or playwright-core is missing (same convention as
test_cuadricula_exhaustive.py)."""
import glob
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _find_playwright_core():
    env = os.environ.get("PLAYWRIGHT_CORE")
    if env and (Path(env) / "index.js").exists():
        return env
    hits = sorted(glob.glob("/private/tmp/**/node_modules/playwright-core/index.js", recursive=True))
    return str(Path(hits[0]).parent) if hits else None


@pytest.fixture(scope="module")
def probe():
    node = shutil.which("node")
    core = _find_playwright_core()
    if not node or not core:
        pytest.skip("needs node and playwright-core (set PLAYWRIGHT_CORE=<dir>)")
    res = subprocess.run([node, str(ROOT / "tests" / "harness" / "ring_overlap_probe.mjs")],
                         env={**os.environ, "PLAYWRIGHT_CORE": core}, capture_output=True, text=True, timeout=600)
    assert res.returncode == 0, res.stderr[-2000:]
    return json.loads(res.stdout)


def _tiles(probe):
    """Decorated stat tiles on the player pages plus the record cards on #jugadores/records."""
    return [(r["cfg"], r.get("player", "records"), t) for r in probe["results"]
            if r["kind"] in ("player", "records") for t in r["tiles"]]


def _pages(probe):
    return [r for r in probe["results"] if r["kind"] == "page"]


def test_the_matrix_ran_in_both_engines_widths_and_themes(probe):
    cfgs = {r["cfg"] for r in probe["results"]}
    assert cfgs == {f"{e}/{w}/{t}" for e in ("chromium", "webkit") for w in (390, 1000) for t in ("dark", "light")}
    assert len(probe["players"]) == 3


def test_every_player_page_has_decorated_tiles_to_check(probe):
    per_cfg = {}
    for r in probe["results"]:
        if r["kind"] == "player":
            per_cfg[r["cfg"]] = per_cfg.get(r["cfg"], 0) + sum(t["ink"] for t in r["tiles"] if t["circles"])
    assert per_cfg and all(n > 0 for n in per_cfg.values()), per_cfg


def test_record_cards_were_measured_including_their_notes(probe):
    recs = [(r["cfg"], t) for r in probe["results"] if r["kind"] == "records" for t in r["tiles"]]
    assert len(recs) >= 8 * 8, len(recs)          # 8 configs x at least 8 record cards
    assert all(t["noteInk"] > 0 for _cfg, t in recs if "rec-card" in t["tile"] and t["ink"] >= 4), "a record note was not measured"
    assert sum(1 for _cfg, t in recs if t["noteInk"] > 0) >= 8 * 8


def test_no_decorative_circle_overlaps_a_label_or_number(probe):
    bad = [(cfg, player, h) for cfg, player, t in _tiles(probe) for h in t["hits"]]
    assert not bad, bad[:8]


def test_content_is_painted_above_the_circle(probe):
    bad = [(cfg, player, z) for cfg, player, t in _tiles(probe) for z in t["zfail"]]
    assert not bad, bad[:8]


def test_tile_text_contrast_is_at_least_4_5(probe):
    bad = [(cfg, player, lab) for cfg, player, t in _tiles(probe) for lab in t["labels"] if lab["ratio"] < 4.5]
    assert not bad, bad[:8]


def test_no_emoji_in_the_rendered_historia_and_jugadores_pages(probe):
    bad = [(r["cfg"], r["view"], r["emoji"]) for r in _pages(probe) if r["emoji"]]
    assert not bad, bad


def test_phone_landings_show_the_first_explore_card_above_the_bottom_tabs(probe):
    for r in _pages(probe):
        if r["view"] not in ("historia", "jugadores") or "/390/" not in r["cfg"]:
            continue
        assert r["cardBottom"] is not None, r
        assert r["cardBottom"] <= r["tabsTop"], r
        assert r["h1Top"] >= r["hdrBottom"], r


def test_historia_kpi_counts(probe):
    for r in _pages(probe):
        if r["view"] == "historia":
            assert r["kpis"] == 2, r
        if r["view"] == "historia-cinta":
            assert r["kpis"] == 2, r
        if r["view"] == "jugadores":
            assert r["kpis"] == 3, r


def test_no_console_errors(probe):
    assert probe["errors"] == [], probe["errors"][:5]


def test_explore_cards_have_distinct_icons_a_16px_gap_and_no_empty_slot(probe):
    seen = 0
    for r in _pages(probe):
        ex = r.get("explore")
        if r["view"] not in ("historia", "jugadores"):
            continue
        assert ex, r
        seen += 1
        assert ex["n"] == (7 if r["view"] == "historia" else 8), r
        assert None not in ex["icons"] and len(set(ex["icons"])) == ex["n"], ("shared icon", r["cfg"], r["view"])
        assert abs(ex["gap"] - 16) <= 1, ("heading-to-grid gap", r["cfg"], r["view"], ex["gap"])
        assert abs(ex["lastRowSpan"] - ex["gridWidth"]) <= 2, ("orphan slot in the last row", r["cfg"], r["view"], ex)
        assert ex["cols"] == (2 if "/390/" in r["cfg"] else 4), ("columns", r["cfg"], r["view"], ex["cols"])
    assert seen == 16


def test_only_the_active_and_keyboard_focused_subnav_pills_are_highlighted(probe):
    subs = [r for r in probe["results"] if r["kind"] == "subnav"]
    assert len(subs) == 4                       # touch run at 390px: 2 engines x 2 themes
    for r in subs:
        cur = [p for p in r["pills"] if p["current"]]
        assert [p["text"] for p in cur] == ["Resumen"], r
        rest = [p for p in r["pills"] if not p["current"]]
        # :hover still matches after a tap on touch; what must not happen is a visible effect from it
        assert not any(p["focusVisible"] or p["outline"] != "none" for p in rest), r
        assert len({p["border"] for p in rest}) == 1, ("a non-active pill has a different border", r)
