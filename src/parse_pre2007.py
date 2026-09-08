"""PHASE_3C parser — the root-level pre-2007 bsnpr.com pages fetched by
`src/fetch_pre2007.py` -> provenance-complete rows in `data/clean/`.

Same rules as PHASE_3 (`docs/global.md`, `docs/project.md`):
  PC1 nothing invented — the `* Feliciano vs Santori` scoring dispute is carried
      as two rows flagged `disputed`, not silently resolved.
  PC2 NULL != 0 — `to_int`/`to_float` (imported from parse_wayback) return None
      on a blank cell.
  PC3 provenance on every row: source_id, source_url, retrieved_at, confidence.
  PC4 gaps are output — DB-error captures (`ADODB.Field error`) are counted and
      reported, not silently skipped.

Outputs:
  data/clean/historic_scoring_champions.csv   lidereshistoricos.asp table 0, 1948->
  data/clean/historic_awards.csv              lidereshistoricos.asp MVP/ROY/DPOY
  data/clean/player_season_stats_2001_2004.csv  equiposstat.asp per-player totals
  data/clean/team_season_totals_2001_2004.csv   equiposstat.asp `Totales` row

Run: `python -m src.parse_pre2007`   (`make parse-pre2007`)
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
from bs4 import BeautifulSoup

from src.wayback_cdx import REPO_ROOT
from src.parse_wayback import decode_html, squish, to_int, to_float, wayback_ts_to_date, _write_csv

RAW_DIR = REPO_ROOT / "data" / "raw" / "pre2007"
CLEAN_DIR = REPO_ROOT / "data" / "clean"
SOURCE_ID = "wayback_bsnpr_root"


def _captures(script_dir: str):
    d = RAW_DIR / script_dir
    if not d.exists():
        return
    for html_path in sorted(d.glob("*.html")):
        meta_path = html_path.with_name(html_path.name + ".meta.json")
        if not meta_path.exists():
            continue
        meta = json.loads(meta_path.read_text())
        retrieved_at = datetime.fromtimestamp(
            meta_path.stat().st_mtime, tz=timezone.utc
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
        yield decode_html(html_path.read_bytes()), meta, retrieved_at


def _db_error(html: str) -> bool:
    return "ADODB." in html or "BOF or EOF" in html or "Microsoft OLE DB" in html


# --------------------------------------------------------------------------- #
# lidereshistoricos.asp                                                        #
# --------------------------------------------------------------------------- #
_SECTIONS = {
    "CAMPEONES ANOTADORES": "scoring",
    "DEFENSA DEL A": "defensive_player",
    "NOVATO DEL A": "rookie",
    "JUGADOR MAS VALIOSO": "mvp",
}


def _section_for(table) -> str | None:
    node = table.find_previous(string=re.compile(
        "|".join(re.escape(k) for k in _SECTIONS), re.I))
    if not node:
        return None
    up = squish(node).upper()
    for key, slug in _SECTIONS.items():
        if key in up:
            return slug
    return None


def parse_lidereshistoricos() -> tuple[Path, Path]:
    # historical compilation: take the single latest capture (most years).
    caps = sorted(_captures("lidereshistoricos"), key=lambda c: c[1]["wayback_timestamp"])
    if not caps:
        print("  ! no lidereshistoricos captures", file=sys.stderr)
        return (CLEAN_DIR / "historic_scoring_champions.csv",
                CLEAN_DIR / "historic_awards.csv")
    html, meta, retrieved_at = caps[-1]
    soup = BeautifulSoup(html, "html.parser")
    src = meta["raw_wayback_url"]
    cdate = wayback_ts_to_date(meta["wayback_timestamp"])

    footnote = ""
    m = re.search(r"\*\s*En algunos documentos[^.]+\.", squish(soup.get_text(" ")))
    if m:
        footnote = m.group(0)

    scoring: list[dict] = []
    awards: list[dict] = []
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if len(rows) < 6:
            continue
        section = _section_for(table)
        if section is None:
            continue
        for tr in rows[1:]:
            cells = [squish(td.get_text(" ")) for td in tr.find_all(["td", "th"])]
            if len(cells) < 3 or not re.fullmatch(r"\d{4}", cells[0]):
                continue
            season, player_raw, team_raw = cells[0], cells[1], cells[2]
            disputed = player_raw.startswith("*")
            player_clean = player_raw.lstrip("* ").strip()
            base = {
                "season": season, "player_raw": player_clean, "team_raw": team_raw,
                "confidence": "disputed" if disputed else "single-source",
                "note": footnote if disputed else "",
                "source_id": SOURCE_ID, "source_url": src, "retrieved_at": retrieved_at,
                "capture_date": cdate,
            }
            if section == "scoring":
                base.update({
                    "games": to_int(cells[3]) if len(cells) > 3 else None,
                    "total_points": to_int(cells[4]) if len(cells) > 4 else None,
                    "ppg": to_float(cells[5]) if len(cells) > 5 else None,
                    # D4: through 1969-70 the title went to total-points; from
                    # 1970-71 to ppg. This table carries both — keep both.
                    "metric_era": "total_points" if int(season) <= 1970 else "ppg",
                })
                scoring.append(base)
            else:
                base["award"] = section
                awards.append(base)

    sp = CLEAN_DIR / "historic_scoring_champions.csv"
    _write_csv(sp, scoring, [
        "season", "player_raw", "team_raw", "games", "total_points", "ppg",
        "metric_era", "note", "confidence", "source_id", "source_url",
        "retrieved_at", "capture_date",
    ])
    ap = CLEAN_DIR / "historic_awards.csv"
    _write_csv(ap, sorted(awards, key=lambda r: (r["award"], r["season"])), [
        "award", "season", "player_raw", "team_raw", "note", "confidence",
        "source_id", "source_url", "retrieved_at", "capture_date",
    ])
    yrs = sorted(r["season"] for r in scoring)
    print(f"[lidereshistoricos] scoring {len(scoring)} rows {yrs[0]}–{yrs[-1]}; "
          f"awards {len(awards)} rows ({len({r['award'] for r in awards})} categories)")
    return sp, ap


# --------------------------------------------------------------------------- #
# equiposstat.asp — per-team, per-player season stats 2001–2004                 #
# --------------------------------------------------------------------------- #
# PUNTOS ACUMULADOS columns (season totals). CC/3P/TL arrive as "made-att".
_ACU_COLS = ["jersey", "player_raw", "games", "_x", "minutes", "fg", "tp", "ft",
             "dreb", "treb", "ast", "stl", "blk", "tov", "pts", "_y"]
# PROMEDIO POR JUGADOR columns (per game / pct).
_AVG_COLS = ["jersey", "player_raw", "games", "_x", "mpg", "fg_pct", "tp_pct",
             "ft_pct", "dreb_pg", "treb_pg", "ast_pg", "stl_pg", "blk_pg",
             "tov_pg", "ppg"]


def _split_att_made(v):
    """`CC`/`3P`/`TL` cells are `"<attempted>-<made>"` — verified against the
    PROMEDIO table's percentages (e.g. `"151-90"` -> 90/151 = 0.596 = CC%)."""
    s = squish(v)
    m = re.match(r"(\d+)\s*-\s*(\d+)", s)
    return (to_int(m.group(1)), to_int(m.group(2))) if m else (None, None)


def _team_and_season(soup: BeautifulSoup) -> tuple[str, str, str]:
    """(team_name, season, serie) from the page heading / selects."""
    txt = squish(soup.get_text(" "))
    m = re.search(r"([A-Za-zÁÉÍÓÚñÑ]+ de [A-Za-zÁÉÍÓÚñÑ]+|Vaqueros|Cangrejeros|"
                  r"Capitanes|Leones|Piratas|Mets|Atléticos|Atleticos|Indios|"
                  r"Gallitos|Brujos|Criollos|Gigantes|Maratonistas|Polluelos|"
                  r"Cardenales|Titanes)\s+(\d{4})", txt)
    team = m.group(1) if m else ""
    season = m.group(2) if m else ""
    serie = ""
    sm = re.search(r"Serie:\s*(Serie Regular|Round Robin|Semi ?Final[a-z ]*|Serie Final)", txt, re.I)
    if sm:
        serie = squish(sm.group(1))
    return team, season, serie


def parse_equiposstat() -> tuple[Path, Path]:
    players: list[dict] = []
    teams: list[dict] = []
    n_caps = n_err = 0
    seen: set[tuple] = set()

    for html, meta, retrieved_at in _captures("equiposstat"):
        n_caps += 1
        if _db_error(html):
            n_err += 1
            continue
        soup = BeautifulSoup(html, "html.parser")
        team, season, serie = _team_and_season(soup)
        if not season:
            continue
        src = meta["raw_wayback_url"]
        cdate = wayback_ts_to_date(meta["wayback_timestamp"])
        try:
            tables = pd.read_html(StringIO(html))
        except ValueError:
            continue

        acu = _avg = None
        for t in tables:
            head = str(t.iloc[0, 0]).upper()
            if "ACUMULADOS" in head:
                acu = t
            elif "PROMEDIO POR JUGADOR" in head:
                _avg = t
        if acu is None:
            continue

        # dedup: one (team, season, serie) — keep the latest capture
        key = (team, season, serie)
        if key in seen:
            continue
        seen.add(key)

        avg_by_player: dict[str, list] = {}
        if _avg is not None:
            for _, r in _avg.iloc[2:].iterrows():
                vals = r.tolist()
                if len(vals) >= 15:
                    avg_by_player[squish(vals[1])] = vals

        for _, r in acu.iloc[2:].iterrows():
            vals = r.tolist()
            if len(vals) < 15:
                continue
            name = squish(vals[1])
            rec = {
                "season": season, "team_raw": team, "serie": serie,
                "jersey": squish(vals[0]) or "", "player_raw": name,
                "games": to_int(vals[2]), "minutes": to_int(vals[4]),
                "pts": to_int(vals[14]), "dreb": to_int(vals[8]),
                "treb": to_int(vals[9]), "ast": to_int(vals[10]),
                "stl": to_int(vals[11]), "blk": to_int(vals[12]),
                "tov": to_int(vals[13]),
                "source_id": SOURCE_ID, "source_url": src,
                "retrieved_at": retrieved_at, "capture_date": cdate,
                "confidence": "single-source",
            }
            rec["fga"], rec["fgm"] = _split_att_made(vals[5])
            rec["tpa"], rec["tpm"] = _split_att_made(vals[6])
            rec["fta"], rec["ftm"] = _split_att_made(vals[7])
            av = avg_by_player.get(name)
            rec["ppg"] = to_float(av[14]) if av and len(av) > 14 else None
            rec["fg_pct"] = to_float(av[5]) if av and len(av) > 5 else None

            if name.lower() == "totales" or squish(vals[0]) == "" and name.lower().startswith("total"):
                t_rec = {k: rec[k] for k in rec if k not in ("jersey", "player_raw")}
                t_rec["n_players_listed"] = None
                teams.append(t_rec)
            elif name:
                players.append(rec)

    pp = CLEAN_DIR / "player_season_stats_2001_2004.csv"
    _write_csv(pp, players, [
        "season", "team_raw", "serie", "jersey", "player_raw", "games", "minutes",
        "fgm", "fga", "tpm", "tpa", "ftm", "fta", "dreb", "treb", "ast", "stl",
        "blk", "tov", "pts", "ppg", "fg_pct", "confidence", "source_id",
        "source_url", "retrieved_at", "capture_date",
    ])
    tp = CLEAN_DIR / "team_season_totals_2001_2004.csv"
    _write_csv(tp, teams, [
        "season", "team_raw", "serie", "games", "minutes", "fgm", "fga", "tpm",
        "tpa", "ftm", "fta", "dreb", "treb", "ast", "stl", "blk", "tov", "pts",
        "confidence", "source_id", "source_url", "retrieved_at", "capture_date",
    ])
    print(f"[equiposstat] {n_caps} captures ({n_err} DB-error), "
          f"{len(players)} player-seasons, {len(teams)} team-seasons, "
          f"{len(seen)} distinct (team, season, serie)")
    return pp, tp


# --------------------------------------------------------------------------- #
# lideres2000.asp / lideres2001.asp / lideres2002.asp — <pre> leader blocks     #
# --------------------------------------------------------------------------- #
# stat-column signature (between JJ and Prom) -> category, same idea as PHASE_3
_PRE_CATEGORY = {
    ("TP",): ("anotaciones", "per_game"),
    ("DEF", "OFF", "TOT"): ("rebotes", "per_game"),
    ("TA",): ("asistencias", "per_game"),
    ("TLA",): ("tiros_libres_anotados", "per_game"),
    ("TLI", "TLA"): ("tiros_libres_pct", "percentage"),
    ("CC3",): ("canastos_3", "per_game"),
    ("3PI", "3PA"): ("canastos_3_pct", "percentage"),
    ("TB",): ("bloqueos", "per_game"),
    ("CB",): ("cortes_balon", "per_game"),
    ("TO",): ("turnovers", "per_game"),
    ("RO",): ("rebotes_ofensivos", "per_game"),
}
_PRE_ROW = re.compile(
    r"^\s*(\d+)\.\s+(.+?)\s+\(([A-Za-z .]+)\)\s+(\d+)\s+(.+?)\s+([\d.]+)\s*$")
_SERIE_BY_PARAM = {"1": "Serie Regular", "3": "Semi Final", "4": "Serie Final"}


def parse_lideres_200x() -> Path:
    rows: list[dict] = []
    # (season, category, serie) -> latest capture ts kept
    best: dict[tuple, str] = {}
    staged: dict[tuple, list[dict]] = {}

    for script_dir, season in (("lideres2000", "2000"), ("lideres2001", "2001"),
                               ("lideres2002", "2002")):
        for html, meta, retrieved_at in _captures(script_dir):
            ts = meta["wayback_timestamp"]
            src = meta["raw_wayback_url"]
            cdate = wayback_ts_to_date(ts)
            q = meta.get("query", "")
            sm = re.search(r"serie=(\d+)", q)
            serie = _SERIE_BY_PARAM.get(sm.group(1) if sm else "", "" if not sm else f"serie={sm.group(1)}")

            for block in re.finditer(r"<pre>(.*?)</pre>", html, re.S | re.I):
                text = block.group(1).replace("&nbsp;", " ")
                lines = [ln for ln in text.splitlines() if ln.strip()]
                if not lines:
                    continue
                hdr = squish(re.sub(r"<[^>]+>", "", lines[0])).upper().split()
                if hdr[:1] != ["JUGADOR"] or hdr[-1] != "PROM" or "JJ" not in hdr:
                    continue
                aux = tuple(hdr[hdr.index("JJ") + 1:-1])
                hit = _PRE_CATEGORY.get(aux)
                if not hit:
                    continue
                category, prom_kind = hit

                key = (season, category, serie)
                if best.get(key, "") > ts:
                    continue
                if best.get(key) != ts:
                    best[key] = ts
                    staged[key] = []

                for ln in lines[1:]:
                    m = _PRE_ROW.match(re.sub(r"<[^>]+>", "", ln))
                    if not m:
                        continue
                    rank, player_raw, club_raw, jj, mid, prom = m.groups()
                    nums = [to_int(x) for x in mid.split()]
                    rec = {
                        "season": season, "category": category, "prom_kind": prom_kind,
                        "serie": serie, "rank": to_int(rank),
                        "player_raw": squish(player_raw), "club_raw": squish(club_raw),
                        "games": to_int(jj), "prom": to_float(prom),
                        "v1": nums[0] if len(nums) > 0 else None,
                        "v2": nums[1] if len(nums) > 1 else None,
                        "v3": nums[2] if len(nums) > 2 else None,
                        "capture_date": cdate, "confidence": "single-source",
                        "source_id": SOURCE_ID, "source_url": src,
                        "retrieved_at": retrieved_at,
                    }
                    # fixed-width overflow can clip a counting stat (e.g. "101"->"01");
                    # flag when v1 is implausible vs prom*games, never rewrite it (PC1).
                    if (prom_kind == "per_game" and rec["v1"] is not None
                            and rec["games"] and rec["prom"]
                            and rec["v1"] < 0.6 * rec["prom"] * rec["games"]):
                        rec["parse_flag"] = "value_maybe_clipped"
                    else:
                        rec["parse_flag"] = ""
                    staged[key].append(rec)

    for recs in staged.values():
        rows.extend(recs)
    rows.sort(key=lambda r: (r["season"], r["category"], r["serie"], r["rank"] or 0))

    path = CLEAN_DIR / "player_season_leaders_2000_2002.csv"
    _write_csv(path, rows, [
        "season", "category", "prom_kind", "serie", "rank", "player_raw",
        "club_raw", "games", "v1", "v2", "v3", "prom", "parse_flag",
        "confidence", "source_id", "source_url", "retrieved_at", "capture_date",
    ])
    seas = sorted({r["season"] for r in rows})
    print(f"[lideres200x] {len(rows)} rows, seasons {seas}, "
          f"{len({(r['season'], r['category'], r['serie']) for r in rows})} (season,category,serie) groups")
    return path


def main() -> int:
    if not RAW_DIR.exists():
        print("! data/raw/pre2007 missing — run `python -m src.fetch_pre2007` first", file=sys.stderr)
        return 1
    print("[parse-pre2007] lidereshistoricos.asp")
    parse_lidereshistoricos()
    print("[parse-pre2007] lideres2000/2001/2002.asp")
    parse_lideres_200x()
    print("[parse-pre2007] equiposstat.asp")
    parse_equiposstat()
    print("\n[done] PHASE_3C parse. `make verify` next.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
