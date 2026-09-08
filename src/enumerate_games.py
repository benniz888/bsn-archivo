"""PHASE_3E — enumerate the archived game-level scripts and write a per-script,
per-year coverage report so tranches can be gated at 500 distinct captures.

Reads the already-cached `data/raw/cdx/cdx_root_all.json` (from
`make enumerate-root`). No network.

Run: `python -m src.enumerate_games`   (`make enumerate-games`)
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from urllib.parse import parse_qs, unquote, urlsplit

from src.wayback_cdx import DOCS_DIR, INTERIM_DIR, REPO_ROOT
from src.parse_pre2007 import _write_csv

ROOT_CDX = REPO_ROOT / "data" / "raw" / "cdx" / "cdx_root_all.json"
GATE = 500

SCRIPTS = [
    "boxscore.asp", "gameinfo.asp", "pogamestat.asp",
    "a2gamestatpbp.asp", "gamestatwide.asp",
]


def _rows():
    data = json.loads(ROOT_CDX.read_text())
    hdr, rows = data[0], data[1:]
    return rows, {k: i for i, k in enumerate(hdr)}


def _captures_for(script: str, rows, ix) -> list[dict]:
    out = []
    for r in rows:
        u = unquote(r[ix["original"]])
        if not urlsplit(u).path.lower().endswith("/" + script):
            continue
        if r[ix["statuscode"]] != "200":
            continue
        q = parse_qs(urlsplit(u).query)
        out.append({
            "original_url": r[ix["original"]], "timestamp": r[ix["timestamp"]],
            "digest": r[ix["digest"]], "r": (q.get("r") or [""])[0],
            "cuarto": (q.get("cuarto") or [""])[0],
        })
    return out


def _game_year(rid: str, capture_ts: str) -> str:
    """Best-guess season year from the game id (`BS20081001`, `BS21005`) else
    the capture year."""
    m = rid.upper()
    if m.startswith("BS") and len(m) >= 6 and m[2:6].isdigit():
        return m[2:6]
    if m.startswith("BS") and len(m) >= 4 and m[2:4].isdigit():
        # 2-digit season code: BS19->2001? BS20->2001, BS21->2001, BS22->2002…
        # unreliable — fall back to capture year, note it
        return "~" + capture_ts[:4]
    return capture_ts[:4]


def main() -> int:
    if not ROOT_CDX.exists():
        print("! run `make enumerate-root` first")
        return 1
    rows, ix = _rows()

    inv_rows: list[dict] = []
    lines = ["# Game-script Wayback coverage (PHASE_3E)\n",
             "From `data/raw/cdx/cdx_root_all.json`. `distinct` = unique content "
             f"digests = fetch count. Gate: {GATE} per tranche.\n"]

    for script in SCRIPTS:
        caps = _captures_for(script, rows, ix)
        by_digest: dict[str, dict] = {}
        for c in caps:
            by_digest.setdefault(c["digest"], c)  # first capture stands in
        reps = list(by_digest.values())

        # split by capture year (the reliable axis) and by game-id year
        cyear = Counter(c["timestamp"][:4] for c in reps)
        gyear = Counter(_game_year(c["r"], c["timestamp"]) for c in reps)
        has_cuarto = sum(1 for c in reps if c["cuarto"])

        lines.append(f"\n## `{script}` — {len(caps)} 200-captures, "
                     f"**{len(reps)} distinct**"
                     + (f", {has_cuarto} carry a `cuarto=` (per-quarter PBP)" if has_cuarto else ""))
        lines.append("\n| capture year | distinct | tranche |")
        lines.append("|---|--:|---|")
        for y in sorted(cyear):
            n = sum(1 for c in reps if c["timestamp"][:4] == y)
            tag = "OK (<=500)" if n <= GATE else f"**GATED (>{GATE}) — split by month**"
            lines.append(f"| {y} | {n} | {tag} |")
        lines.append(f"\ngame-id year (best guess): "
                     + ", ".join(f"{y}:{n}" for y, n in sorted(gyear.items())))

        for c in reps:
            inv_rows.append({
                "script": script, "timestamp": c["timestamp"], "digest": c["digest"],
                "r": c["r"], "cuarto": c["cuarto"],
                "capture_year": c["timestamp"][:4],
                "original_url": c["original_url"],
            })

    total = len(inv_rows)
    lines.append(f"\n## Totals\n\n**{total} distinct game-script captures.** "
                 "Every script exceeds the 500 gate — each capture-year tranche "
                 "over 500 needs a coverage report + approval before fetch.\n")
    lines.append("| script | distinct | window | fetchable now (year tranches <=500) |")
    lines.append("|---|--:|---|---|")
    for script in SCRIPTS:
        s = [r for r in inv_rows if r["script"] == script]
        cy = Counter(r["capture_year"] for r in s)
        ok = sum(n for n in cy.values() if n <= GATE)
        yrs = sorted(cy)
        lines.append(f"| `{script}` | {len(s)} | {yrs[0]}–{yrs[-1]} | "
                     f"{ok} ({', '.join(f'{y}:{cy[y]}' for y in yrs if cy[y] <= GATE) or 'none'}) |")

    inv = INTERIM_DIR / "cdx_games_inventory.csv"
    _write_csv(inv, sorted(inv_rows, key=lambda r: (r["script"], r["timestamp"])),
               ["script", "timestamp", "digest", "r", "cuarto", "capture_year", "original_url"])

    out = DOCS_DIR / "coverage_games.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[enumerate-games] {total} distinct captures -> {inv.relative_to(REPO_ROOT)}, "
          f"{out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
