# Spec: PHASE_3G Historic Follow-up

## [PURPOSE]

An owner `/btw` (2026-09-08) flagged three root-level pre-2007 bsnpr.com
targets that earlier probes noted but "never ingested", on the theory they
might hold **all-time non-scoring leaders back to 1948** — the pre-2000 depth
the app still lacks:

1. `lidereshistoricos.asp?t=*` — only `?t=3` had been seen; other `t` values unknown.
2. `lideres2002.asp` — the 2002 sibling of the already-ingested `lideres2001.asp`.
3. `mvp.asp` at the site **root** (not `/estadisticas/mvp.asp`).

Instruction: fresh CDX enumeration per target (the PHASE_1/3C inventories are
prefix/subset-filtered and could have missed a `t` value), probe one capture
per distinct param value, **confirm each value's meaning from the page itself —
do not assume**, then fetch + parse anything new with full provenance.

## [DECISION]

**No new `data/clean/` rows. All three targets resolve to data already ingested
by PHASE_3C.** PHASE_3G delivers the enumeration, a corroboration cross-check,
and this negative finding.

### What each target turned out to be

| Target | Archived param values | Content | Status |
|---|---|---|---|
| `lidereshistoricos.asp` | **`?t=3` only** (7 caps, 5 digests, 2002-06→2004-09) + 1 bare capture (2002-11, same view) | The "Líderes Históricos" page: **4 tables** — scoring champions `AÑO\|JUGADOR\|EQUIPO\|JJ\|P/A\|PPJ` **1948→2004**, then **DPOY** (`Defensa del Año`, 1964→2004), **ROY** (`Novato del Año`, 1958→2004), **MVP** (`Jugador Más Valioso`, 1958→2004) — all `AÑO\|JUGADOR\|EQUIPO`. **No statistical-category (rebounds/assists/blocks/steals) all-time tables exist.** | Already in `historic_scoring_champions.csv` (58 rows) + `historic_awards.csv` (135 rows), parsed from the same `?t=3` 2004-09 capture in PHASE_3C. |
| `lideres2002.asp` | bare (1 digest) + `?grupo=BS22&serie=1` (3 digests), 2002-05→2003-10 | Serie-Regular player leader `<pre>` blocks, 8 categories (anotaciones, rebotes, asistencias, TL anotados, TL %, canastos-3, canastos-3 %, bloqueos) × top-10. Same schema as `lideres2001.asp`. | Already in `player_season_leaders_2000_2002.csv` — 80 rows for season 2002, parsed in the PHASE_3C `lideres200x` sweep (which already covered `lideres2002`). |
| `mvp.asp` (root) | **bare only** (10 caps, 7 digests, 2004-04→2006-11) | **Byte-equivalent to `lidereshistoricos.asp?t=3`** — identical 4 tables (scoring 1948→2004 + DPOY/ROY/MVP). A second URL alias for the same server-side view. Latest capture (2006) still stops at 2004 (page never updated for 2005/06). | Same content as `lidereshistoricos.asp?t=3`; nothing new. |

### `mvp.asp` corroboration cross-check

The `mvp.asp` 2006-07 capture was parsed and diffed against the clean tables
(reproduce: the snippet in [INTERFACES]). **0 differences** across all 57
scoring seasons and 135 award rows (name + team). It is the same underlying
bsnpr.com database via a different script, so it does **not** earn a
`confidence` promotion to `verified` (not an independent source), but it
confirms the PHASE_3C parse is faithful and rules out any 2005–2006 extension.

### Disposition

- `data/raw/pre2007/mvp/` (7 captures) kept as a **second provenance path** for
  the historical rows, per D-018 (root `campeonatos.asp`/`lideres.asp` were kept
  the same way). Gitignored; manifest tracked.
- `historic_scoring_champions.csv` / `historic_awards.csv` / the 2002 leader
  rows are **not re-parsed or duplicated**.
- The "all-time non-scoring leaders back to 1948" the follow-up hoped for **do
  not exist in the Wayback archive.** Only `t=3` (award histories) was ever
  crawled. This routes to the newspaper / Federación track if ever needed.

## [RATIONALE]

- **PC1 — no fabrication.** The honest outcome is a negative finding; recorded
  as one rather than manufacturing thin "new" rows from a duplicate source.
- **Fresh CDX per target confirmed the gap is real,** not an artifact of the
  earlier narrow enumeration: `bsnpr.com/lidereshistoricos.asp*` returns only
  `t=3` + bare; there is no `t=1`, `t=2`, `t=4`, …
- **The earlier probe guess was wrong and is now corrected.** `archive_probe_spec.md`
  read the three 3-column tables on `?t=3` as "rebounds / assists / another".
  They are DPOY / ROY / MVP award winners by year — confirmed from the page's
  own section headers (`DEFENSA DEL AÑO`, `NOVATO DEL AÑO`, `JUGADOR MÁS
  VALIOSO`). See [OPEN_QUESTIONS] #2 in that spec — now closed.
- **D-018 precedent** governs the duplicate `mvp.asp` source: keep raw for
  dispute-resolution, don't create parallel clean rows.

## [ALTERNATIVES_REJECTED]

- **Re-parse `mvp.asp` into a new `historic_season_leaders.csv`.** Rejected —
  identical content to `lidereshistoricos.asp?t=3`, already parsed. Would create
  two clean copies of the same rows that drift apart (the exact B4 problem).
- **Promote the historical scoring/award rows to `confidence=verified`.**
  Rejected — `mvp.asp` and `lidereshistoricos.asp` are the same bsnpr.com
  database, not independent corroboration. A `verified` bump needs an outside
  source (es.wikipedia, Federación) — that's PHASE_4 reconcile work
  (`reconcile_spec.md` Q, `NEXT_ACTIONS` #4).
- **Fetch every `mvp.asp` capture and every `lideres2002` digest again.** Done
  (idempotent); all were already on disk from PHASE_3C except the 7 `mvp.asp`
  digests, now fetched.

## [INTERFACES]

- `src/enumerate_historic_followup.py` (`make enumerate-historic`) — CDX query
  per target prefix → `data/interim/cdx_historic_followup.csv` (27 rows, every
  capture + status) + a printed distinct-query / capture / digest summary.
- `src/fetch_historic_followup.py` (`make fetch-historic`) — one GET per
  distinct 200-digest, `id_` raw suffix, `polite_get` (PC6), `MAX_TRANCHE=500`
  (all targets far under). Raw → `data/raw/pre2007/{lidereshistoricos,lideres2002,mvp}/`;
  every 200 capture → `data/interim/fetch_manifest_historic_followup.csv` (tracked).
- No parser module — no new clean output. `mvp.asp` corroboration cross-check
  (one-time, reproduce):
  ```
  .venv/bin/python -c "
  import pandas as pd, re, csv; from io import StringIO
  from src.parse_wayback import decode_html, squish
  t = pd.read_html(StringIO(decode_html(open(
      'data/raw/pre2007/mvp/20060716032157_AO4V4346.html','rb').read())))
  # tables[7]=scoring, [8]=DPOY, [9]=ROY, [10]=MVP  -> compare to
  # data/clean/historic_scoring_champions.csv + historic_awards.csv
  "
  ```

## [OPEN_QUESTIONS]

1. **Pre-2000 statistical-category leaders (rebounds/assists/blocks/steals) —
   still a gap.** Not in the archive. Only the newspaper / Federación track can
   fill it. Roadmap Phase 4/6.
2. **`lideres2002.asp` bare capture vs the `grupo=BS22&serie=1` captures.** The
   parser kept the `serie=1` (Serie Regular) rows; the bare capture carries the
   same 8 `<pre>` blocks. If a later pass wants Semi-Final / Serie-Final 2002
   leaders, note that `lideres2002.asp?grupo=BS22&serie={3,4}` was **never
   archived** (only `serie=1`), unlike 2001 which has `serie=4`.
3. **`historic_awards.csv` DPOY starts 1964, not 1958.** The `?t=3` DPOY table
   itself starts 1964 — that is the award's real first year (`Defensa del Año`
   was introduced later than MVP/ROY), not a parse gap. Left as-is.
