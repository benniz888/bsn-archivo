# PHASE_66B roster look: revision 2 (sample only, nothing built into the site)

Open the sample: `python3 -m http.server 8124` from the repo root, then **http://localhost:8124/docs/audits/phase66b_roster_look_sample.html** (use the button for dark/light; no network requests, no web fonts: the site loads Inter and Oswald from Google Fonts and `web/` has no font files, so the sample uses the site's own fallback stack). Screenshots: `/tmp/phase66b_shots2/{chromium,webkit}_{dark,light}_{390,1000}.png`.

Owner feedback applied: the table direction is dropped (revision 1 is superseded); the roster is visual but restrained; no photos, no emoji, no gradients; the hanging retired jerseys are NOT part of this plan and stay exactly as they are in the site.

## (a) Roster as tiles
- **Grid:** 2 columns on phone, 3 in the club page's right column on desktop (the page is 6fr/6fr; 4 columns would only fit if the roster were full width).
- **Tile:** hairline border, 4px radius, card background (no tint). Top row: typographic **monogram** (initials, display face, club text accent, no circle) and a small outlined **position tag**. Then the full name, **ppg** with a 3px bar scaled to that club's highest ppg (Santurce max 23.6, Bayamón 21.8; both computed from the pool), then the **timeline strip** 1930 to 2026.
- **Timeline data, honestly:** ticks come from the season log (`ss`), which exists only for players with RealGM seasons (2012 onward). For Santurce 15 of 40 players have it, for Bayamón 19 of 36. Players without it show **era chips** (decades) instead, and a note under the grid says so. Most ticks are therefore a single mark; nothing is invented for earlier eras.
- **Selection:** a tile is a button (`aria-expanded`); the selected tile gets a 2px top rule in the club accent; the detail strip ("Años con este club" or "Décadas en el BSN", "Distinciones", "Ver ficha") opens as a full-width row under the tile's row. In the sample two copies are toggled by breakpoint; the build would insert it after the last tile of the visual row.
- **Keyboard (kept):** filters and sort as built, tiles are one roving tab stop (arrows move by row/column, Home/End, Enter/Space toggles, Esc closes and returns focus).
- **Filters:** Época and Posición are the quiet segmented controls from revision 1 (accent only on the active segment); search and the PHASE_63 combobox sort stay.
- **Accent use:** monogram text, bar fill, tick marks, selected top rule, active filter. Text accents use the contrast-guarded `--club-t` (>= 4.5:1), graphics `--club-g` (>= 3:1), both per theme, as built.

## (b) Starting five on a line-art half court
- Thin 1.25px lines in the hairline token on the card background (no green, no fill). Five **ring markers** (outlined, club accent): the number inside is the position (1 armador, 2 escolta, 3 alero, 4 delantero, 5 centro), a basketball convention applied to the existing position labels. **Unconfirmed players** get a dashed neutral ring with no number and the existing red **"sin confirmar"**.
- Beside each marker, centered under it: full "Nombre Apellido" (wraps to two lines, never truncated), position in small caps, ppg underneath. Text has a knockout stroke so court lines never cross letters.
- Zones follow the existing rule (first player of each position takes its zone; repeats and unconfirmed fill the free zones), so Bayamón 2013 shows two delanteros and two escoltas honestly (rings 4 and 2 in leftover zones).
- **Accessibility:** the SVG has an `aria-label` and a visually hidden list repeats name, position and ppg for each player (new, the old court had none).
- The explanatory text and the "41 juegos... 3 de 5 con identidad y posición confirmada" note stay; one sentence is added explaining the ring numbers.

## Strings that would change (to `docs/strings_pending_phase66.md` at build)
- New: "Las marcas del eje son temporadas con estadísticas por club en el archivo ({n} de {m} jugadores las tienen); sin ellas se muestran las décadas."; "El número dentro del círculo es la posición (1 armador, 2 escolta, 3 alero, 4 delantero, 5 centro); el círculo punteado es un jugador sin posición confirmada."; the SVG label and the hidden list's wording ("{nombre}, {posición}, {n} puntos por juego").
- Everything else is existing text.

## Build and test plan (after approval)
1. `showTeam` roster closure: replace row markup with tiles (state, filters, sort, paging and roving focus kept; column-aware arrow keys; detail row placement by measured row).
2. `sfCourtSvg` and `renderStartingFive`: line-art court, rings, hidden list (names via the existing flip; `sfAssignZones` kept).
3. CSS: remove the pill/row rules (`eq-row`, `eq-fb` pill look) and the green `sf-court` background; add tile and court rules; retired-jersey CSS untouched.
4. Verify in Chromium and WebKit, 390 and 1000px, dark and light: 0 console errors, taps >= 44px, contrast, keyboard walk, hero-overlap probe, no horizontal scroll, reduced motion; update `tests/test_equipos_phase66.py` (starting-five asserts), run the suite (baseline 736 passed, 1 xfailed, 1 known failure).
5. No new top-level names; no emoji; no gradients; no new fonts.

## Open questions
1. 3 columns in the right column (as shown) or give the roster the full width with 4 columns and move the starting five above it?
2. Ring numbers 1 to 5 on the court: keep, or leave the rings empty?
3. Keep the tile timeline even though most players show one tick, or show era chips for everyone and drop the strip?
