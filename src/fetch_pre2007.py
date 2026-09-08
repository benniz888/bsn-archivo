"""PHASE_3C — bulk-fetch the root-level pre-2007 stat pages enumerated by
`src/enumerate_root.py`.

One HTTP GET per unique content digest (earliest capture as representative),
`id_` raw suffix, `polite_get` backoff (PC6). Raw bytes written unmodified and
never re-fetched (PC5). Every capture (not just the fetched ones) is recorded in
`data/interim/fetch_manifest_pre2007.csv`.

**Safety gate:** any script whose distinct-digest count exceeds MAX_TRANCHE is
skipped with a warning — those need explicit owner approval (the game-level and
`jugador.asp` tranches). Pass `--script NAME` to fetch one tranche, or no args
for all in-scope tranches under the gate.

Run: `python -m src.fetch_pre2007`   (`make fetch-pre2007`)
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
INVENTORY = INTERIM_DIR / "cdx_root_inventory.csv"
MANIFEST = INTERIM_DIR / "fetch_manifest_pre2007.csv"

# distinct-digest ceiling for an un-gated fetch (owner instruction: report before
# bulk-fetching any tranche over 500).
MAX_TRANCHE = 500

# The pre-2007 leaders / standings / team-stats scripts. NOT the game-level
# (`boxscore`, `pogamestat`, `a2gamestatpbp`, …) or identity (`jugador.asp`)
# scripts — those are separate, gated tranches.
IN_SCOPE = {
    "lidereshistoricos.asp", "lideres2001.asp", "lideres2000.asp",
    "lideres2002.asp", "lideres.asp", "posiciones2000.asp", "campeonatos.asp",
    "equiposstat.asp",
}


def _load() -> list[dict]:
    if not INVENTORY.exists():
        sys.exit(f"! {INVENTORY} missing — run `python -m src.enumerate_root` first")
    with INVENTORY.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def fetch_script(script: str, rows: list[dict], session: requests.Session) -> dict:
    caps = [r for r in rows if r["script"] == script and r["statuscode"] == "200"]
    by_digest: dict[str, list[dict]] = defaultdict(list)
    for r in caps:
        by_digest[r["digest"]].append(r)
    reps = {d: min(v, key=lambda c: c["timestamp"]) for d, v in by_digest.items()}

    if len(reps) > MAX_TRANCHE:
        print(f"[{script}] {len(reps)} distinct digests > {MAX_TRANCHE} — GATED, skipped "
              f"(needs owner approval)", file=sys.stderr)
        return {"script": script, "gated": True, "distinct": len(reps),
                "fetched": 0, "cached": 0, "failed": 0, "digest_to_file": {}}

    out_dir = RAW_DIR / script.replace(".asp", "")
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[{script}] {len(caps)} captures, {len(reps)} distinct digests")

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
        print(f"  [{i}/{len(reps)}] {rec['timestamp']} {digest[:8]} {rec['query'][:40]}")
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

    print(f"[{script}] fetched {fetched}, cached {cached}, failed {failed}")
    return {"script": script, "gated": False, "distinct": len(reps),
            "fetched": fetched, "cached": cached, "failed": failed,
            "digest_to_file": digest_to_file}


def main() -> int:
    rows = _load()
    args = sys.argv[1:]
    only = args[args.index("--script") + 1] if "--script" in args else None
    scripts = [only] if only else sorted(IN_SCOPE)

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    results = [fetch_script(s, rows, session) for s in scripts]

    # manifest: every in-scope 200 capture -> its local file (or "" if gated/failed)
    d2f: dict[str, str] = {}
    for res in results:
        d2f.update(res["digest_to_file"])
    with MANIFEST.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["script", "original_url", "timestamp", "digest", "query", "local_file"])
        for r in sorted(rows, key=lambda r: (r["script"], r["digest"], r["timestamp"])):
            if r["script"] in {s["script"] for s in results} and r["statuscode"] == "200":
                w.writerow([r["script"], r["original_url"], r["timestamp"], r["digest"],
                            r["query"], d2f.get(r["digest"], "")])

    tot = {k: sum(r[k] for r in results) for k in ("fetched", "cached", "failed")}
    gated = [r["script"] for r in results if r["gated"]]
    print(f"\n[done] fetched {tot['fetched']}, cached {tot['cached']}, failed {tot['failed']}. "
          f"Manifest -> {MANIFEST.relative_to(REPO_ROOT)}")
    if gated:
        print(f"[gated — not fetched]: {', '.join(gated)}")
    return 1 if tot["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
