# Archive probe — spec

<!-- H2 structure. PHASE_3B_PROBE_ARCHIVE, 2026-09-08. Sample probe only —
no bulk fetch, no parser, no clean output. -->

Cross-refs: [`wayback_ingest_spec.md`](wayback_ingest_spec.md) (open Qs 1–4),
[`../coverage_wayback.md`](../coverage_wayback.md) (other-scripts table),
`data/raw/probe/` (the 22 sample captures), `src/probe_archive.py` (the fetcher).

---

## [PURPOSE]

PHASE_2 processed `campeonatos.asp` + `lideres.asp` and deferred the other ~18
archived `/estadisticas/*.asp` scripts. This probe samples four of them —
`enciclopedia.asp`, `lideres_e.asp`, `livestats.asp`, and the 2001–2002
`estadisticas.asp` cluster — to decide which, if any, warrant a full ingest
phase. Method: 3–5 distinct-digest captures each, spread over the archived date
range, fetched with `id_` raw suffix via `polite_get` (PC6), inspected for
table shape, player- vs team-level, season coverage, and endpoint hints.

---

## [DECISION]

| Script | What it is | Player-level? | Pre-2007 content? | Verdict |
|---|---|---|---|---|
| `enciclopedia.asp` | All-time player directory | **Yes** | Yes (all eras) | **Full ingest phase** |
| `estadisticas.asp` 2001–02 cluster + its root-level links | Standings + **season & historical leaders** | **Yes** (the `lideres*` links) | **Yes — 1948→2002** | **Full ingest phase** |
| `lideres_e.asp` | Team-leader boards ("Líderes por Equipo") | No — team-level | No (2007–2021, same dead `anio=` params as `lideres.asp`) | Low value — optional, later |
| `livestats.asp` | Third-party live-stats widget shell | — | — | **Dead** — content never archived |

**The 2001–2002 cluster partially reverses session-001's headline.** That
finding — "the 1957–2004 per-season leader pages were never archived with
content" — is correct *for `/estadisticas/lideres.asp?anio=YYYY`*. But the
2000–2002 site served the same data from a **different, root-level URL scheme**
(`bsnpr.com/lideres2001.asp`, `/lideres2000.asp`, `/lidereshistoricos.asp`,
`/posiciones2000.asp`, `/equiposstat.asp`) that the PHASE_1 CDX query never saw
(its pattern was `bsnpr.com/estadisticas*`). Those pages **were crawled
2001–2004 while the site was still static HTML, and they returned 200 with
content.** This is real, recoverable, pre-2007 primary-source leader data —
though not box scores.

---

## [FINDINGS — per script]

### `enciclopedia.asp` — player directory  →  FULL INGEST

- 5 captures probed: 2007-04, 2009-01, 2012-06, 2014-02, 2021-09. All param-less,
  all 200, ~760 KB–1 MB each.
- One content table: **`Apellidos | Nombre | Camisa | Nació`** —
  surname(s), first name, jersey number (often blank), birth date (`M/D/YYYY`,
  mostly present). Row count grows **2368 (2007) → 2742 (2012) → 3284 (2021)** —
  it is cumulative and all-time (birth years span the 1900s–1990s).
- **Every row links to `/jugadores/jugador.asp?id=NNNN&e=`** — a stable integer
  player id and a detail page. 2742 distinct ids in the 2012 capture.
- **Why it matters (D1):** this is a canonical BSN player list with exactly the
  disambiguation keys D1 demands — `canonical_name`, split surnames (maternal
  surname visible), and **birth year**. It is the backbone for the alias table
  and the `normalized_name` / birth-year + club match. Nothing else in the
  archive gives this.
- **Bonus discovery:** `bsnpr.com/jugadores/*` has **~1680 archived 200s,
  2004→2026** (the `jugador.asp?id=` detail pages). Never enumerated (outside
  the `/estadisticas` pattern). Likely per-player career tables / bio / teams.

### `estadisticas.asp` 2001–2002 cluster  →  FULL INGEST

- 5 captures probed: 2001-08 (`?t=3`), 2001-11, 2002-06 (`estadisticas.asp`),
  2002-06 (`estadisticas2001.asp`), 2002-10. Title `BALONCESTO SUPERIOR
  NACIONAL`, static HTML, latin-1.
- The bare page renders **standings (Posiciones)** for the current year, split
  by phase: `# | Equipo | Ganados | Perdidos | PCT | JD | Local | Visitante`
  for Serie Regular, Round Robin, Semi Final A/B, Serie Final. Full W-L records,
  14 teams, 2000 / 2001 / 2002. `estadisticas2001.asp` and `?t=3` are the same
  standings view.
- Nav links (root-level scripts, **not** under `/estadisticas/`):
  - `lideres2001.asp?grupo=BS21&serie=4` — **13 CDX captures, 11×200,
    2001-07→2004-01**. Probed (2001-09): player leader tables —
    `Anotaciones: Jugador JJ TP Prom`, `Rebotes: Jugador JJ Def Off Tot Prom`,
    `Asistencias: Jugador JJ TA Prom`, `Tiros Libres…`, phase-split. **2001
    season, player-level.**
  - `lideres2000.asp?t=3` — 9 captures, 7×200. (Probe fetch hit a Wayback 503
    burst; CDX confirms content exists — fetch in the ingest phase.)
  - `lidereshistoricos.asp?t=3` — 6 captures, 6×200, 2002-06→2004-09. Probed
    (2002-11), 282 KB. Contains a **year-by-year single-season-leaders record**:
    - scoring: `AÑO | JUGADOR | EQUIPO | JJ | P/A | PPJ`, **1948→2001** (54 rows;
      carries *both* total P/A and PPJ — straddles the D4 metric boundary with
      both metrics present; `*` prefix = annotation, as in campeonatos).
    - three more `AÑO | JUGADOR | EQUIPO` tables (rebounds / assists / another),
      **1958→2001** and **1964→2001**, player + team, no numbers.
  - `posiciones2000.asp?t=3` — 4 captures, 3×200.
  - `equiposstat.asp?t=XX&serie=N` — **367 CDX captures, 307×200,
    2001-07→2007-05**. Per-team stat pages (XX = 2-letter team code, serie =
    phase). Large, unprobed — a per-team stat corpus bridging 2001→2007.
- **Why it matters:** the only pre-2007 primary-source season data in the whole
  archive. `lidereshistoricos.asp` alone more than doubles the reach of the seed
  `bsn_scoring_champions.csv` (26 rows 1966–1991 → 54 rows 1948–2001).

### `lideres_e.asp` — team leaders  →  LOW VALUE

- 5 captures probed: 2007-05 bare, 2007-05 `grupo=BS26&serie=1`, 2012-05
  `grupo=BS19&serie=1&anio=2012`, 2014-03 `anio=2014`, 2020-06 `anio=2019`.
- `_e` is **not** "extranjeros/refuerzos" (the PHASE_1 guess). Title is
  **"Líderes por Equipo"** and every table is `# | Equipo | JJ | <stat> | Prom`
  — **team-level** aggregates, same 11 categories as `lideres.asp` plus
  `Puntos` / `Puntos Permitidos` (team offense/defense) and, from 2013,
  `FBP/PFT/PIP/SCP`.
- Shows the season current at capture, exactly like `lideres.asp`. Same window
  (2007–2021), same limitation — the year `<select>` lists 1956→2020 but the
  historic `anio=` params are the same dead 302/404s.
- Verdict: real data but redundant with `lideres.asp` at a coarser grain. Worth
  a small tranche only if PHASE_4 wants team-season rate stats. Not urgent.

### `livestats.asp` — dead

- 4 captures probed: 2013-04, 2013-08 (`?live=1&onlylive=1`), 2014-04, 2017-07.
- The 2013–2014 captures are **850–990-byte stubs** — `<title>BSNPR -
  LiveStats</title>` and nothing else. A shell page for a third-party live
  widget (Genius Sports / FIBA LiveStats style) whose content loaded via JS from
  an external host Wayback never captured. No `matchId` / `gameId` / iframe src
  in the archived HTML.
- The 2017 capture is a **404 error page**.
- Verdict: **dead**. Does not help B1 (the box-score endpoint hunt) — no
  endpoint or match-id scheme is exposed in what archived.

---

## [ALTERNATIVES_REJECTED]

- **Parse any of these in PHASE_3B** — out of scope by the phase definition.
  This is a go/no-go probe; ingest is a separate phase.
- **Bulk-fetch `equiposstat.asp` (307 captures) now** — no. Sample first; it is
  a PHASE_3C candidate.
- **Treat `lideres_e.asp` as refuerzos data** — disproven: it is team-level.
  The app's Refuerzos tab still needs another source.
- **Trust the PHASE_1 "pre-2007 unrecoverable" verdict as covering all URL
  schemes** — it does not. It was scoped to `/estadisticas/lideres.asp?anio=`.
  The root-level `lideres2000/2001/historicos.asp` scheme is a separate finding.

---

## [INTERFACES]

### `src/probe_archive.py`
- `TARGETS` — 19 (label, timestamp, url) tuples + 3 added ad hoc for the
  root-level `lideres*` pages. `make`-less; run `python -m src.probe_archive`.
- Fetches to `data/raw/probe/<label>_<ts>.html` (+ `.meta.json`), gitignored.
  Idempotent (skips cached). Reuses `polite_get` / `raw_wayback_url` /
  `decode_html`.
- `inspect(path)` — prints title, year `<select>` ranges, external-provider
  script/iframe hints, `matchId`-style id hints, `read_html` table shapes with a
  player-level heuristic, and body-text year span.

### CDX (run ad hoc during the probe, not persisted)
`bsnpr.com/lideres2001.asp*` 13 (11×200) · `lideres2000.asp*` 9 (7×200) ·
`lidereshistoricos.asp*` 6 (6×200) · `posiciones2000.asp*` 4 (3×200) ·
`equiposstat.asp*` 367 (307×200) · `jugadores/*` 2000 (1680×200).
PHASE_3C should persist these properly via `src/wayback_cdx.py` with a widened
URL pattern (`bsnpr.com/*` or an explicit list), not just `bsnpr.com/estadisticas*`.

---

## [OPEN_QUESTIONS]

1. **`lideres2001.asp` / `lideres2000.asp` table structure** — the probe
   confirmed the category headers from body text but `read_html` did not surface
   clean tables (layout `<table>` nesting). Needs a BeautifulSoup pass in the
   ingest phase. Are the numbers player season totals or phase-specific?
2. **`lidereshistoricos.asp` — how far back, really?** The scoring table starts
   1948. Do the later captures (2004) extend past 2001? What are the 3 unlabeled
   `AÑO|JUGADOR|EQUIPO` categories (rebounds / assists / FT% / 3pt)?
3. **`equiposstat.asp` (307×200, 2001–2007)** — unprobed. Per-team stat pages.
   Player rosters with per-game stats? This could be the bridge that fills the
   2002–2006 player gap. High priority to sample.
4. **`bsnpr.com/jugadores/jugador.asp?id=N`** (~1680×200, 2004–2026) — unprobed.
   If these carry per-player career-by-season tables, combined with
   `enciclopedia.asp`'s id list they are a near-complete player-career dataset.
5. **`grupo` codes** — `lideres2001.asp` uses `grupo=BS21`; `lideres_e.asp`
   showed `BS19/BS26/BS28`. Map the grupo scheme (BSN vs feeder leagues vs
   seasons) before ingesting either.
6. **`lideres_e.asp` `anio=` params** — do the parametrized 200s (2012, 2014,
   2017, 2019) actually serve that season, or the current one? (Same question
   PHASE_3 answered "yes, that season" for `lideres.asp` tranche C.)
