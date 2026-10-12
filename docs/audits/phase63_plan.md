# PHASE_63_TABLES — plan (no code written)

Status: PLAN ONLY, awaiting owner approval. Branch `redesign-v3`. No commit, no push.

## 1. Inventory

Everything routes through ONE builder, `buildTable(host, cols, rows, opts)` (`web/js/tabs.js:1196`),
plus 5 hand-built `<table>`s. Row counts marked (~) are from the screenshots / code caps; the rest
are measured in batch 0 (a read-only script) before any change, not guessed.

### A. Via buildTable (inherit the new component automatically)
| # | Table | Built at | Columns | Rows |
|---|-------|----------|---------|------|
| 1 | Temporadas (`#seasonTable`) | tabs.js:1961 | Año, Campeón(btn), Subcampeón, Nota | 97 |
| 2 | Jugadores índice (`#playerIndex`) | player.js:207 | Jugador(btn), Pos, Años, Clubes, Pts, Reb, Ast, PJ, Fuentes | 376 |
| 3 | Jugadores "todo el archivo" | player.js:233 | Jugador(btn), Pos, Años, Temp. | capped 500 of 3,303 |
| 4 | Líderes (`#leadTable`) | tabs.js:2850 | #, Jugador, Pos, Años, Total, PJ, Por juego | per category |
| 5 | Premios (`#awTable`) | tabs.js:3253 | Año, Premio, Jugador, Club, Línea | measure |
| 6 | Final por año (`#finTbl`) | tabs.js:3295 | Juego, Fecha, Local, Visita, Marcador, Margen, Ganó, Serie, Parciales | per year |
| 7 | Final Brava 2026 + Semis 2026 | tabs.js:1382, 1391 | 8 cols / 5 cols | small |
| 8 | Calendario (`#calendarBox`) | tabs.js:1651 | Año, Temp., Inicio, Fin reg., Playoffs, J, Equipos, Formato | ~97 |
| 9 | Careo en finales (equipo) | tabs.js:2100 | Rival, Ganadas, Perdidas, Total | small |
| 10 | Refuerzos 2025 (`#refScorers`) | tabs.js:3058 | #, Jugador, Club, Estatus, Puntos, PPJ | small |
| 11 | Calidad de datos x4 (`#dqTable`, `#dqDob`, `#dqDisputed`) | data-quality.js:149/155/180 | 4–5 cols each | measure |
| 12 | Consulta / Ask result tables (`o.table`, ~12 variants) | tabs.js:3398 | 2–5 cols | small |
| 13 | Query builder (`#qbResult`) | tabs.js:4173 | dynamic per dataset | up to full dataset |

### B. Hand-built (not buildTable)
| Table | Built at | Plan |
|-------|----------|------|
| Standings 2026 A/B | tabs.js:1448 | Batch 5: apply the shared CSS classes only (small, no sort/CSV today; keep that). |
| Season-compare mini tables | tabs.js:1842, 2768, 2827 | CSS classes only; no JS change. |
| Matrix Campeón\Subcampeón | tabs.js:1923 | OUT OF SCOPE (heatmap grid, not a data table). |

## 2. Shared component design

Evolve `buildTable` in place (all 13 callers keep their signature). New behavior is opt-in per column
via new optional col keys, so unmigrated callers render as today except for the global polish.

- **Structure/CSS:** `.tblwrap` keeps sticky header (always, not only `>24` rows) and sticky first col.
  Scroll fade generalized from `#calendarBox` to every `.tblwrap` (`has-more-right` + `has-more-left`);
  `tabIndex=0` only while `scrollWidth>clientWidth` (ResizeObserver, same reasoning as PHASE_52A);
  focus ring via existing `--focus`.
- **Type:** `td.num` right-aligned + `font-variant-numeric:tabular-nums`; `c.muted` columns use `--ink-3`
  (checked >= 4.5:1 on `--deep` and zebra, both themes, before use). Row separators softened, a bit
  more row height (44px tap targets where a control sits in the row).
- **Emphasis:** new col option `kind:'club'` (champion): crest (`crest()`) + short name, plain text weight 600,
  no `.btn` chip; the whole cell is still one real `<button>` (keyboard/click -> `showTeam`) styled flat.
  `kind:'club2'` runner-up: same without crest, muted. Player-name columns: flat link-button, no box.
- **Empty values:** `dash()` replaced in the default cell path by `<span class="nodata" title="Sin dato" tabindex=-1>`
  with a visually-hidden "sin dato" for screen readers (title alone is not announced reliably). CSV output unchanged
  (still empty, never "sin dato", never 0 — PC2).
- **Long lists:** `opts.pageSize` (default 25 when `rows>25`): "Mostrando 25 de N" + "Mostrar más" button
  (adds 25; focus stays on the first new row; `aria-live=polite` count). Sorting/CSV/"Copiar" operate on ALL rows,
  not only the visible page. `opts.groupBy` (Temporadas, Calendario, Premios): decade divider rows
  (`<tr class="grp"><th colspan scope=rowgroup>`), only when sorted by the group key.
- **Notes:** col option `clamp:true`: one line + ellipsis in the cell, full text in the DOM (not truncated by JS),
  an "Ver nota"/"Ocultar" `<button aria-expanded>` shown only when the text really overflows (measured). Screen
  readers/keyboard get the whole text.
- **Sorting:** header `<th aria-sort>` (set today? verify in batch 0; add if absent), sort via a real `<button>` inside `th`
  so it is keyboard operable. Arrow glyphs become CSS, not text.
- **Kept:** CSV download, **"Copiar como tabla"** (not found in current `buildTable`; batch 0 greps for it. If it does
  not exist today I will list it as a NEW feature for your approval rather than invent "existing behavior").
- **Filters:** one custom combobox pattern (ARIA 1.2 select-only combobox: `role=combobox`, `aria-expanded`,
  `aria-controls`, listbox, Up/Down/Home/End/Enter/Esc/typeahead, 44px, visible `<label>`), enhancing the existing
  native `<select>` (native stays as the source of truth, hidden from AT, so all `onchange` handlers and tests keep
  working; falls back to native if JS fails). Search input gets a clear (x) button (44px target, `aria-label`).
  Applied to: `#sclub`, `#pmode`, `#pf`, `#lcat`, `#lmode`, `#awYear`, `#finYear`, `#dqS`, `#qbds`, `#qbclub`.
  Not touched: profile/preferences selects (not table filters).

## 3. Phone (390px) column decisions
Sticky first col always. Hide-on-phone = column moves to the row's expandable detail; it stays in CSV.

| Table | Visible at 390 | Moved/hidden |
|-------|----------------|--------------|
| Temporadas | Año, Campeón | Subcampeón (muted 2nd line under Campeón), Nota (clamped, expand) |
| Jugadores | Jugador, Pts, PJ | Pos (small, under name), Años, Clubes, Reb, Ast, Fuentes (scroll) |
| Archivo completo | Jugador, Años | Pos, Temp. |
| Líderes | #, Jugador, Total | PJ, Por juego (scroll), Pos/Años under name |
| Premios | Año, Premio, Jugador | Club, Línea (scroll) |
| Final por año | Juego, Marcador, Ganó | Fecha, Local/Visita, Margen, Serie, Parciales (scroll) |
| Calendario | Año, Temp., J | Inicio, Fin reg., Playoffs, Equipos, Formato (scroll; Formato clamped) |
| Careo / Refuerzos / DQ / Consulta / QB | all columns (<=5), horizontal scroll only if needed | QB: dynamic, no hiding (columns unknown ahead) |

Mechanism: col option `phone:'keep'|'sub'|'scroll'`. To avoid duplicated data in the DOM, "sub" columns render as a
muted second line in the first-col cell via CSS-only grid at <=600px where possible; otherwise plain horizontal scroll
(the existing, proven behavior). I will not hide data with no way to reach it.

## 4. Risks
1. **Function-inventory baseline (the blocker-ish one).** Frozen baseline `tests/harness/inventory_main_HEAD.json`; new
   top-level declarations fail tests (precedent: PHASE_52A/PHASE_62 "zero new declarations"). Plan: ALL new logic as
   closures inside `buildTable` and one enhancer called from an existing init path; zero new top-level names, no new
   globals. `TBL_SEQ`-style globals not added. If a combobox genuinely cannot live without a top-level function, I
   stop and ask before touching the baseline JSON.
2. **Text-extraction tests** (`tests/_web_text.py`, `test_web_text.py`, polish/targets tests) read CSS/JS as text: new
   selectors may trip the duplicate-selector sweep and "bare top-level selector" checks. Run full suite each batch;
   baseline 704 passed / 1 xfailed / 1 known fail. Any NEW failure = revert that batch's change, not edit the test.
3. **Public Spanish strings** (all go to `docs/strings_pending_phase63.md`, none shipped unapproved in final form):
   "Sin dato", "Mostrando 25 de N", "Mostrar más", "Ver nota"/"Ocultar nota", "Limpiar búsqueda", "Copiar como tabla" (if new),
   combobox labels. During build they appear as placeholders listed in that file.
4. **Shared `.tblwrap`:** 13 callers + CSS used by hand-built tables; the `#calendarBox`-scoped rules must be un-scoped
   without regressing Calendario (visual diff before/after).
5. **Behavior preserved:** filter handlers that re-call `buildTable` (`DQ_T.state` reuse, `drawDQTable` sort carry-over)
   — return value `{render,state}` keeps its shape; paging resets on filter change.
6. **PC1/PC2:** "sin dato" is presentation only; no value is invented or coerced to 0; no crest images beyond the
   existing drawn `crest()` SVG (L3).
7. Query builder / Consulta: dynamic columns have no `kind`/`phone` hints, so they get only the generic polish.
8. Chromium+WebKit at 390/1000px, one phone + one desktop screenshot per page per batch, in `/private/tmp/bsn_harness`
   (never jsdom alone, per memory). Installs: none planned; nothing deleted outside /tmp.

## 5. Batches (each = one turn, no commit; report in standard format; owner approves before next)
- **B0 (read-only):** measure row counts, confirm aria-sort / "Copiar como tabla" status, contrast of muted/`nodata` tokens,
  capture "before" screenshots. Writes docs only.
- **B1 Core component:** sticky header/first col, generalized scroll fade + conditional tabIndex, numbers/tabular/muted,
  `nodata` mark, softer rows. Check all 13 callers visually.
- **B2 Long lists + groups:** pageSize/"Mostrando 25 de N"/load-more, decade groups (Temporadas, Calendario, Premios).
- **B3 Emphasis + notes:** champion crest+name, runner-up muted, flat player links, clamped notes with expand.
- **B4 Filters:** combobox + search clear on the 10 selects; keyboard tests.
- **B5 Phone priorities + hand-built tables** (standings, season-compare): per section 3.
- **B6 Sweep:** a11y (contrast/tap/focus/reduced-motion), full suite, strings file, final screenshots.

## 6. Decisions I need from you
1. OK to keep zero new top-level declarations (closures only), and stop-and-ask if that proves impossible?
2. "Copiar como tabla": does it exist elsewhere that I missed? If not, approve it as new, or drop?
3. Phone "sub-line" approach (Subcampeón under Campeón) vs. plain horizontal scroll only?
4. Page size 25 also for the 376-row Jugadores index and the 500-cap archive list (default yes)?
