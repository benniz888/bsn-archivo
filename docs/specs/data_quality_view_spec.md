# Data-quality view spec: Calidad de datos (`#archivo/calidad`)

Status: live since 64cc605 (2026-09-21). Counts below are after the jug05 relabel (section 7).

## 1. What it is

A public sub-view under Archivo (menu column "El estado del archivo") for readers such as a league contact who
know the same two problems: one person under two ids, and two pages giving different stats for the same season.
It shows where the archive's sources disagree and what was decided about each case. It never picks a figure.

## 2. What is published (recorded facts only)

- Stat conflicts (107 rows, 74 players; 126 and 80 before the relabel): `data/interim/jug05_career_conflicts.csv`;
  a table with both figures.
- Merged identical pairs (767, 130 players; 667 and 105 before the relabel): `data/interim/jug05_career_merged.csv`;
  counts, by season.
- Dropped rows on merge (4): `data/interim/player_merge_dropped_rows.csv`; a count.
- Identity decisions (4): `data/clean/player_identity_decisions.csv`; the Spanish `evidence_es` text.
- Open birth-date conflicts (5): `data/interim/jugador05_dob_conflicts.csv`; a table, values as recorded.
- Birth-date corrections (10): `data/interim/player_dob_overrides.csv`; a count with its basis.

Not published: the stub twins, the heuristic same-person / different-people classes (they over-link; they are
not decisions), and any Wikipedia claim or URL (project.md L2). The English `evidence` column keeps its
attribution in the decisions CSV; the public text is the new `evidence_es` column.

## 3. Data shape: `web/data/index/data_quality.json` (about 52 KB, 7.9 KB gzipped)

`schema_version`, `counts`, `conflicts`, `decisions`, `dob_open`. A conflict has `id`, `name`, `season`,
`franchise_id`, `a` (the jugador.asp row: team, games, points, Internet Archive url), `b` (the jug05.asp row,
same fields) and `b_retrieved_at`. `build_data_quality()` matches each side to exactly one `career[]` row of the
player's file and stops the build if it cannot. It changes no player, season or game file.

Digest: `_source_digest` now resolves each input in `data/clean`, then `app/`, then `data/interim`. The five interim
logs are digest inputs, so returning visitors purge their cached data once. `counts.data_quality` is 107.

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
unchanged. Alvin Cruz (74): 2,330 pts / 397 games became 1,985 / 362 while his 2005 row was a conflict, and
2,119 / 373 after the relabel of section 7, when it stopped being one.

## 6. Rulings and limits

1. The totals line is the only place that sums career rows; leaders and compare use the baked Wikipedia table.
2. Only recorded decisions and logs are published. 3. Public decision text is Spanish, from `evidence_es`.
4. Five open birth dates are shown as recorded; the 10 corrections are a count. 5. Wording as in section 4.
Known and unchanged: the season card of a flagged season shows only one of its two rows; the career table's
PTS column is clipped at 390 px for long team names (existing); `buildSources()` still says Dalmau is the only
self-contradicting figure.

## 7. The 2005 label offset: closed by the jug05 relabel (2026-09-21)

Mechanism. jug05.asp keeps ONE slot for the newest season and labels it "2005" on every capture. The source
overwrote the slot in place between the captures of 2006-02-24 and 2006-05-28: before, it holds the figures the
ficha files under 2005; after, the ones the ficha files under 2006. 33 of the 37 conflicts of 2005 were that
label, not different figures, and 67 more rows were the same season counted twice and flagged by nothing.
Detail and evidence: docs/specs/jug05_offset_check.md.

Fix. `parse_players.jug05_season` files a row labelled 2005 under 2006 when its capture is on or after 2006-05-01
(any cutoff between the two captures gives the same rows; the only captures between them, of 2006-04-27, have no
2005 row). `parse_jug05` calls it, and `src/apply_jug05_relabel.py` applies it to the committed career CSV (the capture
date is the timestamp in each row's source_url), then runs the existing fold. Every relabelled row is logged in
`data/interim/jug05_relabeled_rows.csv` (id, old and new season, capture date, source_url, team, games, points).

Counts. 145 rows relabelled; 100 were identical to the ficha's 2006 row and folded (career CSV 5,796 -> 5,696);
merged pairs 667 -> 767 (130 players); conflicts 126 -> 107 (74 players): 2005 37 -> 4, 2006 0 -> 14, the rest
unchanged. Trade pairs 276 -> 235 (42 pairs of 2005 were the mislabel; 1 came, player 1208 in 2006).
On the pages, 114 players' totals change (33 up, 79 down, 2 with equal points and different games; net -5,562
points, -824 games); the "2 fuentes" marker leaves the 33 false alarms and appears on 14 rows of 2006.

Open. The exact flip day (between 2006-02-24 and 2006-05-28) is UNVERIFIED. Which label matches the real calendar is
UNVERIFIED. 45 relabelled rows have no ficha 2006 twin that could confirm them (14 conflicts, 31 with no ficha row).
The 14 new 2006 conflicts are not resolved and no cause is published: 13 of their jug05 captures are dated 2006-09 or
later and 1 is 2006-06-18 (the end of the 2006 season is not in the repo, UNVERIFIED); in 12 of them the jug05 row
equals the sum of the ficha's two 2006 rows of a player who changed team. Id 320 may be two players (UNVERIFIED).
