"""PHASE_62 -- La Cuadricula must accept every player who truly satisfies a cell, under every
reasonable spelling, and must still reject everyone who does not.

How it works. The game's POOL is assembled in the browser from six scripts, so a Python re-port
would test a copy, not the game. tests/harness/grid_probe.mjs loads web/ in Chromium and drives the
site's real submitGuess() for each (player, spelling); this file asserts on the JSON it prints.
Needs node + playwright-core (PLAYWRIGHT_CORE=<dir>, or any */node_modules/playwright-core under
/private/tmp); skips with a stated reason when neither exists.

The cell universe is exactly what newBoard() can emit: rows are clubs, columns are clubs or
categories, never the same axis twice. "Truly satisfies" is computed here from facts that do not go
through CATS: per-season rows (ss) for clubs, decades and best-season ppg, the MVP and scoring-title
tables in web/data/index/ for those two tags, and the position label itself. No result of the game's
own predicates is used as truth.
"""

import glob
import json
import os
import re
import shutil
import subprocess
import unicodedata
from collections import defaultdict
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "web" / "data" / "index"


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
    res = subprocess.run(
        [node, str(ROOT / "tests" / "harness" / "grid_probe.mjs")],
        env={**os.environ, "PLAYWRIGHT_CORE": core},
        capture_output=True, text=True, timeout=180,
    )
    assert res.returncode == 0, res.stderr[-2000:]
    out = json.loads(res.stdout)
    assert out["pageErrors"] == [], out["pageErrors"]
    return out


def _nz(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    return re.sub(r"[«»\"'.]", "", re.sub(r"[̀-ͯ]", "", s)).strip()


def _strip_nick(s):
    return re.sub(r"\s+", " ", re.sub(r"«[^»]*»|\"[^\"]*\"|'[^']*'", " ", s)).strip()


GUARD_LABELS = {"G", "PG", "SG"}
POST_LABELS = {"C", "PF", "F/C"}


def _best_ppg(p):
    """Best single-season ppg. Rows for the season that has an official line (hi) are skipped:
    RealGM's 2026 figure includes playoff games and the official one does not (docs/project.md
    / web/index.html mergeOfficial2026), so for that season the official number wins."""
    vals = []
    if p["hi"]:
        vals.append(p["hi"][1])
    official_year = p["hi"][0] if p["hi"] and p["o26"] else None
    for row in p["ss"] or []:
        if row[3] is None or row[0] == official_year:
            continue
        vals.append(row[3])
    if not vals and p["ppg"] is not None:
        vals.append(p["ppg"])
    return max(vals) if vals else None


def _tokens(s):
    return set(re.sub(r"[«»\"',.]", " ", _nz(s).replace(",", " ")).split())


# Tag rows the archive tables assert but that cannot be applied without the owner choosing:
#  - first-name conflict between the table row and the pool player (identity, rule D1)
#  - the site's own Hall-of-Fame card (data.js) says the player has 0 MVPs, so two curated
#    sources disagree (same stance as D5: do not quietly pick one)
OWNER_DECISION = {
    ("Larry Ayuso", "scoring"): "table row says ELIAS AYUSO (2002); pool says Larry",
    ("Carlos Bermúdez", "mvp"): "table row says Charlie Bermudez (1978); pool says Carlos",
    ("Mario Butler", "mvp"): "mvp.json 1988 vs Hall-of-Fame card mvp:0",
    ("Rubén Rodríguez", "mvp"): "mvp.json 1979 vs Hall-of-Fame card mvp:0",
    ("Neftalí Rivera", "mvp"): "mvp.json 1973 vs Hall-of-Fame card mvp:0",
    ("Rolando Frazer", "mvp"): "mvp.json 1981 vs Hall-of-Fame card mvp:0",
}


def build_truth(probe):
    """axis key -> predicate over a pool dict, built from independent facts."""
    xwalk = json.loads((DATA / "player_xwalk.json").read_text())
    awards = defaultdict(set)  # bsnpr_id -> {(tag, row name)}
    for r in json.loads((DATA / "mvp.json").read_text()):
        if r["bsnpr_id"]:
            awards[r["bsnpr_id"]].add(("mvp", r["player"]))
    for r in json.loads((DATA / "scoring_titles.json").read_text()):
        c = r.get("champion") or {}
        if c.get("bsnpr_id"):
            awards[c["bsnpr_id"]].add(("scoring", c["player"]))

    def pid(p):
        return xwalk.get(_nz(p["n"])) or xwalk.get(_nz(_strip_nick(p["n"])))

    def has_award(p, tag):
        """Identity by crosswalk id AND the row's name tokens inside the pool name (a nickname-only
        row such as PACHIN VICENS qualifies; ELIAS AYUSO vs Larry Ayuso does not)."""
        if (p["n"], tag) in OWNER_DECISION:
            return False
        full = _tokens(p["n"])
        return any(t == tag and _tokens(name.replace(",", " ")) <= full for t, name in awards.get(pid(p), ()))

    def clubs(p):
        return set(p["c"]) | {r[1] for r in p["ss"] or []}

    def decades(p):
        return set(p["d"]) | {r[0] // 10 * 10 for r in p["ss"] or []}

    t = {}
    for k in probe["clubs"]:
        t["c:" + k] = lambda p, k=k: k in clubs(p)
    for dec in (1980, 1990, 2000, 2010, 2020):
        t["a:d%d" % dec] = lambda p, dec=dec: dec in decades(p)
    t["a:dpre1980"] = lambda p: any(d < 1980 for d in decades(p))
    t["a:guard"] = lambda p: p["pos"] in GUARD_LABELS
    t["a:big"] = lambda p: p["pos"] in POST_LABELS
    t["a:p20"] = lambda p: (_best_ppg(p) or 0) >= 20
    for tag in ("champion", "import", "native", "nba", "10k", "legend"):
        t["a:" + tag] = lambda p, tag=tag: tag in p["t"]
    t["a:mvp"] = lambda p: "mvp" in p["t"] or has_award(p, "mvp")
    t["a:scoring"] = lambda p: "scoring" in p["t"] or has_award(p, "scoring")
    return t


@pytest.fixture(scope="module")
def truth(probe):
    return build_truth(probe)


def _failures_by_kind(probe):
    sol_by_cell = {(c["r"], c["c"]): set(c["sol"]) for c in probe["cells"] if c["sol"]}
    bad = defaultdict(list)
    for row in probe["rows"]:
        if row["resolved"] == row["name"]:
            continue
        cells = [k for k, s in sol_by_cell.items() if row["name"] in s]
        bad[row["kind"]].append((row["name"], row["text"], row["resolved"], cells[0] if cells else None))
    return bad


SPELLINGS = ["exact", "lower", "upper", "accentless", "no_nickname", "straight_quotes", "no_suffix",
             "suffix_with_comma", "dots_removed", "dots_spaced", "hyphen_as_space", "padded"]


class TestEveryTrueSolutionIsAccepted:
    @pytest.mark.parametrize("kind", SPELLINGS)
    def test_spelling_resolves_to_the_same_player(self, probe, kind):
        rows = [r for r in probe["rows"] if r["kind"] == kind]
        assert rows, "probe produced no %r spellings" % kind
        bad = [(r["name"], r["text"], r["resolved"]) for r in rows if r["resolved"] != r["name"]]
        assert not bad, "%d/%d %s spellings rejected, e.g. %s" % (len(bad), len(rows), kind, bad[:5])

    def test_every_cell_solution_is_reachable_by_its_exact_name(self, probe):
        reach = {(r["name"]): r["resolved"] for r in probe["rows"] if r["kind"] == "exact"}
        miss = [n for c in probe["cells"] for n in c["sol"] if reach.get(n) != n]
        assert not miss, miss[:5]


class TestCriteriaMatchIndependentFacts:
    def _cells(self, probe, truth):
        pool = {p["n"]: p for p in probe["pool"]}
        for c in probe["cells"]:
            want = {n for n, p in pool.items() if truth[c["r"]](p) and truth[c["c"]](p)}
            yield c, want, set(c["sol"])

    def test_no_true_player_is_missing_from_a_cell(self, probe, truth):
        miss = [(c["r"], c["c"], sorted(want - got)) for c, want, got in self._cells(probe, truth) if want - got]
        assert not miss, "%d cells reject a player the archive supports, e.g. %s" % (len(miss), miss[:5])

    def test_no_wrong_player_is_accepted_into_a_cell(self, probe, truth):
        extra = [(c["r"], c["c"], sorted(got - want)) for c, want, got in self._cells(probe, truth) if got - want]
        assert not extra, "%d cells accept a player the archive does not support, e.g. %s" % (len(extra), extra[:5])

    def test_cell_universe_is_every_row_club_by_column_axis(self, probe):
        n_clubs, n_cats = len(probe["clubs"]), len(probe["cats"])
        assert len(probe["cells"]) == n_clubs * (n_clubs - 1 + n_cats)


class TestCriteriaEdgeCases:
    def test_decade_boundaries_follow_the_season_year(self, probe):
        """'Jugo en los 2000' means a season in 2000..2009: 1999 and 2010 do not count."""
        want = {2000: lambda y: 2000 <= y <= 2009, 1990: lambda y: 1990 <= y <= 1999,
                2010: lambda y: 2010 <= y <= 2019, 2020: lambda y: 2020 <= y <= 2029}
        bad = []
        for p in probe["pool"]:
            if not p["ss"]:
                continue
            years = [r[0] for r in p["ss"]]
            for dec, rule in want.items():
                if any(rule(y) for y in years) and dec not in p["d"]:
                    bad.append((p["n"], dec, "season in decade but missing from d"))
        assert not bad, bad[:5]

    def test_poste_is_exactly_c_pf_fc_and_base_o_escolta_exactly_g_pg_sg(self, probe):
        pos = {p["n"]: p["pos"] for p in probe["pool"]}
        for axis, labels in (("a:big", POST_LABELS), ("a:guard", GUARD_LABELS)):
            got = {n for c in probe["cells"] if c["c"] == axis for n in c["sol"]}
            assert got, axis
            assert all(pos[n] in labels for n in got), (axis, [(n, pos[n]) for n in got if pos[n] not in labels])

    def test_no_player_is_both_guard_and_poste(self, probe):
        both = [p["n"] for p in probe["pool"] if p["pos"] in GUARD_LABELS and p["pos"] in POST_LABELS]
        assert not both

    def test_forward_labels_are_neither_guard_nor_poste(self, probe):
        cells = [c for c in probe["cells"] if c["c"] in ("a:big", "a:guard")]
        fwd = {p["n"] for p in probe["pool"] if p["pos"] in ("SF", "F")}
        assert not (fwd & {n for c in cells for n in c["sol"]})

    def test_partial_data_is_never_coerced_to_a_match(self, probe):
        """PC2: NULL is not 0 and not 'every club'. No club -> no club cell; no ppg -> no p20."""
        cells = probe["cells"]
        no_club = {p["n"] for p in probe["pool"] if not p["c"] and not p["ss"]}
        in_club_cell = {n for c in cells if c["c"].startswith("c:") for n in c["sol"]}
        assert not (no_club & in_club_cell)
        no_ppg = {p["n"] for p in probe["pool"] if p["ppg"] is None and not p["hi"] and not p["ss"]}
        in_p20 = {n for c in cells if c["c"] == "a:p20" for n in c["sol"]}
        assert not (no_ppg & in_p20)
        no_pos = {p["n"] for p in probe["pool"] if not p["pos"]}
        in_pos = {n for c in cells if c["c"] in ("a:guard", "a:big") for n in c["sol"]}
        assert not (no_pos & in_pos)


class TestWrongAnswersAreStillRejected:
    def test_every_pool_player_is_judged_as_themselves(self, probe):
        """A wrong guess must be judged on the person typed, so a rejection is about them."""
        exact = {r["name"]: r["resolved"] for r in probe["rows"] if r["kind"] == "exact"}
        pool = {p["n"] for p in probe["pool"]}
        assert not [n for n in pool if exact.get(n, n) != n]

    def test_garbage_and_too_short_guesses_resolve_to_nobody(self, probe):
        by_text = {r["text"]: r["resolved"] for r in probe["probes"]}
        assert by_text["Zzzz Nobody"] is None
        assert by_text["ab"] is None, "two letters must not pick an arbitrary player"

    def test_an_ambiguous_fragment_is_not_resolved_to_the_first_match(self, probe):
        """'Dalmau' fits two pool players; the game must not pick one and charge the guess."""
        by_text = {r["text"]: r["resolved"] for r in probe["probes"]}
        assert by_text["Dalmau"] is None

    def test_a_unique_fragment_still_resolves(self, probe):
        by_text = {r["text"]: r["resolved"] for r in probe["probes"]}
        assert by_text["Blondet"] == "Héctor Blondet"

    def test_archive_duplicates_outside_the_pool_are_not_mistaken_for_someone_else(self, probe):
        """Backlog: Alamo / Candido Fret and Reyes / Hector are archive-index players, not in the
        376-player game pool. They must come back 'not in the roster', never as another player."""
        by_text = {r["text"]: r["resolved"] for r in probe["probes"]}
        for text in ("Candido Fret", "Alamo", "Alamo, Candido Fret", "Hector Reyes"):
            assert by_text[text] is None, (text, by_text[text])
        names = {p["n"] for p in probe["pool"]}
        assert not any(_nz(n) in ("candido fret alamo", "candido alamo", "hector reyes") for n in names)


class TestRejectionReason:
    def test_wrong_guess_names_only_the_failed_criterion_and_costs_an_attempt(self, probe):
        r = probe["reasons"]
        msg = r["wrong_player"]
        assert r["failed_axis_label"] in msg and "no figura en el archivo como" in msg
        assert r["passed_axis_label"] not in msg, "the criterion the player met must not be blamed"
        assert "Intento gastado" in msg and r["wrong_spent"] == 1
        assert "PENDIENTE" not in msg

    def test_rejection_resting_only_on_missing_data_is_reported_and_free(self, probe):
        r = probe["reasons"]
        assert "El archivo no tiene datos de" in r["no_data_text"] and "No gasta intento" in r["no_data_text"]
        assert r["no_data_spent"] == 0, "missing archive data must not cost an attempt"
        assert "PENDIENTE" not in r["no_data_text"]
