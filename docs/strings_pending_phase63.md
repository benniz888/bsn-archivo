# PHASE_63 — public Spanish strings pending owner approval

| String | Where | Note |
|---|---|---|
| sin dato (tooltip "Sin dato") | empty cells in every buildTable table and in phone sub-lines | replaces the bare "—"; CSV still exports empty |
| Mostrando N de M | footer of paged tables (Temporadas, Jugadores both modes) | N = rows drawn, M = total matches, both computed |
| Ver K más | footer button | K = min(25, rows left), computed |
| Mostrar todo | footer button | draws all rows |
| Ver nota / Ocultar nota | clamped Nota cells | button only appears when the text is actually cut |
| Tabla con desplazamiento horizontal | aria-label, only while a table scrolls | screen readers |
| Década de 2020 (etc.) | divider rows in Temporadas, Premios, Calendario | only while sorted by year and >= 12 rows shown |
| Subcampeón: <club> | phone sub-line under Campeón (Temporadas, <= 640px) | the sub-line for other tables is the bare values joined with " · " |
| Limpiar búsqueda | aria-label of the search clear button | |
| Filtro | aria-label fallback for a combobox with no visible label (none today) | |
| Vaqueros, Criollos, Gigantes... | Campeón short names | the club word before " de "; full name in title/aria-label |

Removed: "Mostrando 500 de N — afiná la búsqueda." (the 500 cap is gone; paging shows every match).
Unchanged: "sin registrar", "Descargar CSV", "N filas", all filter labels and options.
