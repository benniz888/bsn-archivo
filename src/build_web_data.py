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
import unicodedata
from pathlib import Path

from src.wayback_cdx import REPO_ROOT
from src.parse_wayback import open_clean_text

CLEAN = REPO_ROOT / "data" / "clean"
APP = REPO_ROOT / "app"
WEB = REPO_ROOT / "web" / "data"

SCHEMA_VERSION = 1
_DE_SPLIT = re.compile(r"\s+de\s+|,\s*", re.I)   # "Nick de City" / "Nick, City"


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


def _reset_dir(path: Path) -> None:
    """Empty a generated subtree before rebuilding it, so a rerun after the data
    shrinks leaves no orphan files (the tree must be a pure function of the CSVs)."""
    if path.exists():
        for p in sorted(path.rglob("*"), reverse=True):
            p.unlink() if p.is_file() else p.rmdir()


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


def _app_norm(s: str) -> str:
    """Match the app's `norm()` (bsn_archivo.html) exactly: lower, NFD, drop
    combining marks, strip « » " ' . — no internal-whitespace collapse."""
    s = unicodedata.normalize("NFD", (s or "").lower())
    s = "".join(c for c in s if not 0x300 <= ord(c) <= 0x36F)
    return re.sub(r"[«»\"'.]", "", s).strip()


def build_player_xwalk() -> Path:
    """web/data/index/player_xwalk.json — { norm(curated PINDEX name): bsnpr_id }
    for the app's `showPlayer` career-detail lookup (5D.3b). Only rows the owner
    signed off (verdict auto/review); `none` rows stay curated-only. Source of
    truth is app/player_crosswalk.csv."""
    out: dict[str, int] = {}
    path = APP / "player_crosswalk.csv"
    with open_clean_text(path, "r") as fh:
        for r in csv.DictReader(fh):
            if r["verdict"] not in ("auto", "review"):
                continue
            pid = _int(r["bsnpr_id"])
            if pid is not None:
                out[_app_norm(r["curated_name"])] = pid
    _jdump(out, WEB / "index" / "player_xwalk.json")
    return WEB / "index" / "player_xwalk.json"


def _scoring_club_resolver():
    """A scoring-champion `club_raw` -> franchise_id. Wider than `_team_resolver`
    (city only): also matches a full franchise name and an unambiguous nickname,
    since the sources give a mix ("SAN JUAN", "Capitanes de Arecibo", "Cariduros")."""
    by_city = _team_resolver()
    master = _read("franchises.csv")
    by_name = {_norm(r["canonical_name"]): r["franchise_id"] for r in master}
    by_nick: dict[str, str] = {}
    ambiguous: set[str] = set()
    for r in master:
        parts = _DE_SPLIT.split(r["canonical_name"], maxsplit=1)
        if len(parts) == 2:
            n = _norm(parts[0])
            if n in by_nick and by_nick[n] != r["franchise_id"]:
                ambiguous.add(n)
            else:
                by_nick[n] = r["franchise_id"]

    def resolve(raw: str) -> str | None:
        if not raw:
            return None
        n = _norm(raw.split(",")[0])   # "Capitanes, Arecibo" -> "capitanes"
        return (by_city(raw) or by_name.get(_norm(raw)) or by_name.get(n)
                or (None if n in ambiguous else by_nick.get(n)))
    return resolve


def build_scoring_titles() -> Path:
    hist = {r["season"]: r for r in _read("historic_scoring_champions.csv")}
    seed = {r["season"]: r for r in _read("bsn_scoring_champions.csv")}
    lead: dict[str, str] = {}
    for r in _read("player_season_leaders.csv"):
        if r["category"] == "anotaciones" and r["rank"] == "1":
            lead[r["season"]] = r["club_raw"]
    resolve = _scoring_club_resolver()

    def club_of(season: str, prefer_raw: str = "") -> tuple:
        raw = (prefer_raw or (seed[season]["club"] if season in seed else "")
               or (hist[season]["team_raw"] if season in hist else "")
               or lead.get(season, "")) or None
        return raw, (resolve(raw) if raw else None)

    out = []
    for r in _read("scoring_champions_reconciled.csv"):
        s = r["season"]
        rec = {
            "season": _int(s), "metric_era": r["metric_era"],
            "agreement": r["agreement"], "confidence": r["confidence"],
            "sources": [x.strip() for x in r["sources"].split(";") if x.strip()],
            "note": r["note"] or None, "champion": None, "dual": None,
        }
        if r["agreement"] == "dual_metric_d4":
            praw, pfid = club_of(s)
            rec["dual"] = {
                "ppg": {"player": r["ppg_champion"], "value": _float(r["ppg_value"]),
                        "club_raw": praw, "franchise_id": pfid},
                "total_points": {"player": r["total_points_champion"],
                                 "value": _int(r["total_points_value"]),
                                 "club_raw": (hist[s]["team_raw"] if s in hist else None),
                                 "franchise_id": resolve(hist[s]["team_raw"]) if s in hist else None},
            }
        else:
            craw, cfid = club_of(s)
            rec["champion"] = {
                "player": r["historic_player"] or r["seed_player"] or r["leaders_player"] or None,
                "club_raw": craw, "franchise_id": cfid,
                "ppg": _float(r["historic_ppg"]) or _float(r["leaders_ppg"]),
                "total_points": _int(r["historic_total"])
                or (_int(r["seed_value"]) if r["metric_era"] == "total_points" else None),
            }
        out.append(rec)
    out.sort(key=lambda x: x["season"] or 0)
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
# 5C — per-entity files: players/ seasons/ games/                              #
# --------------------------------------------------------------------------- #
def _team_resolver():
    """team_raw (a bare, case-inconsistent city name in the game + leader data)
    -> franchise_id | None, via city_franchise_map.csv. For the 2001-2013 game
    seasons the San Juan / Rio Piedras era-ambiguity does not arise."""
    city = {}
    for r in _read("city_franchise_map.csv"):
        city[_norm(r["normalized_city"])] = r["franchise_id"]

    def resolve(team_raw: str) -> str | None:
        return city.get(_norm(team_raw))
    return resolve


def _norm(s: str) -> str:
    s = "".join(c for c in unicodedata.normalize("NFD", s or "")
                if unicodedata.category(c) != "Mn")
    return " ".join(s.lower().split())


def _box_num_cols():
    return ["minutes", "fg2m", "fg2a", "fg3m", "fg3a", "ftm", "fta",
            "oreb", "dreb", "reb", "ast", "stl", "blk", "pf", "tov", "pts"]


def _lev(a: str, b: str) -> int:
    if abs(len(a) - len(b)) > 3:
        return 9
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def _titlecase(s: str) -> str:
    """ALL-CAPS archive name -> readable. Accents can't be recovered from the
    source, so "NEFTALI" stays "Neftali"; "McCADNEY" -> "McCadney"."""
    def cap(m):
        w = m.group(0)
        if w[:2].lower() == "mc" and len(w) > 2:
            return "Mc" + w[2].upper() + w[3:].lower()
        return w[0].upper() + w[1:].lower()
    s = re.sub(r"[^\W\d_]+", cap, s, flags=re.UNICODE)
    return s.replace("‘", "«").replace("’", "»").replace("'", "").replace('"', "")


# MVP nicknames the archive's all-caps table uses in place of the given name
_MVP_NICK = {"teo": "teofilo", "johny": "johnny", "pachin": "juan"}


def _mvp_name_match(app_name: str, csv_name: str) -> bool:
    """Same MVP or not — tolerant of the archive's nickname forms ("TEO CRUZ")
    and typos ("GOERGIE"), strict on a genuinely different person."""
    strip = lambda x: " ".join(re.sub(r"[’‘'`\"«».,\-]", " ", _norm(x)).split())
    na, nb = strip(app_name), strip(csv_name)
    if na == nb:
        return True
    ta, tb = na.split(), nb.split()
    if not ta or not tb or _lev(ta[-1], tb[-1]) > 1:      # surname must be close
        return False
    ga, gb = ta[0], tb[0]
    return (ga == gb or _lev(ga, gb) <= 2
            or _MVP_NICK.get(ga) == gb or _MVP_NICK.get(gb) == ga)


def _parse_app_mvp() -> dict[int, str]:
    """{year: player} from the app's baked `const MVP_YEARS=[...]` block."""
    html = (REPO_ROOT / "app" / "bsn_archivo.html").read_text(encoding="utf-8")
    blk = html[html.index("const MVP_YEARS=["):html.index("];", html.index("const MVP_YEARS="))]
    return {int(y): n for y, n, _c in re.findall(r"\[(\d{4}),'([^']*)','([^']*)'\]", blk)}


def build_mvp() -> Path:
    """web/data/index/mvp.json — the archive's MVP-por-año table (historic_awards
    `award==mvp`, one 2004 capture of lidereshistoricos.asp?t=3, 1958-2003).
    `also` is set only where this genuinely disagrees with the app's baked row
    for a shared year (the app value stays canonical; `also` becomes a footnote).
    """
    app_mvp = _parse_app_mvp()
    resolve_team = _team_resolver()
    idmap: dict[tuple[str, str], str] = {}
    for r in _read("player_id_map.csv"):
        idmap[(_norm(r["player_raw"]), r["season"])] = r["bsnpr_id"]
    out = []
    for r in _read("historic_awards.csv"):
        if r["award"] != "mvp":
            continue
        yr = _int(r["season"])
        disagree = yr in app_mvp and not _mvp_name_match(app_mvp[yr], r["player_raw"])
        out.append({
            "season": yr,
            "player": _titlecase(r["player_raw"]),
            "player_raw": r["player_raw"],
            "bsnpr_id": _int(idmap.get((_norm(r["player_raw"]), r["season"]))),
            "franchise_id": resolve_team(r["team_raw"]),
            "team_raw": _titlecase(r["team_raw"]),
            "also": _titlecase(r["player_raw"]) if disagree else None,
        })
    out.sort(key=lambda m: m["season"])
    _jdump(out, WEB / "index" / "mvp.json")
    return WEB / "index" / "mvp.json"


def diff_app_mvp() -> list[str]:
    """Shared MVP years where the app and historic_awards genuinely name a
    different player. Printed, not written — like diff_app_champions."""
    app_mvp = _parse_app_mvp()
    csv_mvp = {_int(r["season"]): r["player_raw"] for r in _read("historic_awards.csv")
               if r["award"] == "mvp"}
    diffs = []
    for yr in sorted(set(app_mvp) & set(csv_mvp)):
        if not _mvp_name_match(app_mvp[yr], csv_mvp[yr]):
            diffs.append(f"  {yr}: app={app_mvp[yr]!r}  archive={csv_mvp[yr]!r}")
    return diffs


def build_players_detail() -> tuple[int, int]:
    """web/data/players/<bsnpr_id>.json for every id in players_canonical. Players
    with a profile / career rows / id_map observation get a full record; the rest
    get a thin one (name, birth, position, aliases — `has_profile: false`, empty
    `career`) so the app's profile view always has a real card to render and can
    show an honest "sin ficha detallada" note instead of a dead end."""
    canon = {r["bsnpr_id"]: r for r in _read("players_canonical.csv")}
    aliases: dict[str, list] = {}
    for a in _read("player_aliases.csv"):
        if a["alias_type"] not in ("canonical", "normalized"):
            aliases.setdefault(a["bsnpr_id"], []).append(
                {"alias": a["alias"], "type": a["alias_type"]})
    career: dict[str, list] = {}
    for r in _read("player_career_seasons.csv"):
        career.setdefault(r["bsnpr_id"], []).append(r)
    obs: dict[str, list] = {}
    for r in _read("player_id_map.csv"):
        obs.setdefault(r["bsnpr_id"], []).append(r)
    resolve_team = _team_resolver()

    # one file per canonical id. A career/obs row for an id absent from
    # players_canonical (id 13352: a jugador.asp career with no enciclopedia
    # entry) is skipped — it would be an unnamed, unsearchable file.
    _reset_dir(WEB / "players")
    n = n_thin = 0
    for pid in sorted(canon, key=int):
        c = canon.get(pid, {})
        rec = {
            "id": int(pid),
            "name": c.get("canonical_name") or "",
            "aliases": sorted(aliases.get(pid, []), key=lambda a: (a["type"], a["alias"])),
            "birth": {"date": c.get("birth_date") or None,
                      "year": _int(c.get("birth_year")),
                      "city": c.get("birth_city") or None},
            "position": c.get("position") or None,
            "nationality": c.get("nationality") or None,
            "has_profile": c.get("has_profile") == "yes",
            "career": sorted(
                ({"season": _int(r["season"]), "team_raw": r["team_raw"],
                  "franchise_id": resolve_team(r["team_raw"].split(",")[-1]),
                  "games": _int(r["games"]), "points": _int(r["points"])}
                 for r in career.get(pid, [])),
                key=lambda x: (x["season"] or 0, x["team_raw"])),
            "observations": sorted(
                ({"obs_source": r["obs_source"], "season": _int(r["season"]),
                  "club_raw": r["club_raw"], "match_method": r["match_method"],
                  "club_check": r["club_check"]}
                 for r in obs.get(pid, [])),
                key=lambda x: (x["obs_source"], x["season"] or 0, x["club_raw"])),
            "sources": [c["source_url"]] if c.get("source_url") else [],
        }
        if not (rec["career"] or rec["observations"] or rec["has_profile"]):
            n_thin += 1
        _jdump(rec, WEB / "players" / f"{pid}.json")
        n += 1
    return n, n_thin


_LEADER_CATS_ES = {
    "anotaciones": "scoring", "rebotes": "rebounds", "asistencias": "assists",
    "bloqueos": "blocks", "cortes_balon": "steals", "turnovers": "turnovers",
    "canastos_3": "threes", "canastos_3_pct": "three_pct", "rebotes_ofensivos": "off_rebounds",
    "tiros_libres_anotados": "free_throws", "tiros_libres_pct": "free_throw_pct",
}


def _season_leaders() -> dict[str, dict]:
    """season -> {category: [ {rank, player_raw, club_raw, value, games, kind} ]}
    merged from the 1986/2007+ board and the 2000-2002 <pre> board."""
    out: dict[str, dict] = {}
    for r in _read("player_season_leaders.csv"):
        cat = _LEADER_CATS_ES.get(r["category"], r["category"])
        out.setdefault(r["season"], {}).setdefault(cat, []).append({
            "rank": _int(r["rank"]), "player_raw": r["player_raw"],
            "club_raw": r["club_raw"], "value": _float(r["prom"]),
            "games": _int(r["games"]), "kind": r["prom_kind"],
        })
    for r in _read("player_season_leaders_2000_2002.csv"):
        cat = _LEADER_CATS_ES.get(r["category"], r["category"])
        if r["serie"] and r["serie"] != "Serie Regular":
            continue
        out.setdefault(r["season"], {}).setdefault(cat, []).append({
            "rank": _int(r["rank"]), "player_raw": r["player_raw"],
            "club_raw": r["club_raw"], "value": _float(r["prom"]),
            "games": _int(r["games"]), "kind": r["prom_kind"],
        })
    for s in out:
        for cat in out[s]:
            out[s][cat].sort(key=lambda x: x["rank"] or 99)
    return out


def _standings_from_games(resolve_team) -> dict[str, list]:
    """season -> [ {team_raw, franchise_id, w, l, games_recorded} ] from the
    archived game_results. Marked partial in the season file — the archive is
    not a complete game set for most seasons (5A OQ4)."""
    rec: dict[str, dict] = {}
    for r in _read("game_results.csv"):
        a, b = _int(r["score_a"]), _int(r["score_b"])
        if a is None or b is None:
            continue
        s = r["season"]
        for team, mine, theirs in ((r["team_a_raw"], a, b), (r["team_b_raw"], b, a)):
            key = _norm(team)
            d = rec.setdefault(s, {}).setdefault(key, {"team_raw": team, "w": 0, "l": 0})
            d["w" if mine > theirs else "l"] += 1
    out = {}
    for s, teams in rec.items():
        rows = []
        for d in teams.values():
            rows.append({"team_raw": d["team_raw"].title(),
                         "franchise_id": resolve_team(d["team_raw"]),
                         "w": d["w"], "l": d["l"]})
        rows.sort(key=lambda x: (-(x["w"] / max(x["w"] + x["l"], 1)), -x["w"], x["team_raw"]))
        out[s] = rows
    return out


def build_seasons_detail() -> int:
    champ = {r["season"]: r for r in _read("champions_reconciled.csv")}
    tracked = {r["season"]: r for r in _read("seasons_stats_tracked.csv")}
    gaps: dict[str, list] = {}
    for r in _read("leader_coverage_gaps.csv"):
        gaps.setdefault(r["season"], []).append({"status": r["status"], "detail": r["detail"]})
    hist_sc: dict[str, dict] = {r["season"]: r for r in _read("historic_scoring_champions.csv")}
    awards: dict[str, list] = {}
    for r in _read("historic_awards.csv"):
        awards.setdefault(r["season"], []).append(
            {"award": r["award"], "player_raw": r["player_raw"], "team_raw": r["team_raw"]})
    leaders = _season_leaders()
    resolve_team = _team_resolver()
    standings = _standings_from_games(resolve_team)
    games_per_season: dict[str, int] = {}
    for r in _read("game_results.csv"):
        games_per_season[r["season"]] = games_per_season.get(r["season"], 0) + 1

    all_seasons = (set(champ) | set(leaders) | set(awards) | set(hist_sc)
                   | set(standings) | set(tracked))
    _reset_dir(WEB / "seasons")
    for s in sorted(all_seasons):
        cr = champ.get(s, {})
        st = standings.get(s)
        rec = {
            "season": s,
            "champion": cr.get("champion_franchise_id") or None,
            "runner_up": cr.get("runner_up_franchise_id") or None,
            "agreement": cr.get("agreement") or None,
            "confidence": cr.get("confidence") or None,
            "standings": ({"rows": st, "games_recorded": games_per_season.get(s, 0),
                           "complete": games_per_season.get(s, 0) >= 140,
                           "note": "Derived from the games in the Wayback archive — "
                                   "not a complete season unless flagged complete."}
                          if st else None),
            "leaders": leaders.get(s) or None,
            "awards": awards.get(s) or None,
            "scoring_champion": ({"player_raw": hist_sc[s]["player_raw"],
                                  "team_raw": hist_sc[s]["team_raw"],
                                  "total_points": _int(hist_sc[s]["total_points"]),
                                  "ppg": _float(hist_sc[s]["ppg"]),
                                  "metric_era": hist_sc[s]["metric_era"]}
                                 if s in hist_sc else None),
            "coverage": {
                "stats_tracked": {k: (v == "1") for k, v in tracked.get(s, {}).items()
                                  if k != "season"} or None,
                "gaps": gaps.get(s) or None,
            },
        }
        _jdump(rec, WEB / "seasons" / f"{s}.json")
    return {
        "season_files": len(all_seasons),
        "seasons_with_leaders": sum(1 for s in all_seasons if leaders.get(s)),
        "seasons_with_awards": sum(1 for s in all_seasons if awards.get(s)),
        "seasons_with_standings": sum(1 for s in all_seasons if standings.get(s)),
        "seasons_with_scoring_champ": sum(1 for s in all_seasons if s in hist_sc),
    }


def _quarters(v: str):
    """`"24-24-28-16-0-0"` -> `[24, 24, 28, 16]` (trailing padding zeros dropped).
    All-zero / blank -> None."""
    nums = [int(p) for p in (v or "").split("-") if p.lstrip("-").isdigit()]
    last = next((i for i in range(len(nums), 0, -1) if nums[i - 1] != 0), 0)
    return nums[:last] or None


def build_games() -> tuple[int, int]:
    resolve_team = _team_resolver()
    results = {r["game_id"]: r for r in _read("game_results.csv")}
    box: dict[str, list] = {}
    for r in _read("game_box_player.csv"):
        box.setdefault(r["game_id"], []).append(r)

    all_gids = set(results) | set(box)
    by_season: dict[str, list] = {}
    _reset_dir(WEB / "games")
    for gid in sorted(all_gids):
        res = results.get(gid, {})
        rows = box.get(gid, [])
        season = res.get("season") or (rows[0]["season"] if rows else "unknown")
        date = res.get("date") or (rows[0]["date"] if rows else None)

        rec = {
            "game_id": gid, "season": _int(season) if season.isdigit() else season,
            "date": date, "script": res.get("script") or None,
            "teams": {
                "a": {"team_raw": res.get("team_a_raw") or None,
                      "franchise_id": resolve_team(res.get("team_a_raw", ""))},
                "b": {"team_raw": res.get("team_b_raw") or None,
                      "franchise_id": resolve_team(res.get("team_b_raw", ""))},
            },
            "score": {"a": _int(res.get("score_a")), "b": _int(res.get("score_b"))},
            "quarters": ({"a": _quarters(res.get("quarters_a")),
                          "b": _quarters(res.get("quarters_b"))}
                         if res.get("quarters_a") else None),
            "box": sorted(
                ({"player_raw": r["player_raw"], "bsnpr_id": _int(r["bsnpr_id"]),
                  "team_raw": r["team_raw"], "jersey": r["jersey"] or None,
                  "box_check": r["box_check"],
                  **{c: _int(r[c]) for c in _box_num_cols()}}
                 for r in rows),
                key=lambda x: (x["team_raw"], -(x["pts"] or 0), x["player_raw"])),
            "sources": sorted({r["source_url"] for r in ([res] if res else []) + rows if r.get("source_url")}),
        }
        _jdump(rec, WEB / "games" / str(season) / f"{gid}.json")
        by_season.setdefault(season, []).append({
            "game_id": gid, "date": date,
            "a": {"team_raw": rec["teams"]["a"]["team_raw"], "score": rec["score"]["a"]},
            "b": {"team_raw": rec["teams"]["b"]["team_raw"], "score": rec["score"]["b"]},
        })

    for season, lst in by_season.items():
        lst.sort(key=lambda g: (g["date"] or "", g["game_id"]))
        _jdump(lst, WEB / "games" / str(season) / "index.json")
    return len(all_gids), len(by_season)


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
        "player_xwalk": build_player_xwalk(),
        "mvp": build_mvp(),
    }
    counts = {}
    for name, path in built.items():
        obj = json.loads(path.read_text(encoding="utf-8"))
        counts[name] = len(obj["categories"]) if name == "career_leaders" else len(obj)
        print(f"  -> {path.relative_to(REPO_ROOT)} ({counts[name]})")

    # 5C — per-entity files
    n_pdetail, n_pthin = build_players_detail()
    season_counts = build_seasons_detail()
    n_games, n_gseasons = build_games()
    counts["player_files"] = n_pdetail
    counts.update(season_counts)
    counts["game_files"] = n_games
    print(f"  -> web/data/players/*.json ({n_pdetail}; {n_pthin} thin / no career table)")
    print(f"  -> web/data/seasons/*.json ({season_counts['season_files']}; "
          f"leaders {season_counts['seasons_with_leaders']}, "
          f"awards {season_counts['seasons_with_awards']}, "
          f"standings {season_counts['seasons_with_standings']})")
    print(f"  -> web/data/games/<season>/*.json ({n_games} games, {n_gseasons} seasons)")

    SOURCES = [
        "franchises.csv", "champions_reconciled.csv", "franchise_events.csv",
        "players_canonical.csv", "player_aliases.csv", "player_career_seasons.csv",
        "player_id_map.csv", "scoring_champions_reconciled.csv",
        "historic_scoring_champions.csv", "historic_awards.csv",
        "bsn_scoring_champions.csv",
        "player_season_leaders.csv", "player_season_leaders_2000_2002.csv",
        "seasons_stats_tracked.csv", "leader_coverage_gaps.csv",
        "city_franchise_map.csv", "game_results.csv", "game_box_player.csv",
        "bsn_career_leaders.csv", "bsn_records.csv",
        "franchise_key_map.csv", "franchise_curated.json", "player_crosswalk.csv",
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

    mvp_diffs = diff_app_mvp()
    if mvp_diffs:
        print(f"\n[app MVP_YEARS vs historic_awards] {len(mvp_diffs)} genuine name disagreement(s) "
              f"(app value stays canonical; carried as `also` footnote):")
        print("\n".join(mvp_diffs))
    else:
        print("\n[app MVP_YEARS vs historic_awards] no genuine disagreements")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
