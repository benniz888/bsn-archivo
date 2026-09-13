"""PHASE_9 T9.1 — fetch archived latinbasket.com BSN season-standings pages.

`latinbasket.com` publishes a "BSN Standings" table on its per-season page
(`Puerto-Rico/basketball-League-BSN_YYYY.asp[x]`) — the archive does not
have a team-level standings file at all today, only champion/runner-up
(`champions_reconciled.csv`).

This source is fetched via the **Wayback Machine only**, never the live
site. `latinbasket.com/robots.txt` names `ClaudeBot` explicitly under
`Disallow: /` (alongside GPTBot/CCBot/Google-Extended/etc.), and the site's
own honest `USER_AGENT` gets a flat 404 from the live host — only a
spoofed browser UA works there. Routing around a directive that names this
exact agent is not something this pipeline does; see B5 / PHASE_9 in
`docs/session.md`. Wayback captures of the same pages are fetched instead —
PC6's explicitly sanctioned target, same as every other source in `src/`.

Coverage is real, not assumed: CDX-checked against every 2014-2023 URL
before writing this file. 2021 and 2023 have **no capture at all** under
this URL pattern (any scheme/case) — genuine gaps, not fetched, not
guessed (PC1/PC4). The other 8 years (2014-2020, 2022) have >=1 real 200
capture; the latest one per year is fetched (most likely to reflect a
finalized, not mid-season, standings table).

Run: `python -m src.fetch_latinbasket`
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote, urlsplit

import requests

from src.wayback_cdx import REPO_ROOT, USER_AGENT, polite_get
from src.fetch_samples import raw_wayback_url

CDX_ENDPOINT = "http://web.archive.org/cdx/search/cdx"
URL_PATTERN = "latinbasket.com/Puerto-Rico/basketball-League-BSN_*"
RAW_CDX_PATH = REPO_ROOT / "data" / "raw" / "cdx" / "cdx_latinbasket.json"
OUT_DIR = REPO_ROOT / "data" / "raw" / "latinbasket"
MANIFEST = REPO_ROOT / "data" / "interim" / "fetch_manifest_latinbasket.csv"

YEARS = [str(y) for y in range(2014, 2024)]  # 2014-2023, PHASE_9 scope


def _query_cdx() -> list[dict]:
    """Fetch (or reuse a cached) un-collapsed CDX listing for the URL pattern.
    Raw JSON persisted byte-for-byte (PC5)."""
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


def _year_of(original_url: str) -> str | None:
    path = urlsplit(unquote(original_url)).path
    # .../basketball-League-BSN_2014.asp or basketball-league-bsn_2014.aspx
    stem = path.rsplit("_", 1)[-1]
    digits = "".join(c for c in stem if c.isdigit())
    return digits[:4] if len(digits) >= 4 else None


def _is_legacy_asp(original_url: str) -> bool:
    """The pre-redesign `.asp` template is server-rendered (has the actual
    standings table in the raw HTML). The 2018-era `.aspx` redesign loads
    standings client-side via `/js/standings.js` — the raw Wayback capture
    is a near-empty shell with no table at all (checked directly, not
    assumed: 2015/2019/2020/2022's `.aspx` captures have zero
    `/team/Puerto-Rico/` links in the raw HTML, vs. dozens in every `.asp`
    capture). `.asp` is strictly preferred; `.aspx` is only ever a fallback
    of last resort, and even then usually parses to nothing."""
    return urlsplit(unquote(original_url)).path.lower().endswith(".asp")


def targets() -> dict[str, dict]:
    """Best 200 capture per requested year: the latest `.asp` (legacy,
    server-rendered) capture if one exists, else the latest `.aspx` capture
    as a fallback. Missing years are absent from the dict (not fabricated) —
    the caller reports them as gaps."""
    rows = _query_cdx()
    best: dict[str, dict] = {}
    for r in rows:
        if r.get("statuscode") != "200":
            continue
        yr = _year_of(r["original"])
        if yr not in YEARS:
            continue
        cur = best.get(yr)
        cur_is_asp = cur is not None and _is_legacy_asp(cur["original"])
        r_is_asp = _is_legacy_asp(r["original"])
        if cur is None:
            best[yr] = r
        elif r_is_asp and not cur_is_asp:
            best[yr] = r  # legacy always beats redesign, regardless of date
        elif r_is_asp == cur_is_asp and r["timestamp"] > cur["timestamp"]:
            best[yr] = r  # same tier: prefer the later capture
    return best


def main() -> int:
    t = targets()
    missing = [y for y in YEARS if y not in t]
    print(f"[latinbasket] {len(t)}/{len(YEARS)} years have a Wayback capture; "
          f"missing: {', '.join(missing) if missing else 'none'}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    rows_out = []
    for yr in YEARS:
        rec = t.get(yr)
        html_path = OUT_DIR / f"{yr}.html"
        meta_path = OUT_DIR / f"{yr}.meta.json"
        if rec is None:
            rows_out.append({"season": yr, "status": "no_capture", "timestamp": "",
                              "original_url": "", "local_file": ""})
            continue
        if html_path.exists() and html_path.stat().st_size > 0:
            print(f"  [{yr}] cached")
            rows_out.append({"season": yr, "status": "ok", "timestamp": rec["timestamp"],
                              "original_url": rec["original"], "local_file": html_path.name})
            continue
        url = raw_wayback_url(rec["timestamp"], rec["original"])
        try:
            resp = polite_get(url, session=session)
        except requests.RequestException as exc:
            print(f"  ! [{yr}] {exc.__class__.__name__}: {exc}", file=sys.stderr)
            rows_out.append({"season": yr, "status": "fetch_error", "timestamp": rec["timestamp"],
                              "original_url": rec["original"], "local_file": ""})
            continue
        if resp.status_code != 200:
            print(f"  ! [{yr}] HTTP {resp.status_code}", file=sys.stderr)
            rows_out.append({"season": yr, "status": f"http_{resp.status_code}",
                              "timestamp": rec["timestamp"], "original_url": rec["original"], "local_file": ""})
            continue
        html_path.write_bytes(resp.content)
        meta_path.write_text(json.dumps({
            "season": yr, "timestamp": rec["timestamp"], "original_url": rec["original"],
            "digest": rec.get("digest", ""), "raw_wayback_url": url,
            "content_length": len(resp.content),
        }, indent=2))
        print(f"  [{yr}] fetched ({len(resp.content)} bytes, capture {rec['timestamp']})")
        rows_out.append({"season": yr, "status": "ok", "timestamp": rec["timestamp"],
                          "original_url": rec["original"], "local_file": html_path.name})

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    import csv
    with MANIFEST.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["season", "status", "timestamp", "original_url", "local_file"])
        w.writeheader()
        w.writerows(rows_out)
    print(f"[latinbasket] -> {OUT_DIR.relative_to(REPO_ROOT)} + {MANIFEST.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
