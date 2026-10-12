"""PHASE_67C -- ¿Quién soy? clue ladders, the weighted draw, the guess combobox, and the
Temporada Perfecta "pase" plural.

How it works. The pool and every table behind the clues are assembled in the browser from several
scripts, so a Python re-port would test a copy. tests/harness/quiz_probe.mjs loads web/ in Chromium,
asks the site's own clueList() for every POOL player, drives newQuiz() 400 times and the real guess
path, and prints one JSON document that this file asserts on. Needs node + playwright-core
(PLAYWRIGHT_CORE=<dir>, or any */node_modules/playwright-core under /private/tmp); skips with a
stated reason when neither exists. The source-level checks and the plural check need neither.
"""

import glob
import json
import os
import re
import shutil
import subprocess
import unicodedata
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TABS_JS = (ROOT / "web/js/tabs.js").read_text(encoding="utf-8")
GAMES_JS = (ROOT / "web/js/games.js").read_text(encoding="utf-8")

FINAL_KINDS = {"mvp", "fin", "sco", "rook", "def", "six", "mip", "reb", "ast", "titles", "rank", "rec",
               "stone"}
SOURCES = ("POOL.", "awards.", "LEADERS.", "RECORDS:", "STONE", "BIO.", "NBA_PLAYERS", "HOF.")
STOP = {"del", "los", "las", "van", "von"}


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
    res = subprocess.run([node, str(ROOT / "tests/harness/quiz_probe.mjs")],
                         env={**os.environ, "PLAYWRIGHT_CORE": core}, capture_output=True, text=True, timeout=180)
    assert res.returncode == 0, res.stderr[-2000:]
    out = json.loads(res.stdout)
    assert out["pageErrors"] == [], out["pageErrors"]
    return out


def _words(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    s = re.sub(r"[̀-ͯ]", "", s)
    return [w for w in re.sub(r"[^a-z0-9]+", " ", s).split() if w]


def _ladders(probe):
    return [r for r in probe["rows"] if r["L"]]


class TestLadders:
    def test_pool_is_not_empty_and_has_famous_and_mid_players(self, probe):
        L = _ladders(probe)
        assert len(L) >= 50
        assert {"f", "m"} <= {r["tier"] for r in L}

    def test_no_ladder_ends_on_the_best_season_line(self, probe):
        for r in _ladders(probe):
            assert r["L"][-1]["k"] not in ("best", "bestline"), r["n"]
            assert not re.search(r"mejor temporada registrada|En \d{4} promedió", r["L"][-1]["t"]), r["n"]

    def test_every_ladder_has_at_least_three_clues(self, probe):
        assert all(3 <= len(r["L"]) <= 6 for r in _ladders(probe))

    def test_no_clue_before_the_last_leaves_a_single_candidate(self, probe):
        for r in _ladders(probe):
            assert all(c["n"] >= 2 for c in r["L"][:-1]), (r["n"], [c["n"] for c in r["L"]])

    def test_last_clue_leaves_exactly_one_candidate(self, probe):
        for r in _ladders(probe):
            assert r["L"][-1]["n"] == 1, (r["n"], r["L"][-1])

    def test_candidate_counts_never_grow(self, probe):
        for r in _ladders(probe):
            ns = [c["n"] for c in r["L"][:-1]]
            assert ns == sorted(ns, reverse=True), (r["n"], ns)

    def test_name_tokens_never_appear_in_any_clue(self, probe):
        for r in _ladders(probe):
            bad = {w for w in _words(r["n"]) if len(w) >= 3 and w not in STOP}
            for c in r["L"]:
                assert not (bad & set(_words(c["t"]))), (r["n"], c["t"])
            assert not re.search("«", " ".join(c["t"] for c in r["L"])), r["n"]

    def test_every_clue_names_its_data_field(self, probe):
        for r in _ladders(probe):
            for c in r["L"]:
                assert c["f"].startswith(SOURCES) and len(c["f"]) >= 5, (r["n"], c)

    def test_last_clue_is_an_award_record_title_rank_or_best_season(self, probe):
        assert all(r["L"][-1]["k"] in FINAL_KINDS for r in _ladders(probe))

    def test_no_free_text_bio_is_ever_shown(self, probe):
        rows = _ladders(probe)
        assert not any(c["k"] == "bio" for r in rows for c in r["L"])
        for r in rows:
            if r["bio"]:
                assert all(c["t"] != r["bio"] for c in r["L"]), r["n"]  # a claim rebuilt from a field may share words, never the line
        english = re.compile(r"\b(the|reached|came|home|retired|scored|won|led|and|with|first)\b", re.I)
        assert not [c["t"] for r in rows for c in r["L"] if english.search(c["t"])]
        quiz = TABS_JS[TABS_JS.index("function clueList(p){"):TABS_JS.index("function poolDatalist(){")]
        assert "p.b" not in re.sub(r"/\*.*?\*/", "", quiz, flags=re.S)

    def test_era_clue_only_for_players_who_started_before_the_2020s(self, probe):
        for r in _ladders(probe):
            if any(c["k"] == "era" for c in r["L"]):
                assert r["d"][0] < 2020, r["n"]

    def test_club_combination_only_as_fifth_or_later_clue(self, probe):
        for r in _ladders(probe):
            for i, c in enumerate(r["L"]):
                if c["k"] == "clubs":
                    assert i >= 4, r["n"]

    def test_held_players_are_not_drawable(self, probe):
        names = {r["n"] for r in _ladders(probe)}
        assert "Mario Butler" not in names and "Teófilo Cruz" not in names

    def test_decimal_point_and_comma_thousands_everywhere(self, probe):
        for r in _ladders(probe):
            for c in r["L"]:
                # a comma between digits is only ever a thousands separator (15,863), never a decimal
                assert not re.search(r"\d,\d{1,2}(?!\d)", c["t"]), c["t"]
                if "Medía" in c["t"]:
                    assert re.search(r"Medía \d\.\d\d m\.", c["t"]), c["t"]


class TestSuperlativesAndLeaks:
    """RECORDS (career rebounds: Rubén Rodríguez 6,178) contradicts LEADERS (Mario Butler 8,236 first, Rodríguez
    second), so no record or "número 1" clue exists; rank clues must match LEADERS exactly."""

    BAD = re.compile(r"récord|record|número 1\b|máximo|mayor anotador|de todos los tiempos en \w+, con 1\b", re.I)

    def test_no_record_or_number_one_clue_anywhere(self, probe):
        for r in _ladders(probe):
            for c in r["L"]:
                assert not self.BAD.search(c["t"]), (r["n"], c["t"])
                assert c["k"] != "rec"

    def test_every_rank_clue_matches_a_consistent_leaders_row(self, probe):
        cat = {"puntos": "points", "rebotes": "rebounds", "asistencias": "assists"}
        L = probe["leaders"]
        for r in _ladders(probe):
            for c in r["L"]:
                if c["k"] != "rank":
                    continue
                m = re.search(r"número (\d+) de todos los tiempos en (\w+), con ([\d,]+)", c["t"])
                if m:
                    rank, key, total = int(m[1]), cat[m[2]], int(m[3].replace(",", ""))
                    assert rank >= 2
                    rows = [x for x in L[key] if x[0] == rank and x[4] == total]
                    assert rows and abs(rows[0][4] / rows[0][5] - rows[0][6]) <= 0.15, (r["n"], c["t"])
                else:
                    m = re.search(r"diez primeros de la historia del BSN en (\w+)", c["t"])
                    assert m, c["t"]
                    key = cat[m[1]]
                    hit = [x for x in L[key] if x[0] <= 10 and _words(x[1])[-1] in _words(r["n"])]
                    assert hit and abs(hit[0][4] / hit[0][5] - hit[0][6]) <= 0.15, (r["n"], c["t"])

    def test_leaders_tables_are_sorted_with_sequential_ranks(self, probe):
        for key, rows in probe["leaders"].items():
            assert [x[0] for x in rows] == list(range(1, len(rows) + 1))
            assert all(a[4] >= b[4] for a, b in zip(rows, rows[1:])), key

    def test_garcia_has_no_world_record_claim_and_is_not_drawable(self, probe):
        for r in probe["rows"]:
            if "Garc" in r["n"]:
                assert all("mundial" not in c["t"] for c in (r["L"] or []))
        assert all(not re.search(r"mundial|world", c["t"], re.I) for r in _ladders(probe) for c in r["L"])

    def test_award_sentence_frames(self, probe):
        frames = {
            "mvp": [r"Fue elegido Jugador Más Valioso de la liga\.", r"Ganó al menos \d+ veces el premio de Jugador Más Valioso\.",
                    r"Fue Jugador Más Valioso de la liga en [\d, y]+\."],
            "fin": [r"Fue MVP de una serie final\.", r"Fue MVP de la final al menos \d+ veces\.", r"Fue MVP de la final en [\d, y]+\."],
            "sco": [r"Ganó el título de anotación\.", r"Ganó al menos \d+ títulos de anotación\.", r"Fue campeón de anotación en [\d, y]+\."],
            "reb": [r"Lideró la liga en rebotes en una temporada\.", r"Fue líder de rebotes en [\d, y]+\."],
            "ast": [r"Lideró la liga en asistencias en una temporada\.", r"Fue líder de asistencias en [\d, y]+\."],
            "rook": [r"Ganó el premio de Novato del Año\.", r"Ganó el premio de Novato del Año en \d{4}\."],
            "def": [r"Ganó el premio de Defensor del Año\.", r"Ganó el premio de Defensor del Año en \d{4}\."],
            "six": [r"Ganó el premio de Sexto Hombre\.", r"Ganó el premio de Sexto Hombre en \d{4}\."],
            "mip": [r"Ganó el premio de Progreso del Año\.", r"Ganó el premio de Progreso del Año en \d{4}\."],
        }
        seen = set()
        for r in _ladders(probe):
            for c in r["L"]:
                if c["k"] in frames:
                    seen.add(c["k"])
                    assert any(re.fullmatch(p, c["t"]) for p in frames[c["k"]]), (r["n"], c["t"])
        assert {"mvp", "sco", "mip"} <= seen
        # only the four label awards say "el premio de {label}" without a count or the MVP wording
        for r in _ladders(probe):
            for c in r["L"]:
                if c["k"] in ("fin", "sco", "reb", "ast"):
                    assert "el premio de" not in c["t"], c["t"]

    def test_progreso_del_ano_clue_comes_from_awards_mip(self, probe):
        hits = [(r["n"], c) for r in _ladders(probe) for c in r["L"] if "Progreso del Año" in c["t"]]
        assert hits
        for n, c in hits:
            assert re.fullmatch(r"Ganó el premio de Progreso del Año en \d{4}\.", c["t"]), c["t"]
            assert c["k"] == "mip" and c["f"].startswith("awards.mip=["), c
            assert re.search(r"\d{4}", c["f"]).group(0) == re.search(r"\d{4}", c["t"]).group(0)


class TestDraw:
    def test_draw_follows_the_tier_weights(self, probe):
        # tiers with fewer than 15 drawable players cannot supply their weight: weights go proportional
        size = {k: sum(1 for r in _ladders(probe) if r["tier"] == k) for k in "fml"}
        if min(size.values()) < 15:
            want = {k: v / sum(size.values()) for k, v in size.items()}
        else:
            want = {"f": 0.40, "m": 0.35, "l": 0.25}
        t = probe["tiers"]
        n = sum(t.values())
        for k in "fml":
            assert abs(t[k] / n - want[k]) <= 0.08, (k, t, want)

    def test_no_repeat_within_ten_rounds(self, probe):
        d = probe["draws"]
        assert all(n not in d[max(0, i - 10):i] for i, n in enumerate(d))

    def test_recent_list_is_stored_and_capped_at_ten(self, probe):
        assert probe["stored"] == probe["draws"][-10:]

    def test_storage_goes_through_the_guarded_st_helper(self):
        quiz = TABS_JS[TABS_JS.index("function newQuiz("):TABS_JS.index("function drawQuiz(")]
        assert "ST.json('quiz:recent')" in quiz and "ST.setJSON('quiz:recent'" in quiz
        assert "localStorage" not in quiz


class TestGuess:
    def test_ambiguous_fragment_is_not_accepted_and_costs_nothing(self, probe):
        a = probe["res"]["ambig"]
        assert a["guesses"] == 3 and a["done"] is False
        assert a["open"] is True and a["opts"] >= 2
        assert a["msg"] == "Elige un nombre de la lista. No gasta intento."

    def test_unknown_text_costs_nothing(self, probe):
        a = probe["res"]["nomatch"]
        assert a["guesses"] == 3 and a["done"] is False

    def test_wrong_full_name_costs_one_attempt(self, probe):
        a = probe["res"]["wrongFull"]
        assert a["guesses"] == 2 and a["msg"] == "No. Te quedan 2."

    def test_a_fragment_of_the_answer_is_not_accepted(self, probe):
        f = probe["res"]["fragment"]
        assert f["done"] is False and f["guesses"] == 2

    def test_exact_name_without_accents_or_case_is_accepted(self, probe):
        e = probe["res"]["exact"]
        assert e["done"] is True and e["msg"].startswith("Correcto: ")

    def test_source_has_no_substring_acceptance_and_uses_the_combobox_pattern(self):
        g = TABS_JS[TABS_JS.index("function guessQuiz("):TABS_JS.index("/* ====", TABS_JS.index("function guessQuiz("))]
        assert ".includes(v)" not in g and "v.length>=3" not in g
        d = TABS_JS[TABS_JS.index("function drawQuiz("):TABS_JS.index("function revealClue(")]
        for needle in ('role="combobox"', 'role="listbox"', "cbx-list", "cbx-opt", 'aria-expanded="false"', 'aria-controls="qSugg"'):
            assert needle in d, needle
        assert 'list="poolNames"' not in d


class TestPlural:
    def test_draft_line_uses_the_conditional(self):
        assert "${DR.skips} ${DR.skips===1?'pase':'pases'}" in GAMES_JS
        assert "${DR.skips} pases" not in GAMES_JS

    @pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
    def test_pase_singular_only_at_exactly_one(self):
        m = re.search(r"\$\{DR\.skips\} (\$\{DR\.skips===1\?'pase':'pases'\})", GAMES_JS)
        expr = m.group(1)[2:-1]
        js = "const out=[0,1,2,3].map(n=>{const DR={skips:n};return `${DR.skips} ${%s}`;});console.log(JSON.stringify(out));" % expr
        out = subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True).stdout
        assert json.loads(out) == ["0 pases", "1 pase", "2 pases", "3 pases"]


class TestNoNewTopLevelNames:
    def test_quiz_block_declares_only_the_known_top_level_names(self):
        quiz = TABS_JS[TABS_JS.index("let QZ=null;"):TABS_JS.index("function poolDatalist(){")]
        names = set(re.findall(r"^(?:function|const|let|var)\s+([A-Za-z_$][\w$]*)", quiz, flags=re.M))
        assert names == {"QZ", "statClue", "POS_ES", "posEs", "clueList", "newQuiz", "drawQuiz", "revealClue", "guessQuiz"}
