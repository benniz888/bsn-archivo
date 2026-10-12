# Strings pending owner approval — PHASE_67C (¿Quién soy? + La Temporada Perfecta plural)

All strings below are already in the UI. `{…}` marks a value filled from data. Numbers: decimal point (`21.6`, `2.03 m`), comma for thousands (`6,178`, via `num()`), as everywhere on the site.

## ¿Quién soy? — screen
| String | Status |
|---|---|
| Hasta seis pistas, de la más difícil a la más obvia. Mientras menos necesites, más vale el acierto. | changed (card on Juega; was "Seis pistas que van de lo difícil a lo obvio…") |
| Pista {k} de {n} | new |
| Nombre del jugador | new (aria-label of the guess field) |
| Hay varios jugadores con ese nombre. Elige uno de la lista. No gasta intento. | new |
| Elige un nombre de la lista. No gasta intento. | new |
| Ese nombre no está en la nómina verificada. No gasta intento. | reused from La Cuadrícula |
| Sugerencias de jugadores | reused from La Cuadrícula |
| No hay jugadores con pistas suficientes todavía. | new (only if no player can build a ladder) |

Unchanged: Tres intentos · cada pista revelada baja los puntos · {n} puntos · Intentos {n} · ¿Quién es? · Adivinar · Otra pista · Otro jugador · Ver su ficha · Correcto: {nombre}. {n} puntos. · No. Te quedan {n}. · Se acabaron los intentos. Era {nombre}.

## ¿Quién soy? — clues
Era and style
- Jugó en los {1980}s y los {2000}s. / Jugó en los {1980}s. — unchanged; only for players who started before the 2020s
- Jugó en {3} décadas distintas. — new (counts the decades the player was active, from POOL.d; not the first-to-last span)
- Jugaba de {base|escolta|alero|ala-pívot|pívot|base o escolta|alero o ala-pívot}. — changed (lower case; only for curated positions, never the computed ones)
- Medía {2.03 m}. — new
- Promedió entre {15} y {20} puntos por juego en su carrera. — new
- Promedió {21.6} {punto|puntos} por juego en su carrera. — changed (was "…por juego.")
- Promedió {10.6} rebotes y {5.1} asistencias por juego. — unchanged wording (rebotes or asistencias alone, or robos/tapones, as before); only for 8+ rpg or 5+ apg
- Vistió el uniforme de {3} clubes distintos del BSN. — new
- Jugó con {club}. — new
- Jugó con {A} y {B}. / Jugó con {A}, {B} y {C}. — new (fifth clue or later)
- Su mejor temporada registrada fue {2021}, con {19.8} puntos por juego. — new
- En {2021} promedió {19.8} puntos, {2.8} rebotes y {6.2} asistencias con {club}. — new
- Llegó a la liga como refuerzo. / Es nativo o nativizado. — unchanged (rarely selected now)
- Llegó a jugar en la NBA. — new
- Ganó su primer premio de la liga en los {1970}s. — new

Honors (the count wording says "al menos" because the award tables have gaps)
- Fue elegido Jugador Más Valioso de la liga. · Ganó al menos {N} veces el premio de Jugador Más Valioso. · Fue Jugador Más Valioso de la liga en {años}.
- Fue MVP de una serie final. · Fue MVP de la final al menos {N} veces. · Fue MVP de la final en {años}.
- Ganó el título de anotación. · Ganó al menos {N} títulos de anotación. · Fue campeón de anotación en {años}.
- Lideró la liga en rebotes en una temporada. · Lideró la liga en asistencias en una temporada. · Fue líder de rebotes en {años}. · Fue líder de asistencias en {años}.
- Only these four use the archive label (SEASON_AWARDS): Ganó el premio de {Novato del Año|Defensor del Año|Sexto Hombre|Progreso del Año}. · the same with " en {año}." as the last clue
- Ganó al menos un campeonato del BSN. · Ganó al menos {N} campeonatos del BSN.
- Está entre los diez primeros de la historia del BSN en {puntos|rebotes|asistencias}. · Es el número {N} de todos los tiempos en {puntos|rebotes|asistencias}, con {4,884} {puntos|rebotes|asistencias}. (N is 2 or more; no "número 1" and no "récord" clue exists, see docs/audits/data_review_todo.md)
- Un coliseo lleva su nombre.

## La Temporada Perfecta — draft line
| String | Status |
|---|---|
| Gira equipo y década · coloca cinco posiciones · {n} pase / {n} pases | changed: "1 pase", "0 pases", "2 pases" (was "1 pases") |
