# Page specs (from the screenshots in `newredesign/`)

Applies to desktop AND phone. Every new Spanish string goes to `docs/strings_pending_<phase>.md` for owner approval. Never fabricate data; computed values come from the data files.

## Design direction: "El Archivo" feel, different per page
Shared language (tokens, folder component, type scale, motion rules) so it feels like one product, but each page has its own layout and signature:

| Page | Metaphor | Signature |
|---|---|---|
| Inicio | The desk / front counter | Folder cards that lift on hover, club-aware ordering, one hero, few blocks |
| Historia | The timeline drawer | Decade folder tabs along the top, timeline as the spine |
| Jugadores | Personnel files | Dossier cards, paper-clip/stamp details, "sin fuente" stamps |
| Equipos | The club cabinet | Each club page themed from its own colors and crest, retired jerseys hung in the rafters |
| Juega | The game room | Each game has its own look: board, reels, case file, ladder |
| Archivo | The filing cabinet itself | Drawer rows, index cards, labels |

Shared folder component (build once in PHASE_61/63): folder tab + body, hover lift (transform only), open/close expand, optional crest/color accent. Motion: transform and opacity only, 150-300ms, ease-out, off under `prefers-reduced-motion`. No emoji anywhere in the UI (the owner reads them as "made by AI"): replace with SVG icons or text; add a test that fails if emoji codepoints appear in `web/`.

## Shared data table (PHASE_63; reference screenshots: Historia/data organization.png, Jugadores/Data table.png, Cangrejeros/Final Brava tables)
Problems seen: dense single-weight rows, bare divider lines, ghost chips around champion names, a glossy native `<select>`, dashes everywhere, long "Nota" text that stretches rows, nothing tells you what is important.
Spec:
- One `buildTable()`-compatible shared component; all tables (Historia, Jugadores, Archivo, club pages, final series) use it.
- Sticky header + sticky first column on phones with a scroll fade (reuse the Calendario pattern); keyboard-focusable only when it actually scrolls.
- Numbers right-aligned, tabular figures; years in the type scale's display font; muted secondary columns.
- Highlight what matters: champion crest + short name (not a boxed chip), runner-up muted, empty values as a quiet "sin dato" mark with tooltip, never a bare dash that looks like a bug.
- Decade group rows (collapsible) for long lists; "97 filas" becomes "Mostrando 25 de 97" with a load-more (also a performance win).
- Notes: one line with ellipsis + expand control (follow the A la medida rule; no full row stretching), full text available on tap/Enter and to screen readers.
- Filters: custom-styled select/combobox with keyboard support, visible label, 44px height. Search field with clear button.
- Row hover/focus state; zebra only if contrast stays >= 4.5:1.
- CSV/"Copiar como tabla" buttons keep working. Sortable headers stay (aria-sort).
- Phone: priority columns (year, champion, runner-up) visible; others behind the horizontal scroll or a "mas" disclosure. Decide per table, list the choice.

## Inicio (PHASE_64; references: Inicio/computer view 1-9, Statmuse top of screen, phone view tabs)
- Header per Statmuse: logo top-left, search field center (full width on desktop; collapses to an icon that expands on phone), "Iniciar sesion" top-right (placeholder until PHASE_70; hidden if accounts are not approved). Move `#hubSearch` here.
- Remove the Inicio item that references Piculin's death (the owner's "prueba" item). Find it with a case-insensitive search for "Piculín"/"Piculin" in `web/js/` and `web/index.html` and the Inicio screenshots. Remove only that Inicio content; his player page and roster entries stay. List exactly what was removed.
- Selected/active outline: site blue, not orange (see 02).
- Declutter: fewer blocks (the Sep 19 audit counted 13+ heterogeneous blocks). Target: one hero ("tu club"), one row of four entry cards (Jugadores, Comparar, Juega, Archivo), and at most two content blocks below. Everything else lives one click away. Write the keep/cut list to the review before building; owner approves it.
- The champion "cinta" in the hero card renders as a few lonely bars in a very wide card (see computer view 1: bars only span ~30% of the card). Make the tape span the whole card width with a year axis and clearly labeled decades, or shorten the card. Dynasties as solid runs, gaps as gaps.
- Personalization rules (no backend): favorite club chosen in the pill reorders blocks and picks the hero; recently viewed players/clubs from localStorage appear as "Sigue donde lo dejaste". Accounts later sync the same preferences.
- Phone: bottom tabs fixed (see 02 for the indicator bug).

## Historia (PHASE_65)
- Fewer KPI tiles. Keep the ones that answer a question; drop decoration. Show 3-4 numbers max above the fold.
- Streaks: text and icon, no emoji. Example pattern: "Racha de 3 titulos (1998-2001)" with a small SVG bar glyph.
- Tables via the shared component.
- Phone landing: review `Historia Phone landing page.png`; fix anything cut off.

## Jugadores (PHASE_65; reference Player page view.png)
- Bug: decorative circles in the stat tiles sit on top of the labels ("rebotes", "asistencias", "juegos", "puntos por juego", "MVP"). Put the decoration behind the text (z-index below, lower opacity) or move it to the tile corner and clip it. Add a visual test at 390 and 1000px.
- Missing stat (rebotes shows a dash): the "sin dato" treatment from the table spec. Keep the orange "Lo que este archivo no sabe" note; it is a strength, keep it, but do not use orange for outlines (see 02).
- Honors chips: group and order (individual awards, records, status). Fix wrapping.
- Table via the shared component. Phone landing per `Jugadores landing page phone view.png`.

## Equipos (PHASE_66; references: Equipos landing page phone view.png, Cangrejeros team view.png)
Problems seen: the phone landing is three stacked giant stat cards and the title is cut by the sticky header; the club page puts everything in a narrow left column leaving the right half of a desktop screen empty; players are a cloud of identical chips.
- Landing: club crest grid first (12 active + 21 defunct), stats become a compact strip. Phone: 2-column crest grid, subnav pills scroll with edge fade and active pill in view.
- Club pages, one per club, each themed from its own colors (the data has "Colores aproximados": keep that honesty note): own accent, hero treatment, "signature stat" computed from data (e.g., longest title drought, best decade, rival record). Club lore lines come from the existing `TEAM_LORE` and from sourced research only; every lore string is listed with its source and approved by the owner. If a club has no verified lore, show none. Never invent.
- Use the desktop width: two-column layout (identity + stats left, roster/timeline right).
- Roster: replace the chip cloud with an interactive roster: filter by era and position, hover/focus card with the player's years and honors, link to his page; virtualize or paginate (some clubs have 40+ names).
- **Camisetas retiradas**: hanging jerseys. Build a generic jersey SVG (not any real kit design) recolored with the club's colors via CSS variables, number on the back, name and year retired on a small tag, hung from a rail with hangers and a soft shadow; slight sway on hover/focus (transform only, off with reduced motion). Fall back to a clean list for screen readers. Colors are "aproximados".
- Final-series blocks (e.g., Final Brava 2026) use the shared table; the green/red game tiles need a non-color cue (W/L letter) for accessibility.

## Juega (PHASE_67A-D; references: Juega/*.png)
Landing: review `Juega landing page phone view.png` and fix cut-off. Each game gets its own look.

### La Cuadricula (62: logic first; 67A: visuals)
- Bug: correct answers rejected. Do NOT guess the cause. Diagnose with an exhaustive test: for every cell (row criterion x column criterion) enumerate every player who truly satisfies both, from the data, and assert the game accepts each one under every accepted spelling (accents, nicknames in quotes like «Piculin», "Jr.", initials, duplicate-candidate players noted in the backlog, e.g., Alamo/Candido Fret, Reyes/Hector). Log which criterion function rejects. Likely areas to inspect: name normalization, alias handling, position labels (e.g., "Poste" vs C/PF), decade logic ("Jugo en los 2000" boundary years), and partial-data players.
- Add a visible, honest reason when a guess is rejected ("No jugo en los 2000 segun el archivo"), plus a "reportar" link for disputed answers to the corrections contact.
- Visuals: board uses the width on desktop (the board currently occupies the left half); club crests; cell reveal animation (flip), correct/incorrect with color AND icon; attempt pips.

### La Temporada Perfecta (67B: logic + visuals)
- Hardening: make 34-0 genuinely rare. Compute, from the data, the maximum achievable score and the score distribution over all possible spins and placements (Monte Carlo, seeded, results written to `docs/specs/temporada_balance.md`). Choose the score-to-record curve so that 34-0 is reachable only with near-optimal choices (target: under about 1 in 1,000 for good-but-not-perfect play; state the measured numbers). Cap bonuses, diminishing returns, penalties for duplicates or out-of-position picks. Do not change the displayed honesty note about missing data.
- Visuals: team and decade as two slot-machine style reels that spin and decelerate (transform animation, a few hundred ms to ~1.5s, skippable, instant under reduced motion), a court layout for the five positions, pass/refuerzo counters as tokens, result as a scoreboard with the record counting up.

### ¿Quien soy? (67C: logic + visuals)
Problems seen: clues like "Su estatus no esta registrado" (a non-clue), position and averages before anything identifying, you must reveal everything to get a hint.
- Choose players with enough verified facts (minimum number of non-null facts) and enough recognizability (career points, honors, years). Never use a null fact as a clue.
- Clue ladder from broad to specific, 6-8 clues, ordered by how much each narrows the field: era -> position -> first letter of club city?/club -> an award or record -> a stat line -> a distinctive career fact (native, NBA, honors) -> last: initials or name length. Score: fewer clues = more points.
- Autocomplete restricted to players in the archive; accept accents/nicknames.
- Visuals: "case file" card with clues dealt as paper strips, a blurred silhouette that sharpens as clues are revealed (silhouette is generic, not a real photo).

### Sube y Baja (67D)
Owner likes it. Visual restyle only. No logic or content change.

## Archivo (PHASE_68; reference Archivo landing page phone view.png)
- Visual pass in the filing cabinet metaphor; shared tables; fix the cut-off phone landing.
- Backlog items to fold in: Archivo subnav pills 37px (needs 44px), footer links 15px, Calidad contrast items.
