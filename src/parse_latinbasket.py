"""PHASE_9 T9.1 — parse latinbasket.com standings pages into
`data/clean/standings.csv`, the archive's first team-level standings file.

Reads `data/raw/latinbasket/<season>.html` (`src/fetch_latinbasket.py`,
Wayback-only — see that module's docstring + B5 in `docs/session.md` for
why the live site is never touched). Only the pre-redesign `.asp` template
is server-rendered; the newer `.aspx` template's standings load via
`/js/standings.js` client-side and the raw capture has no table at all
(checked, not assumed — 2019/2020/2022 captures parse to zero rows). Those
three seasons plus 2021/2023 (no capture exists) are real, disclosed gaps
in `data/clean/standings.csv` (PC4) — never backfilled from the live site.

Table anchor: each standings widget on the page is `<table class="ctrtbl">`
with a `<td class="ctrtd">` header ("BSN Standings", or "BSN Stage One/Two
Standings" for a multi-stage season like 2018) immediately followed by the
data rows — `<a href=".../team/Puerto-Rico/<Team>/<id>?Year=YYYY">City</a>`
next to a "W-L" record. Anchoring on the header text (not just "any table
with a team link") matters: 2018's page also carries small Home/Road split
tables using the same row shape, which a header-blind regex pass picks up
by accident (verified this the hard way — an early draft of this parser
grabbed a 3-team home/away fragment before the header anchor was added).

Cross-validated, not just assumed correct: 2016's extracted table
(Bayamon 21-15, Santurce 21-15, ...) matches Wikipedia's independently-
sourced 2016 standings exactly; 2018 Stage One matches Wikipedia's 2018
Stage One table exactly, position-for-position.

Run: `python -m src.parse_latinbasket` (after `python -m src.fetch_latinbasket`)
"""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from bs4 import BeautifulSoup

from src.wayback_cdx import REPO_ROOT
from src.parse_wayback import _write_csv

RAW_DIR = REPO_ROOT / "data" / "raw" / "latinbasket"
CITY_MAP_PATH = REPO_ROOT / "data" / "clean" / "city_franchise_map.csv"
OUT_PATH = REPO_ROOT / "data" / "clean" / "standings.csv"
GAPS_PATH = REPO_ROOT / "data" / "clean" / "standings_coverage_gaps.csv"

FIELDS = ["season", "franchise_id", "city_raw", "stage", "position", "wins", "losses",
          "note", "confidence", "source_id", "source_url", "retrieved_at", "capture_date"]

REC_RE = re.compile(r"(\d{1,2})\.\s*[^0-9]*?(\d{1,3})-(\d{1,3})")

# Header substrings to extract, per season, in the order the resulting rows
# should carry a `stage` label. Every season not listed here uses the
# single-table default ("BSN Standings", stage=None).
MULTI_STAGE = {
    "2018": [("BSN Stage One Standings", "stage1"), ("BSN Stage Two Standings", "stage2")],
}

# Cities the parser will see that need a hand-verified, non-default read.
# ISABELA (2017 only): player_career_seasons.csv already carries this
# season's Humacao roster under the hybrid label "Caciques-Gallitos,
# Humacao-Isabela" (a pre-existing, unresolved ambiguity — see D-046 notes
# on bare "Grises" club resolution). franchise_events.csv's own verified
# caciques_humacao row states the franchise "later relocated away from
# Humacao (Isabela, then Guayama, ~2019)" — read here as caciques_humacao
# having relocated to Isabela for this season, not the separate
# `gallitos_isabela` franchise. Flagged `disputed`, not `verified` — this
# is an inference from an existing note, not a fresh independent source
# (PC3's confidence enum has no "inferred" tier; `disputed` is the honest
# fit — two plausible franchise reads exist for this one row).
CITY_OVERRIDES = {
    ("2017", "ISABELA"): ("caciques_humacao", "disputed",
        "2017 Isabela reads as caciques_humacao mid-relocation (per franchise_events.csv's "
        "'later relocated away from Humacao (Isabela, then Guayama, ~2019)' note), not the "
        "separate gallitos_isabela franchise -- inferred from an existing verified note, not "
        "independently sourced this pass. Matches the pre-existing 'Caciques-Gallitos, "
        "Humacao-Isabela' hybrid label already in player_career_seasons.csv for this season."),
    # city_franchise_map.csv's MANATI -> osos_manati mapping is era-blind (its
    # own note already flags this: "Atenienses 2014-17 then Osos 2022+ --
    # verify per season"). osos_manati is the real but *different* 2023+
    # Guayama relocation; the 2015/2016 latinbasket captures are Atenienses
    # de Manati, a separate, real, defunct-2017 franchise (franchises.csv).
    # Found + logged 2026-09-14 during backlog item 7 Phase A scoping,
    # fixed here in Phase D since this pass already touches this exact
    # franchise's data.
    ("2015", "MANATI"): ("atenienses_manati", "single-source",
        "city_franchise_map.csv's MANATI->osos_manati mapping is era-blind; this capture is "
        "Atenienses de Manati (2014-2017), not the unrelated 2023+ Osos de Manati relocation."),
    ("2016", "MANATI"): ("atenienses_manati", "single-source",
        "city_franchise_map.csv's MANATI->osos_manati mapping is era-blind; this capture is "
        "Atenienses de Manati (2014-2017), not the unrelated 2023+ Osos de Manati relocation."),
}


def _load_city_map() -> dict[str, str]:
    with CITY_MAP_PATH.open(encoding="utf-8") as fh:
        return {r["normalized_city"]: r["franchise_id"] for r in csv.DictReader(fh)}


_GROUP_RE = re.compile(r"^Group\s+([A-Z])$", re.IGNORECASE)


def _extract_table(soup: BeautifulSoup, header_substr: str) -> list[tuple[int, str, int, int, str | None]]:
    """Returns (position, city, wins, losses, group) per row, in document
    order. `group` is None unless the table has an internal "Group A" /
    "Group B" divider row (2018 Stage Two) — walking rows in order (not
    just collecting every team link under the header) is what lets a
    divider between two same-numbered groups be told apart."""
    for td in soup.find_all("td", class_="ctrtd"):
        if header_substr.lower() not in td.get_text(strip=True).lower():
            continue
        outer = td.find_parent("table")
        if outer is None:
            continue
        rows, seen, group = [], set(), None
        for tr in outer.find_all("tr"):
            if tr.find("table") is not None:
                continue  # a structural wrapper row, not a data row -- its
                          # nested <table> supplies its own <tr>s separately,
                          # and .get_text() on the wrapper concatenates every
                          # descendant row's text into one, which would
                          # otherwise false-match both the group divider and
                          # the first data row's team link/record.
            gm = _GROUP_RE.match(tr.get_text(strip=True))
            if gm:
                group = gm.group(1).lower()
                continue
            a = tr.find("a", href=lambda h: h and "/team/Puerto-Rico/" in h)
            if a is None:
                continue
            name = a.get_text(strip=True)
            key = (group, name)
            if key in seen:
                continue
            m = REC_RE.search(tr.get_text(" ", strip=True))
            if not m:
                continue
            seen.add(key)
            rows.append((int(m.group(1)), name, int(m.group(2)), int(m.group(3)), group))
        return rows
    return []


def parse_season(season: str, html_path: Path, meta: dict, city_map: dict[str, str]) -> list[dict]:
    soup = BeautifulSoup(html_path.read_text(errors="replace"), "lxml")
    retrieved_at = datetime.fromtimestamp(
        html_path.with_name(html_path.name.replace(".html", ".meta.json")).stat().st_mtime,
        tz=timezone.utc,
    ).strftime("%Y-%m-%dT%H:%M:%SZ")
    ts = meta.get("timestamp", "")
    capture_date = f"{ts[0:4]}-{ts[4:6]}-{ts[6:8]}" if len(ts) >= 8 else ""

    headers = MULTI_STAGE.get(season, [("BSN Standings", None)])
    out = []
    for header, stage in headers:
        for position, city_raw, wins, losses, group in _extract_table(soup, header):
            row_stage = f"{stage}_{group}" if stage and group else stage
            city_key = city_raw.strip().upper()
            override = CITY_OVERRIDES.get((season, city_key))
            if override:
                franchise_id, confidence, note = override
            else:
                franchise_id = city_map.get(city_key, "")
                confidence = "single-source" if franchise_id else "disputed"
                note = "" if franchise_id else f"unmapped city '{city_raw}' -- not in city_franchise_map.csv"
            out.append({
                "season": season, "franchise_id": franchise_id, "city_raw": city_raw,
                "stage": row_stage or "", "position": position, "wins": wins, "losses": losses,
                "note": note, "confidence": confidence,
                "source_id": "wayback_latinbasket", "source_url": meta.get("raw_wayback_url", ""),
                "retrieved_at": retrieved_at, "capture_date": capture_date,
            })
    return out


def main() -> int:
    city_map = _load_city_map()
    rows: list[dict] = []
    gaps: list[dict] = []

    manifest_path = REPO_ROOT / "data" / "interim" / "fetch_manifest_latinbasket.csv"
    with manifest_path.open(encoding="utf-8") as fh:
        manifest = list(csv.DictReader(fh))

    for m in manifest:
        season = m["season"]
        if m["status"] != "ok":
            gaps.append({"season": season, "reason": m["status"] or "no_capture"})
            continue
        html_path = RAW_DIR / f"{season}.html"
        meta_path = RAW_DIR / f"{season}.meta.json"
        meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
        season_rows = parse_season(season, html_path, meta, city_map)
        if not season_rows:
            gaps.append({"season": season, "reason": "captured_but_no_server_rendered_table"})
            continue
        rows.extend(season_rows)

    _write_csv(OUT_PATH, rows, FIELDS)
    _write_csv(GAPS_PATH, gaps, ["season", "reason"])
    print(f"[latinbasket] {len(rows)} standings rows across "
          f"{len({r['season'] for r in rows})} seasons; {len(gaps)} season gaps -> {GAPS_PATH.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
