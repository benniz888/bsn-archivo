# Spec: App Data Map + web/data JSON Schema (PHASE_5, sub-phase 5A)

Companion to [`app_data_sync_spec.md`](app_data_sync_spec.md) (the decision) and
[`clean_data_storage_spec.md`](clean_data_storage_spec.md) (gzip). This is the
contract 5B–5G build against.

> **REWRITTEN 2026-09-09.** 5A–5D were first done against a **stale 2,214-line
> `app/bsn_archivo.html`**. The real file is **6,286 lines / 519 KB**, ~90 data
> blocks, **48 `build*()` functions**, a 55-builder batched-RAF boot behind a
> splash screen, a `PROFILE` system, and deep-link routing. This rewrite is
> against the real file. What survived the mistake, and what didn't, is in
> [DECISION → Salvage].

## [PURPOSE]

Decide, per embedded block: **regenerate from CSV | merge CSV over curated |
leave hand-maintained**, then fix the `web/data/` JSON the app fetches.

### The finding, inverted

The stale file was a simple artifact where only ~4 blocks had a CSV source. The
**real app is a polished, gap-honest Spanish-first product** — and the
`data/clean/` pipeline (PHASE_3C/3D/3E) has already produced most of the data
the app documents as *missing*. `buildSources()` states, in the app UI:

| App says (in `buildSources` / `buildCoverage`) | Pipeline actually has |
|---|---|
| "No existe ninguna base pública de estadísticas por temporada del BSN anterior a 2011" | `historic_scoring_champions.csv` 1948–2004, `player_season_stats_2001_2004.csv`, `player_season_leaders_2000_2002.csv` |
| "No hay boxscores. Ninguno, de ninguna temporada." | `game_box_player.csv` — **39,669 rows / 1,292 games** (2001–03, 2008–13) |
| "Posiciones completas solo de 2009, 2025 y 2026" | 5C derives standings for **2001–03 + 2008–13** from `game_results.csv` |
| "MVP por año: 39 temporadas recuperadas" | `historic_awards.csv` MVP = **47 rows, 1958–2004** (+ ROY, DPOY) |
| "Campeones de anotación 1956–65 y 1992–presente: … no se bajó" | `scoring_champions_reconciled.csv` — **1948–2021** |

**So PHASE_5 has two tracks:**
1. **Sync** the handful of blocks that mirror a CSV (`F.won/ru`, `champOf/ruOf`,
   `SCORING`, arguably `MVP_YEARS`).
2. **Feed the app's existing features** with the pipeline data that closes its
   stated gaps — the player index, the season table, the `DATASETS` query
   builder, `buildSources`/`buildCoverage`, standings. This is where the value
   is, and it needs per-feature design, not a mechanical block swap.

### The app's own merge architecture (this is what `hydrate()` plugs into)

The owner already keeps **provenance-tagged source blocks separate and
merges/derives at parse time** — a run of IIFEs around lines 1810–2470:
- `translate()` (line ~1810) overwrites English display strings with Spanish
  **keyed by name, in place** — explicitly *"rather than editing the source
  tables, which would break their traceability to the research pass."*
- `POOL` is assembled from `POOL` + `POOL_2026` + `POOL_PATCH` + `PLAYERS_NEW`
  + `POOL_RGM` (cites `bsn_player_seasons_realgm.csv`, a RealGM file **not in
  this repo** — L1) + auto-generated coach entries from `F`.
- a "legend criterion" IIFE recomputes the `legend` tag from `LEADERS` /
  `MVP_REPEAT` / `RECORDS` / `STONE`.
- `PINDEX` (the player index) is lazily cross-referenced from **8 curated
  blocks** in `buildPlayerIndex()`.

`hydrate()` from `web/data` is **one more merge step** in this pattern: async,
layered on top, never editing a source block. That is the D-043 rule generalised.

## [DECISION]

### Salvage — what the stale-file mistake cost

| Work | Commit | Status against the real file |
|---|---|---|
| **D-042** parse_players name fix | `a22027c` | ✅ untouched — pure pipeline, no app dependency |
| **5B** `src/build_web_data.py` + `web/data/index/*.json` | `4634dad` | ✅ reads `data/clean/` only. Needs: (a) `cac` row in the crosswalk, (b) `caciques_humacao` added to the pipeline, (c) re-verify `diff_app_champions()` against the real `F` (regex `\n  ([a-z]{3}):\{` still matches — confirmed) |
| **5B** `app/franchise_curated.json` | `4634dad` | ✅ **0 field diffs** vs the real `F` on the 32 shared keys — only missing `cac` |
| **5B** `app/franchise_key_map.csv` | `4634dad` | ⚠️ 32 rows; real `F` has **33** (adds `cac`) |
| **5C** `web/data/{players,seasons,games}/**` | `8891d78` | ✅ pure pipeline — fully valid |
| **5D** `hydrate()` / `DATA` / `deriveChampions()` | *(uncommitted)* | ❌ **lost** — overwritten with the real file. Full redo against the boot architecture (see [5D, revised]) |

### The franchise-key crosswalk (revised)

Real `F` = **33 keys**. `franchises.csv` = 33 `franchise_id` — but **not a
match**: the app has `cac` (Caciques de Humacao, 2009–2018, `active:0,end:2018`),
which has **no `franchise_id`**; the pipeline has `santos_san_juan`, which has
no app key (D5, folded into `cap`).

**RESOLVED — owner 2026-09-09, done in 5B-FIX.** Wikipedia (Caciques de
Humacao, Grises de Humacao): **two distinct franchises**, matching how `F`
already splits `cac` and `hum`:
- **`caciques_humacao`** — one continuous franchise: Toritos de Cayey
  (2002–04) → Grises de Humacao (2005) → **renamed** Caciques de Humacao
  (2010) → relocated away (Isabela, Guayama, ~2019). NEW `franchise_id`.
  `city_franchise_map` HUMACAO → here (the archived Humacao games are all
  2008–2013, inside this era). App key `cac`.
- **`grises_humacao`** — a **separate 2021 expansion** (Wikipedia: "a new
  franchise"), 2021–2023 → **Criollos de Caguas from 2024**. `franchises.csv`
  founded corrected 2005 → 2021. App key `hum`. Never appears in the archived
  game window.

5B-FIX shipped: `franchises.csv` (+`caciques_humacao`, `grises_humacao` refounded
2021), `city_franchise_map` (HUMACAO → `caciques_humacao`), `franchise_events`
(+`toritos_cayey`→`caciques_humacao` 2005; the Grises→Criollos row upgraded to
`verified` 2024), `franchise_key_map.csv` + `franchise_curated.json` (33 keys).
`verify_web_data` / tests bumped 32 → 33. See `reconcile_spec.md`
[OWNER_RESOLUTIONS].

### Per-block classification (real file)

**A — regenerate / sync from a CSV**

| block (line) | shape | consumers | CSV | action |
|---|---|---|---|---|
| `F` `.won`/`.ru` (1076) | year arrays per franchise | `buildRibbon showSeason buildTitleStats buildTitleBars buildDynasties buildMatrix buildSeasonTable buildTiles showTeam buildClubCard drawFinal buildQB buildHub buildPlayerIndex` | `champions_reconciled.csv` | **hydrate — UNION** (D-043: keeps 1945/D5 + 1942-43/D3 that the CSV omits; 0 conflicts confirmed at build time) |
| `champOf` / `ruOf` (2257) | derived `{year:key}` | as above | derived from `F` | wrap in `deriveChampions()`, re-run after hydrate |
| `FKEYS` / `ACTIVE` (2264) | `Object.keys(F)` / active filter — **frozen at parse** | most `build*` | derived | recompute after hydrate (`FKEYS` stable; `ACTIVE` can drift if a `status` flips) |
| `SCORING` (1205) | `[[yr,player,club,metric,val]]` 1966–1991 (26) | `buildScoringChart buildScoringTable buildPlayerIndex buildQB` | `scoring_champions_reconciled.csv` (1948–2021) | **hydrate — replace** in place (26 → ~68 rows). Needs `club_raw` added to `scoring_titles.json` |
| `F` factual (name/city/founded/status/end) | | `showTeam` `buildTiles` `buildQB` … | `franchises.csv` | hydrate — replace factual, **keep curated** (colours/coach/abbr/note) |

**A? — overlaps a CSV, owner call (5D.2 / later)**

| `MVP_YEARS` (2065) | `[[yr,player,club]]` 1951–2018 (41) | `buildMVPYears buildPlayerIndex buildQB DATASETS.mvp` | `historic_awards.csv` MVP rows 1958–2004 (47) | the app calls these "39 recuperados"; the CSV has more + provenance. **Merge candidate** — but the app's are hand-verified with per-year clubs; needs care. |
| `LEADERS` (1166) | career points/rebounds/assists top-10 (30) | `buildLeaders buildPlayerIndex buildQB` | `bsn_career_leaders.csv` (same 30-row seed) | low value to sync (identical); a D7 "floor, ~5 yr stale" banner is the only real add |
| `RECORDS` (1234) | `[[rec,mark,who,yr,ctx]]` (11) | `buildRecords buildPlayerIndex buildQB` | `bsn_records.csv` (same seed) | low value |

**B — NEW capability: feed an existing feature with CSV-only data (the real work)**

| feature | app today | pipeline data | 5C-onwards |
|---|---|---|---|
| **Player index** (`buildPlayerIndex` / `PINDEX` / `showPlayer`, tab `jugadores`) | ~few-hundred players cross-ref'd from 8 curated blocks; `showPlayer` prints a big honest "lo que este archivo NO sabe" gap message | `players_canonical.csv` 3,303 + `player_career_seasons` + `player_id_map` + **`web/data/players/<id>.json` (5C, 1,076 files)** + box-score aggregates | add a "índice completo (3,303)" mode fed by `index/players.json`; `showPlayer` fetches `players/<id>.json` for career lines + box totals → shrinks the gap message |
| **Season table / `showSeason`** (tab `historia`) | champion + runner-up + `NOTES[y]` only | **`web/data/seasons/<year>.json` (5C, 98 files)** — scoring champ, DPOY/ROY/MVP, derived standings, per-season leaders, coverage.gaps | `showSeason` fetches the season file → shows leaders / awards / standings inline where they exist |
| **`DATASETS` query builder** (`buildQB`, tab `consulta`) | 14 datasets, all `rows:()=>[...from const blocks...]` | box scores, historic leaders, standings, awards | add `rows` sources: `boxscores`, `lideres_historicos` (1948–2004), `posiciones_historicas` (2001–13), `premios_historicos` — from `web/data` |
| **`buildSources` / `buildCoverage`** (tab `fuentes`) | hard-coded gap list + `COVERAGE` %s that are **now partly wrong** | the pipeline manifests | rewrite the gap text; recompute `COVERAGE` bars from what's actually loaded |
| **`STANDINGS`** (1509, only 2009) | one hand-entered season | 5C derived standings 2001–13 | `buildClubCard` / a standings view reads `seasons/<year>.json.standings` |

**C — curated editorial, no CSV, stays inline**

`ARENAS COACHES NBA_PLAYERS HOF STONE RETIRED REF_RULES REF_TIMELINE REF_SCORERS
CALENDAR CAL_MILESTONES CAL_SHAPE NEXT_SEASON ON_THIS_DAY FINALS_2025 FINALS_2026
FINALS_BY_YEAR SEMIS_2026 LEAD2026 AWARDS_2026 FIVE_2026 CLINCHERS CHANNELS POOL
POOL_2026 POOL_PATCH POOL_RGM PLAYERS_NEW BIO BIO_ALIAS OWNERS NEWS SEASON_STATE
VENUES STAND2026 GAMES GLOSARIO COVERAGE LEGEND_NOTE HUB CATS NOTES TABS MVP_REPEAT
SEASON_AWARDS` — editorial prose, mini-games, 2026-season specifics, the
`translate()` Spanish layer, user-facing copy. **The build script must never
touch these** (PC1). `MVP_YEARS`/`SEASON_AWARDS`/`RECENT`-style blocks that
happen to overlap a CSV stay curated unless explicitly merged in 5D.2+.

## [INTERFACES]

### `web/data/` tree — 5B + 5C, already built, unchanged by this rewrite

```
web/data/
  manifest.json                       # { schema_version, source_digest, counts }
  index/{franchises,seasons,players,scoring_titles,career_leaders,records}.json
  players/<bsnpr_id>.json              # 1,076
  seasons/<year>.json                 # 98
  games/<season>/index.json + <game_id>.json   # 1,292 + 9
```
Record shapes: see git `4634dad` / `8891d78`. **Additions this rewrite implies:**
- `scoring_titles.json` — add `club_raw` (from `historic_scoring_champions.team_raw` / seed).
- `index/franchises.json` — 33rd entry once `caciques_humacao` exists.
- possibly `index/awards.json` (MVP/ROY/DPOY 1958–2004 from `historic_awards.csv`) for the `DATASETS` builder — 5D.2.

### App integration contract (revised for the real file)

- **`DATA` object** — a fetch/cache helper matching the real `ST` wrapper
  (`ST.json(k)` takes one arg; `ST.set`; `ST.wrote`). `base = location.protocol
  === 'file:' ? null : new URL('data/', location.href).href`. Cache memory →
  `localStorage` (`bsn:data:*`) → network. `syncVersion()` re-fetches
  `manifest.json` each load, purges `bsn:data:*` on a `source_digest` change.
- **Hydration point:** `runBoot()` (line 6284) becomes `async` — `await
  hydrate()` (with a timeout race, ~2 s, so a slow network can't stall boot; the
  splash screen already covers the wait), then the RAF batch loop. `hydrate()`
  returns early on any fetch miss → every embedded block stands (this is the
  `file://` and offline path).
- **`hydrate()` merges, never replaces a source block** — same rule as
  `translate()`. `F.won/ru` union; `SCORING` rebuilt in place; `deriveChampions()`
  + `FKEYS`/`ACTIVE` recompute.
- **Per-feature fetches** (5C-consumers) are lazy: `showPlayer(name)` /
  `showSeason(y)` call `DATA.get('players/<id>.json')` on demand, render the
  extra rows if present, keep the gap message if not (PC2 — never a silent zero).
- **Deep links** already exist (`#jugador/georgie-torres` via `slug`); a fetched
  player file must key by the same `slug(canonical_name)`.
- **Naming:** `snake_case` files (C1). No wall-clock in any output (D-041).

## [RATIONALE]

- **The app's merge architecture makes hydrate low-risk.** The owner already
  layers `translate()`, `POOL_PATCH`, `POOL_RGM` etc. over source blocks at
  parse time without editing them. `hydrate()` is the same move, async.
- **Union not replace (D-043) is the house style.** `translate()`'s comment
  spells out why: editing a source table breaks its traceability to the
  research pass. Championship data: the app deliberately carries 1945 (D5) and
  1942-43 (D3) that the reconciled CSV omits; a union keeps them, and the
  build-time diff already confirms 0 *conflicts*.
- **The gap-closing track is the point, and it's per-feature.** Mechanically
  swapping `SCORING` is easy and low-value. Wiring `web/data/seasons/*.json`
  into `showSeason`, or the 3,303-player index into `buildPlayerIndex`, changes
  what the app *is* — and each needs a UI decision (how much thin data to show,
  how to phrase "parcial"). These are their own sub-phases, not one commit.
- **`buildSources` is now lying and must be fixed early.** An archive whose
  "what's missing" page is wrong is worse than one with no such page (PC4).

## [ALTERNATIVES_REJECTED]

- **Regenerate `MVP_YEARS` / `SEASON_AWARDS` / `RECENT` / `FINALS_BY_YEAR` from
  CSVs.** Rejected for now — hand-verified, per-year club attributions, editorial
  phrasing the CSV can't produce. Merge only `MVP_YEARS` ↔ `historic_awards`,
  and only in a dedicated 5D.2 with the diff shown.
- **Replace the curated `POOL` / `PLAYERS_NEW` with `players_canonical`.**
  Rejected — `POOL` is the Juega game corpus (verified, provenance-per-block);
  the 3,303-player set is thin pre-2011 and would wreck the games. The full set
  is a *new* player-index mode, not a `POOL` swap. (PHASE_4B_GAME_POOL owns any
  `POOL` change.)
- **One `bootstrap.json` codegen'd into the file.** Rejected — the file has no
  build step and the owner's pattern is runtime merge, not codegen. Keep it.
- **Hydrate inside a BOOT batch entry.** Rejected — BOOT entries run
  synchronously in the RAF loop; an async hydrate wouldn't be awaited and
  champion-consuming builders would race it. Must be `await`ed before the loop.

## [OPEN_QUESTIONS]

1. **CLOSED (owner 2026-09-09, shipped in 5B-FIX).** Caciques de Humacao and
   the 2021 Grises de Humacao are two distinct franchises — see the crosswalk
   section above and `reconcile_spec.md` [OWNER_RESOLUTIONS]. Follow-up: after
   `hydrate()` (5D) the app's Franchises tab will show "Grises de Humacao ·
   founded 2021" (the `hum` id = the 2021 expansion). Also `docs/project.md` D2
   ("Grises de Humacao → Criollos de Caguas (2023)") should be refined — owner's
   Tier-2 file.
2. **How far to push the player index.** Default: keep the curated `PINDEX` as
   the front page of tab `jugadores`; add a "buscar en los 3,303" affordance
   that loads `index/players.json` and, on click, fetches `players/<id>.json`.
   `showPlayer`'s gap message shrinks only for ids with real career/box data.
3. **`SCORING` chart vs table (D4).** The chart plots the ppg era only. Keep
   that; table gets the full 1948–2021 with a `metric_era` column + a visible
   1970/71 divider.
4. **`buildSources` rewrite — who owns the new gap text?** It's editorial. 5D
   proposes the factual corrections (box scores exist, standings 2001–13 exist,
   MVP 1958–2004 exists); the owner phrases them.
5. **`app/` vs `web/` for the shell (5G).** Unchanged from before — 5G moves the
   file to the Pages-served root; `app/` stays canonical until then.
6. **`bsn_player_seasons_realgm.csv` / `bsnpr_scraper.py`.** Referenced by the
   app (`POOL_RGM`, `buildSources`) but **not in this repo**. Out of PHASE_5
   scope; flag that the app assumes external data the pipeline doesn't have.
