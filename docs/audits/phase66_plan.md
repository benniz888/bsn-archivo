# PHASE_66_EQUIPOS: plan (Step 1, plan only; nothing built, nothing staged)

Read: global/project/session tiers, 01_master_plan.md, 05_page_specs.md (Equipos), phase60_claims.md, bsn_team_page_plan.md, both screens in ~/Desktop/newredesign/Equipos/, and the current code (`web/js/tabs.js` showTeam ~L2067, tile/tileGone/buildTiles ~L2026, buildEquiposHero/Landing ~L5966-6040, buildRetiredNums ~L3073; `web/js/data.js` F, RETIRED, POOL*). Archive/folder look is out of scope until PHASE_73.

## 0. Facts that shape the plan
- `RETIRED` holds only two clubs, digits only, no names, no years: Bayamón `4 · 5 · 9 · 15 · 16 · 17 · 17 · 54` (r[1]=8, the duplicate 17 is kept as recorded, ×2) and Guaynabo `5 · 9 · 15`. The site's own text says the league publishes them as digits without names and the archive does not guess.
- Conflict to flag: `BIO` (Piculín Ortiz) says the number 4 is retired by Santurce, but `RETIRED` has no Santurce row. I will not add it to RETIRED without a source and your approval.
- The spec asks for "name and year retired" on each jersey tag. The data has neither. **Plan: tags show the number only.** Names/years appear only if you approve sourced research (see section 5).
- Roster data: POOL + POOL_2026 + POOL_RGM entries carry `n`, `c` (club keys), `d` (decades), `pos`, `ppg/rpg/apg`, `ns` (seasons), `hi`, optional `t` tags and `b` blurb; the 45-name seed also has HOF `hon`. Years/honors are not uniform across entries, so cards show only what exists (null = "sin dato", never 0).
- Colors: `F[k].colorSrc` is `wiki` or `approx`. Rule: the note stays on every club page, reworded.

## 1. Keep / cut / change

### Landing (`#equipos`, phone fixed)
| | Item | Why |
|---|---|---|
| CUT | Three stacked giant stat cards (stats3) | Phone problem in the screen; replaced by a compact strip |
| CHANGE | Title cut by sticky header | Add scroll-margin/top padding to the `#equipos` head so the h1 clears the header on phone |
| CHANGE | Crest grid first: 12 active, then 21 defunct (2 columns on phone, 4-6 on desktop), each crest tile links to the club page; tile shows name, titles count | Spec: crest grid first |
| CHANGE | Stats become one strip: `12 activos · 21 desaparecidos · 96 campeonatos (falta 1953)` (all computed from F/champOf, as today) | Compact, same numbers |
| CHANGE | Subnav pills: horizontal scroll, edge fade, active pill scrolled into view, pills at 44px | Spec + 44px rule |
| KEEP | Hero lede (computed counts), Resumen/Activos/Apoderados/Desaparecidas/Camisetas retiradas pills | Existing, test-covered |
| CUT | "Explora Equipos" xcard grid on the Resumen landing | Duplicates the pills and pushes crests below the fold |

### Club page (`showTeam`)
| | Item | Why |
|---|---|---|
| CHANGE | Narrow left column -> two columns at >= 900px: left = identity + signature stat + facts; right = roster + timeline + careo. One column on phone | Empty right half |
| CHANGE | Card border/accent from the club color, hero treatment per club (section 3) | Unique pages |
| CHANGE | Chip cloud -> interactive roster (section 4) | Request |
| CHANGE | "Campeón: ..."/"Subcampeón: ..." year lists -> one timeline strip of finals years (W/L letter + title text, not color alone) | Spec: non-color cue |
| CHANGE | "Colores verificados" tag -> "Colores de Wikipedia" (claims audit, tabs.js:2071) | Approved rewording that lands here |
| CHANGE | TEAM_LORE.man: drop "el que todavía se lo debe a su fanaticada" (editorial) | Claims audit L346 |
| CHANGE | TOWN_LORE.san: drop "el único pueblo de Puerto Rico fundado por negros libres" until sourced | Claims audit L373 |
| KEEP | Sourced lore lines, VENUES line (with "~" capacity tooltip), 2026 record tag, coach, rival line, starting five, careo table | Existing and sourced |
| ADD | Camisetas retiradas block (section 5), only for clubs that have RETIRED data | Request |
| N/A | "récord mundial extraoficial" (Inicio) and "Mejor Jugador del Mundo" (player bio) do not land on Equipos; not touched | Out of page scope |
| N/A | `Dirigente —` empty row: hide the row when there is no coach (today shows a dash) | PC4 honesty is kept by the existing "sin dato" notes elsewhere; an empty row adds nothing |

## 2. Layout
Desktop (1000px+): header band full width (crest large, name, city/founded, accent bar, signature stat) -> two columns 5/7. Left: facts list (cancha, dirigente, 2026 record, rival, lore lines, color note). Right: roster module, finals timeline, careo table, cinco inicial, camisetas retiradas rail (full width below).
Phone (390px): header band, signature stat, facts, then sections as stacked blocks; roster filters collapse to a single row of horizontally scrolling chips + a sort select; retired rail scrolls horizontally with snap.

## 3. What is unique per club, and where it comes from
All of it is computed from existing data; no per-club hand-written copy except the existing lore.
- **Accent**: `F[k].c1/c2` set as `--club`/`--club-2` on the page. A guard picks a text-safe variant (>= 4.5:1 on the card background, dark and light) and a graphics variant (>= 3:1); if a club color fails, text falls back to the ink color and the color is used only as a graphic. A test enumerates all 33 clubs x 2 themes.
- **Signature stat** (one per club, chosen by this priority, all from `F.won/.ru`, `champOf/ruOf`): longest run of consecutive titles (>= 3, e.g. Bayamón 1971-75, from data) -> best decade by titles -> longest title drought if the club has a title -> finals lost with no title (never-champions) -> years active (defunct clubs). The stat names its basis ("racha de 5 títulos seguidos, 1971-1975").
- **Hero treatment**: three variants chosen by data: dynasty (run >= 3: run years highlighted on the timeline), contender (titles, no run), seeker (no title: finals markers only), defunct (years-active line + lineage note from D2 events only where the data has them).
- **Content blocks present only when data exists**: lore, town lore, cancha, retired jerseys, cinco inicial, notable players (`t` tags / HOF), rival record. A club with none shows none (no filler).
- Source for lore: `TEAM_LORE`/`TOWN_LORE` (sourced in `docs/specs/bsn_team_page_plan.md`, es.wikipedia 2026-09-14). Defunct clubs get no lore in this phase unless you approve researched lines (section 6).

## 4. Interactive roster
Source: `POOL.filter(p=>p.c.includes(k))` (same as today), grouped, 24 per page with "Mostrar más" (paginate, no virtualization needed).
- **Filters**: era (decade chips from `p.d`, only decades the club actually has), position (Armadores/Aleros/Pivots groups from `p.pos`; players without position under "Sin posición", not hidden), text search by name (accent-insensitive via existing `norm()`). Active filters show a count in an `aria-live="polite"` line ("23 de 61 jugadores").
- **Sort**: select with Nombre, Puntos por juego (nulls last), Temporadas (nulls last), Más reciente.
- **Card/row**: name (link to the player page), position, decades, seasons, ppg. Hover or focus (and tap on phone) opens a detail strip under the row: years in the archive and honors (from `t`/`hon`/`b` where present; "sin dato" otherwise), link "Ver ficha".
- **Keyboard**: filters are native buttons/select/input in tab order; the roster list is a single tab stop with roving tabindex (Up/Down move, Home/End jump, Enter/Space toggles the detail strip, Enter on the link opens the player, Esc closes the strip and returns focus to the row). Visible `:focus-visible`, rows >= 44px.
- Prefers-reduced-motion: no expand animation.
- Implementation: closures inside `showTeam` (no new top-level function names; inventory stays at 476). Reuse the shared `buildTable` from PHASE_63 if its filter/paging options cover this (verified first at Step 2 start); otherwise a local closure.

## 5. Retired jerseys (SVG)
- **Generic jersey**: one inline SVG symbol (simple tank silhouette, no stripes/collar marks/logos/sponsor shapes, no league or club marks), fill from `--club`, trim from `--club-2`, number set as SVG text on the back, large and high-contrast (number color chosen by the same contrast guard, >= 3:1 as graphic, >= 4.5:1 if treated as text).
- **Hanging**: rail across the block, a hanger per jersey, soft drop shadow; a small tag below with the number (and, only if approved, name + year). Sway on hover/focus: `transform: rotate(±1.5deg)` only, disabled under `prefers-reduced-motion`. No real photos.
- **Accessibility**: the rail is `aria-hidden` visual art; an adjacent real list (`<ul>`, visible on the page, not hidden) reads "Números retirados: 4, 5, 9, 15, 16, 17 (dos veces), 54". The duplicate 17 renders as one jersey with "×2" in the tag, matching today's chips.
- **Honesty**: a "Colores aproximados" note under the rail when `colorSrc==='approx'`, "Colores de Wikipedia" otherwise, as on the hero. The existing "La liga los publica como dígitos, sin nombres" note stays.
- **Data needed**:
  | Club | Numbers | Name/year | Source today |
  |---|---|---|---|
  | Bayamón | 4, 5, 9, 15, 16, 17, 17, 54 | none | BSN export, already cited on the Archivo coverage page; duplicate 17 unresolved (kept as recorded) |
  | Guaynabo | 5, 9, 15 | none | same |
  | Santurce | 4 (per BIO text only) | Piculín Ortiz per BIO | not in RETIRED; **not shown** until sourced |
  Optional research (needs your OK): find sourced name + year per number for Bayamón and Guaynabo (club or league pages, es.wikipedia). Each result would be listed with its URL in the strings file; nothing displayed until you approve that line.
- The existing "Camisetas retiradas" view (`buildRetiredNums`, chips) is replaced by the same jersey rail component for all clubs that have data.

## 6. Open questions for you
1. Retired tags: number-only (my default) or approve a research pass for names/years?
2. Santurce #4: keep out until sourced (default)?
3. Defunct clubs: no lore this phase (default), or research?
4. Confirm the claim rewordings I treat as approved: tabs.js:2071 (colors), L346 (`man`), L373 (`san`). The audit marked them "proposed"; strings are in the strings file as PENDING.

## 7. Test plan
- Pytest (new `tests/test_equipos_phase66.py`): every club has valid `c1/c2`; contrast guard passes for all 33 clubs x light/dark (text 4.5, graphics 3); signature stat is computed from F (no digits hardcoded in the JS); jersey SVG contains no `<image>`/external href/`<text>` other than the number; no emoji (existing `test_no_emoji_in_web`); no new top-level declarations (inventory still 476, baseline file untouched); no "según la prensa"-style phrasing and no removed claims reappear; RETIRED unchanged; roster filter/sort pure logic (decade/position/null ordering) via the existing JS-eval harness pattern.
- Existing suite: baseline 721 passed, 1 xfailed, 1 known failure in `tests/test_web_text.py`; `test_equipos_copy.py` and `test_equipos_gone_tiles.py` updated only where the approved landing change forces it.
- Real browsers (`/private/tmp/bsn_harness` Playwright): Chromium and WebKit, 390 and 1000px, dark and light, landing + at least Bayamón (dynasty, retired), Cangrejeros (contender), Maratonistas/any defunct, Manatí (no title, seeker). Checks: 0 console errors, no horizontal scroll, tap targets >= 44px via bounding boxes, keyboard walk of filters + roster + retired rail, reduced-motion emulation (no sway/animation), focus visible. One phone + one desktop screenshot per page.
- Duplicate-selector sweep and a literal scan of buildTable render callbacks / `.style.` assignments before CSS work (standing memory rules).
- No writes to `data/clean/`, no `make parse-players`, no commit/push/staging.
