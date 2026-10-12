# PHASE_72_AUDIT proposed Spanish strings

Sections A-D are the audit's proposals. Section E is what PHASE_72A built (owner decisions D1, D5, D6, D7); its rows are in `web/` and were approved by the owner (E7 and E9 as edited). "Existing" means the Spanish text is already live and only a key or placement changes.

## A. Decisions on existing public strings (item 7)
| # | Where | Current forms | Proposal | Status |
|---|---|---|---|---|
| S1 | Defensive award, all views | "Defensor del Año" (6), "Defensor del año" (1), "Defensa del Año" (renders 41 historic season rows), "Jugador Defensivo del Año" (1, Butler's bio) | Owner picks one official name; every other form is rewritten to it. Dominant today: "Defensor del Año". The league's own historic page prints "DEFENSA DEL AÑO". | PENDING owner |
| S2 | Sixth-man award | "Sexto Hombre" (4), "Sexto hombre del año" (1) | Owner picks one; dominant today: "Sexto Hombre". | PENDING owner |
| S3 | Capitalization of "del Año" | "Novato del Año" 8 / "Novato del año" 5; "Progreso del Año" 5 / "Progreso del año" 2 | One rule for all awards (capital "Año", as in the archive labels). | PENDING owner |

## B. Existing text, key fix only (item 5)
| # | Where | Text | Status |
|---|---|---|---|
| S4 | `POOL` bio for José «Piculín» Ortiz | «Piculín». Llegó a la NBA y volvió a casa a terminar. | Existing in `BIO_ES` under the key `José Ortiz`; the pool name is `José «Piculín» Ortiz`, so it never applies. Re-key only; no new text. |

## C. New text proposed
| # | Where | Proposed text | Why | Status |
|---|---|---|---|---|
| S5 | Récords and Líderes, career rebounds (item 1) | Los récords y los líderes no coinciden en rebotes de carrera. Seguimos verificando la cifra. | Until an independent source decides between Rodríguez 6,178 and Butler 8,236. Uses the existing `.warn` pattern. | PENDING owner |
| S6 | Atenienses de Manatí club note (item 8a) | Jugó en el BSN en 2015 y 2016. | Replaces "Se mudó a Fajardo en 2017.", which is unverified. The two seasons are the ones the archive standings show. | PENDING owner |
| S7 | Season-detail row for the 1979 rookie award (item 2) | Sin selección | The source cell reads "NO FUE SELECCIONADO", which is not a person. Alternative: hide the row. | PENDING owner |
| S8 | `COVERAGE` percentage footnote (item 6, H11) | Only if the owner keeps the percentages: state the basis in one sentence. If dropped, the footnote is deleted. | The two `COVERAGE` tables disagree and the figures are unsourced. | PENDING owner |

## D. Not strings
Name corrections (GOERGIE, Casian0, truncations) change data values, not interface text; they are listed in the audit's override table and need the owner's approval of the display style (accents, nickname quotes, maternal surname), not of wording.

## E. PHASE_72A as built (in `web/`) - all APPROVED by the owner (E7 and E9 as edited)
| # | Where | Text now | Basis | Status |
|---|---|---|---|---|
| E1 | Líderes > Rebotes, Butler row (tag) | SIN CONFIRMAR | wording given by the owner in D1 | APPROVED |
| E2 | Butler bio line (`tabs.js` `life`) | Líder histórico de rebotes del BSN con 8,236 (sin confirmar). | D1; "sin confirmar" is existing site vocabulary | APPROVED |
| E3 | Butler Salón de la Fama role and first chip | ... máximo reboteador histórico (sin confirmar) ... / Máximo reboteador histórico (sin confirmar) | D1 | APPROVED |
| E4 | Récords | the "Rebotes de carrera" card (Rubén Rodríguez, 6,178) is removed | D1 | APPROVED |
| E5 | Season detail, defensive award label (41 historic rows) | Defensor del Año (was Defensa del Año) | D7 | APPROVED |
| E6 | Butler bio | Siete veces Defensor del Año. (was Jugador Defensivo del Año) | D7 | APPROVED |
| E7 | Moses Brown / Christian López bios | Fue Defensor del Año en 2026. / Fue Sexto Hombre en 2026. (were "Defensor del año", "Sexto hombre del año") | D7, edited by the owner | APPROVED (as edited) |
| E8 | Cobertura tile text, per decade | Campeón a/n · Subcampeón b/n · Anotación c/n · MVP d/n (counts derived from the data; words already used on the site) | D6 replaces the typed notes such as "Campeones sí. Nada más." | APPROVED |
| E9 | Cobertura footnote, under the tiles | El porcentaje indica cuántos de cuatro datos (campeón, subcampeón, campeón de anotación y MVP) tiene el archivo por cada temporada de la década. (replaces the removed "estimación editorial" footnote) | D6, wording by the owner | APPROVED (as edited) |
| E10 | Jugadores > Todo el archivo, offline note | El índice completo solo está disponible en la versión publicada, con conexión. Esta copia local trae los N jugadores destacados. (the typed "(3.303 jugadores)" and the fallback 385 are removed) | the count cannot be read offline | APPROVED |
| E11 | Piculín bio | no change in text; the existing Spanish line now applies (key fixed) | D5 | APPROVED |

## F. PHASE_72D: the 1979 row (S7), proposal only, NOT applied
| # | Where | Text now | Proposed text | Status |
|---|---|---|---|---|
| F1 | Historia > La cinta > 1979, season detail, line "Novato del Año" | `NO FUE SELECCIONADO` (the source's own cell, shown as printed; the display layer leaves it alone) | `No se seleccionó` (what the source says, in sentence case). Alternatives: `Sin selección` (the S7 draft), or hide the line. | PENDING owner |
| F2 | `docs/data_update_runbook.md` and the data-update report | English, developer-facing; not a public string | n/a | no approval needed |
