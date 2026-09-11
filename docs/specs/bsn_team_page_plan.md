# Spec: Team page "time warp" — coliseo, rivalry, lore

Revises the original plan (kept below as history) with the owner's review
answers + facts confirmed against the live repo and outside sources before
writing any code.

## [DECISION]

Owner-approved 2026-09-11, after plan review:

1. **Extend `VENUES` + the existing `.phero` masthead** (shipped in 8.3b —
   title count / sparkline / note). No separate "coliseo strip" card.
2. **Rivalry + title counts are read live from `F[key].won`/`.ru`**, never
   from a CSV snapshot — the page can never contradict its own data.
3. **Fix Guaynabo's venue**: Coliseo Mario «Quijote» Morales, 5,500 (not the
   current wrong "Fernando «Rube» Hernández, 3,500"). Add a live caveat: the
   Mets play the 2026 season in Gurabo during a $17M renovation, back home
   expected 2028.
4. **Rename `F.car`** to reflect "Gigantes de Carolina/Canóvanas."
5. **Drop the Guaynabo 1935-Cangrejeros lineage anecdote** — conflicts with
   `F.san.founded:1918` and isn't corroborated. Replace with the
   already-sourced, uncontested fact: Mario Morales, the franchise's
   4×-MVP legend, has the arena named for him.
6. **Hold the Humacao anecdote** until D-045 (Grises/Caciques de Humacao
   split) resolves.
7. **Defunct franchises: not this pass.** Ship the 12 actives; defunct teams
   (Humacao included, once D-045 resolves) are a follow-up phase.
8. **Capacities marked as approximate in the UI** — not just a mental
   caveat.

## [FOUND DURING REVIEW — reshapes the build]

Checked against the live `app/bsn_archivo.html` before planning the diff:

- **`VENUES` already exists** for all 12 active clubs (`{key:[name,
  capacity]}`, line ~1842) and `showTeam()`'s kv-list already renders it
  ("Cancha: *name* · *capacity*"). This is an **extend**, not a build.
- **The rivalry data is already fully computed in `showTeam()`.** `opp` /
  `oppRows` (built from `f.won`/`f.ru` against `champOf`/`ruOf`) is already
  sorted descending by total finals meetings for the "El careo en finales"
  table. `oppRows[0]` **is** the top-rival row — no new computation needed,
  just a second, highlighted render of the row that already exists.
- **A free, already-sourced anecdote source**: the `HOF` array (Salón de la
  Fama legends) tags 4 players `"Arena named for him"` — Mario Morales
  (Guaynabo), Raymond Dalmau (Quebradillas), Juan «Pachín» Vicéns (Ponce),
  Rubén Rodríguez (Bayamón).
- **Corrected in this revision**: the first pass of this spec treated the
  other 7 active clubs as needing a fresh build-time sourcing pass. Wrong —
  the original plan's own "Nickname/lore" column (section 1 below, Wikipedia/
  PlateaPR/press-cited, never dropped) already has real material for 6 of
  those 7 (San Germán, Santurce, Mayagüez, Caguas, Aguada, Carolina/
  Canóvanas). That table is folded into `TEAM_LORE` below instead of being
  re-sourced. **Arecibo is the one genuine gap** — that column is blank for
  them in the original table too, not just missed here.
- **Internal corroboration on the Guaynabo fix**: the `HOF` entry for Mario
  Morales already says, in an unrelated note field, *"The Mets play at the
  Mario Morales Coliseum in Guaynabo."* — the file already knows `VENUES.gua`
  is wrong; it just never got reconciled. Independent of the outside sources
  checked during plan review (El Nuevo Día, Wikipedia).

## [DATA]

### `VENUES` — extend each entry with nickname + opened year (both nullable — PC2: NULL≠0, don't fabricate an unknown)

| key | name (correction marked) | cap | nickname | opened | source |
|---|---|---|---|---|---|
| bay | Coliseo Rubén Rodríguez | 12,000 | "El Rancho Vaquero" | 1988 | Wikipedia, El Vocero |
| pon | Auditorio Juan Pachín Vicéns | 11,000 | "Coliseo de Ponce" | 1972 | Wikipedia |
| sge | Coliseo Arquelio Torres Ramírez | 5,000 | "La Cuna" | 1985 | Wikipedia, PlateaPR |
| san | Coliseo Roberto Clemente | 9,000 | — | 2021 (move) | El Vocero |
| are | Coliseo Manuel «Petaca» Iguina | 12,000 | — | TBD | Wikipedia |
| que | Coliseo Raymond Dalmau | 5,500 | "La Guarida del Pirata" | 2008 | Wikipedia, PlateaPR |
| may | Palacio de Recreación y Deportes | 5,500 | "Sultana del Oeste" | 1981 | Wikipedia |
| cag | Coliseo Roger Mendoza | 3,000 | "La Presión" | TBD | Wikipedia |
| agu | Coliseo Ismael «Chavalillo» Delgado | 7,500 | — | 2010 | Wikipedia, PlateaPR |
| car | Coliseo Carlos Miguel Mangual | 5,500 | — | TBD | Primera Hora (confirmed live) |
| **gua** | **Coliseo Mario «Quijote» Morales** *(was: Fernando «Rube» Hernández, wrong)* | **5,500** *(was 3,500)* | — | 1983 | El Nuevo Día, Wikipedia — **confirmed via web search this session** (the "1983" was already in the original plan's table, just attached there to the correctly-named coliseo — it carries over once the name is fixed) |
| man | Coliseo Juan Aubín «Bincito» Cruz Abreu | 6,500–8,000 (keep app's 8,000 as the upper bound already in use) | — | TBD | PlateaPR |

`TBD` fields ship as `null` and render nothing extra (not "0" or a blank
dash pretending to be data) until sourced — matches how the rest of the
archive already handles a gap.

### `VENUE_NOTES` — new, small, temporal-only map (separate from `VENUES` so the one-off 2026 caveat doesn't force every other entry to carry unused trailing nulls, and is trivial to delete once the Mets move back in 2028)

```
gua: "Los Mets juegan la temporada 2026 en Gurabo mientras el Coliseo Mario
     «Quijote» Morales pasa por una remodelación de $17M; el regreso se
     espera en 2028."
```

### `F.car` — rename to match the confirmed 2025 relocation

`name:"Gigantes de Carolina"` → `"Gigantes de Carolina/Canóvanas"`;
`city:"Carolina"` → `"Carolina/Canóvanas"`. Confirmed official via
[Primera Hora](https://www.primerahora.com/deportes/baloncesto/notas/oficial-gigantes-se-mudan-al-coliseo-carlos-miguel-mangual-de-canovanas/)
and [El Nuevo Día](https://www.elnuevodia.com/deportes/baloncesto/notas/bsn-los-gigantes-de-carolina-oficializan-su-mudanza-a-canovanas-para-la-temporada-2025/).

### `TEAM_LORE` — new, one sourced line per active club

| key | status | anecdote | source |
|---|---|---|---|
| bay | ready | Cinco títulos seguidos, 1971–1975 — la dinastía más larga de la liga. El juego de 1969 contra Río Piedras reunió 17,621 personas, récord de asistencia del BSN. | `bsn_records.csv`, cited in original plan |
| que | ready | Raymond Dalmau y Neftalí Rivera, el «Dynamic Duo» de 1966–69, encendieron la dinastía de los 70 (4 títulos). Dalmau tiene la cancha nombrada en su honor. | `HOF` (Dalmau), plan doc |
| man | ready | El único club activo sin título — el más joven de la liga, y el que todavía se lo debe a su fanaticada. | `F.man.won.length===0`, live-derived, always true |
| gua | ready | Mario «Quijote» Morales, 4× MVP y campeón de anotación en 1980, tiene la cancha del club nombrada en su honor. | `HOF` (Morales) — replaces the dropped lineage claim per decision 5 |
| pon | ready | Juan «Pachín» Vicéns, 4× MVP, tiene el auditorio del club nombrado en su honor — "el Coliseo de Ponce" para la fanaticada. | `HOF` (Vicéns) + original plan's nickname column |
| sge | ready | Conocido como "La Cuna" — y, para su fanaticada, "el hogar del monstruo anaranjado." | original plan, Wikipedia/PlateaPR |
| san | ready | Los Cangrejeros dejaron el histórico Coliseo José Miguel Agrelot por el Coliseo Roberto Clemente, en San Juan, en 2021. | original plan, El Vocero |
| may | ready | Mayagüez es conocida como "la Sultana del Oeste" — el Palacio de Recreación y Deportes ha sido su cancha desde 1981. | original plan, Wikipedia |
| cag | ready | El Coliseo Roger Mendoza es, para la fanaticada criolla, "La Presión." | original plan, Wikipedia |
| agu | ready | El Coliseo Ismael «Chavalillo» Delgado se construyó para los Juegos Centroamericanos y del Caribe de 2010. | original plan, Wikipedia/PlateaPR |
| car | ready | Los Gigantes se mudaron de Carolina a Canóvanas en 2025 tras no llegar a acuerdo con el municipio de Carolina por el uso del Coliseo Guillermo Angulo — hoy juegan como Gigantes de Carolina/Canóvanas en el Coliseo Carlos Miguel Mangual. | original plan + [Primera Hora](https://www.primerahora.com/deportes/baloncesto/notas/oficial-gigantes-se-mudan-al-coliseo-carlos-miguel-mangual-de-canovanas/), confirmed during plan review |
| are | **genuine gap** | — | the original plan's own table has "—" for Arecibo's nickname/lore *and* opened year, not just missed in this revision. Falls back to the live-derived line below unless there's something to add. |

11 of 12 active clubs now have a sourced anecdote drawn entirely from
material already in this doc or the app (`HOF`, the original plan's
nickname/lore column, or this session's own confirmed web search) — no new
sourcing pass needed. Arecibo is the one real gap. Every team — Arecibo
included — also gets a true, always-available fallback line derived live
from `F[key]` (e.g. *"N títulos en M temporadas — el más reciente en Y."*,
or the "sin título" framing for a winless club), so no team ever ships with
an empty anecdote block. Same "flag the gap, don't fake it" rule as
everywhere else in this archive.

## [LAYOUT] — inside the existing `showTeam()`, not a new template

```
.card
  .phero                                    (existing, 8.3b)
    crest
    .phero-body
      h3 name
      .phero-sub  city · founded            (existing)
      .phero-stat  title count + sparkline  (existing)
      .phero-statl "títulos"                (existing)
      .phero-note  computed record line     (existing)
      + .phero-venue  NEW — coliseo line: name, nickname if any,
                      ~capacity (title= tooltip: "capacidad aproximada —
                      varía por fuente y renovación"), opened year if known;
                      VENUE_NOTES[k] appended as a small caveat line if present
      .chips  (2026 record, colour-source)  (existing)
      .kv  dirigente / cancha / números retirados / nota (existing —
           "Cancha" row simplifies since .phero-venue now carries that detail,
           or stays as a compact backup; decide at build time by what reads
           least redundant)
      + .rival  NEW — one line, reusing oppRows[0] already computed above:
                "Mayor rival: [crest] Leones de Ponce — 5 finales (3-2)"
      + .lore   NEW — TEAM_LORE[k] or the live-derived fallback
      campeón / subcampeón note lines        (existing)
  roster chips                               (existing)
  #teamOpp → "El careo en finales" table     (existing, unchanged)
```

Net new CSS is small: a `.phero-venue`/`.rival`/`.lore` line style (reuse
`.phero-note`'s look — `color:var(--ink-2); font-size:var(--fs-2xs)` — no
new visual language invented). No new top-level card, no new builder
function beyond extending `showTeam()` itself.

## [OUT OF SCOPE — this pass]

- Defunct franchises (20 clubs) — decision 7. `showTeam()` keeps working for
  them exactly as today (`VENUES[k]`/`TEAM_LORE[k]` simply return
  `undefined` and the new lines don't render — no regression).
- Caciques de Humacao specifically — decision 6, gated on D-045.
- The equipo/club/franquicia consistency sweep (LANG pass, deferred earlier).

## [ALTERNATIVES_REJECTED]

- **A separate "coliseo strip" card below the masthead** (original plan's
  layout). Rejected — decision 1; `.phero` already carries this class of
  fact, a second nearly-identical block competes with it instead of reading
  as one page.
- **Recomputing rivalry from `bsn_champions_by_season.csv` at build time.**
  Rejected — decision 2, and unnecessary: `showTeam()` already computes the
  live equivalent (`oppRows`) from the app's own `F`/`champOf`/`ruOf`, which
  is guaranteed to match everything else on the page.
- **The Guaynabo 1935-lineage anecdote.** Rejected — decision 5, uncorroborated
  and self-contradicting against `F.san.founded`.

---

## Original plan (superseded above, kept for history)

For review before Claude Code build. Sources are Wikipedia + PlateaPR/Primera
Hora/El Nuevo Día coverage, all fetched this session.

### 1. Coliseo reference (12 active franchises)

| Franchise | Coliseo | Nickname/lore | Opened | Cap. | Source |
|---|---|---|---|---|---|
| Vaqueros de Bayamón | Coliseo Rubén Rodríguez | "El Rancho Vaquero" | 1988 | 12,000 | Wikipedia, El Vocero |
| Leones de Ponce | Auditorio Juan Pachín Vicéns | "Coliseo de Ponce" | 1972 | 11,000 | Wikipedia |
| Atléticos de San Germán | Coliseo Arquelio Torres Ramírez | "La Cuna" / "hogar del monstruo anaranjado" | 1985 | 5,000 | Wikipedia, PlateaPR |
| Cangrejeros de Santurce | Coliseo Roberto Clemente (San Juan) | moved from José Miguel Agrelot | 2021 move | — | El Vocero |
| Capitanes de Arecibo | Coliseo Manuel "Petaca" Iguina | — | — | 10–12,000 | Wikipedia |
| Piratas de Quebradillas | Coliseo Raymond Dalmau | "La Guarida del Pirata" | 2008 | 6,000–7,000 | Wikipedia, PlateaPR |
| Indios de Mayagüez | Palacio de Recreación y Deportes | "Sultana del Oeste" | 1981 | 5,500 | Wikipedia |
| Criollos de Caguas | Coliseo Roger Mendoza | "La Presión" | — | ~3,000 | Wikipedia |
| Santeros de Aguada | Coliseo Ismael "Chavalillo" Delgado | built for 2010 Central American Games | 2010 | 7,500 | Wikipedia, PlateaPR |
| Gigantes de Carolina/Canóvanas | Coliseo Carlos Miguel Mangual | relocated Carolina→Canóvanas 2025 | — | 5,500 | Primera Hora |
| Mets de Guaynabo | Coliseo Mario "Quijote" Morales | named for team legend, 3x champ | 1983 | 5,500 | Wikipedia, PlateaPR |
| Osos de Manatí | Coliseo Juan Aubín "Bincito" Cruz Abreu | named for 40-yr mayor de Manatí | — | 6,500–8,000 | PlateaPR |

### 2. Rivalries (from bsn_champions_by_season.csv — real finals meeting counts)
1. Piratas de Quebradillas vs Vaqueros de Bayamón — 6 finals
2. Atléticos de San Germán vs Cardenales de Río Piedras — 5 finals (Río Piedras defunct 1985)
3. Capitanes de Arecibo vs Leones de Ponce — 5 finals
4. Leones de Ponce vs Vaqueros de Bayamón — 5 finals
5. Cangrejeros de Santurce vs Leones de Ponce — 4 finals

*(Confirmed independently during plan review by recomputing straight from
the CSV — exact match, all 5, same order, same counts.)*

### 3. Anecdotes (from bsn_records.csv)
- Bayamón: 5 straight titles, 1971–1975 dynasty
- 1969 Bayamón–Río Piedras game: 17,621 attendance, still the BSN record
- Caciques de Humacao: 130 pts / 46 in a quarter (2012) — Humacao not in
  current franchises list, flagged — **this is the same open thread as D-045**
- Quebradillas: the Dalmau–Rivera "Dynamic Duo" 1966–69, sparked the 1970s
  dynasty (4 titles)
- Mets de Guaynabo: originally founded 1935 as Cangrejeros de Santurce,
  relocated to Guaynabo 1976 — **dropped, see decision 5**
- Osos de Manatí: only active franchise with 0 titles

### 4. Page layout (top → bottom) — superseded by [LAYOUT] above

### 5. Open items — resolved by [DECISION] above
