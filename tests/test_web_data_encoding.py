"""PHASE_66 fixup 2 -- no mojibake in the published data, and the display-only repair in
src/build_web_data.py behaves (touches only values with "Ã"/"Â", leaves failed round trips alone)."""

import re
from pathlib import Path

from src import build_web_data as b

ROOT = Path(__file__).parent.parent
# "Ã"/"Â" followed by a Latin-1 symbol is what UTF-8 text decoded as cp1252 looks like ("JosÃ©", "RubÃ©n").
MOJIBAKE = re.compile("[ÃÂ][ -¿]")


def test_no_mojibake_anywhere_in_web_data():
    bad = []
    for p in sorted((ROOT / "web/data").rglob("*.json")):
        m = MOJIBAKE.search(p.read_text(encoding="utf-8"))
        if m:
            bad.append(f"{p.relative_to(ROOT)}: ...{m.group(0)}...")
    assert bad == [], bad[:5]


def test_repair_fixes_only_broken_values_and_keeps_failed_round_trips(tmp_path, monkeypatch):
    (tmp_path / "t.csv").write_text(
        "name,note\n"
        '"GonzÃ¡lez, Javier",ok\n'      # broken -> fixed
        '"Lloreda, José Jaime",ok\n'     # already right -> untouched
        '"Ãx unchanged",ok\n'            # contains Ã but the round trip fails -> unchanged
        , encoding="utf-8")
    monkeypatch.setattr(b, "CLEAN", tmp_path)
    rows = b._read("t.csv")
    assert [r["name"] for r in rows] == ["González, Javier", "Lloreda, José Jaime", "Ãx unchanged"]
    assert all(r["note"] == "ok" for r in rows)


def test_build_revision_is_part_of_the_data_digest(tmp_path, monkeypatch):
    # The digest hashes input CSVs only; a build-step change (the mojibake repair) must still move it,
    # or cached clients keep the old web/data copy (DATA.syncVersion compares source_digest).
    (tmp_path / "f.csv").write_text("a\n1\n", encoding="utf-8")
    monkeypatch.setattr(b, "CLEAN", tmp_path)
    d1 = b._source_digest(["f.csv"])
    monkeypatch.setattr(b, "DIGEST_REVISION", b.DIGEST_REVISION + 1)
    assert b._source_digest(["f.csv"]) != d1
