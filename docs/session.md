# SESSION STATE — TIER 3
<!-- Authoritative for current state and task priority. Update at every phase exit. -->

**SESSION:** 002 — PHASE_3 / 3B / 3C / 3D / 4 / 3E / 3E-STORAGE / 3G / 3F (continues 001)
**DATE:** 2026-09-08
**MODEL:** Claude Sonnet 5 (claude-sonnet-5) via Claude Code

Session 002 (cont.) — all pushed to origin/main:
- `app_data_sync_spec.md` (e5609ee) — owner-supplied PHASE_5 decision.
- PHASE_3E_CLEAN_STORAGE (72d2b52) — P2 storage call. `game_plays.csv` (65 MB,
  grew every ingest, tripping GitHub's 50 MB warning + a fat history blob per
  `make parse-games`) → committed **gzipped** (`game_plays.csv.gz`, 2.7 MB) via
  a shared `open_clean_text` / `_write_csv` helper; content byte-identical.
  `docs/specs/clean_data_storage_spec.md`.
- PHASE_3G_HISTORIC_FOLLOWUP (100e9c6) — **negative finding.** Fresh CDX on all
  3 owner /btw targets: everything already ingested by PHASE_3C. No new clean
  rows. `docs/specs/historic_followup_spec.md`.
- PHASE_3F_IDENTITY_LIFT (b599e27) — club-code corroboration; id_map 423→433,
  review queue 828→818, +`club_check`. `identity_spine_spec.md` Q2 closed.
- PHASE_5_APP_SYNC — **stale-file correction 2026-09-09** (D-044). 5A–5D were
  done vs an inherited 2,214-line `app/bsn_archivo.html`; the real file is 6,286
  lines. 5B (4634dad) + 5C (8891d78) + D-042 (a22027c) **survive** — pipeline
  only. Since: **5A rewritten** + **5B-FIX** (`caciques_humacao` / D-045) =
  77a3aae · **5D redo** (`DATA`+`hydrate()` into `runBoot()`) = c22ce10 ·
  **5D.2** (SCORING hydrate 26→68) = 6c6c8a5 · **5D.3a** (`showSeason` detail
  from `seasons/*.json`) = 8fd7c6f (pushed). **5D.3b IN PROGRESS**: crosswalk
  `app/player_crosswalk.csv` built (386 curated names → 112 auto / 48 review /
  226 none; matcher = `scratchpad/xwalk_match.py`) — sent to owner for spot-check
  of the 48 review `bsnpr_id`s + the thin-JSON open question; no `showPlayer`
  code until sign-off. Queue: 5D.3b impl → 5D.3c (full-archive search) → 5D.2b
  (MVP_YEARS) → 5D.4 (gap text) → 5E (PWA) → 5G (deploy).

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
  accent-stripped names, ~24k aliases, **649 id-map links** (633 season + 16
  club-tiebreak), 602-row review queue. Tranche B (1,078 profiles) done. 725
  mangled names fixed 2026-09-08 (D-042 — drove 433→649 / 828→602).
- PHASE_4_RECONCILE (ac4a23e + d7c3024 + cd8ef54) — reconciled champions +
  scoring vs the Wikipedia seed. 89/98 champion seasons `agree`. Owner resolved
  4 of 5 conflicts; es.wikipedia retested and **fetchable** (F3 resolved) — used
  to verify Brujos→Osos and disprove wiki support for Grises→Criollos.
  `reconcile_conflicts.csv` = 2 rows (1945/D5; Criollos founding year).
- PHASE_3E_GAME_DATA (d421922 · e94fec9 · 640964e · a041a60 · 891fc12 · 2d1928c
  · 7f09013) — enumerated the 5 archived game scripts (10,548 distinct captures);
  gated fetcher (hard 500/tranche); box-score + play-by-play parsers.
  **`a2gamestatpbp` 2001–2004 fetch COMPLETE** — `game_plays` = 233,664 plays
  (2001–2003). `pogamestat`/`boxscore` 2007–09 + `gameinfo` still owner-HELD.
- PHASE_3E_CLEAN_STORAGE (72d2b52) · PHASE_3G_HISTORIC_FOLLOWUP (100e9c6) ·
  PHASE_3F_IDENTITY_LIFT (b599e27) · `app_data_sync_spec.md` (e5609ee) — all
  pushed. See the "Session 002 (cont.)" block at the top of this file for the
  one-line summary of each.
- PHASE_5_APP_SYNC — STARTED. Sub-phased 5A–5G in [TASK_QUEUE]; 5A (data map +
  JSON schema spec, no code) is the current sub-phase. One sub-phase per turn,
  pause + approve between.

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
- `franchises.csv` (34 — +`caciques_humacao`, D-045), `franchise_events.csv`
  (9 D2 events), `city_franchise_map.csv`,
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
  `normalized_name`. **725 mangled names ("…, Estadísticas Jugador") fixed
  2026-09-08 — D-042.**
- `player_aliases.csv` ~24k (id, alias, 9 alias types incl. `initial`,
  `given_first_only`, `nickname`).
- `player_career_seasons.csv` (from jugador.asp), `player_id_map.csv` **649**
  obs→id links (633 `name+season_in_career` + 16 `name+season+club` — PHASE_3F
  club tiebreak; `club_check` advisory column), `data/interim/player_review_queue.csv`
  **602** rows (199 no name match, 315 season outside career span, 79
  multi-candidate, 9 same-name ambiguity; `club_match_ids` hints — **no fuzzy
  match ever enters the id map**). Jump from 433/828 = D-042 name fix.

Game data (PHASE_3E — `a2gamestatpbp` 2001–2004 fetch complete; box scores
2001–03 + 2008–13):
- `game_results.csv` 1,287 games; `game_box_player.csv` 39,669 player-game
  rows; **`game_plays.csv.gz` 233,664 plays** (gzipped — see PHASE_3E_CLEAN_STORAGE).
- **Box-score `bsnpr_id` resolution: 21,751/39,669 = 55% overall** (pre-2007
  26%, 2007+ 74%). The gap is the identity spine's pre-2007 hole
  (`identity_spine_spec` Q3), NOT the matcher — every match is season-corroborated.
- Box seasons: **2001–2003 + 2008–2013**. `box_check` column flags source
  pts-mismatch rows (4/39,669 = 0.01%, PC4 — flagged not hidden).
- **PBP event_type counts** (233,664 plays, seasons 2001–2003 from
  `a2gamestatpbp.asp`): unclassified 70,400 · rebound 42,367 · made_2 23,482 ·
  assist 19,794 · miss_2 19,132 · miss_3 17,301 · turnover 12,469 · made_3
  8,925 · steal 8,290 · team_rebound 5,198 · timeout 4,029 · jump_ball 2,277.
  ~70% classified; `jugada_raw` verbatim; `actor_raw` is a bare surname
  (PBP's own format).

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

### PHASE_3E_FETCH_REMAINING — a2gamestatpbp CHAIN COMPLETE (2026-09-08, commit 7f09013)

**`a2gamestatpbp.asp` 2001–2004 all fetched + parsed.** `game_plays` = 233,664
plays, seasons 2001–2003 (2004 captures held no in-window PBP rows). Committed
7f09013; re-emitted as `game_plays.csv.gz` by PHASE_3E_CLEAN_STORAGE. Still
HELD by owner (do NOT fetch): `pogamestat` 2007/08/09, `boxscore` 2007, all of
`gameinfo` — until owner reviews the PBP contents. The rest of this section is
kept as the historical resume contract.

---

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
  resolved pre-2007, 74% 2007+, 55% overall) · `game_plays.csv.gz` 233,664
  plays (2001–2003). Committed 7f09013 (data) + PHASE_3E_CLEAN_STORAGE (gzip).
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

### PHASE_3E_CLEAN_STORAGE — COMPLETE (2026-09-08, owner-directed P2 call)

Owner instruction: resolve the `game_plays.csv` 62 MB problem before it grows —
pick Git LFS / split-by-season / compression, log the decision + rationale in a
spec (H1/H2).

- **DECISION: gzip the file in place.** `data/clean/game_plays.csv` (65 MB,
  233,664 rows, +2.7 MB every ingest session) → **`game_plays.csv.gz` (2.7 MB,
  24×)**. Single logical file, no split, no LFS, no new dependency. Full
  rationale + rejected alternatives (Git LFS / split-by-season / Parquet /
  defer-to-PHASE_5): `docs/specs/clean_data_storage_spec.md`.
- `src/parse_wayback.py` — new `open_clean_text(path, mode)`: gzip-transparent
  on a `.gz` suffix, `mtime=0` for deterministic output (no-op reparse = empty
  git diff). `_write_csv` routes through it; hardened its log line against
  out-of-repo paths.
- `src/parse_games.py` — writes `game_plays.csv.gz`.
- `src/verify_clean.py` — `_clean_path()` / `_exists()` resolve `<name>` →
  `<name>.gz`; consumers still ask for `"game_plays.csv"`.
- `tests/test_parse_wayback.py` — +4 tests (gz round-trip, magic bytes,
  determinism, plain-CSV path). **129 pytest pass** (was 125).
- `git rm` the tracked 65 MB `.csv`; `.gz` tracked in its place. Content
  verified byte-identical to the committed `.csv` (`diff` = 0 lines).
- **NOT done** (needs owner OK — P1/G4): purging the 65 MB blob already in
  history (commits 2d1928c, 7f09013). `.git` is 10 MB; a `filter-repo` +
  force-push isn't worth it yet. Flagged in the spec [OPEN_QUESTIONS].
- Threshold for future tables: raw CSV > ~20 MB → `.csv.gz`. Next candidate
  `game_box_player.csv` (10 MB, growing) — one-line change when it crosses.

**Verify:** `make verify` green (326,175 checks); `make test` 129 pass;
`make parse-games` re-emits `game_plays.csv.gz` deterministically;
`pandas.read_csv` reads it natively. Paused (P6), nothing committed (P4).

### PHASE_3G_HISTORIC_FOLLOWUP — COMPLETE (2026-09-08). NEGATIVE FINDING.

**Result: no new `data/clean/` rows. All three targets resolve to data already
ingested by PHASE_3C.** Full detail: `docs/specs/historic_followup_spec.md`.

**What each param value turned out to be** (confirmed from the pages, not assumed):
- **`lidereshistoricos.asp`** — fresh CDX (`bsnpr.com/lidereshistoricos.asp*`)
  shows **only `?t=3`** (7 caps / 5 digests, 2002-06→2004-09) + 1 bare capture
  (same view). No `t=1`/`t=2`/`t=4`/… ever existed. `?t=3` = the "Líderes
  Históricos" page: scoring champions 1948→2004 **+ DPOY (1964→2004) / ROY
  (1958→2004) / MVP (1958→2004) award histories**. The 3 "unlabeled" tables the
  probe spec guessed as rebounds/assists are those award histories (page section
  headers `DEFENSA DEL AÑO` / `NOVATO DEL AÑO` / `JUGADOR MÁS VALIOSO`). **All of
  it is already in `historic_scoring_champions.csv` + `historic_awards.csv`**
  (PHASE_3C parsed the same `?t=3` 2004-09 capture). archive_probe_spec Q2 closed.
- **`lideres2002.asp`** — bare (1 digest) + `?grupo=BS22&serie=1` (3 digests),
  2002-05→2003-10. Serie-Regular player leaders, 8 categories × top-10. **Already
  in `player_season_leaders_2000_2002.csv`** (80 rows for 2002 — the PHASE_3C
  `lideres200x` sweep already covered `lideres2002`). `serie={3,4}` 2002 were
  never archived.
- **`mvp.asp` (root)** — bare only, 10 caps / 7 digests, 2004-04→2006-11.
  **Byte-equivalent to `lidereshistoricos.asp?t=3`** — a second URL alias for
  the same server-side view, same 4 tables, latest capture (2006) still stops at
  2004. Cross-checked the 2006 capture against the clean tables: **0 diffs**
  across 57 scoring seasons + 135 award rows. Not an independent source (same
  bsnpr DB) → no `confidence` bump; kept as a 2nd provenance path (D-018), not
  re-parsed.

**The "all-time non-scoring leaders back to 1948" the follow-up hoped for do NOT
exist in the archive.** Only `t=3` (award histories) was crawled. Routes to the
newspaper / Federación track if ever needed.

- T3G.1 — DONE. `src/enumerate_historic_followup.py` (`make enumerate-historic`).
  `data/interim/cdx_historic_followup.csv` (27 captures, all statuses).
- T3G.2 — DONE. `src/fetch_historic_followup.py` (`make fetch-historic`). 7
  `mvp.asp` digests fetched (0 fail); lidereshistoricos/lideres2002 already on
  disk from PHASE_3C. `MAX_TRANCHE=500` (all far under). Manifest tracked.
- T3G.3 — DONE. Probed + confirmed each param value from the page; `mvp.asp`
  corroboration cross-check (0 diffs). No parser — no new clean output.
- T3G.4 — DONE. `historic_followup_spec.md` (H2); archive_probe_spec Q2 closed;
  session.md updated.

**Verify:** `make verify` green (326,175 checks, unchanged — no clean data
touched); `make test` 129 pass. Paused (P6), nothing committed (P4).

<details><summary>original scope (owner /btw)</summary>

Three root-level pre-2007 targets the earlier probes noted but never ingested,
in this order:

1. **`lidereshistoricos.asp?t=*`** — the year-by-year single-season-leaders
   record. `?t=3` is probed (archive_probe_spec): scoring `AÑO|JUGADOR|EQUIPO|
   JJ|P/A|PPJ` 1948→2001 carrying BOTH total P/A and PPJ (straddles the D4
   boundary), plus 3 more `AÑO|JUGADOR|EQUIPO` tables (rebounds 1958→2001,
   assists 1964→2001, one more) player+team, no numbers. **Other `t` values
   are NOT yet known** — root CDX so far only shows `?t=3` + one bare hit.
2. **`lideres2002.asp`** — the 2002-season sibling of `lideres2001.asp`
   (already ingested: phase-split player leader tables `Anotaciones/Rebotes/
   Asistencias/Tiros Libres`, `Jugador JJ TP Prom`). Root CDX: 9 captures,
   4 distinct digests, param hit `?grupo=BS22&serie=1`. 2002-05→2003-10.
3. **`mvp.asp` at root** (`bsnpr.com/mvp.asp`, NOT `/estadisticas/mvp.asp`
   which is the 2007+ one already in `coverage_wayback.md`). Root CDX: ~10
   captures, params unknown. Unprobed — could be award history predating the
   2007+ `historic_awards.csv` range, could be a redirect stub.

**APPROACH (owner /btw — follow exactly):**
- **Enumerate `t` (and other param) values FIRST.** Fresh CDX query per target
  (`bsnpr.com/lidereshistoricos.asp*`, `.../lideres2002.asp*`, `.../mvp.asp*`),
  collect every distinct query string + capture count, write to
  `data/interim/cdx_historic_followup.csv`.
- **Probe ONE capture per distinct param value.** Fetch with `id_` raw suffix
  via `polite_get`. **Read the page header / `<title>` / first table caption to
  confirm what that value actually is. DO NOT assume what any `t` value means**
  (t=3 being "históricos" does not tell us t=1, t=2, … — Spanish category
  labels only, confirmed from the page itself).
- **Then fetch the rest** of each confirmed-useful param value (all targets are
  well under the 500 gate — no owner approval needed for the bulk fetch, but
  report counts before fetching per PC4).
- **Parse into `data/clean/` with full provenance** (PC3). Likely outputs:
  extend `historic_scoring_champions.csv` / a new `historic_season_leaders.csv`
  (rebounds/assists all-time-by-year), `player_season_leaders_2002.csv`
  (mirror the 2000_2002 schema), `historic_awards.csv` rows if `mvp.asp` has
  pre-2007 content. `player_raw` stays verbatim — D1 resolution is a later join.
- Keep raw in `data/raw/pre2007/{lidereshistoricos,lideres2002,mvp}/` (PC5).

Cross-refs: `docs/specs/archive_probe_spec.md` (t=3 probe),
`docs/specs/pre2007_ingest_spec.md` (lideres200x schema, D4 metric boundary),
`data/clean/historic_scoring_champions.csv` (1948–2004, the overlap to dedup).

</details>

### PHASE_3F_IDENTITY_LIFT — COMPLETE (2026-09-08, owner-directed). Code-only, no fetch.

Owner instruction: club-code corroboration as a 2nd identity signal
(NEXT_ACTIONS 2a / identity_spine_spec Q2). Detail: `identity_spine_spec.md`
(points 5–6, RATIONALE, Q2 closed).

- **`_load_club_resolver()`** in `parse_players.py` — maps any club string
  (5-char `lideres200x` code, 2-letter `equiposstat` code, `"Nick de City"`,
  career `"Nick, City"`, bare nick/city) → one stable franchise key, from
  `club_code_map` + `city_franchise_map` + `franchises`. Observed club and the
  `jugador.asp` career team names both go through it. Thin-master fallback =
  `nick_city` synthetic; ambiguous bare nick → `""`.
- **`build_id_map`** — new branch: `>1 season-corroborated` candidates + the
  club uniquely picks one → `player_id_map.csv`, `match_method=name+season+club`
  (club is a **tiebreaker within** the season test, never overrides it).
- **Results:** id_map **423 → 433** (+10 `name+season+club`); review queue
  **828 → 818**; "multiple players match name+season" bucket **15 → 5**; 42
  review rows now carry `club_match_ids` (which candidate the club points at —
  makes manual resolution point-and-click). New `club_check` column on every
  id_map row {confirms 311 / no_obs_club 84 / contradicts 36 / no_career_club 2}
  — **advisory only, PC4**: `contradicts` = the career table shows a different
  club for an adjacent season (stale/gappy table, mid-season move, or thin
  master), NOT a wrong match; rows stay mapped + flagged.
- **The 106 "multiple name candidates, none corroborated by season" bucket did
  NOT shrink** — those candidates have no career data at/near the observed
  season, so club has nothing to test against. Blocked on career-span data
  (identity_spine_spec Q3: `jug05.asp` fetch or a manual historic seed), not on
  the club signal. Reported straight (PC1) rather than forcing thin matches.

- T3F.1 — DONE. `_load_club_resolver` + 7 unit tests (`test_parse_players.py`).
- T3F.2 — DONE. `build_id_map` club tiebreak + `club_check` + review enrichment.
- T3F.3 — DONE. `verify_players`: `club_check` values valid; every
  `name+season+club` row is `club_check=confirms`; D1 assertion widened to
  accept "club" as corroboration. `make verify` green (326,177, +2).
- T3F.4 — DONE. `identity_spine_spec.md` updated (Q2 closed), session.md.

**Verify:** `make verify` green (326,177 checks); `make test` **136 pass** (+7).
`players_canonical` / `player_aliases` / `player_career_seasons` byte-unchanged
(deterministic). Paused (P6), nothing committed (P4).

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

### PHASE_5_APP_SYNC — STARTED 2026-09-08. Sub-phased; one sub-phase per turn, pause + approve between.

**⚠️ STALE-FILE CORRECTION (2026-09-09).** 5A–5D were done against a stale
**2,214-line `app/bsn_archivo.html`**. The real file (owner-supplied 2026-09-09)
is **6,286 lines / 519 KB**, ~90 data blocks, **48 `build*()`**, a 55-builder
batched-RAF boot behind a splash, a `PROFILE` system, deep-link routing.
- **5A rewritten** (`app_data_map.md`, 2026-09-09) — the "~4 CSV blocks" finding
  is wrong: the app is a polished gap-honest product and the pipeline
  (PHASE_3C/3D/3E) has already produced most of what `buildSources()` calls
  *missing* (box scores, historic leaders 1948–2004, MVP 1958–2004, standings
  2001–13). PHASE_5 = (1) small sync + (2) **feed the app's existing features**
  (player index, season table, `DATASETS`, `buildSources`) with that data.
- **5B / 5C survive** — they read `data/clean/` only (D-044). Patches: add `cac`
  / `caciques_humacao` to the crosswalk + pipeline; re-verify the app-vs-CSV
  champion diff (regex still matches the real `F`). `franchise_curated.json` =
  0 diffs on the 32 shared keys.
- **5D lost** (was uncommitted, overwritten) → full redo against `runBoot()`.

**Decision (`app_data_sync_spec.md`, committed e5609ee): static JSON generated at
build time, fetched at runtime, GitHub Pages. Supersedes PC7.**

**Risk that shapes the sub-phasing (B4):** the app's embedded blocks are NOT all
CSV-derived. Some are hand-curated with no CSV source (team colours tagged
`wiki`/`approx`, coaches, arena capacities, franchise `note:` lines, Hall-of-Fame
curation, the Juega game/quiz/draft data, the rules text). The build script must
only regenerate blocks with a real CSV source and leave the curated ones intact
(PC1 — never present curated data as sourced). 5A settles exactly which is which
before any code is written.

Owner rule for this phase: **one sub-phase per turn, verify, pause for approval.
Do not run the whole rebuild in one shot.**

#### 5A — DATA MAP + JSON SCHEMA (spec only, no code) — v1 2026-09-08, **REWRITTEN 2026-09-09**
`docs/specs/app_data_map.md` (H2). v1 analysed the stale 2,214-line file; the
rewrite is against the real **6,286-line** one.

**Rewrite finding — the v1 "~4 CSV blocks" is wrong.** The real app is a
polished gap-honest product, and `data/clean/` has already produced most of what
`buildSources()` tells the user is *missing*:

| App UI says missing | Pipeline has |
|---|---|
| "No hay boxscores. Ninguno." | `game_box_player.csv` 39,669 rows / 1,292 games |
| "estadísticas por temporada … anterior a 2011 — el muro real" | `historic_scoring_champions` 1948–2004, `player_season_stats_2001_2004`, `player_season_leaders_2000_2002` |
| "Posiciones completas solo de 2009, 2025 y 2026" | 5C standings 2001–03 + 2008–13 |
| "MVP por año: 39 recuperados" | `historic_awards` MVP 47 rows 1958–2004 (+ROY, DPOY) |

**So PHASE_5 = two tracks:**
1. **Sync** — `F.won/ru` + `champOf/ruOf` (`champions_reconciled`), `SCORING`
   26→~68 (`scoring_champions_reconciled`), `F` factual (`franchises`).
2. **Feed existing features** with CSV-only data — `buildPlayerIndex` (3,303 vs
   ~few-hundred + `players/<id>.json`), `showSeason` (← `seasons/<year>.json`),
   `DATASETS` query builder (+ box scores / historic leaders / standings),
   `buildSources`/`buildCoverage` (the gap text is now partly wrong). Per-feature
   sub-phases, not one commit.

**The app already merges provenance-tagged blocks at parse time** (`translate()`,
`POOL_PATCH`/`POOL_RGM`/`PLAYERS_NEW` merge, legend-criterion IIFE). `hydrate()`
is one more such step — async, layered, never editing a source block.

Curated-inline (no CSV): ~40 blocks incl. `BIO PLAYERS_NEW POOL* HOF ARENAS
FINALS_* NEWS SEASON_STATE VENUES GAMES GLOSARIO HUB CATS NOTES COVERAGE OWNERS
MVP_YEARS SEASON_AWARDS` — the build script must never touch these (PC1).

**Verify:** every real-file block classified in the spec table; no curated-only
block marked CSV-derived (PC1); the 5B/5C `web/data` schema still holds; the
`caciques_humacao` gap + 5D boot-architecture plan documented. No code touched.

#### 5B — build skeleton + crosswalk + manifest + index files — COMPLETE 2026-09-08 (survives the stale-file mistake — D-044)
- `app/franchise_key_map.csv` — 32 app 3-letter keys ↔ 33 `franchise_id`
  (curated; `santos_san_juan` documented as no-app-key per D5). Build asserts
  completeness (D-040).
- `app/franchise_curated.json` — colours / abbr / coach / note / end for the 32
  keys, mechanically extracted from the app `F` block; the source for those
  fields from now on.
- `src/build_web_data.py` (`make build-web-data`). Emits `web/data/manifest.json`
  (`source_digest` = sha256 of the input files — no wall-clock, no git state,
  D-041) + `web/data/index/{franchises,seasons,players,scoring_titles,
  career_leaders,records}.json` per the 5A schema. Deterministic
  (`json.dumps(sort_keys, separators=(",",":"))` + `\n`; `_int`/`_float` →
  null-not-zero, PC2). `web/` tracked. **728 KB** total (players.json is the bulk).
- `verify_web_data()` in `verify_clean.py` — JSON valid, manifest counts match,
  32 keys, real franchise_ids, seasons == `champions_reconciled`, no `0`-for-year.
- Build-time diff report: **app vs `champions_reconciled` = 0 disagreements**
  (the app's championship data is already consistent with the reconciled CSV).

**5B surfaced a PHASE_3D name bug (fixed here, own commit):** 725/3,303
`players_canonical` names were `"<Surname>, Estadísticas Jugador"` — the
`jugador.asp` heading scan had grabbed a section header. `clean_field()` now
nulls that + `"No se sabe"` (position) + `"nan"` (all fields). Cascade: id_map
**433 → 649**, review queue **828 → 602** (the "no canonical name match" bucket
346 → 199 — those observations couldn't match a mangled name). D-042.

**Verify:** `make verify` green (329,499); `make test` 148 pass (+12); build
deterministic (rerun = byte-identical); crosswalk assert covers all keys/ids.

#### 5B-FIX — crosswalk + `caciques_humacao` — COMPLETE 2026-09-09 (owner-resolved D2)
Real `F` = **33 keys** (adds `cac`). **Owner 2026-09-09 + Wikipedia:** Caciques
de Humacao and the 2021 Grises de Humacao are **two distinct franchises** —
`caciques_humacao` = one continuous chain (Toritos de Cayey 2002–04 → Grises de
Humacao 2005 → Caciques 2010 → relocated ~2019), `grises_humacao` = a **new 2021
expansion** → Criollos de Caguas 2024. App splits them as `cac`/`hum` already.
- `franchises.csv` — +`caciques_humacao` (founded 2005, relocated ~2019);
  `grises_humacao` founded corrected **2005 → 2021**, status → "renamed 2024 ->
  criollos_caguas".
- `city_franchise_map.csv` — **HUMACAO → `caciques_humacao`** (all archived
  Humacao games are 2008–2013, inside its era; the 2021 Grises never had games).
- `franchise_events.csv` — +`relocated_renamed 2005 toritos_cayey →
  caciques_humacao` (`verified`); the Grises→Criollos row upgraded
  `single-source 2023` → **`verified 2024`** (Wikipedia "a new franchise").
- `franchise_key_map.csv` + `franchise_curated.json` — **33 keys** (`cac`
  added; re-extracted from the real `F`, 0 field diffs on the other 32).
- `verify_web_data` + 2 tests bumped **32 → 33**.

**Verify:** `make build-web-data` (33 franchises; `cac` = caciques_humacao,
lineage from toritos_cayey; Humacao standings 2009/2012 → caciques_humacao);
`make verify` green (329,507); `make test` 153 pass; rebuild = byte-identical.
`diff_app_champions()` regex confirmed matching the real `F` — still "0
disagreements". `reconcile_spec.md` [OWNER_RESOLUTIONS] updated.

#### 5C — per-entity JSON: players/ + seasons/ + games/ (box scores) — COMPLETE 2026-09-09 (survives — D-044)
`build_web_data.py` +3 builders (`build_players_detail`, `build_seasons_detail`,
`build_games`) + `_team_resolver` (`team_raw` city name → `franchise_id` via
`city_franchise_map`). `_reset_dir()` clears each generated subtree first so a
rebuild after the data shrinks leaves no orphan.

- **`web/data/players/<id>.json` — 1,076 files.** Only ids with a profile,
  career rows, or an id_map observation; the other ~2,227 are index-only
  (`players.json` has their light record). Carries aliases, birth, career
  (per-season team + resolved `franchise_id` + games/points), and the id_map
  observations with `match_method`/`club_check`.
- **`web/data/seasons/<year>.json` — 98 files** (1930–2026). champion/runner-up
  + `scoring_champion` (historic 1948–2004) + `awards` (DPOY/ROY/MVP) + `leaders`
  (1986 + 2000–2021, Spanish categories mapped to `scoring`/`rebounds`/…) +
  **`standings` derived from `game_results`** (W–L, `games_recorded`,
  `complete` = ≥140 games — most seasons are partial, flagged not hidden per
  5A OQ4) + `coverage.{stats_tracked, gaps}` (PC2/PC4). Unknown → `null`, never
  an empty list (verify asserts 1953/D6 carries nulls).
- **`web/data/games/<season>/<game_id>.json` — 1,292 files** + 9
  `games/<season>/index.json`. Box score (16 stat fields, each `int|null` —
  unresolved `bsnpr_id` stays `null`, PC2), `box_check`, quarter scores
  (trailing padding zeros trimmed), resolved `franchise_id` per side, `sources`.
- `verify_web_data` +12 checks (manifest counts, file-set == CSV game_ids,
  every player file id in the index, PC2 spot-checks). +5 unit tests.

**Tree: 2,483 files / 18 MB** (`games/` 13 MB = the box-score corpus, `players/`
4 MB). Tracked (packs to ~4–5 MB; per-entity ⇒ minimal churn per rebuild). If
this becomes a problem, 5G can build `web/data` in CI instead of committing it.

**Found (own follow-up, not fixed here):** id **13352** has a `player_career_seasons`
row but no `players_canonical` entry — a `jugador.asp` career for an id the
enciclopedia doesn't list. `build_players_detail` skips it (would be an
unnamed/unsearchable file); `parse_players.build_canonical` should pick up
career-only ids. → NEXT_ACTIONS.

**Verify:** `make verify` green (329,507); `make test` 153 pass (+5); build
deterministic (rerun = byte-identical); spot-checks vs CSVs pass
(player 37 = 17 career rows; game BS21001 = 21 box rows, 95–82).

#### 5D (redo) — app fetch layer — COMPLETE 2026-09-09 (owner-reviewed plan first)
`app/bsn_archivo.html` **+75 / −4**, 4 spots — additive, no `const` block removed
(they're the `file://` baseline). 4 edits:
1. **`DATA` object** after the `ST` wrapper. `base = file:` → `null` ⇒ `get()`
   returns `null`, 0 fetches, 0 console noise; else `new URL('data/',
   location.href)`. Cache memory → `bsn:data:*` localStorage (via the real `ST`:
   `ST.json` 1-arg, `ST.setJSON`, `ST.del`, `ST.keys`) → network.
   `syncVersion()` re-fetches `manifest.json` each load, purges `bsn:data:*` on
   a `source_digest` change.
2. **`deriveChampions()`** — the `champOf`/`ruOf` build wrapped in a re-runnable fn.
3. **`hydrate()`** — merges `index/franchises.json` over `F`: factual fields
   replaced, curated (colours/coach/abbr/note) kept, `won`/`ru` = **UNION**
   (D-043 — keeps 1945/D5 + 1942-43/D3; build-time diff = 0 conflicts). Then
   `deriveChampions()` + `ACTIVE` refresh. Early-returns on any fetch miss.
   No `build*()` touched.
4. **`runBoot()` → `async`**; `await Promise.race([hydrate().catch(()=>{}),
   setTimeout 2500])` before the RAF batch loop. Splash covers the wait.

SCORING sync = 5D.2; `showPlayer`/`showSeason` per-entity fetches = 5D.3.

**Verify:** `node --check` clean; DOM-stubbed harness (`scratchpad/boot_harness.js`)
— `runBoot()` completes, **all 55 BOOT builders + `finishBoot` run with 0
exceptions** in both `http:` (2 fetches: manifest + franchises) and `file:` (0
fetches) modes. `champOf` 96 → 96 (**0 lost / 0 gained / 0 changed** — clean
superset; `champOf[1945]`=cap kept). `F.man.founded` 2014→**2023**,
`F.hum.founded`→**2021**, `F.bay.c1`/`.coach` unchanged (curated kept). `ACTIVE`
= 12. `make verify`/`make test` unchanged (329,507 / 153 — HTML only). Browser
render-parity is the owner's check.

#### 5D.2 — hydrate SCORING — COMPLETE 2026-09-09
- `build_scoring_titles`: every `scoring_titles.json` entry now carries
  `club_raw` + `franchise_id` (seed club → `historic_scoring_champions.team_raw`
  → `player_season_leaders` club, resolved by a new `_scoring_club_resolver` =
  city map + full name + unambiguous nickname). **66/68 resolve a franchise_id.**
- `hydrate()`: fetches `index/scoring_titles.json`, rebuilds `SCORING` in place
  **26 (1966–91) → 68 (1948–2021)**. One row/year; 1971 & 1974 use the **ppg**
  champion (matches the baked-in table). Club = `F` name when resolved, else raw.
- `buildScoringChart` — hard-coded ticks `[1971..1991]` + aria-label made
  data-driven; `DATASETS.anotacion.label` → a getter reading `SCORING`'s range.
- `verify_web_data` +3 checks; +1 test assertion.
- **Owner browser check found the club column all "—".** Diagnosis (repro'd in
  the harness): the served `web/data/scoring_titles.json` was the pushed HEAD
  (5D-redo) version, which predates 5D.2's `club_raw`/`franchise_id` fields —
  so `club(c)` fell through to `undefined || '—'` for every row. Fixes:
  (a) `hydrate` keeps the **baked-in club** as a final fallback, so an
  older/stale `scoring_titles.json` keeps the 1966–91 names instead of blanking
  the whole column; (b) `hydrate`'s F-merge made **surgical** — only
  `founded`/`active`/`end`/`won`/`ru` from the JSON, `name`/`city`/colours/coach
  stay baked-in (accented Spanish forms; the CSV's are accent-stripped). The
  real fix for the owner is to push 5D.2 + re-snapshot `web/data/`.

**Verify:** `node --check`; harness — SCORING 26→68 (1948–2021), samples
`[1967,"ADOLFO PORRATA","Capitalinos de San Juan","total",516]` /
`[1971,…,"Cangrejeros de Santurce","ppg",22.4]` / `[2013,…,"Vaqueros de
Bayamon","ppg",18.2]`; `file:` keeps the 26-row baked-in; 0 boot exceptions
both modes. `make verify` green (329,510); `make test` 153 pass; `web/data`
rebuild byte-identical.

#### 5D.2b — MVP_YEARS ↔ historic_awards merge — QUEUED
`MVP_YEARS` (41, hand-verified, per-year clubs) vs `historic_awards.csv` MVP
(47, 1958–2004). Merge with the diff shown; own sub-step.

#### 5D.3 — feed player/season views from `web/data` per-entity JSON — split 3 ways
**Match-rate finding:** the app's ~385 curated PINDEX names and the pipeline's
3,303 `players_canonical` are largely disjoint. Auto-matching a curated name to
a `bsnpr_id` (norm / alias / swapped order): **only 103/385**. Georgie Torres,
Raymond Dalmau, Neftalí Rivera etc. are *in* `players_canonical` but under forms
like "Torres Dougherty, George" that no rule bridges; recent imports aren't in
the pipeline at all. So a naive list-swap would gut the curated feature. →
split: **5D.3a** (showSeason — no matching), **5D.3b** (showPlayer career
detail, needs a hand-seeded `curated_name → bsnpr_id` crosswalk with owner
spot-check), **5D.3c** ("Todo el archivo (3,303)" search mode alongside the
curated "Destacados").

##### 5D.3a — `showSeason` from `seasons/<year>.json` — COMPLETE 2026-09-09
`app/bsn_archivo.html` +57/−9. New `<div id="seasonExtra">` after `#readout`;
`showSeason` restructured (return→if/else) + fire `loadSeasonExtra(y)`; new
`async loadSeasonExtra(y)` fetches `data/seasons/<y>.json` (via `DATA`, so
`file://` → null → nothing extra) and appends, in a `.card`:
- `scoring_champion` (57/98 seasons) — "Campeón de anotación: NAME · club · N por juego"
- `awards` (47/98) — MVP / Defensa del Año / Novato del Año, `<dl class="kv">`
- `standings` (9/98) — mini G/P table + "parcial, N juegos" note when `!complete` (PC4)
- `leaders` (15/98) — rank-1 per category
Player names stay `player_raw` text (no `showPlayer` link — that's 5D.3b).
Stale-click guarded by `host.dataset.y`. **Verify:** `node --check`; season
harness — 1974 shows scoring champ + awards, 2009 shows standings + leaders,
`file:` = 0 fetches + nothing extra, stale-click (2009→1953) doesn't leak;
boot harness still 0 exceptions / 55 builders; `make verify` (329,510) / `make
test` (153) unchanged (HTML only). **Owner:** browser render parity.

##### 5D.3b — `showPlayer` career detail — CROSSWALK BUILT, AWAITING OWNER SIGN-OFF
`app/player_crosswalk.csv` — `curated_name,bsnpr_id,canonical_name,career_span,
verdict,confidence,flag,evidence`, one row per curated PINDEX name (386).
Matcher `scratchpad/xwalk_match.py`: curated BIO full-name + birth date + HOF
span + scoring years + clubs + nicknames, scored (fuzzy Levenshtein ≤2 on
full-name/alias, birth-year ±0) against `players_canonical` + `player_aliases`
+ `player_career_seasons` + `player_id_map`. Verdicts: **113 auto** (strong
name/alias + birth year), **45 review** (surname + swap + decade/club only —
owner confirms each id), **228 none** (no confident match; 5 explicit
rejections with note — incl. Arnaldo Toro Jr vs Sr, José Ortiz ambiguity).
Only ~78/158 matched ids have a built `web/data/players/<id>.json` today (rest
are career-less canonical rows).
Georgie Torres fixed: 790 → **788** "Torres Dougherty, George" (fuzzy full-name).
Rolando Frazer → **2089** now clean after D-046 (was "Frazer Thorne, Error 404").
**Open Q for owner:** emit a thin `players/<id>.json` for every canonical row
(no career table) so the 82 career-less matches still get a real card, or fall
back to curated-only + "sin ficha detallada"?
Then `showPlayer` looks up an embedded `PLAYER_XWALK` block → fetches
`players/<id>.json` → career-by-season table + fills null stats, curated
bio/tags/warning kept on top.

##### 5D.3c — "Todo el archivo (3,303)" search mode — QUEUED
`renderPlayerIndex` mode toggle: "Destacados (385)" (default) / "Todo (3,303)"
from `index/players.json`. No-JSON ids (2,227) → card shows index fields + an
explicit "sin ficha detallada" note (PC4). Optional `build_web_data` change:
add a `search` alias string to `players.json`.

#### 5D.4 — fix `buildSources` / `buildCoverage` gap text — QUEUED
The app's "lo que falta" list and `COVERAGE` %s are now partly wrong (box scores,
standings 2001–13, MVP 1958–2004 all exist). 5D proposes the factual
corrections; owner phrases them.

#### 5E — PWA: service worker + offline cache + web manifest — after the 5D chain
`web/sw.js` (cache the shell + fetched JSON, cache-first with network
revalidate), `web/manifest.webmanifest` (installable). Register from the shell
behind a feature check. **Verify:** SW registers; second load works offline
(DevTools → offline); install prompt appears; no SW errors on `file://`.

#### 5F — PBP per-game JSON (gated, likely stays deferred)
`web/data/games/<season>/<game_id>_pbp.json` — emitted **only** for games whose
`actor_raw` is `bsnpr_id`-linked (spec [INTERFACES] / OQ2). Depends on the
still-open PBP→identity linking task. Include as queued; execute only once
linking exists, else ship the PBP tab as "beta, per-game" per spec OQ2 default.

#### 5G — GitHub Pages deploy
Choose `/docs` output vs `gh-pages` branch (spec OQ1 default: GitHub Pages,
`/docs`). Wire `make build-web-data` output + the shell into the served path;
document the one-time repo Pages setting (owner action). **Verify:** live URL
loads, tabs work, PWA installs from the deployed origin.

**Sequencing:** 5A → 5B → 5C → 5D → 5E → (5F when linking lands) → 5G. Each is a
`[PAUSE_CONDITIONS] P6` stop. 5D and 5G also touch outward-facing surfaces
(the app file; a public deploy) — extra care / explicit approval.

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
- B4 — **BEING RESOLVED by PHASE_5_APP_SYNC (started 2026-09-08).** The
  codegen-vs-runtime call is made (`app_data_sync_spec.md`: static JSON at build
  time + runtime fetch). PHASE_5 is sub-phased 5A–5G in [TASK_QUEUE]; until 5D
  lands, the CSVs remain source of truth and the app is stale.
  <details><summary>original B4</summary>
- B4 — **`data/clean/` and `app/bsn_archivo.html` are two unsynchronized copies
  of the same data.** The app carries its dataset as hand-written JS literals;
  the CSVs are edited independently. Every data change has to be made twice and
  they already disagree in places. PHASE_5_APP_SYNC fixes this, but the
  codegen-vs-runtime-loading choice is a **P2 architectural decision requiring a
  spec file** (`docs/specs/app_data_sync_spec.md`) before any change to the app.
  Until then, treat the CSVs as the source of truth and the app as stale.
  </details>

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

Decisions made session 002 (PHASE_5_APP_SYNC):
- **D-046 — 404-page jugador.asp snapshots leaked into player names; fixed at
  parse (owner-flagged, 5D.3b).** 3 profiles (ids 405, 1926, 2089) were
  canonically `"<Surname>, Error 404"` — the Wayback capture of
  `jugador.asp?id=N` was the site's "Error 404 - Not Found" page and the heading
  scan grabbed "Error 404". `parse_jugador` now skips a capture whose `<title>`
  matches `error \d{3}`, so the enciclopedia name wins: 2089 → **"Frazer
  Thorne, Rolando"** (b.1958-07-03; "Frazer Thorne" is a legit two-part
  surname, NOT corrupt — only the appended error string was), 1926 → "Ramos
  Manso, Ramon", 405 → "Martin, Counzo". `clean_field` also strips an inline
  `error/http/status <3-digit>` token as defence-in-depth. Scan of
  `players_canonical` found only these 3 (all one root cause). Knock-on:
  `has_profile` 1076→1073, aliases 24076→24071, `web/data/players/{405,1926,
  2089}.json` become index-only. Bonus: Rolando Frazer's review-queue
  observations (`ROLANDO FRAZER` 1981/1982 scoring champ, `Frazer, R.` Coamo
  2001, `Frazer, Rolando` 1986) now resolve to id 2089 — they were "no
  canonical name match" against the corrupt name.
  Same rebuild also flushed **pre-existing `web/data` drift**: 5B-FIX (77a3aae)
  committed the D-045 franchise CSVs without rebuilding `web/data`, so
  `observations[].club_check` for ~11 Caciques/Grises de Humacao players was
  stale. Rebuilt now. Also: `_load_club_resolver` marks the bare nick "Grises"
  ambiguous (D-045 — two Humacao franchises reuse it, resolver is season-blind);
  "Grises, Humacao" still resolves by city → `caciques_humacao`, bare "Grises"
  → unresolved (advisory `no_obs_club`) instead of a false contradiction.
  club_check is advisory only — no identity mappings changed (id_map still 649).
- **D-045 — Grises/Caciques de Humacao = two distinct franchises (owner
  2026-09-09 + Wikipedia).** `caciques_humacao` = the continuous chain Toritos
  de Cayey (2002–04) → Grises de Humacao (2005) → Caciques (2010) → relocated
  (~2019); NEW `franchise_id`, gets the archived Humacao games (2008–2013).
  `grises_humacao` = a separate **2021** expansion → Criollos de Caguas 2024
  (Wikipedia: "a new franchise", not a continuation) — `franchises.csv` founded
  corrected 2005→2021, both `franchise_events` rows now `verified`. App keys
  `cac`/`hum` map 1:1. `reconcile_spec` OQ2 closed; `docs/project.md` D2 needs
  an owner refinement.
- **D-044 — the app file used for 5A–5D was stale; the pipeline outputs are the
  salvage.** 5A–5D were built against an inherited 2,214-line
  `app/bsn_archivo.html`; the real file (2026-09-09) is 6,286 lines. **5B/5C
  survive** because they read `data/clean/` only — the `web/data/` tree is
  correct regardless of the app. `franchise_curated.json` = 0 field diffs on the
  32 shared `F` keys. **5D is lost** (uncommitted, overwritten). Lesson for the
  handoff: anything that parses or edits `app/bsn_archivo.html` must be
  re-checked against the real file; anything that only touches `data/clean/` or
  `web/data/` is safe. The rewritten `app_data_map.md` is the authority now.
- **D-043 — `hydrate()` UNIONS `won`/`ru`, never replaces.** The reconciled
  `champions_reconciled` omits two seasons the app deliberately carries: 1945
  (D5 — shown as Capitalinos with a caveat `NOTES[1945]`) and the 1942-1943
  split (D3). `build_web_data`'s build-time diff confirms **0 season CONFLICTS**
  between app and CSV, so a union of the two title lists only ever re-adds what
  the CSV leaves out — it cannot resurrect a title the CSV corrected. Curated
  franchise fields (colours/coach/abbr/note) are likewise kept from the embedded
  `F`, not overwritten. The app stays a strict superset of the reconciled data.
- **D-042 — `jugador.asp` placeholder text is nulled at parse (PC1/PC2).**
  `clean_field()` in `parse_players` maps `"Estadísticas Jugador"` (a section
  header the heading scan grabbed — 725 profiles), `"No se sabe"` (position),
  `"nan"` (pandas NaN) → `""`. Surfaced building the web player index (5B). Fixes
  725 canonical names; cascades to id_map 433→649, review 828→602 (a mangled
  name matched no observation). `verify_players` now asserts no canonical_name
  carries placeholder text. Own commit, tagged PHASE_3D/3F.
- **D-039 — PHASE_5 scope is narrow: sync 4 blocks, expose the rest as new
  JSON.** 5A found the app is ~90% hand-curated editorial with no CSV source
  (`app_data_map.md` classification table). The build script (`make
  build-web-data`, 5B+) regenerates ONLY `champOf`/`ruOf`, `F.won`/`F.ru`,
  `SCORING`, `LEADERS`, `RECORDS`, and the factual columns of `F` — and MUST
  leave `RECENT`/`HOF`/`CLINCHERS`/`ON_THIS_DAY`/`REF_*`/`POOL`/colours/coaches
  untouched (PC1 — never regenerate curated prose from a CSV). The larger deliverable
  is per-entity fetched JSON for the CSV-only archive (players, games, box
  scores, historic scoring/awards, standings) the app cannot show today.
- **D-040 — franchise-key crosswalk is a checked-in curated file, asserted
  complete at build time.** `app/franchise_key_map.csv` (32 app 3-letter keys ↔
  33 `franchise_id`). Not name-similarity-derived (D5's `santos_san_juan` and
  the Manatí Osos/Atenienses era-ambiguity break that). Mirrors D-029 /
  `club_code_map`. A build that finds an unmapped id or key fails.
- **D-041 — `web/data/` build is deterministic; version = a digest of the
  inputs, not a timestamp or git SHA.** `json.dumps(sort_keys=True,
  separators=(",",":"))` + `\n`, fixed float precision. `manifest.json.
  source_digest` = sha256 over the exact bytes of every input CSV + curated
  file. No wall-clock, no `git` call (avoids the chicken-and-egg of committing
  an artifact that records its own commit) ⇒ rerun on unchanged inputs = empty
  git diff (spec [INTERFACES]). `web/` is a tracked deploy artifact, not
  gitignored.

Decision made session 002 (PHASE_3F_IDENTITY_LIFT):
- **D-038 — club-code is a season-test *tiebreaker*, never a substitute or a
  veto.** Wired into `parse_players.build_id_map` via `_load_club_resolver()`.
  A link enters `player_id_map` on club grounds only when the season test
  already corroborates >1 candidate and the club picks exactly one
  (`match_method=name+season+club`, +10 rows). Club is NOT used to (a) map a
  row the season test rejects — that stays in review with a `club_match_ids`
  hint (the 106 bucket is data-limited, not signal-limited: D-022 stands), or
  (b) un-map a row where the club disagrees — `club_check=contradicts` (36
  rows) is advisory (PC4), because career-table club data has split seasons,
  stale modern rows, and D2 franchise-master gaps that make a contradiction
  unreliable. Resolver returns `""` for ambiguous bare nicknames rather than
  guess. `identity_spine_spec.md` points 5–6.

Decision made session 002 (PHASE_3G_HISTORIC_FOLLOWUP):
- **D-037 — PHASE_3G is a negative finding; no clean rows added.** Fresh CDX
  confirmed `lidereshistoricos.asp` has only `?t=3` (award histories, already
  parsed), `lideres2002.asp` was already covered by the PHASE_3C `lideres200x`
  sweep, and root `mvp.asp` is a byte-equivalent alias of
  `lidereshistoricos.asp?t=3` (0-diff cross-check vs `historic_scoring_champions`
  + `historic_awards`). Per D-018, `mvp.asp` raw kept as a 2nd provenance path,
  not re-parsed into duplicate rows; no `confidence` promotion (same bsnpr DB,
  not independent). The hoped-for all-time rebounds/assists/blocks leaders back
  to 1948 **are not in the archive** — newspaper/Federación track only. Probe
  spec's "unlabeled tables = rebounds/assists" guess was wrong (they're
  DPOY/ROY/MVP); archive_probe_spec Q2 closed. `historic_followup_spec.md`.

Decision made session 002 (PHASE_3E_CLEAN_STORAGE):
- **D-036 — large clean tables are committed gzipped (`<name>.csv.gz`), not
  raw, split, or LFS'd.** `data/clean/` is NOT regenerable from a fresh clone
  (raw gitignored, re-fetch = multi-day PC6 crawl), so every table must live in
  the repo — but `game_plays` at 65 MB tripped GitHub's 50 MB warning and added
  a fat blob to history every parse. gzip → 2.7 MB (24×), one file, stdlib-only,
  `pandas.read_csv` + `csv` read it transparently. `open_clean_text` (in
  `parse_wayback.py`) is the single choke point; `mtime=0` keeps reruns
  byte-stable. Git LFS rejected (clone/CI prerequisite, 1 GB/mo bandwidth cap,
  silent-pointer corruption mode); split-by-season rejected (pushes globbing
  into every consumer for a problem gzip closes in one helper); Parquet rejected
  (premature dependency). Threshold: raw CSV > ~20 MB. Full spec:
  `docs/specs/clean_data_storage_spec.md`. Existing 65 MB history blob NOT
  purged — needs owner OK (P1/G4), not worth it at `.git` = 10 MB.

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
| PHASE_5 / 5D (v1) | — | — | — | — | — | **VOIDED 2026-09-09 (D-044).** Built against the stale 2,214-line app; uncommitted, overwritten. Design carried forward to the redo. |
| PHASE_5 / 5D.3a | PASS | PASS | PASS | PASS | PASS | V1: `showSeason` appends per-season detail from `seasons/<y>.json` (scoring champ / awards / standings / leaders) below the champion readout; new `#seasonExtra` div + `loadSeasonExtra()`. No `build*()` / build-script change. V2: PC2/PC4 (`file://` → `DATA.get` null → nothing extra, base readout unchanged; missing block → not rendered, no "—" spam; partial standings flagged "N juegos en el archivo"; player names stay `player_raw`, no fabricated link); union-safe (append-only, never touches the existing readout logic beyond return→if/else). V3: no secrets. V4: `node --check`; season harness — 1974 scoring champ + awards render, 2009 standings + leaders render, `file:` 0 fetches, stale-click (2009→1953) doesn't leak; boot harness 0 exceptions / 55 builders; `make verify` 329,510 / `make test` 153 unchanged (HTML only). Owner: browser render parity. V5: reuses `.card`/`.kv`/`.tblwrap`/`.note`; matches idiom. |
| PHASE_5 / 5D.2 | PASS | PASS | PASS | PASS | PASS | V1: `build_scoring_titles` adds `club_raw`+`franchise_id` (new `_scoring_club_resolver`, 66/68 resolved); `hydrate()` rebuilds `SCORING` 26→68 (1948–2021), F-merge made **surgical** (founded/active/end/won/ru only — name/colours stay baked-in) and SCORING club falls back to the **baked-in** value for schema drift; `buildScoringChart` ticks/aria-label + `DATASETS.anotacion.label` data-driven; `verify_web_data` +3, +1 test. V2: PC1/PC2 (`file://` keeps the 26-row baked-in; 1971/1974 use the ppg champion as the baked-in table does; D4 `metric_era` per row); the 2 unresolved clubs → `club_raw`, not a guess; accented Spanish names no longer lost to the CSV form. V3: no secrets. V4: `node --check`; harness — SCORING 26→68 with clubs from JSON; **stale-schema harness** (`--stale-scoring`, HEAD's `scoring_titles.json`) → 1966–91 clubs kept from baked-in, 0 boot exceptions; `file:`=0 fetches; `make verify` green (329,510); `make test` 153 pass; `web/data` rebuild byte-identical. V5: matches idiom. |
| PHASE_5 / 5D (redo) | PASS | PASS | PASS | PASS | PASS | V1: `app/bsn_archivo.html` +75/−4 — `DATA` object (+ `syncVersion` digest cache-bust, real `ST` API), `deriveChampions()`, `hydrate()` (union merge over `F`, curated fields kept, `ACTIVE` refresh), `runBoot()` → async with a 2.5 s hydrate race. No `build*()` / DOM code touched; SCORING → 5D.2. V2: PC1/PC2 (`file://` → `null`, embedded blocks stand — no fabrication, no silent-zero; failed fetch → `null`); D5/D3 (D-043 union keeps 1945 + 1942-43); D-032/D-045 (Osos 2023, Grises 2021 flow through); house rule (layer over the source block like `translate()`, never edit). V3: no secrets; `DATA.base` is `data/` relative to the page. V4: `node --check` clean; DOM-stubbed harness — `runBoot()` + all 55 BOOT builders + `finishBoot` no-throw in `http:` AND `file:`; `file:` = 0 fetches; `champOf` after hydrate = 0 lost / 0 gained / 0 changed; curated colours/coach preserved. `make verify`/`make test` unchanged (329,507 / 153 — HTML only). Browser render-parity is the owner's check. V5: matches the file's terse JS idiom + `/* why */` comment style. |
| PHASE_5 / 5B-FIX | PASS | PASS | PASS | PASS | PASS | V1: `caciques_humacao` added to `franchises.csv` + `city_franchise_map` + `franchise_events` (owner D2, D-045); `grises_humacao` refounded 2021; crosswalk + curated JSON 32→33 (`cac`, re-extracted from real `F`, 0 diffs on the 32); `verify_web_data` + 2 tests 32→33. V2: PC1/D2 (two franchises per owner+Wikipedia, not a guess; `franchise_events` cites `wikipedia:Caciques_de_Humacao` / `Grises_de_Humacao`); the Grises→Criollos event upgraded single-source→verified with the source recorded; `docs/project.md` D2 flagged for owner (not edited — Tier 2). V3: no secrets. V4: `make build-web-data` (33 franchises, Humacao standings 2009/2012 → `caciques_humacao`); `make verify` green (329,507); `make test` 153 pass; rebuild byte-identical; `diff_app_champions` still "0 disagreements" against the real `F`. V5: snake_case, CSV note style matched. |
| PHASE_5 / 5A (rewrite) | PASS | PASS | n/a | n/a | PASS | V1: `app_data_map.md` rewritten against the real file — per-block table for the ~90 blocks, the two-track finding (sync + feed-existing-features), the `caciques_humacao` crosswalk gap, the `runBoot()` hydration point, 6 open Qs. V2: PC1 (the ~40 curated blocks incl. `BIO`/`POOL*`/`FINALS_*` explicitly "never touch"; `buildSources` flagged as now-inaccurate — PC4); the app's own "merge tagged blocks at parse time" pattern documented as the `hydrate` model. V3/V4: no code. V5: snake_case, links. |
| PHASE_5 / 5C | PASS | PASS | PASS | PASS | PASS | V1: `build_players_detail` / `build_seasons_detail` / `build_games` + `_team_resolver` + `_reset_dir`; `web/data/{players,seasons,games}/` (1,076 + 98 + 1,292 files); `verify_web_data` +12 checks; +5 tests. V2: PC2 (every game-box stat + year coerces to `null` not `0`; unresolved `bsnpr_id` stays `null`; a season with no standings/leaders is `null` not `[]` — verify asserts 1953); PC4 (`standings.complete` flags partial archive coverage; `coverage.gaps` per season); PC1 (id 13352 — a career with no canonical row — skipped, not invented; reported). V3: no secrets; reads `data/clean/` + `app/` only. V4: `make verify` green (329,507); `make test` 153 pass; **rerun = byte-identical tree**; spot-checks vs CSVs (player 37, game BS21001) pass; `_reset_dir` prevents orphans. V5: snake_case, English, "why" comments. |
| PHASE_5 / 5B | PASS | PASS | PASS | PASS | PASS | V1: `franchise_key_map.csv` (32↔33, asserted complete) + `franchise_curated.json` + `src/build_web_data.py` (`make build-web-data`) → `manifest.json` + 6 `index/*.json` per the 5A schema; `verify_web_data()` in `make verify`; +12 tests. V2: PC1 (only the 4 CSV-sourced blocks emitted; a build-time diff shows app vs `champions_reconciled` = 0 disagreements); PC2 (`_int`/`_float` → null not 0; verify asserts no `0`-for-year); PC4 (`coverage.gaps` reserved in the schema for 5C); D-040/D-041/D-042. V3: no secrets; reads `data/clean/` + `app/` only. V4: `make verify` green (329,499); `make test` 148 pass; **rerun = byte-identical `web/data/` tree** (determinism); crosswalk assert would `sys.exit` on any unmapped id/key. V5: snake_case, English, "why" comments. |
| PHASE_3D/3F name-fix (with 5B) | PASS | PASS | PASS | PASS | PASS | V1: `clean_field()` nulls `jugador.asp` placeholders; 725 mangled canonical names fixed; `verify_players` regression guard. V2: PC1 (placeholder text was being presented as a player name — removed at source, not band-aided in the projection); PC2 (`No se sabe`/`nan` → null). D1 unaffected — the +216 id_map rows are all `name+season(+club)` corroborated, just now matchable. V4: `make parse-players` + `make verify` green; `make test` 148 pass (+2 `clean_field`); id_map 433→649, review 828→602, deterministic re-parse. V5: snake_case. |
| PHASE_5 / 5A | PASS | PASS | n/a | n/a | PASS | V1: `docs/specs/app_data_map.md` (H2) — every embedded `const` block classified {regen from CSV · merge · keep curated}, full `web/data/` tree + per-record schema, build contract, 6 open Qs. V2: PC1 (curated editorial — `RECENT`/`HOF`/`CLINCHERS`/`ON_THIS_DAY`/`REF_*`/`POOL` — explicitly "keep inline, do not regenerate"; only 4 blocks have a real CSV source); PC2 (every schema field "null when unrecorded, never 0"); PC4 (`coverage.gaps` per season is a first-class output); PC7 superseded per `app_data_sync_spec.md`. V4/V3: no code, no secrets — `make verify`/`make test` unaffected. V5: `app_data_map.md`, snake_case schema names. Spec-only sub-phase; S3 (secret scan) / V4 (compile) n/a. |
| PHASE_3F | PASS | PASS | PASS | PASS | PASS | V1: T3F.1–T3F.4 done — `_load_club_resolver` + club tiebreak in `build_id_map` + `club_check` column + review-queue `club_match_ids` enrichment + verify + tests + spec. V2: PC1 (the 106 bucket did not shrink — reported straight, not force-matched); PC3 (id_map + review rows keep full keys; provenance unchanged); PC4 (`club_check=contradicts` surfaced in the column, 36 rows, not hidden and not acted on); D1 (club is corroboration *beyond* the name; only ever a tiebreaker *within* the season test — `name+season+club`; never name-alone); D-022 (season-corroboration still required for the map; club-only stays in review). V3: no secrets; pure module. V4: `make verify` green (326,177, +2 club checks); `make test` 136 pass (+7 club-resolver tests); `players_canonical`/`aliases`/`career_seasons` byte-unchanged; id_map 423→433, review 828→818, name+season bucket 15→5. V5: snake_case, English, "why" comments. |
| PHASE_3G | PASS | PASS | PASS | PASS | PASS | V1: fresh CDX per target (`cdx_historic_followup.csv`), probed + confirmed every param value from the page, reported what each is (see TASK_QUEUE). V2: PC1 (negative finding reported straight — no thin rows manufactured from a duplicate source; probe-spec's wrong guess corrected from the page's own section headers); PC3 (`mvp.asp` manifest tracked with provenance); PC4 (`t` gap reported as a gap — no other `t` value exists); PC5 (raw cached unmodified, gitignored); PC6 (`polite_get`, one GET/digest, single stream — `pgrep` confirmed no other fetcher); D-018 (duplicate `mvp.asp` source kept raw, not re-parsed). V3: no secrets. V4: `make verify` green (326,175 checks, unchanged — no clean data touched); `make test` 129 pass; `mvp.asp` 2006 capture cross-checked vs clean = 0 diffs / 57 scoring + 135 award rows. V5: snake_case, English, "why" comments. |
| PHASE_3E_CLEAN_STORAGE | PASS | PASS | PASS | PASS | PASS | V1: P2 storage call made + logged (`clean_data_storage_spec.md`, H2 structure, alternatives rejected); `game_plays.csv` → `.csv.gz` via shared helper; old blob `git rm`'d; `make parse-games` re-emits it. V2: PC1 (content byte-identical to committed `.csv`, `diff` = 0 — no data touched); PC3 (provenance cols intact, `verify` asserts them on the gz-read rows); PC5 (parser still reads `data/raw/` only, idempotent + deterministic via `mtime=0`); PC7 (no new dependency — `gzip`/`csv`/`pandas` are stdlib+existing). V3: no secrets; read-only on raw. V4: `make verify` green (326,175 checks); `make test` 129 pass (+4: gz round-trip / magic / determinism / plain-path); `pandas.read_csv` reads the gz (233,664×17); `_write_csv` log line hardened against out-of-repo paths. V5: snake_case, English, "why" comments; `.csv.gz` double-extension convention documented. |

---

[FILE_MANIFEST]

| Path | Status | Notes |
|---|---|---|
| `app/bsn_archivo.html` | real file = 46a0c5a; PHASE_5/5D* touched | **6,286 → ~6,430 lines** (was a stale 2,214-line inherited copy, replaced 2026-09-09). ~90 data blocks, 48 `build*()`, 55-builder batched-RAF boot behind a splash, `PROFILE` system, deep-link routing. 5D redo: `DATA` fetch layer + `hydrate()` into `runBoot()`. 5D.2: `SCORING` hydrates 26→68. 5D.3a: `showSeason` appends per-season detail from `seasons/<y>.json`. All additive — embedded blocks are the `file://` baseline. No build step, no deps. Do not restructure. |
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
| `src/parse_players.py` | new S002 (PHASE_3D); updated PHASE_3F | D1 identity spine builder. `make parse-players`. PHASE_3F: `_load_club_resolver()` + club tiebreak / `club_check` / review `club_match_ids` in `build_id_map`. |
| `tests/test_parse_players.py` | new S002 (PHASE_3D); +7 PHASE_3F | 19 unit tests — name normalisation + `_load_club_resolver` (`TestClubResolver`). |
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
| `data/clean/franchises.csv` | new S002 (PHASE_4); +`caciques_humacao` 5B-FIX | 34-row franchise master. D-045: Grises & Caciques de Humacao split into 2 ids. |
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
| `data/raw/games/**` | **new, S002 (PHASE_3E)** | Fetched game-script captures: `gamestatwide` 864, `pogamestat` 1021, `boxscore` 261, `a2gamestatpbp` 2001–2004 complete. gitignored. |
| `data/clean/game_results.csv` | **new, S002 (PHASE_3E)** | 1,287 rows — one per game, teams + quarter/final scores. Seasons 2001–03, 2008–13. Stub captures (blank score + no box) dropped; team-Totals-row score fallback. |
| `data/clean/game_box_player.csv` | **new, S002 (PHASE_3E)** | 39,669 player-game rows. `bsnpr_id` joined where D1-resolvable: **pre-2007 4,152/15,941 = 26%; 2007+ 17,599/23,728 = 74%; total 21,751/39,669 = 55%**. `fg2m/fg2a` and `fg3m/fg3a` kept separate. `box_check`: 39,663 `ok` / 4 `pts_mismatch` (source data-entry errors, flagged not rewritten). |
| `data/clean/game_plays.csv.gz` | **new, S002 (PHASE_3E; gzipped PHASE_3E_CLEAN_STORAGE)** | 233,664 play-by-play events, seasons 2001–2003 — from `a2gamestatpbp`. **gzip-compressed** (65 MB raw → 2.7 MB; D-036). `jugada_raw` verbatim + parsed `event_type`/`actor_raw`/`team_raw`. Classified ~70%: rebound 42,367 · made_2 23,482 · assist 19,794 · miss_2 19,132 · miss_3 17,301 · turnover 12,469 · made_3 8,925 · steal 8,290 · team_rebound 5,198 · timeout 4,029 · jump_ball 2,277; 70,400 unclassified. Read via `open_clean_text` / `pandas.read_csv`. |
| `docs/coverage_games.md` | **new, S002 (PHASE_3E)** | Per-script per-capture-year table; the >500 gated tranches. |
| `docs/specs/game_data_spec.md` | **new, S002 (PHASE_3E)** | Game-engine shapes, tranche gate, two id schemes, shot-cell conventions, open Qs. |
| `docs/specs/clean_data_storage_spec.md` | **new, S002 (PHASE_3E_CLEAN_STORAGE)** | P2 decision: large `data/clean/` tables committed gzipped (`.csv.gz`); the `open_clean_text` helper; Git LFS / split / Parquet rejected; >20 MB threshold; history-purge deferred. |
| `docs/specs/app_data_sync_spec.md` | new S002 (owner-supplied, e5609ee) | PHASE_5 decision: static JSON generated at build time, fetched at runtime, GitHub Pages. Supersedes PC7. |
| `docs/specs/app_data_map.md` | new S002 (PHASE_5 / 5A); **rewritten 2026-09-09** | The 5B–5G contract, vs the **real 6,286-line** app: per-block classification for ~90 blocks, the two-track finding (sync + feed existing features), `web/data/` schema, the `caciques_humacao` crosswalk gap, the `runBoot()` hydration point, D-044 salvage table. |
| `src/build_web_data.py` | **new, S002 (PHASE_5 / 5B)** | `make build-web-data` — `data/clean/` + `app/franchise_*` → deterministic `web/data/` static JSON (manifest + 6 index files). |
| `app/franchise_key_map.csv` | new S002 (PHASE_5 / 5B); 33 rows 5B-FIX | Curated crosswalk: **33** app 3-letter keys ↔ `franchise_id` (`santos_san_juan` has no app key — D5). Build asserts completeness. |
| `app/franchise_curated.json` | new S002 (PHASE_5 / 5B); 33 keys 5B-FIX | Colours / abbr / coach / note / end per app key — re-extracted from the **real** `F` block (33 keys). Source for those fields going forward. |
| `web/data/**` | new S002 (PHASE_5 / 5B+5C) | Tracked deploy artifact, `make build-web-data`. `manifest.json` + `index/*.json` (5B) + `players/<id>.json` ×1,076 + `seasons/<year>.json` ×98 + `games/<season>/<game_id>.json` ×1,292 + `games/<season>/index.json` (5C). **2,483 files / 18 MB.** PBP `_pbp.json` = 5F. |
| `tests/test_build_web_data.py` | new S002 (PHASE_5 / 5B+5C) | 17 tests — coercion, deterministic `_jdump`, crosswalk completeness, franchise merge, scoring dual-metric, per-entity shapes, `_norm`/`_team_resolver`, quarter trimming. |
| `src/parse_wayback.py` | updated S002 (PHASE_3E_CLEAN_STORAGE) | +`open_clean_text()` gzip-transparent clean-table IO (`mtime=0`, deterministic); `_write_csv` routes through it + hardened log line. |
| `src/enumerate_historic_followup.py` | **new, S002 (PHASE_3G)** | Fresh CDX per target (`lidereshistoricos`/`lideres2002`/`mvp` prefixes). `make enumerate-historic`. |
| `src/fetch_historic_followup.py` | **new, S002 (PHASE_3G)** | One GET per distinct 200-digest, `MAX_TRANCHE=500`, `--script`. `make fetch-historic`. No parser (negative finding — nothing new to parse). |
| `data/interim/cdx_historic_followup.csv` | **new, S002 (PHASE_3G)** | 27 captures across the 3 targets, every status. Tracked. |
| `data/interim/fetch_manifest_historic_followup.csv` | **new, S002 (PHASE_3G)** | Every 200 capture → local file. Tracked. |
| `data/raw/pre2007/mvp/` | **new, S002 (PHASE_3G)** | 7 `mvp.asp` captures 2004–2006. Byte-equivalent to `lidereshistoricos.asp?t=3`; kept as 2nd provenance (D-018). gitignored. |
| `docs/specs/historic_followup_spec.md` | **new, S002 (PHASE_3G)** | The negative finding: all 3 targets already ingested by PHASE_3C; what each param value is; `mvp.asp` 0-diff corroboration; no clean rows added. |

---

[NEXT_ACTIONS]

1. **Owner-directed queue (2026-09-08 session), in order, pause after each:**
   (a) PHASE_3E_CLEAN_STORAGE — **DONE** (`game_plays.csv.gz`, commit 72d2b52);
   (b) PHASE_3G_HISTORIC_FOLLOWUP — **DONE** (negative finding, commit 100e9c6);
   (c) PHASE_3F_IDENTITY_LIFT — **DONE** (b599e27).
   All three owner-directed items complete + pushed.
2. **PHASE_5_APP_SYNC — stale-file correction 2026-09-09 (D-044).** 5A rewritten
   vs the real 6,286-line `app/bsn_archivo.html` (`app_data_map.md`). 5B
   (4634dad) + 5C (8891d78) + D-042 (a22027c) survive — pipeline only. **5D
   lost.** Working tree has the real app file (uncommitted; "replace stale app
   file" commit = 46a0c5a). Queue: 5D redo (c22ce10) + 5D.2 (6c6c8a5) + **5D.3a DONE** (showSeason
   detail, uncommitted) → **5D.3b next** (showPlayer + crosswalk) → 5D.3c
   (full-archive search) → 5D.2b (MVP_YEARS) → 5D.4 (gap text) → 5E → 5G.
   5D.3 (feed player/season views) → 5D.4 (fix `buildSources` gap text) → 5E
   (PWA) → 5G (deploy). One sub-phase per turn, pause + approve.
   Owner HOLD still stands on `pogamestat`/`boxscore` 2007–09 and all `gameinfo`.
   PHASE_3D follow-up: id **13352** (career row, no canonical entry).
   Owner Tier-2 touch: `docs/project.md` D2 — refine "Grises → Criollos (2023)"
   per D-045.
3. **RANKED IDENTITY-LIFT PLAN** — box-score `bsnpr_id` resolution 26% pre-2007
   / 74% modern; review queue **602** rows (315 season-not-in-known-span · 199
   no-name-match · 79 multi-candidate-no-season · 9 multi-match) — post D-042.
   a. **DONE (PHASE_3F).** Club-code corroboration wired into
      `parse_players.build_id_map` — +10 `name+season+club`, name+season
      ambiguity bucket 15→5, `club_match_ids` hints on 42 review rows.
      identity_spine_spec Q2 closed. The 106 bucket did NOT move — data-limited
      (needs 2b/2c), not signal-limited.
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
4. **PHASE_3E parse follow-ups** — PBP + (if ever un-held) `gameinfo` metadata are
   separate parse targets (`game_data_spec` Q5/Q6). game↔franchise join (Q4).
   Box vs `player_season_stats_2001_2004` cross-check (Q7).
5. **PHASE_4 follow-ups** (reconcile_spec Q1–Q7): the 5 flagged conflicts +
   3 disputed franchise_events need an owner decision or a third source
   (es.wikipedia, Federación). Then: apply `player_id_map` → `bsnpr_id` columns
   on `player_season_*` / `player_season_stats_*` (after tranche B); reconcile
   `historic_scoring_champions` 1948–65 / 92–04 against es.wiki; career-leaders /
   records reconcile (D7 — floors only). wayback_ingest_spec Q9–Q12 still open.
6. **PHASE_4B_GAME_POOL** — rebuild the app's game pool from
   `champions_reconciled` + the identity spine + `player_season_stats_2001_2004`
   + `game_results` / `game_box_player`. Own scope.
7. Small ungated follow-ups: `playbyplay.asp` (460), `equipo.asp` (489),
   `informe.asp` (175, game reports 2004–06), `posiciones2000.asp` +
   `estadisticas.asp` cluster → `standings_pre2007.csv` (pre2007 spec Q4).
8. Roadmap newspaper track — now only needed for pre-2001 box scores and
   anything the archive genuinely lacks. Much narrower than before.
9. Human-side: B1 DevTools recon — value reduced (see B1); still useful for the
   current/post-2021 API.
10. `git`: PHASE_3 = 4ca04f2, 3B = 21f1a5f, 3C = a3b792a, 3D = 0d0d12d + 0640a1d,
   PHASE_4 = ac4a23e + d7c3024 + cd8ef54.
   PHASE_3E = d421922, e94fec9, 640964e, a041a60, 891fc12, 2d1928c, 7f09013.
   `app_data_sync_spec.md` = e5609ee. PHASE_3E_CLEAN_STORAGE = 72d2b52.
   PHASE_3G = 100e9c6. PHASE_3F = b599e27. PHASE_5/5A(v1) = dc776b3.
   D-042 name fix = a22027c. PHASE_5/5B = 4634dad. PHASE_5/5C = 8891d78.
   real app file = 46a0c5a. PHASE_5 5A-rewrite + 5B-FIX = 77a3aae.
   PHASE_5/5D redo = c22ce10 (all pushed). PHASE_5/5D v1 = VOIDED (D-044).
   PHASE_5/5D.2 = 6c6c8a5 (pushed). **PHASE_5/5D.3a** (`showSeason` detail,
   `app/bsn_archivo.html` +57/−9) + this `docs/session.md` update = pending P4.
