# SESSION STATE — TIER 3
<!-- Authoritative for current state and task priority. Update at every phase exit. -->

**SESSION:** 001 — repo bootstrap + Wayback enumeration
**DATE:** 2026-09-07
**MODEL:** Claude Sonnet 5 (claude-sonnet-5) via Claude Code

---

[SESSION_STATE]

PHASE_1_ENUMERATE complete. Environment bootstrapped (`.venv`, 19 passing tests),
Wayback CDX enumerated, coverage matrix produced, 3-snapshot probe run, ingest
spec written.

**The central finding is negative and it matters (PC4, resolves B2):** the
1957–2004 per-season `lideres.asp?anio=YYYY` pages that Wikipedia cites and that
this whole repo was built to recover **were never archived with content**. They
were crawled once (2021-07-09, IABot) *after* bsnpr.com became a JS app — all
302→404. Only `anio=1986` survived, by luck, from a 2017 crawl.

**What is recoverable from Wayback instead** (all small, all Phase 2):
- `campeonatos.asp` — 79 distinct HTML captures. A full champion/coach/runner-up
  ledger **1930→2005+**, by city. Directly informs D3/D5/D6.
- `lideres.asp` (no params) — ~96 distinct captures 2007–2021, 11 stat-category
  leader tables each, showing whatever season was current at capture time.
  Reaches ~4 years below RealGM's 2011-12 floor.
- ~10 parametrized `lideres.asp?anio=` 200s (1986, 2007–2014, 2021).
- ~18 other `/estadisticas/*.asp` scripts archived (`enciclopedia`, `mvp`,
  `finales`, `posiciones`, per-category leaders) — unprobed, Phase 3+ candidates.

Everything pre-2007 now goes to the roadmap Phase 4 newspaper track.

Prior context: repo scaffolded from a chat session (`docs/research/summary.md`).
The Wayback query is what this repo existed to run; it is now run. Full detail in
`docs/coverage_wayback.md` and `docs/specs/wayback_ingest_spec.md`.

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

### PHASE_3_PARSE — queued, do not start
Parse `data/raw/{campeonatos,lideres}/` → `data/interim/` → validated
`data/clean/` with full provenance (PC3). Two output streams:
- `champions_from_bsnpr.csv` from tranche A (AÑO/EQUIPO/DIRIGENTE/SUB.CAMPEON,
  city→franchise, handle the 1953 `*`, annotation bleed, multi-coach cells).
- `player_season_leaders.csv` from tranches B/C (11 stat categories, parse
  `Jugador` = "Apellido, Nombre (Club)" into raw fields — resolve identity
  later per D1, never at ingest; dedup captures per season keeping latest
  post-season-end; `stats_tracked` from which category tables have rows).
See `docs/specs/wayback_ingest_spec.md` [INTERFACES] + [OPEN_QUESTIONS].

### PHASE_4_RECONCILE — queued, do not start
Cross-check parsed leaders against the existing seed CSVs. Resolve D5 (1945), D6 (1953, 2024). Rebuild the game pool.

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

- B1 — **Manual, user-only.** The bsnpr.com DevTools recon (roadmap Phase 0, steps 1–7) requires a human in Chrome. One hour of work, unblocks four features. Not scriptable — do not attempt to automate it. Ask for the cURL output when ready.
- B2 — **RESOLVED by Phase 1.** Wayback coverage of the 1957–2004 per-season
  target is effectively zero (see coverage doc). Outcome is the "patchy" branch:
  pre-2007 season leaders need the roadmap Phase 4 newspaper track. Wayback
  still yields the `campeonatos.asp` ledger and 2007–2021 leader boards.
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

---

[VERIFICATION_LOG]

| Phase | V1 | V2 | V3 | V4 | V5 | Notes |
|---|---|---|---|---|---|---|
| PHASE_1 | PASS | PASS | PASS | PASS | PASS | V1: T1.1–T1.7 all delivered (T1.5 deviation documented, D-003). V2: PC5 raw immutable + cached; PC6 sequential/≥1.5s/backoff; PC1 no fabrication — negative finding reported straight. V3: no secrets; `.env` gitignored; UA carries no PII. V4: `make enumerate` + `make samples` run clean; 19 pytest pass; `read_html` verified on all 3 probes. V5: snake_case modules, English code/comments. |
| PHASE_2 | PASS | PASS | PASS | PASS | PASS | V1: T2.1–T2.5 done; 193/193 digests fetched, 0 failed; manifests written. V2: PC5 raw bytes unmodified + never re-fetched (idempotent re-run confirmed); PC6 one request per digest, ≥1.5s spacing, backoff; PC3 provenance captured per file in `.meta.json`. V3: no secrets; raw HTML gitignored. V4: 23 pytest pass; sampled files parse with `read_html`. V5: snake_case, English. |

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
| `docs/specs/wayback_ingest_spec.md` | **new, S001** | Ingest strategy, observed source shapes, 8 open questions. |
| `.venv/` | **new, S001** | Python 3.14, deps from requirements.txt. gitignored. |
| `src/fetch_wayback.py` | **new, S001** | PHASE_2 tranche A–C bulk fetcher. `make fetch`. Idempotent. |
| `data/raw/campeonatos/*.html` (+meta) | **new, S001** | 79 champion-ledger snapshots, 2007–2021. gitignored. |
| `data/raw/lideres/*.html` (+meta) | **new, S001** | 114 season-leader snapshots, 2007–2021. gitignored. |
| `data/interim/fetch_manifest_{campeonatos,lideres}.csv` | **new, S001** | Every capture → its local raw file. Tracked. Phase 3 input. |

---

[NEXT_ACTIONS]

1. **PHASE_3_PARSE** — parse the 193 fetched snapshots to provenance-complete
   `data/clean/` CSVs. Scope written in TASK_QUEUE. Needs a go-ahead (P6).
2. Roadmap Phase 4 newspaper track — still the only path to pre-2007 season
   stats. Federación / BSN league office email (roadmap Phase 6). Human-side.
3. Human-side: B1 DevTools recon (unchanged).
4. Later phase: probe the other archived `/estadisticas/*.asp` scripts from the
   coverage report's other-scripts table (spec open Qs 1–4) — deferred this
   session per owner's "A-C only". Priority order:
   - **`enciclopedia.asp`** (~79 distinct captures, 2007–2021, zero
     parametrized) — an "encyclopedia" page; likely player career records /
     bios. High potential value for D1 identity work and career leaders.
   - **`lideres_e.asp`** (~53 distinct captures, runs to 2021-09) — `_e` most
     likely "extranjeros" → **refuerzos** (import players) leader tables. Would
     feed the app's Refuerzos tab directly.
   - **`livestats.asp`** (13 captures, 6 distinct, 2013–2017) — may expose the
     Genius Sports / FIBA LiveStats endpoint or `matchId` scheme, which is
     exactly what B1's DevTools recon is trying to find for box scores.
   - **Identify the 2001-08-03 capture** (`20010803075616` =
     `http://bsnpr.com/estadisticas.asp?t=3`, HTTP 200) — the oldest snapshot in
     the inventory, ~6 years before anything else. It heads a small **2001–2002
     cluster** on an older URL scheme (`estadisticas.asp`, `estadisticas2001.asp`,
     `?t=3`) predating the `/estadisticas/lideres.asp` engine. If those pages
     carry 2000–2001 season data in any usable form they would be the only
     pre-2007 primary source in the whole archive — check before writing off.
5. `git add` new source + docs + `data/interim/` (NOT `data/raw/`, NOT `.venv/`)
   and commit — awaiting P4 approval; nothing committed in session 001.
