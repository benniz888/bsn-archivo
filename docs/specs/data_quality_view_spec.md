# Data-quality view spec: Calidad de datos (`#archivo/calidad`)

Status: live since 64cc605 (2026-09-21). Counts below are after the jug05 relabel (section 7).

## 1. What it is

A public sub-view under Archivo (menu column "El estado del archivo") for readers such as a league contact who
know the same two problems: one person under two ids, and two pages giving different stats for the same season.
It shows where the archive's sources disagree and what was decided about each case. It never picks a figure.

## 2. What is published (recorded facts only)

- Stat conflicts (94 rows, 71 players; 126 and 80 before section 7, 107 and 74 before section 8):
  `data/interim/jug05_career_conflicts.csv`; a table with both figures.
- Merged identical pairs (767, 130 players; 667 and 105 before the relabel): `data/interim/jug05_career_merged.csv`;
  counts, by season.
- Dropped rows on merge (4): `data/interim/player_merge_dropped_rows.csv`; a count.
- Identity decisions (4): `data/clean/player_identity_decisions.csv`; the Spanish `evidence_es` text.
- Open birth-date conflicts (5): `data/interim/jugador05_dob_conflicts.csv`; a table, values as recorded.
- Birth-date corrections (10): `data/interim/player_dob_overrides.csv`; a count with its basis.
- Foreign rows (5, 4 players): `data/interim/jug05_foreign_rows.csv`; the rows and their evidence (section 9).

Not published: the stub twins, the heuristic same-person / different-people classes (they over-link; they are
not decisions), and any Wikipedia claim or URL (project.md L2). The English `evidence` column keeps its
attribution in the decisions CSV; the public text is the new `evidence_es` column.

## 3. Data shape: `web/data/index/data_quality.json` (about 88 KB, 13.3 KB gzipped)

`schema_version`, `counts`, `conflicts`, `decisions`, `dob_open`, `season_totals`, `relabeled`, `foreign_rows`.
A conflict has `id`, `name`, `season`,
`franchise_id`, `a` (the jugador.asp row: team, games, points, Internet Archive url), `b` (the jug05.asp row,
same fields) and `b_retrieved_at`. `build_data_quality()` matches each side to exactly one `career[]` row of the
player's file and stops the build if it cannot. It changes no player, season or game file.

Digest: `_source_digest` now resolves each input in `data/clean`, then `app/`, then `data/interim`. The eight interim
logs (those of sections 7, 8 and 9 included) are digest inputs, so returning visitors purge their cached data once.
`counts.data_quality` is 94; `counts.season_totals` is 13 and `counts.relabeled` is 145.

## 4. The view

Lede (fixed): "Dónde las fuentes no coinciden y qué hicimos con cada caso. El archivo muestra las dos cifras; no
escoge una a ojo." Then: four counts; the conflicts table (four columns: player and team, year, ficha JJ / PTS,
jug05 JJ / PTS; sort, name and season filters, CSV with ids and capture links); the decision cards; the
birth-date table (values as recorded, "formato M/D/AAAA", no month names) and the count of corrections with
their basis; "Cómo decidimos" (never merge on a name alone; show both figures, do not average; a merge needs
evidence and is logged with who and when); two short notes under the conflicts paragraph (section 8). The word
"error" is never used. The file is fetched only when the view
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

## 8. Season totals folded (2026-09-21, owner-approved)

Finding (docs/specs/jug05_sumrow_check.md). In the slot labelled 2005 jug05 mostly shows ONE row for the whole season
of a player who changed team, while the ficha has one row per team; the per-team fold paired that total with one
team's partial row and reported a conflict. 13 of the 107 conflicts left after section 7 were that: 12 of 2006 and
1 of 2005 (id 985); none in 2000-2003 (0 of 89).

Rule. `parse_players.fold_season_totals`: a jug05 row whose games AND points both equal the sum of the players-source
rows of the same player-season (two or more rows, no blank figure) is folded out of the career CSV and logged in
`data/interim/jug05_season_totals.csv` (id, season, jug05 team, games, points, source url, the per-team rows and their
sum); the per-team rows stay. It never folds a row equal to a single team row, so the 2 merged pairs whose second
ficha row is 0/0 (ids 1442 and 1512) stay merged. Order: relabel (section 7), season totals, per-team fold.
`src/apply_jug05_season_totals.py` (--check, idempotent) applies it to the committed CSV; merge_jug05 calls it too.

Counts. 13 rows folded (13 players); career CSV 5,696 -> 5,683; conflicts 107 -> 94 (71 players; 2005: 3, 2006: 2);
merged 767 and trade pairs 235 unchanged. 13 players' totals rise by 1,057 points and 116 games in all (player 1995:
4,300 / 455 -> 4,339 / 460); the "2 fuentes" marker leaves those 13 rows. ids 81 and 1066 and the 2000-2003 conflicts
stay conflicts.

The view. Counts in the strip and the filters follow the file (94). Two short notes sit under the conflicts
paragraph, driven by counts.season_totals and counts.relabeled:
    "En 13 casos la fila de jug05 es el total de la temporada de un jugador que cambió de equipo. El archivo conserva
    las filas por equipo y registra el total como corroboración."
    "En las capturas de jug05 a partir de mayo de 2006, la temporada más reciente conserva la etiqueta 2005. En 100 de
    145 filas las cifras coinciden con la temporada 2006 de la ficha del jugador. Reasignamos las 145 a 2006 y
    publicamos el registro."
The registry is published in data_quality.json (`season_totals` with 13 rows, `relabeled` with 145 rows). The wording
"a partir de" (not "posteriores a") is because 3 relabelled rows come from captures of 2006-05-28, in May. The 100
is the relabelled rows whose games and points equal a ficha 2006 row of the same player (checked from the files; it
equals the 100 folded into the merged log); it is written in the note, so a test pins it.

Open. ids 81 (jug05 5 games and 71 points above the sum of two rows) and 1066 (one team, 3 games and 2 points above)
stay conflicts, cause UNVERIFIED. The causes of the 2000-2003 conflicts (89) are UNVERIFIED. 45 relabelled rows have no
ficha 2006 twin (of them 12 are now season totals): UNVERIFIED against the ficha. The exact flip day and the real
calendar meaning of the labels are UNVERIFIED. Id 320 may be two players. A jug05 page can carry another player's line
in the slot (Carmona, Abel, id 4, shows Alvin Cruz's BAYAMON 24/211): found while reading the registry, not fixed.

## 9. Foreign rows dropped (2026-09-21, owner-approved)

Finding (docs/specs/foreign_slot_check.md). A jug05 page can show ANOTHER player's line: the slot row follows the `r`
URL parameter while the name and history come from another record. Found by lines shared between different players'
captures: 4 lines in the newest-season slot (8 players, 11 captures, all of 2006-06-18 to 2006-12-12) and 3 rows on one
page in the 2001 block. Shared lines also occur by chance, so nothing is detected automatically.

Rule. The owner decided that 5 published rows rest on another player's line: id 4 (2006 BAYAMON 24/211), id 313
(2006 GUAYAMA 9/6), id 1208 (2006 GUAYNABO 9/43) and id 49 (2001 COAMO 11/18 and 2001 PONCE 3/0). They are listed
by hand, with per-row evidence, in `data/interim/jug05_foreign_lines.csv`; `parse_players.drop_foreign_rows` drops
them (after the relabel, before the season totals and the fold), `src/apply_jug05_foreign_rows.py` (--check,
idempotent) applies it to the committed CSV, and every dropped row is logged with its evidence in
`data/interim/jug05_foreign_rows.csv`, a digest input. Class b (Cruz 74, Santiago Ricardo 2000: the owners) and
class c (Allen 1912, Saez 990032: no evidence either way) stay, and so do all other rows of the 4 players.

Counts. 5 rows removed; career CSV 5,683 -> 5,678; conflicts 94 and merged 767 unchanged; trade pairs 235 -> 233 (1208
in 2006, 49 in 2001). 4 player files change (4, 313, 1208, 49); ids 4 and 313 lose their 2006 season and 313 has no
career rows left. The 4 players' totals fall by 278 points and 56 games in all (id 4: 211 / 24, id 313: 6 / 9, id 1208:
43 / 9, id 49: 18 / 14). `counts.foreign_rows` is 5 and `foreign_rows` holds the rows (id, name, season, team, games,
points, owner, evidence in Spanish, capture date, url).

The view. One more note under the relabel note, driven by the count and the rows:
    "En 5 filas de 4 jugadores, una página de jug05 mostraba la línea de otro jugador. Las quitamos de la ficha y
    de los totales y publicamos el registro. No podemos detectar los casos cuyo dueño no tiene captura."

Open. The mechanism (why a page mixes two players) is UNCLEAR. Cases whose owner has no capture cannot be seen by this
method: extent UNVERIFIED. The 31 unchecked relabelled rows with no twin (3 were these; 2 are class c, 26 have no
evidence). 5 minted ids (990007, 990019, 990023, 990024, 990033) carry the same rows as ficha ids (out of scope). The
exact flip day and id 320 (may be two players) stay open.

## 10. Cayey mapped (J16b, 2026-09-21): counts that moved

"Toritos, Cayey" and "CAYEY" now resolve to `toritos_cayey` (city map and `reconcile.py`). No data_quality.json field
changes. The 19 blank `franchise_id` cells of the merged log now carry it (0 blank). The trade pairs of section 9 go
from 233 to 241: 9 player-seasons now show two franchises with Cayey, one of them already a pair; (990024, 2003) is
the minted duplicate of id 763 and would leave the count if that duplicate is merged. The test pins follow.

