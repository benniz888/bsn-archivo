"""PHASE_3E — fetch archived game-level captures in gated tranches.

Reads `data/interim/cdx_games_inventory.csv` (from `make enumerate-games`). A
tranche = one (script, capture_year). **Hard gate: a tranche with more than
MAX_TRANCHE distinct captures is refused** — those need a coverage report and
owner approval (they can then be run with `--force-year`, still one script-year
at a time, or split further with `--month`).

One HTTP GET per unique digest, `id_` raw suffix, `polite_get` backoff (PC6).
Raw bytes written unmodified, never re-fetched (PC5). Progress every 25.

Run: `python -m src.fetch_games --script gamestatwide.asp [--year 2002] [--force-year]`
     `make fetch-games` (all ungated <=500 tranches)
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

RAW_DIR = REPO_ROOT / "data" / "raw" / "games"
INVENTORY = INTERIM_DIR / "cdx_games_inventory.csv"
MANIFEST = INTERIM_DIR / "fetch_manifest_games.csv"
MAX_TRANCHE = 500
PROGRESS_EVERY = 25


def _load() -> list[dict]:
    if not INVENTORY.exists():
        sys.exit("! run `make enumerate-games` first")
    with INVENTORY.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _tranches(rows: list[dict], script: str | None, year: str | None):
    by: dict[tuple, list[dict]] = defaultdict(list)
    for r in rows:
        if script and r["script"] != script:
            continue
        if year and r["capture_year"] != year:
            continue
        by[(r["script"], r["capture_year"])].append(r)
    return dict(sorted(by.items()))


def fetch_tranche(script: str, year: str, recs: list[dict],
                  session: requests.Session, force: bool) -> list[dict]:
    reps = {r["digest"]: r for r in recs}  # inventory is already digest-deduped
    n = len(reps)
    if n > MAX_TRANCHE and not force:
        print(f"[{script} {year}] {n} distinct > {MAX_TRANCHE} — GATED, skipped. "
              f"Report coverage + approve, then re-run with --force-year.", file=sys.stderr)
        return [{"script": script, "capture_year": year, "digest": r["digest"],
                 "r": r["r"], "timestamp": r["timestamp"], "local_file": "",
                 "gated": "yes"} for r in recs]

    out_dir = RAW_DIR / script.replace(".asp", "")
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[{script} {year}] fetching {n} distinct captures"
          + ("  (FORCED past the gate)" if n > MAX_TRANCHE else ""))
    records: list[dict] = []
    done = ok = 0
    for r in sorted(reps.values(), key=lambda r: r["timestamp"]):
        fname = f"{year}_{r['timestamp']}_{r['digest'][:8]}.html"
        fpath = out_dir / fname
        got = fpath.exists() and fpath.stat().st_size > 0
        if not got:
            url = raw_wayback_url(r["timestamp"], r["original_url"])
            try:
                resp = polite_get(url, session=session)
                if resp.status_code == 200:
                    fpath.write_bytes(resp.content)
                    (out_dir / f"{fname}.meta.json").write_text(json.dumps({
                        "script": script, "wayback_timestamp": r["timestamp"],
                        "original_url": r["original_url"], "raw_wayback_url": url,
                        "digest": r["digest"], "r": r["r"], "cuarto": r["cuarto"],
                        "content_length": len(resp.content)}, indent=2))
                    got = True
                else:
                    print(f"    ! HTTP {resp.status_code} {url}", file=sys.stderr)
            except requests.RequestException as exc:
                print(f"    ! {exc.__class__.__name__}: {exc}", file=sys.stderr)
        ok += got
        records.append({"script": script, "capture_year": year, "digest": r["digest"],
                        "r": r["r"], "timestamp": r["timestamp"],
                        "local_file": fname if got else "", "gated": "no"})
        done += 1
        if done % PROGRESS_EVERY == 0 or done == n:
            print(f"  [{script} {year}] {done}/{n}  ({ok} ok)")
    return records


def _merge_manifest(new: list[dict]) -> None:
    prior: dict[tuple, dict] = {}
    if MANIFEST.exists():
        with MANIFEST.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                prior[(r["script"], r["digest"])] = r
    for r in new:
        prior[(r["script"], r["digest"])] = r
    with MANIFEST.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["script", "capture_year", "digest", "r",
                                           "timestamp", "local_file", "gated"])
        w.writeheader()
        for r in sorted(prior.values(), key=lambda r: (r["script"], r["timestamp"])):
            w.writerow(r)


def main() -> int:
    rows = _load()
    args = sys.argv[1:]
    script = args[args.index("--script") + 1] if "--script" in args else None
    year = args[args.index("--year") + 1] if "--year" in args else None
    force = "--force-year" in args

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    all_recs: list[dict] = []
    for (scr, yr), recs in _tranches(rows, script, year).items():
        all_recs += fetch_tranche(scr, yr, recs, session, force)

    _merge_manifest(all_recs)
    fetched = sum(1 for r in all_recs if r["local_file"])
    gated = sorted({(r["script"], r["capture_year"]) for r in all_recs if r["gated"] == "yes"})
    print(f"\n[done] {fetched} available; manifest -> {MANIFEST.relative_to(REPO_ROOT)}")
    if gated:
        print("[gated — not fetched]:", ", ".join(f"{s} {y}" for s, y in gated))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
