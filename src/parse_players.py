"""PHASE_3D — build the player identity spine (D1).

Sources (fetched by `src/fetch_players.py`):
  data/raw/players/enciclopedia/*.html   the all-time directory: Apellidos |
    Nombre | Camisa | Nació, one /jugadores/jugador.asp?id=N link per row.
  data/raw/players/jugador/<id>_<ts>.html  per-player profile: full name incl.
    nickname, birth city + date, position, height/weight, career-by-season table.

Outputs (all PC3-complete):
  data/clean/players_canonical.csv    one row per bsnpr_id — canonical_name,
    normalized_name, apellidos, nombre, birth_date, birth_year, first_season,
    last_season, position, nationality (from jugador.asp where available).
  data/clean/player_aliases.csv       bsnpr_id, alias, alias_type, source.
  data/clean/player_career_seasons.csv  bsnpr_id, season, team_raw (jugador.asp).
  data/clean/player_bios.csv          bsnpr_id -> 2005-06 scouting prose +
    birthplace/roster context (jugador05.asp, enrich-only — PHASE_3H follow-up).
  data/clean/player_id_map.csv        observation player_raw -> bsnpr_id, with
    match_method + confidence. Only rows that clear the D1 bar land here.
  data/interim/player_review_queue.csv  everything that did not — ambiguous or
    name-only matches, with the candidate ids and the reason.

Curated inputs (hand-maintained, consulted by the build):
  data/interim/jug05_xwalk.csv / jugador05_xwalk.csv  nickname bridges (PHASE_3H)
  data/interim/player_dob_overrides.csv  birth-date corrections (PHASE_3H)
  data/interim/player_historic_seed.csv + app/player_crosswalk.csv  curated
    name→id for the 1948–2004 scoring champions (PHASE_3I); scoring titles seed
    `first_season`/`last_season` and corroborate via `match_method=name+season+title`.
  PHASE_3J — `build_id_map` season-gated fallbacks for clipped / bare-surname
    observation names: `name+season+trunc`, `surname+season+club`.

D1 rules enforced:
  - canonical ids are the league's own (`?id=N`) — no fuzzy dedup *within* the
    canonical table.
  - linking an observation name to an id needs corroboration beyond the name:
    the observed season must fall in the player's career span AND the observed
    club must be consistent. A unique name match with no corroboration goes to
    the review queue, never the id map ("never on name alone").
  - accent-stripped `normalized_name` + an alias table, per D1.

Run: `python -m src.parse_players`   (`make parse-players`)
"""

from __future__ import annotations

import csv
import json
import re
import sys
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

from src.wayback_cdx import REPO_ROOT
from src.parse_wayback import decode_html, squish, to_int
from src.parse_pre2007 import _write_csv  # noqa: F401 - re-exported helper
from src.city_season_overrides import OVERRIDES_FILE, load_overrides, override_for

RAW_DIR = REPO_ROOT / "data" / "raw" / "players"
CLEAN_DIR = REPO_ROOT / "data" / "clean"
INTERIM_DIR = REPO_ROOT / "data" / "interim"
SOURCE_ID = "wayback_bsnpr_players"

# observation files whose player_raw strings we try to resolve to a bsnpr_id
OBSERVATION_FILES = [
    ("player_season_leaders.csv", "player_raw", "club_raw", "season"),
    ("player_season_leaders_2000_2002.csv", "player_raw", "club_raw", "season"),
    ("player_season_stats_2001_2004.csv", "player_raw", "team_raw", "season"),
    ("historic_scoring_champions.csv", "player_raw", "team_raw", "season"),
    # backlog item 4 addendum (MVP-season marking, 2026-09-14) — MVP/Rookie/
    # DPOY awards were never run through identity resolution at all before
    # this; scoring champions got the equivalent treatment in PHASE_3I. Every
    # resolved row this adds used the plain existing name+season_in_career
    # tier (verified: no title-tier fallback was needed for any of the 36
    # MVP rows that resolved), so no _TITLE_FILES change was needed either.
    ("historic_awards.csv", "player_raw", "team_raw", "season"),
]


# --------------------------------------------------------------------------- #
# name normalisation                                                           #
# --------------------------------------------------------------------------- #
def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def normalize(s: str) -> str:
    """accent-stripped, lowercased, punctuation/whitespace collapsed."""
    s = strip_accents(s).lower()
    s = re.sub(r"['`.‘’“”\"]", "", s)
    s = re.sub(r"[^a-z0-9 ,]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def norm_key(s: str) -> str:
    """comma/space-insensitive sorted-token key for matching "Apellido, Nombre"
    against "Nombre Apellido" and initials."""
    toks = [t for t in re.split(r"[ ,]+", normalize(s)) if t]
    return " ".join(sorted(toks))


_NICK_RE = re.compile(r"['‘’\"]([^'‘’\"]{2,})['‘’\"]?")


def extract_nickname(name: str) -> str:
    m = _NICK_RE.search(name)
    return squish(m.group(1)) if m else ""


def strip_nickname(name: str) -> str:
    return squish(_NICK_RE.sub("", name).replace("()", "")).strip(" ,")


# --------------------------------------------------------------------------- #
# tranche A — enciclopedia directory                                           #
# --------------------------------------------------------------------------- #
def _iter_files(subdir: str):
    d = RAW_DIR / subdir
    if not d.exists():
        return
    for p in sorted(d.glob("*.html")):
        mp = p.with_name(p.name + ".meta.json")
        meta = json.loads(mp.read_text()) if mp.exists() else {}
        retrieved_at = datetime.fromtimestamp(
            (mp if mp.exists() else p).stat().st_mtime, tz=timezone.utc
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
        yield p, decode_html(p.read_bytes()), meta, retrieved_at


def parse_enciclopedia() -> dict[str, dict]:
    """bsnpr_id -> merged directory record."""
    players: dict[str, dict] = {}
    n_caps = 0
    for _p, html, meta, retrieved_at in _iter_files("enciclopedia"):
        n_caps += 1
        ts = meta.get("wayback_timestamp", "")
        src = meta.get("raw_wayback_url", "")
        ids = re.findall(r"jugador\.asp\?id=(\d+)", html)
        try:
            tables = [t for t in pd.read_html(StringIO(html))
                      if {"Apellidos", "Nombre"} <= set(map(str, t.columns))]
        except ValueError:
            tables = []
        if not tables or len(ids) != len(tables[0]):
            continue
        tbl = tables[0]
        for pid, (_, row) in zip(ids, tbl.iterrows()):
            apellidos = squish(row["Apellidos"])
            nombre_raw = squish(row["Nombre"])
            nacio = clean_dob(squish(row.get("Nació", ""))) if "Nació" in tbl.columns else ""
            camisa = squish(row.get("Camisa", ""))
            rec = players.setdefault(pid, {
                "bsnpr_id": pid, "apellidos": "", "nombre": "", "nickname": "",
                "birth_date": "", "jerseys": set(), "enc_captures": 0,
                "first_seen": ts, "last_seen": ts, "source_url": src,
                "retrieved_at": retrieved_at,
            })
            rec["enc_captures"] += 1
            rec["last_seen"] = max(rec["last_seen"], ts)
            # latest capture wins for the name (corrections accrete over time)
            if ts >= rec["last_seen"] or not rec["apellidos"]:
                rec["apellidos"] = apellidos or rec["apellidos"]
                rec["nombre"] = strip_nickname(nombre_raw) or rec["nombre"]
            nick = extract_nickname(nombre_raw)
            if nick and not rec["nickname"]:
                rec["nickname"] = nick
            if nacio and not rec["birth_date"]:
                rec["birth_date"] = nacio
                rec["source_url"] = src
                rec["retrieved_at"] = retrieved_at
            if camisa and camisa.lower() != "nan":
                rec["jerseys"].add(re.sub(r"\.0$", "", camisa))
    print(f"[enciclopedia] {n_caps} captures -> {len(players)} distinct player ids")
    return players


# --------------------------------------------------------------------------- #
# tranche B — per-player profiles                                              #
# --------------------------------------------------------------------------- #
_DATE_RE = re.compile(r"\b(\d{1,2}/\d{1,2}/\d{4})\b")
# the source writes an unknown DOB as 1/1/1900 — treat as null (PC2).
_DOB_SENTINELS = {"1/1/1900", "01/01/1900"}


def clean_dob(raw: str) -> str:
    m = _DATE_RE.search(raw or "")
    if not m or m.group(1) in _DOB_SENTINELS:
        return ""
    return m.group(1)


# jugador.asp fills an unknown field with a placeholder rather than leaving it
# blank; `read_html` also stringifies an empty cell as "nan". Treat all of these
# as null (PC2). "Estadísticas Jugador" is a section header the heading scan
# grabbed when the page had no real <h*> name — 725 profiles were affected and
# ended up canonically named "<Surname>, Estadísticas Jugador".
_FIELD_SENTINELS = {"", "nan", "no se sabe", "estadisticas jugador",
                    "estadistica jugador", "jugador", "jugadores",
                    "not found", "bad request", "forbidden",
                    "internal server error", "service unavailable"}

# A failed fetch/scrape sometimes concatenated an HTTP status line onto (or into)
# a field — e.g. nombre "Error 404 Not Found" for id 405/1926/2089, whose
# apellidos ("Frazer Thorne" etc.) are legitimate two-part surnames. Strip the
# status token (+ any trailing reason phrase); keep whatever real text is left.
_HTTP_ERR = re.compile(
    r"\s*\b(?:https?\s+)?(?:error|err|http|status)\s*[:\-]?\s*[1-5]\d{2}\b"
    r"(?:[\s:\-]+(?:not\s+found|bad\s+request|forbidden|unauthorized|"
    r"internal\s+server\s+error|service\s+unavailable|gateway\s+timeout))?\.?",
    re.I)


def clean_field(raw: str) -> str:
    s = squish(_HTTP_ERR.sub(" ", squish(raw or "")))
    return "" if normalize(s) in _FIELD_SENTINELS else s


def parse_jugador() -> tuple[dict[str, dict], list[dict]]:
    """bsnpr_id -> profile enrichment;  + list of career-season rows."""
    profiles: dict[str, dict] = {}
    career: list[dict] = []
    n = 0
    for p, html, meta, retrieved_at in _iter_files("jugador"):
        n += 1
        pid = meta.get("player_id") or p.stem.split("_")[0]
        src = meta.get("raw_wayback_url", "")
        ts = meta.get("wayback_timestamp", "")
        soup = BeautifulSoup(html, "html.parser")

        # some jugador.asp snapshots captured the site's "Error 404 - Not Found"
        # page instead of a profile — skip so its heading can't leak into a name
        # (ids 405 / 1926 / 2089 were canonically "<Surname>, Error 404").
        title = squish(soup.title.get_text()) if soup.title else ""
        if re.match(r"error\s*[1-5]\d{2}\b", normalize(title)):
            continue

        heading = ""
        for tag in soup.find_all(["h1", "h2", "h3", "h4"]):
            t = clean_field(tag.get_text())
            if t:
                heading = t
                break

        try:
            tables = pd.read_html(StringIO(html))
        except ValueError:
            tables = []

        ciudad = posicion = birth = ""
        for t in tables:
            cells0 = [squish(str(x)) for x in t.iloc[0].tolist()]
            if "Nacimiento" in cells0 and len(t) > 1:
                vals = [squish(str(x)) for x in t.iloc[1].tolist()]
                row = dict(zip(cells0, vals))
                ciudad = clean_field(row.get("Ciudad", ""))
                posicion = clean_field(row.get("Posición", "") or row.get("Posicion", ""))
                birth = clean_dob(row.get("Nacimiento", ""))
                break

        seasons: list[int] = []
        for t in tables:
            cols = [squish(str(c)) for c in t.columns]
            if cols[:2] != ["Año", "Equipo"]:
                continue
            for _, r in t.iterrows():
                yr = to_int(r["Año"])
                if not yr or yr < 1929 or yr > 2030:
                    continue
                seasons.append(yr)
                career.append({
                    "bsnpr_id": pid, "season": yr, "team_raw": squish(str(r["Equipo"])),
                    "games": to_int(r.get("JJ")), "points": to_int(r.get("PTS")),
                    "source_id": SOURCE_ID, "source_url": src,
                    "retrieved_at": retrieved_at,
                })

        nationality = ""
        if ciudad:
            country = ciudad.split(",")[-1].strip()
            nationality = "Puerto Rico" if "puerto rico" in country.lower() else country

        profiles[pid] = {
            "bsnpr_id": pid, "profile_name": strip_nickname(heading),
            "profile_nickname": extract_nickname(heading),
            "birth_date": birth, "position": posicion, "nationality": nationality,
            "birth_city": ciudad,
            "first_season": min(seasons) if seasons else None,
            "last_season": max(seasons) if seasons else None,
            "n_seasons": len(set(seasons)),
            "source_url": src, "retrieved_at": retrieved_at, "capture_ts": ts,
        }
    print(f"[jugador] {n} profiles parsed, {len(career)} career-season rows")
    return profiles, career


# --------------------------------------------------------------------------- #
# tranche C — jug05.asp (PHASE_3H)                                             #
# --------------------------------------------------------------------------- #
JUG05_SOURCE_ID = "wayback_bsnpr_jug05"

# jug05.asp keeps ONE slot for the newest season and labels it "2005" on every capture. Until the
# capture of 2006-02-24 the slot holds the figures jugador.asp files under 2005; from the capture of
# 2006-05-28 it holds the ones jugador.asp files under 2006 (the source overwrote it in place and kept
# the label). So for that one label the capture date, not the page, says which season the row is.
# No capture lies between 2006-02-24 and 2006-05-28 with a 2005 row (the only two, of 2006-04-27, have
# none), so any cutoff in that gap gives the same rows. docs/specs/jug05_offset_check.md.
JUG05_SLOT_LABEL = 2005
JUG05_SLOT_FLIP = "20060501000000"          # Wayback timestamp, YYYYMMDDhhmmss
_WAYBACK_TS = re.compile(r"/web/(\d{14})")


def jug05_capture_ts(source_url) -> str:
    """The 14-digit Wayback timestamp inside a capture URL, "" when there is none."""
    m = _WAYBACK_TS.search(source_url or "")
    return m.group(1) if m else ""


def jug05_season(label: int, capture_ts: str) -> int:
    """The season a jug05 row belongs to: its page label, except that the newest-season slot
    ("2005") captured on or after JUG05_SLOT_FLIP holds the next season's figures. The ONE place
    this is decided; parse_jug05 and src/apply_jug05_relabel.py both call it."""
    if label == JUG05_SLOT_LABEL and capture_ts and capture_ts >= JUG05_SLOT_FLIP:
        return label + 1
    return label
_J5_NAME = re.compile(r"Estad[ií]sticas\s+Jugador\s+(.+?)\s+Ciudad\s+Nacimiento", re.S)
_J5_BIO = re.compile(r"Ciudad\s+Nacimiento\s+Edad\s+Posici[oó]n\s+Altura\s+Peso\s+"
                     r"(.*?)\s+A[nñ]o\s+Equipo\s+3pi", re.S)
_J5_DOB = re.compile(r"\b(\d{1,2}/\d{1,2}/\d{4})\b")
_J5_POS = re.compile(r"\b(Armador|Escolta|Alero|Delantero|Centro)"
                     r"(?:\s*/\s*(?:Armador|Escolta|Alero|Delantero|Centro))?\b")
_J5_CAR = re.compile(r"A[nñ]o\s+Equipo\s+3pi.+?JJ\s+PTS\s+%\s+(.+?)(?:\s+Temporadas:|\s+©|\Z)", re.S)
_J5_ROW = re.compile(r"(\d{4})\s+([A-ZÑÁÉÍÓÚ.\- ]+?)\s+(?=\d)(.+?)(?=\s+\d{4}\s+[A-ZÑ]|\Z)", re.S)


def parse_jug05() -> list[dict]:
    """The 2005-era player page: one record per file (deduped by digest at fetch
    time). Name is always present; birth date ~89%, position ~99%, career
    ~95%. No league id — these only enrich existing canonical rows (D1). A row's season is its
    Año label, except the newest-season slot after the capture date the source changed it
    (jug05_season)."""
    out: list[dict] = []
    for p, html, meta, retrieved_at in _iter_files("jug05"):
        txt = " ".join(BeautifulSoup(html, "html.parser").get_text(" ").split())
        if "Ciudad Nacimiento" not in txt:
            continue
        m = _J5_NAME.search(txt)
        name = clean_field(m.group(1)) if m else ""
        if not name or "," not in name:
            continue
        bio = (_J5_BIO.search(txt) or [None, ""])[1] if _J5_BIO.search(txt) else ""
        dob = clean_dob((_J5_DOB.search(bio) or [None, ""])[1] if _J5_DOB.search(bio) else "")
        pos = _J5_POS.search(bio)
        career: list[tuple] = []
        cm = _J5_CAR.search(txt)
        if cm:
            for r in _J5_ROW.finditer(cm.group(1)):
                yr = int(r.group(1))
                if yr < 1929 or yr > 2030:
                    continue
                yr = jug05_season(yr, meta.get("wayback_timestamp", ""))
                team = squish(r.group(2))
                # row tail is: 3pi 3pa % 2pi 2pa % TLI TLA % ASIS apg REB rpg JJ PTS ppg
                # a complete row ends on the ppg float; JJ/PTS are the two ints before it.
                toks = re.findall(r"\d+\.\d+|\d+%|\d+", r.group(3))
                jj = pts = None
                if len(toks) >= 3 and re.fullmatch(r"\d+\.\d+", toks[-1]):
                    if toks[-3].isdigit():
                        jj = int(toks[-3])
                    if toks[-2].isdigit():
                        pts = int(toks[-2])
                career.append((yr, team, jj, pts))
        ape, _, nom = name.partition(",")
        out.append({
            "name": name, "apellidos": squish(ape), "nombre": clean_field(nom),
            "birth_date": dob, "position": pos.group(0) if pos else "",
            "career": career, "source_url": meta.get("raw_wayback_url", ""),
            "retrieved_at": retrieved_at,
        })
    # the same player has several pages (different r/r2 tokens -> different
    # digests); collapse on name+birth_date, keeping the fullest career.
    dedup: dict[tuple, dict] = {}
    for r in out:
        k = (norm_key(r["name"]), r["birth_date"])
        cur = dedup.get(k)
        if cur is None or len(r["career"]) > len(cur["career"]):
            r = {**r, "career": sorted(set(r["career"]))}
            dedup[k] = r
    players = list(dedup.values())
    print(f"[jug05] {len(out)} pages -> {len(players)} distinct players, "
          f"{sum(len(r['career']) for r in players)} career-season rows")
    return players


JUG05_ID_BASE = 990000   # minted ids: far above the league's real ?id=N range


def _pdate(s: str):
    """M/D/YYYY (the bsnpr.com format) -> date, or None."""
    m = _DATE_RE.search(s or "")
    if not m:
        return None
    try:
        mo, d, y = m.group(1).split("/")
        return datetime(int(y), int(mo), int(d)).date()
    except (ValueError, TypeError):
        return None


# --------------------------------------------------------------------------- #
# cross-source career dedup (docs/specs/merge_jug05_audit_spec.md, D1-D6)       #
# --------------------------------------------------------------------------- #
# jugador.asp writes a team as "Nick, City" and jug05.asp as a bare city, so one
# real player-season arrived twice under two spellings. The key is the city,
# which both spellings share; the stats decide whether it is one record.
# `fold_cross_source_career` is the ONE place that decision is made. merge_jug05
# calls it, and src/apply_career_dedup.py applies it to the committed
# player_career_seasons.csv, which cannot simply be regenerated because the
# identity outputs carry hand edits (docs/session.md).
# jug05_retrieved_at is the fetch time of the jug05 row (the removed row in the merged log,
# row b in the conflicts log); it is provenance that the wayback timestamp in the URL does
# not carry. Blank when the row has none.
CAREER_MERGED_COLUMNS = ["bsnpr_id", "season", "franchise_id", "games", "points",
                         "players_source_url", "jug05_source_url", "jug05_team_raw",
                         "jug05_retrieved_at"]
CAREER_CONFLICT_COLUMNS = ["bsnpr_id", "season", "city_token",
                           "team_raw_a", "source_id_a", "games_a", "points_a", "source_url_a",
                           "team_raw_b", "source_id_b", "games_b", "points_b", "source_url_b",
                           "jug05_retrieved_at"]


def city_token(team_raw) -> str:
    """The city half of a team string: "Criollos, Caguas" and "CAGUAS" both give "caguas"."""
    return normalize(team_raw or "").split(",")[-1].strip()


def _career_stats(row) -> tuple:
    """(games, points) as ints or None, whether the row came from memory or a CSV.
    None is kept apart from 0 (PC2): a blank stat never equals a recorded zero."""
    return (to_int(row.get("games")), to_int(row.get("points")))


def _load_site_franchise_resolver():
    """(team_raw, season) -> the franchise_id the site shows for it: city_franchise_map.csv
    plus the season overrides, keyed on the city half of the string; "" when the city map
    lacks the city (the two hybrid Humacao-* labels). Mirrors
    build_web_data._team_resolver on purpose, so the merged-pairs log names franchises the
    way the site does (and leaves the unresolved ones blank, never guessed)."""
    with (CLEAN_DIR / "city_franchise_map.csv").open(encoding="utf-8") as fh:
        city = {normalize(r["normalized_city"]): r["franchise_id"] for r in csv.DictReader(fh)}
    overrides_fp = CLEAN_DIR / OVERRIDES_FILE
    overrides = load_overrides(overrides_fp, normalize) if overrides_fp.exists() else {}

    def resolve(team_raw, season) -> str:
        key = normalize(str(team_raw).split(",")[-1])
        return override_for(overrides, key, season) or city.get(key, "")
    return resolve


def _named_franchise(row, season, resolve_club) -> str:
    """The franchise a row names, or "" when it names none. A bare city ("CAGUAS") says where,
    not which team, so it is no evidence against a "Nick, City" row of the same city."""
    team = row["team_raw"]
    return resolve_club(team, season) if "," in team else ""


def fold_cross_source_career(career: list[dict], resolve_club=None, site_franchise=None):
    """Fold jug05 career rows into the players row they duplicate.

    Key: (bsnpr_id, season, city token). Only a jug05 row is ever folded, only into a row
    from another source, and only when games AND points are identical: the players row
    survives. A pair whose stats differ stays as two rows and is reported as a conflict
    (neither source is known to be right). Rows that name different franchises (two
    "Nick, City" strings that resolve apart, e.g. Atenienses and Osos) are never folded,
    and rows of one source are never folded into each other.

    Pure: nothing is written and `career` is not mutated. Rows may hold ints (in memory)
    or strings (read from the CSV). Returns (kept, merged, conflicts): kept is every row
    except the folded ones, in input order; merged and conflicts are sorted log rows."""
    resolve_club = resolve_club or _load_club_resolver()
    site_franchise = site_franchise or _load_site_franchise_resolver()
    groups: dict[tuple, list[int]] = defaultdict(list)
    for i, r in enumerate(career):
        groups[(str(r["bsnpr_id"]), int(r["season"]), city_token(r["team_raw"]))].append(i)

    dropped: set[int] = set()
    merged: list[dict] = []
    conflicts: list[dict] = []
    for key in sorted(groups, key=lambda k: (int(k[0]), k[1], k[2])):
        idx = groups[key]
        if len(idx) < 2:
            continue
        base = [i for i in idx if career[i]["source_id"] != JUG05_SOURCE_ID]
        for j in (i for i in idx if career[i]["source_id"] == JUG05_SOURCE_ID):
            row = career[j]
            twins = []
            for i in base:
                fa = _named_franchise(career[i], key[1], resolve_club)
                fb = _named_franchise(row, key[1], resolve_club)
                if not (fa and fb and fa != fb):       # two named, different franchises: never fold
                    twins.append(i)
            if not twins:
                continue
            same = next((i for i in twins if _career_stats(career[i]) == _career_stats(row)), None)
            if same is not None:
                dropped.add(j)
                games, points = _career_stats(career[same])
                merged.append({
                    "bsnpr_id": key[0], "season": key[1],
                    "franchise_id": site_franchise(career[same]["team_raw"], key[1]),
                    "games": games, "points": points,
                    "players_source_url": career[same]["source_url"],
                    "jug05_source_url": row["source_url"], "jug05_team_raw": row["team_raw"],
                    "jug05_retrieved_at": row.get("retrieved_at") or ""})
            else:
                a, b = career[twins[0]], row
                (ga, pa), (gb, pb) = _career_stats(a), _career_stats(b)
                conflicts.append({
                    "bsnpr_id": key[0], "season": key[1], "city_token": key[2],
                    "team_raw_a": a["team_raw"], "source_id_a": a["source_id"],
                    "games_a": ga, "points_a": pa, "source_url_a": a["source_url"],
                    "team_raw_b": b["team_raw"], "source_id_b": b["source_id"],
                    "games_b": gb, "points_b": pb, "source_url_b": b["source_url"],
                    "jug05_retrieved_at": b.get("retrieved_at") or ""})
    return [r for i, r in enumerate(career) if i not in dropped], merged, conflicts


def write_career_logs(merged: list[dict], conflicts: list[dict], interim_dir=None) -> None:
    """Write data/interim/jug05_career_merged.csv and jug05_career_conflicts.csv.
    Conflicts are recomputed from the rows that remain, so that file is overwritten.
    Merged pairs are history (the jug05 row is gone from the CSV once merged), so new pairs
    are ADDED to those already logged: a second run must not empty the log."""
    out = interim_dir or INTERIM_DIR
    path = out / "jug05_career_merged.csv"
    logged: dict[tuple, dict] = {}
    if path.exists():
        with path.open(encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                logged[(r["bsnpr_id"], r["season"], r["jug05_team_raw"], r["jug05_source_url"])] = r
    for r in merged:
        logged[(str(r["bsnpr_id"]), str(r["season"]), r["jug05_team_raw"], r["jug05_source_url"])] = r
    _write_csv(path, sorted(logged.values(), key=lambda r: (
        int(r["bsnpr_id"]), int(r["season"]), r["jug05_team_raw"], r["jug05_source_url"])),
        CAREER_MERGED_COLUMNS)
    _write_csv(out / "jug05_career_conflicts.csv", sorted(conflicts, key=lambda r: (
        int(r["bsnpr_id"]), int(r["season"]), r["team_raw_b"])), CAREER_CONFLICT_COLUMNS)


SEASON_TOTALS_COLUMNS = ["bsnpr_id", "season", "jug05_team_raw", "jug05_games", "jug05_points",
                         "jug05_source_url", "jug05_retrieved_at", "ficha_rows", "ficha_games_sum",
                         "ficha_points_sum", "ficha_source_urls"]


def fold_season_totals(career: list[dict]):
    """Fold a jug05 row that is the SEASON TOTAL of a player who changed team.

    jugador.asp (the "ficha", source `wayback_bsnpr_players`) has one row per team; in the slot labelled 2005
    jug05.asp mostly shows one row for the whole season (docs/specs/jug05_sumrow_check.md). The per-team fold
    then pairs that total with one team's partial row and reports a conflict. Owner decision 2026-09-21: a jug05
    row whose games AND points both equal the sum of the players-source rows of the same player-season, at least
    two rows, none with a blank figure (PC2), is corroboration of the season, not a conflict. It is folded out and
    logged; the per-team rows stay. It is NOT folded when it equals a single team row (a second row of 0/0 makes
    the sum equal that row: the ordinary fold merges it), and a jug05 row that matches no sum is left alone.

    Pure: `career` is not mutated; rows may hold ints or strings. Returns (kept, totals): kept is every row but
    the folded ones, in input order; totals are log rows (SEASON_TOTALS_COLUMNS), sorted."""
    by: dict[tuple, list[dict]] = defaultdict(list)
    for r in career:
        if r["source_id"] == SOURCE_ID:
            by[(str(r["bsnpr_id"]), int(r["season"]))].append(r)
    kept: list[dict] = []
    totals: list[dict] = []
    for r in career:
        if r["source_id"] == JUG05_SOURCE_ID:
            comp = by.get((str(r["bsnpr_id"]), int(r["season"])), [])
            j = _career_stats(r)
            stats = [_career_stats(c) for c in comp]
            if (len(comp) >= 2 and None not in j and all(None not in st for st in stats)
                    and j not in stats
                    and (sum(st[0] for st in stats), sum(st[1] for st in stats)) == j):
                comp = sorted(comp, key=lambda c: c["team_raw"])
                totals.append({
                    "bsnpr_id": str(r["bsnpr_id"]), "season": int(r["season"]),
                    "jug05_team_raw": r["team_raw"], "jug05_games": j[0], "jug05_points": j[1],
                    "jug05_source_url": r["source_url"], "jug05_retrieved_at": r.get("retrieved_at") or "",
                    "ficha_rows": " | ".join(f"{c['team_raw']} {c['games']}/{c['points']}" for c in comp),
                    "ficha_games_sum": j[0], "ficha_points_sum": j[1],
                    "ficha_source_urls": " | ".join(dict.fromkeys(c["source_url"] for c in comp))})
                continue
        kept.append(r)
    totals.sort(key=lambda t: (int(t["bsnpr_id"]), t["season"], t["jug05_team_raw"], t["jug05_source_url"]))
    return kept, totals


def write_season_totals_log(totals: list[dict], interim_dir=None) -> None:
    """Write data/interim/jug05_season_totals.csv. History, like the merged log: the jug05 row is gone from the
    CSV once folded, so new rows are ADDED to those already logged and a second run does not empty the file."""
    path = (interim_dir or INTERIM_DIR) / "jug05_season_totals.csv"
    logged: dict[tuple, dict] = {}
    if path.exists():
        with path.open(encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                logged[(r["bsnpr_id"], r["season"], r["jug05_team_raw"], r["jug05_source_url"])] = r
    for r in totals:
        logged[(str(r["bsnpr_id"]), str(r["season"]), r["jug05_team_raw"], r["jug05_source_url"])] = r
    _write_csv(path, sorted(logged.values(), key=lambda r: (
        int(r["bsnpr_id"]), int(r["season"]), r["jug05_team_raw"], r["jug05_source_url"])), SEASON_TOTALS_COLUMNS)


FOREIGN_INPUT_FILE = "jug05_foreign_lines.csv"
FOREIGN_LOG_FILE = "jug05_foreign_rows.csv"
FOREIGN_LOG_COLUMNS = ["bsnpr_id", "season", "team_raw", "games", "points", "source_url", "capture_date",
                       "retrieved_at", "owner_id", "owner_name", "evidence", "evidence_es"]

DISPUTED_ROWS_FILE = "disputed_career_rows.csv"


def load_disputed_rows(interim_dir=None) -> list[dict]:
    """Hand-curated list of career rows that conflict with the player's OWN birth_date on the same bsnpr.com
    page (data/interim/disputed_career_rows.csv, evidence in docs/specs/cluster_evidence_a05.md). Unlike a
    foreign row, a disputed row is not known to belong to anyone else -- it stays in player_career_seasons.csv
    untouched; the app marks it and drops it from the player's totals, and neither side is called wrong.
    [] when the file is absent."""
    path = (interim_dir or INTERIM_DIR) / DISPUTED_ROWS_FILE
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def check_disputed_rows(career: list[dict], disputed: list[dict]) -> list[str]:
    """Every listed row must still exactly match one row of `career` (bsnpr_id, season, team_raw, games,
    points, source_url). The list only flags rows for display -- it never edits or removes one -- so a stale
    entry (the underlying row changed shape, or is gone) is reported, not silently ignored."""
    have = {(r["bsnpr_id"], str(r["season"]), r["team_raw"], str(r["games"]), str(r["points"]), r["source_url"])
            for r in career}
    problems = []
    for d in disputed:
        key = (d["bsnpr_id"], str(d["season"]), d["team_raw"], str(d["games"]), str(d["points"]), d["source_url"])
        if key not in have:
            problems.append(f"disputed_career_rows: {d['bsnpr_id']}/{d['season']} does not match any career row")
    return problems


def load_foreign_rows(interim_dir=None) -> list[dict]:
    """The hand-curated list of jug05 rows that show ANOTHER player's line (data/interim/jug05_foreign_lines.csv,
    with per-row evidence; docs/specs/foreign_slot_check.md). Like player_dob_overrides.csv it is curated by hand:
    shared lines also occur by chance, so nothing here is detected automatically. [] when the file is absent."""
    path = (interim_dir or INTERIM_DIR) / FOREIGN_INPUT_FILE
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _foreign_key(r) -> tuple:
    return (str(r["bsnpr_id"]), int(r["season"]), r["team_raw"], str(r["games"]), str(r["points"]), r["source_url"])


def drop_foreign_rows(career: list[dict], foreign: list[dict]):
    """Drop the jug05 rows the curated list says are another player's line. A row goes only when its player, season,
    team, games, points AND capture url all equal a listed row, and only a jug05 row is ever dropped. Runs after the
    relabel (the listed season is the relabelled one) and before the season-total and per-team folds.

    Pure: `career` is not mutated; rows may hold ints or strings. Returns (kept, dropped): kept is every row but the
    dropped ones, in input order; dropped are log rows (FOREIGN_LOG_COLUMNS), sorted."""
    want = {_foreign_key(f): f for f in foreign}
    kept: list[dict] = []
    dropped: list[dict] = []
    for r in career:
        f = want.get(_foreign_key(r)) if r["source_id"] == JUG05_SOURCE_ID else None
        if f is None:
            kept.append(r)
            continue
        dropped.append({"bsnpr_id": str(r["bsnpr_id"]), "season": int(r["season"]), "team_raw": r["team_raw"],
                        "games": r["games"], "points": r["points"], "source_url": r["source_url"],
                        "capture_date": f["capture_date"], "retrieved_at": r.get("retrieved_at") or "",
                        "owner_id": f["owner_id"], "owner_name": f["owner_name"],
                        "evidence": f["evidence"], "evidence_es": f["evidence_es"]})
    dropped.sort(key=lambda d: (int(d["bsnpr_id"]), d["season"], d["team_raw"], d["source_url"]))
    return kept, dropped


def write_foreign_rows_log(dropped: list[dict], interim_dir=None) -> None:
    """Write data/interim/jug05_foreign_rows.csv. History, like the merged log: the row is gone from the career CSV
    once dropped, so new rows are ADDED to those already logged and a second run does not empty the file."""
    path = (interim_dir or INTERIM_DIR) / FOREIGN_LOG_FILE
    logged: dict[tuple, dict] = {}
    if path.exists():
        with path.open(encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                logged[(r["bsnpr_id"], r["season"], r["team_raw"], r["source_url"])] = r
    for r in dropped:
        logged[(str(r["bsnpr_id"]), str(r["season"]), r["team_raw"], r["source_url"])] = r
    _write_csv(path, sorted(logged.values(), key=lambda r: (
        int(r["bsnpr_id"]), int(r["season"]), r["team_raw"], r["source_url"])), FOREIGN_LOG_COLUMNS)


def merge_jug05(canon: list[dict], career: list[dict],
                jug05: list[dict]) -> dict:
    """Fold jug05 players into the spine. Three tiers:
      - enrich  — the player is already canonical (exact name+year, or the
                  canonical apellidos is a token-prefix of jug05's / vice-versa
                  with the given name and birth date agreeing) -> union career.
      - mint    — no canonical match at all -> a new canonical row with a
                  flagged synthetic id (JUG05_ID_BASE + n, has_profile=jug05,
                  D-047). PHASE_3H / owner OQ1 = (a).
      - review  — the name+birth-year collides with a canonical but the fuller
                  match fails -> jug05_review.csv, no change to the spine.
    Mutates `canon` and `career` in place. Returns a counts dict + the review
    list."""
    exact: dict[str, list[dict]] = defaultdict(list)
    byfam: dict[str, list[dict]] = defaultdict(list)
    by_id: dict[str, dict] = {}
    for c in canon:
        exact[norm_key(c["canonical_name"])].append(c)
        by_id[c["bsnpr_id"]] = c
        fam = normalize(c["apellidos"]).split()
        if fam:
            byfam[fam[0]].append(c)
    # Exact repeats only: the same jug05 row offered twice (two jug05 pages mapped to one id)
    # is skipped in _union_career. A jug05 row that differs in spelling from a players row is
    # decided at the end by fold_cross_source_career (city token + stats), not by this key.
    have = {(r["bsnpr_id"], int(r["season"]), normalize(r["team_raw"])) for r in career}

    # tier 0 — hand-curated resolution of the name+birth-year collisions
    # (nickname bridges, spelling variants). See docs/specs/jug05_spec.md.
    xwalk: dict[tuple, str] = {}
    xw_path = INTERIM_DIR / "jug05_xwalk.csv"
    if xw_path.exists():
        with xw_path.open(encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                xwalk[(norm_key(row["jug05_name"]), row["jug05_birth_date"])] = row["bsnpr_id"]

    def _family_name_candidates(jfam, jgiv):
        """Same surname-prefix + given-name-first-token test as _match()'s
        second tier, but with no birth-date requirement at all -- the pure
        name-shape signal, before any date corroboration is asked of it.
        Used only to decide mint-vs-review when jug05 has no birth date to
        confirm or reject a candidate with (see the call site below); never
        used to auto-match on its own (D1)."""
        out = []
        for c in byfam.get(jfam[0], []):
            cfam, cgiv = normalize(c["apellidos"]).split(), normalize(c["nombre"]).split()
            if cfam[:len(jfam)] != jfam and jfam[:len(cfam)] != cfam:
                continue
            if not cgiv or cgiv[0] != jgiv[0]:
                continue
            out.append(c)
        return out

    def _match(j) -> dict | None:
        jyr = j["birth_date"][-4:] if j["birth_date"] else ""
        for c in exact.get(norm_key(j["name"]), []):
            if not jyr or c["birth_year"] == jyr:
                return c
        jfam, jgiv, jd = normalize(j["apellidos"]).split(), normalize(j["nombre"]).split(), _pdate(j["birth_date"])
        if not (jfam and jgiv):
            return None
        for c in _family_name_candidates(jfam, jgiv):
            cd = _pdate(c["birth_date"])
            if jd and cd and abs((jd - cd).days) <= 7:
                return c
            if (not jd or not cd) and jyr and c["birth_year"] == jyr:
                return c
        return None

    def _union_career(pid, j):
        n = 0
        for yr, team, jj, pts in j["career"]:
            k = (pid, yr, normalize(team))
            if k in have:
                continue
            have.add(k)
            career.append({"bsnpr_id": pid, "season": yr, "team_raw": team,
                           "games": jj, "points": pts, "source_id": JUG05_SOURCE_ID,
                           "source_url": j["source_url"], "retrieved_at": j["retrieved_at"]})
            n += 1
        return n

    enriched = added = xw_hits = 0
    to_mint, review = [], []
    for j in jug05:
        forced = xwalk.get((norm_key(j["name"]), j["birth_date"]))
        if forced == "review":
            review.append({"name": j["name"], "birth_date": j["birth_date"],
                           "position": j["position"],
                           "seasons": ";".join(str(s) for s, *_ in j["career"]),
                           "collides_with": "xwalk: left in review"})
            continue
        if forced and forced in by_id:
            xw_hits += 1
            enriched += 1
            added += _union_career(forced, j)
            continue
        c = _match(j)
        if c:
            enriched += 1
            added += _union_career(c["bsnpr_id"], j)
            continue
        jfam = normalize(j["apellidos"]).split()
        jgiv = normalize(j["nombre"]).split()
        jyr = j["birth_date"][-4:] if j["birth_date"] else ""
        collide = [x for x in byfam.get(jfam[0], []) if jyr and x["birth_year"] == jyr] if jfam else []
        collide_reason = "birth_year"
        if not collide and not jyr and jfam and jgiv:
            # backlog item 7 addendum (2026-09-14) — the gap a systematic
            # canonical-file duplicate scan found: jug05.asp often has no
            # parseable birth date at all, and the birth-year collision check
            # above silently no-ops when jyr is empty — every one of the 22
            # duplicates found (990001-990040 band) minted a fresh id this way
            # despite a same-surname+same-given-name candidate already sitting
            # in the canonical set, because there was no date to confirm OR
            # reject it against. This doesn't try to resolve that candidate
            # (still D1: never match on name alone) — it only makes sure a
            # human sees it in the review queue instead of a silent mint.
            collide = _family_name_candidates(jfam, jgiv)
            collide_reason = "no_birth_date_name_shape_only"
        (review if collide else to_mint).append(j)
        if collide:
            review[-1] = {"name": j["name"], "birth_date": j["birth_date"],
                          "position": j["position"],
                          "seasons": ";".join(str(s) for s, *_ in j["career"]),
                          "collides_with": " | ".join(f'{x["bsnpr_id"]} {x["canonical_name"]}' for x in collide)
                              + (" [no birth date — name-shape match only, unconfirmed]"
                                 if collide_reason == "no_birth_date_name_shape_only" else "")}

    to_mint.sort(key=lambda j: (norm_key(j["name"]), j["birth_date"]))
    minted = 0
    for j in to_mint:
        pid = str(JUG05_ID_BASE + minted + 1)
        minted += 1
        yrs = [s for s, *_ in j["career"]]
        by = j["birth_date"].split("/")[-1] if j["birth_date"] else ""
        canon.append({
            "bsnpr_id": pid, "canonical_name": j["name"],
            "normalized_name": normalize(j["name"]),
            "apellidos": j["apellidos"], "nombre": j["nombre"], "nickname": "",
            "birth_date": j["birth_date"], "birth_year": by, "birth_city": "",
            "nationality": "", "position": j["position"],
            "first_season": str(min(yrs)) if yrs else "",
            "last_season": str(max(yrs)) if yrs else "",
            "n_seasons": str(len(set(yrs))), "has_profile": "jug05",
            "confidence": "jug05-only", "source_id": JUG05_SOURCE_ID,
            "source_url": j["source_url"], "retrieved_at": j["retrieved_at"],
        })
        added += _union_career(pid, j)

    kept, foreign_rows = drop_foreign_rows(career, load_foreign_rows())      # after the relabel (parse_jug05)
    kept, season_totals = fold_season_totals(kept)                            # then the season totals, then the fold
    kept, merged, conflicts = fold_cross_source_career(kept)
    career[:] = kept                      # in place, like every other mutation in this function
    added -= len(merged) + len(season_totals) + len(foreign_rows)
    print(f"[jug05] {len(jug05)} players -> {enriched} enriched ({xw_hits} via xwalk), "
          f"{minted} minted (id {JUG05_ID_BASE+1}..{JUG05_ID_BASE+minted}), "
          f"{len(review)} to review; {added} new career-season rows; "
          f"{len(merged)} duplicate rows merged, {len(season_totals)} season totals folded, "
          f"{len(foreign_rows)} foreign rows dropped, "
          f"{len(conflicts)} stat conflicts kept as two rows")
    return {"enriched": enriched, "minted": minted, "review": len(review),
            "career_rows": added, "review_list": review,
            "merged": merged, "conflicts": conflicts, "season_totals": season_totals,
            "foreign_rows": foreign_rows}


# --------------------------------------------------------------------------- #
# tranche D — jugador05.asp (PHASE_3H follow-up)                                #
# --------------------------------------------------------------------------- #
# jugador05.asp is the 2005-06 sibling of jug05.asp: a scouting bio, NOT a
# stat page. One block per file:
#   <TEAM> [<jersey>] - <Apellido> , <Nombre>
#   Origen: <birthplace>  Edad: <age>  Fecha: <M/D/YYYY>
#   Altura: <h>  Peso: <w>  Posición: <pos>
#   Notas Sobresalientes: <scouting prose>
# No career table -> these NEVER mint (D1). They enrich empty spine fields on
# a matched canonical row and contribute the prose to player_bios.csv.
JUGADOR05_SOURCE_ID = "wayback_bsnpr_jugador05"
# BeautifulSoup drops the HTML comment that used to separate the roster <select>
# from the heading, so the block reads: "... Foros Jugador <TEAM> [<num>] -
# <Ape> , <Nom> Origen: ... Notas Sobresalientes: <prose> ©". Anchor on the
# standalone "Jugador" heading label and walk the fixed label sequence; every
# value can be empty.
_J05_BLOCK = re.compile(
    r"\bJugador\s+(?P<team>[^-<>]{2,40}?)\s+-\s+"
    r"(?P<ape>[^,<>]{1,40}?)\s*,\s*(?P<nom>[^,<>]{1,40}?)\s+"
    r"Origen:\s*(?P<origen>.*?)\s*"
    r"Edad:\s*(?P<edad>\d*)\s*"
    r"Fecha:\s*(?P<fecha>[\d/]*)\s*"
    r"Altura:\s*(?P<altura>[\d'\u2019.\- ]*?)\s*"
    r"Peso:\s*(?P<peso>\d*)\s*"
    r"Posici[oó]n:\s*(?P<pos>[A-Za-z\u00c0-\u017e/ ]*?)\s*"
    r"Notas\s+Sobresalientes:\s*(?P<notas>.*?)\s*(?:\u00a9|$)", re.S)
_J05_TEAMNUM = re.compile(r"\s+(\d{1,3})$")
_J05_POS = _J5_POS


def parse_jugador05() -> list[dict]:
    """The 2005-06 scouting bio page. One record per file; deduped across a
    player's several roster pages on name+birth_date, keeping the fullest."""
    out: list[dict] = []
    for _p, html, meta, retrieved_at in _iter_files("jugador05"):
        txt = " ".join(BeautifulSoup(html, "html.parser").get_text(" ").split())
        if "Notas Sobresalientes" not in txt or "Origen:" not in txt:
            continue
        m = _J05_BLOCK.search(txt)
        if not m:
            continue
        team_raw = squish(m.group("team"))
        jersey = ""
        tn = _J05_TEAMNUM.search(team_raw)
        if tn:
            jersey, team_raw = tn.group(1), _J05_TEAMNUM.sub("", team_raw)
        ape = clean_field(m.group("ape"))
        nom = clean_field(m.group("nom"))
        if not ape or not nom:
            continue
        name = f"{squish(ape)}, {squish(nom)}"
        origen = squish(m.group("origen"))
        country = origen.split(",")[-1].strip() if origen else ""
        nationality = ("Puerto Rico" if "puerto rico" in country.lower()
                       else country if country and country != origen else "")
        pos = _J05_POS.search(m.group("pos") or "")
        notas = squish(m.group("notas"))
        out.append({
            "name": name, "apellidos": squish(ape), "nombre": squish(nom),
            "birth_date": clean_dob(m.group("fecha")),
            "position": pos.group(0) if pos else "",
            "birth_city": origen, "nationality": nationality,
            "roster_team": team_raw, "roster_year": (meta.get("wayback_timestamp", "") or "")[:4],
            "jersey": jersey, "notes_es": notas,
            "source_url": meta.get("raw_wayback_url", ""), "retrieved_at": retrieved_at,
        })

    def _score(r: dict) -> tuple:
        return (bool(r["birth_date"]), bool(r["position"]), bool(r["birth_city"]),
                len(r["notes_es"]))

    dedup: dict[tuple, dict] = {}
    for r in out:
        k = (norm_key(r["name"]), r["birth_date"])
        if k not in dedup or _score(r) > _score(dedup[k]):
            dedup[k] = r
    players = list(dedup.values())
    print(f"[jugador05] {len(out)} pages -> {len(players)} distinct players "
          f"({sum(1 for r in players if r['birth_date'])} w/ DOB, "
          f"{sum(1 for r in players if r['notes_es'])} w/ notes)")
    return players


def merge_jugador05(canon: list[dict], bios: list[dict],
                    dob_settled: set[str] | None = None) -> dict:
    """Enrich-only: match each jugador05 bio to a canonical row (same test as
    merge_jug05 minus the mint tier), fill *empty* spine fields
    (birth_date/birth_year, birth_city, nationality, position) — never
    overwrite — and emit a player_bios row for the prose. No match -> review.
    `dob_settled` ids already had their birth date adjudicated by
    `apply_dob_overrides`, so a lingering jugador05 disagreement is not re-logged.
    Mutates `canon` in place; returns counts + (bio_rows, review_list)."""
    dob_settled = dob_settled or set()
    exact: dict[str, list[dict]] = defaultdict(list)
    byfam: dict[str, list[dict]] = defaultdict(list)
    by_id: dict[str, dict] = {}
    for c in canon:
        exact[norm_key(c["canonical_name"])].append(c)
        by_id[c["bsnpr_id"]] = c
        fam = normalize(c["apellidos"]).split()
        if fam:
            byfam[fam[0]].append(c)

    # tier 0 — hand-curated bridges. jug05_xwalk.csv covers the shared 2005-06
    # roster ("Ayuso, Larry" etc.); jugador05_xwalk.csv adds this source's own
    # review rows and wins on a conflict. Keyed on name+DOB first, then name
    # alone when that surname maps to exactly one id.
    xwalk: dict[tuple, str] = {}
    xwalk_name: dict[str, set] = defaultdict(set)
    for fn, ncol, dcol in (("jug05_xwalk.csv", "jug05_name", "jug05_birth_date"),
                           ("jugador05_xwalk.csv", "jugador05_name", "jugador05_birth_date")):
        p = INTERIM_DIR / fn
        if not p.exists():
            continue
        with p.open(encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                k = norm_key(row[ncol])
                xwalk[(k, row[dcol])] = row["bsnpr_id"]
                xwalk_name.setdefault(k, set()).add(row["bsnpr_id"])

    def _family_shape_candidates(jfam, jgiv, exclude_id=None):
        """Same surname-prefix + given-name-first-token test as _match()'s
        second tier, but usable standalone to check for a *different*
        plausible candidate before the exact-name tier below auto-accepts
        on a blank canonical birth year. This is exactly the 2722/1271
        shape (2026-09-14): the bare exact name "Ortiz, Jose" silently
        absorbed jugador05's real Piculín Ortiz bio because canonical id
        2722 had no birth_year on file, even though "Ortiz Rijos, Jose
        Rafael" (id 1271) was sitting right there as a same-surname-prefix,
        same-given-token, date-corroborated candidate. Never used to
        auto-match on its own (D1) -- only to withhold an auto-accept."""
        out = []
        for c in byfam.get(jfam[0], []):
            if c["bsnpr_id"] == exclude_id:
                continue
            cfam, cgiv = normalize(c["apellidos"]).split(), normalize(c["nombre"]).split()
            if cfam[:len(jfam)] != jfam and jfam[:len(cfam)] != cfam:
                continue
            if not cgiv or cgiv[0] != jgiv[0]:
                continue
            out.append(c)
        return out

    def _match(j) -> dict | None:
        nk = norm_key(j["name"])
        forced = xwalk.get((nk, j["birth_date"]))
        if forced is None and len(xwalk_name.get(nk, ())) == 1:
            forced = next(iter(xwalk_name[nk]))
        if forced == "review":
            return None
        if forced and forced in by_id:
            return by_id[forced]
        jyr = j["birth_date"][-4:] if j["birth_date"] else ""
        jfam, jgiv = normalize(j["apellidos"]).split(), normalize(j["nombre"]).split()
        # exact full name: accept unless both sides carry a birth year and they
        # disagree (a missing canonical year is the case we most want to fill)
        # -- but not when the accept would rest solely on a blank year (either
        # side) while a different, same-surname+given-token candidate exists.
        # That ambiguity falls through to the family-shape tier below, which
        # requires real date corroboration before it will pick one.
        for c in exact.get(nk, []):
            if jyr and c["birth_year"]:
                if c["birth_year"] == jyr:
                    return c
                continue                       # both have a year, and it differs
            if jfam and jgiv and _family_shape_candidates(jfam, jgiv, exclude_id=c["bsnpr_id"]):
                continue                       # ambiguous -- let date corroboration decide
            return c
        jd = _pdate(j["birth_date"])
        if not (jfam and jgiv):
            return None
        for c in byfam.get(jfam[0], []):
            cfam, cgiv = normalize(c["apellidos"]).split(), normalize(c["nombre"]).split()
            if cfam[:len(jfam)] != jfam and jfam[:len(cfam)] != cfam:
                continue
            if not cgiv or cgiv[0] != jgiv[0]:
                continue
            cd = _pdate(c["birth_date"])
            if jd and cd:
                if abs((jd - cd).days) <= 7:
                    return c
                continue                       # both dated, and they disagree
            if jyr and c["birth_year"]:
                if c["birth_year"] == jyr:
                    return c
                continue                       # both have a year, and it differs
        return None

    matched = filled = 0
    bios_by_id: dict[str, dict] = {}
    review, dob_conflicts = [], []
    for j in bios:
        c = _match(j)
        if not c:
            review.append({"name": j["name"], "birth_date": j["birth_date"],
                           "position": j["position"], "birth_city": j["birth_city"],
                           "roster_team": j["roster_team"], "roster_year": j["roster_year"],
                           "note": "no canonical match; jugador05 has no career table so cannot mint (D1)"})
            continue
        matched += 1
        pid = c["bsnpr_id"]
        if j["birth_date"]:
            if not c["birth_date"]:
                c["birth_date"] = j["birth_date"]
                c["birth_year"] = j["birth_date"].split("/")[-1]
                filled += 1
            elif _pdate(c["birth_date"]) != _pdate(j["birth_date"]) and pid not in dob_settled:
                dob_conflicts.append({"bsnpr_id": pid, "canonical_name": c["canonical_name"],
                                      "canonical_dob": c["birth_date"], "jugador05_dob": j["birth_date"]})
        for spine, src in (("birth_city", "birth_city"), ("nationality", "nationality"),
                           ("position", "position")):
            if not c.get(spine) and j.get(src):
                c[spine] = j[src]
                filled += 1
        row = {
            "bsnpr_id": pid, "notes_es": j["notes_es"], "birthplace": j["birth_city"],
            "roster_team": j["roster_team"], "roster_year": j["roster_year"],
            "jersey": j["jersey"], "source_id": JUGADOR05_SOURCE_ID,
            "source_url": j["source_url"], "retrieved_at": j["retrieved_at"],
        }
        # a player with both a 2005 and a 2006 page: keep the one with prose,
        # else the later roster year.
        prev = bios_by_id.get(pid)
        if prev is None or (len(row["notes_es"]), row["roster_year"]) > (len(prev["notes_es"]), prev["roster_year"]):
            bios_by_id[pid] = row

    bio_rows = list(bios_by_id.values())
    print(f"[jugador05] {len(bios)} players -> {matched} matched "
          f"({filled} empty spine fields filled, {len(dob_conflicts)} DOB disagreements), "
          f"{len(review)} to review; {len(bio_rows)} bio rows "
          f"({sum(1 for b in bio_rows if b['notes_es'])} w/ prose)")
    for d in dob_conflicts[:12]:
        print(f"    DOB? {d['bsnpr_id']:>5} {d['canonical_name']:<30} "
              f"canonical {d['canonical_dob']}  vs jugador05 {d['jugador05_dob']}")
    return {"matched": matched, "filled": filled, "disagree": len(dob_conflicts),
            "bio_rows": bio_rows, "review_list": review, "dob_conflicts": dob_conflicts}


# --------------------------------------------------------------------------- #
# assembly                                                                     #
# --------------------------------------------------------------------------- #
def apply_dob_overrides(canon: list[dict]) -> set[str]:
    """Hand-curated corrections to enciclopedia birth dates, each corroborated
    by the 2005-era jug05 / jugador05 player pages (mostly M/D transpositions).
    `data/interim/player_dob_overrides.csv`. Applied only when the current
    canonical value still equals the recorded `old_dob` — a re-parse that
    changed it upstream logs a skip instead of silently clobbering. An empty
    `new_dob` nulls a value known to be wrong with no trusted replacement."""
    p = INTERIM_DIR / "player_dob_overrides.csv"
    if not p.exists():
        return set()
    by_id = {c["bsnpr_id"]: c for c in canon}
    done: set[str] = set()
    skipped = 0
    with p.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            c = by_id.get(row["bsnpr_id"])
            if c is None:
                continue
            done.add(row["bsnpr_id"])
            if c["birth_date"] != row["old_dob"]:
                print(f"  [dob-override] id {row['bsnpr_id']}: canonical is "
                      f"{c['birth_date']!r}, not the recorded {row['old_dob']!r} — skipped")
                skipped += 1
                continue
            c["birth_date"] = row["new_dob"]
            c["birth_year"] = row["new_dob"].split("/")[-1] if row["new_dob"] else ""
    print(f"[dob-overrides] {len(done) - skipped} applied"
          + (f", {skipped} skipped (stale)" if skipped else ""))
    return done


def build_canonical(enc: dict[str, dict], prof: dict[str, dict]) -> list[dict]:
    rows: list[dict] = []
    for pid, e in sorted(enc.items(), key=lambda kv: int(kv[0])):
        p = prof.get(pid, {})
        apellidos = clean_field(e["apellidos"])
        nombre = (clean_field(p["profile_name"].split(",")[-1])
                  if p.get("profile_name") else clean_field(e["nombre"]))
        # jugador.asp heading is "Apellidos, Nombre"; prefer its apellidos if present
        if p.get("profile_name") and "," in p["profile_name"]:
            apellidos = clean_field(p["profile_name"].split(",")[0]) or apellidos
        canonical_name = f"{apellidos}, {nombre}".strip(" ,")
        birth_date = p.get("birth_date") or e["birth_date"]
        birth_year = ""
        bm = _DATE_RE.search(birth_date)
        if bm:
            birth_year = bm.group(1).split("/")[-1]
        rows.append({
            "bsnpr_id": pid,
            "canonical_name": canonical_name,
            "normalized_name": normalize(canonical_name),
            "apellidos": apellidos,
            "nombre": nombre,
            "nickname": e["nickname"] or p.get("profile_nickname", ""),
            "birth_date": birth_date,
            "birth_year": birth_year,
            "birth_city": p.get("birth_city", ""),
            "nationality": p.get("nationality", ""),
            "position": p.get("position", ""),
            "first_season": p.get("first_season") or "",
            "last_season": p.get("last_season") or "",
            "n_seasons": p.get("n_seasons") or "",
            "has_profile": "yes" if pid in prof else "no",
            "confidence": "single-source",
            "source_id": SOURCE_ID,
            "source_url": p.get("source_url") or e["source_url"],
            "retrieved_at": p.get("retrieved_at") or e["retrieved_at"],
        })
    return rows


def build_aliases(canon: list[dict], enc: dict[str, dict]) -> list[dict]:
    out: list[dict] = []
    seen: set[tuple] = set()

    def add(pid, alias, kind, source):
        alias = squish(alias)
        key = (pid, normalize(alias), kind)
        if alias and key not in seen:
            seen.add(key)
            out.append({"bsnpr_id": pid, "alias": alias, "normalized_alias": normalize(alias),
                        "alias_type": kind, "source": source})

    for c in canon:
        pid = c["bsnpr_id"]
        add(pid, c["canonical_name"], "canonical", "derived")
        add(pid, c["normalized_name"], "normalized", "derived")
        # Western order: "Nombre Apellidos"
        if c["nombre"] and c["apellidos"]:
            add(pid, f"{c['nombre']} {c['apellidos']}", "given_family_order", "derived")
        # paternal-surname-only "Apellido, Nombre" (first surname token)
        pat = c["apellidos"].split()[0] if c["apellidos"] else ""
        first_given = c["nombre"].split()[0] if c["nombre"] else ""
        for surname in {c["apellidos"], pat}:
            if surname and c["nombre"]:
                add(pid, f"{surname}, {c['nombre']}", "paternal_surname", "derived")
                # first given name only — drops middle names/initials
                # ("Arroyo, Carlos A." -> "Arroyo, Carlos"); deliberately
                # ambiguous, disambiguated later by season + club (D1).
                if first_given and first_given != c["nombre"]:
                    add(pid, f"{surname}, {first_given}", "given_first_only", "derived")
                # initial form, as equiposstat writes it: "Apellido, N."
                if first_given:
                    add(pid, f"{surname}, {first_given[0]}.", "initial", "derived")
        if c["nickname"]:
            add(pid, c["nickname"], "nickname", "bsnpr")
            if pat:
                add(pid, f"{pat}, {c['nickname']}", "nickname_surname", "derived")
        # the raw enciclopedia "Nombre" field (may carry a nickname/middle name)
        e = enc.get(pid, {})
        if e.get("nombre"):
            add(pid, f"{c['apellidos']}, {e['nombre']}", "enciclopedia", "bsnpr")
    return out


# --------------------------------------------------------------------------- #
# club-code corroboration (PHASE_3F, identity_spine_spec Q2)                    #
# --------------------------------------------------------------------------- #
# A second signal beyond name+season: does the observed club match a club the
# candidate is on record as playing for? Used only to *break ties* and to
# *enrich* the review queue — never to un-map an existing link (club data has
# split seasons, mid-career gaps in jugador.asp, and D2 name/era ambiguity that
# make a contradiction unreliable; those are surfaced in `club_check`, not acted
# on). See docs/specs/identity_spine_spec.md.
_DE_SPLIT = re.compile(r"\s+de\s+|,\s*", re.I)


def _load_club_resolver():
    """-> resolve_club(raw) mapping any club string (5-char code, 2-letter
    `equiposstat` code, "Nick de City", "Nick, City", bare nick, bare city) to a
    stable franchise key. Both the observed club and the career-table team names
    go through this same function, so consistent inputs give a consistent key
    even where the franchise master is thin (Conquistadores de Guaynabo,
    Caciques de Humacao) — a `nick_city` synthetic key is used as the fallback."""
    def _rows(name):
        fp = CLEAN_DIR / name
        return list(csv.DictReader(fp.open(encoding="utf-8"))) if fp.exists() else []

    code_map: dict[str, str] = {}
    for r in _rows("club_code_map.csv"):
        code_map[r["code"].upper()] = r["franchise_id"]
    city_map: dict[str, str] = {}
    for r in _rows("city_franchise_map.csv"):
        city_map[normalize(r["normalized_city"])] = r["franchise_id"]
    # Same era-scoped overrides build_web_data._team_resolver reads, so the two
    # resolvers cannot disagree about a city that changed hands (Manatí). Absent
    # file = no overrides, matching how _rows() treats every other optional file.
    overrides_fp = CLEAN_DIR / OVERRIDES_FILE
    overrides = load_overrides(overrides_fp, normalize) if overrides_fp.exists() else {}
    nick_map: dict[str, str] = {}
    nick_ambiguous: set[str] = set()

    def _reg_nick(nick: str, fid: str) -> None:
        n = normalize(nick)
        if not n:
            return
        if n in nick_map and nick_map[n] != fid:
            nick_ambiguous.add(n)
        else:
            nick_map[n] = fid

    for r in _rows("franchises.csv"):
        fid = r["franchise_id"]
        parts = _DE_SPLIT.split(r["canonical_name"], maxsplit=1)
        if len(parts) == 2:
            _reg_nick(parts[0], fid)

    # "Grises" names two different Humacao franchises across eras — the 2005-19
    # chain (now keyed caciques_humacao) and the separate 2021-23 grises_humacao
    # expansion that became Criollos de Caguas (D-045). The resolver is
    # season-blind and both appear in player_season_leaders.csv, so force the
    # bare nick ambiguous: "Grises, Humacao" still resolves by city (→
    # caciques_humacao, correct for every archived season), while a bare "Grises"
    # stays unresolved (advisory no_obs_club) rather than a spurious contradiction.
    nick_ambiguous.add(normalize("Grises"))

    def resolve_club(raw: str, season: int | str | None = None) -> str:
        if not raw:
            return ""
        s = squish(raw)
        if s.upper() in code_map:
            return code_map[s.upper()]
        parts = _DE_SPLIT.split(s, maxsplit=1)
        nick = normalize(parts[0]) if parts else ""
        city = normalize(parts[1]) if len(parts) == 2 else ""
        city_fid = override_for(overrides, city, season) or city_map.get(city)
        nick_fid = None if nick in nick_ambiguous else nick_map.get(nick)
        if city_fid and (not nick_fid or nick_fid == city_fid):
            return city_fid
        if nick_fid and not city:
            return nick_fid
        if nick and city:
            return f"{nick}_{city}"          # synthetic — consistent both sides
        # bare single token: could be a city or an (unambiguous) nickname
        return (override_for(overrides, nick, season) or city_map.get(nick)
                or ("" if nick in nick_ambiguous else nick_map.get(nick, "")) or "")

    return resolve_club


# --------------------------------------------------------------------------- #
# observation -> id matching (D1)                                              #
# --------------------------------------------------------------------------- #
def _load_observations() -> list[dict]:
    obs: list[dict] = []
    for fname, pcol, ccol, scol in OBSERVATION_FILES:
        fp = CLEAN_DIR / fname
        if not fp.exists():
            continue
        with fp.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                pr = squish(r.get(pcol, ""))
                if not pr:
                    continue
                obs.append({
                    "obs_source": fname, "player_raw": pr,
                    "club_raw": squish(r.get(ccol, "")),
                    "season": squish(r.get(scol, "")),
                })
    # collapse to distinct (source, player_raw, club_raw, season)
    uniq: dict[tuple, dict] = {}
    for o in obs:
        uniq[(o["obs_source"], o["player_raw"], o["club_raw"], o["season"])] = o
    return list(uniq.values())


# --------------------------------------------------------------------------- #
# PHASE_3I — historic scoring-title seed                                        #
# --------------------------------------------------------------------------- #
# The 1948–1971 scoring champions are all in `players_canonical` but have no
# `jugador.asp` profile, so `build_id_map` has no career span to test a season
# against and parks them in review. bsnpr.com's own records page names them the
# season's scoring champion — an authoritative per-season attestation (owner-
# approved as corroboration for a *unique* name candidate, D1-compatible).

_TITLE_FILES = [
    ("historic_scoring_champions.csv", ["player_raw"]),
    ("scoring_champions_reconciled.csv",
     ["ppg_champion", "total_points_champion", "historic_player",
      "leaders_player", "seed_player"]),
]


def _title_seasons() -> dict[str, set[int]]:
    """raw champion name -> {season} across the scoring-title records."""
    out: dict[str, set[int]] = defaultdict(set)
    for fname, cols in _TITLE_FILES:
        fp = CLEAN_DIR / fname
        if not fp.exists():
            continue
        with fp.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                sy = r.get("season", "")
                if not re.fullmatch(r"\d{4}", sy):
                    continue
                for col in cols:
                    nm = squish(r.get(col, ""))
                    if nm:
                        out[nm].add(int(sy))
    return out


def _title_seasons_by_key() -> dict[str, set[int]]:
    """norm_key(champion name) -> {season} — the view `build_id_map` tests."""
    out: dict[str, set[int]] = defaultdict(set)
    for nm, seasons in _title_seasons().items():
        out[norm_key(nm)] |= seasons
    return out


def _crosswalk_name_ids() -> list[tuple[str, str]]:
    """(name, bsnpr_id) from the owner-curated `app/player_crosswalk.csv`
    (verdict auto/review, id present). **Additive** — an extra alias that can
    resolve a "no name match" row; it never overrides an existing candidate."""
    xw = REPO_ROOT / "app" / "player_crosswalk.csv"
    if not xw.exists():
        return []
    with xw.open(encoding="utf-8") as fh:
        return [(r["curated_name"], r["bsnpr_id"]) for r in csv.DictReader(fh)
                if r.get("bsnpr_id") and r.get("verdict") in ("auto", "review")]


def _historic_seed_ids() -> list[tuple[str, str]]:
    """(observed_name, bsnpr_id) from `data/interim/player_historic_seed.csv`.
    **Authoritative** — a hand-curated resolution that replaces the candidate set
    (used for the dup-canonical champion rows the auto matcher can't split)."""
    seed = INTERIM_DIR / "player_historic_seed.csv"
    if not seed.exists():
        return []
    with seed.open(encoding="utf-8") as fh:
        return [(r["observed_name"], r["bsnpr_id"])
                for r in csv.DictReader(fh) if r.get("bsnpr_id")]


def seed_historic_spans(canon: list[dict], aliases: list[dict]) -> int:
    """Extend `first_season`/`last_season` on a canonical row when a scoring-title
    record uniquely names it — so `build_id_map` can then corroborate the
    observation, and the app can show the years we can document the player active.
    Runs before `build_id_map`; mutates `canon` in place."""
    by_pid = {c["bsnpr_id"]: c for c in canon}
    alias_idx: dict[str, set[str]] = defaultdict(set)
    key_idx: dict[str, set[str]] = defaultdict(set)
    for a in aliases:
        alias_idx[a["normalized_alias"]].add(a["bsnpr_id"])
        key_idx[norm_key(a["alias"])].add(a["bsnpr_id"])
    for c in canon:
        key_idx[norm_key(c["canonical_name"])].add(c["bsnpr_id"])
    for nm, pid in _crosswalk_name_ids():
        if pid in by_pid:
            alias_idx[normalize(nm)].add(pid)
            key_idx[norm_key(nm)].add(pid)
    seed_override = {normalize(nm): pid for nm, pid in _historic_seed_ids() if pid in by_pid}

    seeded = 0
    for nm, seasons in _title_seasons().items():
        # resolve the champion name the same way build_id_map does
        if normalize(nm) in seed_override:
            cands = {seed_override[normalize(nm)]}
        else:
            cands = alias_idx.get(normalize(nm)) or key_idx.get(norm_key(nm))
        if not cands or len(cands) != 1:
            continue
        c = by_pid[next(iter(cands))]
        lo = min([*seasons, int(c["first_season"])] if c["first_season"] else seasons)
        hi = max([*seasons, int(c["last_season"])] if c["last_season"] else seasons)
        if (str(lo), str(hi)) != (c["first_season"], c["last_season"]):
            c["first_season"], c["last_season"] = str(lo), str(hi)
            # n_seasons stays as-is: a title run is not a season count, and we
            # have no record of how many seasons these players actually played.
            seeded += 1
    print(f"[historic-seed] {seeded} canonical career spans seeded/extended from scoring titles")
    return seeded


def build_id_map(canon: list[dict], aliases: list[dict],
                 career: list[dict]) -> tuple[list[dict], list[dict]]:
    by_pid = {c["bsnpr_id"]: c for c in canon}
    # normalized alias / norm_key -> {pid}
    alias_idx: dict[str, set[str]] = {}
    key_idx: dict[str, set[str]] = {}
    for a in aliases:
        alias_idx.setdefault(a["normalized_alias"], set()).add(a["bsnpr_id"])
        key_idx.setdefault(norm_key(a["alias"]), set()).add(a["bsnpr_id"])
    for c in canon:
        key_idx.setdefault(norm_key(c["canonical_name"]), set()).add(c["bsnpr_id"])
    # PHASE_3I — the owner-curated crosswalk as an extra (additive) alias source
    for nm, pid in _crosswalk_name_ids():
        if pid in by_pid:
            alias_idx.setdefault(normalize(nm), set()).add(pid)
            key_idx.setdefault(norm_key(nm), set()).add(pid)
    # …and the historic seed as an authoritative override of the candidate set
    seed_override = {normalize(nm): pid for nm, pid in _historic_seed_ids() if pid in by_pid}
    title_by_name = _title_seasons_by_key()

    # PHASE_3J (identity_spine_spec Q4) — indexes for the truncated / bare-surname
    # fallbacks: first apellido token -> {pid}, and -> [(given tokens, pid)].
    surname_idx: dict[str, set[str]] = defaultdict(set)
    prefix_idx: dict[str, list[tuple[list[str], str]]] = defaultdict(list)
    for c in canon:
        at, gt = normalize(c["apellidos"]).split(), normalize(c["nombre"]).split()
        if at:
            surname_idx[at[0]].add(c["bsnpr_id"])
            if gt:
                prefix_idx[at[0]].append((gt, c["bsnpr_id"]))
    _CLIP = re.compile(r"\s*['\"‘’“”][^'\"‘’“”]*$")

    career_by_pid: dict[str, set[int]] = {}
    for r in career:
        career_by_pid.setdefault(r["bsnpr_id"], set()).add(r["season"])

    # club-code corroboration (PHASE_3F): franchise key per (pid, season)
    resolve_club = _load_club_resolver()
    club_by_pid_season: dict[str, dict[int, set[str]]] = {}
    club_by_pid: dict[str, set[str]] = {}
    for r in career:
        fid = resolve_club(r["team_raw"], r["season"])
        if not fid:
            continue
        club_by_pid_season.setdefault(r["bsnpr_id"], {}).setdefault(r["season"], set()).add(fid)
        club_by_pid.setdefault(r["bsnpr_id"], set()).add(fid)

    mapped: list[dict] = []
    review: list[dict] = []

    for o in _load_observations():
        pr, season = o["player_raw"], o["season"]
        if normalize(pr) in seed_override:
            cands = {seed_override[normalize(pr)]}
        else:
            cands = alias_idx.get(normalize(pr), set()) or key_idx.get(norm_key(pr), set())
        cands = set(cands)
        sy = int(season) if re.fullmatch(r"\d{4}", season) else None
        obs_fid = resolve_club(o["club_raw"], sy)

        # corroborate with career span / season-in-range
        def in_career(pid: str) -> bool:
            c = by_pid[pid]
            if pid in career_by_pid and sy is not None:
                yrs = career_by_pid[pid]
                return min(yrs) - 1 <= sy <= max(yrs) + 1
            if c["first_season"] and c["last_season"] and sy is not None:
                return int(c["first_season"]) - 1 <= sy <= int(c["last_season"]) + 1
            return False

        # did this pid play for obs_fid in a season within ±1 of the observation?
        def club_in_season(pid: str) -> bool:
            if not obs_fid or sy is None or pid not in club_by_pid_season:
                return False
            return any(abs(s - sy) <= 1 and obs_fid in fids
                       for s, fids in club_by_pid_season[pid].items())

        def club_check(pid: str) -> str:
            if not obs_fid:
                return "no_obs_club"
            if club_in_season(pid):
                return "confirms"
            near = {f for s, fs in club_by_pid_season.get(pid, {}).items()
                    if sy is not None and abs(s - sy) <= 1 for f in fs}
            return "contradicts" if near else "no_career_club"

        def club_ids(pool: set[str]) -> list[str]:
            return sorted(p for p in pool if obs_fid and obs_fid in club_by_pid.get(p, set()))

        def q4_fallback():
            """PHASE_3J (identity_spine_spec Q4) — a truncated or bare-surname
            observed name, resolved only when the season also corroborates."""
            if sy is None:
                return None
            head, _, tail = pr.partition(",")
            st, gt = normalize(head).split(), normalize(tail).split()
            # A. drop a trailing quote-opened clip: "Elias 'Lar" -> "Elias"
            cleaned = _CLIP.sub("", pr).strip(" ,.")
            if cleaned and cleaned != pr:
                cc = {p for p in (alias_idx.get(normalize(cleaned))
                                  or key_idx.get(norm_key(cleaned)) or set()) if in_career(p)}
                if len(cc) == 1:
                    return next(iter(cc)), "name+season+trunc"
            # A'. trailing partial given token, no quote: "Victor Man" -> "Victor Manuel"
            if st and gt and len(gt[-1]) >= 3:
                hit = {pid for cg, pid in prefix_idx.get(st[0], [])
                       if len(gt) <= len(cg)
                       and all(cg[i] == gt[i] for i in range(len(gt) - 1))
                       and cg[len(gt) - 1].startswith(gt[-1]) and cg[len(gt) - 1] != gt[-1]}
                hit = {p for p in hit if in_career(p)}
                if len(hit) == 1:
                    return next(iter(hit)), "name+season+trunc"
            # C. bare surname (or an unmatched "surname, given") -> surname + club + season
            if st:
                pool = surname_idx.get(st[0], set())
                if gt:   # tighten with the given first-token prefix when it is present
                    pool = {p for p in pool
                            if (normalize(by_pid[p]["nombre"]).split()[:1] or [""])[0].startswith(gt[0])}
                sc = {p for p in pool if club_in_season(p)}
                if len(sc) == 1:
                    return next(iter(sc)), "surname+season+club"
            return None

        corroborated = {pid for pid in cands if in_career(pid)}
        club_hits = {pid for pid in corroborated if club_in_season(pid)}

        # PHASE_3I: bsnpr.com's records name this player the season's scoring
        # champion — a per-season attestation. Owner-approved corroboration for
        # a *unique* name candidate (D1: not name alone).
        title_ok = (sy is not None and len(cands) == 1
                    and sy in title_by_name.get(norm_key(pr), set()))

        if len(corroborated) == 1:
            pid = next(iter(corroborated))
            mapped.append({**o, "bsnpr_id": pid,
                           "canonical_name": by_pid[pid]["canonical_name"],
                           "match_method": "name+season_in_career",
                           "club_check": club_check(pid),
                           "confidence": "single-source"})
        elif title_ok:
            pid = next(iter(cands))
            mapped.append({**o, "bsnpr_id": pid,
                           "canonical_name": by_pid[pid]["canonical_name"],
                           "match_method": "name+season+title",
                           "club_check": club_check(pid),
                           "confidence": "single-source"})
        elif len(corroborated) > 1 and len(club_hits) == 1:
            # PHASE_3F: season corroborates several, club uniquely picks one
            pid = next(iter(club_hits))
            mapped.append({**o, "bsnpr_id": pid,
                           "canonical_name": by_pid[pid]["canonical_name"],
                           "match_method": "name+season+club",
                           "club_check": "confirms",
                           "confidence": "single-source"})
        elif len(cands) == 1 and not corroborated:
            pid = next(iter(cands))
            review.append({**o, "candidate_ids": pid,
                           "candidate_names": by_pid[pid]["canonical_name"],
                           "club_franchise_id": obs_fid, "club_match_ids": "|".join(club_ids(cands)),
                           "reason": "unique name match, season not in known career span (or player has no profile yet)"})
        elif len(corroborated) > 1:
            review.append({**o, "candidate_ids": "|".join(sorted(corroborated)),
                           "candidate_names": " | ".join(by_pid[p]["canonical_name"] for p in sorted(corroborated)),
                           "club_franchise_id": obs_fid, "club_match_ids": "|".join(club_ids(corroborated)),
                           "reason": "multiple players match name + season span"})
        elif cands:
            review.append({**o, "candidate_ids": "|".join(sorted(cands)),
                           "candidate_names": " | ".join(by_pid[p]["canonical_name"] for p in sorted(cands)),
                           "club_franchise_id": obs_fid, "club_match_ids": "|".join(club_ids(cands)),
                           "reason": "multiple name candidates, none corroborated by season"})
        else:
            hit = q4_fallback()
            if hit:
                pid, method = hit
                mapped.append({**o, "bsnpr_id": pid,
                               "canonical_name": by_pid[pid]["canonical_name"],
                               "match_method": method,
                               "club_check": club_check(pid),
                               "confidence": "single-source"})
            else:
                review.append({**o, "candidate_ids": "", "candidate_names": "",
                               "club_franchise_id": obs_fid, "club_match_ids": "",
                               "reason": "no canonical name match"})

    return mapped, review


# --------------------------------------------------------------------------- #
def main() -> int:
    if not (RAW_DIR / "enciclopedia").exists():
        print("! data/raw/players/enciclopedia missing — run `make fetch-players`", file=sys.stderr)
        return 1

    enc = parse_enciclopedia()
    prof, career = parse_jugador()
    canon = build_canonical(enc, prof)
    dob_settled = apply_dob_overrides(canon)   # curated birth-date fixes, jug05/jugador05-corroborated
    jug05_review: list[dict] = []
    jug05_merged: list[dict] = []
    jug05_conflicts: list[dict] = []
    jug05_season_totals: list[dict] = []
    jug05_foreign_rows: list[dict] = []
    if (RAW_DIR / "jug05").exists():
        j05 = merge_jug05(canon, career, parse_jug05())
        jug05_review, jug05_merged, jug05_conflicts = j05["review_list"], j05["merged"], j05["conflicts"]
        jug05_season_totals = j05["season_totals"]
        jug05_foreign_rows = j05["foreign_rows"]
    j05b_review: list[dict] = []
    j05b_bios: list[dict] = []
    j05b_dob: list[dict] = []
    if (RAW_DIR / "jugador05").exists():
        r = merge_jugador05(canon, parse_jugador05(), dob_settled)   # enrich-only; never mints (D1)
        j05b_review, j05b_bios, j05b_dob = r["review_list"], r["bio_rows"], r["dob_conflicts"]
    aliases = build_aliases(canon, enc)   # after minting, so jug05 rows get aliases
    seed_historic_spans(canon, aliases)   # PHASE_3I — title-attested career spans
    mapped, review = build_id_map(canon, aliases, career)
    disputed_problems = check_disputed_rows(career, load_disputed_rows())   # J16 A05 — flagged, not dropped
    if disputed_problems:
        sys.exit("! " + "\n! ".join(disputed_problems))

    _write_csv(CLEAN_DIR / "players_canonical.csv",
               sorted(canon, key=lambda c: int(c["bsnpr_id"])), [
        "bsnpr_id", "canonical_name", "normalized_name", "apellidos", "nombre",
        "nickname", "birth_date", "birth_year", "birth_city", "nationality",
        "position", "first_season", "last_season", "n_seasons", "has_profile",
        "confidence", "source_id", "source_url", "retrieved_at",
    ])
    _write_csv(CLEAN_DIR / "player_aliases.csv",
               sorted(aliases, key=lambda a: (int(a["bsnpr_id"]), a["alias_type"], a["alias"])),
               ["bsnpr_id", "alias", "normalized_alias", "alias_type", "source"])
    _write_csv(CLEAN_DIR / "player_career_seasons.csv",
               sorted(career, key=lambda r: (int(r["bsnpr_id"]), r["season"], r["team_raw"])),
               ["bsnpr_id", "season", "team_raw", "games", "points",
                "source_id", "source_url", "retrieved_at"])
    _write_csv(CLEAN_DIR / "player_id_map.csv",
               sorted(mapped, key=lambda r: (r["obs_source"], r["player_raw"], r["season"])),
               ["obs_source", "player_raw", "club_raw", "season", "bsnpr_id",
                "canonical_name", "match_method", "club_check", "confidence"])
    _write_csv(INTERIM_DIR / "player_review_queue.csv",
               sorted(review, key=lambda r: (r["reason"], r["player_raw"], r["season"])),
               ["obs_source", "player_raw", "club_raw", "season",
                "candidate_ids", "candidate_names", "club_franchise_id",
                "club_match_ids", "reason"])
    _write_csv(INTERIM_DIR / "jug05_review.csv",
               sorted(jug05_review, key=lambda r: r["name"]),
               ["name", "birth_date", "position", "seasons", "collides_with"])
    write_career_logs(jug05_merged, jug05_conflicts)
    write_season_totals_log(jug05_season_totals)
    write_foreign_rows_log(jug05_foreign_rows)
    _write_csv(CLEAN_DIR / "player_bios.csv",
               sorted(j05b_bios, key=lambda r: int(r["bsnpr_id"])),
               ["bsnpr_id", "notes_es", "birthplace", "roster_team", "roster_year",
                "jersey", "source_id", "source_url", "retrieved_at"])
    _write_csv(INTERIM_DIR / "jugador05_review.csv",
               sorted(j05b_review, key=lambda r: r["name"]),
               ["name", "birth_date", "position", "birth_city", "roster_team",
                "roster_year", "note"])
    _write_csv(INTERIM_DIR / "jugador05_dob_conflicts.csv",
               sorted(j05b_dob, key=lambda r: int(r["bsnpr_id"])),
               ["bsnpr_id", "canonical_name", "canonical_dob", "jugador05_dob"])

    with_profile = sum(1 for c in canon if c["has_profile"] == "yes")
    with_birth = sum(1 for c in canon if c["birth_year"])
    print(f"\n[done] canonical {len(canon)} ({with_profile} w/ profile, {with_birth} w/ birth year); "
          f"aliases {len(aliases)}; id_map {len(mapped)}; review queue {len(review)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
