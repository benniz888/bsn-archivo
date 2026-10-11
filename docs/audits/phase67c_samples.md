# PHASE_67C — Muestras de escalera de pistas (¿Quién soy?)

> Corrección (PHASE_67C paso 2): en la muestra 3 dije que los MVP de Hodge no existían como campo estructurado. Sí existen (MVP_YEARS 2014 y 2022; MVP de la final 2018). Ver `docs/audits/data_review_todo.md`.

Generadas con un script de muestra en el directorio temporal (solo lectura; nada bajo `web/` fue modificado). Cada pista lleva el campo de datos y el valor que la sostiene. Orden: de más difícil (más candidatos) a más fácil.

Columnas: **Cand.** = candidatos que quedan del pool de 376 tras esa pista, contando como "posible" a todo jugador que no tiene el campo (cota conservadora: la escalera nunca parece más estrecha de lo que es). **Único** = jugadores del pool que sí tienen el campo y lo cumplen (cuán identificadora es la pista por sí sola).

Todo el texto es **propuesto**. Las cadenas se listarán en `docs/strings_pending_phase67c.md` al construir (aún no existe).

## 1. Raymond Dalmau — Muy famoso · 1960s–1980s

Nivel de datos: **A** · pistas: 6 · tipos distintos: 6

| # | Pista (ES) | Campo = valor | Cand. | Único |
|---|---|---|---|---|
| 1 | Es nativo o nativizado. | `POOL.t has native` | 342 | 43 |
| 2 | Promedió entre 20 y 25 puntos por juego en su carrera. | `POOL.ppg=21.6` | 53 | 34 |
| 3 | Jugó con Piratas de Quebradillas. | `POOL.c=["que"]` | 13 | 23 |
| 4 | Jugaba de base. | `POOL.pos=PG (curated, no posSrc)` | 5 | 20 |
| 5 | Promedió 10.6 rebotes por juego. | `POOL.rpg=10.6` | 5 | 8 |
| 6 | Se retiró en 1985 liderando la liga en puntos, rebotes y asistencias a la vez. | `POOL.b` | 1 | — |

**Veredicto:** OK. Nada lo regala antes de la pista 6. Un aficionado que sepa "base nativo, ~21 ppg, 10.6 rebotes, solo Quebradillas" llega en 4–5. La pista 1 (nativo) casi no descarta (43 jugadores con etiqueta) pero es inocua.

## 2. Georgie Torres — Muy famoso · 1970s–1990s

Nivel de datos: **A** · pistas: 6 · tipos distintos: 6

| # | Pista (ES) | Campo = valor | Cand. | Único |
|---|---|---|---|---|
| 1 | Es nativo o nativizado. | `POOL.t has native` | 342 | 43 |
| 2 | Promedió entre 20 y 25 puntos por juego en su carrera. | `POOL.ppg=23.4` | 53 | 34 |
| 3 | Jugaba de escolta. | `POOL.pos=SG (curated, no posSrc)` | 25 | 3 |
| 4 | Medía 1,93 m. | `BIO.ht=1.93 m` | 25 | 2 |
| 5 | Fue Jugador Más Valioso de la liga al menos 3 veces. | `awards mvp [1984,1985,1986] [MVP_YEARS/SEASON_AWARDS/seasons/*.json/FINALS_BY_YEAR/SCORING` | 1 | 4 |
| 6 | Máximo anotador histórico con 15,863 puntos. | `POOL.b` | 1 | — |

**Veredicto:** OK con reserva. La pista 4 (estatura, BIO.ht) la comparten solo 2 jugadores con dato; la pista 5 (MVP al menos 3 veces) ya lo identifica, así que se resuelve en 4–5, que es la meta. El conteo "al menos 3" sale de MVP_YEARS (1984–86), no de un campo de carrera.

## 3. Walter Hodge — Intermedio · 2010s–2020s

Nivel de datos: **A** · pistas: 6 · tipos distintos: 6

| # | Pista (ES) | Campo = valor | Cand. | Único |
|---|---|---|---|---|
| 1 | Promedió entre 10 y 15 puntos por juego en su carrera. | `POOL.ppg=12.7` | 77 | 45 |
| 2 | Jugaba de base. | `POOL.pos=PG (curated, no posSrc)` | 42 | 20 |
| 3 | Su mejor temporada registrada fue 2021, con 19.8 puntos por juego. | `POOL.hi=[2021,19.8]` | 10 | 15 |
| 4 | Jugó con Capitanes de Arecibo, Cangrejeros de Santurce. | `POOL.c=["are","san"]` | 5 | 1 |
| 5 | Ganó al menos un campeonato del BSN. | `career/ss ∩ champion [2021]` | 5 | 18 |
| 6 | MVP de la liga en 2014 y otra vez en 2022 con Arecibo, y MVP de la final de 2018. | `POOL.b` | 1 | — |

**Veredicto:** FLAG leve. La pista 4 (Arecibo + Santurce) es una combinación de clubes que solo cumple él entre los jugadores con dato. Regla propuesta: combinaciones de clubes no antes de la pista 5. Los MVP de Hodge (2014, 2022) no existen como campo estructurado; solo están en la frase de la pista 6.

## 4. Gary Browne — Intermedio · 2010s–2020s

Nivel de datos: **A** · pistas: 6 · tipos distintos: 6

| # | Pista (ES) | Campo = valor | Cand. | Único |
|---|---|---|---|---|
| 1 | Promedió entre 10 y 15 puntos por juego en su carrera. | `POOL.ppg=10.2` | 77 | 45 |
| 2 | Es nativo o nativizado. | `POOL.t has native` | 64 | 43 |
| 3 | Su mejor temporada registrada fue 2022, con 15.5 puntos por juego. | `POOL.hi=[2022,15.5]` | 30 | 10 |
| 4 | Promedió 7 asistencias por juego. | `POOL.apg=7` | 22 | 6 |
| 5 | Fue Jugador Más Valioso de la liga. | `awards mvp [2017] [MVP_YEARS/SEASON_AWARDS/seasons/*.json/FINALS_BY_YEAR/SCORING]` | 6 | 14 |
| 6 | MVP y líder de asistencias en 2017. Campeón con Bayamón en 2026. | `POOL.b` | 1 | — |

**Veredicto:** OK. Cinco tipos distintos; el MVP 2017 (pista 5) lo deja en 6 candidatos y la frase final lo cierra.

## 5. Mario Butler — Intermedio · 1980s–2000s

Nivel de datos: **X** · pistas: 6 · tipos distintos: 6

| # | Pista (ES) | Campo = valor | Cand. | Único |
|---|---|---|---|---|
| 1 | Promedió entre 15 y 20 puntos por juego en su carrera. | `POOL.ppg=15.7` | 152 | 120 |
| 2 | Promedió 10.6 rebotes por juego. | `POOL.rpg=10.6` | 35 | 8 |
| 3 | Medía 2,03 m. | `BIO.ht=2.03 m` | 30 | 1 |
| 4 | Su carrera en la liga duró de 1980 a 2008. | `HOF.yrs=1980–2008` | 27 | 1 |
| 5 | Fue Jugador Más Valioso de la liga. | `awards mvp [1988] [MVP_YEARS/SEASON_AWARDS/seasons/*.json/FINALS_BY_YEAR/SCORING]` | 7 | 14 |
| 6 | Número 1 de todos los tiempos en rebotes, con 8,236 rebotes en 1980–2008. | `POOL.b` | 1 | — |

**Veredicto:** FLAG, quedaría fuera hasta resolver. Las pistas 3 (estatura 2,03 m) y 4 (carrera 1980–2008) casi lo identifican solas (1 jugador con dato cada una). POOL.c está vacío, así que falta la pista de club. La atribución MVP 1988 sale de un cruce por nombre y debe verificarse antes de usarla.

## 6. Héctor Blondet — Menos conocido · 1970s

Nivel de datos: **A** · pistas: 6 · tipos distintos: 6

| # | Pista (ES) | Campo = valor | Cand. | Único |
|---|---|---|---|---|
| 1 | Es nativo o nativizado. | `POOL.t has native` | 342 | 43 |
| 2 | Jugaba de base o escolta. | `POOL.pos=G (curated, no posSrc)` | 300 | 24 |
| 3 | Jugó con Capitanes de Arecibo. | `POOL.c=["are"]` | 23 | 22 |
| 4 | Promedió entre 25 y 30 puntos por juego en su carrera. | `POOL.ppg=25.1` | 4 | 2 |
| 5 | Ganó el título de anotación. | `awards scoretitle [1974] [MVP_YEARS/SEASON_AWARDS/seasons/*.json/FINALS_BY_YEAR/SCORING]` | 2 | 7 |
| 6 | Campeón de anotación en 1974. | `POOL.b` | 1 | — |

**Veredicto:** OK en el límite. La pista 4 (25–30 ppg) deja 4 candidatos y el título de anotación de 1974 (pista 5) lo cierra casi solo. Un aficionado casual no lo resuelve antes de la 5; un conocedor sí.

## 7. Alfonso Plummer — Menos conocido · 2020s

Nivel de datos: **A** · pistas: 6 · tipos distintos: 6

| # | Pista (ES) | Campo = valor | Cand. | Único |
|---|---|---|---|---|
| 1 | Jugó en el BSN en los 2020. | `POOL.d=[2020]` | 279 | 279 |
| 2 | Promedió entre 15 y 20 puntos por juego en su carrera. | `POOL.ppg=18.9` | 84 | 120 |
| 3 | Jugaba de base o escolta. | `POOL.pos=G (curated, no posSrc)` | 73 | 24 |
| 4 | Jugó con Capitanes de Arecibo. | `POOL.c=["are"]` | 4 | 22 |
| 5 | Su mejor temporada registrada fue 2024, con 19 puntos por juego. | `POOL.hi=[2024,19]` | 2 | 18 |
| 6 | Progreso del año en 2024 con Arecibo. | `POOL.b` | 1 | — |

**Veredicto:** FLAG, pista vaga. La pista 1 ("Jugó en los 2020") no descarta a 279 de 376. Es el patrón de los 2020s: los jugadores de RealGM comparten década, estatus y posición calculada, y solo se separan por club + mejor temporada (pistas 4–5).

## 8. Cheick Diallo — Menos conocido · 2020s

Nivel de datos: **A** · pistas: 6 · tipos distintos: 6

| # | Pista (ES) | Campo = valor | Cand. | Único |
|---|---|---|---|---|
| 1 | Promedió entre 15 y 20 puntos por juego en su carrera. | `POOL.ppg=19.3` | 152 | 120 |
| 2 | Llegó a la liga como refuerzo. | `POOL.t has import` | 127 | 34 |
| 3 | Su mejor temporada registrada fue 2025, con 19.3 puntos por juego. | `POOL.hi=[2025,19.3]` | 30 | 17 |
| 4 | Jugaba de pívot. | `POOL.pos=C (curated, no posSrc)` | 12 | 14 |
| 5 | Jugó con Osos de Manatí, Cangrejeros de Santurce. | `POOL.c=["man","san"]` | 2 | 1 |
| 6 | Tercero en anotación y segundo en tapones en 2025. | `POOL.b` | 1 | — |

**Veredicto:** OK pero difícil. Sin honores estructurados; se apoya en ppg, rebotes y mejor temporada. Quien no tenga en la cabeza la lista de refuerzos necesita las 6 pistas.

## 9. Teófilo Cruz — Famoso · 1950s–1980s

Nivel de datos: **A** · pistas: 6 · tipos distintos: 6

| # | Pista (ES) | Campo = valor | Cand. | Único |
|---|---|---|---|---|
| 1 | Es nativo o nativizado. | `POOL.t has native` | 342 | 43 |
| 2 | Promedió 8 rebotes por juego. | `POOL.rpg=8` | 58 | 29 |
| 3 | Jugó con Cangrejeros de Santurce. | `POOL.c=["san"]` | 15 | 22 |
| 4 | Jugaba de pívot. | `POOL.pos=C (curated, no posSrc)` | 5 | 14 |
| 5 | Medía 2,06 m. | `BIO.ht=2.06 m` | 5 | 1 |
| 6 | Cuatro MVP y un puesto en el Salón de la Fama de FIBA. | `POOL.b` | 1 | — |

**Veredicto:** FLAG de datos. La pista de club (Cangrejeros de Santurce, POOL.c=[san]) no se pudo verificar en este paso. Mario Morales tiene el mismo campo [san] mientras STONE dice que su cancha es la de los Mets de Guaynabo: conflicto sin resolver. La pista 5 (estatura 2,06 m) es casi única (1 con dato).

## 10. Juan Báez — Menos conocido · 1950s–1960s

Nivel de datos: **X** · pistas: 2 · tipos distintos: 2

| # | Pista (ES) | Campo = valor | Cand. | Único |
|---|---|---|---|---|
| 1 | Jugaba de alero o ala-pívot. | `POOL.pos=F (curated, no posSrc)` | 310 | 27 |
| 2 | Tres veces MVP con los Cardenales de Río Piedras: 1957, 1963 y 1964. | `POOL.b` | 1 | — |

**Veredicto:** FLAG, EXCLUIR. Solo 2 pistas válidas (posición y la frase). La frase regala club, años y los 3 MVP; no hay ppg/rpg/apg ni BIO. Jugador importante con datos insuficientes: ejemplo de exclusión.
