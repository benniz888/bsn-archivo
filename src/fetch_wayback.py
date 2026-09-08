"""PHASE_2_FETCH — bulk-fetch the archived bsnpr.com stats pages that Phase 1
found actually recoverable. Enumeration proved the per-season 1957–2004 target
was never archived; this fetches what survived instead.

Tranches (see docs/specs/wayback_ingest_spec.md):
  A  campeonatos.asp   — every distinct 200-capture. Champion/coach/runner-up
                         ledger, 1930 -> year-of-capture.       -> data/raw/campeonatos/
  B  lideres.asp        — every distinct parameter-less 200-capture, 2007–2021.
                         11 stat-category leader tables, season-current-at-capture. -> data/raw/lideres/
  C  lideres.asp?...     — every distinct parametrized 200-capture.  -> data/raw/lideres/

Dedup is by content digest: one HTTP fetch per unique digest, the earliest
capture standing in for all captures that share it. Every capture (not just the
fetched ones) is recorded in the per-tranche `_manifest.csv` so the parse phase
knows which local file holds which timestamp's content.

PC5: raw bytes are written unmodified and never re-fetched once on disk.
PC6: sequential, >=1.5 s spacing, exponential backoff (via polite_get).

Run: `python -m src.fetch_wayback`
"""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import requests

from src.wayback_cdx import INTERIM_DIR, REPO_ROOT, USER_AGENT, polite_get
from src.fetch_samples import raw_wayback_url

RAW_DIR = REPO_ROOT / "data" / "raw"
INVENTORY = INTERIM_DIR / "cdx_inventory.csv"


def _tranche_a(rows: list[dict]) -> list[dict]:
    return [r for r in rows if r["endpoint"] == "campeonatos.asp" and r["statuscode"] == "200"]


def _tranche_b(rows: list[dict]) -> list[dict]:
    return [
        r for r in rows
        if r["endpoint"] == "lideres.asp" and r["parametrized"] == "no" and r["statuscode"] == "200"
    ]


def _tranche_c(rows: list[dict]) -> list[dict]:
    return [
        r for r in rows
        if r["endpoint"] == "lideres.asp" and r["parametrized"] == "yes" and r["statuscode"] == "200"
    ]


TRANCHES = {
    "campeonatos": (_tranche_a,),
    "lideres": (_tranche_b, _tranche_c),
}


def local_name(rec: dict) -> str:
    return f"{rec['timestamp']}_{rec['digest'][:8]}.html"


def fetch_tranche(name: str, records: list[dict], session: requests.Session) -> dict:
    out_dir = RAW_DIR / name
    out_dir.mkdir(parents=True, exist_ok=True)

    # one representative capture per digest — earliest timestamp
    by_digest: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_digest[r["digest"]].append(r)
    reps = {d: min(caps, key=lambda c: c["timestamp"]) for d, caps in by_digest.items()}

    print(f"\n[{name}] {len(records)} captures, {len(reps)} distinct digests to fetch")

    fetched, cached, failed = 0, 0, 0
    digest_to_file: dict[str, str] = {}

    for i, (digest, rec) in enumerate(sorted(reps.items(), key=lambda kv: kv[1]["timestamp"]), 1):
        fname = local_name(rec)
        fpath = out_dir / fname
        digest_to_file[digest] = fname

        if fpath.exists() and fpath.stat().st_size > 0:
            cached += 1
            continue

        url = raw_wayback_url(rec["timestamp"], rec["original_url"])
        print(f"  [{i}/{len(reps)}] {rec['timestamp']} {digest[:8]} -> {fname}")
        try:
            resp = polite_get(url, session=session)
        except requests.RequestException as exc:
            print(f"    ! {exc.__class__.__name__}: {exc}", file=sys.stderr)
            failed += 1
            digest_to_file[digest] = ""
            continue

        if resp.status_code != 200:
            print(f"    ! HTTP {resp.status_code} — skipped", file=sys.stderr)
            failed += 1
            digest_to_file[digest] = ""
            continue

        fpath.write_bytes(resp.content)
        (out_dir / f"{fname}.meta.json").write_text(json.dumps({
            "wayback_timestamp": rec["timestamp"],
            "original_url": rec["original_url"],
            "raw_wayback_url": url,
            "final_url": resp.url,
            "digest": digest,
            "anio": rec["anio"],
            "content_length": len(resp.content),
            "content_type": resp.headers.get("Content-Type", ""),
        }, indent=2))
        fetched += 1

    # manifest: every capture, pointed at its local file. Written to data/interim/
    # (not data/raw/, which is gitignored) so a cold-start resume can see what was
    # fetched without the bytes.
    manifest_path = INTERIM_DIR / f"fetch_manifest_{name}.csv"
    with manifest_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["original_url", "timestamp", "statuscode", "digest", "anio", "parametrized", "local_file"])
        for r in sorted(records, key=lambda r: (r["digest"], r["timestamp"])):
            w.writerow([
                r["original_url"], r["timestamp"], r["statuscode"], r["digest"],
                r["anio"], r["parametrized"], digest_to_file.get(r["digest"], ""),
            ])

    print(f"[{name}] fetched {fetched}, cached {cached}, failed {failed}; manifest -> {manifest_path.relative_to(REPO_ROOT)}")
    return {"fetched": fetched, "cached": cached, "failed": failed, "distinct": len(reps)}


def main() -> int:
    if not INVENTORY.exists():
        print(f"! {INVENTORY} missing — run `make enumerate` first", file=sys.stderr)
        return 1

    with INVENTORY.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    totals = {"fetched": 0, "cached": 0, "failed": 0, "distinct": 0}
    for name, filters in TRANCHES.items():
        records: list[dict] = []
        seen: set[tuple] = set()
        for f in filters:
            for r in f(rows):
                key = (r["original_url"], r["timestamp"])
                if key not in seen:
                    seen.add(key)
                    records.append(r)
        res = fetch_tranche(name, records, session)
        for k in totals:
            totals[k] += res[k]

    print(f"\n[done] {totals['distinct']} distinct digests: "
          f"{totals['fetched']} newly fetched, {totals['cached']} cached, {totals['failed']} failed.")
    return 1 if totals["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
