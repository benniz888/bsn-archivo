# JUG05_SUMROW_CHECK — are some conflicts a season total against one team's row?

Audit date 2026-09-21. READ-ONLY: no code, CSV or web/ change; this file is the only output (uncommitted).
State: HEAD `155c2c4` (the jug05 relabel), tree clean before this file. Every count was recomputed from the committed
data/clean/player_career_seasons.csv and the three logs in data/interim in this phase (scratch scripts, no
regeneration target). Anything not verified directly is tagged UNVERIFIED. "ficha" = the players source
(`wayback_bsnpr_players`, one row per team); "jug05" = `wayback_bsnpr_jug05`.

[VERDICT]

The hypothesis holds for 13 of the 107 conflicts and for none of the other 94. In 13 cases jug05 has ONE row that
equals the sum of the ficha's rows for that player-season (a player who changed team), and the per-team match paired
that total with one team's partial row: 12 of the 14 new 2006 conflicts and 1 of the 4 real 2005 ones (id 985).
It explains nothing in 2000-2003 (0 of 89). No unflagged jug05 row equals a sum (T3), so nothing is hidden.

[T1] The 14 new 2006 conflicts

    id|player|jug05 row|ficha 2006 rows (team games/points)|sum|jug05 = sum
    81|Sweet Valencia, Andre|SAN GERMAN 31/333|San German 13/126; Coamo 13/136|26/262|NO
    151|Reyes Canales, Angelo|CAGUAS 27/468|Caguas 4/71; Morovis 23/397|27/468|YES
    193|Latimer Rivera, Antonio|COAMO 20/364|San German 8/142; Coamo 12/222|20/364|YES
    284|Escalera Gonzalez, Carlos|BAYAMON 25/446|Coamo 21/392; Bayamon 4/54|25/446|YES
    763|Martinez Arroyo, Freddie|PONCE 25/102|Ponce 20/86; Morovis 5/16|25/102|YES
    777|Burgos Algarin, Gary Joe|HUMACAO 24/56|Humacao 8/17; Coamo 16/39|24/56|YES
    808|Venzen Aloyo, Gilberto|COAMO 24/146|San German 12/47; Coamo 12/99|24/146|YES
    870|Zayas Irizarry, Hector|COAMO 14/43|Caguas 12/43; Coamo 2/0|14/43|YES
    932|Caro Beltran, Ismael|SAN GERMAN 27/302|San German 14/166; Coamo 13/136|27/302|YES
    1066|Roman Rodriguez, Joel|MOROVIS 29/161|Morovis 26/159 (one row)|26/159|NO
    1284|Rodriguez Rodriguez, Joseph|MOROVIS 12/72|Santurce 5/5; Morovis 7/67|12/72|YES
    1462|Allende Ruiz, Luis|SAN GERMAN 9/9|San German 5/9; Coamo 4/0|9/9|YES
    1995|Melendez Huertas, Ricardo|CAGUAS 24/194|Caguas 5/39; Bayamon 19/155|24/194|YES
    2067|Nieves Perez, Roberto|COAMO 25/227|San German 12/87; Coamo 13/140|25/227|YES

12 match the sum on games AND points. The other 2: id 81 (jug05 is 5 games and 71 points above the sum of two
rows; a third stint missing from the ficha is one possible reading, UNVERIFIED) and id 1066 (one team, jug05 3 games
and 2 points above the ficha row; a real difference, cause UNVERIFIED). In every YES case the jug05 team is one of
the ficha's teams, and the fold paired the total with that team's row (the partial one).

[T2] All 107 conflicts

Order of the test: (sum) jug05 equals the sum of the ficha's rows of that player-season, with at least 2 rows;
(partial) otherwise jug05 is smaller in games AND points than the matching same-city ficha row; otherwise (other):
"larger" = jug05 larger in both, "mixed" = equal or opposite on one side. A subset sum (two of three rows) never
occurred.

    season|conflicts|sum|partial|other: jug05 larger in both|other: mixed or equal on one side
    2000|17|0|2|0|15
    2001|51|0|11|15|25
    2002|18|0|3|11|4
    2003|3|0|3|0|0
    2005|4|1|3|0|0
    2006|14|12|0|2|0
    ALL|107|13|22|28|44

The sum pattern explains 0 of the 89 conflicts of 2000-2003. Those are single-team rows that differ in one or both
figures, in both directions; their cause stays open (UNVERIFIED). In 1999-2004 jug05 lists a multi-team season one row
per team, and those rows fold as identical (merged) or stay conflicts; jug05 shows a season total only in the slot
labelled 2005: 1 of 2 multi-team player-seasons of 2005 and 12 of 13 of 2006. The 4 remaining 2005 conflicts: id 985
(jug05 Isabela 32/221 = ficha Isabela 10/87 + Coamo 22/134) is a sum; ids 320, 952 and 1127 are "partial" (id 320 may
be two players, UNVERIFIED).

[T3] Sums that were NOT flagged

    kept jug05 rows (CSV): 351 = 107 conflict rows + 244 others
    of the 244: equal to the sum of 2 or more ficha rows: 0
    of the 244: equal to one ficha row of another city token: 0
    merged pairs (767) whose figures also equal a sum of 2 or more ficha rows: 2 (ids 1442 in 2002 and 1512 in
      2000; in both a second ficha row is 0/0, so the sum equals the single row; they stay merged)

So the 13 sum rows are all in the conflict log, and no other jug05 row is a total in disguise.

[T4] Smallest fix (NOT applied)

Rule: after the per-team fold, a kept jug05 row whose games and points equal the sum of the ficha rows of the same
player-season (at least 2 rows, none with a blank figure, PC2) is a season total: it is folded out of the career CSV
and logged as such, not as a conflict. It never overrides a team row, and it is only tried after the identical-row
fold. One function next to fold_cross_source_career, called by merge_jug05 and by an apply script (same pattern
as apply_jug05_relabel; regeneration stays unsafe, N7).

Predicted counts (simulated in memory on the committed CSV):

    season-total rows folded: 13 (13 players; 2005: 1, 2006: 12); all 13 are conflict rows today
    player_career_seasons.csv: 5,696 -> 5,683 rows
    jug05_career_conflicts.csv: 107 -> 94 rows (71 players); by season 2000: 17, 2001: 51, 2002: 18, 2003: 3,
      2005: 3, 2006: 2
    jug05_career_merged.csv: 767, unchanged
    new log data/interim/jug05_career_season_totals.csv: 13 rows (id, season, jug05 team, games, points, jug05 url,
      the ficha rows summed with their urls)
    trade pairs: 235, unchanged (only jug05 rows leave)

"Totales del archivo": 13 players change and all rise, by 1,057 points and 116 games in all, because a real stint
that was excluded with the conflict is counted again and no total is double counted: 151, 193, 284, 763, 777, 808,
870 (games only), 932, 985, 1284, 1462, 1995 (4,300/455 -> 4,339/460) and 2067. The "2 fuentes" marker and the
"sin N temporadas" note leave those 13 rows. No player's total falls.

Files that change: src/parse_players.py (new function and its call in merge_jug05), a new apply script or a second
step of apply_jug05_relabel, tests (new tests, the pins 107 -> 94), data/clean/player_career_seasons.csv,
data/interim/jug05_career_conflicts.csv and the new log. Web: players/<id>.json for the 13 players (one row fewer
each), index/players.json (career_seasons -1 for those 13), index/data_quality.json, manifest.json (digest; add
the new log to DQ_INTERIM_LOGS if it is published). A deploy purges visitors' cached data once. Needs an owner
decision: D1 (2026-09-20) said "merge only when the stats are identical"; a sum is a different corroboration.

Calidad de datos wording that would need to change (nothing changed now): the strip and lede count "cifras distintas"
(107 -> 94, 74 -> 71 players); the conflicts paragraph says both pages give figures "del mismo jugador, equipo y
temporada", which stays true for the 94; add a short block, neutral and without "error": "En 13 casos la fila de
jug05 es el total de la temporada de un jugador que cambió de equipo y coincide con la suma de las filas por equipo
de la ficha. Se cuenta una vez." The tooltip of the marker and the totals sentence need no change. The spec
(data_quality_view_spec.md, sections 2, 5 and 7) needs the new counts. Until the fix, 12 of the 14 conflicts of 2006 in
the view are this pattern, and their players' totals leave out a real stint.

[T5] Verification

Recomputed from the files in this phase: 14 and 107 conflicts (by season above), 351 jug05 rows in the CSV, 767
merged pairs, the 13 sum rows and the simulated counts. The simulation used the same totals rule as the page (both
rows of a conflict out of the sum); exact page numbers were not re-read in a browser (UNVERIFIED). UNVERIFIED: the
cause of the 2000-2003 conflicts, of ids 81 and 1066, and why jug05 shows a total only in the slot labelled 2005.
