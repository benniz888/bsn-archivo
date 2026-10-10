# PHASE_66 Spanish strings as built (owner reviews the batch)

`{n}` values are computed from F / champOf, never typed. No "según la prensa"-style attributions.

## A. Claim rewordings (owner approved Oct 10, exact before/after)
| # | Where | Before | After |
|---|---|---|---|
| A1 | club tag (tabs.js, showTeam) | Colores verificados | Colores de Wikipedia |
| A2 | TEAM_LORE.man | El único club activo sin título — el más joven de la liga, y el que todavía se lo debe a su fanaticada. | El único club activo sin título — el más joven de la liga. (checked: F.founded of Manatí is the latest of the 12 active clubs; no other active club has an empty `won`) |
| A3 | TOWN_LORE.san | Santurce no es un municipio — es un barrio de San Juan, el único pueblo de Puerto Rico fundado por negros libres. Se llamó Cangrejos antes que Santurce; de ahí «Cangrejeros». | Santurce no es un municipio — es un barrio de San Juan. Se llamó Cangrejos antes que Santurce; de ahí «Cangrejeros». |

A3 source, confirmed Oct 10 on es.wikipedia.org/wiki/Santurce_(San_Juan): "Santurce es un barrio/distrito del municipio de San Juan, Puerto Rico."; "el barrio era conocido como Cangrejos."; "el uso de facto del nombre Cangrejos y el gentilicio cangrejeros." The "negros libres" clause was not checked and is removed.

## B. Landing
| # | Where | Text |
|---|---|---|
| B1 | strip | {n} activos · {n} desaparecidos · {n} campeonatos{ — falta el de 1953, existing logic} |
| B2 | crest grid headings | Activos / Desaparecidos |
(Tile names, "{n}×" title counts and the Desaparecidas city/years line are the existing tile()/tileGone() strings.)

## C. Club page
| # | Where | Text |
|---|---|---|
| C1 | signature, 3+ titles in a row | Racha más larga: {n} títulos seguidos, {a}–{b} |
| C2 | signature, one best decade (>= 2 titles) | Mejor década: los {decada}, con {n} títulos |
| C3 | signature, longest gap >= 5 seasons (not shown if the gap spans a year with no recorded champion) | Sequía más larga: {n} años sin título, entre {a} y {b} (changed from the plan's draft so the years are the two titles) |
| C4 | signature, finals but no title | {n} final perdida / finales perdidas, aún sin título (existing wording) |
| C5 | signature, defunct, no title | Activo {a}–{b} (plan said "Activo {a}–{b} ({n} temporadas)"; the season count is dropped, hiatuses are not modeled) |
| C6 | signature, exactly one title (new) | Único título: {año} |
| C7 | timeline | heading "Finales"; legend "G = campeón · P = subcampeón"; screen-reader suffix ": campeón" / ": subcampeón" |
| C8 | roster | heading "Jugadores en el archivo con este club"; filters "Época", "Posición", "Buscar jugador", "Ordenar por"; sorts "Nombre", "Puntos por juego", "Temporadas", "Más reciente"; groups "Todas", "Armadores", "Aleros", "Pivots", "Sin posición" |
| C9 | roster count / empty | {m} de {n} jugadores ("jugador" when n = 1) / Ningún jugador coincide con estos filtros. |
| C10 | roster | Mostrar más |
| C11 | detail strip | "Años con este club" (only where a season log exists) or "Décadas en el BSN"; "Distinciones" (existing tag words: MVP, Campeón de anotación, Campeón, Refuerzo, Nativo, NBA, 10.000+ puntos, Leyenda, Figura del BSN); "sin dato"; button "Ver ficha". Position labels use the existing posEs(). |
| C12 | observed, NOT changed | "Mayor rival: … — 1 finales (0-1)" is an existing string with a plural slip. Proposed: "1 final (0-1)". Awaiting your OK. |

## D. Camisetas retiradas
| # | Where | Text |
|---|---|---|
| D1 | block heading (club page) | Camisetas retiradas |
| D2 | list label (visible text) | Números retirados, según el archivo: 4, 5, 9, 15, 16, 17, 54. |
| D3 | count line (existing, unchanged) | 8 números retirados — el 17 se retiró dos veces. |
| D4 | no-names note (existing, unchanged) | La liga los publica como dígitos, sin nombres — y el archivo no los adivina. |
| D5 | under the rail (new) | Dibujo ilustrativo, no es el uniforme del club. Colores aproximados. |
No name or year appears on any tag (owner: number-only this phase).

## E. Fixups (Oct 10)
| # | Where | Text |
|---|---|---|
| E1 | accessible name of each retired jersey (replaces the visible number caption, which is removed) | Camiseta con el número {n} |
| E2 | starting five court | no new text; names now read "Nombre Apellido", wrap to two lines, no "…"; "sin confirmar" unchanged |
