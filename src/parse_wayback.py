"""PHASE_3_PARSE — turn the fetched Wayback snapshots into provenance-complete
rows under data/clean/.

Inputs  (PC5: never re-fetched, read byte-for-byte from data/raw/):
  data/raw/campeonatos/*.html   79 champion-ledger captures, 2007–2021
  data/raw/lideres/*.html        114 season-leader captures, 1986 + 2007–2021
  each with a sibling *.meta.json (wayback timestamp, original_url, digest)

Outputs:
  data/interim/champions_bsnpr_long.csv     every ledger row of every capture
  data/interim/player_leaders_long.csv      every leader row of every capture
  data/interim/leader_capture_index.csv     (capture, category) -> row count
  data/clean/champions_from_bsnpr.csv       one row per season, latest capture wins
  data/clean/player_season_leaders.csv      one row per (season, category, rank)
  data/clean/seasons_stats_tracked.csv      per season, which categories carried data (PC2)

Design notes live in docs/specs/wayback_ingest_spec.md. Key rules honoured here:
  PC1  nothing invented — the `*` 1953 row is recorded as "no champion", not guessed.
  PC2  NULL != 0 — a missing stat cell parses to empty, never to 0.
  PC3  provenance on every clean row: source_id, source_url, retrieved_at, confidence.
  PC4  gaps are output — empty category tables become the stats_tracked signal;
       mid-season captures are flagged, not hidden.
  spec point 3  parse by column signature, never by table index.

Run: `python -m src.parse_wayback`   (`make parse`)
"""

from __future__ import annotations

import csv
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pandas as pd
from bs4 import BeautifulSoup

from src.wayback_cdx import REPO_ROOT

RAW_DIR = REPO_ROOT / "data" / "raw"
INTERIM_DIR = REPO_ROOT / "data" / "interim"
CLEAN_DIR = REPO_ROOT / "data" / "clean"
FRANCHISES_CSV = CLEAN_DIR / "bsn_franchises.csv"

SOURCE_ID = "wayback_bsnpr"

# Seasons the archive can actually speak to (docs/coverage_wayback.md): 1986 by a
# lucky 2017 crawl, then every year 2007–2021. verify_clean.py enforces this.
KNOWN_LEADER_SEASONS = {"1986"} | {str(y) for y in range(2007, 2022)}


# --------------------------------------------------------------------------- #
# text / encoding helpers                                                      #
# --------------------------------------------------------------------------- #
def decode_html(raw: bytes) -> str:
    """Decode a Wayback capture to text.

    The retired engine served iso-8859-1; the 2019+ rebuild serves utf-8; a
    handful of 2011–2013 captures are utf-8 with one stray invalid byte. Order:
    strict utf-8, then (if the page declares utf-8) lossy utf-8 so the one bad
    byte does not force a mojibake fallback, then cp1252, then latin-1 (which
    never raises). Spec [OPEN_QUESTIONS] Q8.
    """
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        pass
    head = raw[:4096].decode("latin-1", "ignore").lower()
    if "utf-8" in head or "utf8" in head:
        return raw.decode("utf-8", "replace")
    for enc in ("cp1252", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1", "replace")


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def squish(s) -> str:
    return re.sub(r"\s+", " ", str(s)).strip()


def to_int(v):
    """Parse an integer cell. Returns None for anything non-numeric (PC2)."""
    s = squish(v)
    if not s or s.lower() in ("nan", "-", "none"):
        return None
    try:
        return int(float(s))
    except ValueError:
        return None


def to_float(v):
    s = squish(v)
    if not s or s.lower() in ("nan", "-", "none"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def wayback_ts_to_date(ts: str) -> str:
    return f"{ts[0:4]}-{ts[4:6]}-{ts[6:8]}"


def read_tables(html: str) -> list[pd.DataFrame]:
    for flavor in ("lxml", "bs4"):
        try:
            return pd.read_html(StringIO(html), flavor=flavor)
        except ValueError:
            return []          # "No tables found" — a real, non-fatal outcome
        except Exception as exc:  # noqa: BLE001 - lxml chokes on some cruft; retry with bs4
            print(f"  ! read_html({flavor}) failed: {exc.__class__.__name__}: {exc}", file=sys.stderr)
    return []


# --------------------------------------------------------------------------- #
# capture discovery                                                            #
# --------------------------------------------------------------------------- #
def iter_captures(subdir: str):
    """Yield (html_text, meta_dict, retrieved_at_iso) for each raw capture."""
    d = RAW_DIR / subdir
    for html_path in sorted(d.glob("*.html")):
        meta_path = html_path.with_name(html_path.name + ".meta.json")
        if not meta_path.exists():
            print(f"  ! no meta for {html_path.name} — skipped", file=sys.stderr)
            continue
        meta = json.loads(meta_path.read_text())
        retrieved_at = datetime.fromtimestamp(
            meta_path.stat().st_mtime, tz=timezone.utc
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
        yield decode_html(html_path.read_bytes()), meta, retrieved_at


# --------------------------------------------------------------------------- #
# tranche A — campeonatos.asp champion ledger                                  #
# --------------------------------------------------------------------------- #
def find_champions_table(tables: list[pd.DataFrame]) -> pd.DataFrame | None:
    """The ledger table by header signature: EQUIPO + a *CAMPEON column."""
    for t in tables:
        cols = [strip_accents(str(c)).strip().upper() for c in t.columns]
        if "EQUIPO" in cols and any("CAMPEON" in c for c in cols):
            df = t.copy()
            df.columns = ["ano", "equipo", "dirigente", "subcampeon"][: len(cols)]
            return df
    return None


def parse_season_cell(raw) -> str:
    """AÑO cell -> a season key. campeonatos.asp folds the 1942–43 split into one
    `1942` row (D3); we keep whatever key the source used, unmodified."""
    s = squish(raw)
    m = re.match(r"\d{4}(?:\s*[-/]\s*\d{2,4})?", s)
    return m.group(0).replace(" ", "") if m else s


def clean_equipo(raw) -> tuple[str | None, str, bool]:
    """(champion_city, note, no_champion). A leading `*` marks a season with no
    champion of record — 1953, `* NO SE TERMINÓ (PONCE VS SAN GERMAN)` (D6)."""
    s = squish(raw)
    if s.startswith("*"):
        note = s.lstrip("* ").strip()
        return None, note or "no champion of record", True
    return s, "", False


def split_annotation(city: str, known_cities: set[str]) -> tuple[str, str]:
    """Some EQUIPO cells carry an annotation ahead of the city
    (`COPA OLIMPICA - CANOVANAS`, 1984). Split it off only when the tail is a
    city we recognise; otherwise leave the cell whole for review."""
    norm = strip_accents(city).upper().replace(" - ", " ")
    if norm in known_cities:
        return city, ""
    toks_norm = norm.split()
    toks_raw = re.split(r"\s+|\s-\s", city)
    for take in (2, 1):
        if len(toks_norm) > take and " ".join(toks_norm[-take:]) in known_cities:
            return " ".join(toks_raw[-take:]), " ".join(toks_raw[:-take]).strip(" -")
    return city, ""


def load_known_cities() -> set[str]:
    cities: set[str] = set()
    if FRANCHISES_CSV.exists():
        with FRANCHISES_CSV.open(encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                cities.add(strip_accents(row["city"]).upper())
    # cities that appear only as champions/runners-up in the ledger itself
    cities.update({"SAN JUAN", "SANTURCE", "RIO PIEDRAS", "UPR", "CANOVANAS", "ISABELA"})
    return cities


def parse_campeonatos() -> tuple[Path, Path]:
    """Tranche A. -> interim long CSV + clean per-season CSV."""
    known_cities = load_known_cities()
    long_rows: list[dict] = []
    # season -> list of dicts (one per capture that carried the season)
    by_season: dict[str, list[dict]] = {}

    n_caps = 0
    for html, meta, retrieved_at in iter_captures("campeonatos"):
        n_caps += 1
        ts = meta["wayback_timestamp"]
        src = meta["raw_wayback_url"]
        table = find_champions_table(read_tables(html))
        if table is None:
            print(f"  ! {ts}: no champion table", file=sys.stderr)
            continue

        for _, r in table.iterrows():
            season = parse_season_cell(r["ano"])
            if not re.match(r"^\d{4}", season):
                continue
            equipo_raw = squish(r.get("equipo", ""))
            dirigente_raw = squish(r.get("dirigente", ""))
            sub_raw = squish(r.get("subcampeon", ""))

            long_rows.append({
                "capture_timestamp": ts, "capture_date": wayback_ts_to_date(ts),
                "source_url": src, "season_raw": season,
                "equipo_raw": equipo_raw, "dirigente_raw": dirigente_raw,
                "subcampeon_raw": sub_raw,
            })

            champion_city, note, no_champ = clean_equipo(equipo_raw)
            parse_flag = "ok"
            if champion_city is not None:
                champion_city, ann = split_annotation(champion_city, known_cities)
                if ann:
                    note = (note + "; " if note else "") + ann
                if strip_accents(champion_city).upper() not in known_cities:
                    parse_flag = "review"

            if no_champ:
                # the `*` row repeats its text across all four cells — keep it in
                # the note only, leave champion / coach / runner-up empty (PC1).
                dirigente_raw, sub_raw = "", ""
            # read_html has already collapsed the runs of spaces that separated a
            # mid-season coach change ("DEL HARRIS  TOM NISSALKE"), so the split
            # point is gone. Keep the cell verbatim and flag the likely-multi
            # ones (4+ tokens, no comma) for a cleaner source to resolve later.
            coach_flag = "multi?" if (
                "," not in dirigente_raw and len(dirigente_raw.split()) >= 4
            ) else ""

            by_season.setdefault(season, []).append({
                "capture_timestamp": ts, "source_url": src, "retrieved_at": retrieved_at,
                "season": season, "no_champion": no_champ,
                "champion_city": champion_city or "", "coach": dirigente_raw,
                "coach_flag": coach_flag, "runner_up_city": sub_raw,
                "note": note, "parse_flag": parse_flag,
            })

    long_path = INTERIM_DIR / "champions_bsnpr_long.csv"
    _write_csv(long_path, long_rows, [
        "capture_timestamp", "capture_date", "source_url", "season_raw",
        "equipo_raw", "dirigente_raw", "subcampeon_raw",
    ])

    # --- dedup: latest capture wins; disagreements across captures -> disputed ---
    clean_rows: list[dict] = []
    for season, variants in sorted(by_season.items()):
        latest = max(variants, key=lambda v: v["capture_timestamp"])
        seen = {
            (v["champion_city"], v["runner_up_city"])
            for v in variants
            if v["champion_city"] or v["runner_up_city"]
        }
        confidence = "single-source"
        note = latest["note"]
        if len(seen) > 1:
            confidence = "disputed"
            note = (note + "; " if note else "") + (
                "captures disagree: " + " | ".join(
                    f"{c or '?'}/{r or '?'}" for c, r in sorted(seen)
                )
            )
        if season == "1945":
            # D5: the ledger's "SAN JUAN" is a city, not a club — it does not
            # settle Capitalinos vs Santos. Carried disputed per project rule.
            confidence = "disputed"
            note = (note + "; " if note else "") + (
                "D5: ledger city 'SAN JUAN' does not disambiguate "
                "Capitalinos de San Juan vs Santos de San Juan"
            )
        if latest["no_champion"]:
            confidence = "single-source"

        clean_rows.append({
            "season": season,
            "champion_city": latest["champion_city"],
            "coach": latest["coach"],
            "coach_flag": latest["coach_flag"],
            "runner_up_city": latest["runner_up_city"],
            "no_champion": latest["no_champion"],
            "note": note,
            "parse_flag": latest["parse_flag"],
            "confidence": confidence,
            "source_id": SOURCE_ID,
            "source_url": latest["source_url"],
            "retrieved_at": latest["retrieved_at"],
            "n_captures": len(variants),
        })

    clean_path = CLEAN_DIR / "champions_from_bsnpr.csv"
    _write_csv(clean_path, clean_rows, [
        "season", "champion_city", "coach", "coach_flag", "runner_up_city",
        "no_champion", "note", "parse_flag", "confidence",
        "source_id", "source_url", "retrieved_at", "n_captures",
    ])
    print(f"[campeonatos] {n_caps} captures -> {len(long_rows)} long rows, "
          f"{len(clean_rows)} seasons")
    return long_path, clean_path


# --------------------------------------------------------------------------- #
# tranches B/C — lideres.asp season-leader tables                              #
# --------------------------------------------------------------------------- #
# category identified by the aux column headers between JJ and Prom (spec pt 3)
CATEGORY_BY_AUX: dict[tuple[str, ...], tuple[str, str]] = {
    ("TOT",): ("anotaciones", "per_game"),
    ("DEF", "OFF", "TOT"): ("rebotes", "per_game"),
    ("TLA",): ("tiros_libres_anotados", "per_game"),
    ("TLI", "TLA"): ("tiros_libres_pct", "percentage"),
    ("CC3",): ("canastos_3", "per_game"),
    ("3PI", "3PA"): ("canastos_3_pct", "percentage"),
    ("TB",): ("bloqueos", "per_game"),
    ("CB",): ("cortes_balon", "per_game"),
    ("TO",): ("turnovers", "per_game"),
    ("RO",): ("rebotes_ofensivos", "per_game"),
    ("TA",): ("asistencias", "per_game"),
}
CLEAN_CATEGORIES = [c for c, _ in CATEGORY_BY_AUX.values()]


def classify_leader_table(columns) -> tuple[str, str, str, bool] | None:
    """(category, prom_kind, stat_columns, known) for a `# | Jugador | JJ | … |
    Prom` table, else None. Unknown aux signatures (FBP/PIP/SCP, appeared ~2013)
    are kept with a derived slug and known=False so no data is silently dropped."""
    cols = [squish(c) for c in columns]
    if len(cols) < 4 or cols[0] != "#" or cols[1] != "Jugador" or cols[2] != "JJ" or cols[-1] != "Prom":
        return None
    aux = tuple(c.upper() for c in cols[3:-1])
    stat_columns = "|".join(cols[3:-1])
    if aux in CATEGORY_BY_AUX:
        cat, kind = CATEGORY_BY_AUX[aux]
        return cat, kind, stat_columns, True
    slug = "cat_" + "_".join(re.sub(r"[^a-z0-9]", "", a.lower()) for a in aux)
    return slug, "unknown", stat_columns, False


def split_player_cell(raw) -> tuple[str, str]:
    """`"Apellido, Nombre (Club, Ciudad)"` -> (player_raw, club_raw), verbatim.
    Club may be a nickname, a city, both, empty (`"(  )"`), or a truncated
    nickname bleeding into the name (`"Morales, Mario 'Qui (Mets)"`). Identity
    resolution is a later phase (D1) — never here."""
    s = squish(raw)
    m = re.search(r"^(.*)\(([^()]*)\)\s*$", s)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return s, ""


SERIE_NAMES = {
    "1": "Serie Regular", "2": "Round Robin", "3": "Semi Final",
    "4": "Serie Final", "5": "Pre-Temporada", "13": "Cuartos de Final",
}


def selected_option_value(soup: BeautifulSoup, names: tuple[str, ...]) -> str:
    """The `value` of the selected <option> of the first matching <select>.

    The retired engine's markup often leaves option tags unclosed, so the
    *text* of a selected option concatenates every option after it — the
    `value` attribute stays clean and is what we key on.
    """
    for sel in soup.find_all("select"):
        if (sel.get("name") or "").lower() not in names:
            continue
        for opt in sel.find_all("option"):
            if opt.has_attr("selected"):
                return squish(opt.get("value") or opt.get_text())
    return ""


def page_context(soup: BeautifulSoup, meta: dict) -> tuple[str, str, str, bool, bool]:
    """(season, serie_context, grupo, career_view, is_regular) from URL params
    first, then the page's own <select> state. `is_regular` (serie value == "1")
    drives dedup — a "Serie Final" board shows finals-only totals, not season
    leaders (verified against 2011/2017 raw)."""
    q = parse_qs(urlsplit(meta["original_url"]).query)
    grupo = (q.get("grupo") or [""])[0]
    serie_param = (q.get("serie") or [""])[0]
    career = (q.get("vida") or [""])[0] == "2"
    season = (q.get("anio") or [""])[0] or selected_option_value(soup, ("anio", "sel3"))
    serie_val = serie_param or selected_option_value(soup, ("serie", "sel"))
    serie = SERIE_NAMES.get(serie_val, f"serie={serie_val}" if serie_val else "")
    is_regular = serie_val == "1"
    return season, serie, grupo, career, is_regular


def leader_rows(df: pd.DataFrame, category: str, prom_kind: str) -> list[dict]:
    cols = [squish(c) for c in df.columns]
    aux_names = [c.upper() for c in cols[3:-1]]
    out: list[dict] = []
    for _, r in df.iterrows():
        player_raw, club_raw = split_player_cell(r[df.columns[1]])
        aux = {name: r[df.columns[3 + i]] for i, name in enumerate(aux_names)}
        rec = {
            "rank": to_int(r[df.columns[0]]),
            "player_raw": player_raw, "club_raw": club_raw,
            "jj": to_int(r[df.columns[2]]),
            "total": None, "made": None, "attempted": None,
            "def_reb": None, "off_reb": None,
            "prom": to_float(r[df.columns[-1]]),
        }
        if category == "rebotes":
            rec["def_reb"], rec["off_reb"] = to_int(aux.get("DEF")), to_int(aux.get("OFF"))
            rec["total"] = to_int(aux.get("TOT"))
        elif category == "tiros_libres_pct":
            rec["attempted"], rec["made"] = to_int(aux.get("TLI")), to_int(aux.get("TLA"))
        elif category == "canastos_3_pct":
            rec["attempted"], rec["made"] = to_int(aux.get("3PI")), to_int(aux.get("3PA"))
        elif len(aux) == 1:
            rec["total"] = to_int(next(iter(aux.values())))
        if rec["player_raw"]:
            out.append(rec)
    return out


def _season_complete(season: str, capture_ts: str) -> bool:
    """A BSN season runs ~Mar–Aug of its own year; finals occasionally slip into
    autumn. Treat a capture on/after 1 Oct of the season year (or any later year)
    as showing settled numbers; earlier captures are flagged provisional."""
    try:
        sy = int(season)
    except ValueError:
        return False
    return capture_ts >= f"{sy}1001000000"


def parse_lideres() -> tuple[Path, Path, Path]:
    long_rows: list[dict] = []
    index_rows: list[dict] = []
    n_caps = 0

    for html, meta, retrieved_at in iter_captures("lideres"):
        n_caps += 1
        ts = meta["wayback_timestamp"]
        src = meta["raw_wayback_url"]
        soup = BeautifulSoup(html, "html.parser")
        season, serie, grupo, career, is_regular = page_context(soup, meta)
        cdate = wayback_ts_to_date(ts)

        seen_cats: set[str] = set()
        for table in read_tables(html):
            hit = classify_leader_table(table.columns)
            if hit is None:
                continue
            category, prom_kind, stat_columns, known = hit
            if category in seen_cats:
                continue
            seen_cats.add(category)
            rows = leader_rows(table, category, prom_kind)

            index_rows.append({
                "capture_timestamp": ts, "capture_date": cdate, "season": season,
                "serie_context": serie, "is_regular": is_regular,
                "career_view": career, "grupo": grupo,
                "category": category, "category_known": known, "n_rows": len(rows),
            })
            for rec in rows:
                long_rows.append({
                    "capture_timestamp": ts, "capture_date": cdate, "source_url": src,
                    "retrieved_at": retrieved_at, "season": season,
                    "serie_context": serie, "is_regular": is_regular,
                    "career_view": career, "grupo": grupo,
                    "category": category, "category_known": known,
                    "prom_kind": prom_kind, "stat_columns": stat_columns, **rec,
                })

    long_cols = [
        "capture_timestamp", "capture_date", "source_url", "retrieved_at", "season",
        "serie_context", "is_regular", "career_view", "grupo", "category",
        "category_known", "prom_kind", "stat_columns", "rank", "player_raw",
        "club_raw", "jj", "total", "made", "attempted", "def_reb", "off_reb", "prom",
    ]
    long_path = INTERIM_DIR / "player_leaders_long.csv"
    _write_csv(long_path, long_rows, long_cols)
    index_path = INTERIM_DIR / "leader_capture_index.csv"
    _write_csv(index_path, index_rows, [
        "capture_timestamp", "capture_date", "season", "serie_context", "is_regular",
        "career_view", "grupo", "category", "category_known", "n_rows",
    ])

    # --- dedup for the clean file --------------------------------------------
    # scope: real seasons only, BSN main group, season view (not career/"Vida"),
    # known stat categories. Everything else stays in the interim long file.
    def in_scope(row: dict) -> bool:
        return (
            not row["career_view"]
            and row["grupo"] in ("", "BS26")
            and row["category_known"]
            and re.fullmatch(r"\d{4}", str(row["season"] or ""))
        )

    # The clean file carries regular-season leader boards only. A "Serie Final"
    # capture shows finals-only totals (5–7 games), not season leaders — verified
    # against 2011/2017 raw. Seasons with no regular-season capture are reported
    # as gaps (PC4), not folded in with a caveat.
    scoped = [r for r in long_rows if in_scope(r) and r["is_regular"]]
    # latest regular-season capture per (season, category)
    best: dict[tuple[str, str], str] = {}
    for r in scoped:
        key = (r["season"], r["category"])
        if r["capture_timestamp"] > best.get(key, ""):
            best[key] = r["capture_timestamp"]

    clean_rows: list[dict] = []
    for r in scoped:
        key = (r["season"], r["category"])
        if r["capture_timestamp"] != best[key]:
            continue
        complete = _season_complete(r["season"], r["capture_timestamp"])
        note = f"regular-season leader board as of {r['capture_date']}"
        if not complete:
            note += "; season in progress at capture — provisional"
        clean_rows.append({
            "season": r["season"], "category": r["category"],
            "prom_kind": r["prom_kind"], "rank": r["rank"],
            "player_raw": r["player_raw"], "club_raw": r["club_raw"],
            "games": r["jj"], "total": r["total"], "made": r["made"],
            "attempted": r["attempted"], "def_reb": r["def_reb"],
            "off_reb": r["off_reb"], "prom": r["prom"],
            "season_complete": complete,
            "serie_context": r["serie_context"],
            "capture_date": r["capture_date"],
            "note": note,
            "confidence": "single-source",
            "source_id": SOURCE_ID, "source_url": r["source_url"],
            "retrieved_at": r["retrieved_at"],
        })
    clean_rows.sort(key=lambda r: (r["season"], r["category"], r["rank"] or 0))

    clean_path = CLEAN_DIR / "player_season_leaders.csv"
    _write_csv(clean_path, clean_rows, [
        "season", "category", "prom_kind", "rank", "player_raw", "club_raw",
        "games", "total", "made", "attempted", "def_reb", "off_reb", "prom",
        "season_complete", "serie_context", "capture_date", "note",
        "confidence", "source_id", "source_url", "retrieved_at",
    ])

    # --- coverage / gaps: one row per season the archive could speak to (PC4) --
    reg_seasons = {r["season"] for r in scoped}
    any_seasons = {
        r["season"] for r in index_rows
        if not r["career_view"] and r["grupo"] in ("", "BS26")
        and re.fullmatch(r"\d{4}", str(r["season"] or ""))
    }
    coverage_rows = []
    for s in sorted(KNOWN_LEADER_SEASONS):
        if s in reg_seasons:
            status, detail = "regular_season", ""
        elif s in any_seasons:
            ctx = sorted({
                r["serie_context"] for r in index_rows
                if r["season"] == s and not r["career_view"] and r["n_rows"] > 0
            })
            status = "playoff_only"
            detail = "only non-regular captures: " + ", ".join(c or "?" for c in ctx)
        else:
            status, detail = "not_archived", "no lideres.asp capture with content"
        coverage_rows.append({"season": s, "status": status, "detail": detail})
    coverage_path = CLEAN_DIR / "leader_coverage_gaps.csv"
    _write_csv(coverage_path, coverage_rows, ["season", "status", "detail"])

    # --- stats_tracked: per season, which categories carried data (PC2) -------
    tracked_path = _write_stats_tracked(index_rows)

    seasons = sorted(reg_seasons)
    playoff_only = sorted(s for s in any_seasons - reg_seasons)
    print(f"[lideres] {n_caps} captures -> {len(long_rows)} long rows, "
          f"{len(clean_rows)} clean rows across {len(seasons)} regular-season "
          f"seasons: {', '.join(seasons)}")
    if playoff_only:
        print(f"[lideres] playoff-only (excluded from clean, see gaps file): {', '.join(playoff_only)}")
    return long_path, clean_path, tracked_path


def _write_stats_tracked(index_rows: list[dict]) -> Path:
    """1 = category carried >=1 row in *any* in-scope capture of that season
        (proof the era tracked it, regardless of which series view);
    0 = the category table was present but empty in every capture (not tracked);
    '' = no capture of that season had the table at all.
    Uses all series views, not just regular season: an early-season capture can
    miss a stat that a later playoff-view capture of the same season shows."""
    rel = [
        r for r in index_rows
        if not r["career_view"] and r["grupo"] in ("", "BS26")
        and r["category_known"] and re.fullmatch(r"\d{4}", str(r["season"] or ""))
    ]
    seasons = sorted({r["season"] for r in rel})
    per: dict[str, dict[str, int]] = {s: {} for s in seasons}
    for r in rel:
        s = r["season"]
        cur = per[s].get(r["category"])
        val = 1 if r["n_rows"] > 0 else 0
        per[s][r["category"]] = max(val, cur) if cur is not None else val

    rows = []
    for s in seasons:
        row = {"season": s}
        for cat in CLEAN_CATEGORIES:
            v = per[s].get(cat)
            row[cat] = "" if v is None else v
        rows.append(row)

    path = CLEAN_DIR / "seasons_stats_tracked.csv"
    _write_csv(path, rows, ["season", *CLEAN_CATEGORIES])
    return path


# --------------------------------------------------------------------------- #
def _write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in fieldnames})
    print(f"  -> {path.relative_to(REPO_ROOT)} ({len(rows)} rows)")


def main() -> int:
    if not (RAW_DIR / "campeonatos").exists() or not (RAW_DIR / "lideres").exists():
        print("! data/raw/{campeonatos,lideres} missing — run `make fetch` first", file=sys.stderr)
        return 1
    print("[parse] tranche A — campeonatos.asp")
    parse_campeonatos()
    print("[parse] tranches B/C — lideres.asp")
    parse_lideres()
    print("\n[done] PHASE_3_PARSE. Run `make verify` to check the clean outputs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
