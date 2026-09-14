# Spec: season-vs-season comparison + per-season profile view

**Status: DONE, owner-verified live** — data layer extended and rebuilt
(250 rich season-rows, 154 players, verified against the spec's own
predicted counts), inline compare panel + per-season route implemented,
`scratchpad/season_detail_harness.mjs` green alongside all existing
harnesses, `make verify` + `make test` (174) green. Owner verified live on
Raymond Dalmau's page ("checkboxes, compare panel, and per-season delta
all work exactly as spec'd") while reporting the separate Georgie Torres
crosswalk bug — see `docs/session.md`. Known gaps for later: cross-player
season comparison and modern-era (2024–2026) data — queued as backlog
item 4, not this spec.

For review before build. Data findings verified directly against
`data/clean/*.csv` and the current `build_players_detail()` — see
[FOUND] below for exact counts.

## [DECISION]

Owner-approved 2026-09-11, after the data-inventory review:

1. **Season-vs-season comparison is inline in the player card** — check 2+
   rows in the existing "Temporada por temporada" table, a compare panel
   appears. Not a third Comparar mode, not a new subnav view. No hash/URL
   state — pure in-page interaction, same as any other client-side toggle
   in this app.
2. **Per-season profile is a real route** — `#jugadores/jugador/<slug>/<season>`,
   deep-linkable, extending the existing router. Renders inline within the
   `buscar` view (same place `#jugadores/jugador/<slug>` already renders —
   player-detail routes were never their own top-level `.view`, and this
   stays consistent with that).
3. **Tier 3 (aggregating `game_box_player.csv` to season totals) is an
   explicit later phase**, named but not built here — see [OUT OF SCOPE].
4. The "antes de 2011" copy overstatement is a separate follow-up, logged
   in `docs/session.md`, not part of this spec.

## [FOUND] — the data inventory, verified against the repo

| Tier | Source | Coverage | Status |
|---|---|---|---|
| 1 | `player_career_seasons.csv` → `web/data/players/<id>.json`'s `career[]` | 1,107 players, seasons 1956–2021, 6,555 rows. 729 players have ≥2 seasons (comparable); median 3/player, one outlier at 55 (worth a build-time sanity glance, not a blocker). | **Live today** — games + points only, no other categories. Already rendered as the flat "Temporada por temporada" table. |
| 2 | `player_season_stats_2001_2004.csv` | **154 players, already resolved to a canonical `bsnpr_id`** (276 of 504 rows, via `player_id_map.csv`, `obs_source='player_season_stats_2001_2004.csv'`). Minutes, FG/3PT/FT makes+attempts+FG%, defensive + total rebounds, assists, steals, blocks, turnovers, points, ppg. 2001–2004 only. | **Sourced, identity-resolved, parsed, verified — never read by `build_web_data.py`.** This is the real find: no new fetching, no new identity work, one function needs extending. |
| 3 | `game_box_player.csv` | 39,670 per-game rows, 54% (21,751) carry a `bsnpr_id`. 2001–2003 + 2008–2013, 54–151 linked players/season-year. Already published per-game (`web/data/games/<season>/<id>.json`). | **Raw material, not season totals.** No aggregation step exists. The archive's own comments already flag these years as an incomplete game set — any aggregate would be a partial-season sum, not a real total, and has to say so. Named as a follow-up phase, not built now. |
| 4 | `player_season_leaders.csv` (+ 2000–2002 variant) → `web/data/seasons/<year>.json`'s `leaders` | Per-season top-N leaderboards, keyed by raw player name (not `bsnpr_id`). | **Live**, feeds `loadSeasonExtra`. Usable read-only as a name-matched cross-reference (see [DATA] §3), not a data-integrity claim — identity for these players is already established elsewhere; this is a display nicety, not a new identity link. |

**Overlap check** (ran directly against the CSVs before writing this):
of the 154 resolved players' 250 distinct (`bsnpr_id`, season) pairs, **242
already line up with an existing `career[]` row** (clean case — attach the
richer stats to it) and **8 are new** (no existing `career[]` row at that
season — a fresh entry gets synthesized from the stats row's own
season/team/games/points, same shape as every other entry). Also found: 296
stat rows resolve from 276 crosswalk keys — a handful of (`bsnpr_id`,
season) pairs have more than one matching stat row (a mid-season team
change, or a source duplicate). Build rule: **keep the one with more
recorded games, never silently sum or duplicate** — same "pick
deterministically and say so" discipline as the rest of this archive.

## [DATA]

### 1. `build_players_detail()` — extend, don't replace **(built — `_season_stats()`)**

`career[]` keeps its current shape (`season, team_raw, franchise_id, games,
points`) — the existing "Temporada por temporada" table needs zero changes.
Each entry optionally gains a `stats` object when Tier 2 has it:

```
stats: { games, pts, minutes, fg:{m,a,pct}, tp:{m,a}, ft:{m,a}, reb:{d,t},
         ast, stl, blk, tov, ppg }
```

Build steps:
1. Read `player_season_stats_2001_2004.csv`, keyed by (`player_raw`,
   `team_raw`, `season`).
2. Read `player_id_map.csv` rows where `obs_source ==
   'player_season_stats_2001_2004.csv'`, keyed the same way, to get
   `bsnpr_id`.
3. Join. Where a (`bsnpr_id`, season) pair has >1 matching row, keep the
   one with more `games` recorded.
4. Attach `stats` to the matching `career[]` entry; for the 8 pairs with no
   existing entry, append a new one (season/team_raw/games/points from the
   stats row, `franchise_id` resolved the same way every other entry is).
5. `null`/absent fields stay absent — never a fabricated `0`.

Absolutely nothing here touches identity resolution — the 154 players are
already linked; this is a data-shape change only.

**Two things the build surfaced, not visible from the CSVs alone:**

- **`stats.games`/`stats.pts` repeat the totals inside the `stats` object
  itself, rather than overwriting the entry's own top-level `games`/
  `points`.** The two sources can disagree — one build hit a player-season
  where `player_career_seasons.csv` said 411 points and
  `player_season_stats_2001_2004.csv` said 422 for the same year. Never
  silently reconciled: the top-level fields stay whatever
  `player_career_seasons.csv` said (so the existing thin table is
  byte-for-byte unchanged), and the richer, more granular Tier-2 total
  lives in `stats.pts` — the same "show both, labelled, don't merge" rule
  `loadPlayerExtra`'s own code comment already states for this exact class
  of problem (archive-vs-curated totals).
- **`player_career_seasons.csv` sometimes carries more than one row for the
  same player-season** — the same team written two ways across different
  Wayback captures (e.g. `"BAYAMON"` and `"Vaqueros, Bayamon"` as two
  separate rows for one player's 2001). Confirmed: 135 of the 250 Tier-2
  pairs land on a season with a sibling row like this. Pre-existing in the
  source data, not introduced or worsened here — the existing "Temporada
  por temporada" table already renders both rows today. `stats` attaches
  to whichever sibling's `team_raw` actually matches the crosswalk key
  (verified: exactly one match every time, 0 misses across all 250 pairs).
  §4's per-season route picks the stats-bearing sibling when one exists;
  deduplicating the source rows themselves is a separate data-quality task,
  not in scope here.

### 2. Comparison categories (Feature 1)

Render whichever categories **either** selected season has, `—` for the
one that doesn't — never silently drop a category just because one side is
thin (that hides a real gap, this archive's whole ethos is the opposite).

| Category | Tier | Note |
|---|---|---|
| PTS (total) | 1 | always available |
| JJ (games) | 1 | always available |
| PPG | 1 (derived) / 2 (real) | Tier 2 uses the source's own `ppg`; Tier 1 derives `pts/games`, labeled "calculado" like the rest of the app already marks derived values |
| MIN | 2 only | |
| REB / RPG | 2 only | RPG derived (`reb.t/games`), labeled "calculado" |
| AST / APG | 2 only | APG derived, labeled "calculado" |
| STL, BLK, TOV | 2 only | totals only, no per-game (keeps the panel from overcrowding) |
| FG%, 3PT (m-a), FT (m-a) | 2 only | real, from source |

Visual: reuse the existing player-vs-player Comparar bar components
(`.cmprow`/`.cmptrack`/`.cmpfill`/`.cmpval`/`.cmplab`) as-is — same shape
of problem (two columns of numbers, a bar each), zero new CSS needed.

### 3. Per-season profile (Feature 2)

For a Tier-2 season: headline PPG/RPG/APG (matches `showPlayer`'s existing
`.strip` 6-stat pattern — reuse `.strip`, zero new CSS), FG%/3PT/FT line,
games+minutes, and a **"vs [most recent prior season]" delta line** that
calls the exact same diff logic Feature 1's compare panel uses — the two
features share one comparison function, not two.

For a Tier-1-only season: season, team, games, points, and — matching
`build_players_detail()`'s existing thin/`has_profile` honesty pattern —
*"Sin más detalle por temporada en el archivo."* Never an empty block.

**Optional cross-reference, low-stakes**: if this player+season+category
appears in that season's `web/data/seasons/<year>.json` `leaders` list
(normalized exact name match — a small per-season list, low collision
risk, and this is a display nicety on top of an identity that's already
established, not a new identity claim), show *"Líder de la liga en
anotación esa temporada."* Skipped silently when there's no match — never
a forced/empty line.

### 4. Routing

`applyHash`'s existing `#jugadores/jugador/<slug>` branch gains an optional
4th segment:

```
#jugadores/jugador/<slug>/<season>
```

`showPlayer(name, id, season)` gains the third param. When present, after
the normal card renders, it also renders the per-season block (§3) and
scrolls to it. Works through **both** existing player-resolution paths —
the curated `PINDEX` match and the archive-only `openArchivePlayer` path —
since season data lives on `web/data/players/<id>.json` regardless of
curation status. An unknown/mistyped season is silently ignored (renders
the normal card, no per-season block), matching every other defensive
`if(!x) return` in this router — never an error state for a bad deep link.

## [LAYOUT]

```
Player card (.phero, existing)
Temporada por temporada (existing table, now with a checkbox per row)
  [ ] 2001  Bayamón   26  221
  [x] 2002  Bayamón   24  198
  [x] 2003  Bayamón   26  278
  → 2+ checked: compare panel appears here (reuses .cmprow/.cmptrack/...)
  → click a season's year (or a small "Ver temporada" link on the row):
    navigates to #jugadores/jugador/<slug>/<season>
      → per-season block renders below the table (.strip 6-stat grid +
        FG%/3PT/FT line + "vs <prior season>" delta + optional league-
        leader callout), page scrolls to it
```

## [OUT OF SCOPE — this pass]

- **Tier 3**: aggregating `game_box_player.csv` into season totals.
  Real follow-up phase — more players/seasons than Tier 2 (2001–2003 +
  2008–2013 vs. 2001–2004 only), but needs new aggregation code and a
  "partial season, archive isn't a complete game set" caveat that Tier 2
  doesn't need. Not bundled in.
- The "antes de 2011" copy overstatement — logged as a follow-up in
  `docs/session.md`, not touched here.

## [ALTERNATIVES_REJECTED]

- **A third Comparar mode, or a new subnav view, for season comparison.**
  Rejected — decision 1. Inline on the card it already lives on.
- **Restricting comparison to Tier-2-only season pairs.** Rejected —
  degrading gracefully (thin vs. thin, thin vs. rich) and showing the gap
  is more honest and more useful than an artificial restriction.
- **A modal for the per-season view.** Rejected — decision 2 wants a real,
  shareable URL; every other detail view in this app already has one.

---

# Addendum: backlog item 4 — cross-player season comparison

**Status: BUILT, verified locally (real jsdom execution of the actual
built page against real data — see [VERIFICATION] at the end), pending
push + live poll.** Owner asked for two things:
(1) comparing two *different* players' specific chosen seasons, not just one
player across their own seasons; (2) confirming whether modern-era
(2024–2026) data exists at the granularity needed, before promising it.
Findings below are checked directly against the repo, not assumed.

## [FOUND] — modern-era wall (owner ask 2)

Checked every place player-season data could live, not just
`web/data/seasons/<year>.json`:

| Source | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|
| `player_career_seasons.csv` (any row) | 2 stray | 2 stray | 2 stray | 0 | 0 | 0 | 0 | 0 |
| `player_season_stats_2001_2004.csv` / `player_season_leaders.csv` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `standings.csv` (team-level, no players) | no capture | no capture | no capture | captured, unparseable | no capture | — | — | — |
| `web/data/seasons/<year>.json` | — | — | — | — | — | champion/runner-up only | champion/runner-up only | champion/runner-up only |

**No player-level data exists for 2022–2026, and team standings stop at
2018.** 2019–2021's handful of rows (2–6/year) are incidental captures on
individual `jugador.asp` profile pages, not a systematic season pull — not
"thin," genuinely absent for 2022+. **Decision: the season picker (below)
never offers 2022–2026 for anyone** — the years simply aren't in any
player's `career[]`, so this falls out for free, no special-case code. A
static note near the picker explains why (owner's call, explicit-note
option), not a silent gap someone could mistake for a bug. Closing this
data gap is backlog item 7 (latinbasket roster ingest), explicitly deferred
to its own phase — not pulled into this feature.

Real season-vs-season comparisons are meaningful **1956–2017ish**: rich
(full stat line) only for the 154 Tier-2 players, **2001–2004**; thin
(PTS/GP, PPG calculado, `—` elsewhere) for the wider Tier-1 population,
**1956–2021**, density falling off hard after 2017. This is the same
graceful-degradation contract §2/§3 already implement — nothing new here,
just now driven by two independently-chosen (player, season) pairs instead
of one player's own rows.

## [FOUND] — the index's `n_seasons`/`has_profile` fields are not reliable
eligibility signals

Before designing the picker, checked whether the existing
`web/data/index/players.json` fields could drive "does this player have a
real season to pick" without a new build-time field:

- **`n_seasons` is a pass-through of `players_canonical.csv`'s free-typed
  field, not derived from actual `career[]` rows.** Cross-checked all 3,357
  canonical players' declared `n_seasons` against their real row count in
  `player_career_seasons.csv`: **251 mismatches**, of which **6 declare a
  positive `n_seasons` with zero actual career rows** — concretely, 4 of
  T9.5's own additions this session (`991009` Evans, `991012` Wells,
  `991013` Smith, `991014` Hines all show `n_seasons:1` with `career:[]`
  empty — the `991xxx` band deliberately never gets a
  `player_career_seasons.csv` row, D-048's own established pattern) plus 2
  more elsewhere in the archive. A picker built on `n_seasons>0` would let
  someone "select" these 6 and land on an empty panel.
- **`has_profile` doesn't work either**: 26 players show `has_profile:yes`
  with zero career rows, and 24 show `has_profile:no` with real career rows
  present — a `jugador.asp` capture existing (or not) doesn't track with
  whether it actually carried a parseable season table.
- **Conclusion: needs one new, correctly-derived field.** `build_web_data.py`
  already computes each player's `career[]` when writing
  `web/data/players/<id>.json` — the fix is to also emit its real length
  (e.g. `career_seasons`) into `web/data/index/players.json` at the same
  time, from the same data, no new fetch/parse/identity work. `n_seasons`
  itself is left untouched (it's shown as biographical info elsewhere and
  sourced deliberately differently in some rows — this isn't "fixing" it,
  it's adding the one field this feature can actually trust).

## [DECISION] — owner-approved 2026-09-13

1. **Player search: full archive index (3,357), not the curated ~228-name
   `PINDEX`.** Reaches the real Tier-2 players (most of the 154 2001–2004
   names aren't in `PINDEX`) — the feature is only worth building if it can
   reach them. Filtered to the new `career_seasons>0` field.
2. **No third Comparar mode.** Extends the existing Comparar mode: each
   added player gets an optional **"Carrera / Temporada"** dropdown next to
   their card. Left on "Carrera" (default), a player's row is byte-identical
   to today's output — zero behavior change for existing usage. Switching
   either side to a specific season swaps that side's comparison object from
   the `PINDEX` career-average shape to a `seasonCmpObj()`-built season
   shape (already exists, `season_detail_spec.md` §1/§3 — built for the
   single-player case, generic enough to reuse as-is here).
3. **2022–2026 never appear in any season dropdown**, with a one-line static
   note near the picker (see [FOUND] above) — not silently omitted.

## [DATA]

### 1. `build_web_data.py` — one new index field

`web/data/index/players.json` entries gain `career_seasons: int` = the
length of that player's already-computed `career[]` array (0 for anyone
without one). No new source read, no new identity work — same data
`build_players_detail()` already produces, just also surfaced at index
level so the picker doesn't need to fetch every candidate's full JSON to
know if they're eligible.

### 2. Player picker — reuse the archive-wide search, not `PINDEX`

The app already has full-archive player search/resolution (the
`openArchivePlayer` path, PHASE_8 5D.3c). Comparar's `cmpAdd()` today only
searches `PINDEX` via a `<datalist>`; this feature's picker instead
searches the full `players.json` index, filtered to `career_seasons>0`.
Selecting a player fetches `web/data/players/<id>.json` (same fetch
`showPlayer`/`loadPlayerExtra` already does for the single-player case) to
populate that side's season dropdown from their real `career[]` entries —
never from `first_season`/`last_season`/`n_seasons`.

### 3. Comparison render — no new component

Once both sides have a chosen (player, season) or (player, "Carrera"):
- Career side → existing `PINDEX` lookup → existing `CMP_RATE/SHOT/TOTAL` +
  `cmpBarRow()`, unchanged.
- Season side → existing `seasonCmpObj(career[i])` → same `cmpBarRow()`,
  same category groups §2 already defined (`SEASON_CMP_RATE/SHOT/TOTAL`
  used when *either* side is season-mode, since those are the categories a
  season actually has — career totals like "Puntos de carrera" don't apply
  once one side is a single season).
- Mixed mode (one side career, one side a season) is allowed — same
  "render whichever categories either side has, `—` for the other" rule
  §2 already states, just applied across two different players instead of
  two seasons of one player.

Zero new CSS: `.cmphead`/`.cmprow`/`.cmptrack`/`.cmpfill` already handle an
arbitrary label string (`cmpHead`/`renderSeasonCmp` both already build
custom label text), so `"Bonzi Wells · 2010"` renders exactly like
`"Raymond Dalmau · 2001"` already does today for the single-player case.

## [LAYOUT]

```
Comparar (existing view)
  [ Buscar/añadir jugador ] [Añadir] [Limpiar]   (existing, now searches
                                                   the full archive index)
  ┌─ Bonzi Wells ──────────────┐  ┌─ Ángel Rodríguez ───────────┐
  │ Carrera ▾ | 2010            │  │ Carrera ▾ | 2001  2002  …   │
  │ (dropdown: only seasons      │  │ (only seasons that exist)    │
  │  present in career[])        │  │                               │
  └───────────────────────────┘  └───────────────────────────────┘
  ⓘ 2022–2026 aún no tienen datos por jugador en el archivo — la
    comparación llega hasta donde el archivo llega.

  [ existing cmphead / cmpradar (career-mode only) / cmpBarRow panel,
    unchanged rendering, fed by whichever shape each side resolved to ]
```

## [OUT OF SCOPE — this pass]

- **Closing the 2022–2026 gap.** Backlog item 7 (latinbasket roster
  ingest), its own future phase, not folded in here — same boundary T9.1
  already drew for the team-standings half of this same source.
- **Radar chart in mixed/season mode.** `cmpRadar()` is scaled against
  `PINDEX`'s career-level per-game maxes app-wide; a single season's rate
  stats aren't on the same scale (a great single season can exceed any
  career average). Radar stays career-mode-only for now — showing it
  against a mismatched scale would be misleading, not just incomplete.
  Flagged, not solved here.
- **Fixing the other 245 `n_seasons` mismatches** found in [FOUND] above
  that aren't the 0-career-rows class (e.g. a bio claims 18 seasons, the
  archive captured 6 of them) — real, but a separate data-quality question,
  not this feature's job; `career_seasons` is added as a new, narrowly-
  scoped field specifically so this feature never has to touch or trust
  the existing `n_seasons` semantics.

## [ALTERNATIVES_REJECTED]

- **Fetch-and-check every archive-wide search result's full JSON to
  determine eligibility at picker time.** Rejected — up to 3,357 fetches
  for a live-search box. The new `career_seasons` index field makes
  eligibility a local filter instead.
- **Reusing `n_seasons`/`has_profile` as the eligibility signal.** Rejected
  — both demonstrably wrong on real rows (see [FOUND]), would silently
  promise data that doesn't exist for at least 6 known players today.

## [VERIFICATION]

No live browser tool was available in this session (`claude-in-chrome`
wasn't connected) and this repo has no Playwright/jsdom test infra of its
own (`app/bsn_archivo.html` is deliberately dependency-free, PC7). Rather
than skip real execution, ran the *actual built page* — `web/index.html`
post-`make site`, real `web/data/*` — inside `jsdom` (installed to a
scratch `/tmp` dir, not added to this repo) with a second `<script>`
injected into the same document so it shares the app's top-level `let`/
`const` scope (those never attach to `window` — only functions/`var` do;
this is why the test script runs *inside* the page rather than poking at
it from outside). `PINDEX` built from the page's own baked-in arrays (no
network); `FID2APP`/`PALL`/`PXWALK` loaded from the real on-disk
`web/data/index/*.json` the same way `hydrate()` does over the wire.

Confirmed directly against the running code, not asserted:
1. `cmpCandidateNames()`: 1,484 names, up from `PINDEX`'s 381 — the picker
   really is wider now.
2. `cmpPreset('Raymond Dalmau','Rubén Rodríguez')` (today's existing
   career-vs-career preset): renders `cmpcard`, keeps the radar, keeps the
   "De carrera" label, and now shows a season `<select>` per side
   (defaulted to "Carrera") — the addition is additive, the existing path
   still renders.
3. Switching Dalmau to his last fetched season (20 real career rows):
   radar drops, "De la temporada" label appears, the season label reads
   "Temporada 1985" (his actual last season) — confirms `cmpSetMode` +
   `cmpResolved` + `seasonCmpObj` wiring end-to-end against real data, not
   a mock.
4. Added `Rivera, A.g.` (`career_seasons:1`, not a `PINDEX` name) alone:
   correctly shows "Añade otro jugador" (not a crash), a season `<select>`
   with no "Carrera" option. Added Dalmau as the second side: a full mixed
   comparison renders with "De la temporada" — the season-only-archive-
   player path works, including the header stub for a still-resolving
   pending side.
5. The picker note explicitly names 2022 as where data stops.

No error traceable to any new function (`cmpResolved`, `cmpEnsureData`,
`cmpCandidateNames`, `cmpSeasonSelect`, `cmpSetMode`, `drawCompare`'s new
branches) appeared in the run. The console noise that did appear (`BSN:
falló el constructor «…»`, `matchMedia is not defined`) is the app's own
unrelated `BOOT()` sequence auto-firing against a DOM this harness
deliberately stripped down to 4 elements — a test-harness artifact of
running outside a real browser, not a regression; every one of those
failures is inside the app's own pre-existing per-widget try/catch and
would not occur against the real page in a real browser.
`make verify` (339,252 checks) / `make test` (191) green (Python side —
the `career_seasons` field addition to `build_web_data.py`).

---

# Part 2: MVP-season marking (2026-09-14)

**Status: BUILT, verified locally, pushed. Owner asked**: mark
MVP-winning seasons in the season dropdown (e.g. "1975 — MVP") so
they're easy to pick on purpose — but only after confirming real
coverage, same honest-gap discipline as everything else.

**[FOUND]**: MVP years were not already linked. `historic_awards.csv`
(MVP/Rookie/DPOY, 1958-2004) had never been run through identity
resolution at all — only `historic_scoring_champions.csv` got that
treatment (PHASE_3I). Added it to `OBSERVATION_FILES`
(`src/parse_players.py`), same pattern. Real coverage, using the actual
matcher (`build_id_map`), verified against the persisted result, not a
guess: 36 of 47 MVP rows resolve to a specific canonical player on the
plain existing `name+season_in_career` tier (no new matching code
needed); of those, **22 have a real `career[]` row for that exact
season** — the number that matters for a dropdown marker. 11 land in
the review queue (season not corroborated), 4 are unresolvable typos in
the source itself. Full detail: `docs/session.md`'s 2026-09-14 entries.

**A separate, real bug surfaced and fixed along the way**: spot-checking
Raymond Dalmau live revealed `991001` (a Pabellón-HOF mint, D-048) and
`1962` (the real archive profile) were the same person under two
canonical ids — exact birth-date match (Oct 27 1948), same team, same
span; `991001` carried zero distinguishing data. Merged into `1962`
(confidence -> `multi-source`, `991001`'s citations folded into
`source_url`); `991001` deleted everywhere (grepped first — zero other
references anywhere in the repo). Also found and fixed, same pass: the
deployed site's `web/data/players/*.json` had gone 3 identity-pipeline
phases stale (last committed 2026-09-09, three later phases never
propagated) — full rebuild swept, live-verified byte-for-byte, and a
new `.githooks/pre-commit` hook now blocks a future commit from
shipping that gap again (tested against the real failure mode before
trusting it).

## [DATA] — the marking itself

No new data plumbing needed: `hydrate()` already builds `MVP_ID`
(`season -> bsnpr_id`, one MVP per year) from `web/data/index/mvp.json`
for an unrelated existing feature (`buildFinalsByYear`'s MVP column).
`cmpSeasonSelect()`'s per-season `<option>` loop now checks
`MVP_ID[c.season]===d.id` — real, direct equality against the specific
player's own id, never a name guess — and appends `" — MVP"` to the
label when true. Because the check only ever runs over `c` values in
that player's own fetched `career[]`, it structurally can't mark a
"span-only" match (one of the 14 resolved-but-no-real-row cases) —
those seasons simply aren't in the dropdown's option list at all, so
there's nothing to (mis)mark.

## [VERIFICATION]

Same jsdom-against-the-real-built-page method as Part 1 (no live
browser tool this session). Confirmed: `MVP_ID` has 36 entries (up from
13 before the id_map fix); Raymond Dalmau's season dropdown marks
exactly 1968/1969/1972 as MVP and no other year; Christian Dalmau's
marks exactly 2004. Re-ran Part 1's full original test suite (candidate
widening, career-vs-career preset, season switching, archive-only mixed
comparison, the 2022+ note) — no regressions, `PALL` count correctly
reflects the Dalmau merge (3356, was 3357). `make verify` (339,243) +
`make test` (191) green.
