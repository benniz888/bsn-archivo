# Spec: App Data Map + web/data JSON Schema (PHASE_5, sub-phase 5A)

Companion to [`app_data_sync_spec.md`](app_data_sync_spec.md) (the decision) and
[`clean_data_storage_spec.md`](clean_data_storage_spec.md) (gzip). This file is
the **contract 5B–5G build against**: which embedded block comes from where, and
the exact shape of every `web/data/` file. No code in 5A.

## [PURPOSE]

`app/bsn_archivo.html` (2,214 lines) carries ~30 embedded `const` data blocks.
5A settles, per block: **regenerate from CSV | merge CSV + curated | leave
hand-maintained**, then fixes the target JSON tree. The finding that shapes
everything downstream:

**The app is ~90% hand-curated editorial content with no CSV counterpart.**
`data/clean/` is the *research archive* (3,303 players, 1,287 games, 39,669
box-score rows, historic champions/scoring/awards 1948–2004). The app is a
*curated magazine* (club colours, coach names, arena capacities, Hall-of-Fame
essays, "on this day", the refuerzo-rule timeline, the Juega game pool). The two
overlap only at champions, scoring titles, career leaders and records.

So PHASE_5 is **not** "regenerate the app from CSVs". It is:
1. sync the ~4 blocks that genuinely have a CSV source (§A), and
2. expose the large CSV-only archive the app cannot currently show at all, as
   fetched per-entity JSON (§D) — new capability, new UI in later sub-phases.
Everything else stays inline, hand-edited (§C).

## [DECISION]

### The franchise-key crosswalk (the one hard dependency for 5B)

The app keys franchises by a 3-letter code (`bay`, `sge`, `pon`, …, 30 keys);
the pipeline keys them by `franchise_id` slug (`vaqueros_bayamon`,
`atleticos_san_german`, …, 33 in `franchises.csv`). **5B's first task is an
explicit, checked-in crosswalk** `app/franchise_key_map.csv`
(`app_key,franchise_id,note`) — a curated naming file, not derived. Unmapped
rows on either side are a hard error in the build (a franchise in `champions_
reconciled` with no app key would silently drop a championship). 5A lists the
30 app keys and 33 ids for the mapping in [OPEN_QUESTIONS] Q1.

### Per-block classification

| block (app line) | shape | consumed by | source | 5B action |
|---|---|---|---|---|
| `F` (757) | `{key:{name,abbr,city,founded,active,end?,c1,c2,colorSrc,coach?,won:[y],ru:[y],note?}}` | ribbon, titleStats, matrix, seasons, teams, games, today, juega | **MERGE**: `name/city/founded/status` ← `franchises.csv`; `won/ru` ← `champions_reconciled.csv` (via crosswalk); `c1/c2/colorSrc/coach/abbr/note/end` = **curated, keep** | emit `index/franchises.json` merging the two; curated fields from a new `app/franchise_curated.json` |
| `champOf`/`ruOf` (1336) | derived `{year:key}` | ribbon, seasons, matrix | **REGEN** ← `champions_reconciled.csv` | fold into `index/seasons.json`; app derives the maps client-side |
| `SCORING` (884) | `[[year,player,club,metric,value]]`, 1966–1991 (26) | scoring tab (chart + table) | **REGEN** ← `scoring_champions_reconciled.csv` (68 seasons 1948–2021) + `historic_scoring_champions.csv` | emit `index/scoring_titles.json`; **expansion** — 26 → ~68 rows, D4 `metric_era` preserved |
| `LEADERS` (845) | `{category:[[rank,name,pos,years,total,gp,pg]]}` | leaders tab | **REGEN** ← `bsn_career_leaders.csv` (same 30-row seed) | emit `index/career_leaders.json`; carry D7 "floor, ~5yr stale" flag |
| `RECORDS` (913) | `[[label,value,holder,year,note]]` (11) | records tab | **REGEN** ← `bsn_records.csv` (same seed) | emit `index/records.json` |
| `MVP_REPEAT` (881) | `[[name,count]]` (7) | leaders tab | curated (derivable from `historic_awards.csv` later) | **keep inline** for MVP; note as a Q |
| `ARENAS` (830) | `[[team,city,arena,capacity]]` (12) | teams tab | **curated, no CSV** | keep inline |
| `COACHES` (927) | HOF coaches (11) | records tab | curated | keep inline |
| `NBA_PLAYERS` (937) | (7) | records tab | curated | keep inline |
| `RECENT` (947) | rich season recaps 2009–2026 (7) | recent tab | **curated editorial** (some facts overlap `champions_reconciled`, `game_results`) | keep inline; do not regen |
| `HOF` (1034) | essay cards (~11) | HoF tab | **curated editorial** | keep inline |
| `STONE`/`RETIRED` (1102/1109) | (4/2) | HoF tab | curated | keep inline |
| `REF_RULES`/`REF_TIMELINE`/`REF_SCORERS` (1114/1121/1129) | refuerzo rules + 2024–25 timeline | refuerzos tab | **curated editorial** | keep inline |
| `CALENDAR`/`NEXT_SEASON`/`ON_THIS_DAY`/`FINALS_2025`/`CLINCHERS`/`CHANNELS` (1138–1206) | today/games editorial | today, games | **curated editorial** | keep inline |
| `STANDINGS` (1187) | `{year:{teams,games,rows:[[team,w,l]],note}}` — only 2009 | games tab | **NEW from CSV**: derive W–L from `game_results.csv` winners for 2001–03, 2008–13 | emit into `seasons/<year>.json`; keep the 2009 hand row as a cross-check |
| `POOL` (1224) | Juega game pool `{n,d:[dec],c:[key],ppg,rpg,apg,pos,t:[tag],b}` (~45) | juega tab | **curated game data** (PC1 note in the block itself) | keep inline; PHASE_4B_GAME_POOL is its own scope |
| `TAGS`/`NOTES`/image config | — | juega, seasons | curated | keep inline |
| rules text, `REF_*` prose, tab copy in HTML | — | all tabs | curated | keep inline |

### CSV-only archive → new fetched JSON (§D — no current app block)

| CSV | → web/data | grain |
|---|---|---|
| `players_canonical.csv` (3,303) + `player_aliases.csv` + `player_career_seasons.csv` + `player_id_map.csv` | `index/players.json` (light) + `players/<bsnpr_id>.json` (full) | one per player |
| `game_results.csv` (1,287) + `game_box_player.csv` (39,669) | `games/<season>/index.json` + `games/<season>/<game_id>.json` | one per game |
| `game_plays.csv.gz` (233,664) | `games/<season>/<game_id>_pbp.json` | one per game — **5F, gated on actor→id linking** |
| `historic_scoring_champions.csv` (1948–2004) + `historic_awards.csv` (1958–2004) | `seasons/<year>.json` | one per season |
| `player_season_leaders.csv` + `player_season_leaders_2000_2002.csv` + `player_season_stats_2001_2004.csv` | `seasons/<year>.json` | one per season |
| `seasons_stats_tracked.csv` + `leader_coverage_gaps.csv` | `seasons/<year>.json` `.coverage` block | PC2/PC4 gap signal |
| `franchise_events.csv` (D2 lineage) | `index/franchises.json` `.lineage` | per franchise |

## [INTERFACES]

### Target tree

```
web/
  bsn_archivo.html            # the shell (moved/symlinked from app/ in 5G; app/ stays canonical until then)
  sw.js                       # 5E
  manifest.webmanifest        # 5E
  data/
    manifest.json             # { schema_version, source_commit, counts:{players,games,seasons,...} }
    index/
      franchises.json         # [ FranchiseIndex ]   §A+curated merge
      seasons.json            # [ SeasonIndex ]      champions_reconciled
      players.json            # [ PlayerIndex ]      3,303, light
      scoring_titles.json     # [ ScoringTitle ]     scoring_champions_reconciled + historic
      career_leaders.json     # { category: [CareerLeader] }
      records.json            # [ Record ]
    players/<bsnpr_id>.json    # PlayerFull
    seasons/<year>.json        # SeasonFull
    games/<season>/index.json  # [ GameIndex ]
    games/<season>/<game_id>.json       # GameBox
    games/<season>/<game_id>_pbp.json   # GamePBP   (5F, only if actor-linked)
```

### Record shapes (field → null when unrecorded — never 0, PC2)

```
FranchiseIndex = { franchise_id, app_key, name, city, founded:int, status:"active"|"defunct",
                   end:int|null, abbr, colors:{c1,c2,src:"wiki"|"approx"}, coach:str|null,
                   titles:[int], finals_lost:[int], note:str|null,
                   lineage:[ {event_type, season:int|null, from:franchise_id|null, to:franchise_id|null, confidence, note} ] }
SeasonIndex    = { season:int, champion:franchise_id|null, runner_up:franchise_id|null,
                   agreement, confidence, note:str|null }
PlayerIndex    = { id:int, name, norm, first_season:int|null, last_season:int|null,
                   position:str|null, birth_year:int|null, nationality:str|null,
                   n_seasons:int|null, has_profile:bool }
ScoringTitle   = { season:int, metric_era:"total_points"|"ppg", player, club_raw,
                   ppg:float|null, total_points:int|null, games:int|null,
                   confidence, sources:[str], note:str|null }
CareerLeader   = { rank:int, player, position:str|null, years, total:int|null,
                   games_played:int|null, per_game:float|null }   # + list-level "stale_since" note (D7)
Record         = { record, holder, value, season:int|null, note:str|null }
PlayerFull     = { id, name, aliases:[{alias, type}], birth:{date:str|null, year:int|null, city:str|null},
                   position:str|null, nationality:str|null, has_profile:bool,
                   career:[ {season:int, team_raw, franchise_id:str|null, games:int|null, points:int|null} ],
                   observations:[ {obs_source, season:int, club_raw, match_method, club_check} ],
                   sources:[str] }
SeasonFull     = { season:int, champion:franchise_id|null, runner_up:franchise_id|null,
                   standings:[ {team_raw, franchise_id:str|null, w:int, l:int} ] | null,
                   leaders:{ category: [ {rank:int, player_raw, club_raw, value:float|null, kind} ] } | null,
                   awards:[ {award, player_raw, team_raw} ] | null,
                   coverage:{ stats_tracked:{cat:bool}, gaps:[ {status, detail} ] },
                   sources:[str] }
GameIndex      = { game_id, date:str|null, a:{team_raw, score:int|null}, b:{team_raw, score:int|null} }
GameBox        = { game_id, season:int, date:str|null, script,
                   teams:{ a:{team_raw, franchise_id:str|null}, b:{...} },
                   score:{ a:int|null, b:int|null }, quarters:{ a:[int], b:[int] } | null,
                   box:[ {player_raw, bsnpr_id:int|null, team_raw, jersey, minutes:int|null,
                          fg2m,fg2a,fg3m,fg3a,ftm,fta,oreb,dreb,reb,ast,stl,blk,pf,tov,pts,  # each int|null
                          box_check:"ok"|"pts_mismatch"} ],
                   sources:[str] }
GamePBP        = { game_id, season:int, plays:[ {q:int, clock, seq:int, text, event_type:str|null,
                          actor_raw:str|null, actor_id:int|null, team_raw:str|null} ] }
```

### Build contract (`make build-web-data`, 5B)

- **Deterministic.** `json.dumps(obj, ensure_ascii=False, sort_keys=True,
  separators=(",",":"))` + `"\n"`. Floats formatted to a fixed precision
  (`round(x, 2)` for ppg/pct). No wall-clock time in any file —
  `manifest.json.source_commit` = `git rev-parse HEAD` is the version. Rerun on
  the same commit ⇒ byte-identical tree ⇒ empty git diff (spec [INTERFACES]).
- **Reads `data/clean/` only** (via `open_clean_text` for the `.gz`), plus the
  two curated files under `app/`. Never the network. Idempotent.
- **`web/data/` is a tracked deploy artifact** — not gitignored. Committed with
  each ingest session's data changes.
- **Gap contract (spec [INTERFACES]).** A missing file, a `null` field, or an
  empty `leaders`/`standings` ⇒ the app renders its existing "not recorded" /
  "N of 15 categories were never recorded" message. The build never writes `0`
  for an unknown, never invents a row (PC1/PC2). `coverage.gaps` per season is a
  first-class output (PC4).
- **PBP gating (5F).** `<game_id>_pbp.json` is emitted only for games where
  every play's `actor_raw` is resolved to a `bsnpr_id`. Until the PBP→identity
  link exists, no PBP files are written and the app shows the PBP section as
  "beta, per game" (spec OQ2).

## [ALTERNATIVES_REJECTED]

- **Regenerate `RECENT` / `HOF` / `CLINCHERS` from `champions_reconciled` +
  `game_results`.** Rejected — these are written prose with editorial judgement
  (which facts to lead with, how to phrase a caveat). The CSVs can't produce
  them and shouldn't try. They stay hand-edited; if a fact drifts, that's a
  one-line manual fix, not a pipeline concern.
- **One big `web/data/all.json`.** Rejected — that is the PC7 problem the spec
  already killed. Per-entity chunking is the point.
- **Derive the franchise crosswalk from name similarity.** Rejected — 3 of the
  33 ids have no clean app-key match (Santos de San Juan, Club Náutico,
  Cocoteros) and 2 app keys are era-ambiguous (`man` Osos vs `ate` Atenienses).
  A checked-in curated map with a build-time completeness assert is the only
  safe form (mirrors D-029 / `club_code_map`).
- **Put `built_at` wall-clock in `manifest.json`.** Rejected — breaks the
  deterministic-tree property. `source_commit` carries the version; `git log`
  carries the "when".

## [OPEN_QUESTIONS]

1. **Franchise crosswalk (blocks 5B).** **32 app keys** (`bay sge pon san are que
   gua cag car may agu man` active; `cap rio veg upr cno nau aib mor toi guy isa
   coa faj hum ate vil cab agd con cay` defunct) vs **33 `franchise_id`** in
   `franchises.csv`. The mapping is ~1:1 by name; the one extra id is
   **`santos_san_juan`** (D5 — the 1945 dispute; the app folds it into `cap`).
   5B builds `app/franchise_key_map.csv` (`app_key,franchise_id,note`) with a
   build-time assert that every `champions_reconciled` / `franchises` id and
   every app key is accounted for (an explicit `note` row for `santos_san_juan`,
   whichever way the owner wants 1945 shown).
2. **Which `won`/`ru` wins when app and `champions_reconciled` disagree?**
   Default: the CSV (it's the reconciled, provenance-tracked source — B4 says
   CSV is truth). The app's arrays get regenerated; a diff report at build time
   flags every season where they differed so a human can eyeball it once.
3. **`SCORING` metric switch (D4).** The CSV has `metric_era`; the app chart
   currently plots only the ppg era (1971+). Keep that (chart = ppg era only,
   table = full 1948–2021 with a metric column and a visible D4 divider).
4. **Season standings from `game_results`.** W–L is derivable for 2001–03 +
   2008–13 but the archive is not a complete game set for any season except
   maybe 2009. Default: emit standings only where `game_results` covers ≥90% of
   a plausible schedule, else omit (→ gap message). 5C decides the threshold
   from the actual game counts.
5. **`app/` vs `web/` for the shell.** 5A–5F keep editing `app/bsn_archivo.html`
   as canonical. 5G moves/copies it to `web/` (the Pages-served root) and
   settles whether `app/` becomes a symlink or is retired. Not decided now.
6. **MVP/award history in the app.** `historic_awards.csv` (MVP/ROY/DPOY
   1958–2004) could replace the curated `MVP_REPEAT` and feed a new awards view.
   Deferred — not blocking; revisit after 5C.
