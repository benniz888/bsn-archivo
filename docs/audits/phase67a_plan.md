# PHASE_67A_JUEGA_CUADRICULA: plan (Step 1, plan only; nothing built)

Scope: La Cuadrícula visuals only (`web/js/games.js` ~L232-410, `web/css/main.css` L1558-1650, `web/index.html` only if needed). No game logic, answer data, or other games touched. Existing tests to keep green: `tests/test_juega_grid_layout.py` (pins `gHead`, `.ghead`, `.ghead .glabel`, crest-plate centering), `tests/test_no_emoji_in_web.py`.

## 1. Current problems (with references)

| # | Where | Problem |
|---|---|---|
| P1 | main.css L1603 | Selected cell uses `--rojo` border + inset shadow. Red/orange-family outline; the new site style is blue (`--focus` = `--azul-hi`). |
| P2 | main.css L1602 | Hover is `--azul` (1663D8) while selected is red: two accent colors for one interaction. |
| P3 | main.css L1604-1605 | `.ok` / `.bad` states are carried by background tint + border colour only (green vs red). No non-colour cue (icon/text), so colour-blind users cannot tell a miss from a hit once the name is long. Also `.bad` cells are never rendered by `drawBoard` (wrong guesses are not stored in `GB.ans`, only in `GB.history`), so `.gcell.bad` is dead CSS. |
| P4 | main.css L1599-1608 | `.gcell` has `aspect-ratio:1` with `--fs-3xs` (11px) text. At 390px a cell is ~70px wide; a long name ("Jose «Piculín» Ortiz") plus a share line clips or overflows. No wrap/clamp rule on `.pn`. |
| P5 | main.css L1599 | Empty cell shows a bare "+" with no visible focus style of its own; relies on the global `button:focus-visible` (L775). Selected cell + focused cell look different only by colour. |
| P6 | games.js L253-272, main.css L1581-1587 | Headers: crest (32px) + 2-line-clamped label at 11px. Works, but the label only fits via `title` tooltip when clamped (hover only, no touch). Non-club axes (position, category) have no icon and look identical to club headers minus the crest, so the grid has no visual row-vs-column cue. |
| P7 | games.js L283-286, main.css L1637-1650 | Pick UI is a bare `<input>` + a custom `.sugg` dropdown (`border:1px solid var(--azul)`, 9px padding, no 44px rows, no `role=listbox`). It does not match PHASE_63's `.cbx-list` / `.cbx-opt` look (raise bg, shadow, 44px rows, blue left bar on selected, `--focus` ring on active). Active row is `.on` background only. |
| P8 | games.js L300-308 | Result block: plain `.scoreline` spans; "PERFECTA" is green text only; "Copiar resultado" gives a status message but the share text itself is never shown, so the user cannot see what ■/□ they are copying. Copy failure (no clipboard API) is silent. |
| P9 | games.js L282, L405-410 | Share text already uses ■/□ (PHASE_65), so no change to the format; it only needs to be visible and legible in both themes. |
| P10 | games.js L260-290 | Accessibility: cells have no accessible name that includes row and column. Screen reader hears "+" or just the player name. Pips have an `aria-label` on a plain `<div>` (no role). Header `title` is not announced reliably. |
| P11 | games.js L286 | `#gSugg` list buttons are not reachable semantically as options; `aria-activedescendant` / `aria-expanded` missing. Disabled "ya usado" rows use inline `opacity:.4`, which drops below 4.5:1 contrast. |

## 2. Proposed changes

### CSS (main.css, Cuadrícula block only; existing selectors edited in place, no new top-level JS names)
1. Cell states, all blue, no red outlines:
   - base: `--deep` bg, `--line` border.
   - hover: `border-color:var(--azul-hi)`.
   - selected (`aria-pressed=true`): `border-color:var(--focus); box-shadow:0 0 0 2px var(--focus) inset; background:var(--tint-azul)`.
   - `:focus-visible`: `outline:2px solid var(--focus); outline-offset:2px` (distinct from selected, which is inset).
   - `.ok`: keep `--tint-ok` + `--ok-line`; add a corner check drawn in CSS (a `::after` rotated-border tick, not an emoji) so correctness is not colour-only.
   - `.bad`: remove dead rule (or keep restyled as a neutral state if section 4 option B is chosen).
2. Cell text: `.pn` gets `overflow-wrap:anywhere` + a 3-line clamp, `.pr` stays; at <=639px the cell drops `aspect-ratio:1` to `min-height:72px` (min 44px tap is already satisfied) so names fit without clipping.
3. Headers: add a `.ghead.col` / `.ghead.row` distinction via `border-bottom`/`border-right` accent in `--azul` (row headers get a left accent). Label keeps the 2-line clamp; at 390px bump nothing in font size (11px is the site's floor) but un-clamp to 3 lines when the label is a non-club axis (no crest takes space).
4. Pick UI: restyle `.sugg` to reuse the PHASE_63 tokens exactly: `background:var(--raise); border:1px solid var(--line); box-shadow:0 8px 24px var(--shadow); padding:4px`; rows `min-height:44px`, `.on` = `--deep` bg + `2px solid var(--focus)` inset outline, used rows `color:var(--ink-3)` (no opacity). Input gets `min-height:44px`. I reuse `.cbx-list` / `.cbx-opt` class names directly if the markup can carry them (preferred: zero duplicated CSS); otherwise `.sugg` mirrors them.
5. Result block: `.scoreline` becomes a small card (`--raise`, `--line`); a `<pre class="sharebox">` shows the exact ■/□ text (`font-family:monospace`, `--ink` on `--deep`, both themes via tokens). "PERFECTA" gets a text label plus a tick-free pill so it is not colour-only.
6. `prefers-reduced-motion`: no new animation is introduced; the one transition I would add (border colour 120ms) goes inside `@media (prefers-reduced-motion:no-preference)`.

### Markup (games.js `drawBoard`, template strings only)
- Cell: `aria-label="Fila: {axFull(row)}, columna: {axFull(col)}. {estado}"` where estado = `vacía` / `acertada: {name}, {share}%` / `seleccionada`. Keep `aria-pressed`. (Assumes the grid stays a flat div grid of buttons; I will add `role="group"` + `aria-label="Cuadrícula 3 por 3"` on `.gridtable`.)
- Headers: replace `title` reliance with visible text only; `title` stays (test-pinned) and also gets `aria-hidden` on the crest span (decorative, label follows).
- Pick UI: `role="combobox"` on `#gGuess` with `aria-expanded`, `aria-controls="gSugg"`, `aria-autocomplete="list"`, `aria-activedescendant`; `#gSugg` gets `role="listbox"`, rows `role="option"` + ids + `aria-selected`; used rows `aria-disabled="true"`. Existing keyboard handling (ArrowUp/Down/Enter) is unchanged; I only add `aria-activedescendant` updates in `paintSugg`. Escape closes the list (small addition, UI only).
- Pips: add `role="img"`, keep label, extend with counts ("3 de 9 usados").
- Result: render share text in `.sharebox`; if clipboard API is missing or rejects, show message "No se pudo copiar. Selecciona el texto de arriba." instead of silence.

## 3. Strings (will be written to `docs/strings_pending_phase67a.md`; NOT placed in UI until approved)
New/changed, all Spanish, no emoji:
1. Cell labels: `Fila: …, columna: …. Vacía.` / `… Acertada: {nombre}, {n}%.` / `… Seleccionada.`
2. Group label: `Cuadrícula de 3 por 3`
3. Pips label: `Intentos usados: {n} de 9`
4. Share box label (visible heading): `Tu resultado`
5. Copy failure: `No se pudo copiar. Selecciona el texto y cópialo a mano.`
6. Combobox accessible name (replaces `Escribe un nombre`): `Nombre del jugador para la casilla seleccionada`
7. Used-option suffix stays `ya usado` (unchanged).
Existing strings (Copiar resultado, Ver respuestas, Otra en práctica, Aciertos, Rareza, PERFECTA, all gMsg texts) are untouched.

## 4. Decisions needed from owner
A. Wrong guesses: today a miss only appears as a spent pip, never in the cell, so `.gcell.bad` is dead. Default: leave logic alone, delete the dead `.bad` rule. Option B (needs logic touch, out of this phase's rules): show last miss in the cell.
B. Reuse `.cbx-list/.cbx-opt` classes directly (default, no new CSS) vs mirror them in `.sugg`.
C. Visible share box (default yes) vs copy-only.

## 5. Risks
- `tests/test_juega_grid_layout.py` reads `gHead` and `.ghead` source by string index; edits must keep those anchors verbatim. I will run it first after each edit.
- Dropping `aspect-ratio:1` on mobile changes board height; verify no overflow at 390px and 320px, in Chromium AND WebKit (`-webkit-line-clamp` plus `overflow-wrap:anywhere` renders differently).
- `.ok` tick via `::after` must reach 3:1 against `--tint-ok` in both themes (light `--ok` is #0A7A42; will measure).
- `aria-label` on a button overrides its inner text for AT; label must therefore contain the player name (it does).
- `.sugg` is `position:absolute` inside `.guessbar` with `flex-wrap`; restyling rows to 44px increases height to ~8 x 44 = 352px; keep `max-height:220px` scroll, check it is not clipped by the viewport on phone (may need the `.cbx.up` flip logic, otherwise cap at 40vh).
- Flaky `test_player_ring_overlap::test_no_console_errors` is expected in full runs only; known failure in `tests/test_web_text.py` unchanged.
- Process note: I read the head of `docs/global.md`, the CLAUDE.md rules, and the PHASE_66 plan for format; I did not re-read all 9,124 lines of `docs/session.md`.
