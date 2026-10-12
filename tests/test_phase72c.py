"""PHASE_72C -- display-layer names (owner decision D2) and the Cruz / Morales clubs (D8).

The display layer (src/display_names.py, applied by src/build_web_data.py) changes what the generated
web/data/ shows as `player`; `player_raw`, data/clean and data/raw keep the source spelling. Browser checks
use tests/harness/phase72c_probe.mjs (skips without node + playwright-core).
"""
import csv
import glob
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from src import display_names as dn

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web/data"


# --- the casing table: one row per pattern found in the real data, plus the patterns the owner named ---
CASING = [
    # (raw, expected, pattern)
    ("ADOLFO PORRATA", "Adolfo Porrata", "plain first-last"),
    ("RAUL FELICIANO", "Raul Feliciano", "no accent is invented"),
    ("HECTOR NUÑEZ", "Hector Nuñez", "source accent (Ñ) is kept and lower-cased"),
    ("GEÑITO JIMENEZ", "Geñito Jimenez", "source accent in the first name"),
    ("RUBEN MONTAÑEZ", "Ruben Montañez", "source accent in the surname"),
    ("HÉCTOR NÚÑEZ", "Héctor Núñez", "accented capitals"),
    ("JOSE DE LA ROSA", "Jose de la Rosa", "particles de la"),
    ("ANGEL DE JESUS", "Angel de Jesus", "particle de"),
    ("TEO CRUZ Y BILL McCADNEY", "Teo Cruz y Bill McCadney", "particle y and an internal-caps surname"),
    ("BILL McCADNEY", "Bill McCadney", "mixed-case McCADNEY"),
    ("MARIO MCDONALD", "Mario McDonald", "Mc prefix"),
    ("KEVIN MACDONALD", "Kevin MacDonald", "Mac prefix, explicit list"),
    ("RAFAEL MACHADO", "Rafael Machado", "Mac is NOT a prefix in Machado (real data)"),
    ("JOHN SMITH JR", "John Smith Jr.", "Jr"),
    ("JOHN SMITH SR.", "John Smith Sr.", "Sr."),
    ("JOHN SMITH II", "John Smith II", "II"),
    ("JOHN SMITH III", "John Smith III", "III"),
    ("PATRICK O'BRYANT", "Patrick O'Bryant", "apostrophe after one letter"),
    ("IVAN GANDIA-ROSA", "Ivan Gandia-Rosa", "hyphen"),
    ("JOSE A. CAMPOS", "Jose A. Campos", "initial with a period"),
    ("RIVERA, JOSE", "Rivera, Jose", "Last, First order"),
    ("JOSE LUIS RIVERA", "Jose Luis Rivera", "two given names"),
    ("JUAN ‘PACHIN’ VICENS", "Juan «Pachin» Vicens", "curly nickname quotes"),
    ('JOSE "PICULIN" ORTIZ', "Jose «Piculin» Ortiz", "straight double quotes"),
    ("ALEJANDO 'BIMBO' CARMONA", "Alejando «Bimbo» Carmona", "straight single quotes; the typo is NOT touched"),
    ("MARIANO ‘TITO’ORTIZ", "Mariano «Tito» Ortiz", "missing space after the nickname"),
    ("MARIO ‘QUIJOTE’MORALES", "Mario «Quijote» Morales", "missing space after the nickname"),
    ("JAVIER ‘TOÑITO’ COLON", "Javier «Toñito» Colon", "accent inside a nickname"),
    ("MARIO ‘QUIJOTE’ MORALES", "Mario «Quijote» Morales", "nickname with spaces"),
    # left exactly as the source printed them
    ("NO FUE SELECCIONADO", "NO FUE SELECCIONADO", "not a name"),
    ("Rhett, MJ", "Rhett, MJ", "initials in a mixed-case name"),
    ("De Jesus", "De Jesus", "mixed case is kept"),
    ("Butler, Mario Albe", "Butler, Mario Albe", "truncated, no linked id"),
    ("Morales, Mario 'Qui", "Morales, Mario 'Qui", "truncated nickname, no linked id"),
    ("Maura, Kevin 'K.J", "Maura, Kevin 'K.J", "truncated nickname is not recased"),
    ("Alicea", "Alicea", "surname only, no linked id"),
    ("Casian0", "Casian0", "an unevidenced typo is not fixed"),
    ("ELIAS AYUSO", "ELIAS AYUSO", "Ayuso is not touched (D2)"),
    ("Ayuso, Elias 'Lar", "Ayuso, Elias 'Lar", "Ayuso is not touched (D2)"),
]


@pytest.mark.parametrize("raw,expected,pattern", CASING, ids=[c[2] for c in CASING])
def test_casing_table(raw, expected, pattern):
    assert dn.display_name(raw) == expected


def _real_names():
    """Every ALL-CAPS name the source tables carry (data/clean), not a sample."""
    names = set()
    for f, col in (("historic_awards.csv", "player_raw"), ("historic_scoring_champions.csv", "player_raw"),
                   ("scoring_champions_reconciled.csv", "historic_player"), ("scoring_champions_reconciled.csv", "seed_player")):
        with (ROOT / "data/clean" / f).open(encoding="utf-8", newline="") as fh:
            names |= {r[col] for r in csv.DictReader(fh) if r.get(col)}
    return {n for n in names if dn.is_all_caps(n) or re.search(r"\bMc[A-Z]{2}", n)}


def test_every_real_all_caps_name_is_cased_without_losing_a_letter():
    names = _real_names()
    assert len(names) >= 100
    for raw in sorted(names):
        shown = dn.display_name(raw)
        if raw in dn.NON_NAMES or dn.AYUSO.search(raw):
            assert shown == raw
            continue
        if raw in dn.OVERRIDES:
            continue
        letters = lambda s: re.sub(r"[^a-zñáéíóúü]", "", s.lower())
        assert letters(shown) == letters(raw), (raw, shown)                     # nothing added, dropped or respelled
        assert not re.search(r"[‘’“”\"]", shown), (raw, shown)
        for tok in re.findall(r"[^\W\d_]+", shown):
            assert tok in ("II", "III", "IV") or not (len(tok) > 1 and tok.isupper()), (raw, shown)


def test_particles_are_lower_case_after_the_first_word():
    assert dn.display_name("JOSE DE LA ROSA").split()[1:3] == ["de", "la"]
    assert dn.display_name("DE LA ROSA, JOSE").startswith("De la")


# --- overrides: one entry per name, each with its source row ---
class TestOverrides:
    def test_only_evidenced_entries_exist(self):
        assert dn.OVERRIDES == {"GOERGIE TORRES": "Georgie Torres"}

    def test_every_entry_has_a_comment_citing_a_source_row(self):
        src = (ROOT / "src/display_names.py").read_text(encoding="utf-8")
        block = src[src.index("OVERRIDES: dict"):src.index("# Left alone")]
        for raw in dn.OVERRIDES:
            before = block[:block.index(f'"{raw}"')]
            assert re.search(r"# data/clean/\w+\.csv:\d+", before), raw

    def test_evidence_rows_exist_in_the_clean_data(self):
        rows = list(csv.DictReader((ROOT / "data/clean/historic_awards.csv").open(encoding="utf-8", newline="")))
        mvp = {r["season"]: r for r in rows if r["award"] == "mvp"}
        assert mvp["1986"]["player_raw"] == "GOERGIE TORRES"
        assert mvp["1985"]["player_raw"] == mvp["1984"]["player_raw"] == "GEORGIE TORRES"
        assert mvp["1986"]["team_raw"] == mvp["1985"]["team_raw"] == "FAJARDO"


# --- truncated / surname-only: expanded only through an already-linked id ---
class TestExpansion:
    def test_surname_only_expands_with_a_linked_consistent_id(self):
        assert dn.display_name("Hatton", "Hatton Negron, Roberto Jose") == "Hatton Negron, Roberto Jose"

    def test_truncated_expands_with_a_linked_consistent_id(self):
        assert dn.display_name("Morales, Mario 'Qui", "Morales Micheo, Mario") == "Morales Micheo, Mario"
        assert dn.display_name("Santos, William \"b", "Santos Alvarez, William") == "Santos Alvarez, William"

    def test_an_inconsistent_canonical_name_is_ignored(self):
        assert dn.display_name("Hatton", "Dalmau Santana, Christian") == "Hatton"
        assert dn.display_name("Morales, Mario 'Qui", "Cruz Rosario, Angel") == "Morales, Mario 'Qui"

    def test_no_id_no_change(self):
        assert dn.display_name("Butler, Mario Albe") == "Butler, Mario Albe"
        assert dn.display_name("Alicea") == "Alicea"

    def test_a_complete_name_is_never_replaced_by_its_canonical_form(self):
        assert dn.display_name("Butler, Mario", "Butler Graham, Mario Alberto") == "Butler, Mario"

    def test_ayuso_is_never_touched(self):
        assert dn.display_name("Ayuso, Elias 'Lar", "Ayuso Carrillo, Elias") == "Ayuso, Elias 'Lar"
        assert dn.display_name("Ayuso", "Ayuso Carrillo, Elias") == "Ayuso"


# --- what the build wrote ---
def _season_records():
    for f in sorted(glob.glob(str(WEB / "seasons/*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        recs = list(d.get("awards") or []) + [x for l in (d.get("leaders") or {}).values() for x in l]
        if d.get("scoring_champion"):
            recs.append(d["scoring_champion"])
        for r in recs:
            yield d["season"], r


class TestBuildOutput:
    def test_player_is_written_only_where_it_differs_and_raw_is_preserved(self):
        changed = 0
        for _s, r in _season_records():
            assert r["player_raw"]
            if "player" in r:
                assert r["player"] != r["player_raw"]
                changed += 1
        assert changed == 250

    def test_source_spellings_in_the_season_files_are_exactly_the_clean_data(self):
        clean = set()
        for f in ("historic_awards.csv", "historic_scoring_champions.csv", "player_season_leaders.csv", "player_season_leaders_2000_2002.csv"):
            with (ROOT / "data/clean" / f).open(encoding="utf-8", newline="") as fh:
                clean |= {r["player_raw"] for r in csv.DictReader(fh)}
        assert {r["player_raw"] for _s, r in _season_records()} <= clean

    def test_1986_goergie_is_shown_as_georgie_and_the_source_is_kept(self):
        d = json.load(open(WEB / "seasons/1986.json", encoding="utf-8"))
        mvp = next(a for a in d["awards"] if a["award"] == "mvp")
        assert (mvp["player_raw"], mvp["player"]) == ("GOERGIE TORRES", "Georgie Torres")

    def test_truncated_leader_names_expand_only_with_a_linked_id(self):
        d = json.load(open(WEB / "seasons/1986.json", encoding="utf-8"))
        names = {x["player_raw"]: x.get("player") for l in d["leaders"].values() for x in l}
        assert names["Morales, Mario 'Qui"] == "Morales Micheo, Mario"
        assert names["Butler, Mario Albe"] is None                  # no linked id: left as printed

    def test_ayuso_rows_are_untouched_everywhere(self):
        seen = 0
        for _s, r in _season_records():
            if re.search(r"ayuso", r["player_raw"], re.I):
                seen += 1
                assert "player" not in r
        assert seen > 0
        for f in ("mvp", "scoring_titles"):
            blob = (WEB / f"index/{f}.json").read_text(encoding="utf-8")
            for m in re.finditer(r'"player":"([^"]*[Aa][Yy][Uu][Ss][Oo][^"]*)","player_raw":"([^"]*)"', blob):
                assert m.group(1) == m.group(2)

    def test_mvp_index_uses_the_display_layer(self):
        mvp = {r["season"]: r for r in json.load(open(WEB / "index/mvp.json", encoding="utf-8"))}
        assert mvp[1983]["player"] == "Mario «Quijote» Morales" and mvp[1983]["player_raw"] == "MARIO ‘QUIJOTE’MORALES"
        assert mvp[1986]["player"] == "Georgie Torres" and mvp[1986]["player_raw"] == "GOERGIE TORRES"
        assert mvp[2002]["player"] == "Jose «Piculin» Ortiz"

    def test_scoring_titles_carry_both_spellings(self):
        st = json.load(open(WEB / "index/scoring_titles.json", encoding="utf-8"))
        s48 = next(r for r in st if r["season"] == 1948)["champion"]
        assert (s48["player"], s48["player_raw"]) == ("Raul Feliciano", "RAUL FELICIANO")

    def test_the_digest_covers_the_display_module(self):
        src = (ROOT / "src/build_web_data.py").read_text(encoding="utf-8")
        assert "display_names.py" in src.split("def _source_digest")[1].split("def ")[0]


class TestRawAndCleanUntouched:
    def test_display_module_never_writes(self):
        src = (ROOT / "src/display_names.py").read_text(encoding="utf-8")
        assert not re.search(r"open\(|write_text|write_bytes|_write_csv|\.unlink", src)

    @pytest.mark.skipif(shutil.which("git") is None, reason="git not available")
    def test_data_raw_and_data_clean_have_no_uncommitted_change(self):
        out = subprocess.run(["git", "status", "--porcelain", "--", "data/raw", "data/clean"], cwd=ROOT,
                             capture_output=True, text=True)
        assert out.returncode == 0 and out.stdout.strip() == ""


# --- D8: Cruz and Morales ---
class TestCruzMorales:
    DATA = (ROOT / "web/js/data.js").read_text(encoding="utf-8")

    def test_morales_has_both_clubs_the_rows_support_and_no_other(self):
        assert '{n:"Mario Morales",d:[1970,1980,1990],c:["san","gua"],' in self.DATA
        mvp = {r["season"]: r for r in json.load(open(WEB / "index/mvp.json", encoding="utf-8"))}
        assert [mvp[y]["franchise_id"] for y in (1980, 1982, 1983, 1993)] == ["mets_guaynabo"] * 4
        sc = {r["season"]: r["champion"] for r in json.load(open(WEB / "index/scoring_titles.json", encoding="utf-8")) if r["champion"]}
        assert sc[1993]["franchise_id"] == "mets_guaynabo" and sc[1980]["franchise_id"] == "cangrejeros_santurce"

    def test_cruz_keeps_the_one_club_his_rows_support_and_stays_held(self):
        assert '{n:"Teófilo Cruz",d:[1950,1960,1970,1980],c:["san"],' in self.DATA
        tabs = (ROOT / "web/js/tabs.js").read_text(encoding="utf-8")
        assert "'teofilo|cruz':1" in tabs
        mvp = {r["season"]: r for r in json.load(open(WEB / "index/mvp.json", encoding="utf-8"))}
        assert {mvp[y]["franchise_id"] for y in (1962, 1967, 1970, 1971)} == {"cangrejeros_santurce"}


# --- the browser ---
@pytest.fixture(scope="module")
def probe():
    node = shutil.which("node")
    env = os.environ.get("PLAYWRIGHT_CORE")
    hits = sorted(glob.glob("/private/tmp/**/node_modules/playwright-core/index.js", recursive=True))
    core = env if env and (Path(env) / "index.js").exists() else (str(Path(hits[0]).parent) if hits else None)
    if not node or not core:
        pytest.skip("needs node and playwright-core (set PLAYWRIGHT_CORE=<dir>)")
    res = subprocess.run([node, str(ROOT / "tests/harness/phase72c_probe.mjs")],
                         env={**os.environ, "PLAYWRIGHT_CORE": core}, capture_output=True, text=True, timeout=180)
    assert res.returncode == 0, res.stderr[-2000:]
    out = json.loads(res.stdout)
    assert out["pageErrors"] == [], out["pageErrors"]
    return out


class TestBrowser:
    def test_search_finds_the_player_by_either_spelling(self, probe):
        assert probe["searchCorrected"] is True
        assert probe["searchOriginal"] is True          # "goergie": the spelling the archive printed
        assert probe["searchCaps"] is True
        assert probe["searchNone"] is False

    def test_season_detail_shows_the_display_names(self, probe):
        t = probe["season1986"]
        assert "Georgie Torres" in t and "GOERGIE" not in t and "GEORGIE TORRES" not in t
        assert "Morales Micheo, Mario" in t or "Butler, Mario Albe" in t

    def test_premios_scoring_table_and_hydrated_scoring_rows(self, probe):
        assert "Raul Feliciano" in probe["scoringTable"] and "RAUL FELICIANO" not in probe["scoringTable"]
        assert probe["scoring1948"] == [1948, "Raul Feliciano"]

    def test_leaders_table_still_renders(self, probe):
        assert "Georgie Torres" in probe["leaders"]

    def test_clubs(self, probe):
        assert probe["moralesClubs"] == ["san", "gua"] and probe["cruzClubs"] == ["san"]
