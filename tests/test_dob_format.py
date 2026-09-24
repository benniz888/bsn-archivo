"""PHASE_DOB_FORMAT — archive DOBs render unambiguously (app/bsn_archivo.html, fmtArchiveDob/
_daysInMonth). Render-time only, no data/clean write; the raw M/D/YYYY string stays exactly as stored,
and every count/span/export elsewhere is untouched. Port of the two JS functions to Python, the same way
test_route_slugs.py ports slug(), so the real committed data can be checked without a browser; the
browser itself is checked separately (Playwright, three time zones -- see docs/session.md)."""

import csv
import re

import pytest

from src.wayback_cdx import REPO_ROOT

APP = REPO_ROOT / "app" / "bsn_archivo.html"
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
          "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

_PAT = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$")


def _days_in_month(y, m):
    """Port of _daysInMonth() in app/bsn_archivo.html: pure calendar arithmetic, no Date object."""
    d = [31, 29 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 28,
         31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return d[m - 1]


def fmt_archive_dob(raw):
    """Port of fmtArchiveDob() in app/bsn_archivo.html."""
    m = _PAT.match(str(raw or ""))
    if not m:
        return raw
    mo, da, yr = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if mo < 1 or mo > 12 or da < 1 or da > _days_in_month(yr, mo):
        return raw
    return f"{da} de {MESES[mo - 1]} de {yr}"


def _rd(name, folder="clean"):
    with (REPO_ROOT / "data" / folder / name).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


class TestFmtArchiveDobRule:
    def test_a_well_formed_date_is_reformatted(self):
        assert fmt_archive_dob("5/9/1980") == "9 de mayo de 1980"
        assert fmt_archive_dob("12/31/1999") == "31 de diciembre de 1999"
        assert fmt_archive_dob("1/1/2000") == "1 de enero de 2000"

    def test_no_leading_zero_padding_in_the_output(self):
        assert fmt_archive_dob("2/5/1975") == "5 de febrero de 1975"   # not "05 de febrero"

    def test_leap_day_is_valid_only_in_a_leap_year(self):
        assert fmt_archive_dob("2/29/2000") == "29 de febrero de 2000"   # divisible by 400 -- leap
        assert fmt_archive_dob("2/29/1980") == "29 de febrero de 1980"   # divisible by 4, not 100 -- leap
        assert fmt_archive_dob("2/29/1900") == "2/29/1900"               # divisible by 100, not 400 -- invalid
        assert fmt_archive_dob("2/29/1981") == "2/29/1981"               # not divisible by 4 -- invalid

    def test_a_calendar_invalid_date_falls_back_to_the_raw_string(self):
        assert fmt_archive_dob("2/30/1980") == "2/30/1980"
        assert fmt_archive_dob("13/1/1980") == "13/1/1980"
        assert fmt_archive_dob("4/31/1980") == "4/31/1980"

    def test_an_unparseable_or_empty_value_falls_back_unchanged(self):
        assert fmt_archive_dob("") == ""
        assert fmt_archive_dob(None) is None
        assert fmt_archive_dob("unknown") == "unknown"


class TestCommittedData:
    """Every real birth_date-shaped value in the repo, checked the same way (players_canonical.csv,
    jugador05_dob_conflicts.csv, player_dob_overrides.csv) -- the regression that fails loudly if a
    future edit ever introduces a day-first record (this fix's whole premise depends on there being
    none)."""

    def _all_date_values(self):
        vals = []
        for r in _rd("players_canonical.csv"):
            if r["birth_date"].strip():
                vals.append((r["bsnpr_id"], r["birth_date"]))
        for r in _rd("jugador05_dob_conflicts.csv", "interim"):
            vals.append((r["bsnpr_id"] + ":canonical", r["canonical_dob"]))
            vals.append((r["bsnpr_id"] + ":jugador05", r["jugador05_dob"]))
        for r in _rd("player_dob_overrides.csv", "interim"):
            vals.append((r["bsnpr_id"] + ":old", r["old_dob"]))
            if r["new_dob"]:
                vals.append((r["bsnpr_id"] + ":new", r["new_dob"]))
        return vals

    def test_2011_players_have_a_birth_date(self):
        assert sum(1 for _ in _rd("players_canonical.csv")) == 3326
        assert len([r for r in _rd("players_canonical.csv") if r["birth_date"].strip()]) == 2011

    def test_no_value_anywhere_has_a_first_component_over_12(self):
        # this is the fix's entire premise: M/D/YYYY only holds unambiguously if this is always 0
        vals = self._all_date_values()
        assert len(vals) > 2000   # sanity: the list actually has data
        bad = [(k, v) for k, v in vals if (m := _PAT.match(v)) and int(m.group(1)) > 12]
        assert bad == []

    def test_no_value_anywhere_is_calendar_invalid_as_month_day_year(self):
        vals = self._all_date_values()
        bad = [(k, v) for k, v in vals if fmt_archive_dob(v) == v and _PAT.match(v)]
        assert bad == []   # every well-formed M/D/YYYY value in the repo is also calendar-valid

    def test_no_sentinel_or_placeholder_dates_in_players_canonical(self):
        for r in _rd("players_canonical.csv"):
            v = r["birth_date"].strip()
            if not v:
                continue
            m = _PAT.match(v)
            assert m, (r["bsnpr_id"], v)
            yr = int(m.group(3))
            assert v != "1/1/1900" and 1900 <= yr <= 2026, (r["bsnpr_id"], v)


class TestAppWiring:
    def test_fmt_archive_dob_and_days_in_month_never_construct_a_date(self):
        text = APP.read_text(encoding="utf-8")
        block = text[text.index("function _daysInMonth"):text.index("function fmtArchiveDob(raw){") + 400]
        assert "new Date" not in block   # no timezone-dependent operation anywhere in the fix

    def test_the_bio_line_calls_fmt_archive_dob_on_b_date(self):
        text = APP.read_text(encoding="utf-8")
        assert "esc(fmtArchiveDob(b.date))" in text

    def test_the_web_copy_is_a_byte_copy(self):
        # PHASE_1_SPLIT STEP 2: web/index.html links css/main.css instead of inlining it, so the
        # reconstructed text (app_text()) is what has to match now, not the raw file.
        from tests._app_text import app_text
        assert app_text().encode("utf-8") == APP.read_bytes()
