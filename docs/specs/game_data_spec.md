# Game-level data — spec

<!-- H2 structure. PHASE_3E, 2026-09-08. -->

Cross-refs: [`../coverage_games.md`](../coverage_games.md) (per-script coverage),
[`identity_spine_spec.md`](identity_spine_spec.md) (the `player_raw` → `bsnpr_id`
join), `data/interim/cdx_games_inventory.csv`.

---

## [PURPOSE]

Wayback archived the retired bsnpr.com game engine — box scores 2001–2014 and
play-by-play 2001–2004. This phase enumerates it, fetches it in tranches gated
at **500 distinct captures per tranche**, and parses the box scores into
per-player, per-game rows with the identity-spine `bsnpr_id` joined on.

---

## [DECISION]

**1. Five scripts, ~10,548 distinct captures.** (`docs/coverage_games.md`.)

| script | distinct | window | content |
|---|--:|---|---|
| `pogamestat.asp` | 4059 | 2007–2014 | per-player final box score |
| `a2gamestatpbp.asp` | 3093 | 2001–2004 | play-by-play (per-quarter) |
| `gameinfo.asp` | 1457 | 2007–2009 | game metadata (venue / coaches / officials), **no player stats** |
| `boxscore.asp` | 1075 | 2007–2009 | per-player box score (the live-updating page) |
| `gamestatwide.asp` | 864 | 2001–2004 | per-player box score (pre-2007) |

**2. Tranche = (script, capture-year); hard gate at 500.**
`src/fetch_games.py` refuses any tranche over `MAX_TRANCHE=500` — those need a
coverage report + owner approval, then `--force-year` (still one script-year at
a time). Every script exceeds 500 in total; the fetchable-now tranches are the
capture-years under 500 (`coverage_games.md` lists them).

**3. Game id = `r=BS<NN><seq>`, season = 1980 + NN.** `BS21001` → 2001,
`BS28152` → 2008. Verified against capture years.

**4. `read_html(flavor="bs4")`.** The engine leaves `<b>` tags unclosed inside
`<td><font>` cells; the default lxml flavor drops or merges those tables, bs4
recovers them.

**5. Box-score shot cells:**
- `gamestatwide.asp` — `CC3I-CC3A` / `CCI-CCA` / `TLI-TLA` = **attempted-made**
  (verified: `2·FG2 + 3·FG3 + FT == PTS` holds on every parsed row).
  `CCI-CCA` is **2-point** field goals only; `CC3I-CC3A` is 3-pointers. Stored
  as `fg2m/fg2a` + `fg3m/fg3a` (not a combined "FG").
- `boxscore.asp` / `pogamestat.asp` — separate `2 Points` / `3 Points` /
  `Free Throws` blocks, each `M A %` = **made-attempted**. Rebounds `O D To`.

**6. `player_raw` → `bsnpr_id` via the identity spine (D1).** Same rule as
`parse_players`: normalized-name / order-insensitive-key alias match, kept only
when exactly one candidate has that season in its `player_career_seasons` span.
No unique corroborated match → `bsnpr_id` blank (never a guess). Current
resolution ~22% — limited by the spine's pre-2007 coverage
(`identity_spine_spec` Q3), not by the matcher.

---

## [RATIONALE]

- **Why `gamestatwide.asp` went first.** 864 distinct, every capture-year
  tranche ≤ 500 (179 / 395 / 284 / 6) → **fully ungated**. It is the *only*
  pre-2007 per-player box-score source and it parses cleanly (0 arithmetic
  errors on the first 80 games). `boxscore.asp` / `pogamestat.asp` overlap it
  for 2007–2009 and their early "live" captures cram both teams' box into one
  HTML cell — messier, and gated (>500 in 2007).
- **Why `gameinfo.asp` is deprioritised.** Metadata only (venue, coaches,
  referees) — no player or team stats. Useful later to attach venue/officials
  to `game_results`, not a box-score source.
- **Why `a2gamestatpbp.asp` (PBP) is a separate effort.** 3093 quarter-captures
  (≈ 4 per game), a `Cuarto | Reloj | Jugada | Local | Visitante | Diff` play
  log — a different parse target and a different table (`game_plays`), 2002/2003
  both gated. Deferred.

---

## [ALTERNATIVES_REJECTED]

- **Fetch all 10.5k captures now** — rejected; the 500 gate + Wayback's throttle
  (~1 capture / 30–60 s) make it a multi-day job. Tranche it, report, approve.
- **Guess `bsnpr_id` from name + team alone** — rejected (D1). Season-in-career
  corroboration or nothing.
- **One combined `fg` column** — rejected; the source separates 2P and 3P, and
  collapsing them loses the shot-type split that makes the box useful.
- **Parse the crammed "live" `boxscore.asp` 2007 captures with regex on the
  mega-cell** — deferred; `pogamestat.asp` has the same games in a cleaner
  final-box layout for most of 2007–2009.

---

## [INTERFACES]

### `src/enumerate_games.py` (`make enumerate-games`)
Slices `cdx_root_all.json` for the 5 scripts. → `data/interim/cdx_games_inventory.csv`
(one row per distinct digest: script, timestamp, digest, `r`, `cuarto`,
capture_year, url) + `docs/coverage_games.md`.

### `src/fetch_games.py` (`make fetch-games`)
`--script`, `--year`, `--force-year`. `MAX_TRANCHE=500`. One GET per digest,
`id_` suffix, `polite_get`, progress every 25. → `data/raw/games/<script>/`,
`data/interim/fetch_manifest_games.csv` (merged across runs, `gated` column).

### `src/parse_games.py` (`make parse-games`)
Pure helpers unit-tested (`_season_from_rid`, `_num_pair`, `_reb_pair`,
`_split_jugador`). Runs on whatever is fetched.
- `data/clean/game_results.csv` — game_id, season, date, script, team_a/b_raw,
  score_a/b, quarters_a/b, provenance.
- `data/clean/game_box_player.csv` — game_id, season, date, team_raw, jersey,
  player_raw, **bsnpr_id**, minutes, fg2m/fg2a, fg3m/fg3a, ftm/fta, oreb, dreb,
  reb, ast, stl, blk, pf, tov, pts, provenance.

`verify_clean.py` → `verify_games()`: provenance per row; `2·FG2 + 3·FG3 + FT ==
PTS` on every full row; made ≤ attempted; every `bsnpr_id` is real; every game
with player rows has a `game_results` row.

---

## [OPEN_QUESTIONS]

1. **The gated tranches** — need a coverage report + approval each:
   `boxscore.asp` 2007 (814); `gameinfo.asp` 2007 (944) + 2008 (509);
   `pogamestat.asp` 2007 (1329) + 2008 (774) + 2009 (935);
   `a2gamestatpbp.asp` 2002 (1462) + 2003 (1555).
2. **Ungated, queued** (≤500, no approval needed, just time):
   `pogamestat.asp` 2010–2021 (1021 across 6 years), `boxscore.asp` 2008–09
   (261), `a2gamestatpbp.asp` 2001 + 2004 (76).
3. **`bsnpr_id` resolution is ~22%** — the pre-2007 identity gap
   (`identity_spine_spec` Q3). The unresolved `player_raw` values here are a
   good candidate seed list for extending the canonical player table.
4. **`game_results` team ↔ franchise** — `team_a_raw` is a city name; join via
   `city_franchise_map` in a follow-up (needs the season-aware logic from
   `reconcile.py`).
5. **PBP** (`a2gamestatpbp.asp`) — own parse target (`game_plays.csv`),
   deferred.
6. **`gameinfo.asp`** — venue / coaches / officials to enrich `game_results`,
   deferred.
7. **Dedup vs `player_season_stats_2001_2004`** — the game box scores summed per
   player-season should reconcile against the `equiposstat` season totals
   (PHASE_3C). A cross-check worth running once a season is fully fetched.
