"""PHASE_3E — parse archived game-level box scores into data/clean/.

Covers the two box-score families:
  gamestatwide.asp (2001-2004)  — per-player box, "attempted-made" shot cells,
    `REB off/def`, `FP` (fouls), `TP` (points). Game id from the `r=BS<NN>...`
    param (season = 1980 + NN).
  boxscore.asp / pogamestat.asp (2007-2014) — per-player box, "made-attempted"
    cells, `O D To` rebounds. Same game-id scheme. Layout is capture-era
    dependent; crammed "live" captures are skipped with a count.

Outputs (PC3-complete):
  data/clean/game_results.csv     one row per game — teams, final + quarter scores
  data/clean/game_box_player.csv  one row per player per game; `player_raw`
    resolved to `bsnpr_id` via the identity spine where a unique
    season-in-career match exists (D1), else left blank.

Run: `python -m src.parse_games`   (`make parse-games`)
"""

from __future__ import annotations

import csv
import json
import re
import sys
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

import pandas as pd

from src.wayback_cdx import REPO_ROOT
from src.parse_wayback import squish, to_int
from src.parse_pre2007 import _write_csv
from src.parse_players import normalize, norm_key

RAW_DIR = REPO_ROOT / "data" / "raw" / "games"
CLEAN = REPO_ROOT / "data" / "clean"
SOURCE_ID = "wayback_bsnpr_games"


# --------------------------------------------------------------------------- #
# identity resolver (D1) — reuse the spine's aliases + career spans           #
# --------------------------------------------------------------------------- #
def _load_resolver():
    alias_idx: dict[str, set[str]] = {}
    key_idx: dict[str, set[str]] = {}
    if (CLEAN / "player_aliases.csv").exists():
        with (CLEAN / "player_aliases.csv").open(encoding="utf-8") as fh:
            for a in csv.DictReader(fh):
                alias_idx.setdefault(a["normalized_alias"], set()).add(a["bsnpr_id"])
                key_idx.setdefault(norm_key(a["alias"]), set()).add(a["bsnpr_id"])
    career: dict[str, set[int]] = {}
    if (CLEAN / "player_career_seasons.csv").exists():
        with (CLEAN / "player_career_seasons.csv").open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                yr = to_int(r["season"])
                if yr:
                    career.setdefault(r["bsnpr_id"], set()).add(yr)
    return alias_idx, key_idx, career


def _resolve(name: str, season: int, alias_idx, key_idx, career) -> str:
    cands = alias_idx.get(normalize(name)) or key_idx.get(norm_key(name)) or set()
    if not cands:
        return ""
    corrob = {p for p in cands if p in career
              and min(career[p]) - 1 <= season <= max(career[p]) + 1}
    return next(iter(corrob)) if len(corrob) == 1 else ""


# --------------------------------------------------------------------------- #
def _iter(subdir: str):
    d = RAW_DIR / subdir
    if not d.exists():
        return
    for p in sorted(d.glob("*.html")):
        mp = p.with_name(p.name + ".meta.json")
        if not mp.exists():
            continue
        meta = json.loads(mp.read_text())
        retrieved_at = datetime.fromtimestamp(mp.stat().st_mtime, tz=timezone.utc)\
            .strftime("%Y-%m-%dT%H:%M:%SZ")
        yield p, meta, retrieved_at


def _season_from_rid(rid: str) -> int | None:
    m = re.match(r"BS(\d{2})", rid.upper())
    return 1980 + int(m.group(1)) if m else None


def _tables(html: str) -> list[pd.DataFrame]:
    try:
        return pd.read_html(StringIO(html), flavor="bs4")
    except (ValueError, Exception):  # noqa: BLE001
        return []


def _num_pair(cell: str) -> tuple[int | None, int | None]:
    """'19-7' -> (19, 7).  Order is source-specific; caller assigns."""
    m = re.match(r"\s*(\d+)\s*-\s*(\d+)", str(cell))
    return (to_int(m.group(1)), to_int(m.group(2))) if m else (None, None)


def _reb_pair(cell: str, sep: str) -> tuple[int | None, int | None]:
    m = re.match(rf"\s*(\d+)\s*{re.escape(sep)}\s*(\d+)", str(cell))
    return (to_int(m.group(1)), to_int(m.group(2))) if m else (None, None)


def _split_jugador(raw: str) -> tuple[str, str]:
    s = squish(raw)
    m = re.match(r"(\d{1,2})\s+(.+)", s)
    return (m.group(1), m.group(2)) if m else ("", s)


# --------------------------------------------------------------------------- #
def parse_gamestatwide(resolver, results: list[dict], box: list[dict]) -> int:
    n = 0
    alias_idx, key_idx, career = resolver
    for p, meta, retrieved_at in _iter("gamestatwide"):
        rid = squish(meta.get("r", ""))
        season = _season_from_rid(rid)
        src = meta.get("raw_wayback_url", "")
        try:
            html = p.read_bytes().decode("cp1252", "replace")
        except Exception:  # noqa: BLE001
            continue
        tabs = _tables(html)

        line = next((t for t in tabs if len(t) >= 3
                     and "TOTAL" in [str(x) for x in t.iloc[0]]
                     and "1st" in [str(x) for x in t.iloc[0]]), None)
        boxes = [t for t in tabs if len(t) > 2 and str(t.iloc[1, 0]).strip() == "JUGADOR"]
        if line is None or len(boxes) != 2:
            continue
        n += 1

        gdate = ""
        dm = re.match(r"(\d{1,2})/(\d{1,2})/(\d{2})", str(line.iloc[0, 0]))
        if dm:
            yy = int(dm.group(3))
            gdate = f"{2000 + yy}-{int(dm.group(1)):02d}-{int(dm.group(2)):02d}"

        teams = []
        for _, r in line.iloc[1:3].iterrows():
            vals = [str(x) for x in r]
            teams.append({"name": squish(vals[0]), "total": to_int(vals[-1]),
                          "q": [to_int(x) for x in vals[1:-1]]})
        results.append({
            "game_id": rid, "season": season or "", "date": gdate, "script": "gamestatwide.asp",
            "team_a_raw": teams[0]["name"], "score_a": teams[0]["total"],
            "team_b_raw": teams[1]["name"], "score_b": teams[1]["total"],
            "quarters_a": "-".join(str(x) for x in teams[0]["q"]),
            "quarters_b": "-".join(str(x) for x in teams[1]["q"]),
            "confidence": "single-source", "source_id": SOURCE_ID,
            "source_url": src, "retrieved_at": retrieved_at,
        })

        for tbl in boxes:
            team = squish(str(tbl.iloc[0, 0]))
            hdr = [squish(str(x)) for x in tbl.iloc[1]]
            for _, r in tbl.iloc[2:].iterrows():
                cells = {hdr[i]: r.iloc[i] for i in range(min(len(hdr), len(r)))}
                jug = squish(str(cells.get("JUGADOR", "")))
                if not jug or jug.lower().startswith("total"):
                    continue
                jersey, player_raw = _split_jugador(jug)
                fg3a, fg3m = _num_pair(cells.get("CC3I-CC3A", ""))     # attempted-made
                fg2a, fg2m = _num_pair(cells.get("CCI-CCA", ""))
                fta, ftm = _num_pair(cells.get("TLI-TLA", ""))
                oreb, dreb = _reb_pair(cells.get("REB off/def", ""), "/")
                pid = _resolve(player_raw, season, alias_idx, key_idx, career) if season else ""
                box.append({
                    "game_id": rid, "season": season or "", "date": gdate,
                    "team_raw": team, "jersey": jersey, "player_raw": player_raw,
                    "bsnpr_id": pid, "minutes": to_int(cells.get("MIN")),
                    "fg2m": fg2m, "fg2a": fg2a, "fg3m": fg3m, "fg3a": fg3a,
                    "ftm": ftm, "fta": fta, "oreb": oreb, "dreb": dreb,
                    "reb": (oreb + dreb) if oreb is not None and dreb is not None else None,
                    "ast": to_int(cells.get("AST")), "stl": to_int(cells.get("STEALS")),
                    "blk": to_int(cells.get("BK")), "pf": to_int(cells.get("FP")),
                    "tov": to_int(cells.get("TO")), "pts": to_int(cells.get("TP")),
                    "confidence": "single-source", "source_id": SOURCE_ID,
                    "source_url": src, "retrieved_at": retrieved_at,
                })
    return n


def parse_modern_box(resolver, results: list[dict], box: list[dict]) -> tuple[int, int]:
    """boxscore.asp + pogamestat.asp. Returns (parsed, skipped-crammed)."""
    alias_idx, key_idx, career = resolver
    parsed = skipped = 0
    for sub, script in (("boxscore", "boxscore.asp"), ("pogamestat", "pogamestat.asp")):
        for p, meta, retrieved_at in _iter(sub):
            rid = squish(meta.get("r", ""))
            season = _season_from_rid(rid)
            src = meta.get("raw_wayback_url", "")
            html = p.read_bytes().decode("cp1252", "replace")
            tabs = _tables(html)
            # clean player tables: header row has 'Name' and 'PTS'
            pt = [t for t in tabs if len(t) > 1
                  and "Name" in [str(x) for x in t.iloc[0]]
                  and "PTS" in [str(x) for x in t.iloc[0]]]
            if not pt:
                skipped += 1
                continue
            parsed += 1
            for tbl in pt:
                hdr = [squish(str(x)) for x in tbl.iloc[0]]
                # M A % triples for 2P, 3P, FT in order; then O D To; AS PF TO ST BS PTS
                for _, r in tbl.iloc[1:].iterrows():
                    v = [squish(str(x)) for x in r]
                    if len(v) < 20 or not v[1] or v[1].lower().startswith("total"):
                        continue
                    name = v[1]
                    pid = _resolve(name, season, alias_idx, key_idx, career) if season else ""
                    box.append({
                        "game_id": rid, "season": season or "", "date": "",
                        "team_raw": "", "jersey": v[0], "player_raw": name,
                        "bsnpr_id": pid, "minutes": None,
                        "fg2m": to_int(v[3]), "fg2a": to_int(v[4]),
                        "fg3m": to_int(v[6]), "fg3a": to_int(v[7]),
                        "ftm": to_int(v[9]), "fta": to_int(v[10]),
                        "oreb": to_int(v[12]), "dreb": to_int(v[13]),
                        "reb": to_int(v[14]) if len(v) > 14 else None,
                        "ast": to_int(v[15]), "pf": to_int(v[16]), "tov": to_int(v[17]),
                        "stl": to_int(v[18]), "blk": to_int(v[19]),
                        "pts": to_int(v[20]) if len(v) > 20 else None,
                        "confidence": "single-source", "source_id": SOURCE_ID,
                        "source_url": src, "retrieved_at": retrieved_at,
                    })
    return parsed, skipped


# --------------------------------------------------------------------------- #
# a2gamestatpbp.asp — play-by-play (2001-2004)                                  #
# --------------------------------------------------------------------------- #
_PBP_EVENT = [
    (r"3-pt .* hecho por", "made_3"),
    (r"3-pt .* fallado por", "miss_3"),
    (r"Tiro .* hecho por", "made_2"),
    (r"Tiro .* intentado por|Tiro .* fallado por", "miss_2"),
    (r"Tiro Libre .* hecho", "made_ft"),
    (r"Tiro Libre .* fallado", "miss_ft"),
    (r"Asistencia por", "assist"),
    (r"Rebote de Equipo", "team_rebound"),
    (r"Rebote por", "rebound"),
    (r"Corte por|Corte de", "steal"),
    (r"Tapon por|Bloqueo por", "block"),
    (r"Error \[", "turnover"),
    (r"Falta .* por|Falta por", "foul"),
    (r"Salto Inicial", "jump_ball"),
    (r"Tiempo|Time Out", "timeout"),
    (r"Sale .* Entra|Cambio", "substitution"),
]
_PBP_ACTOR = re.compile(
    r"por ([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ.\- ]+?)(?:\s*[\(<]\d+[\)>])?\s+de\s+([A-ZÁÉÍÓÚÑ ]+)\s*$")


def _pbp_fields(jugada: str) -> tuple[str, str, str]:
    """(event_type, actor_raw, team_raw) — best effort; jugada_raw is kept verbatim."""
    s = squish(jugada)
    etype = next((t for pat, t in _PBP_EVENT if re.search(pat, s, re.I)), "")
    m = _PBP_ACTOR.search(s)
    actor = squish(m.group(1)) if m else ""
    team = squish(m.group(2)) if m else ""
    return etype, actor, team


def parse_pbp(plays: list[dict]) -> int:
    n = 0
    for p, meta, retrieved_at in _iter("a2gamestatpbp"):
        rid = squish(meta.get("r", ""))
        season = _season_from_rid(rid)
        cuarto = squish(meta.get("cuarto", ""))
        src = meta.get("raw_wayback_url", "")
        html = p.read_bytes().decode("cp1252", "replace")
        tabs = _tables(html)
        tbl = next((t for t in tabs if len(t) > 5 and str(t.iloc[0, 0]) == "Cuarto"), None)
        if tbl is None:
            continue
        n += 1
        hdr = [str(x) for x in tbl.iloc[0]]
        local_team = squish(hdr[3].replace("Local", "")) if len(hdr) > 3 else ""
        visit_team = squish(hdr[4].replace("Vistante", "").replace("Visitante", "")) if len(hdr) > 4 else ""
        for seq, (_, r) in enumerate(tbl.iloc[1:].iterrows(), 1):
            v = [squish(str(x)) for x in r]
            jug = v[2] if len(v) > 2 else ""
            if not jug or jug.lower().startswith("primer |"):
                continue
            etype, actor, team = _pbp_fields(jug)
            plays.append({
                "game_id": rid, "season": season or "",
                "quarter": v[0] or cuarto, "clock": v[1] if len(v) > 1 else "",
                "seq": seq, "jugada_raw": jug,
                "event_type": etype, "actor_raw": actor, "team_raw": team,
                "local_team": local_team, "visit_team": visit_team,
                "local_score": to_int(v[3]) if len(v) > 3 else None,
                "visit_score": to_int(v[4]) if len(v) > 4 else None,
                "confidence": "single-source", "source_id": SOURCE_ID,
                "source_url": src, "retrieved_at": retrieved_at,
            })
    return n


PBP_COLS = ["game_id", "season", "quarter", "clock", "seq", "jugada_raw",
            "event_type", "actor_raw", "team_raw", "local_team", "visit_team",
            "local_score", "visit_score", "confidence", "source_id",
            "source_url", "retrieved_at"]

BOX_COLS = ["game_id", "season", "date", "team_raw", "jersey", "player_raw", "bsnpr_id",
            "minutes", "fg2m", "fg2a", "fg3m", "fg3a", "ftm", "fta", "oreb", "dreb", "reb",
            "ast", "stl", "blk", "pf", "tov", "pts",
            "confidence", "source_id", "source_url", "retrieved_at"]
RESULT_COLS = ["game_id", "season", "date", "script", "team_a_raw", "score_a",
               "team_b_raw", "score_b", "quarters_a", "quarters_b",
               "confidence", "source_id", "source_url", "retrieved_at"]


def main() -> int:
    if not RAW_DIR.exists():
        print("! data/raw/games missing — run `make fetch-games`", file=sys.stderr)
        return 1
    resolver = _load_resolver()
    results: list[dict] = []
    box: list[dict] = []

    n_gsw = parse_gamestatwide(resolver, results, box)
    n_mod, skipped = parse_modern_box(resolver, results, box)
    plays: list[dict] = []
    n_pbp = parse_pbp(plays)

    _write_csv(CLEAN / "game_results.csv",
               sorted(results, key=lambda r: (str(r["season"]), r["game_id"])), RESULT_COLS)
    _write_csv(CLEAN / "game_box_player.csv",
               sorted(box, key=lambda r: (str(r["season"]), r["game_id"], r["team_raw"], r["jersey"])),
               BOX_COLS)
    if plays:
        _write_csv(CLEAN / "game_plays.csv",
                   sorted(plays, key=lambda r: (r["game_id"], str(r["quarter"]), r["seq"])),
                   PBP_COLS)

    resolved = sum(1 for r in box if r["bsnpr_id"])
    print(f"[games] gamestatwide {n_gsw} games; modern box {n_mod} games ({skipped} crammed/skipped); "
          f"{len(box)} player-game rows, {resolved} resolved to bsnpr_id "
          f"({100 * resolved // max(len(box), 1)}%)")
    if n_pbp:
        etypes = {}
        for pl in plays:
            etypes[pl["event_type"] or "(unclassified)"] = etypes.get(pl["event_type"] or "(unclassified)", 0) + 1
        print(f"[pbp] {n_pbp} quarter-captures, {len(plays)} plays; event types: {etypes}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
