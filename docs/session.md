# SESSION STATE — TIER 3
<!-- Authoritative for current state and task priority. Update at every phase exit. -->

**SESSION:** 001 — repo bootstrap + Wayback enumeration
**DATE:** (set on first run)
**MODEL:** (set on first run)

---

[SESSION_STATE]

Cold start. This repo was scaffolded from a prior chat-based session whose full handoff lives in `docs/research/summary.md`.

What exists: a feature-complete single-file app (`app/bsn_archivo.html`), five seed CSVs in `data/clean/`, a roadmap, and an audit.

What does not exist: any ingestion code, any test suite, any environment setup.

The prior session could not run the highest-value task — a Wayback Machine CDX query — because `web.archive.org` was not on that sandbox's network allowlist. **That is the reason this repo exists.** Claude Code runs with local network access, so it can be done here.

---

[TASK_QUEUE]

### PHASE_1_ENUMERATE — active

Scope is enumeration only. Do not bulk-fetch snapshots in this phase.

- T1.1 — Set up the project environment: `.gitignore`, `requirements.txt`, `Makefile`, `.env.example`, venv bootstrap. `git init` if not already a repo. **Do not commit** (P4).
- T1.2 — Write `src/wayback_cdx.py`. Queries the CDX API for everything archived under the old stats path:
  ```
  http://web.archive.org/cdx/search/cdx?url=bsnpr.com/estadisticas*&output=json&limit=50000&collapse=urlkey
  ```
  Writes the raw JSON response to `data/raw/cdx/` unmodified (PC5). Handles 429/5xx with backoff (PC6).
- T1.3 — Parse the CDX result into `data/interim/cdx_inventory.csv`: `original_url`, `timestamp`, `statuscode`, `mimetype`, `digest`, plus extracted `endpoint` (`lideres.asp` / `campeonatos.asp` / other) and extracted `anio` where present.
- T1.4 — Produce `docs/coverage_wayback.md`: a coverage matrix of which `anio` values from **1957–2004** have at least one snapshot with HTTP 200, which have only redirects/errors, and which are entirely absent. Include per-decade totals.
- T1.5 — Fetch **exactly three** sample snapshots (one from the 1960s, one from the 1980s, one from the 2000s) to `data/raw/samples/`. Confirm `pandas.read_html` parses the tables and report what columns actually exist per era. Three only — this is a probe, not the ingest.
- T1.6 — Write `docs/specs/wayback_ingest_spec.md` per H2, recording the actual observed table shape, the column drift across eras, and the proposed parse strategy.
- T1.7 — Update this file: `[VERIFICATION_LOG]`, `[FILE_MANIFEST]`, `[NEXT_ACTIONS]`.

**Phase exit:** report status per `[STATUS_UPDATE_FORMAT]`, then pause (P6).

### PHASE_2_FETCH — queued, do not start
Bulk-fetch every 200-status `lideres.asp` snapshot identified in Phase 1 into `data/raw/lideres/`. Requires approval; scope depends entirely on what Phase 1 finds.

### PHASE_3_PARSE — queued, do not start
Parse raw → `data/interim/` → validated `data/clean/player_season_leaders.csv` with full provenance (PC3).

### PHASE_4_RECONCILE — queued, do not start
Cross-check parsed leaders against the existing seed CSVs. Resolve D5 (1945), D6 (1953, 2024). Rebuild the game pool.

---

[BLOCKERS]

- B1 — **Manual, user-only.** The bsnpr.com DevTools recon (roadmap Phase 0, steps 1–7) requires a human in Chrome. One hour of work, unblocks four features. Not scriptable — do not attempt to automate it. Ask for the cURL output when ready.
- B2 — Unknown until T1.4 completes: whether Wayback coverage is good enough to make Phase 2 worthwhile. If coverage is patchy, that is still a successful outcome — it defines exactly which seasons need newspaper work.

---

[WORKING_MEMORY]

- Decisions made this session: (none yet)

---

[VERIFICATION_LOG]

| Phase | V1 | V2 | V3 | V4 | V5 | Notes |
|---|---|---|---|---|---|---|
| PHASE_1 | — | — | — | — | — | not yet run |

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

---

[NEXT_ACTIONS]

1. Run PHASE_1_ENUMERATE.
2. In parallel, human-side and outside this repo: the roadmap's Phase 6 league email (Federación / BSN league office). One hour, highest value-per-hour remaining, unblocks the logo/photo legal problem.
3. Human-side: B1 DevTools recon.
