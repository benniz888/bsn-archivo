# PHASE_68 — Spanish strings awaiting owner approval

Status: NOTHING BELOW IS APPROVED. Every string is a clearly marked DRAFT in the code (comments say "DRAFT wording").
`{N}`, `{Y}` etc. are values read from the data at render time; none is a typed-in number.
"Was" is the text in HEAD. Approve, edit or reject each line; wording in the code changes only after that.

## A01 — false "Antes de 2011" claim (3 sites, plus 2 siblings of the same claim)

The archive holds per-season leader tables for 15 seasons (`manifest.counts.seasons_with_leaders`, 1986 and 2000–2002,
2007–2010, 2012–2014, 2018–2021 per `web/data/seasons/*.json`), so a "nothing before 2011" claim is false.
The draft below states the count, taken from the manifest, against `YEARS.length`. When the manifest cannot be loaded
the text says "solo en una parte" and gives no number.

| # | Where | Was | Draft |
|---|---|---|---|
| S1a | Archivo landing, "Lo que este archivo no sabe" card, title line | Antes de 2011 no hay estadística por temporada | Líderes por temporada en {N} de {Y} temporadas |
| S1b | same, no-manifest fallback | (none) | Líderes por temporada solo en una parte de las temporadas |
| S1c | same card, body | Ese es el muro real. Todo lo demás — los huecos, … | Ese es el hueco real. Todo lo demás — los huecos, … (only the first sentence changes) |
| S2a | Inicio hub card "Archivo": big number | 2011 | {N} (— when the manifest is missing) |
| S2b | same card, caption | el muro real | temporadas con líderes |
| S3a | Player page, "Lo que este archivo no sabe de {Nombre}", last sentence | Antes de 2011 no existe ninguna base pública de estadísticas por temporada del BSN. | Este archivo tiene líderes por temporada en {N} de {Y} temporadas. |
| S3b | same, no-manifest fallback | (none) | Este archivo tiene líderes por temporada solo en una parte de las temporadas. |
| S4a | Cobertura, "Lo que falta" list, first bullet | No hay una base pública de estadísticas por temporada del BSN anterior a 2001. Antes de eso el archivo solo tiene campeones, campeones de anotación y MVP. | Líderes por temporada: {N} de {Y} temporadas. En las demás el archivo no tiene tablas de líderes. |
| S4b | same, no-manifest fallback | No existe ninguna base pública de estadísticas por temporada del BSN anterior a 2011. Ese es el muro real. | Las tablas de líderes por temporada existen solo en una parte de las temporadas. Ese es el hueco real. |

Note on S4a: the deployed bullet said "anterior a 2001", which contradicts both HEAD's own landing text (2011) and the data
(leader tables exist for 1986 and 2000). I replaced it with the same count-based claim rather than leave a third version.
Owner decides whether "estadística por temporada" should mean leader tables (what the draft counts) or something else.

## A04 — hard-coded counts replaced by values read from the data

Numbers only; the words are unchanged unless stated.

| # | Where | Was | Now |
|---|---|---|---|
| S5a | Constructor, table picker | Franquicias (32) | Franquicias ({FKEYS.length}) — renders 33 |
| S5b | same | MVP por año (39 recuperados) | MVP por año ({MVP_YEARS.length} recuperados) — renders 63 |
| S5c | same | Líderes de carrera (30) / Récords de la liga (11) / Temporadas (1930–2026) | same words, count and years read from LEADERS, RECORDS, YEARS |
| S5d | Constructor, Desde/Hasta placeholders | 1930 / 2026 | first and last year of YEARS |
| S5e | Historia heading | 97 temporadas | {Y} temporadas (renders 97) |
| S5f | Historia, "Títulos por franquicia" lede | Quién ha ganado más en 97 temporadas. Bayamón lleva la delantera desde hace décadas. | Quién ha ganado más en {Y} temporadas. {Ciudad del club con más títulos} lleva la delantera. — **"desde hace décadas" dropped**: no data in the app states it |
| S5g | Historia, Dinastías footnote | {n} rachas de dos o más títulos consecutivos en 97 temporadas. Bayamón 2025–26 es la primera desde Ponce en 2014–15. | {n} rachas de dos o más títulos consecutivos en {Y} temporadas. La más reciente es {Club} {a}–{b}; la anterior, {Club} {a}–{b}. — **the "primera desde" claim is replaced** by the two latest runs read from the same data |
| S5h | Inicio hub "El más ganador" card; Historia view card; Glosario lede | 97 temporadas (3 places) | {Y} temporadas |
| S5i | Cobertura, source card title | Campeones 1930–2025 | Campeones {primer año}–{último año − 1} (the 2026 season has its own card next to it) |
| S5j | Cobertura, "Lo que falta" | Los números retirados de Bayamón (8) y Guaynabo (3) … | same sentence, clubs and counts read from RETIRED |
| S5k | Cobertura, scoring-champions bullet | Campeones de anotación 1948–2021 (68 temporadas). Faltan 2022 en adelante. | range and "Faltan {año} en adelante" read from the scoring table |
| S5l | Cobertura, no-manifest fallback | MVP por año: 39 temporadas recuperadas de … | same, count read from MVP_YEARS |
| S5m | Historia, view card "La cinta" | Cada temporada desde 1930 con su campeón, … | Cada temporada desde {primer año} con su campeón, … |
| S5n | Preguntar, season after the last | El archivo llega hasta 2026. | El archivo llega hasta {último año}. |

## A05 — stale cross-references (links added)

| # | Where | Was | Draft |
|---|---|---|---|
| S6a | Calendario note | … enlazadas en Hoy bajo «Canales oficiales». | … enlazadas en [Inicio], bajo «Canales oficiales». ([Inicio] links to `#inicio`) |
| S6b | Glosario lede | También se pueden preguntar en Consulta: escribe «qué es un refuerzo». | También se pueden preguntar en [Preguntar]: escribe «qué es un refuerzo». ([Preguntar] links to `#archivo/preguntar`) |

## A12 — decade title in Preguntar

| # | Was | Draft (owner picks) |
|---|---|---|
| S7 | Campeones de los 1970 | Campeones de la década de 1970 — or: Campeones de los años 70 |

## A11 — empty and invalid states in "A la medida"

| # | When | Draft |
|---|---|---|
| S8a | no rows match | Sin resultados con estos filtros. |
| S8b | Desde > Hasta | «Desde» es mayor que «Hasta»: no hay años en ese rango. |
| S8c | a year field is not a number | Escribe el año con números; se ignoró «{valor}». |

## A18 — season detail could not be loaded (Historia, la cinta)

| # | When | Draft |
|---|---|---|
| S9 | the season JSON request fails or the file is missing (was: blank) | No se pudo cargar el detalle de esta temporada. |

## A17 — Cobertura fallback when the manifest cannot be loaded

| # | Was | Draft |
|---|---|---|
| S10a | No hay boxscores. Ninguno, de ninguna temporada. (false: 1,292 box scores exist) | Los boxscores existen solo para algunas temporadas; sin los datos del sitio no se puede decir cuáles. |
| S10b | Posiciones completas solo de 2009, 2025 y 2026. | (line removed; stale, the manifest-backed version already states the real count) |
| S10c | "La pista que abre todo" card ("Hallazgo del 3 de septiembre de 2026 … Eso era falso …") | (block removed; session narrative that is not a statement about the archive) |

## A06 / A07 — accessible names added (screen readers)

| # | Where | Text |
|---|---|---|
| S11a | Year links in "Todas las temporadas" and the scoring-champions list | Ver la temporada {año} |
| S11b | Scrollable table region (already in HEAD for buildTable; now also on hand-built tables) | Tabla con desplazamiento horizontal |

## Not changed, listed for completeness

- A03 note ("Esta lista y la de Récords no coinciden…"): not built. The owner deferred A03 to PHASE_72 and said not to pick a side.
- A06 optional visible hint "Desliza para ver más columnas": not added. The cue is an edge fade plus a drawn chevron, no text.
- A14 ties: ranks are shown as the same number (1, 2, 2, 4). No "T4" string is used, so there is nothing to approve.
- A07 on phones: the runner-up in "Todas las temporadas" stays plain text in the sub-line (a link there cannot reach 44px without taller rows). The year and the champion are links at every width; the runner-up is a link from 641px up. No string involved.

## Owner decision, 2026-10-11: ALL strings above APPROVED as drafted; S7 = 'Campeones de la década de 1970'.
