"""PHASE_3C — CDX enumeration of the root-level bsnpr.com URL scheme.

PHASE_1 only enumerated `bsnpr.com/estadisticas*`. PHASE_3B found the 2000–2002
site served leader/standings data from root-level scripts
(`bsnpr.com/lideres2001.asp`, `/lidereshistoricos.asp`, `/equiposstat.asp`, …)
plus `bsnpr.com/jugadores/*`. This module runs a `bsnpr.com/*` CDX query,
drops everything already covered under `/estadisticas/`, and writes an
inventory + a per-script coverage report so the owner can gate the large
tranches before any bulk fetch.

Enumeration only. No snapshot fetching (that is `src/fetch_pre2007.py`).

Run: `python -m src.enumerate_root`   (`make enumerate-root`)
"""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote, urlsplit

import requests

from src.wayback_cdx import RAW_CDX_DIR, INTERIM_DIR, DOCS_DIR, REPO_ROOT, USER_AGENT, polite_get

CDX_ENDPOINT = "http://web.archive.org/cdx/search/cdx"
TARGET = "bsnpr.com/*"

# Scripts PHASE_3C actually intends to ingest — the coverage report calls these
# out explicitly. Everything else in the root scheme is reported but parked.
INGEST_SCRIPTS = {
    "lidereshistoricos.asp", "lideres2001.asp", "lideres2000.asp",
    "lideres2002.asp", "lideres.asp", "posiciones2000.asp", "posiciones2001.asp",
    "posiciones2002.asp", "campeonatos.asp", "equiposstat.asp",
}

# Game-level scripts — not this phase's target, but a major roadmap finding
# (box scores / play-by-play, which B1 was hunting for). Reported prominently.
GAME_SCRIPTS = {
    "boxscore.asp", "playbyplay.asp", "gameinfo.asp", "pogamestat.asp",
    "pogamestatwide2.asp", "pogamestat_online.asp", "a2gamestatpbp.asp",
    "gamestatwide.asp", "informe.asp", "juego.asp", "porjuego.asp",
}
PLAYER_SCRIPTS = {"jugador.asp", "jug05.asp", "jugador05.asp", "print_jugador.asp",
                  "jugadores/<dir>", "equipo.asp", "equipo05.asp"}

# Asset / forum / chrome noise — suppressed from the report entirely.
def _is_noise(script: str) -> bool:
    return (
        script.endswith((".jpg", ".png", ".gif", ".ico", ".css", ".js", ".xml", ".txt"))
        or script in {"discusion.asp", "topicos.asp", "forolist.asp", "a2forolist.asp",
                      "foros.asp", "reportar.asp", "proceso_ilegal.asp", "embed", "feed",
                      "reglas.asp", "enlaces.asp", "galeriafotos.asp", "galeria.asp",
                      "galeria_show.asp", "galeria_1.asp", "generate_thumb.asp",
                      "outofservice.asp", "404.asp", "frameset.asp", "bsnpr", "<root>",
                      "print_noticias.asp", "noticiasread.asp", "noticiasread4.asp",
                      "noticias05.asp", "entrevista.asp", "directiva.asp", "mensaje.asp",
                      "historia.asp", "historia05.asp", "cancha.asp", "definiciones.asp",
                      "leones", "jugador", "home.asp", "default.asp"}
    )


def _fetch(session: requests.Session) -> dict[str, Path]:
    RAW_CDX_DIR.mkdir(parents=True, exist_ok=True)
    queries = {
        "root_all": {"url": TARGET, "output": "json", "limit": 200000},
        "root_bydigest": {"url": TARGET, "output": "json", "limit": 200000, "collapse": "digest"},
    }
    out: dict[str, Path] = {}
    for name, params in queries.items():
        path = RAW_CDX_DIR / f"cdx_{name}.json"
        if path.exists() and path.stat().st_size > 0:
            print(f"[cdx] {name}: cached ({path.stat().st_size} bytes)")
            out[name] = path
            continue
        print(f"[cdx] {name}: querying {params}")
        resp = polite_get(CDX_ENDPOINT, params=params, session=session)
        resp.raise_for_status()
        path.write_bytes(resp.content)
        print(f"  -> {path.relative_to(REPO_ROOT)} ({len(resp.content)} bytes)")
        out[name] = path
    return out


def _rows(path: Path) -> list[dict]:
    data = json.loads(path.read_text())
    if not data:
        return []
    header, *rest = data
    return [dict(zip(header, r)) for r in rest]


def _path_of(original: str) -> str:
    return urlsplit(unquote(original)).path


def _script(original: str) -> str:
    """Last path segment if it looks like a script/page, else the dir prefix."""
    p = _path_of(original).lower()
    seg = p.rstrip("/").rsplit("/", 1)[-1]
    if seg.endswith((".asp", ".aspx", ".html", ".htm", ".php")):
        return seg
    if p.startswith("/jugadores"):
        return "jugadores/<dir>"
    return seg or "<root>"


def build_inventory(all_path: Path) -> tuple[Path, list[dict]]:
    rows = _rows(all_path)
    kept: list[dict] = []
    for r in rows:
        original = r.get("original", "")
        path = _path_of(original).lower()
        if path.startswith("/estadisticas/") or path == "/estadisticas.asp":
            continue  # already covered by PHASE_1 / PHASE_3B
        q = urlsplit(unquote(original)).query
        kept.append({
            "original_url": original,
            "timestamp": r.get("timestamp", ""),
            "statuscode": r.get("statuscode", ""),
            "mimetype": r.get("mimetype", ""),
            "digest": r.get("digest", ""),
            "script": _script(original),
            "path": _path_of(original),
            "query": q,
            "parametrized": "yes" if q else "no",
        })

    # Persist only the stats-relevant scripts — the full 133k-row inventory is
    # mostly news/forum/image noise and too big to track. Coverage still counts
    # everything from `kept` (in memory).
    relevant = INGEST_SCRIPTS | GAME_SCRIPTS | PLAYER_SCRIPTS | {
        "anotaciones.asp", "asistencias.asp", "rebotes.asp", "tiroslibres.asp",
        "mvp.asp", "posiciones.asp", "porequipo_info.asp", "calporequipo.asp",
        "stats-online.asp", "equiposstat_print.asp",
    }
    subset = [r for r in kept if r["script"] in relevant]
    out = INTERIM_DIR / "cdx_root_inventory.csv"
    fields = ["original_url", "timestamp", "statuscode", "mimetype", "digest",
              "script", "path", "query", "parametrized"]
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(sorted(subset, key=lambda r: (r["script"], r["timestamp"])))
    print(f"[inventory] {len(rows)} root captures, {len(kept)} non-/estadisticas/, "
          f"{len(subset)} stats-relevant -> {out.relative_to(REPO_ROOT)}")
    return out, kept


def build_coverage(rows: list[dict]) -> Path:
    by_script: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_script[r["script"]].append(r)

    def stat(recs: list[dict]) -> dict:
        ok = [r for r in recs if r["statuscode"] == "200"]
        ts = sorted(r["timestamp"] for r in ok)
        return {
            "captures": len(recs),
            "http200": len(ok),
            "distinct200": len({r["digest"] for r in ok}),
            "first": ts[0][:8] if ts else "—",
            "last": ts[-1][:8] if ts else "—",
            "param200": len({r["query"] for r in ok if r["parametrized"] == "yes"}),
        }

    lines = ["# Root-scheme Wayback coverage (PHASE_3C)\n"]
    lines.append(
        "Generated by `src/enumerate_root.py`. CDX query `url=bsnpr.com/*`, "
        "rows under `/estadisticas/` dropped (covered by PHASE_1/3B). "
        "`distinct200` = unique content digests behind the HTTP 200 captures — "
        "that is the fetch count.\n"
    )

    def table(scripts: list[str], with_param: bool = True) -> None:
        hdr = "| script | captures | HTTP 200 | distinct digests |"
        if with_param:
            hdr += " param 200s |"
        hdr += " first | last | >500? |"
        lines.append(hdr)
        lines.append("|---|--:|--:|--:|" + ("--:|" if with_param else "") + "---|---|---|")
        for s in scripts:
            st = stat(by_script[s])
            if st["http200"] == 0:
                continue
            gate = "**YES — gate**" if st["distinct200"] > 500 else "no"
            row = f"| `{s}` | {st['captures']} | {st['http200']} | {st['distinct200']} |"
            if with_param:
                row += f" {st['param200']} |"
            row += f" {st['first']} | {st['last']} | {gate} |"
            lines.append(row)

    ingest = sorted((s for s in by_script if s in INGEST_SCRIPTS),
                    key=lambda s: -stat(by_script[s])["distinct200"])
    game = sorted((s for s in by_script if s in GAME_SCRIPTS),
                  key=lambda s: -stat(by_script[s])["distinct200"])
    player = sorted((s for s in by_script if s in PLAYER_SCRIPTS),
                    key=lambda s: -stat(by_script[s])["distinct200"])
    misc = sorted((s for s in by_script
                   if s not in INGEST_SCRIPTS | GAME_SCRIPTS | PLAYER_SCRIPTS
                   and not _is_noise(s) and stat(by_script[s])["http200"] > 0),
                  key=lambda s: -stat(by_script[s])["http200"])

    lines.append("## PHASE_3C ingest targets (pre-2007 leaders / standings / team stats)\n")
    table(ingest)
    budget = sum(d for s in ingest
                 if (d := stat(by_script[s])["distinct200"]) <= 500)
    lines.append(f"\n**≤500 fetch budget: {budget} distinct captures** — proceeds without gating.\n")

    lines.append("## Game-level data — NOT this phase, but a major roadmap finding\n")
    lines.append(
        "Box scores and play-by-play, 2001–2021, were archived. B1 (the DevTools "
        "box-score hunt) has partial answers here. Every one of these is >500 → "
        "each needs its own gated tranche.\n"
    )
    table(game)

    lines.append("\n## Player / team pages (identity spine — gated)\n")
    table(player)

    lines.append("\n## Other non-noise root scripts (parked, unreviewed — top 25 by HTTP 200)\n")
    table(misc[:25], with_param=False)

    out = DOCS_DIR / "coverage_root.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[coverage] -> {out.relative_to(REPO_ROOT)}")
    return out


def main() -> int:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    paths = _fetch(session)
    _, rows = build_inventory(paths["root_all"])
    build_coverage(rows)
    print("\n[done] Root enumeration complete. Review docs/coverage_root.md before fetching.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
