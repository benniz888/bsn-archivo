# Session Summary — BSN Archivo

**Date:** 1 September 2026
**Project:** A Basketball-Reference-style archive and game hub for Puerto Rico's Baloncesto Superior Nacional (BSN), built as a single self-contained HTML file for personal use, intended to become an App Store product.
**Owner:** Alejandro "Benniz" — business analyst in San Juan, building the sports content brand `bennizpr`.

---

## Overview

The session began as a research question ("can I get all-time BSN data?") and ended with a working, feature-complete single-file web app plus a research corpus and a build roadmap.

The arc was: map what BSN data exists → assess feasibility honestly → extract everything obtainable → build the app → progressively add Hall of Fame, refuerzos, live-season sections, three games, and finally the MVP-completing layer (daily puzzle, streaks, share cards, favourite club, global search).

The single most valuable output is not the app but a **research finding**: the retired bsnpr.com stats engine published season leaders back to **1957**, and those URLs are likely still in the Wayback Machine. That one dataset unlocks nearly every remaining gap in the project.

---

## Objectives

1. Identify every source of historical BSN data (all eras, all players).
2. Assess honest feasibility of a "complete" BSN database.
3. Extract the maximum data obtainable without archival fieldwork.
4. Build a personal-use HTML reference app (Basketball Reference style, NBA-app polish).
5. Add a Hall of Fame section.
6. Add a refuerzos (imports) section.
7. Add real logos/photos, or a path to them.
8. Add official-BSN-app features (standings, team pages, news, stats) and NBA-app features (history, highlights, past games, clinching moments, on this day, season start).
9. Add games modelled on Immaculate Grid and 82-0.
10. Bring the build to MVP-complete so the remaining gaps are the *ask* in a pitch.

---

## Major Decisions

### Research and data

**Honest feasibility scoring instead of encouragement.** Rated the project 8/10 for a modern-era app (2005–present), 6/10 for season-level history to 1930, and **3/10** for the stated vision of every player and every box score since 1930 — because that last one is an archival project (microfilm, OCR, thousands of volunteer hours), not a software project. Recorded so the next session doesn't over-promise.

**RealGM has a hard floor at 2011-12.** Verified directly, not assumed. Awards only reach 2014-15. This is the ceiling for any scraper-based approach and should not be re-investigated.

**es.wikipedia.org is cache-only and cannot be fetched** in this environment; content is only reachable through search snippets. English Wikipedia fetches fine.

**The sandbox cannot reach RealGM, Wikipedia, or the Wayback Machine over the network** — only an allowlist (PyPI, npm, GitHub, Ubuntu). All data acquisition had to go through `web_fetch`/`web_search`, one page at a time. **This is why the Wayback CDX query was never run and remains the top outstanding task.** It must be done by the user or in an environment with open network access (e.g. Claude Code).

**`web_fetch` can only fetch URLs already present in the conversation.** Constructed/guessed URLs are rejected. Search first, then fetch the returned link.

### Data integrity philosophy

**Show the gaps rather than hide them.** A stats archive that conceals its holes is worse than one that displays them. Every uncertain figure is flagged in the UI, not silently smoothed. This drove the `confidence` fields, the Sources tab, and the in-game "N of 15 categories were never recorded" message.

**Never fabricate.** No invented image URLs, no invented news, no invented video IDs, no guessed team colours presented as fact, no plausible-but-unverified stats. Where data was missing, the app says so. This was applied consistently even when it made a feature less impressive.

**`NULL` ≠ `0`.** Unrecorded stats must never be stored as zero — it silently corrupts every career leaderboard. Enforced in the schema design and in the game pool (`ppg:null` renders as a dash).

### App architecture

**Single self-contained HTML file, no build step, no dependencies.** Chosen for portability and because the user opens it locally. Fonts load from Google Fonts with system fallback.

**Vanilla JS, no framework.** Boring and proven; keeps the file portable and readable.

**Original SVG crests instead of real logos — with a drop-in image layer underneath.** Rationale: no image generation available and fabricating URLs would produce broken boxes. So every crest and portrait renders as drawn SVG *and* sits under an `<img>` slot that takes over automatically if a file exists at the expected path. Zero images = perfect render; adding images = progressive enhancement, no code change.

**Team colours: six verified, the rest approximated and labelled as such.** Verified from Wikipedia: Bayamón, San Germán, Quebradillas, Guaynabo, Mayagüez, Aibonito, Guayama. Every franchise card states which category it falls in via the `colorSrc` field.

**Design direction: "hardwood in shadow", not generic sports dark mode.** Warm dark browns (`--ink:#17110D`) with brass accent, because 28 franchise colours needed to carry all the chroma without clashing. Typography: Archivo Black display + IBM Plex Sans with tabular numerals.

**The hero is the championship ribbon, not a big number.** 97 season blocks coloured by winning franchise, laid out in decade rows, so dynasties read as solid colour runs (Bayamón's 1971–75 five-peat). Chosen because it is instantly legible, uses only real data, and nobody has rendered BSN history that way before.

**Spanish-first positioning.** Nobody is building a Spanish-language BSN product; that is the moat. Section names use BSN vernacular (`Juega`, `La Cuadrícula`, `Mi equipo`, `#LaMásDura` — the league's own hashtag).

### Games

**Immaculate Grid uses team × attribute axes, not team × team.** Rationale: a team × team grid requires players with multiple franchises, and the verified pool has very few. Attribute columns (MVP, scoring champion, refuerzo, nativo, NBA, 10k points, decades) make every cell answerable. **Revisit this once the pool grows** — true team × team is the better game.

**82-0 became 34-0.** BSN seasons are 34 games. Named *La Temporada Perfecta*.

**34-0 spins a decade, not a franchise+decade.** Rationale: decade membership is verifiable for nearly every pool player; full club history is not.

**The 34-0 rating formula was rewritten mid-build.** The first version summed points/rebounds/assists and produced a **median result of 0-34**, because most pool players have only one recorded category. Fixed by adding honour weights (`TAGV`: MVP 9, scoring title 7, 10k 5, legend 5, NBA 3, champion 2) so achievement stands in for missing stats. Recalibrated the sigmoid to `K=125, S=28` against 20,000 simulated drafts.

**Boards are only issued when all nine cells have a verified answer.** Generation retries up to 600 times, and the daily seed nudges up to 40 times on failure. Verified: 1,095 consecutive days generate successfully, zero failures.

### MVP completion

**Recommendation given, and it was "add almost nothing."** The app already had more features than an MVP needs; what was missing was a *reason to exist* the official app can't claim. The user overrode this — wanting the MVP to be the finished app with gaps as the ask — which was accepted and built.

**Positioning identified: the seven-month gap.** The BSN season runs late March to August. The official Genius-Sports-powered app owns "today" (live scores, standings, news) and cannot be beaten there. But it has nothing to do in September. History and games are year-round. Pitch line: *the official app covers the season; this covers the other seven months.*

**Daily seeded board over infinite random boards.** Immaculate Grid's magic is that everyone gets the same puzzle and compares scores. Seeded from the date via `mulberry32`.

**Storage wrapper with silent fallback.** `localStorage` when opened normally, in-memory when sandboxed. Never throws. Chosen because the file may be opened locally *or* inside a sandboxed viewer.

### Legal / commercial (relevant only if this ships publicly)

- Stats are facts and not copyrightable; a compiled *database* can be protected.
- Wikipedia is CC BY-SA — usable with attribution.
- **Scraping RealGM/Proballers for a commercial app is the real exposure.** Use them to verify, not as a shipped source.
- **Team logos and player photos are a hard no** without permission — Apple rejects apps over this.
- Therefore **league permission stops being optional** the moment this goes public.
- Current build is explicitly personal-use, which is why real logos/photos were permitted by the user.

### Rejected ideas

- **Full 1930-present box scores before shipping** — rejected as project-killing. The archive work is open-ended; if it's a prerequisite, nothing launches.
- **Fabricated news/video/highlight sections** — rejected. Hollow sections make a pitch look unfinished; better to omit.
- **Hotlinking Wikipedia/Commons images** — rejected; no verified URLs, and broken images are worse than drawn ones.
- **Retired-number names** — Bayamón (8 numbers) and Guaynabo (3) are published as digits only. Refused to guess names; listed digits and said why.
- **Deferring player identity resolution** — flagged as one of the three things that will kill the project.

---

## Features Added (final app state)

Thirteen tabs in `bsn_archivo.html`:

1. **Today** — live date, season status, **Mi equipo** club picker, **On this day** (15 dated events, date-aware), season calendar 2024–26, next-season guidance, official channel links.
2. **Championships** — the 97-season ribbon hero, stat strip, titles-by-franchise bars, **finals head-to-head matrix**.
3. **Games** — 2025 Finals game-by-game with scores and quarter splits, clinching moments back to 2009, standings viewer (2009 seeded), instructions for wiring the live feed.
4. **Juega** — three games (below).
5. **Every season** — searchable/filterable table, 1930–2026, with per-row notes.
6. **Franchises** — 32 clubs, crest cards, detail panel with coach/arena/finals record/title chips.
7. **Hall of Fame** — 18 players sortable by era/points/MVP, "Honoured in stone" (4 arenas named for players), retired numbers.
8. **Refuerzos** — rules (Articles 22.1, 23.1, 13.1), the 2024 rule-change timeline, 2025 leaderboard impact, roster-split visual.
9. **Career leaders** — top 10 points/rebounds/assists, sortable bars + table, MVP repeat winners.
10. **Scoring titles** — SVG line chart 1971–91, full table, metric-change explanation.
11. **Records** — 11 league records, Hall of Fame coaches who passed through, BSN→NBA players.
12. **Recent seasons** — 2026, 2025, 2024, 2020, 2017, 2009 detail cards with awards, All-Star fives, standings.
13. **Sources & gaps** — conflicts, gaps, coverage matrix, image drop-in instructions, the Wayback lead.

**Games:**
- **La Cuadrícula** — 3×3 grid, Daily (date-seeded, shared, persistent, streak-tracked) and Practice modes, rarity scores, emoji share card.
- **34-0** — decade slot machine, 5 picks, 1 skip, projection with lineup bonuses, share card.
- **¿Quién soy?** — progressive clue reveal, guess the player.

**Cross-cutting:** global search (players/clubs/seasons/legends/records), favourite club with drought and rival computation, drop-in image layer, `localStorage` persistence with memory fallback.

---

## Files Created

| File | Purpose |
|---|---|
| `bsn_archivo.html` | The app. Single file, 131KB, no dependencies. |
| `bsn_project_roadmap.md` | Seven-phase build roadmap (needs updating — see Current State). |
| `bsn_data/README.md` | Research findings, coverage matrix, the Wayback lead. |
| `bsn_data/bsn_champions_by_season.csv` | 96 rows, 1930–2025, champion/runner-up/confidence/notes. |
| `bsn_data/bsn_career_leaders.csv` | 30 rows — top 10 points, rebounds, assists. |
| `bsn_data/bsn_scoring_champions.csv` | 26 rows, 1966–1991, with metric column. |
| `bsn_data/bsn_records.csv` | 11 league records. |
| `bsn_data/bsn_franchises.csv` | 28 franchises. |
| `img/crest/README.txt` | Placeholder folder for club logos. |
| `img/player/README.txt` | Placeholder folder for player photos. |
| `summary.md` | This document. |

---

## Files Modified

`bsn_archivo.html` was built and extended across five passes:

1. **Initial build** — 8 tabs, ribbon hero, SVG crests, 52KB.
2. **Hall of Fame + Refuerzos + images** — added 2 tabs, finals matrix, image drop-in layer, 2009/2020 season cards. 78KB.
3. **Today + Games** — added 2 tabs, extended archive to 2026, corrected 2025 data, added coaches to franchises, standings/clinchers/calendar/on-this-day. 94KB.
4. **Juega** — added games tab, 45-player verified pool, three games. 120KB.
5. **MVP layer** — daily seeded board, streaks, share cards, favourite club, global search, storage wrapper; extracted `showTab()` for search navigation. 131KB.

`bsn_data/bsn_champions_by_season.csv` — the 2024 runner-up (Osos de Manatí) was found later and added to the app but **not back-ported to the CSV**. See Current State.

---

## Current State

### Done and verified

- App runs clean. All builders execute headless without error; tags balanced; every nav tab has a matching section.
- 97 seasons, 96 champions, **zero duplicate champions or runners-up**.
- Daily board: 1,095 consecutive days generate successfully; first 60 boards all distinct; same seed reproduces the same board.
- 34-0 curve calibrated over 20,000 drafts: median 21-13, p5 = 4 wins, p95 = 33, perfect 34-0 in 1.2% of *random* drafts.
- Storage fallback verified with `localStorage` undefined.

### Known gaps and issues

- **1953 has no champion** in any source consulted. Either no season was held or the franchise table is incomplete. Unresolved.
- **1945 champion is disputed** — English Wikipedia says Capitalinos de San Juan; Spanish Wikipedia says Santos de San Juan. Both agree the runner-up was Gallitos de la UPR. App carries the English version and flags it.
- **1942–43 is folded into 1942**, so **San Germán shows 13 titles where most sources say 14**. Documented in the Sources tab. A proper schema needs a season key that can represent split-year seasons.
- **2026 title is provisional** — sourced from RealGM (which labels it "2025-26"); Wikipedia has not updated past 2025. The resolution reached: Bayamón won both 2025 (17th, Gallinari Finals MVP) and 2026 (18th, Balkman Finals MVP), back-to-back.
- **No player season stats before 2011** exist in any fetchable public source. This is the real wall.
- **Season MVPs by year not captured** — Wikipedia renders them in a sortable widget that does not survive text extraction. Only repeat-winner counts were obtained.
- **Scoring titles 1956–1965 and 1992–present not captured** — same article, same table, simply not fetched. Easy win.
- **Retired-number names unknown** for Bayamón's 8 and Guaynabo's 3.
- **Standings exist for 2009 only.**
- **No news, video, or highlights** — deliberately omitted rather than faked.
- **Game pool is 45 players across 19 franchises** — the binding constraint on both games.
- **`bsn_project_roadmap.md` is now partly stale** — written before the app existed. Phases 0/1/2 descriptions still stand, but it does not reflect the built app, the games, or the MVP layer.
- **2024 runner-up not back-ported to the CSV** (it is correct in the app).
- **`img/` folders are empty** — the user has not yet added logos or photos.

---

## Important Context

### User profile and preferences

- Alejandro "Benniz", 23, San Juan PR. Business analyst (Contact Center division, major PR bank). Strong SQL, Excel, Power BI. Double major: Business Analytics + Sports Marketing, Saint Joseph's, graduated May 2025.
- Building `bennizpr` — sports content across Instagram, YouTube, TikTok. Goal: recognition, then player interviews about athlete mindset.
- Die-hard: FC Barcelona, Argentina, Dallas Mavericks, MLB teams with Puerto Rican players.
- Carries a **global instructions framework** (TIER 1) favouring: autonomous execution, zero fluff, phased work, MVP-first, durable artifacts over ephemeral chat, `snake_case` filenames, comments explaining "why" not "what".
- Communicates in English; the product should be Spanish-first.

### Working conventions established

- `snake_case` for all filenames.
- Comments in code explain rationale, never mechanics.
- **Verify before shipping** — every build pass ended with headless execution of all builders plus data-integrity assertions (duplicate checks, distribution tests, determinism tests). Continue this.
- Deliver files, not walls of code in chat.

### Environment constraints (important — these bit repeatedly)

- Sandbox network allowlist excludes RealGM, Wikipedia, and web.archive.org.
- `web_fetch` rejects URLs not already in the conversation.
- `es.wikipedia.org` is cache-only.
- Node is available and was used for headless testing of the app's JS.

---

## Conversation Insights

- **The citations were more valuable than the article.** The Wayback lead was found not in Wikipedia's prose but in its *reference list* — every scoring-champion figure cited `bsnpr.com/estadisticas/lideres.asp?anio=YYYY` with `anio` values from 1957 to 2004. Worth remembering as a research technique: check what a source cites, not just what it says.
- **Inverting a table surfaces its holes.** The season-by-season champion list was built by inverting Wikipedia's per-franchise "years won" lists. That inversion is what revealed the 1953 gap and made duplicate-detection possible — the franchise view hid both.
- **A game can be an honest diagnostic.** The 34-0 result explicitly reports how many stat categories were unrecorded. Rather than hiding the data gap, the game surfaces it — which doubles as an argument for why the archive project matters.
- **Sim calibration needs empirical testing.** The first rating formula looked reasonable and was badly broken (median 0-34). Only running 20,000 simulated drafts revealed it.
- **The "help me" ask should be one dataset, not a vague request.** The pitch is stronger as "the player pool is 45 because that's all this archive can verify; one dataset takes it to hundreds and unlocks grid axes, sim accuracy, standings, and box scores" than as "help me build an app."

---

## Outstanding Tasks

- [ ] **Run the Wayback CDX query** for archived `bsnpr.com/estadisticas/*` — the highest-value action in the project.
- [ ] **Run DevTools recon on bsnpr.com** — find the JSON API behind the stats tables; determine how far back `season` goes.
- [ ] Probe for the Genius Sports / FIBA LiveStats endpoint on a game page (per-game box scores).
- [ ] Email the BSN league office and the Federación de Baloncesto de PR — ask for historical media guides, record books, retired-number names, and data access.
- [ ] Finish the scoring-champions fetch (1956–65 and 1992–present).
- [ ] Resolve the 1945 Capitalinos/Santos conflict.
- [ ] Resolve the 1953 gap.
- [ ] Decide how to represent the 1942–43 split season; fix San Germán's title count.
- [ ] Confirm the 2026 title and promote it from provisional.
- [ ] Back-port the 2024 runner-up into `bsn_champions_by_season.csv`.
- [ ] Add real logos to `img/crest/` and photos to `img/player/`.
- [ ] Update `bsn_project_roadmap.md` to reflect the built app.
- [ ] Grow the game pool; switch La Cuadrícula to true team × team axes once it supports it.
- [ ] Populate `STANDINGS` for recent seasons once the API is mapped.

---

## Suggested Next Steps

**In this order.**

1. **Wayback CDX query.** Query `http://web.archive.org/cdx/search/cdx?url=bsnpr.com/estadisticas*&output=json&limit=50000&collapse=urlkey`, filter for `lideres.asp`, note which `anio` values were captured, fetch each snapshot with the `id_` suffix for raw HTML, parse with pandas `read_html`. **Must be done outside this sandbox** — Claude Code is the right tool. If coverage is good, this collapses half the archival phase into a weekend.
2. **DevTools recon on bsnpr.com** (~1 hour). Unlocks standings, box scores, and news simultaneously — four features currently blocked on one task.
3. **League email.** Costs nothing, converts the biggest legal risk into the biggest asset, and is the same door as player interviews.
4. **Finish the cheap Wikipedia fetches** — scoring champions, season MVPs if extractable.
5. **Rebuild the game pool** from whatever step 1 yields, then upgrade La Cuadrícula's axes.
6. **Only then** consider React Native / Expo and the App Store path.

---

## Start Next Conversation With

**Current project:** BSN Archivo — a single-file HTML archive and game hub for Puerto Rico's Baloncesto Superior Nacional, covering 1930–2026. Personal build, intended as an MVP to pitch.

**Current progress:** Feature-complete at 131KB. Thirteen tabs: Today, Championships, Games, Juega, Every season, Franchises, Hall of Fame, Refuerzos, Career leaders, Scoring titles, Records, Recent seasons, Sources & gaps. Three games (daily seeded Immaculate Grid with streaks and share cards, 34-0 draft sim, clue-based player quiz), global search, favourite club, and a drop-in image layer. All data verified; all gaps flagged in the UI.

**Immediate priorities:** (1) Run the Wayback CDX query against archived `bsnpr.com/estadisticas/lideres.asp` — the old league site published season leaders back to 1957 and those pages are dead but likely archived. (2) DevTools recon on bsnpr.com for the live JSON API. (3) Email the league.

**Known issues:** 1953 has no champion; 1945 champion disputed between two Wikipedia editions; San Germán shows 13 titles instead of 14 because 1942–43 is folded into 1942; the 2026 title is provisional from RealGM; no player season stats before 2011 anywhere; game pool is only 45 players, which constrains both games; `bsn_project_roadmap.md` is stale.

**Recommended first prompt to paste:**

> I'm continuing work on BSN Archivo — a single-file HTML archive of Puerto Rico's Baloncesto Superior Nacional, 1930–2026. I've attached `bsn_archivo.html` (the app), `summary.md` (full handoff from the last session), and the `bsn_data/` CSVs.
>
> Read `summary.md` first — it has every decision, constraint and known gap.
>
> The top priority is the Wayback Machine lead: the retired bsnpr.com stats engine published season leaders at `estadisticas/lideres.asp?anio=YYYY` for years 1957 through 2004, and those URLs now 404. Help me enumerate what's archived via the CDX API, pull the snapshots, and parse them into the schema. If you can't reach web.archive.org from your environment, write me the script to run locally instead.
>
> Two rules carried over from last session: never fabricate data — flag gaps instead — and verify every change by running the app's JS headless before declaring it done.
