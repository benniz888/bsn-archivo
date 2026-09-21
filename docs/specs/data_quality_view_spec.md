# Data-quality view spec: Calidad de datos (`#archivo/calidad`)

Status: built in PHASE_DQ_VIEW_APPLY, staged, not committed. Owner rulings of 2026-09-21 are in section 6.

## 1. What it is

A public sub-view under Archivo (menu column "El estado del archivo") for readers such as a league contact who
know the same two problems: one person under two ids, and two pages giving different stats for the same season.
It shows where the archive's sources disagree and what was decided about each case. It never picks a figure.

## 2. What is published (recorded facts only)

- Stat conflicts (126 rows, 80 players): `data/interim/jug05_career_conflicts.csv`; a table with both figures.
- Merged identical pairs (667, 105 players): `data/interim/jug05_career_merged.csv`; counts, by season.
- Dropped rows on merge (4): `data/interim/player_merge_dropped_rows.csv`; a count.
- Identity decisions (4): `data/clean/player_identity_decisions.csv`; the Spanish `evidence_es` text.
- Open birth-date conflicts (5): `data/interim/jugador05_dob_conflicts.csv`; a table, values as recorded.
- Birth-date corrections (10): `data/interim/player_dob_overrides.csv`; a count with its basis.

Not published: the stub twins, the heuristic same-person / different-people classes (they over-link; they are
not decisions), and any Wikipedia claim or URL (project.md L2). The English `evidence` column keeps its
attribution in the decisions CSV; the public text is the new `evidence_es` column.

## 3. Data shape: `web/data/index/data_quality.json` (about 61 KB, 8.7 KB gzipped)

`schema_version`, `counts`, `conflicts`, `decisions`, `dob_open`. A conflict has `id`, `name`, `season`,
`franchise_id`, `a` (the jugador.asp row: team, games, points, Internet Archive url), `b` (the jug05.asp row,
same fields) and `b_retrieved_at`. `build_data_quality()` matches each side to exactly one `career[]` row of the
player's file and stops the build if it cannot. It changes no player, season or game file.

Digest: `_source_digest` now resolves each input in `data/clean`, then `app/`, then `data/interim`. The five interim
logs are digest inputs, so returning visitors purge their cached data once. `counts.data_quality` is 126.

## 4. The view

Lede (fixed): "Dónde las fuentes no coinciden y qué hicimos con cada caso. El archivo muestra las dos cifras; no
escoge una a ojo." Then: four counts; the conflicts table (four columns: player and team, year, ficha JJ / PTS,
jug05 JJ / PTS; sort, name and season filters, CSV with ids and capture links); the decision cards; the
birth-date table (values as recorded, "formato M/D/AAAA", no month names) and the count of corrections with
their basis; "Cómo decidimos" (never merge on a name alone; show both figures, do not average; a merge needs
evidence and is logged with who and when). The word "error" is never used. The file is fetched only when the view
opens or a player page loads; if it cannot be fetched the player page is unchanged.

## 5. Player pages

A career row that belongs to a conflict carries a "2 fuentes" tag (link to the view, tooltip with both figures).
Both rows of a conflicted team-season stay in the table and stay out of "Totales del archivo", and the line says
so: "Totales sin N temporadas con fuentes en conflicto (ver Calidad de datos)". Players without conflicts are
unchanged. Alvin Cruz (74): 2,330 pts / 397 games become 1,985 / 362.

## 6. Rulings and limits

1. The totals line is the only place that sums career rows; leaders and compare use the baked Wikipedia table.
2. Only recorded decisions and logs are published. 3. Public decision text is Spanish, from `evidence_es`.
4. Five open birth dates are shown as recorded; the 10 corrections are a count. 5. Wording as in section 4.
Known and unchanged: the season card of a flagged season shows only one of its two rows; the career table's
PTS column is clipped at 390 px for long team names (existing); `buildSources()` still says Dalmau is the only
self-contradicting figure.
