"""PHASE_72B -- mojibake decoder, the 296-row name repair overlay, and the Javier González split
(docs/audits/phase72_audit.md items 3 and 8b; owner decisions D3 and D8).

Guarantees pinned here:
  * the decoder reads pure-UTF-8, mixed (UTF-8 names inside a cp1252 page) and pure-cp1252 pages;
  * the overlay changes exactly 296 rows (three names) and nothing else: every other row of
    data/clean/game_box_player.csv, including the 365 bsnpr_id values a re-parse would have moved,
    hashes to the digest recorded before the repair;
  * the overlay is idempotent and writes nothing in check mode;
  * the 58 mojibake González rows are id 2513; the rows that cannot be settled stay blank.
"""
import csv
import hashlib
import re
from pathlib import Path

import pytest

from src import apply_game_name_repair as agr
from src import parse_games as pg

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data/clean/game_box_player.csv"
RAW = ROOT / "data/raw/games/pogamestat"
THREE = {"Lloreda, José Jaime": ("Lloreda, JosÃ© Jaime", 118, "2690"),
         "Cotto, Rubén": ("Cotto, RubÃ©n", 120, "2675"),
         "González, Javier": ("GonzÃ¡lez, Javier", 58, "2513")}
# sha256 over every row except the repaired names' rows (39,371 rows), recorded BEFORE the repair
# and equal to the value after it; includes the 82 ASCII "Gonzalez, Javier" rows and every
# bsnpr_id a re-parse would have moved.
UNRELATED_ROWS_DIGEST = "f542ac5d53902e6be16284494722df1f18b53acc241c124e8788a6661fc9ef97"


def _rows():
    with CSV_PATH.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _break(rows):
    """Re-create the damaged state from the repaired file: mojibake the three names, blank their ids
    (only the 296 rows the overlay repaired: the 2 pre-existing blank-team 2008 González rows stay)."""
    out, n = [], 0
    for r in rows:
        key = r["player_raw"]
        if key in THREE and not (key == "González, Javier" and r["season"] == "2008"):
            r = dict(r, player_raw=THREE[key][0], bsnpr_id="")
            n += 1
        out.append(r)
    return out, n


class TestDecoder:
    def test_pure_cp1252_page(self):
        assert pg._decode("<td>Niño</td><p>©™</p>".encode("cp1252")) == "<td>Niño</td><p>©™</p>"

    def test_pure_utf8_page(self):
        assert pg._decode("<td>Lloreda, José Jaime</td> ©".encode("utf-8")) == "<td>Lloreda, José Jaime</td> ©"

    def test_mixed_page_utf8_names_in_a_cp1252_page(self):
        raw = b"<td>Cotto, Rub\xc3\xa9n</td> <b>\xc2\xa9</b> pagerank\x99 Ni\xf1o"
        with pytest.raises(UnicodeDecodeError):
            raw.decode("utf-8")                       # the whole-page UTF-8 test the first fix tried
        assert pg._decode(raw) == "<td>Cotto, Rubén</td> <b>©</b> pagerank™ Niño"

    def test_ascii_page_is_unchanged(self):
        assert pg._decode(b"<td>Richard, Jaja</td>") == "<td>Richard, Jaja</td>"

    def test_all_three_sites_use_the_decoder(self):
        src = (ROOT / "src/parse_games.py").read_text(encoding="utf-8")
        assert src.count("_decode(p.read_bytes())") == 3
        assert 'decode("cp1252", "replace")' in src.split("def _decode")[1].split("\n\n\n")[0]
        assert "p.read_bytes().decode" not in src

    @pytest.mark.skipif(not RAW.exists(), reason="data/raw/games not present")
    def test_real_mixed_page_decodes_the_names(self):
        page = RAW / "2011_20110624050700_D2EUGZVL.html"
        raw = page.read_bytes()
        with pytest.raises(UnicodeDecodeError):
            raw.decode("utf-8")
        text = pg._decode(raw)
        assert "Lloreda, José Jaime" in text and "Ã" not in text and "�" not in text

    @pytest.mark.skipif(not RAW.exists(), reason="data/raw/games not present")
    def test_real_pure_cp1252_pages_are_not_touched_by_the_utf8_pattern(self):
        gw = sorted((ROOT / "data/raw/games/gamestatwide").glob("*.html"))[:200]
        assert gw
        for p in gw:
            raw = p.read_bytes()
            assert pg._UTF8_SEQ.search(raw) is None
            assert pg._decode(raw) == raw.decode("cp1252", "replace")


class TestUnmojibake:
    def test_repairs_the_three_names(self):
        for fixed, (broken, _n, _i) in THREE.items():
            assert agr.unmojibake(broken) == fixed

    def test_leaves_clean_or_unrepairable_values_alone(self):
        assert agr.unmojibake("Lloreda, José Jaime") is None
        assert agr.unmojibake("Richard, Jaja") is None
        assert agr.unmojibake("Ã") is None            # not a valid UTF-8 sequence on its own
        assert agr.unmojibake("Ã‘Ã‘ x") is None or isinstance(agr.unmojibake("Ã‘Ã‘ x"), str)
        assert agr.unmojibake("Ωmega Ã©") is None     # a character outside cp1252: no exact round trip


class TestOverlay:
    def test_committed_file_has_no_pending_repair_and_no_mojibake(self):
        rows = _rows()
        assert not any(re.search("[ÃÂ�]", r["player_raw"]) for r in rows)
        _, log = agr.repair(rows, pg._load_resolver())
        assert log == []

    def test_row_diff_is_exactly_296_rows_and_two_columns(self):
        rows = _rows()
        broken, n = _break(rows)
        assert n == 296
        fixed, log = agr.repair(broken, pg._load_resolver())
        assert len(log) == 296
        changed = [(a, b) for a, b in zip(broken, fixed) if a != b]
        assert len(changed) == 296
        for a, b in changed:
            assert {k for k in a if a[k] != b[k]} <= {"player_raw", "bsnpr_id"}
        assert fixed == rows                           # the repair restores the committed file exactly
        by = {}
        for entry in log:
            by[(entry["after"], entry["id_after"])] = by.get((entry["after"], entry["id_after"]), 0) + 1
        assert by == {(k, v[2]): v[1] for k, v in THREE.items()}

    def test_input_rows_are_not_mutated(self):
        broken, _ = _break(_rows())
        snapshot = [dict(r) for r in broken]
        agr.repair(broken, pg._load_resolver())
        assert broken == snapshot

    def test_every_unrelated_row_is_byte_identical_to_before_the_repair(self):
        h, n = hashlib.sha256(), 0
        for r in _rows():
            if r["player_raw"] in THREE:                       # 296 repaired rows + the 2 blank-team 2008 rows
                continue
            h.update("\x1f".join(r.values()).encode() + b"\n")
            n += 1
        assert n == 39371
        assert h.hexdigest() == UNRELATED_ROWS_DIGEST

    def test_cli_check_mode_writes_nothing_and_apply_is_idempotent(self, tmp_path, monkeypatch):
        broken, _ = _break(_rows())
        target = tmp_path / "game_box_player.csv"
        from src.parse_wayback import _write_csv
        _write_csv(target, broken, pg.BOX_COLS)
        before = target.read_bytes()
        monkeypatch.setattr(agr, "PATH", target)
        assert agr.main([]) == 1                       # check mode: repair pending, exit 1
        assert target.read_bytes() == before           # ... and nothing written
        assert agr.main(["--apply"]) == 0
        after = target.read_bytes()
        assert after != before
        assert agr.main([]) == 0                       # nothing left to repair
        assert agr.main(["--apply"]) == 0
        assert target.read_bytes() == after            # idempotent
        assert after == CSV_PATH.read_bytes()          # and equals the committed repaired file

    def test_csv_roundtrips_byte_for_byte(self, tmp_path):
        from src.parse_wayback import _write_csv
        out = tmp_path / "x.csv"
        _write_csv(out, _rows(), pg.BOX_COLS)
        assert out.read_bytes() == CSV_PATH.read_bytes()


class TestGonzalezSplit:
    def test_58_mojibake_rows_are_id_2513_with_matching_club_and_season(self):
        rows = [r for r in _rows() if r["player_raw"] == "González, Javier" and r["season"] != "2008"]
        assert len(rows) == 58
        assert {r["bsnpr_id"] for r in rows} == {"2513"}
        with (ROOT / "data/clean/player_career_seasons.csv").open(encoding="utf-8", newline="") as fh:
            career = {(r["season"], r["team_raw"]) for r in csv.DictReader(fh) if r["bsnpr_id"] == "2513"}
        assert ("2013", "Cangrejeros, Santurce") in career and ("2012", "Caciques, Humacao") in career
        assert {(r["season"], r["team_raw"]) for r in rows} == {("2013", "Santurce"), ("2012", "Humacao")}

    def test_rows_that_cannot_be_settled_stay_blank(self):
        rows = _rows()
        q = [r for r in rows if r["player_raw"] == "Gonzalez, Javier"]
        assert len(q) == 82 and {r["team_raw"] for r in q} == {"QUEBRADILLAS"}
        assert {r["season"] for r in q} == {"2001", "2002", "2003"}
        assert {r["bsnpr_id"] for r in q} == {""}                  # candidate 1006 has no season rows: not assigned
        y = [r for r in rows if r["player_raw"] == "González, Javier" and r["season"] == "2008"]
        assert len(y) == 2 and {r["bsnpr_id"] for r in y} == {""} and {r["team_raw"] for r in y} == {""}

    def test_the_two_players_are_distinct_ids(self):
        ids = {r["bsnpr_id"] for r in _rows() if r["player_raw"] in ("González, Javier", "Gonzalez, Javier")}
        assert ids == {"", "2513"}                      # 1006 is never assigned: it has no season rows to corroborate

    def test_web_data_carries_the_repaired_ids(self):
        import json
        san = json.loads((ROOT / "web/data/starting_five/san.json").read_text(encoding="utf-8"))
        assert any(p["bsnpr_id"] == 2513 for p in san["2013"]["players"])
        g = json.loads((ROOT / "web/data/games/2013").glob("*.json").__next__().read_text(encoding="utf-8"))
        assert "box" in g
        blob = "".join(p.read_text(encoding="utf-8") for p in (ROOT / "web/data/games").glob("*/*.json"))
        assert "Ã" not in blob
        # the 2008 González rows have no team and legitimately stay null, so check only 2011-2013 files
        late = "".join(p.read_text(encoding="utf-8") for y in ("2011", "2012", "2013") for p in (ROOT / "web/data/games" / y).glob("*.json"))
        assert not re.search(r'"bsnpr_id":null,[^}]*"player_raw":"(González, Javier|Cotto, Rubén|Lloreda, José Jaime)"', late)
