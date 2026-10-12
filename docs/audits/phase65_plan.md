# PHASE_65_HISTORIA_JUGADORES: plan (no code written)

Status: PLAN ONLY, awaiting owner "approved". Branch `redesign-v3`. No commit, no push, nothing staged.
Refs read: 01_master_plan.md, 05_page_specs.md (Historia, Jugadores), phase60_claims.md, screens `Historia/Historia Phone landing page.png`, `Jugadores/Player page view.png`, `Jugadores/Jugadores landing page phone view.png`.
Probed live (Chromium, local server): Historia and Jugadores landings at 390px, player page at 390 and 1000px, 0 console errors. Findings below are measured, not assumed.

## 1. What I found (measured)
- **Circles**: `#jugadores .strip>div::after` is a 50px ring (8px border) at `right:-12px; bottom:-16px`, `opacity:.5`, painted *over* the tile text (no z-index, the label is not positioned). The ring covers the tile's bottom-right 38 x 34px; the label's bottom edge sits 15px above the tile bottom, so any label wide enough to reach the right third crosses the ring: "asistencias", "puntos por juego", "rebotes", "juegos", "MVP" at 1000px (confirmed in screenshot). The same ring motif exists on `.hero-stat::after` (Inicio) and `#jugadores .pcard::after`; only the strip tiles overlap text.
- **Historia phone landing (390px)**: eyebrow + 6-line lede (about 190px), then three stacked full-width stat cards of about 150px each, so the first "Explora Historia" card is below the second fold. The owner's screenshot also shows the page title tucked under the sticky header; in the current build the eyebrow clears the header (h1 at y=110, header bottom 56), so the cut-off is the stacked cards and long lede, not the header offset. I will re-check the title/header gap in WebKit at build time (the owner's capture is Safari) and fix it if it reproduces.
- **Jugadores phone landing**: same pattern (4-line lede, three stacked cards).
- **KPIs on Historia today**: landing `stats3` (3 big cards) + `#titleStats` strip (5 tiles) on the Cinta view = 8 numbers, two of which repeat the same facts.
- **Emoji in `web/`** (full scan of index.html, js, css, data/*.json, sw.js, manifest): `tabs.js` L3040/L3284 (`🔥` in streak pill markup), L3047/L3297 (`🔥` in the footnotes), L3003/L3017/L3267 (`🔥` in comments), `games.js` L408 (`🟩`/`⬛` in the Cuadrícula share text copied to the clipboard). `main.css` L2036 uses `✓` (U+2713, a plain text dingbat, not emoji); it goes away anyway, see the `.fixnote` item. `web/data/*.json`: 0 hits.
- **Internal changelog text shown to visitors**: Historia shows `.fixnote` "Celdas a 44x44px mínimo ... el survey encontró las celdas anteriores en 27.6x40px ... Corregido aquí." That is a dev note, not user copy.
- **Hardcoded "97"** (not computed): `index.html` L232 and L1963-adjacent strings in `tabs.js` (rachas note, VIEW_DESC "en 97 temporadas"). Master plan says computed counts are never hardcoded. I will compute these only in strings I am already touching; the rest is flagged in NEXT, not widened into this phase.

## 2. HISTORIA: keep / cut / change
| Item | Decision |
|---|---|
| Hero (eyebrow, h1, lede) | CHANGE: lede cut from 6 lines to 1-2 (string 1). |
| Landing KPI "18 títulos de Vaqueros de Bayamón, el club más ganador" | KEEP. Answers "who is the most successful club". Computed. |
| Landing KPI "97 temporadas documentadas, de 1930 a 2026" | KEEP. The scale of the archive; computed. |
| Landing KPI "franquicias distintas que han sido campeonas" | CUT. Repeats the Títulos view and `#titleStats`. |
| `#titleStats` "temporadas, 1930 a 2026" | CUT. Duplicate of the landing KPI. |
| `#titleStats` "con campeón identificado" | KEEP. Honesty KPI (PC4: show the gaps; 1953 has none). |
| `#titleStats` "títulos de X, el máximo" | CUT. Duplicate of the landing KPI. |
| `#titleStats` "franquicias han ganado" | CUT (also on the Títulos bars, which list them). |
| `#titleStats` "clubes activos sin título" | KEEP. A real question ("who has never won?") not answered by the bars. |
| `.fixnote` dev note (44x44px) | CUT (string 4). Also removes the only CSS `✓`. |
| Streak pill `🔥 N×` on scoring and MVP lists | CHANGE: text + small inline SVG bar glyph, "Racha de N (A-B)" (strings 5-8). |
| Tables | Already on the shared component (PHASE_63). Untouched. |
Result: 8 KPI numbers become 4 (2 on the landing, 2 on Cinta; at most 2 per screen).

## 3. JUGADORES: keep / cut / change
| Item | Decision |
|---|---|
| Landing 3 stat cards (376 con ficha, 18 Salón, N NBA) | CHANGE (not cut): one compact row of three on phone and desktop, number over a short label, no stacked giant cards. DECISION FOR OWNER: keep all three (recommended; you asked to reduce KPIs on Historia only) or keep two. |
| Hero lede (4 lines on phone) | CHANGE: shortened (string 9). |
| Player Resumen stat tiles (rebotes, asistencias, juegos, ppj, MVP) | KEEP all tiles; fix the ring so it never touches text (section 5). |
| Ring decoration | CHANGE: ring moves behind content (`z-index:0`, content `position:relative; z-index:1`), is clipped to the tile's top-right corner, `opacity` lowered, and the label/number get a reserved inset so ink never enters the ring's box. Keeps the motif, removes the overlap by construction, not by luck. |
| Missing stat "—" | OUT OF SCOPE here (PHASE_63 "sin dato" mark already ships on tables; the player tile dash was listed in 05 but is not in the owner's PHASE_65 list). Will report if still a bare dash, not change. |
| Orange "Lo que este archivo no sabe" note | KEEP as is. |
| Honors chips wrap | OUT OF SCOPE (not in the PHASE_65 request). |
| "récord mundial extraoficial" (Jonathan García, Récords de la liga + his ficha blurb) | CHANGE per phase60 (string 10). |

## 4. Layout
**Historia desktop (>=1000)**: eyebrow, h1, one-line lede; subnav pills; two KPI tiles side by side (red solid + neutral), "Explora Historia" 3-col card grid directly under, first row of cards inside the first 700px.
**Historia phone (390)**: eyebrow, h1 (clears the sticky header in WebKit and Chromium), lede 2 lines max, pills (scroll with the existing edge fade), then the two KPIs as one row of two compact tiles (number 32px, label 2 lines), then the 2-up explore cards. Target: first explore card fully visible above the bottom tabs at 844px height.
**Jugadores desktop**: same as above with three compact tiles in a row.
**Jugadores phone**: three tiles in one row would be too tight at 390 (labels would wrap to 4+ lines), so: the solid tile full width (compact, 1 number + 1 line), then two half-width tiles. Explore cards below.
**Player page tiles (both widths)**: tile = number, then label; ring in the top-right corner behind the content, clipped by the tile (`overflow:hidden` already), label has `padding-inline` so text stays clear of the ring on narrow tiles.
All tap targets stay >= 44px (pills, explore cards, tile-links). Focus ring stays site blue (`--focus`). Motion: none added.

## 5. Visual regression test design (rings vs labels)
File: `tests/test_player_ring_overlap.py` + probe `tests/harness/ring_overlap_probe.mjs` (same pattern as `test_cuadricula_exhaustive.py`: node + playwright-core, serves `web/` statically, skips with a stated reason if node or Playwright is missing; the finder already globs `/private/tmp/**/node_modules/playwright-core/index.js`. Note: `/private/tmp/bsn_harness/node_modules/playwright-core` is a hollow copy today, `bsn_harness_v2` is the working one, v1.56.1).
- Matrix: Chromium and WebKit x 390 and 1000px = 4 cases, x 3 players with different label lengths (Georgie Torres plus two with missing stats and long labels), all via `#jugadores/jugador/<slug>`.
- Geometry, not pixels: for every tile in `.rp-stats .strip>div` the probe (a) reads each `::after` decoration's box from computed style (`position:absolute`, `width/height`, `right/bottom/top/left`, `border-radius`) relative to the tile and clips it to the tile (overflow hidden), (b) takes the label and number *ink* rectangles via `Range.getBoundingClientRect()` over the text nodes (not the block box, which spans the whole tile), (c) tests circle-vs-rectangle intersection (nearest point on the rect to the circle centre, with the circle's outer radius), and fails if any decorative circle overlaps any ink rect. Also fails if the decoration is not behind the content (z-order check: content `z-index` greater than the circle's).
- Generic: the probe enumerates decorations (absolute, circular pseudo-elements) in `#jugadores`, so a future ring on a new tile is checked without editing the test.
- Anti-regression proof: the test is run once against the current CSS and must FAIL (recorded in the report), then pass after the fix.
- Also asserts text contrast of label and number >= 4.5:1 in dark and light, and 0 console errors, per case.
- Screenshots are attached per run (not baselined, to keep the repo small); the assertion is geometric.

## 6. Emoji guard
File: `tests/test_no_emoji_in_web.py`. Static scan of every text file under `web/` (index.html, js, css, data/*.json, sw.js, manifest), comments included, so strings, CSS `content:`, and data-driven UI strings are all covered. Codepoints flagged: U+1F000-U+1FAFF, regional indicators, U+FE0F, U+200D, U+20E3, and the BMP Emoji_Presentation set (U+231A-231B, 23E9-23FA, 25FD-25FE, 2614-2615, 2648-2653, 267F, 2693, 26A1, 26AA-26AB, 26BD-26BE, 26C4-26C5, 26CE, 26D4, 26EA, 26F2-26F5, 26FA, 26FD, 2705, 270A-270B, 2728, 274C, 274E, 2753-2755, 2757, 2795-2797, 27B0, 27BF, 2B1B-2B1C, 2B50, 2B55). Plain text symbols stay allowed (arrows, check mark U+2713, black squares U+25A0/25A1). The failure message prints file:line:codepoint:name. Plus a rendered-DOM check inside the Playwright test above for Historia and Jugadores (catches runtime-built text, for example `String.fromCodePoint`). The guard covers the whole site, so `games.js` L408 must change in this phase (string 11) or the guard fails.

## 7. Claims (phase60_claims.md) applied to these two pages
Searched Historia and Jugadores text for every row of the audit table. Only one row lands on these pages:
- "récord mundial extraoficial" (Jonathan García, 33 asistencias): Jugadores > Récords de la liga (`index.html` L561 area) and the player blurb (L710 area). Phase60 offers "añadir fuente o 'según la prensa'". I will use "según la prensa" (string 10), since I cannot invent a source (PC1). The same sentence at L629 is Inicio's on-this-date timeline, not one of these pages; flagged, not changed.
- No other row appears on Historia or Jugadores. The "verificada/verificado" rows are Juega, Archivo, Equipos; "Mejor Jugador del Mundo" (tabs.js, BIO life line) is flagged for PHASE_66 in the audit itself.
- NOTE: phase60_claims.md says "Proposed text is a proposal only". Your message says these are approved, so I am treating the concrete wordings as approved; rows that only say "needs a source" are NOT applied.

## 8. Build constraints (step 2)
Closures only, 0 new top-level names (inventory baseline 476; `streakRun`-style helpers live inside `buildScoringTable`/`buildMvpYears`). `scoringStreaksFor` keeps its name and signature; the run start year is derived as `year - length + 1`. Asset hashes refreshed with `src/update_asset_hashes.py`; `sw.js` cache version follows the existing rule. Streak pill font raised from 10px to `--fs-2xs` (12px, the type scale floor). Verify Chromium + WebKit, 390 and 1000px, dark and light, 0 console errors; one phone and one desktop screenshot per page; suite baseline 704 passed, 1 xfailed, 1 known failure (`test_web_text`).

## 9. Questions for you
1. Jugadores landing: keep all three KPIs (recommended) or two?
2. Historia KPIs: OK with 2 on the landing and 2 on Cinta (list in section 2)?
3. Cuadrícula share text (string 11): `■`/`□` squares OK?
4. Remove the `.fixnote` dev note (string 4)?
5. "según la prensa" for the García record (string 10): OK, or do you have a named source?
