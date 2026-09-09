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
  data/clean/player_id_map.csv        observation player_raw -> bsnpr_id, with
    match_method + confidence. Only rows that clear the D1 bar land here.
  data/interim/player_review_queue.csv  everything that did not — ambiguous or
    name-only matches, with the candidate ids and the reason.

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
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

from src.wayback_cdx import REPO_ROOT
from src.parse_wayback import decode_html, squish, to_int
from src.parse_pre2007 import _write_csv  # noqa: F401 - re-exported helper

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
                    "estadistica jugador", "jugador", "jugadores"}


def clean_field(raw: str) -> str:
    s = squish(raw or "")
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
# assembly                                                                     #
# --------------------------------------------------------------------------- #
def build_canonical(enc: dict[str, dict], prof: dict[str, dict]) -> list[dict]:
    rows: list[dict] = []
    for pid, e in sorted(enc.items(), key=lambda kv: int(kv[0])):
        p = prof.get(pid, {})
        apellidos = clean_field(e["apellidos"])
        nombre = p.get("profile_name", "").split(",")[-1].strip() if p.get("profile_name") else clean_field(e["nombre"])
        # jugador.asp heading is "Apellidos, Nombre"; prefer its apellidos if present
        if p.get("profile_name") and "," in p["profile_name"]:
            apellidos = p["profile_name"].split(",")[0].strip() or apellidos
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

    def resolve_club(raw: str) -> str:
        if not raw:
            return ""
        s = squish(raw)
        if s.upper() in code_map:
            return code_map[s.upper()]
        parts = _DE_SPLIT.split(s, maxsplit=1)
        nick = normalize(parts[0]) if parts else ""
        city = normalize(parts[1]) if len(parts) == 2 else ""
        city_fid = city_map.get(city)
        nick_fid = None if nick in nick_ambiguous else nick_map.get(nick)
        if city_fid and (not nick_fid or nick_fid == city_fid):
            return city_fid
        if nick_fid and not city:
            return nick_fid
        if nick and city:
            return f"{nick}_{city}"          # synthetic — consistent both sides
        # bare single token: could be a city or an (unambiguous) nickname
        return city_map.get(nick) or ("" if nick in nick_ambiguous else nick_map.get(nick, "")) or ""

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

    career_by_pid: dict[str, set[int]] = {}
    for r in career:
        career_by_pid.setdefault(r["bsnpr_id"], set()).add(r["season"])

    # club-code corroboration (PHASE_3F): franchise key per (pid, season)
    resolve_club = _load_club_resolver()
    club_by_pid_season: dict[str, dict[int, set[str]]] = {}
    club_by_pid: dict[str, set[str]] = {}
    for r in career:
        fid = resolve_club(r["team_raw"])
        if not fid:
            continue
        club_by_pid_season.setdefault(r["bsnpr_id"], {}).setdefault(r["season"], set()).add(fid)
        club_by_pid.setdefault(r["bsnpr_id"], set()).add(fid)

    mapped: list[dict] = []
    review: list[dict] = []

    for o in _load_observations():
        pr, season = o["player_raw"], o["season"]
        cands = alias_idx.get(normalize(pr), set()) or key_idx.get(norm_key(pr), set())
        cands = set(cands)
        sy = int(season) if re.fullmatch(r"\d{4}", season) else None
        obs_fid = resolve_club(o["club_raw"])

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

        corroborated = {pid for pid in cands if in_career(pid)}
        club_hits = {pid for pid in corroborated if club_in_season(pid)}

        if len(corroborated) == 1:
            pid = next(iter(corroborated))
            mapped.append({**o, "bsnpr_id": pid,
                           "canonical_name": by_pid[pid]["canonical_name"],
                           "match_method": "name+season_in_career",
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
    aliases = build_aliases(canon, enc)
    mapped, review = build_id_map(canon, aliases, career)

    _write_csv(CLEAN_DIR / "players_canonical.csv", canon, [
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

    with_profile = sum(1 for c in canon if c["has_profile"] == "yes")
    with_birth = sum(1 for c in canon if c["birth_year"])
    print(f"\n[done] canonical {len(canon)} ({with_profile} w/ profile, {with_birth} w/ birth year); "
          f"aliases {len(aliases)}; id_map {len(mapped)}; review queue {len(review)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
