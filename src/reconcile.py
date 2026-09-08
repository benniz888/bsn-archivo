"""PHASE_4 — reconcile the parsed archive data against the inherited seed CSVs.

Produces a merged view where sources agree and a single flagged-conflicts file
where they do not. **No conflict is ever resolved automatically** — where two
sources disagree, both values and both sources are recorded and the row is
flagged for the owner (per the phase instruction and PC1).

Inputs (all in data/clean/):
  seed:    bsn_champions_by_season.csv, bsn_franchises.csv, bsn_scoring_champions.csv
  archive: champions_from_bsnpr.csv (PHASE_3), historic_scoring_champions.csv,
           player_season_leaders.csv (PHASE_3/3C)

Outputs (data/clean/):
  franchises.csv               franchise master (seed + names only in game rows)
  franchise_events.csv         D2 lineage as dated events, each with confidence
  city_franchise_map.csv       (normalized city, season range) -> franchise_id
  club_code_map.csv            lideres200x / equiposstat codes -> franchise_id
  champions_reconciled.csv     season x {champion, runner_up}, agreement status
  scoring_champions_reconciled.csv   1948-> merged, D4 metric boundary respected
  reconcile_conflicts.csv      THE flagged-conflicts file — both sources, no winner

Run: `python -m src.reconcile`   (`make reconcile`)
"""

from __future__ import annotations

import csv
import re
import sys
import unicodedata
from pathlib import Path

from src.wayback_cdx import REPO_ROOT
from src.parse_pre2007 import _write_csv

CLEAN = REPO_ROOT / "data" / "clean"
SEED_SRC = "en.wikipedia.org/wiki/Baloncesto_Superior_Nacional"
BSNPR_SRC = "wayback:bsnpr.com/estadisticas/campeonatos.asp"


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def ncity(s: str) -> str:
    return re.sub(r"\s+", " ", strip_accents(s).upper().replace(".", " ")).strip()


# --------------------------------------------------------------------------- #
# franchise knowledge (D2 + names that appear only in champion/scoring rows)   #
# --------------------------------------------------------------------------- #
# franchise_id -> (canonical_name, city, founded, status)
FRANCHISES: dict[str, tuple[str, str, str, str]] = {
    "atleticos_san_german": ("Atleticos de San German", "San German", "1930", "active"),
    "cangrejeros_santurce": ("Cangrejeros de Santurce", "Santurce", "1918", "active"),
    "capitanes_arecibo": ("Capitanes de Arecibo", "Arecibo", "1946", "active"),
    "criollos_caguas": ("Criollos de Caguas", "Caguas", "1976", "active"),
    "santeros_aguada": ("Santeros de Aguada", "Aguada", "1992", "active"),
    "gigantes_carolina": ("Gigantes de Carolina", "Carolina", "1971", "active"),
    "indios_mayaguez": ("Indios de Mayaguez", "Mayaguez", "1956", "active"),
    "leones_ponce": ("Leones de Ponce", "Ponce", "1946", "active"),
    "mets_guaynabo": ("Mets de Guaynabo", "Guaynabo", "1935", "active"),
    "osos_manati": ("Osos de Manati", "Manati", "2014", "active"),
    "piratas_quebradillas": ("Piratas de Quebradillas", "Quebradillas", "1926", "active"),
    "vaqueros_bayamon": ("Vaqueros de Bayamon", "Bayamon", "1930", "active"),
    "atenienses_manati": ("Atenienses de Manati", "Manati", "2014", "defunct 2017"),
    "avancinos_villalba": ("Avancinos de Villalba", "Villalba", "1996", "defunct 1998"),
    "cardenales_rio_piedras": ("Cardenales de Rio Piedras", "Rio Piedras", "1940", "defunct 1985"),
    "cariduros_fajardo": ("Cariduros de Fajardo", "Fajardo", "1973", "defunct 2023"),
    "conquistadores_aguada": ("Conquistadores de Aguada", "Aguada", "1994", "defunct 1998"),
    "gallitos_isabela": ("Gallitos de Isabela", "Isabela", "1969", "defunct 2005"),
    "grises_humacao": ("Grises de Humacao", "Humacao", "2005", "defunct 2023"),
    "indios_canovanas": ("Indios de Canovanas", "Canovanas", "1980", "defunct 1996"),
    "maratonistas_coamo": ("Maratonistas de Coamo", "Coamo", "1985", "defunct 2015"),
    "polluelos_aibonito": ("Polluelos de Aibonito", "Aibonito", "1977", "defunct 2001"),
    "tainos_cabo_rojo": ("Tainos de Cabo Rojo", "Cabo Rojo", "1989", "defunct 1993"),
    "tiburones_aguadilla": ("Tiburones de Aguadilla", "Aguadilla", "1990", "defunct 1998"),
    "titanes_morovis": ("Titanes de Morovis", "Morovis", "1977", "defunct 2006"),
    "toritos_cayey": ("Toritos de Cayey", "Cayey", "2002", "defunct 2004"),
    "capitalinos_san_juan": ("Capitalinos de San Juan", "San Juan", "1930", "defunct 1998"),
    "brujos_guayama": ("Brujos de Guayama", "Guayama", "1971", "relocated 2022"),
    # --- names that appear only in champion / scoring-champion rows ---
    "santos_san_juan": ("Santos de San Juan", "San Juan", "1971", "defunct ~1980"),
    "club_nautico_san_juan": ("Club Nautico de San Juan", "San Juan", "1930", "defunct ~1940"),
    "cocoteros_tortuguero": ("Cocoteros de Tortuguero", "Tortuguero", "1943", "defunct ~1944"),
    "gallitos_upr": ("Gallitos de la UPR", "Rio Piedras", "1930", "defunct ~1955"),
    "vega_baja": ("Vega Baja", "Vega Baja", "1934", "defunct ~1940"),
}

# D2 lineage — (event_type, season, from_id, to_id, confidence, note)
FRANCHISE_EVENTS: list[tuple] = [
    ("relocated_renamed", "2022", "brujos_guayama", "osos_manati", "verified",
     "D2: Brujos de Guayama -> Osos de Manati (2022). Note: an earlier Manati "
     "franchise 'Atenienses de Manati' (2014-2017) and the seed's 'Osos de "
     "Manati founded 2014' row make the Osos identity itself ambiguous — flagged."),
    ("renamed", "2023", "grises_humacao", "criollos_caguas", "disputed",
     "D2: Grises de Humacao -> Criollos de Caguas (2023). Criollos existed "
     "1976-2006 too; whether this is a revival of that franchise or a rename "
     "of Grises is unresolved — flagged."),
    ("merged", "1998", "capitalinos_san_juan", "cangrejeros_santurce", "single-source",
     "D2: Tiburones de Aguadilla + Capitalinos de San Juan -> Cangrejeros (1998)."),
    ("merged", "1998", "tiburones_aguadilla", "cangrejeros_santurce", "single-source",
     "D2: Tiburones de Aguadilla + Capitalinos de San Juan -> Cangrejeros (1998)."),
    ("name_toggle", "1989", "indios_mayaguez", "tainos_cabo_rojo", "single-source",
     "D2: Indios de Mayaguez <-> Tainos de Cabo Rojo 1989-1993; toggled twice."),
    ("hiatus_start", "2005", "piratas_quebradillas", "", "single-source",
     "D2: Piratas de Quebradillas hiatus 2005-2008."),
    ("hiatus_end", "2009", "piratas_quebradillas", "", "single-source",
     "D2: Piratas de Quebradillas returned 2009."),
    ("relationship_unclear", "", "santos_san_juan", "capitalinos_san_juan", "disputed",
     "D5-adjacent: 'Santos de San Juan' (scoring champ club 1972/75/76) and "
     "'Capitalinos de San Juan' may be the same club renamed, or two clubs. "
     "Also bears on the disputed 1945 champion. Not resolved."),
]

# normalized city -> (franchise_id, season_exceptions {season: note})
# season_exceptions flag a season where the city does NOT map cleanly.
CITY_MAP: dict[str, tuple[str, dict[str, str]]] = {
    "SAN GERMAN": ("atleticos_san_german", {}),
    "BAYAMON": ("vaqueros_bayamon", {}),
    "ARECIBO": ("capitanes_arecibo", {}),
    "SANTURCE": ("cangrejeros_santurce", {}),
    "RIO PIEDRAS": ("cardenales_rio_piedras", {}),
    "UPR": ("gallitos_upr", {}),
    "PONCE": ("leones_ponce", {}),
    "QUEBRADILLAS": ("piratas_quebradillas", {}),
    "CANOVANAS": ("indios_canovanas", {}),
    "ISABELA": ("gallitos_isabela", {}),
    "AIBONITO": ("polluelos_aibonito", {}),
    "MOROVIS": ("titanes_morovis", {}),
    "GUAYNABO": ("mets_guaynabo", {}),
    "CAROLINA": ("gigantes_carolina", {}),
    "CAGUAS": ("criollos_caguas", {}),
    "GUAYAMA": ("brujos_guayama", {}),
    "COAMO": ("maratonistas_coamo", {}),
    "MAYAGUEZ": ("indios_mayaguez", {}),
    "FAJARDO": ("cariduros_fajardo", {}),
    "AGUADA": ("santeros_aguada", {}),
    "VEGA BAJA": ("vega_baja", {}),
    "TORTUGUERO": ("cocoteros_tortuguero", {}),
    "SAN JUAN": ("capitalinos_san_juan", {
        # 1936 handled by OWNER_RESOLUTIONS (Club Nautico de San Juan).
        "1945": "D5: EN-wiki=Capitalinos, ES-wiki=Santos de San Juan; bsnpr city only",
    }),
    "HUMACAO": ("grises_humacao", {"*": "Humacao also had Caciques (~2012) — verify per season"}),
    "MANATI": ("osos_manati", {"*": "Manati: Atenienses 2014-17 then Osos 2022+ — verify per season"}),
}

# lideres200x 5-char codes + equiposstat 2-letter `t=` codes -> franchise_id
CLUB_CODES: dict[str, str] = {
    # lideres2000/2001/2002 5-char (uppercase, may carry a trailing space)
    "SANTU": "cangrejeros_santurce", "PONCE": "leones_ponce", "BAYAM": "vaqueros_bayamon",
    "SAN G": "atleticos_san_german", "MAYAG": "indios_mayaguez", "COAMO": "maratonistas_coamo",
    "MOROV": "titanes_morovis", "AIBON": "polluelos_aibonito", "CAGUA": "criollos_caguas",
    "CAROL": "gigantes_carolina", "ARECI": "capitanes_arecibo", "ISABE": "gallitos_isabela",
    "QUEBR": "piratas_quebradillas", "GUAYA": "brujos_guayama", "FAJAR": "cariduros_fajardo",
    "CAYEY": "toritos_cayey",
    # equiposstat 2-letter `t=` codes
    "SA": "cangrejeros_santurce", "PO": "leones_ponce", "BA": "vaqueros_bayamon",
    "AR": "capitanes_arecibo", "MA": "indios_mayaguez", "CO": "maratonistas_coamo",
    "MO": "titanes_morovis", "AI": "polluelos_aibonito", "CA": "criollos_caguas",
    "CN": "gigantes_carolina", "IS": "gallitos_isabela", "GU": "brujos_guayama",
    "CY": "toritos_cayey",
}
_CLUB_CODE_AMBIGUOUS = {"CA", "CO"}  # CA = Caguas or Carolina?; CO = Coamo — see note

# --------------------------------------------------------------------------- #
# owner resolutions — 2026-09-08. Recorded here so they are auditable.         #
# --------------------------------------------------------------------------- #
# (topic, season) -> resolution. "agree" resolutions carry a franchise_id and a
# note; "dual_metric" resolutions record BOTH scoring champions (D4 boundary).
OWNER_RESOLUTIONS: dict[tuple[str, str], dict] = {
    ("champion", "1936"): {
        "kind": "agree", "franchise_id": "club_nautico_san_juan",
        "confidence": "single-source",
        "note": "OWNER 2026-09-08: city-vs-club naming, not a disagreement — "
                "seed 'Club Nautico de San Juan' == bsnpr city 'SAN JUAN'. "
                "bsnpr campeonatos.asp captures themselves varied over time "
                "(SAN JUAN / VEGA BAJA); the seed's specific club is used."},
    ("runner_up", "1968"): {
        "kind": "agree", "franchise_id": "cardenales_rio_piedras",
        "confidence": "single-source",
        "note": "OWNER 2026-09-08: not a genuine disagreement — resolved to the "
                "seed's Cardenales de Rio Piedras. bsnpr campeonatos.asp captures "
                "disagreed internally over time (RIO PIEDRAS in some, PONCE in "
                "others); the RIO PIEDRAS captures concur with the seed."},
    # 1971 / 1974: the two sources name different scoring champions because they
    # rank by different metrics across the D4 boundary. Record BOTH, labelled.
    ("scoring_champion", "1971"): {"kind": "dual_metric"},
    ("scoring_champion", "1974"): {"kind": "dual_metric"},
    # 1945: genuine, unresolved. No OWNER_RESOLUTIONS action — stays a conflict.
}

NAME_TO_ID = {v[0]: k for k, v in FRANCHISES.items()}
NAME_TO_ID_NORM = {ncity(v[0]): k for k, v in FRANCHISES.items()}


def _read(name: str) -> list[dict]:
    with (CLEAN / name).open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def resolve_city(city: str, season: str) -> tuple[str, str, str]:
    """(franchise_id, dispute_note, unmapped_note).

    `dispute_note` — a known source disagreement for this (city, season); it
    makes the row a flagged conflict. `unmapped_note` — we simply can't map
    this token; the row is not a conflict, just incomplete.
    """
    key = ncity(city).replace("FCLA MARTIN", "FCLA_MARTIN")
    if not key:
        return "", "", ""
    if key == "FCLA_MARTIN":
        return "", "", "unmapped club 'Fcla. Martin' (1930s runner-up)"
    if key not in CITY_MAP:
        return "", "", f"no city->franchise mapping for {city!r}"
    fid, exceptions = CITY_MAP[key]
    return fid, exceptions.get(season, ""), exceptions.get("*", "")


def resolve_seed_name(name: str) -> str:
    if not name:
        return ""
    return NAME_TO_ID.get(name) or NAME_TO_ID_NORM.get(ncity(name), "")


# --------------------------------------------------------------------------- #
def write_franchise_layer() -> None:
    _write_csv(CLEAN / "franchises.csv", [
        {"franchise_id": k, "canonical_name": v[0], "city": v[1],
         "founded": v[2], "status": v[3],
         "source": "seed:bsn_franchises.csv" if k in NAME_TO_ID and v[3] != "active"
                   or k in NAME_TO_ID else "derived:champion/scoring rows"}
        for k, v in FRANCHISES.items()
    ], ["franchise_id", "canonical_name", "city", "founded", "status", "source"])

    _write_csv(CLEAN / "franchise_events.csv", [
        {"event_type": e[0], "season": e[1], "from_franchise_id": e[2],
         "to_franchise_id": e[3], "confidence": e[4], "note": e[5],
         "source": "docs/project.md D2/D5"}
        for e in FRANCHISE_EVENTS
    ], ["event_type", "season", "from_franchise_id", "to_franchise_id",
        "confidence", "note", "source"])

    rows = []
    for city, (fid, exc) in sorted(CITY_MAP.items()):
        rows.append({"normalized_city": city, "franchise_id": fid,
                     "season_flags": " | ".join(f"{k}: {v}" for k, v in exc.items())})
    _write_csv(CLEAN / "city_franchise_map.csv", rows,
               ["normalized_city", "franchise_id", "season_flags"])

    _write_csv(CLEAN / "club_code_map.csv", [
        {"code": code, "franchise_id": fid,
         "scheme": "equiposstat_t" if len(code) <= 2 else "lideres200x_5char",
         "flag": "ambiguous — verify" if code in _CLUB_CODE_AMBIGUOUS else ""}
        for code, fid in sorted(CLUB_CODES.items())
    ], ["code", "franchise_id", "scheme", "flag"])


# --------------------------------------------------------------------------- #
def reconcile_champions(conflicts: list[dict]) -> None:
    seed = {r["season"]: r for r in _read("bsn_champions_by_season.csv")}
    bsnpr = {r["season"]: r for r in _read("champions_from_bsnpr.csv")}
    all_seasons = sorted(set(seed) | set(bsnpr),
                         key=lambda s: (int(s[:4]), s))

    out = []
    for s in all_seasons:
        sd, bp = seed.get(s), bsnpr.get(s)
        row = {"season": s, "agreement": "", "champion_franchise_id": "",
               "runner_up_franchise_id": "", "seed_champion": "",
               "seed_runner_up": "", "bsnpr_champion_city": "",
               "bsnpr_runner_up_city": "", "coach": "", "note": "",
               "confidence": "", "sources": ""}

        if bp and bp["no_champion"] == "True":
            row.update(agreement="no_champion", note=bp["note"],
                       confidence="single-source", sources=BSNPR_SRC,
                       seed_champion=sd["champion"] if sd else "")
            if sd and not sd["champion"]:
                row["sources"] = f"{SEED_SRC}; {BSNPR_SRC}"
            out.append(row)
            continue

        seed_champ_id = resolve_seed_name(sd["champion"]) if sd else ""
        bp_champ_id, champ_disp, champ_unmapped = resolve_city(bp["champion_city"], s) if bp else ("", "", "")
        seed_ru_id = resolve_seed_name(sd["runner_up"]) if sd else ""
        bp_ru_id, ru_disp, ru_unmapped = resolve_city(bp["runner_up_city"], s) if bp else ("", "", "")

        row["seed_champion"] = sd["champion"] if sd else ""
        row["seed_runner_up"] = sd["runner_up"] if sd else ""
        row["bsnpr_champion_city"] = bp["champion_city"] if bp else ""
        row["bsnpr_runner_up_city"] = bp["runner_up_city"] if bp else ""
        row["coach"] = (bp["coach"] + (f"  [{bp['coach_flag']}]" if bp and bp["coach_flag"] else "")) if bp else ""

        srcs = []
        if sd:
            srcs.append(SEED_SRC)
        if bp:
            srcs.append(BSNPR_SRC)
        row["sources"] = "; ".join(srcs)

        unmapped = "; ".join(x for x in (
            f"champion city {champ_unmapped}" if champ_unmapped else "",
            f"runner-up city {ru_unmapped}" if ru_unmapped else "") if x)

        # owner resolutions (2026-09-08) — supersede the auto-detected conflict
        champ_res = OWNER_RESOLUTIONS.get(("champion", s))
        ru_res = OWNER_RESOLUTIONS.get(("runner_up", s))

        if sd and bp:
            champ_conflict = (seed_champ_id and bp_champ_id and seed_champ_id != bp_champ_id
                              and not champ_res)
            ru_conflict = (seed_ru_id and bp_ru_id and seed_ru_id != bp_ru_id
                           and not ru_res)
            champ_disp = "" if champ_res else champ_disp
            ru_disp = "" if ru_res else ru_disp
            res_notes = [r["note"] for r in (champ_res, ru_res) if r and r.get("note")]

            if champ_conflict or ru_conflict or champ_disp or ru_disp:
                row["agreement"] = "conflict"
                row["confidence"] = "disputed"
                notes = [unmapped] if unmapped else []
                if champ_disp:
                    notes.append(f"champion: {champ_disp}")
                if ru_disp:
                    notes.append(f"runner-up: {ru_disp}")
                if champ_conflict:
                    notes.append(f"champion: seed={sd['champion']} vs bsnpr city={bp['champion_city']}")
                    conflicts.append({
                        "topic": "champion", "season": s,
                        "source_a": SEED_SRC, "value_a": sd["champion"],
                        "source_b": BSNPR_SRC, "value_b": f"{bp['champion_city']} (city)",
                        "agree_on": "", "note": "seed uses franchise name, bsnpr uses city — mapped values differ"})
                if ru_conflict:
                    notes.append(f"runner-up: seed={sd['runner_up']} vs bsnpr city={bp['runner_up_city']}")
                    conflicts.append({
                        "topic": "runner_up", "season": s,
                        "source_a": SEED_SRC, "value_a": sd["runner_up"],
                        "source_b": BSNPR_SRC, "value_b": f"{bp['runner_up_city']} (city)",
                        "agree_on": "", "note": "mapped values differ"})
                if champ_disp and "D5" in champ_disp:
                    conflicts.append({
                        "topic": "champion", "season": s, "source_a": "en.wikipedia",
                        "value_a": "Capitalinos de San Juan", "source_b": "es.wikipedia",
                        "value_b": "Santos de San Juan", "agree_on": "runner-up: Gallitos de la UPR",
                        "note": "D5 unresolved. bsnpr adds coach Adolfo Porrata, city 'SAN JUAN' — does not disambiguate."})
                # a conflict on one of the two slots does not taint the other —
                # keep the resolved id for whichever slot the sources concur on
                if not (champ_conflict or champ_disp):
                    row["champion_franchise_id"] = seed_champ_id or bp_champ_id
                if not (ru_conflict or ru_disp):
                    row["runner_up_franchise_id"] = seed_ru_id or bp_ru_id
                row["note"] = "; ".join(n for n in notes if n)
            else:
                row["agreement"] = "agree"
                row["champion_franchise_id"] = (
                    champ_res["franchise_id"] if champ_res else seed_champ_id or bp_champ_id)
                row["runner_up_franchise_id"] = (
                    ru_res["franchise_id"] if ru_res else seed_ru_id or bp_ru_id)
                # verified only when two independent sources genuinely concur;
                # an owner resolution carries its own confidence
                confs = [r["confidence"] for r in (champ_res, ru_res) if r]
                row["confidence"] = min(confs, key=lambda c: ["single-source", "verified"].index(c)) if confs else "verified"
                row["note"] = "; ".join(n for n in ([unmapped] + res_notes) if n)
        elif sd:
            row["agreement"] = "seed_only"
            row["champion_franchise_id"] = seed_champ_id
            row["runner_up_franchise_id"] = seed_ru_id
            row["confidence"] = sd["confidence"] or "single-source"
            if s == "2024":
                row["note"] = sd["notes"]
            if s > "2020":
                row["note"] = (row["note"] + "; " if row["note"] else "") + "bsnpr campeonatos.asp ends at 2020"
        elif bp:
            row["agreement"] = "bsnpr_only"
            row["champion_franchise_id"] = bp_champ_id
            row["runner_up_franchise_id"] = bp_ru_id
            row["confidence"] = "single-source"
            if s == "1942-1943":
                row["note"] = "D3: split-season key — the seed folds this into 1942"
        out.append(row)

    _write_csv(CLEAN / "champions_reconciled.csv", out, [
        "season", "agreement", "champion_franchise_id", "runner_up_franchise_id",
        "seed_champion", "seed_runner_up", "bsnpr_champion_city",
        "bsnpr_runner_up_city", "coach", "note", "confidence", "sources"])
    agg = {}
    for r in out:
        agg[r["agreement"]] = agg.get(r["agreement"], 0) + 1
    print(f"[champions] {len(out)} seasons: {agg}")


# --------------------------------------------------------------------------- #
def reconcile_scoring(conflicts: list[dict]) -> None:
    seed = {r["season"]: r for r in _read("bsn_scoring_champions.csv")}
    hist = {r["season"]: r for r in _read("historic_scoring_champions.csv")}
    lead: dict[str, dict] = {}
    for r in _read("player_season_leaders.csv"):
        if r["category"] == "anotaciones" and r["rank"] == "1":
            lead[r["season"]] = r

    def lastname(n: str) -> str:
        n = strip_accents(n).lower()
        return re.split(r"[ ,]", n.strip())[0] if "," in n else n.split()[-1] if n else ""

    seasons = sorted(set(seed) | set(hist) | set(lead), key=int)
    out = []
    for s in seasons:
        sd, h, ld = seed.get(s), hist.get(s), lead.get(s)
        metric_era = "total_points" if int(s) <= 1970 else "ppg"
        row = {"season": s, "metric_era": metric_era, "agreement": "",
               "seed_player": sd["player"] if sd else "",
               "seed_value": sd["value"] if sd else "",
               "historic_player": h["player_raw"] if h else "",
               "historic_total": h["total_points"] if h else "",
               "historic_ppg": h["ppg"] if h else "",
               "leaders_player": ld["player_raw"] if ld else "",
               "leaders_ppg": ld["prom"] if ld else "",
               "note": "", "confidence": "", "sources": ""}
        names = {"seed": sd["player"] if sd else "",
                 "historic": h["player_raw"] if h else "",
                 "leaders": ld["player_raw"] if ld else ""}
        present = {k: v for k, v in names.items() if v}
        lastnames = {lastname(v) for v in present.values()}
        row["sources"] = "; ".join(sorted(present))

        res = OWNER_RESOLUTIONS.get(("scoring_champion", s))
        if res and res["kind"] == "dual_metric":
            # OWNER 2026-09-08: not a conflict — the two sources rank by different
            # metrics across the D4 boundary. Record both, each labelled.
            row["agreement"] = "dual_metric_d4"
            row["confidence"] = "verified"
            row["ppg_champion"] = sd["player"] if sd else ""
            row["ppg_value"] = sd["value"] if sd else ""
            row["total_points_champion"] = h["player_raw"] if h else ""
            row["total_points_value"] = h["total_points"] if h else ""
            row["note"] = ("OWNER 2026-09-08: D4 metric boundary — the seed's "
                           f"{row['ppg_champion']} led points-per-game, the bsnpr "
                           f"historic ledger's {row['total_points_champion']} led "
                           "total points. Both are recorded; neither is 'the' champion.")
        elif len(present) < 2:
            row["agreement"] = f"{next(iter(present))}_only" if present else "none"
            row["confidence"] = "single-source"
        elif len(lastnames) == 1:
            row["agreement"] = "agree"
            row["confidence"] = "verified"
        else:
            row["agreement"] = "conflict"
            row["confidence"] = "disputed"
            row["note"] = "; ".join(f"{k}={v}" for k, v in present.items())
            pairs = sorted(present.items())
            conflicts.append({
                "topic": "scoring_champion", "season": s,
                "source_a": pairs[0][0], "value_a": pairs[0][1],
                "source_b": pairs[1][0], "value_b": pairs[1][1],
                "agree_on": "", "note": (
                    f"{metric_era} era. " + ("bsnpr's 'campeón anotador' may use total "
                    "points where the seed uses ppg." if metric_era == "ppg" else ""))})
        out.append(row)

    _write_csv(CLEAN / "scoring_champions_reconciled.csv", out, [
        "season", "metric_era", "agreement", "seed_player", "seed_value",
        "historic_player", "historic_total", "historic_ppg", "leaders_player",
        "leaders_ppg", "ppg_champion", "ppg_value", "total_points_champion",
        "total_points_value", "note", "confidence", "sources"])
    agg = {}
    for r in out:
        agg[r["agreement"]] = agg.get(r["agreement"], 0) + 1
    print(f"[scoring] {len(out)} seasons: {agg}")


# --------------------------------------------------------------------------- #
def main() -> int:
    for f in ("bsn_champions_by_season.csv", "champions_from_bsnpr.csv",
              "historic_scoring_champions.csv"):
        if not (CLEAN / f).exists():
            print(f"! {f} missing — run earlier phases first", file=sys.stderr)
            return 1

    write_franchise_layer()
    conflicts: list[dict] = []
    reconcile_champions(conflicts)
    reconcile_scoring(conflicts)

    conflicts.sort(key=lambda c: (c["topic"], c["season"]))
    _write_csv(CLEAN / "reconcile_conflicts.csv", conflicts, [
        "topic", "season", "source_a", "value_a", "source_b", "value_b",
        "agree_on", "note"])
    print(f"\n[reconcile_conflicts] {len(conflicts)} flagged conflicts — NO winner picked.")
    for c in conflicts:
        print(f"  {c['topic']:16} {c['season']:9} {c['value_a']}   vs  {c['value_b']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
