# PHASE_71 Spanish strings as built

Build step 2. Nothing committed. Every string below is in `web/` now.

## A. Approved in the PHASE_71 STEP 2 message
| # | Where | Final text | Status |
|---|---|---|---|
| S1 | `og:title`, `twitter:title` | El Archivo | APPROVED |
| S2 | 404 page `<h1>` | No encontramos esa página | APPROVED |
| S3 | 404 page body | Puede que el enlace esté mal escrito o que la página ya no exista. | APPROVED |
| S4 | 404 page link | Ir a Inicio | APPROVED |
| S5 | `og:description`, `twitter:description` | **Not the approved sentence.** The page already had an approved `<meta name="description">` with different wording, so by the instruction it is reused: "Archivo histórico independiente del Baloncesto Superior Nacional, 1930–2026. Proyecto de un aficionado, no oficial." The sentence offered in the message ("La historia del BSN en un solo lugar: campeones, jugadores, récords y juegos.") is NOT in the code. | REUSED EXISTING; owner to confirm which one wins |
| S6 | `document.title` per route | "<label> · El Archivo", Inicio just "El Archivo". Labels are existing visible text only: nav label (Historia, Jugadores, Equipos, Juega, Archivo), subnav pill (La cinta, Títulos, Buscar, Comparar, Salón, Líderes de carrera, Récords, Preguntar, A la medida, Cobertura y fuentes, Calidad de datos, the four game names, ...), the visible `<h1>` for Perfil and the four legal pages, the player name and the club name on those pages. | APPROVED (pattern); no new words |
| S7 | 404 `<title>` | No encontramos esa página · El Archivo (S2 plus the S6 suffix) | APPROVED (pattern); owner to confirm |

## B. Built under the delegation, not individually approved in the message
These are accessible names only (nothing is drawn). They come from the audit's section 9 and are the only way to meet WCAG 2.5.3 / landmark rules; the owner should confirm or reword.
| # | Where | Final text | Status |
|---|---|---|---|
| A1 | header mark `aria-label` (was "Ir a Inicio") | El Archivo 1930 — 2026, ir a Inicio. The audit proposed "El Archivo, ir a Inicio"; the visible text is "EL ARCHIVO 1930 — 2026", and a name must contain all of it. | PENDING owner confirmation |
| A2 | Juega game tiles | No string. The `aria-label` "Abrir <juego>" was removed, so each tile is named by its own visible text (title, description, meta, "Jugar"). | no new text |
| A3 | `#privacidad` scrolling table block | Tabla de datos, desplazable (audit P11 proposal) | PENDING owner confirmation |
| A4 | bottom bar landmark | Secciones (the existing rail label, reused) | no new text |
| A5 | scrollable tables (`buildTable`) | Unchanged label "Tabla con desplazamiento horizontal"; role changed from `region` to `group` so two tables on one page no longer collide as landmarks | no new text |

## APPROVED (owner decisions, PHASE_71 fixup)
- S5: keep the existing meta description for og:description and twitter:description; the offered sentence is dropped. APPROVED.
- A1: "El Archivo 1930 — 2026, ir a Inicio" APPROVED.
- A3: "Tabla de datos, desplazable" APPROVED.
- S7: 404 title "No encontramos esa página · El Archivo" APPROVED.
