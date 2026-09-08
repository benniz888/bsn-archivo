# BSN Stats Platform — Roadmap

**Updated 1 September 2026.** Supersedes the original pre-build version.

Target: a queryable database + app covering BSN history, 1930–present. This document tracks phase status; `summary.md` holds the full session handoff and every decision with its rationale.

**Status at a glance:** the app is built and feature-complete. The database behind it is thin. Everything below is now about filling the data, not building the interface.

---

## PHASE STATUS

| Phase | Status | Notes |
|---|---|---|
| 0 — Recon | **Partial** | Aggregator floors confirmed. bsnpr.com DevTools recon NOT done. |
| 1 — Schema | **Deferred** | App uses in-file JS objects. Postgres schema not built. |
| 2 — Modern ingest | **Not started** | Blocked on Phase 0 DevTools. |
| 3 — Wikipedia backfill | **Mostly done** | Champions 1930–2026, leaders, records, scoring titles 1966–91. |
| 4 — Historical archive | **Lead found, not executed** | The Wayback query is the whole ballgame. |
| 5 — App | **Done (single-file)** | `bsn_archivo.html`, 13 tabs, 3 games. Native app not started. |
| 6 — League relationship | **Not started** | Highest value-per-hour task remaining. |

---

## PHASE 0 — RECON

**Done.** RealGM's BSN season dropdown stops at **2011-12**; awards at **2014-15**. Proballers similar. Verified directly — do not re-investigate.

**Not done — the outstanding hour of work:**

1. Open `https://www.bsnpr.com/estadisticas` in Chrome.
2. F12 → Network → filter `Fetch/XHR` → hard reload.
3. Find the JSON request populating the stats table. Look for `/api/`, `_next/data/`, or an `api.bsnpr.com` host.
4. Copy as cURL, confirm it works outside the browser, note required headers.
5. Repeat on `/jugadores`, `/calendario`, a game page, and `/equipos/BAY`.
6. **Critical:** find the season parameter and walk it backwards. `season=2025` → `2015` → `2005` → `1995`. Where it stops is your Tier 1 boundary.
7. Probe game pages for a Genius Sports / FIBA LiveStats endpoint (`fibalivestats`, `genius`, or a numeric `matchId`). That yields per-game box scores.

**This one task unblocks four features:** standings, box scores, news, and current-season stats.

---

## PHASE 4 — THE ARCHIVE LEAD (top priority)

Wikipedia's BSN Scoring Champion article cites every figure to the retired bsnpr.com stats engine:

```
https://www.bsnpr.com/estadisticas/lideres.asp?anio=YYYY&liga=1&serie=1&grupo=BS26&B1=Ver
```

Citations run **anio=1957 through anio=2004**, retrieved July 2021. There was also `estadisticas/campeonatos.asp`. The league published a season-leaders database going back to **1957** — fifty-four years deeper than RealGM.

Confirmed: those URLs now return 404. The site was rebuilt as a JS app and the ASP pages left the live web. **They should still be in the Wayback Machine.**

```bash
# 1. Enumerate what was archived
curl "http://web.archive.org/cdx/search/cdx?url=bsnpr.com/estadisticas*&output=json&limit=50000&collapse=urlkey"

# 2. Filter for lideres.asp, note which anio values exist

# 3. Fetch raw HTML without archive chrome
#    https://web.archive.org/web/{timestamp}id_/{original_url}

# 4. Parse — these are server-rendered tables, pandas read_html handles them
```

Good coverage collapses half the archival phase into a weekend. Patchy coverage still tells you exactly which seasons need newspaper work before you commit to a library.

**Must be run outside the Claude sandbox** — web.archive.org is not on the network allowlist. Use Claude Code or run it locally.

### If the Wayback pull comes up short

- Federación de Baloncesto de PR and the BSN league office — media guides, record books, anniversary publications.
- Salón de la Fama del Deporte Puertorriqueño — inductee career records.
- Biblioteca Digital Puertorriqueña (UPR) — digitised *El Mundo*.
- El Nuevo Día / Primera Hora archives; Colección Puertorriqueña microfilm at UPR Río Piedras.
- OCR with `tesseract` + Spanish pack. Box scores OCR badly; budget heavy manual correction.
- Build a validating manual-entry form (totals must reconcile to the final score before saving).
- Crowdsource via bennizpr, with a photo of the source required per submission.

---

## PHASE 1 — SCHEMA (when moving off the single file)

Deferred, not cancelled. The design decisions still stand:

**Stack:** Postgres via Supabase (free, hosted, auto-generated REST API). Python for ingestion. One repo.

**Tables:** `seasons`, `franchises`, `teams`, `team_seasons`, `players`, `player_name_aliases`, `player_seasons`, `games`, `box_scores`, `awards`, `records`, `sources`, `franchise_events`.

**Three things that will kill this project if deferred:**

1. **`NULL` ≠ `0`.** Unrecorded stats stored as zero silently corrupt every leaderboard. Add `seasons.stats_tracked` so the UI knows which columns are meaningful per era.
2. **Player identity resolution.** Spanish naming (maternal surnames, accents) plus nicknames (Piculín, Pachín, Quijote) will produce duplicates. Needs `canonical_name` + alias table + accent-stripped `normalized_name`, matched on birth year + first season + primary club, never on name alone. Fuzzy matches below threshold go to a manual review queue.
3. **Franchise lineage.** Model the franchise separately from the name-in-a-season. Known cases: Brujos de Guayama → Osos de Manatí (2022); Grises de Humacao → Criollos de Caguas (2023); Tiburones + Capitalinos → Cangrejeros (1998); Indios de Mayagüez ↔ Taínos de Cabo Rojo (1989–93); Piratas' 2005–08 hiatus.

**Also:** the 1942–43 split season needs a season key that can represent it. Folding it into 1942 is why San Germán currently shows 13 titles instead of 14.

**Provenance on every row:** `source_id`, `ingested_at`, `confidence` (verified / single-source / disputed).

---

## PHASE 5 — THE APP

**Built.** `bsn_archivo.html` — single self-contained file, 131KB, no dependencies, no build step.

Thirteen tabs: Today · Championships · Games · Juega · Every season · Franchises · Hall of Fame · Refuerzos · Career leaders · Scoring titles · Records · Recent seasons · Sources & gaps.

Games: **La Cuadrícula** (date-seeded daily Immaculate Grid, streaks, emoji share cards, practice mode), **34-0** (decade draft sim, calibrated over 20,000 drafts), **¿Quién soy?** (clue-based quiz).

Cross-cutting: global search, favourite club, drop-in image layer, `localStorage` with memory fallback.

### Adding images

Drawn SVG renders underneath; a real file takes over automatically.

- `img/crest/<key>.png` — keys are the three-letter codes lowercased (`bay`, `sge`, `pon`, `que`).
- `img/player/<slug>.jpg` — name lowercased, accents stripped, spaces to hyphens.
- PNG/SVG/JPG/WebP for crests; JPG/PNG/WebP for portraits.
- Set `USE_IMAGES = false` near the top of the script to force drawn marks.

### If going native

React Native + Expo (one codebase, and Android matters in PR). Supabase backend. Apple Developer account $99/yr, 1–2 weeks first review.

**Legal, only if shipping publicly:** stats are facts and not copyrightable, but scraping RealGM's compilation for a commercial app is real exposure — verify with them, don't ship from them. Wikipedia is CC BY-SA, fine with attribution. **Team logos and player photos are a hard no without permission.** Which is why Phase 6 stops being optional.

---

## PHASE 6 — LEAGUE RELATIONSHIP

Not started. Highest value per hour of anything remaining.

1. Email the BSN league office and the Federación. You're a Puerto Rican analyst building a free historical archive. Ask about data access, historical media guides, record books, and **the names attached to Bayamón's 8 and Guaynabo's 3 retired numbers**.
2. Engagement converts you from scraper to partner — changing what data you can get *and* removing the logo/photo problem.
3. Document the build on bennizpr. "I'm building the BSN's stats database" is a content series, a credibility signal, and a reason for PR basketball to know your name.
4. This is the same door as player interviews. Analysts who build things for a league get access that fans asking for interviews do not.

---

## PITCH POSITIONING

**The seven-month gap.** The BSN runs late March to August. The official app is Genius Sports–powered and owns "today" — live scores, standings, news. You will not beat it there. But it has nothing to do in September. History and games are year-round.

> The official app covers the season. This covers the other seven months.

**Demo path:** championship ribbon → daily grid → share card → mi equipo. Four screens.

**The ask, stated precisely:** the game pool is 45 players because that is every player this archive can verify. One dataset — the archived league stats — takes it to hundreds, which unlocks true team × team grid axes, real numbers in the sim, standings, and box scores. That is a far better ask than "help me build an app."

---

## SEQUENCING

| Task | Effort | Blocking? |
|---|---|---|
| Wayback CDX query | 1 weekend | **Do first** |
| bsnpr.com DevTools recon | 1 hour | Blocks 4 features |
| League email | 1 hour | Run in parallel today |
| Finish Wikipedia fetches | 2 hours | No |
| Rebuild game pool | 1 weekend | After Wayback |
| Postgres schema + ingest | 2–3 weekends | Only if going native |
| React Native port | 3–4 weekends | Last |
| Deep newspaper archive | Years | Never blocking |
