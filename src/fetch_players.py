"""PHASE_3D — fetch the player-identity sources.

Two tranches:
  A  enciclopedia.asp  (/estadisticas/, from data/interim/cdx_inventory.csv) —
     the all-time player directory: Apellidos | Nombre | Camisa | Nació + a
     /jugadores/jugador.asp?id=N link per player. ~78 distinct captures.
  B  /jugadores/jugador.asp?id=N  (from data/raw/cdx/cdx_root_all.json) — the
     per-player profile: full name incl. nickname, birth city + date, position,
     height/weight, and a career-by-season stat table. One capture per player
     id (the latest — most complete). ~1079 distinct ids.

One HTTP GET per unique digest (tranche A) / per id (tranche B), `id_` raw
suffix, `polite_get` backoff (PC6). Raw bytes written unmodified, never
re-fetched (PC5). Progress is printed every PROGRESS_EVERY fetches so a
background run is followable.

Run: `python -m src.fetch_players [--tranche A|B] [--limit N]`
     (`make fetch-players`)
"""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

import requests

from src.wayback_cdx import INTERIM_DIR, REPO_ROOT, USER_AGENT, polite_get
from src.fetch_samples import raw_wayback_url

RAW_DIR = REPO_ROOT / "data" / "raw" / "players"
ROOT_CDX = REPO_ROOT / "data" / "raw" / "cdx" / "cdx_root_all.json"
PHASE1_INV = INTERIM_DIR / "cdx_inventory.csv"
MANIFEST = INTERIM_DIR / "fetch_manifest_players.csv"
PROGRESS_EVERY = 25


def _root_rows() -> tuple[list[list], dict[str, int]]:
    data = json.loads(ROOT_CDX.read_text())
    hdr, rows = data[0], data[1:]
    return rows, {k: i for i, k in enumerate(hdr)}


def _write_manifest(records: list[dict]) -> None:
    with MANIFEST.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["tranche", "key", "original_url", "timestamp", "digest", "local_file"])
        for r in sorted(records, key=lambda r: (r["tranche"], r["key"])):
            w.writerow([r["tranche"], r["key"], r["original_url"], r["timestamp"],
                        r["digest"], r["local_file"]])


def _fetch_one(url: str, out_path: Path, meta: dict, session: requests.Session) -> bool:
    if out_path.exists() and out_path.stat().st_size > 0:
        return True
    try:
        resp = polite_get(url, session=session)
    except requests.RequestException as exc:
        print(f"    ! {exc.__class__.__name__}: {exc}", file=sys.stderr)
        return False
    if resp.status_code != 200:
        print(f"    ! HTTP {resp.status_code} {url}", file=sys.stderr)
        return False
    out_path.write_bytes(resp.content)
    out_path.with_name(out_path.name + ".meta.json").write_text(
        json.dumps({**meta, "raw_wayback_url": url,
                    "content_length": len(resp.content)}, indent=2))
    return True


def tranche_a(session: requests.Session, limit: int | None) -> list[dict]:
    with PHASE1_INV.open(encoding="utf-8") as fh:
        caps = [r for r in csv.DictReader(fh)
                if r["endpoint"] == "enciclopedia.asp" and r["statuscode"] == "200"]
    by_digest: dict[str, list[dict]] = defaultdict(list)
    for r in caps:
        by_digest[r["digest"]].append(r)
    reps = {d: min(v, key=lambda c: c["timestamp"]) for d, v in by_digest.items()}
    out_dir = RAW_DIR / "enciclopedia"
    out_dir.mkdir(parents=True, exist_ok=True)

    items = sorted(reps.items(), key=lambda kv: kv[1]["timestamp"])
    if limit:
        items = items[:limit]
    print(f"[A enciclopedia] {len(caps)} captures, {len(items)} digests to fetch")
    records: list[dict] = []
    done = 0
    for digest, rec in items:
        fname = f"{rec['timestamp']}_{digest[:8]}.html"
        url = raw_wayback_url(rec["timestamp"], rec["original_url"])
        ok = _fetch_one(url, out_dir / fname, {
            "tranche": "A", "wayback_timestamp": rec["timestamp"],
            "original_url": rec["original_url"], "digest": digest}, session)
        records.append({"tranche": "A", "key": digest, "original_url": rec["original_url"],
                        "timestamp": rec["timestamp"], "digest": digest,
                        "local_file": fname if ok else ""})
        done += 1
        if done % PROGRESS_EVERY == 0 or done == len(items):
            print(f"  [A] {done}/{len(items)}")
    return records


def tranche_b(session: requests.Session, limit: int | None) -> list[dict]:
    rows, ix = _root_rows()
    by_id: dict[str, list[list]] = defaultdict(list)
    for r in rows:
        if urlsplit(unquote(r[ix["original"]])).path.lower() != "/jugadores/jugador.asp":
            continue
        if r[ix["statuscode"]] != "200":
            continue
        pid = (parse_qs(urlsplit(unquote(r[ix["original"]])).query).get("id") or [None])[0]
        if pid and pid.isdigit():
            by_id[pid].append(r)

    out_dir = RAW_DIR / "jugador"
    out_dir.mkdir(parents=True, exist_ok=True)
    ids = sorted(by_id, key=int)
    if limit:
        ids = ids[:limit]
    print(f"[B jugador.asp] {len(by_id)} distinct ids, fetching {len(ids)} (latest capture each)")
    records: list[dict] = []
    done = ok_n = 0
    for pid in ids:
        rec = max(by_id[pid], key=lambda r: r[ix["timestamp"]])
        ts, digest = rec[ix["timestamp"]], rec[ix["digest"]]
        fname = f"{pid}_{ts}.html"
        url = raw_wayback_url(ts, rec[ix["original"]])
        got = _fetch_one(url, out_dir / fname, {
            "tranche": "B", "player_id": pid, "wayback_timestamp": ts,
            "original_url": rec[ix["original"]], "digest": digest}, session)
        ok_n += got
        records.append({"tranche": "B", "key": pid, "original_url": rec[ix["original"]],
                        "timestamp": ts, "digest": digest,
                        "local_file": fname if got else ""})
        done += 1
        if done % PROGRESS_EVERY == 0 or done == len(ids):
            print(f"  [B] {done}/{len(ids)}  ({ok_n} ok)")
    return records


def main() -> int:
    if not ROOT_CDX.exists():
        sys.exit("! data/raw/cdx/cdx_root_all.json missing — run `make enumerate-root`")
    args = sys.argv[1:]
    which = args[args.index("--tranche") + 1].upper() if "--tranche" in args else "AB"
    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else None

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    # merge with any prior manifest so a resumed / partial run keeps its records
    prior: dict[tuple, dict] = {}
    if MANIFEST.exists():
        with MANIFEST.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                prior[(r["tranche"], r["key"])] = r

    records: list[dict] = []
    if "A" in which:
        records += tranche_a(session, limit)
    if "B" in which:
        records += tranche_b(session, limit)

    for r in records:
        prior[(r["tranche"], r["key"])] = r
    _write_manifest(list(prior.values()))
    fetched = sum(1 for r in records if r["local_file"])
    print(f"\n[done] {fetched}/{len(records)} available; manifest -> {MANIFEST.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
