# SESSION STATE — TIER 3
<!-- Authoritative for current state and task priority. Update at every phase exit. -->

**SESSION:** 002 — PHASE_3 / 3B / 3C / 3D / 4 / 3E (continues 001)
**DATE:** 2026-09-08
**MODEL:** Claude Sonnet 5 (claude-sonnet-5) via Claude Code

Session 001 (2026-09-07): PHASE_1_ENUMERATE + PHASE_2_FETCH. Env bootstrapped,
Wayback CDX enumerated (central finding negative — see below), 193 snapshots
fetched to `data/raw/`.

Session 002:
- PHASE_3_PARSE (committed 4ca04f2) — 193 snapshots → provenance-complete `data/clean/`.
- PHASE_3B_PROBE_ARCHIVE (committed 21f1a5f) — probed 4 more scripts; found a
  pre-2007 root-level URL scheme the PHASE_1 enumeration missed.
- PHASE_3C_INGEST_PRE2007 (committed a3b792a) — enumerated `bsnpr.com/*`,
  ingested the ≤500 pre-2007 tranches. 1948–2004 scoring champions + awards,
  2000–2003 player season stats/leaders now in `data/clean/`. Box-score / PBP
  scripts found + gated.
- PHASE_3D_IDENTITY_SPINE (committed 0d0d12d + refresh) — D1 canonical player
  table: **3,303 players** (1,076 with a full profile), league ids,
  accent-stripped names, ~25k aliases, **423 season-corroborated id-map links**,
  828-row review queue. Tranche B fetch (1,078 profiles) finished.
- PHASE_4_RECONCILE (ac4a23e + d7c3024 + cd8ef54) — reconciled champions +
  scoring vs the Wikipedia seed. 89/98 champion seasons `agree`. Owner resolved
  4 of 5 conflicts; es.wikipedia retested and **fetchable** (F3 resolved) — used
  to verify Brujos→Osos and disprove wiki support for Grises→Criollos.
  `reconcile_conflicts.csv` = 2 rows (1945/D5; Criollos founding year).
- PHASE_3E_GAME_DATA (d421922 · e94fec9 · 640964e · a041a60 · 891fc12 · 2d1928c)
  — enumerated the 5 archived game scripts (10,548 distinct captures); gated
  fetcher (hard 500/tranche); box-score + play-by-play parsers. Fetch is a slow
  throttled multi-day job, run one tranche at a time (PC6), tracked in
  PHASE_3E_FETCH_REMAINING below.

---

[SESSION_STATE]

**Pipeline: 12 `make` targets** (`Makefile`), each idempotent:
`enumerate` → `fetch` → `parse` → `verify`  (PHASE_1–3, `/estadisticas/` engine)
`enumerate-root` → `fetch-pre2007` → `parse-pre2007`  (PHASE_3C, root scheme)
`fetch-players` → `parse-players`  (PHASE_3D identity spine)
`reconcile`  (PHASE_4)
`enumerate-games` → `fetch-games` → `parse-games`  (PHASE_3E game data)
`make verify` runs `src/verify_clean.py` — one gate over all of `data/clean/`.
`make test` — 125 pytest (all pure helpers). Last full run: **verify green
(326,175 checks); 125 tests pass.**

**`data/clean/` — the deliverable, 25 CSVs, all PC3-complete
(`confidence` ∈ {verified, single-source, disputed}). Provenance columns on
every row: `source_id`, `source_url`, `retrieved_at`, `confidence`.**

Championships / franchises:
- `champions_from_bsnpr.csv` 92 rows 1930–2020 (bsnpr ledger, city-based, coach).
- `champions_reconciled.csv` 98 seasons — seed↔bsnpr join; 89 `agree` (87 →
  `verified`, i.e. two independent sources concur), 3 conflict, 1 no_champion
  (1953/D6), 1 bsnpr_only (1942-1943/D3), 6 seed_only (2021–26).
- `scoring_champions_reconciled.csv` 68 seasons 1948–2021; `metric_era` per D4;
  1971 & 1974 = `dual_metric_d4` (both winners recorded, owner-resolved).
- `reconcile_conflicts.csv` **2 rows** — 1945 champion (D5, es.wiki
  self-contradicts) + Criollos founding year (1969 en.wiki vs 1976 seed).
- `franchises.csv` (33), `franchise_events.csv` (8 D2 events), `city_franchise_map.csv`,
  `club_code_map.csv` (5-char + 2-letter codes → franchise_id).
- `historic_scoring_champions.csv` 58 rows **1948–2004** (games/total/ppg),
  `historic_awards.csv` 135 rows MVP/Rookie/DPOY **1958–2004**.

Player season stats / leaders:
- `player_season_leaders.csv` 1250 rows, 12 seasons (1986 + 2007–21 minus
  2011/15/16/17), 11 categories, ranks 1–10. `player_raw`/`club_raw` verbatim.
- `player_season_leaders_2000_2002.csv` 403 rows, 9 categories, serie-split.
- `player_season_stats_2001_2004.csv` 503 player-seasons (equiposstat, 2001–03,
  14 teams — only pre-2007 player-level source) + `team_season_totals_2001_2004.csv`.
- `seasons_stats_tracked.csv` (PC2 era signal), `leader_coverage_gaps.csv` (PC4).

Identity spine (D1):
- `players_canonical.csv` **3,303 players** keyed by the league's own
  `bsnpr_id`, 1,076 with a full profile, 1,988 with a birth year; accent-stripped
  `normalized_name`.
- `player_aliases.csv` ~25k (id, alias, 9 alias types incl. `initial`,
  `given_first_only`, `nickname`).
- `player_career_seasons.csv` (from jugador.asp), `player_id_map.csv` 423
  season-corroborated obs→id links, `data/interim/player_review_queue.csv` 828
  rows (346 no name match, 361 season outside career span, 106 multi-candidate,
  15 same-name ambiguity — **no fuzzy match ever enters the id map**).

Game data (PHASE_3E, fetch ongoing — numbers grow as tranches land):
- `game_results.csv` ~1,287 games; `game_box_player.csv` ~39,669 player-game
  rows; `game_plays.csv` ~11,106 plays.
- **Box-score `bsnpr_id` resolution by era: pre-2007 4,152/15,941 = 26%; 2007+
  17,599/23,728 = 74%.** The gap is the identity spine's pre-2007 hole
  (`identity_spine_spec` Q3), NOT the matcher — every match is season-corroborated.
- Box seasons: **2001–2003 + 2008–2013**. `box_check` column flags source
  pts-mismatch rows (4/39,669 = 0.01%, PC4 — flagged not hidden).
- **PBP event_type counts** (11,106 plays, 2001 + partial 2003): unclassified
  2,483 · rebound 2,065 · made_2 1,606 · miss_2 1,198 · assist 1,025 · miss_3
  790 · turnover 630 · made_3 433 · steal 398 · team_rebound 201 · jump_ball
  140 · timeout 137. ~78% classified; `jugada_raw` verbatim; `actor_raw` is a
  bare surname (PBP's own format).

**Central negative finding (S001, PC4, B2 — partly reopened, see below):** the
1957–2004 per-season `/estadisticas/lideres.asp?anio=YYYY` pages Wikipedia
cites were never archived with content. BUT PHASE_3B/3C found a **root-level**
pre-2007 URL scheme (`lideres2001.asp`, `lidereshistoricos.asp`,
`equiposstat.asp`, `gamestatwide.asp`, `a2gamestatpbp.asp`, …) that WAS
archived — hence the 1948–2004 scoring champs, 2000–2003 player stats, and the
2001–2003 box scores + PBP now in `data/clean/`.

**Cross-validations that held:** 1986 scoring leader parsed = "Torres, George"
29.8 ppg = seed exactly. 1986 `campeonatos.asp` scoring champ = seed
`bsn_scoring_champions.csv` 1986. 87/98 champion seasons independently
corroborate seed↔bsnpr. Box-score invariant `2·FG2 + 3·FG3 + FT == PTS` holds
on 39,663/39,669 rows; the 4 `pts_mismatch` are source data-entry errors (2 rows
have a missing cell), flagged in `box_check`, never rewritten.

Full detail: `docs/coverage_wayback.md`, `docs/specs/wayback_ingest_spec.md`.

---

[TASK_QUEUE]

### PHASE_1_ENUMERATE — COMPLETE (2026-09-07)

Scope was enumeration only. No snapshots bulk-fetched.

- T1.1 — DONE. `.venv` bootstrapped (Python 3.14, pandas 3.0.5). `.gitignore`,
  `requirements.txt`, `.env.example` were already scaffolded; `Makefile` gained
  `samples` target. Repo was already a git repo. Not committed (P4).
- T1.2 — DONE. `src/wayback_cdx.py`. Runs **two** CDX queries: the collapsed one
  from the task text, plus an un-collapsed one for accurate per-capture status
  (see WORKING_MEMORY decision). Raw JSON in `data/raw/cdx/` (PC5). Polite
  backoff (PC6).
- T1.3 — DONE. `data/interim/cdx_inventory.csv`, 1562 rows. Added `query` +
  `parametrized` columns and record the real `.asp` script name (not just
  lideres/campeonatos/other) — the archive holds ~20 distinct scripts.
- T1.4 — DONE. `docs/coverage_wayback.md`. Headline: **1/48 in-window
  `lideres.asp` seasons usable** (only 1986). Per-decade + per-season tables,
  out-of-window captures, and a full table of the other archived scripts.
- T1.5 — DONE, **with a documented deviation.** The task asked for 1960s/1980s/
  2000s `lideres.asp` snapshots. The 1960s–70s (and most of 1957–2004) were
  never archived with content. The 3 probes fetched instead:
  `lideres.asp?anio=1986` (2017 — the only archived historic season),
  `lideres.asp` bare (2007), `campeonatos.asp` bare (2007). Still exactly three.
  Rationale in `src/fetch_samples.py` docstring + the spec.
- T1.6 — DONE. `docs/specs/wayback_ingest_spec.md` per H2. Observed table
  shapes, the 1986-vs-2007 stat-category drift (blocks/steals/TO/off-reb
  untracked in 1986), column-signature parse strategy, 8 open questions.
- T1.7 — DONE (this edit).

**Phase exit:** status delivered, paused (P6). PHASE_2 scope below needs
rewriting against the new findings before it starts.

### PHASE_2_FETCH — COMPLETE (2026-09-07). Approved by owner ("run tranches A-C").
Original plan (per-season `anio=` backfill 1957–2004) was dead — content never
archived. Revised scope executed, all inside PC6, 193 distinct digests, 0 fails:

- T2.1 — DONE. `src/fetch_wayback.py`: reads `cdx_inventory.csv`, one HTTP
  request per unique content digest (earliest capture as representative),
  `id_` raw suffix, `polite_get` backoff. Idempotent — re-run = 0 fetched, 193
  cached (PC5). `make fetch`. 4 new unit tests (23 total pass).
- T2.2 — DONE. Tranche A: 80 `campeonatos.asp` 200-captures → **79 HTML files**
  in `data/raw/campeonatos/` (+ `.meta.json` each).
- T2.3 — DONE. Tranche B: 101 bare `lideres.asp` 200-captures → 96 files.
- T2.4 — DONE. Tranche C: 18 parametrized `lideres.asp?...` 200-captures → 18
  files. All in `data/raw/lideres/` (114 files total). Some C entries are
  `vida=2` (career view) or `grupo=BS19` (different group) — flag in parse.
- T2.5 — DONE (this edit).

Manifests (every capture → its local file) in `data/interim/fetch_manifest_{campeonatos,lideres}.csv`
— tracked in git; the raw HTML under `data/raw/` is gitignored (~10 MB).

Spot-check: all sampled files parse with `read_html`. campeonatos = 1 content
table, grew 76 rows (2007 capture) → 92 rows (2021). lideres = 11–15
category tables matching the `# | Jugador | JJ` signature.

**Deferred** (owner said A-C only): probing the other ~18 archived scripts
(`lideres_e.asp`, `enciclopedia.asp`, `finales.asp`, `mvp.asp` — spec open Qs 1–4).

### PHASE_3_PARSE — COMPLETE (2026-09-08)

- T3.1 — DONE. `src/parse_wayback.py` (`make parse`). Pure, no network,
  idempotent. Column-signature category detection (spec pt 3), not table index.
- T3.2 — DONE. Tranche A → `champions_bsnpr_long.csv` (6486 rows, every capture)
  → `champions_from_bsnpr.csv` (92 seasons). 1953 `*` → `no_champion` + note
  (resolves spec Q5 / D6). 1984 "COPA OLIMPICA - CANOVANAS" annotation split
  off. Multi-coach cells: read_html collapsed the separating spaces, so the
  split point is lost — kept verbatim, `coach_flag=multi?` on the 4 affected
  rows (1967/1972/1975/1981). Cross-capture disagreement → `disputed` (1936,
  1968; plus 1945 per D5).
- T3.3 — DONE. Tranches B/C → `player_leaders_long.csv` (10345 rows) +
  `leader_capture_index.csv` → `player_season_leaders.csv` (1250 rows).
  `Jugador` parsed to `player_raw`/`club_raw` verbatim (D1 later). Dedup:
  regular-season captures only (`serie` value 1), latest per (season, category)
  — resolves spec Q7. `season_complete` heuristic (spec Q6). Encoding via
  `decode_html` (spec Q8).
- T3.4 — DONE. `seasons_stats_tracked.csv` (PC2) + `leader_coverage_gaps.csv`
  (PC4). 2011/2017 = playoff_only, 2015/2016 = not_archived.
- T3.5 — DONE. `src/verify_clean.py` (`make verify`), 6375 assertions, green.
  `tests/test_parse_wayback.py` — 38 new unit tests (61 total pass).
- T3.6 — DONE (this edit). Spec [INTERFACES]/[OPEN_QUESTIONS] updated.

**Phase exit:** status delivered, paused (P6). Nothing committed (P4).

**Deliberately deferred out of PHASE_3** (belongs in PHASE_4, logged as spec
Q9–Q12): city→franchise mapping (D2/D5); the 2 `vida=2` career-view captures;
the 2 `grupo=BS19` captures; extending the franchise-city vocabulary for the 3
`review`-flagged champion rows.

### PHASE_3B_PROBE_ARCHIVE — COMPLETE (2026-09-08, owner-requested)

Findings in full: `docs/specs/archive_probe_spec.md`. Headline:

| Script | Verdict |
|---|---|
| `enciclopedia.asp` | **Full ingest** — all-time player directory, 2368→3284 players, name + birth date + `/jugadores/jugador.asp?id=N` link. D1 backbone. |
| `estadisticas.asp` 2001–02 cluster | **Full ingest** — standings + a **root-level pre-2007 URL scheme** (`lideres2001.asp`, `lideres2000.asp`, `lidereshistoricos.asp`, `equiposstat.asp`) that WAS archived with content. `lidereshistoricos.asp` = season scoring leaders **1948→2001** (JJ/P-A/PPJ). |
| `lideres_e.asp` | Low value — team-level ("Líderes por Equipo"), not refuerzos; redundant with `lideres.asp` at coarser grain. |
| `livestats.asp` | **Dead** — 850-byte widget stubs / 404; third-party live content never archived. Does not help B1. |

**This partially reverses session-001's headline.** "Pre-2007 leader pages never
archived" is true *for `/estadisticas/lideres.asp?anio=`*. The 2000–2002 site
served the same data from **root-level URLs** (`bsnpr.com/lideres2001.asp` …)
never seen by the PHASE_1 CDX query (pattern was `bsnpr.com/estadisticas*`).
CDX confirms: `lideres2001.asp` 11×200, `lideres2000.asp` 7×200,
`lidereshistoricos.asp` 6×200, `equiposstat.asp` 307×200 (2001–2007),
`bsnpr.com/jugadores/*` 1680×200 (2004–2026).

- T3B.1–T3B.3 — DONE. `src/probe_archive.py`; 22 sample captures in
  `data/raw/probe/`; spec written.
- T3B.4 — DONE (this edit).

**Phase exit:** status delivered, paused (P6). Nothing committed (P4).

<details><summary>original scope</summary>

Scope: sample-probe the archived `/estadisticas/` scripts left unexamined after
PHASE_2 (spec open Qs 1–4 + NEXT_ACTIONS #4). **Sample only — no bulk fetch, no
parser, no clean output.** Determine what each script's pages contain and
whether they hold player-level or pre-2007 data, to decide if any deserves a
full ingest phase later.

- T3B.1 — Fetch 3–5 distinct-digest captures each, spread across the archived
  date range, via `polite_get` + `id_` suffix, into `data/raw/probe/`
  (gitignored). Targets:
  - `enciclopedia.asp` — 5: 20070417, 20090131, 20120621, 20140221, 20210901
    (all param-less; 79 distinct 200s, 2007–2021).
  - `lideres_e.asp` — 5: 20070509 (bare), 20070505 (`grupo=BS26&serie=1`),
    20120507 (`grupo=BS19&serie=1&anio=2012`), 20140325 (`anio=2014`),
    20200601 (`anio=2019`). `_e` hypothesis: refuerzos/import-player leaders.
  - `livestats.asp` — 4: 20130428 (bare), 20130831 (`?live=1&onlylive=1`),
    20140420 (bare, later digest), 20170708 (latest). Hypothesis: Genius
    Sports / FIBA LiveStats embed — may expose a box-score endpoint (feeds B1).
  - `estadisticas.asp` 2001–2002 cluster — 5: 20010803075616 (`?t=3`, oldest
    snapshot in the whole inventory), 20011124 (bare), 20020616014253 (bare),
    20020616014713 (`estadisticas2001.asp`), 20021005 (`estadisticas.asp`).
    Only possible pre-2007 primary source in the archive — verify or write off.
- T3B.2 — Inspect each: table shapes, whether rows are player-level, the season
  each page represents, encoding, any box-score / match-id / endpoint hints.
- T3B.3 — Findings to `docs/specs/archive_probe_spec.md` (H2 structure). One
  verdict per script: {full ingest phase warranted | low value | dead}.
- T3B.4 — Update spec Q1–Q4, session.md, NEXT_ACTIONS.

Not in scope: parsing any of these into `data/interim/` or `data/clean/`;
`finales.asp` / `mvp.asp` / `posiciones.asp` (still deferred — the four above
are the owner's list).
</details>

### PHASE_3C_INGEST_PRE2007 — COMPLETE for the ≤500 tranches (2026-09-08)

Full detail: `docs/specs/pre2007_ingest_spec.md` + `docs/coverage_root.md`.

- T3C.1 — DONE. `src/enumerate_root.py` (`make enumerate-root`). CDX
  `bsnpr.com/*`: 135,005 captures, 133,454 outside `/estadisticas/`. Persisted
  inventory = the ~34k stats/game/player-script subset (rest is news/forum/image
  noise). Raw CDX JSON cached (46 MB, gitignored).
- T3C.2 — DONE. Coverage delivered (`coverage_root.md`) before any >500 fetch.
- T3C.3 — DONE. `src/fetch_pre2007.py` (`make fetch-pre2007`), `MAX_TRANCHE=500`
  hard gate. Fetched 315 distinct captures across 8 scripts, 0 failed (2
  `equiposstat` DB-error pages). `data/raw/pre2007/`, manifest tracked.
- T3C.4 — DONE. `src/parse_pre2007.py` (`make parse-pre2007`). 5 clean outputs:
  - `historic_scoring_champions.csv` (58 rows, **1948→2004**, games+total+ppg;
    `metric_era` flips 1970/71 per D4; 1952 Feliciano/Santori = 2 `disputed`
    rows) + `historic_awards.csv` (135 rows — MVP/ROY/DPOY, **1958→2004**).
  - `player_season_leaders_2000_2002.csv` (403 rows, 9 categories, serie-split;
    `lideres2000` is surname-only — D1 note).
  - `player_season_stats_2001_2004.csv` (503 player-seasons, 2001–2003, 14
    teams — the only pre-2007 **player-level** stat source) +
    `team_season_totals_2001_2004.csv` (38 rows).
  - root `campeonatos.asp` / `lideres.asp` NOT re-parsed (duplicate the
    `/estadisticas/` engine PHASE_3 already did).
- T3C.5 — DONE. `verify_pre2007()` added (13,410 assertions, green); 8 new unit
  tests (79 total pass); spec + session.md updated.

**GATED — reported, NOT fetched (owner approval, each >500 distinct):**
`jugador.asp` **5986** (per-player pages — D1 spine w/ `enciclopedia.asp`);
`pogamestat.asp` 4059, `a2gamestatpbp.asp` 3093, `gameinfo.asp` 1457,
`boxscore.asp` 1075, `gamestatwide.asp` 864, `pogamestatwide2.asp` 512 (**box
scores + play-by-play, 2001–2021 — a roadmap-scale finding, partial answer to
B1**); `jug05.asp`/`jugador05.asp` 600 each.
Fetchable without a new gate (≤500, not done this turn): `playbyplay.asp` 460,
`equipo.asp` 489, `informe.asp` 175, `print_jugador.asp` 203.

**Phase exit:** status delivered, paused (P6). Nothing committed (P4).

### PHASE_3D_IDENTITY_SPINE — COMPLETE (2026-09-08; tranche B finished)

Implements D1. Full detail: `docs/specs/identity_spine_spec.md`.

- T3D.1 — DONE. `src/fetch_players.py` (`make fetch-players`). Tranche A =
  `enciclopedia.asp` (77/78). Tranche B = `/jugadores/jugador.asp?id=N`, one
  latest capture per id — **1,078/1,079 fetched** (1 transient fail), ~3 h under
  Wayback throttle.
- T3D.2 — DONE. `src/parse_players.py` (`make parse-players`). Outputs
  (final, post-tranche-B):
  - `players_canonical.csv` — **3,303 players**, league `bsnpr_id`;
    `canonical_name`, accent-stripped `normalized_name`, `birth_date`
    (`1/1/1900` → null), `birth_year` (1,988), + position / nationality /
    career-span for **1,076** with a profile.
  - `player_aliases.csv` — ~25k rows, 9 alias types.
  - `player_career_seasons.csv` — from `jugador.asp` season tables.
  - `player_id_map.csv` — **423** observation→`bsnpr_id` links, all
    season-corroborated (`match_method=name+season_in_career`).
  - `data/interim/player_review_queue.csv` — **828** rows: 346 no canonical
    name match (pre-2007 players absent from the encyclopedia), 361 season
    outside the profile's career span, 106 multi-candidate uncorroborated, 15
    genuine same-name ambiguity. **No fuzzy match ever enters the id map (D1).**
- T3D.3 — DONE. `verify_players()`; 12 new unit tests. `make verify` green.
- T3D.4 — DONE. Re-parsed + re-verified after tranche B completed.

**Phase exit:** identity spine complete. Paused (P6).

### PHASE_3E_GAME_DATA — CORE DONE; fetch continuation queued below (2026-09-08)

Owner instruction: enumerate the 5 game scripts, report distinct counts by
script/year, fetch in tranches with a **hard 500 gate per tranche**, parse to
`data/clean/` with provenance, join player rows to `player_id_map`. Report
coverage before any tranche over 500. Spec: `docs/specs/game_data_spec.md`,
`docs/coverage_games.md`.

- T3E.1 — DONE. `src/enumerate_games.py` (`make enumerate-games`): 10,548
  distinct captures across 5 scripts. `data/interim/cdx_games_inventory.csv` +
  `docs/coverage_games.md` (per-script per-capture-year table).
- T3E.2 — DONE. Probed all 5 structures (`data/raw/games_probe/`):
  - `gamestatwide.asp` (864, 2001-04) — pre-2007 per-player box scores.
  - `boxscore.asp` (1075, 2007-09) / `pogamestat.asp` (4059, 2007-14) — modern
    per-player box scores (near-identical layout; pogamestat = final).
  - `gameinfo.asp` (1457, 2007-09) — game metadata only (venue/coaches/refs),
    no player stats — LOW value.
  - `a2gamestatpbp.asp` (3093, 2001-04) — play-by-play, `Cuarto|Reloj|Jugada`.
- T3E.3 — DONE (fetch in progress). `src/fetch_games.py` (`make fetch-games`),
  `MAX_TRANCHE=500` hard gate, tranche = (script, capture_year). `gamestatwide.asp`
  (864, all 4 year-tranches ≤500) fetching in background (~134/864 at commit).
- T3E.4 — DONE. `src/parse_games.py` (`make parse-games`) → `game_results.csv`
  + `game_box_player.csv`. `read_html(flavor="bs4")` (engine leaves `<b>`
  unclosed). Shot cells: gamestatwide `X-Y` = attempted-made, `CCI-CCA` = 2P
  only → stored `fg2*`/`fg3*` separately. **`2·FG2 + 3·FG3 + FT == PTS` holds
  on every parsed row** (0 mismatches). `player_raw` → `bsnpr_id` via the
  identity spine (season-in-career, D1) — ~22%, capped by the pre-2007 spine
  gap not the matcher.
- T3E.5 — DONE. `verify_games()` + `verify` for `game_plays`; 17 new unit tests
  (125 total pass); `docs/specs/game_data_spec.md`.
- T3E.6 — PBP parser (`parse_pbp` → `game_plays.csv`, committed e94fec9). Modern
  box parser fixed for the MultiIndex `boxscore`/`pogamestat` layout + line-score
  → `game_results`. `box_check` column flags source pts-mismatch rows
  (~0.02%, PC4 — flagged not hidden).

### PHASE_3E_FETCH_REMAINING — QUEUED (owner: "add to task queue", 2026-09-08)

The parser + verify are done and green; what's left is a slow, throttled,
sequential fetch (Wayback ~1 capture/30–60 s) that keeps getting killed by
session limits. **This entry is the resume contract — any session can pick it
up from disk.**

**Owner approvals on record:** `a2gamestatpbp.asp` **2002 + 2003** (PBP, no
substitute). **HELD by owner, do NOT fetch:** `pogamestat.asp` 2007/2008/2009,
`boxscore.asp` 2007, all of `gameinfo.asp` — until the owner sees the 2002–03
PBP contents.

**RESUME PROCEDURE** (run one tranche at a time, PC6 — never two fetchers at
once; the fetcher is idempotent, re-running skips what's on disk):
1. `.venv/bin/python -m src.fetch_games --script pogamestat.asp`   (ungated
   2010–21; auto-skips gated 2007–09)
2. `.venv/bin/python -m src.fetch_games --script boxscore.asp`     (ungated
   2008–09; auto-skips gated 2007)
3. `.venv/bin/python -m src.fetch_games --script a2gamestatpbp.asp --year 2001`
4. `.venv/bin/python -m src.fetch_games --script a2gamestatpbp.asp --year 2004`
5. `.venv/bin/python -m src.fetch_games --script a2gamestatpbp.asp --year 2002 --force-year`
6. `.venv/bin/python -m src.fetch_games --script a2gamestatpbp.asp --year 2003 --force-year`
7. After each: `make parse-games && make verify`, commit, **report to owner**.
`scratchpad/fetch_chain3.sh` chains steps 5–6 (2002 resume + 2003); it dies with
the session, restart it. **PC6 breach caught 2026-09-08:** a resumed session
left `fetch_chain2.sh` running while another started, so TWO fetchers were
hitting Wayback on the 2002 tranche at once. Both killed; `fetch_chain3.sh` is
the single replacement. Before restarting any chain: `ps aux | grep [f]etch_games`
and kill strays first.

**DISK STATE (updated 2026-09-08, single-stream fetch resumed):**
- `gamestatwide.asp` 864 ✅ · `pogamestat.asp` 1021 ✅ · `boxscore.asp` 261 ✅ ·
  `a2gamestatpbp.asp` 2001 (78 ✅) + 2004 (74 ✅) done;
  **2002 (~343/1462) RESUMING** (single chain `scratchpad/fetch_chain3.sh`,
  task `bzjo92jo3`); 2003 (~4/1555) queued after it.
- `data/clean/game_results.csv` 1,287 · `game_box_player.csv` 39,669 (26%
  resolved pre-2007, 74% 2007+, 55% overall) · `game_plays.csv` 11,106 plays
  (2001 = 8,771; 2003 = 2,335). These are committed at 2d1928c; the 2002/2003
  fetch will grow `game_plays` on the next parse.
- After 2002/2003 land: `make parse-games && make verify`, commit, report.
- STILL HELD by owner (do NOT fetch): `pogamestat` 2007/08/09, `boxscore` 2007,
  all of `gameinfo` (metadata only) — until owner reviews the PBP contents.

Parser notes for the resumer: `_season_from_rid` handles both id schemes
(`BS<NN>` pre-2007 = 1980+NN, `BS<YYYY>` 2007+); modern box columns mapped by
LABEL not position (2013 captures add FBP/PFT/PIP/SCP before PTS); pre-2007
`gamestatwide` shot cells are `att-made`, modern `boxscore`/`pogamestat` are
`made-att`, stored as `fg2m/fg2a` + `fg3m/fg3a` (2P and 3P kept separate);
`box_check` column flags the ~0.01% source pts-mismatch rows (PC4); `_tables`
uses lxml for modern boxes (3× faster), bs4 for gamestatwide (unclosed `<b>`).
The `2010-2021` capture-year `pogamestat` tranche actually holds **2009–2013
season** games (Jan-2010 crawls captured late-2009 games).

**GATED (>500 distinct, need explicit owner approval + `--force-year`):**
`boxscore.asp` 2007 (814); `gameinfo.asp` 2007 (944) + 2008 (509);
`pogamestat.asp` 2007 (1329) + 2008 (774) + 2009 (935);
`a2gamestatpbp.asp` 2003 (1555) — 2002 already approved + fetching.

### PHASE_4_RECONCILE — COMPLETE (2026-09-08, owner-requested)

Owner instruction: reconcile the parsed data against the seed CSVs. **For every
disputed row, present the conflict with both sources and leave it flagged — do
NOT pick a winner without asking.** Spec: `docs/specs/reconcile_spec.md`.

**Status: T4.1–T4.5 DONE. Owner resolved 4 of the 5 conflicts 2026-09-08.**
89/98 champion seasons `agree`; **`reconcile_conflicts.csv` now = 1 row (1945,
D5 — genuinely unresolved).** Game-pool + player-id-join deferred.

- T4.1 — DONE. `src/reconcile.py` franchise layer. `data/clean/`:
  - `franchises.csv` — franchise master (seed + the names that only appear in
    champion/scoring rows: Santos de San Juan, Club Nautico, Cocoteros de
    Tortuguero, Gallitos de la UPR, Vega Baja, …). `franchise_id` slug.
  - `franchise_events.csv` — D2 lineage as dated events (founded / renamed /
    relocated / merged / split / hiatus / dissolved), each with `confidence`
    + source; the messy ones (Brujos→Osos vs Atenienses/Osos-2014) flagged.
  - `city_franchise_map.csv` — (normalized_city, first_season, last_season) →
    franchise_id, for resolving the bsnpr city-only champion ledger. SAN JUAN
    1936 (Club Nautico) and 1945 (D5) explicitly flagged, not auto-resolved.
  - `club_code_map.csv` — lideres200x 5-char codes + equiposstat 2-letter `t=`
    codes + full names → franchise_id.
- T4.2 — DONE. `champions_reconciled.csv`, 98 seasons: 87 agree (→ `verified`),
  3 conflict (1936, 1945, 1968), 1 no_champion (1953, D6), 1 bsnpr_only
  (1942-1943, D3), 6 seed_only (2021–2026, past the bsnpr ledger). Conflict on
  one slot leaves the other slot resolved (1968 champion is filled; only the
  runner-up is flagged).
- T4.3 — DONE. `scoring_champions_reconciled.csv`, 68 seasons: 24 agree, 2
  conflict (1971, 1974), 31 historic_only (1948–65, 92–04), 11 leaders_only
  (2007+). `metric_era` per D4.
- T4.4 — DONE. `reconcile_conflicts.csv`. The reconcile found 5 disagreements;
  **owner resolved 4 on 2026-09-08** (`src/reconcile.py` `OWNER_RESOLUTIONS`,
  dated + auditable; seed CSVs untouched):
  - scoring 1971 & 1974 → `dual_metric_d4`, both winners recorded with metric
    labelled (ppg vs total points), confidence `verified` — the D4 boundary,
    not a conflict.
  - champion 1936 → `agree`, `club_nautico_san_juan` (city-vs-club naming; note
    also records bsnpr's own SAN JUAN/VEGA BAJA capture variance).
  - runner-up 1968 → `agree`, `cardenales_rio_piedras` (note: bsnpr captures
    disagreed internally over time, RIO PIEDRAS / PONCE).
  - **1945 → left `disputed`.** The only row left in `reconcile_conflicts.csv`.
- T4.5 — DONE. `verify_reconcile()` (40,114 checks green); 17 unit tests
  (108 total pass); `docs/specs/reconcile_spec.md` [OWNER_RESOLUTIONS].

**Phase exit:** champions + scoring reconciled; 4 conflicts owner-resolved.
Franchise lineage checked against es/en.wikipedia (F3 resolved — es.wiki IS
fetchable): Brujos→Osos = `verified`; Grises→Criollos = unverified (no wiki
support); Santos de San Juan = distinct, unresolved.
**`reconcile_conflicts.csv` = 2 rows** (1945 champion / D5; Criollos founding
year 1969 vs 1976). Paused (P6).

NOT this phase (reconcile_spec Q4/Q6/Q7): game-pool rebuild; applying
`player_id_map` to the observation tables (waits on tranche B); career-leader /
records reconcile.

### PHASE_5_APP_SYNC — queued, do not start
Generate the app's hardcoded JS data blocks in `app/bsn_archivo.html` from
`data/clean/*.csv` instead of hand-maintaining them. Today the CSVs and the app
are two independent copies of the same data that drift apart on every edit
(see B4).

Blocked on a P2 decision that needs its own spec file
(`docs/specs/app_data_sync_spec.md`) before any work starts: **build-time
codegen** (a script rewrites the `<script>` data blocks in place; app stays
single-file, no runtime deps — PC7) **vs. runtime loading** (app `fetch()`s the
CSVs; simpler pipeline but adds a load step and a local-file-origin problem for
a `file://` open). Codegen is the presumed answer under PC7 but the call is the
owner's. Do not touch `app/bsn_archivo.html` until that spec is approved.

---

[BLOCKERS]

- B1 — **Manual, user-only — but partly answered by PHASE_3C.** The bsnpr.com
  DevTools recon (roadmap Phase 0) was to find the box-score endpoint. PHASE_3C's
  `bsnpr.com/*` enumeration found `boxscore.asp` (1075 distinct, 2007–2009),
  `pogamestat.asp` (4059, 2007–2021), `a2gamestatpbp.asp` (3093, 2001–2004 PBP),
  `gameinfo.asp` (1457) **archived in Wayback**. A box-score/PBP ingest phase is
  now viable from the archive alone. The live DevTools recon still adds value
  for post-2021 and the current API, but is no longer the only path.
- B2 — **PARTIALLY REOPENED by PHASE_3B (2026-09-08).** The Phase-1 verdict —
  zero coverage of `/estadisticas/lideres.asp?anio=YYYY` for 1957–2004 — still
  stands. BUT the 2000–2002 site served leader data from **root-level URLs**
  (`bsnpr.com/lideres2001.asp`, `/lideres2000.asp`, `/lidereshistoricos.asp`,
  `/equiposstat.asp`) that the Phase-1 CDX pattern (`bsnpr.com/estadisticas*`)
  never enumerated — and those WERE archived with content (CDX-confirmed 200s,
  2001–2007). `lidereshistoricos.asp` carries season scoring leaders **1948→
  2001**. So: 2000–2001 player season leaders + a 1948–2001 historical-leaders
  compilation ARE recoverable from Wayback. 2002–2006 season-leader gap partly
  addressable via `equiposstat.asp` (307 caps). Box scores still need the
  newspaper track. See `docs/specs/archive_probe_spec.md`. Ingest = PHASE_3C.
- B3 — **RESOLVED.** Owner approved the revised Phase 2 ("run tranches A-C");
  executed and complete 2026-09-07. The newspaper/Federación track remains a
  parallel human-side effort, not a blocker.
- B4 — **`data/clean/` and `app/bsn_archivo.html` are two unsynchronized copies
  of the same data.** The app carries its dataset as hand-written JS literals;
  the CSVs are edited independently. Every data change has to be made twice and
  they already disagree in places. PHASE_5_APP_SYNC fixes this, but the
  codegen-vs-runtime-loading choice is a **P2 architectural decision requiring a
  spec file** (`docs/specs/app_data_sync_spec.md`) before any change to the app.
  Until then, treat the CSVs as the source of truth and the app as stale.

---

[WORKING_MEMORY]

Decisions made this session:
- **D-001 — two CDX queries, not one.** The task text specifies
  `collapse=urlkey`, which keeps one arbitrary capture per URL and can mask a
  200 behind a later redirect/404. `src/wayback_cdx.py` runs both the collapsed
  query (persisted as specified) and an un-collapsed query, and builds the
  inventory + coverage from the un-collapsed set. Both raw responses saved (PC5).
- **D-002 — inventory records the real `.asp` script name.** T1.3 asked for
  `lideres.asp / campeonatos.asp / other`. The archive holds ~20 distinct
  `/estadisticas/*.asp` scripts; bucketing them as "other" would discard the
  map. `endpoint` now holds the script basename. Coverage doc tables them.
- **D-003 — T1.5 probe targets deviate from the 1960s/1980s/2000s brief.** No
  usable 1960s–70s `lideres.asp` snapshot exists. Probed the 3 highest-signal
  captures that do exist (1986 param, 2007 bare lideres, 2007 bare campeonatos).
  Count held at exactly three (PC6). Logged in fetch_samples.py + spec.
- **D-004 — Phase 2 scope rewritten.** Per-season `anio=` backfill 1957–2004
  abandoned (content never archived). New scope = campeonatos ledger + 2007–21
  leader boards. See revised PHASE_2_FETCH.
- **D-005 — dedup fetch by content digest.** ~193 unique digests behind ~199
  captures. One HTTP request per digest (earliest capture as representative);
  the manifest maps every capture's timestamp to the local file. Fewer requests
  (PC6), no duplicate bytes on disk.
- **D-006 — fetch manifests live in `data/interim/`, not `data/raw/`.**
  `data/raw/` is gitignored (10 MB of HTML); the manifests must survive a
  cold-start resume (H5), so they go to tracked `data/interim/`.

Decisions made session 002 (PHASE_3):
- **D-007 — category by column signature, unknowns kept not dropped.** The aux
  headers between `JJ` and `Prom` map to the 11 known categories; the ~3
  advanced tables that appeared in 2013 (FBP/PIP/SCP) have no confident meaning,
  so they land in the interim long file with `category_known=False` and are
  excluded from the clean file. Nothing invented (PC1), nothing lost (PC5).
- **D-008 — clean leader file is regular-season only.** A "Serie Final" leaders
  board shows finals-only totals (5–7 games — checked against 2011 & 2017 raw),
  not season leaders. Keying on the `serie` <select> *value* == "1" (the option
  *text* is corrupted by unclosed tags). Seasons with no regular-season capture
  (2011, 2017) → `leader_coverage_gaps.csv`, not folded in with a caveat (PC4).
- **D-009 — `season_complete` is a heuristic, flagged not filtered.** capture ≥
  1 Oct of season year ⇒ settled; else `season_complete=False` + provisional
  note. 9 of 12 clean seasons are provisional (the archive's last regular-season
  capture usually predates the actual season end). Downstream reconcile (P4)
  tightens this against a real BSN calendar.
- **D-010 — city→franchise NOT done at parse.** D2 (franchise-as-events) + D5
  (San Juan ambiguity) make it reconcile work. `champions_from_bsnpr.csv` stays
  city-based; 3 unusual early cities carry `parse_flag=review`.
- **D-011 — `retrieved_at` = the `.meta.json` mtime** (the PHASE_2 fetch time,
  2026-09-07), since the fetch step recorded no explicit retrieval timestamp.
  The Wayback capture date lives separately in `capture_date` / `source_url`.

Decisions made session 002 (PHASE_3B):
- **D-012 — the PHASE_1 CDX enumeration was too narrow.** Pattern
  `bsnpr.com/estadisticas*` missed the root-level pre-2007 scripts
  (`lideres2001.asp`, `lidereshistoricos.asp`, `equiposstat.asp`) and all of
  `bsnpr.com/jugadores/*`. PHASE_3C must re-enumerate with `bsnpr.com/*` (or an
  explicit script list) and persist it properly via `src/wayback_cdx.py`.
- **D-013 — `enciclopedia.asp` + `jugadores/jugador.asp?id=` are the D1 spine.**
  The encyclopedia gives canonical name + birth date + a stable integer player
  id for ~3300 players. This is fetched/parsed in PHASE_3C and becomes the
  identity anchor PHASE_4 resolves `player_raw` against — not a from-scratch
  fuzzy-match exercise.
- **D-014 — `livestats.asp` written off.** Widget shell only; no archived
  content, no endpoint/match-id scheme. Removed from the B1 hope list.
- **D-015 — probe stays out of the pipeline.** `src/probe_archive.py` +
  `data/raw/probe/` are throwaway investigation artifacts, not an ingest stage.
  No `make` target, no interim/clean output. PHASE_3C writes fresh fetchers.

Decisions made session 002 (PHASE_3C):
- **D-016 — root inventory persisted as a filtered subset.** The full
  `bsnpr.com/*` CDX is 133k rows / 25 MB, mostly news/forum/image noise.
  `cdx_root_inventory.csv` keeps only the ~34k stats/game/player-script rows
  (tracked). The raw CDX JSON (46 MB) is gitignored; regenerate with
  `make enumerate-root`.
- **D-017 — the 500-capture gate is on distinct digests (= actual fetches),
  not raw captures.** `equiposstat.asp` has 525 raw captures but 254 unique
  content digests → fetched. `fetch_pre2007.py` `MAX_TRANCHE=500` refuses any
  script above that; `jugador.asp` (5986) and the game scripts wait for owner OK.
- **D-018 — root `campeonatos.asp` / `lideres.asp` not re-parsed.** Same engine
  and content as the `/estadisticas/` versions PHASE_3 already parsed. Raw files
  kept in `data/raw/pre2007/` as a second provenance source if PHASE_4 needs one
  for a disputed row.
- **D-019 — `equiposstat` `CC/3P/TL` cells are `attempted-made`, not
  made-attempted.** Verified against the PROMEDIO table's percentages
  (`"151-90"` → 90/151 = 0.596 = CC%). Stored as separate nullable `fga`/`fgm`
  etc. (PC2).
- **D-020 — B2 further reopened.** PHASE_3B found the pre-2007 leader scheme;
  PHASE_3C found box-score/PBP scripts (`boxscore.asp`, `pogamestat.asp`,
  `a2gamestatpbp.asp`) archived 2001–2021. Pre-2007 game data is now
  archive-recoverable, not newspaper-only. Own phase, gated.

Decisions made session 002 (PHASE_3D):
- **D-021 — `bsnpr_id` IS the canonical id.** `enciclopedia.asp` /
  `jugador.asp?id=N` carry the league's own integer id. No fuzzy dedup *within*
  the canonical table — D1's dedup risk is about linking observations, not
  building the player list. Two same-name rows with different ids stay separate.
- **D-022 — the id map only holds season-corroborated links.** An observation
  name resolves to an id only if exactly one alias candidate has that season in
  its career span. Unique-name-but-uncorroborated, multi-candidate, and
  no-match all go to `player_review_queue.csv` — never the map ("never on name
  alone", D1). Rows migrate map-ward as tranche B fills career spans.
- **D-023 — `given_first_only` aliases are intentionally ambiguous.** "Arroyo,
  Carlos A." also emits alias "Arroyo, Carlos", shared with "Arroyo, Carlos
  Andrés". The season test disambiguates (id 273 played 2001, id 13124 didn't).
- **D-024 — `1/1/1900` birth date = null.** Source's unknown-DOB sentinel (PC2).
- **D-025 — old `/jugador.asp` (2004–06, opaque `r2=` tokens) skipped.** No
  clean id; the `?id=N` scheme + enciclopedia cover the player set.
- **D-026 — tranche B fetch is a background, cross-session job.** ~1,079 profiles
  at throttled Wayback rates ≈ 2 h. Fetch + parse are idempotent; the spine is
  usable now and sharpens as profiles land.

Decisions made session 002 (PHASE_4):
- **D-027 — no conflict is auto-resolved by code.** Owner instruction + PC1.
  The reconcile flags disagreements; a human clears them. Resolutions live in
  `src/reconcile.py` `OWNER_RESOLUTIONS`, dated 2026-09-08, and are recorded in
  the row `note` prefixed `OWNER <date>:`. The seed CSVs and
  `champions_from_bsnpr.csv` are never edited. 2026-09-08 batch: 1971/1974 →
  `dual_metric_d4` (both winners, metric-labelled); 1936/1968 → `agree`
  (city-vs-club naming); 1945 → stays `disputed`.
- **D-028 — seed + bsnpr concurring → `verified`.** The seed cites en.wiki; the
  bsnpr ledger is the league's own site via Wayback — independent. 87/98
  champion seasons concur and are promoted from `single-source` to `verified`.
- **D-029 — franchise knowledge lives in `src/reconcile.py` as module data.**
  `FRANCHISES` / `FRANCHISE_EVENTS` / `CITY_MAP` / `CLUB_CODES` with D2/D5
  citations in comments. D2 lineage is events (`franchise_events.csv`), not
  folded into the master; the murky ones (Brujos/Osos, Grises/Criollos,
  Santos/Capitalinos) are `confidence=disputed`.
- **D-030 — `champions_reconciled` / `scoring_champions_reconciled` are derived
  joins.** The seed CSVs and `champions_from_bsnpr.csv` stay untouched — they
  carry context the join drops. Regenerable via `make reconcile`.
- **D-031 — es.wikipedia is fetchable from this environment (F3 resolved,
  2026-09-08).** Retested directly via `WebFetch`: main BSN article, champions
  annex, per-franchise articles all load. Both Wikipedias are now reconcile
  sources.
- **D-033 — game-script tranche = (script, capture_year), hard 500 gate.**
  `src/fetch_games.py` `MAX_TRANCHE=500` refuses a bigger tranche; `--force-year`
  overrides after an owner OK. Every script >500 total; only sub-500 capture-year
  slices fetch without approval.
- **D-034 — box-score shot cells are shot-type-split, not combined.**
  gamestatwide `CCI-CCA` = 2-point FG only (attempted-made); `CC3I-CC3A` = 3PT.
  Stored `fg2m/fg2a` + `fg3m/fg3a`. Verified by `2·FG2 + 3·FG3 + FT == PTS`
  (0 mismatches over 1,666 rows). Modern boxscore/pogamestat: `M A` per block
  = made-attempted.
- **D-035 — game-id `r=BS<NN><seq>`, season = 1980 + NN.** `read_html` needs
  `flavor="bs4"` (unclosed `<b>` in `<td><font>` breaks lxml).

- **D-032 — franchise-lineage owner decisions (2026-09-08).** Brujos de Guayama
  → Osos de Manatí = `verified` relocation (es.wiki confirms; `osos_manati`
  founded corrected 2014→2023; Atenienses de Manatí is separate). Grises de
  Humacao → Criollos de Caguas = kept as D2's `single-source` claim, unverified
  (no Wikipedia corroboration). Santos de San Juan = distinct franchise_id,
  `relationship_unclear`, not merged. New `franchise_founded` conflict logged
  (Criollos 1969 en.wiki vs 1976 seed).

---

[VERIFICATION_LOG]

| Phase | V1 | V2 | V3 | V4 | V5 | Notes |
|---|---|---|---|---|---|---|
| PHASE_1 | PASS | PASS | PASS | PASS | PASS | V1: T1.1–T1.7 all delivered (T1.5 deviation documented, D-003). V2: PC5 raw immutable + cached; PC6 sequential/≥1.5s/backoff; PC1 no fabrication — negative finding reported straight. V3: no secrets; `.env` gitignored; UA carries no PII. V4: `make enumerate` + `make samples` run clean; 19 pytest pass; `read_html` verified on all 3 probes. V5: snake_case modules, English code/comments. |
| PHASE_2 | PASS | PASS | PASS | PASS | PASS | V1: T2.1–T2.5 done; 193/193 digests fetched, 0 failed; manifests written. V2: PC5 raw bytes unmodified + never re-fetched (idempotent re-run confirmed); PC6 one request per digest, ≥1.5s spacing, backoff; PC3 provenance captured per file in `.meta.json`. V3: no secrets; raw HTML gitignored. V4: 23 pytest pass; sampled files parse with `read_html`. V5: snake_case, English. |
| PHASE_3 | PASS | PASS | PASS | PASS | PASS | V1: T3.1–T3.6 done — both clean streams + stats_tracked + gaps file produced. V2: PC1 (1953/disputes surfaced, no guesses); PC2 (`to_int`/`to_float` → None on blank, verify asserts pct rows carry no `total`); PC3 (`make verify` enforces provenance on every row); PC4 (`leader_coverage_gaps.csv`, `season_complete`, `parse_flag`); PC5 (parse only reads `data/raw/`, idempotent); D3/D5/D6 asserted in verify. V3: no secrets; parse/verify read-only on raw. V4: `make parse` + `make verify` green (6375 checks); 61 pytest pass; 1986 parse cross-validates against seed scoring CSV (29.8 ppg exact). V5: snake_case, English comments, "why" only. |
| PHASE_3B | PASS | PASS | PASS | PASS | PASS | V1: T3B.1–T3B.4 done — 4 targets probed (5/5/4/5 captures) + 3 root-level `lideres*` follow-ups; verdicts + spec delivered; sample-only respected (no bulk fetch, no parser, no clean output). V2: PC5 raw bytes cached unmodified in `data/raw/probe/`; PC6 sequential via `polite_get`, ≥1.5s, backoff recovered from a Wayback 503 burst; PC1 findings reported straight incl. the "B2 partially reopened" reversal. V3: no secrets. V4: 61 pytest still pass (probe adds no code path to the pipeline); every probed capture inspected. V5: snake_case, English. |
| PHASE_3C | PASS | PASS | PASS | PASS | PASS | V1: T3C.1–T3C.5 done — enumerate + coverage report + fetch (315/315, 0 fail) + 5 clean outputs + verify + tests. Owner's 500-gate honoured: `jugador.asp` (5986) and game scripts reported, not fetched. V2: PC1 (1952 dispute = 2 rows, clipped `<pre>` values flagged not rewritten, root campeonatos not re-parsed to avoid dup rows); PC2 (`fga`/`fgm` split, `to_int`→None on blank); PC3 (`verify_pre2007` asserts provenance on every row); PC4 (2 DB-error captures counted + reported, gated tranches in coverage_root.md); PC5 (parse reads `data/raw/pre2007/` only, idempotent); PC6 (`polite_get`, one GET/digest, rode out a long Wayback 503 throttle); D4 (`metric_era` flip asserted). V3: no secrets; raw CDX + raw HTML gitignored. V4: `make parse-pre2007` + `make verify` green (13,410 checks); 79 pytest pass; `equiposstat` made≤att verified, 1986/1952 cross-checks hold. V5: snake_case, English, "why" comments. |
| PHASE_3D | PASS | PASS | PASS | PASS | PASS | V1: T3D.1–T3D.3 done — canonical spine (3,303 players) + aliases + career-seasons + id_map + review queue; tranche B enrichment fetch backgrounded (partial), T3D.4 = re-run parse on completion. V2: PC1 (no fuzzy match in id_map — D1; ambiguous → review queue); PC2 (`1/1/1900` → null, blank stats stay blank); PC3 (`verify_players` asserts provenance on every canonical row); PC4 (review queue is a first-class output with candidate ids + reason); PC6 (`polite_get`, one GET per id, background throttle); D1 (accent-stripped `normalized_name`, alias table, match needs season corroboration not name alone — asserted in verify). V3: no secrets. V4: `make parse-players` + `make verify` green (38,706 checks); 91 pytest pass (+12); id_map spot-checks correct (Carmona→37, Arroyo Carlos→273 via season). V5: snake_case, English. |
| PHASE_3E | PASS | PASS | PASS | PASS | PASS | V1: T3E.1–T3E.6 done — enumerate (10,548 captures) + `coverage_games.md` + gated fetcher (`MAX_TRANCHE=500`, `--force-year` after approval) + box-score parser + PBP parser + verify + tests. Fetch is a multi-day throttled job, one tranche at a time (PC6); done so far: `gamestatwide` 864, `pogamestat` 1021, `boxscore` 261, `a2gamestatpbp` 2001+2004; 2002 fetching, 2003 queued; owner HOLD on `pogamestat`/`boxscore` 2007–09 + all `gameinfo`. V2: PC1 (`bsnpr_id` blank unless a unique season-in-career match — D1, no guesses; `jugada_raw` kept verbatim; `box_check` flags source pts-mismatch, doesn't rewrite); PC3 (`verify_games` provenance per row); PC4 (crammed/stub captures counted + dropped from results, gated tranches in `coverage_games.md`, `box_check`); PC5 (parse reads `data/raw/games/` only, idempotent); PC6 (`polite_get`, one GET/digest, 500-gate honoured, sequential chain). V3: no secrets; raw gitignored. V4: `make parse-games` + `make verify` green (326,175 checks); 125 pytest pass (+17); **`2·FG2 + 3·FG3 + FT == PTS` on every parsed box row (4/39,669 source-error `pts_mismatch`, flagged); made ≤ att always**. V5: snake_case, English, "why" comments. |
| PHASE_4 | PASS | PASS | PASS | PASS | PASS | V1: T4.1–T4.5 done + owner-resolution follow-up. Franchise layer + champions_reconciled + scoring_champions_reconciled + reconcile_conflicts + verify + tests. V2: PC1 (D-027: code flags, human clears; `OWNER_RESOLUTIONS` dated + auditable; seed CSVs untouched; 1945 left `disputed`); D2 (`franchise_events.csv`, murky lineage = disputed); D3 (`1942`+`1942-1943` both kept); D4 (`metric_era` flip + 1971/1974 `dual_metric_d4` recording BOTH winners); D5 (1945 stays flagged); D6 (1953 no_champion). PC3 (provenance / `sources` per row). V3: no secrets; pure module. V4: `make reconcile` + `make verify` green (40,114 checks); 108 pytest pass (+17); 87/98 seed↔bsnpr `verified`. V5: snake_case, English, D2/D5 citations in comments. |

---

[FILE_MANIFEST]

| Path | Status | Notes |
|---|---|---|
| `app/bsn_archivo.html` | inherited, complete | 2,214 lines, 131KB, no deps. Do not restructure. |
| `data/clean/bsn_champions_by_season.csv` | inherited, seed | 96 rows, 1930–2025. Gaps: 1953, 2024 runner-up. 1945 disputed. |
| `data/clean/bsn_franchises.csv` | inherited, seed | 28 rows. Lineage not yet encoded as events. |
| `data/clean/bsn_career_leaders.csv` | inherited, seed | 30 rows. ~5yr stale — floors only. |
| `data/clean/bsn_scoring_champions.csv` | inherited, seed | 26 rows, 1966–1991. Partial; source runs 1956–present. |
| `data/clean/bsn_records.csv` | inherited, seed | 11 rows. |
| `docs/research/README.md` | inherited | first-pull notes + coverage matrix |
| `docs/research/bsn_project_roadmap.md` | inherited | phase status, sequencing table |
| `docs/research/summary.md` | inherited | full prior-session handoff |
| `docs/research/audit_bsn_archivo_2026_09_01.md` | inherited | app audit |
| `docs/research/residual.py` | inherited | Playwright audit harness for the app; reference only |
| `src/wayback_cdx.py` | **new, S001** | CDX enumeration + inventory + coverage matrix. `make enumerate`. |
| `src/fetch_samples.py` | **new, S001** | T1.5 3-snapshot probe. `make samples`. SAMPLES list is frozen. |
| `tests/test_wayback_cdx.py` | **new, S001** | 19 unit tests over the pure helpers. `make test`. |
| `data/raw/cdx/cdx_estadisticas_{collapsed,all}.json` | **new, S001** | Immutable raw CDX responses (PC5). gitignored (`data/raw/`). |
| `data/raw/samples/*.html` + `*.meta.json` | **new, S001** | 3 probe snapshots + fetch metadata. gitignored. |
| `data/interim/cdx_inventory.csv` | **new, S001** | 1562 Wayback captures, one per row. Regenerable from raw. |
| `docs/coverage_wayback.md` | **new, S001** | Coverage matrix. Read this first for Phase 2 planning. |
| `docs/specs/wayback_ingest_spec.md` | new S001, updated S002 | Ingest strategy, source shapes, PHASE_3 interfaces + outputs, open questions Q1–Q12 (Q5–Q8 resolved). |
| `.venv/` | **new, S001** | Python 3.14, deps from requirements.txt. gitignored. |
| `src/fetch_wayback.py` | **new, S001** | PHASE_2 tranche A–C bulk fetcher. `make fetch`. Idempotent. |
| `data/raw/campeonatos/*.html` (+meta) | **new, S001** | 79 champion-ledger snapshots, 2007–2021. gitignored. |
| `data/raw/lideres/*.html` (+meta) | **new, S001** | 114 season-leader snapshots, 2007–2021. gitignored. |
| `data/interim/fetch_manifest_{campeonatos,lideres}.csv` | **new, S001** | Every capture → its local raw file. Tracked. Phase 3 input. |
| `src/parse_wayback.py` | **new, S002** | PHASE_3 parser. `make parse`. Pure, idempotent, no network. |
| `src/verify_clean.py` | **new, S002** | PHASE_3 integrity gate. `make verify`. 6375 assertions. |
| `tests/test_parse_wayback.py` | **new, S002** | 38 unit tests over the parse helpers. |
| `data/interim/champions_bsnpr_long.csv` | **new, S002** | 6486 rows — every ledger row of every capture. Regenerable. |
| `data/interim/player_leaders_long.csv` | **new, S002** | 10345 rows — every leader row of every capture. Regenerable. |
| `data/interim/leader_capture_index.csv` | **new, S002** | 1315 rows — (capture, category) → row count. Dedup ledger. |
| `data/clean/champions_from_bsnpr.csv` | **new, S002** | 92 rows, 1930–2020. City-based champion/coach/runner-up + provenance. |
| `data/clean/player_season_leaders.csv` | **new, S002** | 1250 rows, 12 seasons × 11 categories. `player_raw`/`club_raw` unresolved (D1). |
| `data/clean/seasons_stats_tracked.csv` | **new, S002** | Season × 11 categories, 1/0/blank. PC2 era signal. |
| `data/clean/leader_coverage_gaps.csv` | **new, S002** | Every archived season → regular_season/playoff_only/not_archived. PC4. |
| `src/probe_archive.py` | **new, S002 (PHASE_3B)** | Throwaway probe fetcher/inspector. No `make` target, not in the pipeline. |
| `data/raw/probe/*.html` (+meta) | **new, S002 (PHASE_3B)** | 22 sample captures (enciclopedia/lideres_e/livestats/estadisticas2001/lideres2001/lidereshistoricos). gitignored. |
| `docs/specs/archive_probe_spec.md` | **new, S002 (PHASE_3B)** | Per-script verdicts; the root-level pre-2007 URL scheme discovery. Read before PHASE_3C. |
| `src/enumerate_root.py` | **new, S002 (PHASE_3C)** | `bsnpr.com/*` CDX enumeration. `make enumerate-root`. |
| `src/fetch_pre2007.py` | **new, S002 (PHASE_3C)** | Pre-2007 tranche fetcher, `MAX_TRANCHE=500` gate. `make fetch-pre2007`. |
| `src/parse_pre2007.py` | **new, S002 (PHASE_3C)** | Parser for lidereshistoricos / lideres200x / equiposstat. `make parse-pre2007`. |
| `tests/test_parse_pre2007.py` | **new, S002 (PHASE_3C)** | 18 unit tests over the pre-2007 parse helpers. |
| `data/raw/cdx/cdx_root_{all,bydigest}.json` | **new, S002 (PHASE_3C)** | Raw `bsnpr.com/*` CDX (46 MB). gitignored, regenerable. |
| `data/raw/pre2007/**` | **new, S002 (PHASE_3C)** | 315 pre-2007 captures across 8 scripts. gitignored. |
| `data/interim/cdx_root_inventory.csv` | **new, S002 (PHASE_3C)** | ~34k stats-relevant root captures (filtered subset). Tracked. |
| `data/interim/fetch_manifest_pre2007.csv` | **new, S002 (PHASE_3C)** | Every fetched pre-2007 capture → local file. Tracked. |
| `docs/coverage_root.md` | **new, S002 (PHASE_3C)** | Root-scheme per-script coverage; the gated (>500) tranches. |
| `docs/specs/pre2007_ingest_spec.md` | **new, S002 (PHASE_3C)** | Ingest decisions, source shapes, the box-score/PBP finding, open Qs. |
| `data/clean/historic_scoring_champions.csv` | **new, S002 (PHASE_3C)** | 58 rows, scoring champions 1948–2004 (games/total/ppg). |
| `data/clean/historic_awards.csv` | **new, S002 (PHASE_3C)** | 135 rows — MVP/Rookie/Defensive-Player, 1958–2004. |
| `data/clean/player_season_leaders_2000_2002.csv` | **new, S002 (PHASE_3C)** | 403 rows, 9 categories, serie-split. `lideres2000` surname-only. |
| `data/clean/player_season_stats_2001_2004.csv` | **new, S002 (PHASE_3C)** | 503 player-seasons, 2001–2003, 14 teams (only pre-2007 player-level source). |
| `data/clean/team_season_totals_2001_2004.csv` | **new, S002 (PHASE_3C)** | 38 team-season totals. |
| `src/fetch_players.py` | **new, S002 (PHASE_3D)** | enciclopedia + jugador.asp fetcher. `make fetch-players`. |
| `src/parse_players.py` | **new, S002 (PHASE_3D)** | D1 identity spine builder. `make parse-players`. Re-run as tranche B lands. |
| `tests/test_parse_players.py` | **new, S002 (PHASE_3D)** | 12 unit tests over the name-normalisation helpers. |
| `data/raw/players/**` | **new, S002 (PHASE_3D)** | enciclopedia (77) + jugador.asp (~1079, backgrounded) captures. gitignored. |
| `data/interim/fetch_manifest_players.csv` | **new, S002 (PHASE_3D)** | Every player capture → local file. Tracked. |
| `data/interim/player_review_queue.csv` | **new, S002 (PHASE_3D)** | Uncorroborated / ambiguous obs names + candidate ids + reason. Tracked. |
| `data/clean/players_canonical.csv` | **new, S002 (PHASE_3D)** | 3,303 players keyed by bsnpr_id. The D1 spine. |
| `data/clean/player_aliases.csv` | **new, S002 (PHASE_3D)** | ~24k (id, alias, type). accent-free normalized_alias. |
| `data/clean/player_career_seasons.csv` | **new, S002 (PHASE_3D)** | (id, season, team_raw) from jugador.asp. |
| `data/clean/player_id_map.csv` | **new, S002 (PHASE_3D)** | obs player_raw → bsnpr_id, season-corroborated only. |
| `docs/specs/identity_spine_spec.md` | **new, S002 (PHASE_3D)** | D1 implementation: sources, alias types, the matching rule, open Qs. |
| `src/reconcile.py` | **new, S002 (PHASE_4)** | Seed↔archive reconcile + franchise layer. `make reconcile`. Pure, no network. |
| `tests/test_reconcile.py` | **new, S002 (PHASE_4)** | 14 unit tests over the city/name-resolution helpers. |
| `data/clean/franchises.csv` | **new, S002 (PHASE_4)** | 33-row franchise master (seed 28 + 5 game-row-only names). |
| `data/clean/franchise_events.csv` | **new, S002 (PHASE_4)** | 8 D2 lineage events; murky ones `disputed`. |
| `data/clean/city_franchise_map.csv` | **new, S002 (PHASE_4)** | normalized city → franchise_id + per-season flags. |
| `data/clean/club_code_map.csv` | **new, S002 (PHASE_4)** | lideres200x 5-char + equiposstat 2-letter codes → franchise_id. |
| `data/clean/champions_reconciled.csv` | **new, S002 (PHASE_4)** | 98 seasons, seed↔bsnpr, `agreement` status. Derived join. |
| `data/clean/scoring_champions_reconciled.csv` | **new, S002 (PHASE_4)** | 68 seasons, seed + historic + 2007+ leaders. |
| `data/clean/reconcile_conflicts.csv` | **new, S002 (PHASE_4)** | 1 flagged conflict (1945/D5). 4 others owner-resolved 2026-09-08 (see `OWNER_RESOLUTIONS`). |
| `docs/specs/reconcile_spec.md` | **new, S002 (PHASE_4)** | Reconcile decisions, the conflicts, franchise/D2 handling, [OWNER_RESOLUTIONS], open Qs. |
| `src/{enumerate_games,fetch_games,parse_games}.py` | **new, S002 (PHASE_3E)** | Game-script enumerate / gated fetch / box-score + PBP parse. `make {enumerate,fetch,parse}-games`. `fetch_games` has `--script/--year/--force-year`, `MAX_TRANCHE=500`. `parse_games` reads two id schemes (pre-2007 `BS<NN>`, 2007+ `BS<YYYY>`), maps modern box columns by LABEL not position (2013 = 25 cols), `gamestatwide` needs `flavor="bs4"`. |
| `tests/test_parse_games.py` | **new, S002 (PHASE_3E)** | 17 unit tests over the box-score + PBP helpers (`_season_from_rid`, `_num_pair`, `_box_check`, `_pbp_fields`, column-by-label). Part of the 125-test suite. |
| `data/interim/cdx_games_inventory.csv` | **new, S002 (PHASE_3E)** | 10,548 distinct game-script captures. Tracked. |
| `data/interim/fetch_manifest_games.csv` | **new, S002 (PHASE_3E)** | Fetched game captures → local file, `gated` column. Tracked. Merged across runs. |
| `data/raw/games/**` | **new, S002 (PHASE_3E)** | Fetched game-script captures: `gamestatwide` 864, `pogamestat` 1021, `boxscore` 261, `a2gamestatpbp` 2001 (78) + 2004 (74) + **2002 (mid-fetch, resume) + 2003 (queued)**. gitignored. |
| `data/clean/game_results.csv` | **new, S002 (PHASE_3E)** | 1,287 rows — one per game, teams + quarter/final scores. Seasons 2001–03, 2008–13. Stub captures (blank score + no box) dropped; team-Totals-row score fallback. |
| `data/clean/game_box_player.csv` | **new, S002 (PHASE_3E)** | 39,669 player-game rows. `bsnpr_id` joined where D1-resolvable: **pre-2007 4,152/15,941 = 26%; 2007+ 17,599/23,728 = 74%; total 21,751/39,669 = 55%**. `fg2m/fg2a` and `fg3m/fg3a` kept separate. `box_check`: 39,663 `ok` / 4 `pts_mismatch` (source data-entry errors, flagged not rewritten). |
| `data/clean/game_plays.csv` | **new, S002 (PHASE_3E)** | 11,106 play-by-play events, seasons 2001 (8,771) + 2003 (2,335) — from `a2gamestatpbp`. `jugada_raw` verbatim + parsed `event_type`/`actor_raw`/`team_raw`. Classified: rebound 2,065 · made_2 1,606 · miss_2 1,198 · assist 1,025 · miss_3 790 · turnover 630 · made_3 433 · steal 398 · team_rebound 201 · jump_ball 140 · timeout 137; ~2,483 unclassified. Grows when 2002/2003 fetch completes. |
| `docs/coverage_games.md` | **new, S002 (PHASE_3E)** | Per-script per-capture-year table; the >500 gated tranches. |
| `docs/specs/game_data_spec.md` | **new, S002 (PHASE_3E)** | Game-engine shapes, tranche gate, two id schemes, shot-cell conventions, open Qs. |

---

[NEXT_ACTIONS]

1. **PHASE_3E fetch resume** (contract: `PHASE_3E_FETCH_REMAINING` in [TASK_QUEUE]) —
   a single-stream chain is running `a2gamestatpbp` 2002 (resume from ~343/1462)
   then 2003 (1555), both owner-approved, `--force-year`. NOTE: a prior run had
   **two** concurrent fetchers on the 2002 tranche (PC6 breach); both were killed
   2026-09-08 and replaced with one chain (`scratchpad/fetch_chain3.sh`,
   task `bzjo92jo3`). When it completes: `make parse-games && make verify`,
   commit, report. Owner HOLD still stands on `pogamestat`/`boxscore` 2007–09 and
   all of `gameinfo` — do NOT fetch until owner reviews PBP contents.
2. **RANKED IDENTITY-LIFT PLAN** — box-score `bsnpr_id` resolution is 26% pre-2007
   vs 74% modern; review queue = 828 rows (361 season-not-in-known-span · 346
   no-name-match · 106 multi-candidate-no-season · 15 multi-match). Lift it in
   this order:
   a. **Club-code map as a 2nd corroboration signal** (identity_spine_spec Q2;
      cheapest, no fetch). `data/clean/club_code_map.csv` already exists from
      PHASE_4. Join observed `club_raw` → `franchise_id` and require club match
      *in addition to* season for the ambiguous buckets — directly clears the
      15 "multiple players match name + season" rows and tightens the 106
      "multiple candidates" rows. Wire into `parse_players.build_id_map()`.
   b. **Fetch `jug05.asp` / `jugador05.asp`** (identity_spine_spec Q3; ~600
      captures each, 2005–2007-era player pages — **GATED >500, needs owner OK**).
      Extends `players_canonical` + `player_career_seasons` into the 2004–2007
      gap the enciclopedia misses, which is where most of the 361
      "season-not-in-known-span" rows fall.
   c. **Manual historic seed** (identity_spine_spec Q3; last, hand work). A
      hand-built list for the ~50 historic scoring champions 1948–1970 and the
      `lideres2000` surname-only leaders absent from the encyclopedia — the bulk
      of the 346 "no canonical name match" rows. Seed file only; never edited
      into `players_canonical` by code (D1).
3. **PHASE_3E parse follow-ups** — PBP + (if ever un-held) `gameinfo` metadata are
   separate parse targets (`game_data_spec` Q5/Q6). game↔franchise join (Q4).
   Box vs `player_season_stats_2001_2004` cross-check (Q7).
4. **PHASE_4 follow-ups** (reconcile_spec Q1–Q7): the 5 flagged conflicts +
   3 disputed franchise_events need an owner decision or a third source
   (es.wikipedia, Federación). Then: apply `player_id_map` → `bsnpr_id` columns
   on `player_season_*` / `player_season_stats_*` (after tranche B); reconcile
   `historic_scoring_champions` 1948–65 / 92–04 against es.wiki; career-leaders /
   records reconcile (D7 — floors only). wayback_ingest_spec Q9–Q12 still open.
5. **PHASE_4B_GAME_POOL** — rebuild the app's game pool from
   `champions_reconciled` + the identity spine + `player_season_stats_2001_2004`
   + `game_results` / `game_box_player`. Own scope.
6. Small ungated follow-ups: `playbyplay.asp` (460), `equipo.asp` (489),
   `informe.asp` (175, game reports 2004–06), `posiciones2000.asp` +
   `estadisticas.asp` cluster → `standings_pre2007.csv` (pre2007 spec Q4).
7. Roadmap newspaper track — now only needed for pre-2001 box scores and
   anything the archive genuinely lacks. Much narrower than before.
8. Human-side: B1 DevTools recon — value reduced (see B1); still useful for the
   current/post-2021 API.
9. `git`: PHASE_3 = 4ca04f2, 3B = 21f1a5f, 3C = a3b792a, 3D = 0d0d12d + 0640a1d,
   PHASE_4 = ac4a23e + d7c3024 + cd8ef54.
   PHASE_3E = d421922, e94fec9, 640964e, a041a60, 891fc12, 2d1928c (committed);
   this `docs/session.md` H4 update pending P4. `a2gamestatpbp` 2002/2003 parse +
   commit still to come when the fetch chain finishes.
