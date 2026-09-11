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
