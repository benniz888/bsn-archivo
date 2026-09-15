"""Backlog item 7, Phase A — fetch archived latinbasket.com BSN team-roster
pages (`basketball.latinbasket.com/team/Puerto-Rico/<Slug>/<id>?Year=YYYY`).

Wayback-only, same B5 discipline as `fetch_latinbasket.py` (standings):
latinbasket.com's `robots.txt` names ClaudeBot explicitly under
`Disallow: /`; only archived Wayback captures are fetched, never the live
site, never with a spoofed UA.

**Real, non-obvious finding from scoping this fetcher (2026-09-14):**
latinbasket's own numeric team ids are NOT a reliable franchise identity
signal — the site reuses an id across two completely unrelated real
franchises once one folds. Confirmed directly from CDX timestamps:
  - id `1976`: "Maratonistas_de_Coamo" captures 2013-2015, then
    "Santeros-de-Aguada" captures 2016-2019 on the *same id* — Coamo folded
    (`franchises.csv`: defunct 2015) and Aguada's slot was assigned the
    freed id. Two unrelated real franchises, not a rename.
  - id `1963`: "Pirates_de_Quebradillas" (2013-2015) -> "Atenienses-de-Manati"
    (2015-2018), same pattern.
Filtering by team id would silently merge these. Filtering by the real
franchise **name/slug** instead avoids it entirely — id is ignored for
identity purposes here, used only as a URL path component.

**The one real, corroborated anchor case**: id `1901` carries both
"Caciques-de-Humacao" (2013-2018) and "Gallitos-de-Isabela" (2017, 2021)
slugs, matching this archive's own pre-existing note
(`city_franchise_map.csv` / `player_career_seasons.csv`'s "Caciques-Gallitos,
Humacao-Isabela" hybrid label) from a fully independent source — real
corroboration, not assumed. Both slugs map to `caciques_humacao` here so
Phase C batches this franchise's whole run as one identity thread, per
owner instruction, rather than splitting on the name change.

**Also excluded, checked directly not assumed**: women's-league and
youth-league pages under the same real team names. latinbasket tags these
with a `Women=1` / `junior=1` query param, or a distinct feminine-form
slug (`Cangrejeras`, `Santeras`, `Leonas`, `Indias`, `Pollitas`, `Super-*`,
the `Manatee`-spelled id `19626`). `_is_real_bsn_slug` / the query-param
check below exclude all of these explicitly, not by accident of pattern.

Season resolution: the `Year=YYYY` (or `Year=YYYY-YYYY`, in which case the
later year is used — matches this archive's single-year season-labeling
convention elsewhere) query param when present. A capture with no `Year`
param falls back to its Wayback capture year, recorded as a lower-precision
`season_source=capture_year` (vs `year_param`) in the manifest — never
silently treated as equally certain (PC1/PC3).

Run: `python -m src.fetch_latinbasket_roster`
"""

from __future__ import annotations

import csv
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

import requests

from src.wayback_cdx import REPO_ROOT, USER_AGENT, polite_get
from src.fetch_samples import raw_wayback_url

CDX_ENDPOINT = "http://web.archive.org/cdx/search/cdx"
URL_PATTERN = "basketball.latinbasket.com/team/Puerto-Rico/*"
RAW_CDX_PATH = REPO_ROOT / "data" / "raw" / "cdx" / "cdx_latinbasket_roster.json"
OUT_DIR = REPO_ROOT / "data" / "raw" / "latinbasket_roster"
MANIFEST = REPO_ROOT / "data" / "interim" / "fetch_manifest_latinbasket_roster.csv"

CORE_YEARS = {str(y) for y in range(2009, 2021)}  # 2009-2020, item 7 scope

TEAM_PATH_RE = re.compile(r"/team/Puerto-Rico/([^/]+)/(\d+)", re.IGNORECASE)

# Real men's BSN franchise slugs (normalized: lowercase, hyphens) -> franchise_id.
# `gallitos-de-isabela` deliberately shares `caciques_humacao` (see docstring).
SLUG_TO_FRANCHISE = {
    "vaqueros-de-bayamon": "vaqueros_bayamon",
    "cangrejeros-de-santurce": "cangrejeros_santurce",
    "capitanes-de-arecibo": "capitanes_arecibo",
    "santeros-de-aguada": "santeros_aguada",
    "caciques-de-humacao": "caciques_humacao",
    "gallitos-de-isabela": "caciques_humacao",
    "leones-de-ponce": "leones_ponce",
    "brujos-de-guayama": "brujos_guayama",
    "piratas-de-quebradillas": "piratas_quebradillas",
    "pirates-de-quebradillas": "piratas_quebradillas",  # latinbasket's own typo, same real team
    "atleticos-de-san-german": "atleticos_san_german",
    "atenienses-de-manati": "atenienses_manati",
    "mets-de-guaynabo": "mets_guaynabo",
    "criollos-de-caguas": "criollos_caguas",
    "gigantes-de-carolina": "gigantes_carolina",
    "cariduros-de-fajardo": "cariduros_fajardo",
    "maratonistas-de-coamo": "maratonistas_coamo",
    "indios-de-mayaguez": "indios_mayaguez",
}

# Substrings that mean "not the real men's top-flight team" even when the
# base name matches (women's/youth/reserve variants), checked before the
# slug lookup above.
EXCLUDE_SLUG_MARKERS = (
    "women", "lady", "ladies", "junior", "super-", "manatee",
    "cangrejeras", "santeras", "leonas", "indias", "pollitas",
)


def _strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def _normalize_slug(slug: str) -> str:
    slug = unquote(slug)
    slug = _strip_accents(slug).lower()
    slug = slug.replace("_", "-")
    return slug


def _query_cdx() -> list[dict]:
    """Fetch (or reuse a cached) un-collapsed CDX listing. Raw JSON persisted
    byte-for-byte (PC5)."""
    if RAW_CDX_PATH.exists():
        data = json.loads(RAW_CDX_PATH.read_text())
    else:
        session = requests.Session()
        session.headers.update({"User-Agent": USER_AGENT})
        resp = polite_get(CDX_ENDPOINT, params={"url": URL_PATTERN, "output": "json"}, session=session)
        resp.raise_for_status()
        data = resp.json()
        RAW_CDX_PATH.parent.mkdir(parents=True, exist_ok=True)
        RAW_CDX_PATH.write_text(json.dumps(data, indent=2))
    if not data:
        return []
    hdr, rows = data[0], data[1:]
    return [dict(zip(hdr, r)) for r in rows]


def _season_of(original_url: str, timestamp: str) -> tuple[str | None, str]:
    """(season, source) — source is 'year_param' or 'capture_year'."""
    qs = parse_qs(urlsplit(unquote(original_url)).query)
    year_param = qs.get("Year", [""])[0]
    if year_param:
        digits = re.findall(r"\d{4}", year_param)
        if digits:
            return digits[-1], "year_param"  # later year of a YYYY-YYYY range
    if len(timestamp) >= 4:
        return timestamp[:4], "capture_year"
    return None, "capture_year"


CAPTCHA_MARKERS = ("WELCOME TO LATINBASKET", "goCaptcha", "captchacode")


def _looks_like_captcha_wall(content: bytes) -> bool:
    """Wayback sometimes archived the live site's own anti-bot challenge
    page (HTTP 200, ~2.7KB, a captcha form) instead of real content —
    confirmed directly on 7 `?Page=1` captures during Phase A (2026-09-14).
    A real team page is 60KB+; this is a cheap, specific marker check, not
    a size heuristic that could false-positive on a thin real page."""
    text = content[:4000].decode("utf-8", errors="ignore")
    return any(marker in text for marker in CAPTCHA_MARKERS)


def candidates() -> dict[tuple[str, str], list[dict]]:
    """All real-BSN-team 200 captures per (franchise_id, season) in
    2009-2020, ranked best-first. Excludes women's/youth pages and
    non-BSN slugs explicitly; never trusts latinbasket's own numeric team
    id for identity (see module docstring).

    **Real finding, checked directly (2026-09-14 Phase A revision)**: the
    bare team URL is often a "team home" teaser (some news + a handful of
    named players), not the roster. The actual full roster is `?Page=1`
    (explicitly linked as "Roster"/"Full Roster" from the teaser itself,
    confirmed by fetching one and reading the real `<table id="trRoster">`
    it contains: jersey/name/height/position/age-or-birth-year/nationality/
    tenure/former-team/agent, plus a stable `latinbasket.com/player/.../id`
    per row — richer than either the bare-URL widget or the old flat table).
    Ranking: season precision (`year_param` beats `capture_year`) stays the
    primary tier so Phase C never trades away a certain season for a fuller
    page; `Page=1` beats no-Page beats any other Page value as the
    tie-break *within* that tier, then latest timestamp. Multiple ranked
    candidates are kept (not just the winner) because some `?Page=1`
    captures turn out to be a Wayback-archived anti-bot CAPTCHA wall, not
    real content (see `_looks_like_captcha_wall`) — the fetch step falls
    back through this list rather than silently accepting one."""
    rows = _query_cdx()
    grouped: dict[tuple[str, str], list[dict]] = {}
    for r in rows:
        if r.get("statuscode") != "200":
            continue
        orig = r["original"]
        path = urlsplit(unquote(orig)).path
        m = TEAM_PATH_RE.search(path)
        if not m:
            continue
        raw_slug = m.group(1)
        norm_slug = _normalize_slug(raw_slug)

        qs = parse_qs(urlsplit(unquote(orig)).query)
        if qs.get("Women", [""])[0] == "1" or qs.get("junior", [""])[0] == "1":
            continue
        if any(marker in norm_slug for marker in EXCLUDE_SLUG_MARKERS):
            continue

        franchise_id = SLUG_TO_FRANCHISE.get(norm_slug)
        if franchise_id is None:
            continue

        season, season_source = _season_of(orig, r["timestamp"])
        if season not in CORE_YEARS:
            continue

        page_param = qs.get("Page", [""])[0]
        is_page1 = page_param == "1"
        is_unpaged = page_param == ""

        rank = (season_source == "year_param", is_page1, is_unpaged, r["timestamp"])
        key = (franchise_id, season)
        grouped.setdefault(key, []).append({
            **r, "_slug": raw_slug, "_season_source": season_source, "_rank": rank,
        })
    for key in grouped:
        grouped[key].sort(key=lambda rec: rec["_rank"], reverse=True)
    return grouped


def targets() -> dict[tuple[str, str], dict]:
    """Best (rank-0) candidate per key — used for reporting/dry-run only.
    The actual fetch (`main`) walks the full `candidates()` list so it can
    fall back past a CAPTCHA-wall capture."""
    return {key: recs[0] for key, recs in candidates().items()}


def main() -> int:
    cand = candidates()
    by_franchise: dict[str, list[str]] = {}
    for (fid, season) in cand:
        by_franchise.setdefault(fid, []).append(season)
    print(f"[latinbasket_roster] {len(cand)} (franchise, season) targets across "
          f"{len(by_franchise)} franchises, 2009-2020 core window")
    for fid in sorted(by_franchise):
        seasons = sorted(by_franchise[fid])
        print(f"  {fid}: {len(seasons)} seasons -> {', '.join(seasons)}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    rows_out = []
    for (fid, season), recs in sorted(cand.items()):
        html_path = OUT_DIR / f"{fid}_{season}.html"
        meta_path = OUT_DIR / f"{fid}_{season}.meta.json"
        best = recs[0]

        # Cached and still matches the current best candidate's capture,
        # and isn't a previously-undetected CAPTCHA wall -> reuse.
        if html_path.exists() and meta_path.exists():
            cached_meta = json.loads(meta_path.read_text())
            same_capture = cached_meta.get("timestamp") == best["timestamp"]
            if same_capture and not _looks_like_captcha_wall(html_path.read_bytes()):
                print(f"  [{fid} {season}] cached")
                rows_out.append({
                    "franchise_id": fid, "season": season, "season_source": best["_season_source"],
                    "slug": best["_slug"], "timestamp": best["timestamp"], "original_url": best["original"],
                    "status": "ok", "local_file": html_path.name,
                })
                continue

        fetched = False
        for i, rec in enumerate(recs):
            base_row = {
                "franchise_id": fid, "season": season, "season_source": rec["_season_source"],
                "slug": rec["_slug"], "timestamp": rec["timestamp"], "original_url": rec["original"],
            }
            url = raw_wayback_url(rec["timestamp"], rec["original"])
            try:
                resp = polite_get(url, session=session)
            except requests.RequestException as exc:
                print(f"  ! [{fid} {season}] candidate {i} {exc.__class__.__name__}: {exc}", file=sys.stderr)
                continue
            if resp.status_code != 200:
                print(f"  ! [{fid} {season}] candidate {i} HTTP {resp.status_code}", file=sys.stderr)
                continue
            if _looks_like_captcha_wall(resp.content):
                print(f"  ! [{fid} {season}] candidate {i} ({rec['timestamp']}) is a CAPTCHA wall, "
                      f"falling back", file=sys.stderr)
                continue
            html_path.write_bytes(resp.content)
            meta_path.write_text(json.dumps({
                **base_row, "digest": rec.get("digest", ""), "raw_wayback_url": url,
                "content_length": len(resp.content), "candidate_rank": i,
            }, indent=2))
            print(f"  [{fid} {season}] fetched ({len(resp.content)} bytes, capture {rec['timestamp']}"
                  f"{', fallback candidate ' + str(i) if i else ''})")
            rows_out.append({**base_row, "status": "ok", "local_file": html_path.name})
            fetched = True
            break
        if not fetched:
            print(f"  ! [{fid} {season}] no usable candidate ({len(recs)} tried, all failed/blocked)",
                  file=sys.stderr)
            rows_out.append({
                "franchise_id": fid, "season": season, "season_source": best["_season_source"],
                "slug": best["_slug"], "timestamp": best["timestamp"], "original_url": best["original"],
                "status": "all_candidates_failed", "local_file": "",
            })

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["franchise_id", "season", "season_source", "slug", "timestamp",
                  "original_url", "status", "local_file"]
    with MANIFEST.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows_out)
    ok = sum(1 for r in rows_out if r["status"] == "ok")
    print(f"[latinbasket_roster] {ok}/{len(rows_out)} ok -> "
          f"{OUT_DIR.relative_to(REPO_ROOT)} + {MANIFEST.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
