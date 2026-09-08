# Wayback ingest — spec

<!-- H2 structure. Written at PHASE_1 exit from observed data, not assumption. -->

Cross-refs: [`../coverage_wayback.md`](../coverage_wayback.md) (coverage matrix),
[`../../data/interim/cdx_inventory.csv`](../../data/interim/cdx_inventory.csv) (full capture list),
`data/raw/samples/` (the three probe snapshots).

---

## [PURPOSE]

Define how the archived bsnpr.com stats engine is turned into
provenance-complete rows in `data/clean/`. Scope of this document is the
extraction strategy and the observed source shape. It is written after Phase 1
enumeration + a 3-snapshot probe, so the numbers here are measured, not
projected.

---

## [DECISION]

**1. The 1957–2004 per-season mission is not recoverable from Wayback.**
The parametrized URLs Wikipedia cites
(`lideres.asp?anio=YYYY&liga=1&serie=1&grupo=BS26&B1=Ver`) were crawled exactly
once, on 2021-07-09, by an IABot reference-rescue run — *after* the site became a
JS app. Every in-window capture is a 302→404. Only `anio=1986` (crawled
2017-08-04, by chance) survives with content. **PHASE_2 does not attempt a
per-season `anio=` backfill for 1957–2004; there is nothing there to fetch.**

**2. PHASE_2 fetches what actually archived, in three tranches:**

| Tranche | Source | What it yields | Volume |
|---|---|---|---|
| A | `campeonatos.asp` (no params), all 80 distinct 200-captures | Champion + coach + runner-up, **1930→year-of-capture**, by city | 79 distinct HTML files |
| B | `lideres.asp` (no params), all ~96 distinct 200-captures, 2007–2021 | Season-leader tables (11 stat categories) for whatever season was *current* at capture time | ~96 distinct HTML files |
| C | `lideres.asp?anio=YYYY` parametrized 200s: 1986, 2007, 2008, 2010, 2013, 2014, 2021 (+ `lideres_e.asp` 27 param-200s, TBD) | Clean single-season leader tables | ~10 HTML files |

All three are small. The whole Phase 2 fetch is < 200 files — a single evening
inside PC6 limits (≥1 s spacing, sequential, cache-on-first-fetch).

**3. Parse by column signature, never by table index.** `pandas.read_html`
returns 4 tables for `campeonatos.asp` and 11–22 for `lideres.asp` depending on
capture era and layout cruft. The real tables are identified by their header
row, not their position.

**4. Raw fetch uses the `id_` suffix** (`/web/{ts}id_/{url}`) per project F4 —
confirmed working for all three probe snapshots.

**5. `seasons.stats_tracked` is populated from the data, not a lookup.** The
1986 snapshot returns *empty* tables for blocks (TB), steals (CB), turnovers
(TO) and offensive rebounds (RO); the 2007 snapshot populates all of them. The
presence/absence of rows per category per season *is* the era-tracking signal
(PC2, D-rules).

---

## [RATIONALE]

- **Why not chase the `anio=` pages harder.** Verified: 30 distinct in-window
  `anio=` URLs, one crawl date (2021-07-09), all 302. A second retry batch
  2025-12-19, all 404. The Wayback calendar has no other captures — `collapse`
  and un-collapsed CDX agree. The engine that served them died between the
  2017 and 2021 crawls. There is no fetch that recovers this.
- **Why `campeonatos.asp` is tranche A / highest value.** One table, 76 rows in
  the 2007 capture, `AÑO | EQUIPO | DIRIGENTE | SUB. CAMPEON`, running 1930→2005.
  It is the league's own championship ledger. It carries data the seed CSV does
  not (coach) and speaks directly to three open domain problems:
  - **D6 / 1953:** the row exists but the champion cell is a literal `*` with
    blank coach and blank runner-up. The league itself recorded no 1953
    champion. (No footnote text for the asterisk in the 2007 capture — check a
    later capture in Phase 4.)
  - **D5 / 1945:** champion `SAN JUAN`, coach `ADOLFO PORRATA`, runner-up `UPR`.
    A third source agreeing on the UPR runner-up; "SAN JUAN" is the city, so it
    disambiguates neither Capitalinos nor Santos — but it is another data point.
  - **D3 / 1942–43 split:** this source folds it into a single `1942` row
    (SAN GERMAN / ARMANDO TORRES / SANTURCE). Same fold as the seed CSV.
- **Why tranche B is worth it despite being mid-season snapshots.** RealGM's
  floor is 2011-12. Tranche B reaches 2007 and, for 2007–2011, is the *only*
  fetchable per-category leader data. Even mid-season leader boards are real,
  citable rows (confidence `single-source`, `notes` records "standings as of
  {capture date}, season in progress").
- **Why column-signature parsing.** Table index is unstable across eras: the
  1986 capture's category tables are `read_html` indices 0–10; the 2007 capture
  interleaves layout `<table>`s so the same content lands at indices
  6,7,9,10,12,13,15,16,18,19,21. A header-row match is stable.

---

## [ALTERNATIVES_REJECTED]

- **Per-season `anio=` crawl of 1957–2004** — rejected: the captures do not
  exist (measured, not assumed). This was the original premise of the whole
  phase; Phase 1 disproved it. That is a successful negative result (PC4, B2).
- **`collapse=urlkey` as the sole CDX query** — rejected as insufficient: it
  keeps one arbitrary capture per URL and would have hidden the `anio=1986`
  200 behind a later 404. Phase 1 runs both the collapsed query (the one the
  task queue specifies) and an un-collapsed query, and derives the inventory
  from the un-collapsed set. *(Decision logged in session.md WORKING_MEMORY.)*
- **Restrict enumeration to `lideres.asp` + `campeonatos.asp`** — rejected as
  too narrow: the archive holds ~20 distinct `/estadisticas/*.asp` scripts
  (`posiciones`, `enciclopedia`, `mvp`, `finales`, `anotaciones`, per-category
  leader pages, `lideres-vida`). The inventory records the real script name;
  the coverage doc tables them. They are Phase 3+ candidates, not this phase's
  work, but they are now visible.
- **`playwright` for fetching** — rejected: every archived page is
  server-rendered HTML; `requests` + `pandas.read_html` is sufficient
  (confirmed on all three probes). Project STACK reserves playwright for
  JS-rendered pages only; none here are.
- **OCR / newspaper track now** — deferred, not rejected: it is the roadmap
  Phase 4 fallback and is exactly what the pre-2007 gap now requires.

---

## [INTERFACES]

### `src/wayback_cdx.py`
- `main()` — run via `make enumerate` / `python -m src.wayback_cdx`. Idempotent:
  raw CDX JSON is cached in `data/raw/cdx/`, re-runs only re-derive the CSV and
  the markdown.
- `polite_get(url, *, params, session) -> Response` — the shared polite-fetch
  primitive (PC6: ≥1.5 s spacing, exp. backoff on 429/5xx, honours
  `Retry-After`). Phase 2's fetcher imports this.
- Outputs: `data/raw/cdx/cdx_estadisticas_{collapsed,all}.json` (immutable),
  `data/interim/cdx_inventory.csv`, `docs/coverage_wayback.md`.

### `data/interim/cdx_inventory.csv`
Columns: `original_url, timestamp, statuscode, mimetype, digest, endpoint,
anio, query, parametrized`. One row per Wayback capture (1562 rows). `endpoint`
is the `.asp` script name or `other`. `parametrized` ∈ {`yes`,`no`}.

### `src/fetch_wayback.py`
- `main()` — `make fetch`. One HTTP GET per unique content digest across
  tranches A–C; `id_` raw suffix; imports `polite_get` from `wayback_cdx`.
  Idempotent (skips any local file already present).
- Outputs: `data/raw/campeonatos/<ts>_<digest8>.html` (79),
  `data/raw/lideres/<ts>_<digest8>.html` (114), a `.meta.json` beside each, and
  `data/interim/fetch_manifest_{campeonatos,lideres}.csv` mapping every capture
  (not just fetched ones) to its local file.
- Run 2026-09-07: 193/193 digests, 0 failures.

### `src/fetch_samples.py`
- `raw_wayback_url(timestamp, original_url) -> str` — builds the `id_` raw URL.
- `SAMPLES` — the three probe entries (frozen; see its docstring for why these
  three and not the task queue's 1960s/1980s/2000s split).
- Outputs: `data/raw/samples/*.html` + `*.meta.json`.

### Observed source shapes (measured from the probes)

**`campeonatos.asp`** — 1 content table:

| col | meaning | notes |
|---|---|---|
| `AÑO` | season year | `*` = no champion (1953); annotations bleed in ("COPA OLIMPICA CANOVANAS" for 1984) |
| `EQUIPO` | champion, **by city** | uppercase, unaccented; maps to franchise via city + year |
| `DIRIGENTE` | head coach | may hold two names (mid-season change): "TOM NISSALKE  FUFI SANTORI" |
| `SUB. CAMPEON` | runner-up, by city | blank where unknown |

**`lideres.asp`** — up to 11 content tables, one per stat category. Every
category table is `# | Jugador | JJ | <stat cols> | Prom`:

| category header | stat columns | tracked in 1986? | tracked in 2007? |
|---|---|---|---|
| Anotaciones | `Tot` | yes | yes |
| Rebotes | `Def Off Tot` | yes (Def/Off zero-filled) | yes |
| Tiros Libres Anotados | `TLA` | yes | yes |
| Tiros Libres x Promedio | `TLI TLA` | yes | yes |
| Canastos de 3 | `CC3` | yes | yes |
| Canastos de 3 x Promedio | `3PI 3PA` | yes | yes |
| Bloqueos | `TB` | **empty** | yes |
| Cortes de Balón | `CB` | **empty** | yes |
| Turnovers | `TO` | **empty** | yes |
| Rebotes Ofensivos | `RO` | **empty** | yes |
| Asistencias | `TA` | yes | yes |

- `Jugador` cell = `"Apellido, Nombre (Club)"`. Club may be a city, a nickname,
  or empty (`"Melendez, Wilfredo ()"`). Nicknames appear mid-string and can be
  truncated (`"Morales, Mario 'Qui (Mets)"`). **This is the D1 identity-
  resolution surface — parse `player_raw`, `club_raw` verbatim into interim,
  resolve in a later phase, never at ingest.**
- Row index arrives as float (`'1.0'`) — `read_html` type inference; cast on
  parse.
- `Prom` for the free-throw / 3pt "x Promedio" tables is a **percentage**
  (88.6), not a per-game average. Header text disambiguates.
- A parameter-less capture shows the **season current at capture time**; a
  `?anio=YYYY` capture shows that season. The year `<select>` in the page lists
  `2007…1956` + `Vida` (career) — evidence the live engine could serve
  1956-onward until it died.

---

## [OPEN_QUESTIONS]

1. **`lideres_e.asp`** (88 captures, 27 parametrized 200s, runs to 2021-09) —
   not probed. `_e` likely = "equipo" (team leaders) or an alternate leader
   view. Probe in early Phase 2 before committing the tranche-C list.
2. **`enciclopedia.asp`** (79 distinct 200s, 2007–2021, zero parametrized) —
   an "encyclopedia" page. Could be player career records / bios — potentially
   high value for D1 and career-leader work. Unprobed.
3. **`finales.asp`** (18 distinct, 2008–2010) — playoff finals detail beyond
   the `campeonatos.asp` one-liner? Series scores, MVPs?
4. **`mvp.asp`** (6 distinct, 2007–2017) — award history. RealGM's award floor
   is 2014-15; this may go deeper.
5. **The 1953 asterisk** — the 2007 `campeonatos.asp` capture has no footnote
   text. Do any of the other 79 captures? (grep the tranche-A raw once fetched.)
6. **`lideres.asp` capture dates vs. season boundaries** — need per-capture
   classification: is snapshot X a completed season or mid-season? Compare
   capture date to known BSN season calendars (Mar–Jun regular season roughly).
7. **De-duplication across the ~96 tranche-B captures** — many will be the same
   season at different mid-points. Keep the latest capture per season, or keep
   all and let confidence/notes carry the as-of date? Leaning: keep the latest
   200 whose capture date is after the season's known end; fall back to latest
   available with a mid-season `notes` flag.
8. **Character encoding** — pages are latin-1 / windows-1252 (Spanish accents).
   Confirm and normalise to UTF-8 at the raw→interim boundary, not before.
