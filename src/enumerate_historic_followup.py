"""PHASE_3G_HISTORIC_FOLLOWUP — fresh CDX enumeration of three root-level
pre-2007 targets the earlier probes noted but never fully ingested:

  lidereshistoricos.asp   — year-by-year all-time single-season leaders.
                            `?t=3` (scoring + DPOY/ROY/MVP award histories) is
                            already in data/clean/ from PHASE_3C. Other `?t=`
                            values are unknown — this is what we're after.
  lideres2002.asp         — the 2002-season sibling of lideres2001.asp.
  mvp.asp  (root, NOT /estadisticas/mvp.asp) — unprobed.

Enumeration only — no snapshot fetching (that is `src/fetch_historic_followup.py`).
The PHASE_1 / PHASE_3C inventories are urlkey/subset-filtered; PHASE_3G's owner
instruction is a *fresh* CDX query per target so no `?t=` value is missed.

Writes `data/interim/cdx_historic_followup.csv` (every capture, every status)
and prints the distinct query strings + capture / status / digest counts.

Run: `python -m src.enumerate_historic_followup`   (`make enumerate-historic`)
"""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote, urlsplit

import requests

from src.wayback_cdx import (
    INTERIM_DIR, RAW_CDX_DIR, REPO_ROOT, USER_AGENT, polite_get,
)

CDX_ENDPOINT = "http://web.archive.org/cdx/search/cdx"

# url prefix -> the script basename we file it under
TARGETS = {
    "bsnpr.com/lidereshistoricos.asp": "lidereshistoricos.asp",
    "bsnpr.com/lideres2002.asp": "lideres2002.asp",
    "bsnpr.com/mvp.asp": "mvp.asp",
}

OUT_CSV = INTERIM_DIR / "cdx_historic_followup.csv"
FIELDS = ["script", "original_url", "timestamp", "statuscode", "mimetype",
          "digest", "query"]


def _fetch(session: requests.Session) -> dict[str, Path]:
    RAW_CDX_DIR.mkdir(parents=True, exist_ok=True)
    out: dict[str, Path] = {}
    for prefix, script in TARGETS.items():
        path = RAW_CDX_DIR / f"cdx_historic_{script.replace('.asp', '')}.json"
        if path.exists() and path.stat().st_size > 0:
            print(f"[cdx] {script}: cached ({path.stat().st_size} bytes)")
            out[script] = path
            continue
        params = {"url": f"{prefix}*", "output": "json", "limit": 50000}
        print(f"[cdx] {script}: querying {params['url']}")
        resp = polite_get(CDX_ENDPOINT, params=params, session=session)
        resp.raise_for_status()
        path.write_bytes(resp.content)
        print(f"  -> {path.relative_to(REPO_ROOT)} ({len(resp.content)} bytes)")
        out[script] = path
    return out


def _rows(path: Path) -> list[dict]:
    data = json.loads(path.read_text())
    if not data:
        return []
    header, *rest = data
    return [dict(zip(header, r)) for r in rest]


def _query(original: str) -> str:
    return urlsplit(unquote(original)).query


def main() -> int:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    paths = _fetch(session)

    all_rows: list[dict] = []
    for script, path in paths.items():
        for r in _rows(path):
            all_rows.append({
                "script": script,
                "original_url": r.get("original", ""),
                "timestamp": r.get("timestamp", ""),
                "statuscode": r.get("statuscode", ""),
                "mimetype": r.get("mimetype", ""),
                "digest": r.get("digest", ""),
                "query": _query(r.get("original", "")),
            })

    all_rows.sort(key=lambda r: (r["script"], r["query"], r["timestamp"]))
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(all_rows)
    print(f"\n[inventory] {len(all_rows)} captures -> {OUT_CSV.relative_to(REPO_ROOT)}\n")

    # per (script, query): capture count, status breakdown, distinct 200-digests
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in all_rows:
        groups[(r["script"], r["query"])].append(r)

    for (script, query), rs in sorted(groups.items()):
        status = defaultdict(int)
        for r in rs:
            status[r["statuscode"]] += 1
        digs = {r["digest"] for r in rs if r["statuscode"] == "200"}
        span = f"{rs[0]['timestamp'][:6]}–{rs[-1]['timestamp'][:6]}"
        q = query or "(no params)"
        print(f"  {script:24} {q:28} {len(rs):3} caps  {span}  "
              f"status={dict(status)}  distinct-200-digests={len(digs)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
