"""PHASE_3G_HISTORIC_FOLLOWUP — fetch the useful root-level pre-2007 captures
enumerated by `src/enumerate_historic_followup.py`.

Reads `data/interim/cdx_historic_followup.csv`. One HTTP GET per distinct
content digest (earliest capture as representative), `id_` raw suffix,
`polite_get` backoff (PC6). Raw bytes written unmodified, never re-fetched
(PC5). Every 200 capture is recorded in `data/interim/fetch_manifest_historic_followup.csv`.

All three targets are far under the 500-digest gate, so no owner approval is
needed for the bulk fetch — but the counts are printed before fetching (PC4).

`--script NAME` fetches one; no args fetches every in-scope script.

Run: `python -m src.fetch_historic_followup`   (`make fetch-historic`)
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

RAW_DIR = REPO_ROOT / "data" / "raw" / "pre2007"
INVENTORY = INTERIM_DIR / "cdx_historic_followup.csv"
MANIFEST = INTERIM_DIR / "fetch_manifest_historic_followup.csv"
MAX_TRANCHE = 500

# lidereshistoricos.asp?t=3 and lideres2002.asp were already fetched + parsed by
# PHASE_3C (data/raw/pre2007/{lidereshistoricos,lideres2002}/, parse_pre2007).
# PHASE_3G re-confirms them from the fresh CDX and fills any gap; `mvp.asp` is
# the only genuinely new target.
IN_SCOPE = {"lidereshistoricos.asp", "lideres2002.asp", "mvp.asp"}


def _load() -> list[dict]:
    if not INVENTORY.exists():
        sys.exit(f"! {INVENTORY} missing — run `python -m src.enumerate_historic_followup` first")
    with INVENTORY.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def fetch_script(script: str, rows: list[dict], session: requests.Session) -> dict:
    caps = [r for r in rows if r["script"] == script and r["statuscode"] == "200"]
    by_digest: dict[str, list[dict]] = defaultdict(list)
    for r in caps:
        by_digest[r["digest"]].append(r)
    reps = {d: min(v, key=lambda c: c["timestamp"]) for d, v in by_digest.items()}

    out_dir = RAW_DIR / script.replace(".asp", "")
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[{script}] {len(caps)} 200-captures, {len(reps)} distinct digests "
          f"-> {out_dir.relative_to(REPO_ROOT)}")
    if len(reps) > MAX_TRANCHE:
        print(f"  ! {len(reps)} > {MAX_TRANCHE} — GATED, skipped", file=sys.stderr)
        return {"script": script, "gated": True, "fetched": 0, "cached": 0, "failed": 0,
                "digest_to_file": {}}

    fetched = cached = failed = 0
    digest_to_file: dict[str, str] = {}
    for i, (digest, rec) in enumerate(sorted(reps.items(), key=lambda kv: kv[1]["timestamp"]), 1):
        fname = f"{rec['timestamp']}_{digest[:8]}.html"
        fpath = out_dir / fname
        digest_to_file[digest] = fname
        if fpath.exists() and fpath.stat().st_size > 0:
            cached += 1
            continue
        url = raw_wayback_url(rec["timestamp"], rec["original_url"])
        print(f"  [{i}/{len(reps)}] {rec['timestamp']} {digest[:8]} {rec['query'] or '(bare)'}")
        try:
            resp = polite_get(url, session=session)
        except requests.RequestException as exc:
            print(f"    ! {exc.__class__.__name__}: {exc}", file=sys.stderr)
            failed += 1
            digest_to_file[digest] = ""
            continue
        if resp.status_code != 200:
            print(f"    ! HTTP {resp.status_code}", file=sys.stderr)
            failed += 1
            digest_to_file[digest] = ""
            continue
        fpath.write_bytes(resp.content)
        (out_dir / f"{fname}.meta.json").write_text(json.dumps({
            "script": script, "wayback_timestamp": rec["timestamp"],
            "original_url": rec["original_url"], "raw_wayback_url": url,
            "digest": digest, "query": rec["query"],
            "content_length": len(resp.content),
        }, indent=2))
        fetched += 1

    print(f"  fetched {fetched}, cached {cached}, failed {failed}")
    return {"script": script, "gated": False, "fetched": fetched, "cached": cached,
            "failed": failed, "digest_to_file": digest_to_file}


def main() -> int:
    rows = _load()
    args = sys.argv[1:]
    only = args[args.index("--script") + 1] if "--script" in args else None
    scripts = [only] if only else sorted(IN_SCOPE)

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    results = [fetch_script(s, rows, session) for s in scripts]

    d2f: dict[str, str] = {}
    for res in results:
        d2f.update(res["digest_to_file"])
    with MANIFEST.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["script", "original_url", "timestamp", "digest", "query", "local_file"])
        done = {s["script"] for s in results}
        for r in sorted(rows, key=lambda r: (r["script"], r["digest"], r["timestamp"])):
            if r["script"] in done and r["statuscode"] == "200":
                w.writerow([r["script"], r["original_url"], r["timestamp"],
                            r["digest"], r["query"], d2f.get(r["digest"], "")])

    tot = {k: sum(r[k] for r in results) for k in ("fetched", "cached", "failed")}
    print(f"\n[done] fetched {tot['fetched']}, cached {tot['cached']}, failed {tot['failed']}. "
          f"Manifest -> {MANIFEST.relative_to(REPO_ROOT)}")
    return 1 if tot["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
