# Strings pending: PHASE_65_HISTORIA_JUGADORES

Status: APPROVED by the owner with the changes in row 10 (no "según la prensa"). Applied in the working tree, uncommitted. Counts in braces are computed from data, never typed.

| # | Where | Current | Proposed |
|---|---|---|---|
| 1 | Historia hero lede (`buildHistoriaHero`, tabs.js) | "Ocho vistas construidas con los datos reales del archivo: la cinta de 97 temporadas, títulos por franquicia, dinastías, finales cara a cara, premios, la regla de refuerzos 2024–2026 y la tabla completa de temporadas." | "Las {NSEASONS} temporadas del BSN: quién ganó, quién repitió y cómo se decidió cada final." |
| 2 | Historia `#titleStats`, tile 2 label | "con campeón identificado" | (unchanged; tile kept) |
| 3 | Historia `#titleStats`, tile 5 label | "clubes activos sin título" | (unchanged; tile kept) |
| 4 | Historia `.fixnote` (index.html) | "Celdas a 44×44px mínimo en todo ancho de pantalla — el survey encontró las celdas anteriores en 27.6×40px en ancho de teléfono, debajo del piso táctil de la app. Corregido aquí." | REMOVE (internal dev note). |
| 5 | Scoring list streak pill (`buildScoringTable`) | "🔥 {n}×" | "Racha de {n} ({a}–{b})", with a small bar glyph (SVG, hidden from screen readers). Full text in `title`: "{n} campeonatos de anotación seguidos, de {a} a {b}". |
| 6 | Scoring list footnote | "{N} temporadas documentadas, {y0}–{y1}. 🔥 marca rachas de campeonatos consecutivos del mismo jugador." | "{N} temporadas documentadas, {y0}–{y1}. «Racha» marca campeonatos de anotación consecutivos del mismo jugador." |
| 7 | MVP list streak pill (`buildMvpYears`) | "🔥 {n}×" | "Racha de {n} ({a}–{b})", same glyph. `title`: "{n} MVP seguidos, de {a} a {b}". |
| 8 | MVP list footnote | "🔥 marca MVP consecutivos del mismo jugador." | "«Racha» marca MVP consecutivos del mismo jugador." |
| 9 | Jugadores hero lede (`buildJugadoresHero`) | "El índice reúne a todos los jugadores que este archivo puede nombrar con fuente. Cada ficha dice también qué no se sabe de él." | "Todos los jugadores que este archivo puede nombrar con fuente. Cada ficha dice también qué no se sabe." |
| 10 | Récords de la liga, Jonathan García (index.html records row + player blurb; tabs.js English seed row) | "…se tiene como récord mundial extraoficial." / "33 asistencias en un juego en 2012, récord mundial extraoficial." | "…Rompió las 25 de Pablo Alicea de 1989." / "33 asistencias en un juego en 2012." Reason: no source exists. `data/clean/bsn_records.csv` has only record,holder,value,season,notes ("May 1, 2012; Caciques de Humacao vs Brujos de Guayama; broke Pablo Alicea's 25 (1989)"), no source column and no world-record claim. Not changed: Inicio's on-this-date entry (index.html, 'Jonathan García reparte 33 asistencias') and its English seed in data.js still carry the claim; flagged for the Inicio owner pass. |
| 11 | Cuadrícula share text (`shareGrid`, games.js; copied to clipboard) | "🟩" correct / "⬛" miss | "■" correct / "□" miss (plain text glyphs, not emoji). Header line unchanged. |
| 12 | Landing KPI labels, Historia | "Títulos de {club}, el club más ganador" / "Temporadas documentadas, de {y0} a {y1}" | (unchanged; third card "Franquicias distintas que han sido campeonas" removed) |
| 13 | Landing KPI labels, Jugadores | "Jugadores destacados con ficha propia en el archivo" / "En el Salón: los que definieron la liga" / "Llegaron del BSN a la NBA" | Shortened for the compact tiles: "Jugadores con ficha propia" / "En el Salón" / "Llegaron a la NBA" |

Code comments containing the emoji (tabs.js L3003, L3017, L3267) are reworded without it; not public strings.

Fixups (icons, explore spacing and grid, record-card ring, sub-nav hover): no new or changed public strings.
