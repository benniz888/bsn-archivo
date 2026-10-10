# Strings pending — PHASE_64_INICIO (owner approves before build)

| # | Where | Old | Proposed |
|---|---|---|---|
| 1 | Search placeholder, desktop | Prueba: cuándo murió Piculín · 1971 · títulos de Bayamón | Prueba: títulos de Bayamón · 1971 |
| 2 | Search placeholder, phone | Prueba: cuándo murió Piculín | Prueba: títulos de Bayamón |
| 3 | Search aria-label | Buscar en el archivo. Ejemplo: Prueba: cuándo murió Piculín · 1971 · títulos de Bayamón | Buscar en el archivo. Ejemplo: títulos de Bayamón o 1971. |
| 4 | Disclosure summary | La liga ahora (header) | Más de la liga ahora |
| 5 | "Sigue donde lo dejaste" row label | (new) | Sigue donde lo dejaste |
| 6 | Entry cards: Jugadores ctx | Cada ficha dice también qué no se sabe de él. | removed (card keeps stat + phrase) |
| 7 | Entry cards: Comparar ctx | Dos carreras lado a lado. Las casillas vacías son huecos del archivo, no ceros. | removed |
| 8 | Entry cards: Juega ctx | Nueve cruces de club × logro. Un jugador que encaje en cada uno. | removed |
| 9 | Entry cards: Archivo ctx | Antes de 2011 no hay estadística por temporada del BSN. El archivo enseña ese hueco y todos los demás. | removed |
| 10 | Hero footer note | Cambia de club desde la píldora de arriba y el archivo se reordena a su alrededor. | removed |
| 11 | Cinta axis labels | (new) | decade years only (1930, 1940, ...), numbers, no prose |

## Build notes (PHASE_64)
- Verified: "títulos de Bayamón" and "1971" both return Bayamón results (18 títulos / campeón 1971) in Chromium and WebKit.
- No new Spanish beyond the table above. Existing strings reused as-is: "Lo próximo", its lede, the disclosure lede, the hero lede, "Hola, X", "Ver la cinta".

## Round 2 fixups
| # | Where | Old | Proposed |
|---|---|---|---|
| 12 | Lo próximo toggle (collapsed) | (new) | Ver todas las fechas |
| 13 | Lo próximo toggle (open) | (new) | Ver menos fechas |
| 14 | Últimos campeones meta | Título #N · ver en Historia → Dinastías | Título #N |
| 15 | Lo próximo stat strip labels (3) | días para la apertura estimada de 2027 / días para la próxima fecha confirmada / días desde el último juego del BSN | removed (hero shows them) |
