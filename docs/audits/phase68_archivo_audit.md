# PHASE_68 Step 1 — Archivo section audit

Read-only audit, 2026-10-11. Nothing in the app, data or other docs was changed. Aesthetics ("archive/folder look") are deferred to PHASE_73 and excluded.

## Scope note (read first)

The brief describes "Archivo" as champions, franchises, records, career leaders and scoring champions. In the code those live in **Historia**, **Jugadores** and **Equipos**. The nav section actually named **Archivo** (`TABS`, `web/js/tabs.js:899`) is ask / query builder / coverage / data quality / calendar / glossary. I audited both: all 6 Archivo views plus the champions, scoring, records, leaders and franchise views they relate to (Historia, `jugadores/lideres`, `jugadores/records`, Equipos). Not walked in detail: Jugadores search/compare/salón/nba/dirigentes/canchas, player pages, Juega, Perfil, Inicio.

Method: `web/` served on port 8123; Playwright Chromium and WebKit, 390px and 1000px, dark and light (176 view-loads, script `/private/tmp/bsn_harness/p68_walk.mjs`), plus interaction scripts for Ask, query builder, season ribbon, keyboard focus and Back.

Automated results across all 176 loads: **0 console errors, 0 page errors, 0 failed requests, 0 horizontal overflow** (`scrollWidth == clientWidth` everywhere). Keyboard focus shows a 2px outline on every control I tabbed (subnav, input, chips). Not verified: error states with failed data fetches (my request-blocking did not take effect, likely cache or service worker), screen-reader output, contrast beyond the automated text sweep.

## Inventory

Routing: `applyHash()` (tabs.js:6742), `showTab`/`showView`/`setHash` (helpers.js:93+), views built by `VIEW_MAP` (tabs.js:6182). Section nav = `buildNav()` (rail on desktop, bottom bar on phone); each section gets a pill subnav from `_subnavEl()`. Legacy hashes `consulta`, `fuentes`, `hoy`, `records`, `refuerzos` redirect via `MOVED`.

| Section / hash | View | Controls | Builder (file) | Data feeding it |
|---|---|---|---|---|
| `#archivo` | Resumen (landing) | stat card, "Ver los huecos", view cards | `buildLanding`, tabs.js:~1092 | `manifest.json` |
| `#archivo/preguntar` | Preguntar | search input, 14 example chips, answer card with Ver/CSV buttons; header search (`hubAsk`) also routes here | `buildAsk`, `ask`, `runAsk` (tabs.js:4192–4250, 4483) | in-memory `F`, `YEARS`, `RECORDS`, `LEADERS`, `SCORING`, `BIO`, `PINDEX` (hydrated from `index/*.json`) |
| `#archivo/constructor` | A la medida | dataset select (12), text, from/to year, franchise, limit, Ejecutar/Limpiar/Copiar, sortable table, CSV | `buildQB`, `runQB` (tabs.js:4350+) | same in-memory tables; hydrated from `index/seasons`, `scoring_titles`, `mvp`, `career_leaders`, `records`, `franchises` |
| `#archivo/cobertura` | Cobertura y fuentes | none (static grid, source cards) | `buildCoverage` (4440), `buildSources` (3343) | `COVERAGE` const, `manifest.json` counts |
| `#archivo/calidad` | Calidad de datos | sortable tables, toggles | `buildDQ`, `openDQ` (data-quality.js) | `index/data_quality.json` (fetched on view open) |
| `#archivo/calendario` | Calendario | sortable table, CSV | `buildCalendar` (tabs.js:1646) | in-code calendar consts |
| `#archivo/glosario` | Glosario | none | `buildGlossary` (4884) | `GLOSSARY` const |
| `#historia` + `/cinta` | La cinta | 97 year buttons, readout, "Ver {club}" | `buildRibbon`, `showSeason`, `renderReadout`, `loadSeasonExtra` (1803–1900) | `index/seasons.json`; `seasons/<y>.json` per click |
| `#historia/temporada/<y>` | deep link into cinta | — | `applyHash` | same |
| `#historia/titulos` | Títulos por franquicia | none | `buildTitleBars` (1925) | `index/franchises.json` |
| `#historia/dinastias` | Dinastías | none | `buildDynasties` (1944) | derived |
| `#historia/finales` | Finales (careo matrix) | none | `buildMatrix` (1966) | derived |
| `#historia/premios` | Premios y líderes | MVP / Campeones de anotación toggle | `buildMVPYears`, `buildSeasonAwards`, `buildScoringChart`, `buildScoringTable` | `index/mvp.json`, `index/scoring_titles.json`, `seasons/*.json` |
| `#historia/refuerzos` | Refuerzos | sortable table | `buildRefRules/Timeline/Scorers` | in-code consts |
| `#historia/temporadas` | Todas las temporadas | search, franchise select, sort, Ver 25 más / Mostrar todo, CSV | `buildSeasonFilters`, `buildSeasonTable` (1986–2000) | `index/seasons.json` |
| `#jugadores/lideres` | Líderes de carrera | category and order selects, bars, sortable table, CSV | `buildLeaderControls`, `buildLeaders` (3054) | `index/career_leaders.json` |
| `#jugadores/records` | Récords | none | `buildRecords` (3123) | `index/records.json` |
| `#equipos` + `/activos` `/duenos` `/desaparecidos` `/retirados` `#equipos/equipo/<k>` | Equipos | tiles, team detail | `buildTiles`, `buildOwners`, `showTeam` | `index/franchises.json` |

Cross-links that exist today: ribbon readout → club page and → Premios; Ask answer → club / season / player; Líderes and scoring rows → player page; Calidad → player page.

## Findings

Severity: high = wrong or misleading to a visitor; med = real usability or consistency gap; low = polish or unverified.

| ID | View | Sev | What is wrong | Evidence | Proposed fix | Effort |
|---|---|---|---|---|---|---|
| A01 | archivo landing, player pages | high | The landing stat card says "Antes de 2011 no hay estadística por temporada". The archive itself holds 2001–03 box scores, 2007+ season leaders and per-season files (Cobertura grid and `buildSources` gaps list say so). Same sentence in the player-page "no sabe" warning. PC4 honesty is violated in the one place that exists to state coverage. | tabs.js:1092 and :2700; screenshot `archivo_landing_chromium_390_dark.png`; `COVERAGE` rows "2000s … boxscores + posiciones de 2001–2003"; `manifest.json` counts | Derive the cutoff from `MANIFEST`/`COVERAGE` or reword to what is true ("estadística completa por temporada solo desde 2011" if that is the real claim). Owner confirms wording. | S |
| A02 | cinta season detail, Premios scoring list | high | Per-season detail prints source strings verbatim with visible defects: typo "GOERGIE TORRES" (1986 MVP); truncated names "Ayuso, Elias 'Lar", "Morales, Mario 'Qui", "Butler, Mario Albe" (2013, 1986 leaders); ALL-CAPS and unaccented names ("RAUL FELICIANO", "Teofilo Cruz", "NEFTALI RIVERA"); three name formats on one page ("Bass, Paris", "CHRISTIAN DALMAU", "Hector Blondet"). The same player shows as "Teófilo Cruz" elsewhere. | Interaction run: 1986 and 2013 `#seasonExtra` text; Premios scoring list buttons (walk.json, `historia/premios`) | Data fix belongs to PHASE_72 (typo, truncation from `src/` parse). Build can display `canonical name` from the player index when `bsnpr_id` resolves, else raw, never guess (PC1). | L (data) / M (display) |
| A03 | Récords vs Líderes | high | Two views contradict each other: Récords says "Rebotes de carrera: 6,178, Rubén Rodríguez"; Líderes #1 in rebounds is Mario Butler, 8,236 in 779 games. Butler's range (1980–2008) and MVP join are already flagged unverified. Also Dalmau assists 2,302 / 537 games ≠ 5.1 (has a † note in Líderes, not in Récords or Ask). | Live eval: `RECORDS` row vs `LEADERS.rebounds[0]`; `data_review_todo.md` "PHASE_67C fixup" | Until sourced, show a visible note on both views that the two lists disagree (use the existing `.warn` pattern); real fix needs an independent source (PHASE_72). | S (note) / L (source) |
| A04 | Historia, QB, Cobertura | med | Hard-coded numbers and years that go stale or are already wrong. QB labels: "Franquicias (32)" renders 33 rows; "MVP por año (39 recuperados)" renders 63; "Premios por temporada" 44. "97 temporadas" appears in 8 places; "Campeones 1930–2025" source card; "Bayamón 2025–26 es la primera desde Ponce 2014–15"; "Bayamón lleva la delantera desde hace décadas". | tabs.js:4210+ (`DATASETS` labels), index.html:210,227, tabs.js:1059, 1958, 3426, 4926, 6237; live eval: `FKEYS.length`=33, `MVP_YEARS.length`=63 | Compute from `YEARS.length`, `FKEYS.length`, `MVP_YEARS.length`, `LAST`. Remove or compute the Bayamón claims. | S |
| A05 | calendario, glosario | med | Stale cross-references: calendar says channels are "en Hoy bajo «Canales oficiales»" (Hoy is now Inicio, redirect only); glossary lede says "preguntar en Consulta" (view is now Preguntar). | tabs.js:1755; index.html:456; `MOVED` in applyHash | Reword and link to `#inicio` / `#archivo/preguntar`. | S |
| A06 | temporadas, líderes, QB, calidad, refuerzos | med | At 390px several tables clip columns with no scroll cue. Temporadas cuts "Nota" mid-word; Líderes cuts "Por juego"; QB table is 788px inside a 356px box. Only `#calendarBox` has the right-edge fade (`has-more-right`). | Screenshots `FULL_historia_temporadas.png`, `FULL_jugadores_lideres.png`; eval `wrap [788,356]` (QB), `[560,356]` (temporadas); main.css:1167 | Apply the existing fade/`has-more-right` pattern to all `.tblwrap`; consider moving "Por juego" into the sub-line on phone like Pos/Años. | M |
| A07 | temporadas, Récords, scoring list | med | Missing links between related things. Season-table rows contain 0 links (no jump to season, club or scoring champion). Récords: holder and year are plain text. Scoring list: club and year not linked. Líderes table has player links but the bars above do not. | Eval `linkInRow:0` (temporadas); `buildRecords`, `buildScoringTable` source | Make year → `#historia/temporada/<y>`, club → team page, holder → player page when resolvable (resolve only on exact match; unresolved stays text). | M |
| A08 | Preguntar, QB, premios, cinta, tables | med | Tap targets under 44px (project rule). 14 example chips 33–34px high; sort headers 7–42px wide (height 44); QB buttons 39–40px and Límite input 41px; "Ver los huecos" 32px high; Premios scoring-name buttons 24px high and MVP/Campeones toggle 35–36px; cinta year cells 41px wide at 1000px. | walk.json `small` arrays, all 8 browser/width/theme configs (Chromium and WebKit agree) | Raise `.chip`, `.btn`, `.cellbtn`, `.thbtn` min size; cinta cell min-width 44. Aesthetic spacing changes belong to PHASE_73 only if they alter the look. | M |
| A09 | Líderes, Ask | med | Number formatting is inconsistent: bars show "15,863", table below shows "15863"; Ask cards show "15863", "5314"; scoring/season totals use `toLocaleString('es-PR')`. | Screenshot `FULL_jugadores_lideres.png`; Ask outputs for "Georgie Torres", "Piculín" | Use the existing `num()` helper in `buildTable` render for `num` columns and in `answerCard` tables. | S |
| A10 | Preguntar | med | Answers are not deep-linkable: URL stays `#archivo/preguntar` after any query; the header search (`hubAsk`) lands on a result with no URL for it. Back does not return to the previous question. | Interaction run: hash unchanged after 8 queries | Add an optional `#archivo/preguntar/<query-slug>` segment; keep existing routes. Needs owner OK (P2-style route change). | M |
| A11 | A la medida | med | Edge states are silent. Desde > Hasta (2000 > 1990) returns "0 filas" with an empty header and no message; non-numeric years (`abc`) are ignored and the SQL echo shows no filter; the empty result has no "sin resultados" text. | Interaction run | Add a visible empty message and a note when a field is ignored or the range is reversed. | S |
| A12 | Preguntar | med | Ask title for decade queries is wrong Spanish: "CAMPEONES DE LOS 1970" for "campeones de los 70". | Interaction run, ask output | Format as "los años 70" or "la década de 1970" (owner picks). | S |
| A13 | all Archivo views | low | Every Archivo view repeats the page title plus a 4-line lede above the subnav: about 300px at 390px before the view's own heading. Section `h1` stays "El archivo" for all views. | `archivo_*_390_*.png` | Collapse the lede on subviews (landing only), keep the view `h2`. | S |
| A14 | titulos | low | Ties are ranked 4 and 5 for two clubs with 8 titles each (Santurce, Arecibo). | Screenshot `historia_titulos_chromium_390_light.png` | Show "T4" or the same rank for ties. | S |
| A15 | all subnavs | low | The pill row is clipped on both edges at 390px ("Co…", "…remios") with no fade cue; works by swipe only. | Screenshots | Add an edge fade like A06. | S |
| A16 | titulos, finales | low | Contrast flags, unverified: rank badges 1–3 computed at 1.14–1.41:1 (probably a gradient background my sweep read as the page color, so likely a false positive); one 12px "4" in finales at 4.14:1 in dark theme. | walk.json `low` | Check the two with a real computed-background probe before changing anything. | S |
| A17 | cobertura | low | `buildSources` has a no-manifest fallback branch (served from `file://`) with stale claims: "No hay boxscores. Ninguno, de ninguna temporada." and a "Hallazgo del 3 de septiembre de 2026" block saying the engine is alive. Not visible on the deployed site. | tabs.js:3343–3420 | Delete or reword the fallback; PC4/PC1 apply even offline. | S |
| A18 | cinta, calidad | low | Loading and error states unverified: `loadSeasonExtra` returns silently on a failed fetch (blank, no "no se pudo cargar"); the Calidad view's behavior when its JSON fails was not observed. | tabs.js:1850–1860; blocked-request test did not take effect | Test with the network offline; add a one-line unavailable message. | S |

Counts: **3 high, 9 med, 6 low = 18.** Verified in a real browser: A01–A15 (except the contrast subclaims in A16). Unverified: A16 contrast cases, A18 error states.

Cross-check with `docs/audits/data_review_todo.md`: A03 (Butler/Rodríguez rebounds, Dalmau assists), Mario Butler unverified career range, and the mojibake repair (the three names are repaired display-only; I saw none in the views walked) are the items visible to a user in Archivo views. Atenienses → Cariduros note sits in Equipos data, not walked.

## Proposed PHASE_68 build scope (ranked)

Do now (UI/string/derivation only, no data rewrite):

1. A01 stale "Antes de 2011" claim (S)
2. A04 derive hard-coded counts and years (S)
3. A05 stale Hoy/Consulta references (S)
4. A03 visible "las dos listas no coinciden" note on Récords and Líderes (S)
5. A06 scroll cue on all wide tables, and phone layout for Líderes (M)
6. A07 links: season, club, player from table rows, Récords, scoring list (M)
7. A08 tap targets to 44px (M)
8. A09 number formatting, A11 QB empty/invalid states, A12 "los 70" title (S each)
9. A13 shorter sub-view header, A14 tie ranks, A15 pill fade (S each)
10. A10 deep-linkable Ask queries (M, needs owner approval of the new route)

Defer to PHASE_72 (data): A02 typos, truncated and mis-cased names in season detail and scoring list; A03 real resolution of the rebounds record and Butler; Dalmau assists.

Defer to PHASE_73 (look): any visual change beyond A08/A15 minimums; archive/folder styling.

Check first, then decide: A16 contrast, A17 fallback text, A18 error states.

## New Spanish strings these fixes would need (text only, not in code)

For owner approval, to be listed in `docs/strings_pending_phase68.md` when built:

- A01: "Antes de 2011 no hay estadística completa por temporada" or a count-based sentence from the manifest (owner decides the true claim).
- A03: "Esta lista y la de Récords no coinciden en los rebotes de carrera. El archivo muestra las dos cifras hasta confirmar la fuente."
- A05: "…están enlazadas en Inicio, bajo «Canales oficiales»." and "También se pueden preguntar en Preguntar: escribe «qué es un refuerzo»."
- A06: "Desliza para ver más columnas" (optional visible hint).
- A11: "Sin resultados con estos filtros." / "«Desde» es mayor que «Hasta»: no hay años en ese rango." / "Escribe el año con números; se ignoró «{valor}»."
- A12: "Campeones de los años 70" (or "de la década de 1970").
- A14: "Empatados" / rank prefix "T4".
- A18: "No se pudo cargar el detalle de esta temporada."
