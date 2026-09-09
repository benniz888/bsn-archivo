"""PHASE_5 / 5B — build the static `web/data/` JSON tree from `data/clean/` +
the curated franchise files under `app/`.

Deterministic: `json.dumps(sort_keys=True, separators=(",",":"))` + `"\n"`,
fixed float precision, no wall-clock and no git state anywhere.
`manifest.json.source_digest` (sha256 over the exact input files) is the
version, so a rerun on unchanged inputs produces a byte-identical tree (clean
git diff). See `docs/specs/app_data_map.md`.

5B scope: `manifest.json` + `index/{franchises,seasons,players,scoring_titles,
career_leaders,records}.json`. Per-entity files (players/, seasons/, games/) are
5C. PBP is 5F.

Run: `python -m src.build_web_data`   (`make build-web-data`)
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

from src.wayback_cdx import REPO_ROOT
from src.parse_wayback import open_clean_text

CLEAN = REPO_ROOT / "data" / "clean"
APP = REPO_ROOT / "app"
WEB = REPO_ROOT / "web" / "data"

SCHEMA_VERSION = 1


# --------------------------------------------------------------------------- #
# io helpers                                                                   #
# --------------------------------------------------------------------------- #
def _read(name: str) -> list[dict]:
    with open_clean_text(CLEAN / name, "r") as fh:
        return list(csv.DictReader(fh))


def _int(v):
    v = (v or "").strip()
    return int(v) if v.lstrip("-").isdigit() else None


def _float(v, ndigits: int = 2):
    v = (v or "").strip()
    try:
        return round(float(v), ndigits)
    except (TypeError, ValueError):
        return None


def _jdump(obj, path: Path) -> int:
    """Write `obj` as canonical JSON. Returns the top-level length (rows / keys)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    path.write_text(text, encoding="utf-8")
    return len(obj)


def _source_digest(inputs: list[str]) -> str:
    """sha256 over the exact bytes of every clean CSV + curated file that feeds
    the build. Version = what the data was built from, fully deterministic and
    independent of git state (no chicken-and-egg when committing the artifact
    alongside its own manifest). Changes iff an input changes."""
    h = hashlib.sha256()
    for name in sorted(inputs):
        path = (CLEAN / name) if (CLEAN / name).exists() else (APP / name)
        with open_clean_text(path, "r") as fh:
            h.update(fh.read().encode("utf-8"))
    return h.hexdigest()


# --------------------------------------------------------------------------- #
# franchise crosswalk (D-040) — checked-in curated map, asserted complete      #
# --------------------------------------------------------------------------- #
def load_crosswalk() -> tuple[dict[str, str], dict[str, str]]:
    with (APP / "franchise_key_map.csv").open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    app_to_fid = {r["app_key"]: r["franchise_id"] for r in rows}
    fid_to_app = {r["franchise_id"]: r["app_key"] for r in rows}

    fids_master = {r["franchise_id"] for r in _read("franchises.csv")}
    fids_champ = set()
    for r in _read("champions_reconciled.csv"):
        fids_champ.update(x for x in (r["champion_franchise_id"], r["runner_up_franchise_id"]) if x)

    mapped_fids = set(fid_to_app)
    # every id that appears in the master or in a reconciled champion row must be
    # in the crosswalk, except ids explicitly documented as having no app key.
    NO_APP_KEY = {"santos_san_juan"}  # D5 — app folds San Juan 1945 into `cap`
    missing_fid = (fids_master | fids_champ) - mapped_fids - NO_APP_KEY
    missing_app = _app_keys() - set(app_to_fid)
    if missing_fid or missing_app:
        sys.exit(f"! franchise_key_map.csv incomplete — franchise_id without a key: "
                 f"{sorted(missing_fid)}; app_key without a mapping: {sorted(missing_app)}")
    return app_to_fid, fid_to_app


def _app_keys() -> set[str]:
    """The franchise keys the app actually defines (from franchise_curated.json)."""
    return set(json.loads((APP / "franchise_curated.json").read_text(encoding="utf-8")))


# --------------------------------------------------------------------------- #
# index builders                                                               #
# --------------------------------------------------------------------------- #
def _title_years(fid_to_app: dict[str, str]) -> tuple[dict, dict]:
    """franchise_id -> sorted [seasons won] / [seasons lost] from champions_reconciled.
    Season keys stay strings so D3's `1942-1943` survives."""
    won: dict[str, list] = {}
    lost: dict[str, list] = {}
    for r in _read("champions_reconciled.csv"):
        if r["champion_franchise_id"]:
            won.setdefault(r["champion_franchise_id"], []).append(r["season"])
        if r["runner_up_franchise_id"]:
            lost.setdefault(r["runner_up_franchise_id"], []).append(r["season"])
    for d in (won, lost):
        for k in d:
            d[k] = sorted(d[k])
    return won, lost


def _lineage(fid: str) -> list[dict]:
    out = []
    for r in _read("franchise_events.csv"):
        if fid in (r["from_franchise_id"], r["to_franchise_id"]):
            out.append({
                "event_type": r["event_type"],
                "season": _int(r["season"]),
                "from": r["from_franchise_id"] or None,
                "to": r["to_franchise_id"] or None,
                "confidence": r["confidence"],
                "note": r["note"] or None,
            })
    return out


def build_franchises(app_to_fid, fid_to_app) -> Path:
    master = {r["franchise_id"]: r for r in _read("franchises.csv")}
    curated = json.loads((APP / "franchise_curated.json").read_text(encoding="utf-8"))
    won, lost = _title_years(fid_to_app)

    out = []
    for app_key, fid in sorted(app_to_fid.items()):
        m = master.get(fid, {})
        c = curated.get(app_key, {})
        status_raw = (m.get("status") or "").strip()
        active = status_raw == "active"
        end = None
        if not active:
            digits = "".join(ch for ch in status_raw if ch.isdigit())
            end = int(digits) if len(digits) == 4 else c.get("end")
        out.append({
            "franchise_id": fid,
            "app_key": app_key,
            "name": m.get("canonical_name") or "",
            "city": m.get("city") or "",
            "founded": _int(m.get("founded")),
            "status": "active" if active else "defunct",
            "end": end,
            "abbr": c.get("abbr"),
            "colors": {"c1": c.get("c1"), "c2": c.get("c2"), "src": c.get("colorSrc")},
            "coach": c.get("coach"),
            "note": c.get("note"),
            "titles": won.get(fid, []),
            "finals_lost": lost.get(fid, []),
            "lineage": _lineage(fid),
        })
    n = _jdump(out, WEB / "index" / "franchises.json")
    return WEB / "index" / "franchises.json"


def build_seasons_index() -> Path:
    out = []
    for r in _read("champions_reconciled.csv"):
        out.append({
            "season": r["season"],
            "champion": r["champion_franchise_id"] or None,
            "runner_up": r["runner_up_franchise_id"] or None,
            "agreement": r["agreement"],
            "confidence": r["confidence"],
            "note": r["note"] or None,
        })
    out.sort(key=lambda s: s["season"])
    _jdump(out, WEB / "index" / "seasons.json")
    return WEB / "index" / "seasons.json"


def build_players_index() -> Path:
    out = []
    for r in _read("players_canonical.csv"):
        out.append({
            "id": _int(r["bsnpr_id"]),
            "name": r["canonical_name"],
            "norm": r["normalized_name"],
            "first_season": _int(r["first_season"]),
            "last_season": _int(r["last_season"]),
            "position": r["position"] or None,
            "birth_year": _int(r["birth_year"]),
            "nationality": r["nationality"] or None,
            "n_seasons": _int(r["n_seasons"]),
            "has_profile": r["has_profile"] == "yes",
        })
    out.sort(key=lambda p: p["id"])
    _jdump(out, WEB / "index" / "players.json")
    return WEB / "index" / "players.json"


def build_scoring_titles() -> Path:
    out = []
    for r in _read("scoring_champions_reconciled.csv"):
        rec = {
            "season": _int(r["season"]),
            "metric_era": r["metric_era"],
            "agreement": r["agreement"],
            "confidence": r["confidence"],
            "sources": [s.strip() for s in r["sources"].split(";") if s.strip()],
            "note": r["note"] or None,
            "champion": None,
            "dual": None,
        }
        if r["agreement"] == "dual_metric_d4":
            rec["dual"] = {
                "ppg": {"player": r["ppg_champion"], "value": _float(r["ppg_value"])},
                "total_points": {"player": r["total_points_champion"],
                                 "value": _int(r["total_points_value"])},
            }
        else:
            player = r["historic_player"] or r["seed_player"] or r["leaders_player"] or None
            rec["champion"] = {
                "player": player,
                "ppg": _float(r["historic_ppg"]) or _float(r["leaders_ppg"]),
                "total_points": _int(r["historic_total"])
                or (_int(r["seed_value"]) if r["metric_era"] == "total_points" else None),
            }
        out.append(rec)
    out.sort(key=lambda s: s["season"] or 0)
    _jdump(out, WEB / "index" / "scoring_titles.json")
    return WEB / "index" / "scoring_titles.json"


def build_career_leaders() -> Path:
    out: dict[str, list] = {}
    for r in _read("bsn_career_leaders.csv"):
        out.setdefault(r["category"], []).append({
            "rank": _int(r["rank"]),
            "player": r["player"],
            "position": r["position"] or None,
            "nationality": r["nationality"] or None,
            "years": r["years"],
            "total": _int(r["total"]),
            "games_played": _int(r["games_played"]),
            "per_game": _float(r["per_game"]),
        })
    for k in out:
        out[k].sort(key=lambda x: x["rank"] or 0)
    payload = {
        "stale_note": "Career totals are a FLOOR, ~5 years stale per Wikipedia's own "
                      "flag (D7). Players active past the cutoff are undercounted.",
        "categories": out,
    }
    _jdump(payload, WEB / "index" / "career_leaders.json")
    return WEB / "index" / "career_leaders.json"


def build_records() -> Path:
    out = []
    for r in _read("bsn_records.csv"):
        out.append({
            "record": r["record"],
            "holder": r["holder"],
            "value": r["value"],
            "season": _int(r["season"]),
            "note": r["notes"] or None,
        })
    _jdump(out, WEB / "index" / "records.json")
    return WEB / "index" / "records.json"


# --------------------------------------------------------------------------- #
# app won/ru vs champions_reconciled — diff report (5A OQ2)                     #
# --------------------------------------------------------------------------- #
def diff_app_champions(app_to_fid) -> list[str]:
    """Every season where the app's F[key].won/ru disagrees with the reconciled
    champions. Printed, not written — a human eyeballs it once."""
    html = (REPO_ROOT / "app" / "bsn_archivo.html").read_text(encoding="utf-8")
    block = html[html.index("const F = {"):html.index("\n};", html.index("const F = {"))]
    app_champ: dict[str, str] = {}
    app_ru: dict[str, str] = {}
    for key, body in zip(*[iter(re.split(r"\n  ([a-z]{3}):\{", "\n" + block)[1:])] * 2):
        body = re.sub(r"\s+", " ", body)
        for tag, dst in (("won", app_champ), ("ru", app_ru)):
            m = re.search(rf"\b{tag}:\[([\d, ]*)\]", body)
            for y in (m.group(1).split(",") if m and m.group(1).strip() else []):
                dst[y.strip()] = key

    diffs = []
    for r in _read("champions_reconciled.csv"):
        s = r["season"]
        for slot, csv_fid, app_map in (("champion", r["champion_franchise_id"], app_champ),
                                       ("runner_up", r["runner_up_franchise_id"], app_ru)):
            app_key = app_map.get(s)
            app_fid = app_to_fid.get(app_key) if app_key else None
            if csv_fid and app_fid and csv_fid != app_fid:
                diffs.append(f"  {s} {slot}: app={app_key}({app_fid})  csv={csv_fid}  [{r['agreement']}]")
            elif csv_fid and not app_fid and r["agreement"] not in ("no_champion", "seed_only", "bsnpr_only"):
                diffs.append(f"  {s} {slot}: app=(none)  csv={csv_fid}  [{r['agreement']}]")
    return diffs


# --------------------------------------------------------------------------- #
def main() -> int:
    if not CLEAN.exists():
        print("! data/clean missing", file=sys.stderr)
        return 1
    app_to_fid, fid_to_app = load_crosswalk()

    built = {
        "franchises": build_franchises(app_to_fid, fid_to_app),
        "seasons": build_seasons_index(),
        "players": build_players_index(),
        "scoring_titles": build_scoring_titles(),
        "career_leaders": build_career_leaders(),
        "records": build_records(),
    }
    counts = {}
    for name, path in built.items():
        obj = json.loads(path.read_text(encoding="utf-8"))
        counts[name] = len(obj["categories"]) if name == "career_leaders" else len(obj)
        print(f"  -> {path.relative_to(REPO_ROOT)} ({counts[name]})")

    SOURCES = [
        "franchises.csv", "champions_reconciled.csv", "franchise_events.csv",
        "players_canonical.csv", "scoring_champions_reconciled.csv",
        "bsn_career_leaders.csv", "bsn_records.csv",
        "franchise_key_map.csv", "franchise_curated.json",
    ]
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "source_digest": _source_digest(SOURCES),
        "counts": counts,
    }
    _jdump(manifest, WEB / "manifest.json")
    print(f"  -> {(WEB / 'manifest.json').relative_to(REPO_ROOT)} "
          f"(digest {manifest['source_digest'][:12]})")

    diffs = diff_app_champions(app_to_fid)
    if diffs:
        print(f"\n[app vs champions_reconciled] {len(diffs)} season/slot disagreements "
              f"(app is stale — 5D regenerates from the CSV):")
        print("\n".join(diffs))
    else:
        print("\n[app vs champions_reconciled] no disagreements")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
