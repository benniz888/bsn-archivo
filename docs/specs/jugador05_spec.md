# Spec: PHASE_3H follow-up — jugador05.asp (the 2005-06 scouting bios)

## [PURPOSE]

`jugador05.asp` is the 2005–2006 sibling of `jug05.asp`, same
`r=xxx&r2=<token>&e=<city>` scheme, no `?id=N`. It is a **scouting bio**, not
a stat page:

```
<TEAM> [<jersey>] - <Apellido> , <Nombre>
Origen: <birthplace>   Edad: <age>   Fecha: <M/D/YYYY>
Altura: <h>   Peso: <w>   Posición: <pos>
Notas Sobresalientes: <scouting prose — college / pro / overseas / style>
```

No career-by-season table. So — unlike `jug05.asp` — it does **not** feed
`build_id_map`'s season-corroboration test and is not an identity-spine lever.
Its yield is biographical: empty-field fills on existing canonical rows plus a
body of Spanish scouting prose nothing else in the archive has.

## [DECISION]

Owner-approved 2026-09-09. "Defer 4 and 5, wire in the data-only pipeline."

1. **Fetch** — `src/fetch_jugador05.py` (`make fetch-jugador05`), a straight
   clone of `fetch_jug05.py`: dedup by CDX digest, latest capture per digest,
   gated per-year tranches (2005: 448, 2006: 152 — both < `MAX_TRANCHE`, ungated,
   no `--force`). PC6 single stream, `polite_get` spacing, raw immutable (PC5).
   600 distinct digests → `data/raw/players/jugador05/`,
   `data/interim/fetch_manifest_jugador05.csv` committed as provenance.

2. **Parse — enrich-only, never mint (D1).** `parse_jugador05()` +
   `merge_jugador05()` in `parse_players.py`, `source_id =
   wayback_bsnpr_jugador05`. Flat-text regex (`_J05_BLOCK`) after BeautifulSoup
   `get_text` (which drops the HTML comment the old `-->` anchor relied on);
   anchor on the standalone "Jugador" heading label + the fixed label sequence,
   every value optional. Dedup a player's several roster pages on
   `(norm_key(name), birth_date)`.

3. **Match tiers** — `jug05_xwalk.csv` as tier 0 (same 2005-06 roster, so the
   same nickname bridges apply; keyed name+DOB, then name alone when a surname
   maps to exactly one id), then exact full name (accepted when the canonical
   row has no birth year to corroborate — that is the case we most want to
   fill), then apellidos token-prefix + given[0] with DOB ±7d **or** matching
   birth year. On a match: fill only *empty* `birth_date`/`birth_year`,
   `birth_city`, `nationality`, `position` — never overwrite. No match → review.

4. **Outputs**
   - `data/clean/player_bios.csv` — `bsnpr_id, notes_es, birthplace,
     roster_team, roster_year, jersey, source_id, source_url, retrieved_at`,
     one row per matched id. Keeps `players_canonical` schema stable.
   - `data/interim/jugador05_review.csv` — the no-match rows (2005-06 imports
     with no encyclopedia entry; can't mint — no career table).
   - `data/interim/jugador05_dob_conflicts.csv` — matched rows where canonical
     and jugador05 give different birth dates. **Deferred worklist** (owner
     decision 4): not fixed in this phase.
   - `build_web_data` folds a `bio` block into `web/data/players/<id>.json`;
     a bio with prose no longer counts a player as "thin / no ficha".

## [ALTERNATIVES_REJECTED]

- **Minting the 26 no-match rows.** No career table → D1 forbids it. They stay
  in review; a curated `jugador05_xwalk.csv` (Facey→2233, Hourruitiner
  Rolando→2090, Wharton→1357, Venzen→808 …) is a possible follow-up.
- **Auto-correcting the 11 DOB conflicts** from jugador05 (all are M/D
  transpositions the `jug05_xwalk.csv` notes already suspect). Owner deferred
  (decision 4) — enrich-only never overwrites.
- **A player-card "Reseña (2005–06)" surface.** Owner deferred (decision 5);
  the data ships in `web/data`, the app change is a separate follow-up.

## [RESULT] (2026-09-10)

600 pages → **155 distinct players** (128 w/ DOB, 99 w/ prose). `merge_jugador05`
runs a hand-curated tier 0 (`jug05_xwalk.csv` for the shared roster +
`jugador05_xwalk.csv` for this source's own 26 review rows — 23 bridged, 3 left)
then the auto match:

| outcome | first pass | + jugador05_xwalk |
|---|--:|--:|
| matched to canonical | 129 | **152** |
| — empty spine fields filled | 112 | **159** (birth-year coverage 2,007 → **2,019**) |
| — `player_bios.csv` rows | 129 | **152** (98 w/ prose) |
| DOB disagreements (flagged, deferred) | 11 | **15** |
| to review (no match, can't mint) | 26 | **3** — Kevin/Kelvin Bonilla, "Tito" López, the 1967-dated Fernando Ortiz page (all deliberate) |

Net on the spine: `players_canonical` unchanged at **3,345**; `player_id_map`
and the review queue **unchanged** (666 / 585 — jugador05 is not an id-map
lever). Deterministic through parse + build (`manifest.json` md5
`01ecca8432450acd86d0313879212f01`).

The nickname bridges also surfaced two jug05-minted rows that are duplicates of
real canonical ids the encyclopedia carries under a different given name:
`990004` "Liriano, Aneury" = id 93, `990030` "Ortiz, Irving" = id 2261. Merging
those renumbers the minted range, so it is a `jug05_xwalk.csv` follow-up, not
this phase.

## [OPEN_QUESTIONS]

1. **Deferred (owner decision 4):** `jugador05_dob_conflicts.csv` — now **15**
   canonical birth dates jugador05 (+ jug05) contradict, all month/day
   transpositions except `417` Daniel Guzmán (canonical `2/20/1948` is a plain
   error). A future pass could correct `players_canonical` from the two
   2005-era sources agreeing.
2. **Deferred (owner decision 5):** surface `bio.notes_es` on the player card.
3. **RESOLVED:** `jugador05_xwalk.csv` worked the 26 review rows — 23 bridged
   (13 high, 10 medium), 3 left in review by design.
4. `jug05_xwalk.csv` follow-up: `990004`/`990030` are minted duplicates of ids
   93 / 2261 (found via the jugador05 bridges). Merging renumbers the minted
   range.
