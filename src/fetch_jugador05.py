"""PHASE_3H (follow-up) — fetch the archived `jugador05.asp` per-player pages.

`jugador05.asp` is the 2005–2006 sibling of `jug05.asp`: same `r=xxx&r2=<token>&e=<city>`
scheme, no `?id=N`. Pages are keyed only by the opaque `r2` token + an `e=` roster
city, so several URLs resolve to identical content.

Dedup is by CDX **digest**: one HTTP GET per distinct page content (the latest
capture of that digest). 600 distinct → over MAX_TRANCHE, so it is fetched as
gated tranches by capture year (2005 ~450, 2006 ~152 — each < 500).
PC6 single stream. Raw bytes written unmodified and never re-fetched (PC5).

Run: `python -m src.fetch_jugador05 [--year 2005|2006] [--limit N] [--force]`
     (`make fetch-jugador05` runs every ungated year in sequence)
"""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

import requests

from src.wayback_cdx import REPO_ROOT, USER_AGENT
from src.fetch_players import _fetch_one
from src.fetch_samples import raw_wayback_url

ROOT_CDX = REPO_ROOT / "data" / "raw" / "cdx" / "cdx_root_all.json"
OUT_DIR = REPO_ROOT / "data" / "raw" / "players" / "jugador05"
MANIFEST = REPO_ROOT / "data" / "interim" / "fetch_manifest_jugador05.csv"
PAGE_PATH = "/jugador05.asp"
TRANCHE = "jugador05"
MAX_TRANCHE = 500
PROGRESS_EVERY = 25


def _targets(year: str | None = None) -> list[dict]:
    """One record per distinct digest: the latest 200 capture of the page.
    A digest's capture year is the year of that latest capture."""
    data = json.loads(ROOT_CDX.read_text())
    hdr, rows = data[0], data[1:]
    ix = {k: i for i, k in enumerate(hdr)}
    by_digest: dict[str, list[list]] = defaultdict(list)
    for r in rows:
        parts = urlsplit(unquote(r[ix["original"]]))
        if parts.path.lower() != PAGE_PATH or r[ix["statuscode"]] != "200":
            continue
        by_digest[r[ix["digest"]]].append(r)
    out = []
    for digest, recs in by_digest.items():
        rec = max(recs, key=lambda r: r[ix["timestamp"]])
        ts = rec[ix["timestamp"]]
        if year and ts[:4] != year:
            continue
        team = (parse_qs(urlsplit(unquote(rec[ix["original"]])).query).get("e") or [""])[0]
        out.append({"digest": digest, "timestamp": ts,
                    "original_url": rec[ix["original"]], "team": team})
    out.sort(key=lambda r: r["digest"])
    return out


def _fetch(targets: list[dict], session: requests.Session) -> list[dict]:
    records, done, ok_n = [], 0, 0
    for t in targets:
        fname = f"{t['digest']}.html"
        url = raw_wayback_url(t["timestamp"], t["original_url"])
        got = _fetch_one(url, OUT_DIR / fname, {
            "tranche": TRANCHE, "digest": t["digest"], "wayback_timestamp": t["timestamp"],
            "original_url": t["original_url"], "roster_team": t["team"]}, session)
        ok_n += got
        records.append({"key": t["digest"], "original_url": t["original_url"],
                        "timestamp": t["timestamp"], "digest": t["digest"],
                        "roster_team": t["team"], "local_file": fname if got else ""})
        done += 1
        if done % PROGRESS_EVERY == 0 or done == len(targets):
            print(f"  {done}/{len(targets)}  ({ok_n} ok)")
    return records


def _write_manifest(records: list[dict]) -> None:
    """Merge with any prior run's rows (a per-year tranche appends)."""
    existing: dict[str, dict] = {}
    if MANIFEST.exists():
        with MANIFEST.open(encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                existing[row["digest"]] = row
    for r in records:
        existing[r["digest"]] = r
    with MANIFEST.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["key", "original_url", "timestamp", "digest", "roster_team", "local_file"])
        for d in sorted(existing):
            r = existing[d]
            w.writerow([r["key"], r["original_url"], r["timestamp"], r["digest"],
                        r["roster_team"], r["local_file"]])


def main() -> int:
    args = sys.argv[1:]
    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else None
    year = args[args.index("--year") + 1] if "--year" in args else None
    force = "--force" in args

    all_n = len(_targets())
    years = [year] if year else sorted({t["timestamp"][:4] for t in _targets()})
    print(f"[jugador05.asp] {all_n} distinct digests total; tranches: {', '.join(years)}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    for y in years:
        targets = _targets(y)
        n = len(targets)
        if n > MAX_TRANCHE and not force:
            print(f"  [{y}] {n} > {MAX_TRANCHE} — GATED, skipped.")
            continue
        if limit:
            targets = targets[:limit]
        print(f"  [{y}] fetching {len(targets)} …")
        _write_manifest(_fetch(targets, session))
        print(f"  [{y}] done.")

    print(f"[jugador05.asp] -> {OUT_DIR.relative_to(REPO_ROOT)} + {MANIFEST.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
