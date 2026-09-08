# PROJECT INSTRUCTIONS — TIER 2 — BSN ARCHIVO
<!-- Read after global.md, before session.md. -->

[PROJECT_IDENTITY]

- NAME: BSN Archivo
- DOMAIN: Historical statistical archive for Puerto Rico's Baloncesto Superior Nacional (BSN), 1930–present.
- OWNER: Alejandro "Benniz" — business analyst, San Juan PR. Sports content brand `bennizpr`.
- CURRENT_STATE: Interface is feature-complete (`app/bsn_archivo.html`, single file, 13 tabs, 3 games). The database behind it is thin — the game pool is 45 players because that is every player currently verifiable.
- THIS_REPO_EXISTS_TO: fill the data. Not to build UI.
- LANGUAGE: Code and comments in English. User-facing strings in Spanish (Puerto Rican usage).

[PROJECT_CONSTRAINTS]

- PC1: **Never fabricate.** No invented URLs, no invented stats, no invented image paths, no guessed team colours presented as fact, no plausible-but-unverified figures. If data is missing, the record says so. This has been applied consistently even where it made a feature less impressive. It does not get relaxed.
- PC2: **`NULL` ≠ `0`.** An unrecorded stat stored as zero silently corrupts every leaderboard forever. Nullable columns everywhere; never coalesce to zero at ingest. `seasons.stats_tracked` records which columns are meaningful in a given era.
- PC3: **Provenance on every row.** `source_id`, `source_url`, `retrieved_at`, `confidence` ∈ {`verified`, `single-source`, `disputed`}. A row without provenance does not get written.
- PC4: **Show the gaps, don't hide them.** An archive that conceals its holes is worse than one that displays them. Coverage gaps are a first-class output, not an embarrassment.
- PC5: **Raw is immutable.** Anything fetched from the network lands in `data/raw/` byte-for-byte and is never edited. All transformation happens raw → interim → clean. Re-running a parse must never require re-fetching.
- PC6: **Be a polite network citizen.** Wayback Machine and any league endpoint: sequential requests, ≥1s delay, retry with exponential backoff on 429/5xx, descriptive User-Agent, cache every response to disk on first fetch. Never parallelise the archive crawl.
- PC7: Single-file app stays single-file. `app/bsn_archivo.html` has no build step and no dependencies. Do not introduce a bundler, framework, or npm install to serve it.

[DOMAIN_RULES]

- D1: **Player identity resolution is the #1 data-integrity risk.** Spanish naming conventions (maternal surnames, accents, inconsistent ordering) plus universal nicknames (Piculín, Pachín, Quijote) will generate duplicate players. Required: `canonical_name`, an alias table, and an accent-stripped `normalized_name`. Match on birth year + first season + primary club — **never on name alone**. Fuzzy matches below threshold go to a manual review queue, not into the database.
- D2: **Franchise ≠ team-name-in-a-season.** Model franchise lineage as events. Known cases: Brujos de Guayama → Osos de Manatí (2022); Grises de Humacao → Criollos de Caguas (2023); Tiburones + Capitalinos → Cangrejeros (1998); Indios de Mayagüez ↔ Taínos de Cabo Rojo (1989–93); Piratas hiatus 2005–08.
- D3: **The 1942–43 split season.** Spanish sources list `1942` and `1942-1943` separately (San Germán won both); the current CSV folds them into `1942`. This is why San Germán shows 13 titles instead of 14. The season key must be able to represent a split-year season. Do not "fix" the title count by editing the number — fix the key.
- D4: **The scoring-title metric changes.** Through 1969–70 the title went to the **total points** leader; from 1970–71 onward to the **points-per-game** leader. The `metric` column preserves this. Comparing 602 total points to 22.4 ppg is meaningless — never rank across the boundary without segmenting.
- D5: **Known unresolved conflict — 1945 champion.** English Wikipedia's franchise table credits Capitalinos de San Juan; Spanish Wikipedia's champions list credits Santos de San Juan. Both agree on Gallitos de la UPR as runner-up. These may be the same club renamed, or a genuine error. Carried as the English version, flagged `disputed`. Do not quietly pick one.
- D6: **Known gaps in the seed CSVs:** `1953` has no champion listed (either no season was held or the source is incomplete — verify). `2024` runner-up is blank; it was Osos de Manatí but was left empty rather than filled from memory. Confirm from a source, then patch with provenance.
- D7: **Career-leader tables are ~5 years stale** per Wikipedia's own flag. Dalmau and Pagán played past the apparent cutoff. Treat every career total as a **floor**, not a current standing.
- D8: Pre-three-point-line context matters. Neftalí Rivera's 79-point game (1974) was 34 field goals, all two-pointers. Era context belongs in `notes`, not silently in the number.

[VERIFIED_FACTS — DO NOT RE-INVESTIGATE]

- F1: RealGM's BSN season dropdown has a hard floor at **2011-12**; awards at **2014-15**. Verified directly. Proballers is similar. This is the ceiling for any scraper-based approach.
- F2: The old bsnpr.com stats engine published season leaders at
  `https://www.bsnpr.com/estadisticas/lideres.asp?anio=YYYY&liga=1&serie=1&grupo=BS26&B1=Ver`
  with Wikipedia citations running **anio=1957 → anio=2004**, retrieved July 2021. There was also `estadisticas/campeonatos.asp`. These URLs now return **404** — the site was rebuilt as a JS app. They should still be in the Wayback Machine. **This is the whole ballgame.**
- F3: `es.wikipedia.org` was unfetchable from the prior sandbox; English Wikipedia fetched fine. Retest from this environment before assuming.
- F4: Wayback CDX + `lideres.asp` pages are server-rendered HTML tables — `pandas.read_html` handles them. Fetch with the `id_` suffix (`https://web.archive.org/web/{timestamp}id_/{url}`) to get raw HTML without archive chrome.

[LEGAL_CONSTRAINTS]

- L1: Statistics are facts and not copyrightable. **Compilations can be protected.** Scraping RealGM's compilation for a commercial product is real exposure — verify with them; do not ship from them.
- L2: Wikipedia content is CC BY-SA — usable with attribution. Attribution must be machine-tracked via `sources`, not a footnote written once.
- L3: **Team logos and player photographs are a hard no without permission.** The app's drawn-SVG fallback exists for this reason. Do not add image files scraped from anywhere.
- L4: Personal/archival use today; App Store product is the stated ambition. Assume everything will eventually be published and behave accordingly.

[STACK]

- Python 3.11+, `requests`, `pandas`, `lxml`, `beautifulsoup4`, `pytest`. `playwright` only where a page is JS-rendered.
- Postgres via Supabase **deferred** until the data justifies it (Phase 1 in the roadmap). Until then: CSV/Parquet in `data/clean/`, one file per entity.
- No ORM until there is a database. No scheduler. No Docker.

[REPO_LAYOUT]

```
CLAUDE.md              loader
docs/global.md         tier 1
docs/project.md        tier 2 (this file)
docs/session.md        tier 3
docs/specs/            architecture decisions, one concern per file
docs/research/         README.md, bsn_project_roadmap.md, prior session summary, audit
data/raw/              immutable network captures (gitignored if large)
data/interim/          parsed but unvalidated
data/clean/            validated, provenance-complete — the deliverable
src/                   snake_case modules
tests/                 pytest
app/bsn_archivo.html   the single-file app
```

[PROJECT_OVERRIDES]

- O1: None yet. Log any deviation from global.md here with justification.
