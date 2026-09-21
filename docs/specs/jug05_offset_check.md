# JUG05_OFFSET_CHECK — is the 2005 "offset" a source label, a parser bug, or something else?

Audit date 2026-09-21. READ-ONLY: no code, CSV or web/ change; this file is the only output (uncommitted).
State: HEAD `e661781`, tree clean before this file. Every count was recomputed from the committed CSVs and the raw
captures in data/raw/players/jug05 in this phase, with scratch scripts (none run `make parse-players`).
Anything not verified directly is tagged UNVERIFIED. "ficha" = the jugador.asp profile page (source
`wayback_bsnpr_players`); "jug05" = jug05.asp (source `wayback_bsnpr_jug05`).

[VERDICT]

The offset is (a) and (c), not (b). jug05 has ONE slot for the newest season, labelled "2005" on every capture.
Until the capture of 2006-02-24 that slot holds the figures the ficha files under 2005. From the capture of
2006-05-28 on, the same slot holds the figures the ficha files under 2006. The source overwrote the slot in place
and kept the label. parse_jug05 copies the page's label as written, so it derives nothing wrong; the pipeline has no
notion that this one label is relative to the capture date (c). Which label matches the real calendar is UNVERIFIED
(the repo has no independent 2005 or 2006 season data); the ficha is the only source that lists both seasons.

[T1] How parse_jug05 derives a row's season (src/parse_players.py)

    :312  _J5_ROW = re.compile(r"(\d{4})\s+([A-ZÑÁÉÍÓÚ.\- ]+?)\s+(?=\d)(.+?)(?=\s+\d{4}\s+[A-ZÑ]|\Z)", re.S)
    :334  for r in _J5_ROW.finditer(cm.group(1)):
    :335      yr = int(r.group(1))
    :348  career.append((yr, team, jj, pts))
    :596-601  for yr, team, jj, pts in j["career"]: ... "season": yr   (merge_jug05)

The season is the first 4-digit token of each row of the "Año Equipo 3pi ... JJ PTS %" table: the page's own Año
column, copied verbatim. It is not read from a heading, a URL parameter or the capture date (meta["wayback_timestamp"]
is used only to name the source URL). The only guard is 1929 <= yr <= 2030 (:336). One more step matters: :358-365
collapses several captures of one player (key: norm_key(name) + birth date) and keeps the capture with the most career
rows, so which capture supplies the "2005" row depends on that tie-break.

[T2] Raw captures: what the page shows and what the parser assigned

The page shows no other season label for its rows. The footer says "© 2005" on all 586 parsed captures; the nav
says "Intinerario 2006 ... Campamento 2006" from 2006-02 on. Label = the Año cell. Parser label = the same number.
They agree in every case below; the question is what the numbers under the label are.

    file|capture|player (id)|page row|parser season|ficha 2004 / 2005 / 2006 (team games/points)
    5PVKX4UC26|2005-09-03|Rivera, Carlos (320)|2005 GUAYAMA 31/113|2005|- / Guayama 31/113 / Ponce 18/22
    BSIVXSY734|2006-02-24|Travieso, Carmelo (344)|2005 SANTURCE 22/141|2005|no ficha rows
    3ISM74MFTT|2006-06-18|Colon, Nelson (990016)|2005 PONCE 0/0|2005|no ficha rows (jug05-only id)
    27MJHISNAL|2006-12-15|Villegas, Sammy (2145)|2005 SANTURCE 2/0|2005|- / - / Santurce 2/0
    3RKPU6AEAN|2007-04-04|Ortiz, Andres (86)|2005 COAMO 13/40|2005|- / - / Coamo 13/40
    3CSERW5D5M|2005-04-18|Ayuso, Larry (574)|2001 SAN GERMAN 26/617|2001|2001 ficha San German 26/580
    2IA3M6ZKRB|2006-12-08|Pagan, Wilfredo (2290)|2001 MOROVIS 23/445|2001|2001 ficha Morovis 23/445
    3AHY4M6VPG|2006-12-06|Colon, Angel (136)|2004 CAYEY 12/159|2004|2004 ficha Cayey 12/159 (equal)

One player, five captures (Dalmau, Raymond, id 1970; ficha 2005 Santurce 27/392, ficha 2006 Santurce 22/264):

    2006-02-24 page "2005" row SANTURCE 27/392  (= ficha 2005)
    2006-05-28 page "2005" row SANTURCE 22/264  (= ficha 2006)
    2006-10-07, 2006-12-14, 2007-04-04: the same 22/264

Across the raw captures, 21 players have a "2005" row both before 2006-03 and after 2006-05; the row differs for all
21 (for example Rosario, Jose: GUAYAMA 32/279, later SANTURCE 26/189; Falcon, Alex: SANTURCE 31/328, later 15/172).
Boundary (all 586 parsed captures with a "2005" row and a mapped player):

    2006-02-24|8 rows equal ficha 2005, 2 with no ficha row, 0 equal ficha 2006
    2006-05-28|12 equal ficha 2006, 1 differs, 1 no ficha row, 0 equal ficha 2005
    2006-06-18|22 equal ficha 2006, 1 differs, 5 no ficha row
    2006-07-13|6 equal ficha 2006

The flip is somewhere between 2006-02-25 and 2006-05-27; the exact day is UNVERIFIED. No capture with a "2005" row
falls in that window, so every cutoff in it gives the same rows. Labels 2003 and 2004 do not move: they match the
ficha at s in every capture month from 2005-04 to 2007-04 (T3). jug05 has no row for the season the ficha calls
2005 in any post-flip capture: the slot was overwritten, not extended.

[T3] Offset test, all 1,118 jug05 rows against the players source

Rows = jug05 rows in player_career_seasons.csv (451) plus the merged log (667) = 1,118. Eligible = the same player has
a players-source row with the same city token (the fold key, parse_players.city_token) in s-1, s or s+1. m_s, m_s+1,
m_s-1 = exact games AND points equal to that player's same-city players row in season s, s+1, s-1.

    season|jug05 rows|eligible|m_s|m_s+1|m_s-1|no match
    1980-1999 (20 seasons, each 100% at s)|459|342|342|0|0|0
    2000|80|65|48|0|0|17
    2001|92|76|25|0|0|51
    2002|103|87|68|0|0|19
    2003|110|89|85|0|0|4
    2004|116|95|95|0|0|0
    2005|158|122|4|100|0|18
    ALL|1118|876|667|100|0|109

Only 2005 shows an offset, always in one direction: the jug05 "2005" row equals the ficha's 2006 row (+1) in 100 of
122 eligible rows and the ficha's 2005 row in 4. No season has an s-1 match. No row matches both s and s+1.
The 4 rows at s are all from captures before 2006-03; the 100 at s+1 are all from captures from 2006-05.

By capture phase, the 158 rows labelled 2005 (kind = how the fold classified them today):

    phase|kind|relation to the ficha|rows
    capture <= 2006-02|merged|equals ficha 2005|4
    capture <= 2006-02|conflict|ficha 2005 exists, differs|4
    capture <= 2006-02|no twin|no same-team ficha row 2005/2006|5
    capture >= 2006-05|conflict|equals ficha 2006|33
    capture >= 2006-05|no twin|equals ficha 2006|67
    capture >= 2006-05|no twin|same-team ficha row exists, differs|14
    capture >= 2006-05|no twin|no same-team ficha row 2005/2006|31

145 published "2005" rows come from captures after the flip; 100 of them are verified equal to a ficha 2006 row. The
other 45 (14 differ from the ficha 2006 row, 31 have no ficha row) follow the same capture-date rule but cannot be
checked against a ficha row: UNVERIFIED. The 4 pre-flip conflicts are ordinary value differences (Sept-2005
captures: ids 320, 952, 985, 1127); id 320's jug05 line (4/13) is next to another jug05 page for "Rivera, Carlos"
(31/113) that matches the ficha, so two players may share that id: UNVERIFIED, not part of this check.

[T4] Exposure beyond the flagged conflicts

4a. Hidden offset duplicates: jug05 rows with no same-player, same-city players row in their own season (all 325
    non-conflict, non-merged jug05 rows qualify) whose games+points equal that player's players row in s+1 or s-1:
      67 rows, 67 players, all season 2005, all +1 (the players row is in 2006). None in s-1. None in any other season.
      Same result for a players row of ANY team: 67. None are 0/0 rows. Together 9,509 points and 1,175 games.
      These 67 are counted in "Totales del archivo" today, so those players' 2006 season is counted twice.
    Examples (id|player|jug05 team|games/points|the players row is in 2006):
      35|Arroyo Bermudez, Alberto C.|GUAYNABO|20/21
      49|Rivera Cruz, Alexander|CAGUAS|7/6
      86|Ortiz Colon, Andres|COAMO|13/40
      87|Rodriguez Fernandez, Andres|CAGUAS|20/131
      93|Liriano Lugo, Aneuris|GUAYAMA|22/50
      120|De Jesus Velazquez, Angel|CAGUAS|26/246
      121|Hernandez Miranda, Angel a.|MOROVIS|8/5
      136|Colon Colon, Angel Luis|ARECIBO|13/8
      143|Lopez Ortiz, Angel Miguel|COAMO|10/6
      158|Guzman Hernaiz, Ansel M|HUMACAO|26/314
4b. Merged pairs (667): 0 have an identical same-city players row in s+1, 0 in s-1 (0 for any team, 0 excluding
    0/0 rows). The 4 merged 2005 pairs are pre-flip captures equal to the ficha's 2005 row. No coincidence risk.
4c. Seasons 2000-2003 (17, 51, 18, 3 conflicts): no offset. 0 of 89 conflict rows match any players row of the same
    player in s+1, s-1, s+2 or s-2. Season 2005: 33 of 37 match s+1, none the others. 2004 has 0 conflicts because
    all 95 of its jug05 rows that have a players twin are identical to it and the other 21 have no twin; nothing
    differs. Why 2000-2003 differ is not answered here (UNVERIFIED). One independent pointer, 2001 only: the Tier-2
    season stats (player_season_stats_2001_2004.csv, captured 2001-07 to 2001-10, so after the season) equal the
    ficha row in 93 of 112 comparable ficha rows, and back the ficha side in 30 of the 39 comparable 2001
    conflicts, the jug05 side in 2 (7 neither). For 2002 and 2003 the Tier-2 captures are from April-June
    (probably not final), so they say nothing (UNVERIFIED).

[T5] Cause, smallest fix, effect (NOT applied)

Cause: the source overwrote the newest-season slot of jug05 in place and kept its label "2005". parse_jug05 is
faithful to the page. What is missing is a capture-date rule.

Smallest fix: relabel the row labelled 2005 to 2006 when the capture is on or after the flip (any cutoff between
2006-02-25 and 2006-05-27 gives the same rows), then run the existing fold. Two parts, because regeneration is unsafe
(N7): (1) src/parse_players.py parse_jug05: apply the rule with meta["wayback_timestamp"], so a future regeneration is
right; (2) a small apply script in the style of apply_career_dedup / apply_identity_decisions that does the same to
the committed player_career_seasons.csv (the row's source_url carries the capture timestamp), re-runs
fold_cross_source_career, and rewrites the two logs. Simulated in memory on the committed CSV:

    rows relabelled 2005 -> 2006: 145 (33 conflict rows + 112 rows with no twin today)
    player_career_seasons.csv: 5,796 -> 5,696 rows (100 jug05 rows fold into the identical ficha 2006 row)
    jug05_career_merged.csv: 667 -> 767 rows (100 players; 33 were conflicts, 67 hidden duplicates)
    jug05_career_conflicts.csv: 126 -> 107 rows (2005: 37 -> 4; 2006: 0 -> 14; 2000-2003 unchanged 17/51/18/3)
    jug05 rows left as 2006 with no twin: 45 (14 of them are the new 2006 conflicts)
    the 4 real 2005 conflicts and the 4 real 2005 merged pairs stay as they are

Files that change: src/parse_players.py, the new apply script and its tests; data/clean/player_career_seasons.csv;
data/interim/jug05_career_merged.csv and jug05_career_conflicts.csv. Then web/: players/<id>.json for the 145
players whose rows change (100 lose a row, 45 change a season label), index/players.json (career_seasons -1 for the
100), index/data_quality.json (126 -> 107 conflicts, 667 -> 767 merged pairs, the by-season counts), manifest.json
(the digest changes: the career CSV and both logs are digest inputs). A deploy purges visitors' cached data once.
Test pins that would move: test_career_dedup (667 / 126) and test_data_quality (126, 667, 37 in 2005).

Effect on the totals line (from the CSVs; the page also adds synthesized rows, so exact page numbers are UNVERIFIED):
114 players change. 33 go up, by 8,125 points in all, because their real 2005 ficha row is no longer excluded
(Alvin Cruz, 74: 1,985 points / 362 games now, 2,119 / 373 after). 79 go down, by 13,687 points in all, because a
duplicate 2006 season stops being counted (67 players) or a new 2006 conflict excludes rows (rest; breakdown
UNVERIFIED). The
"2 fuentes" marker disappears from the 33 and appears on 14 rows of 2006.

If the owner does not want the fix yet (cause (a) only), the Calidad de datos view should say so. Suggested text for
the conflicts block, neutral, no "error": "En 2005, 33 de las 37 diferencias coinciden con la fila de 2006 de la misma
ficha. jug05 rotula «2005» la última temporada de su página y la reescribió entre febrero y mayo de 2006, así
que es probable que sea una diferencia de rotulado y no de cifras. No se ha resuelto."
The current sentence "dos páginas dan cifras distintas para este equipo y temporada" is not accurate for those
33 rows, and the 67 hidden duplicates are not flagged at all.

[T6] Verification

Every count above was recomputed in this phase from the committed CSVs and the raw captures: 600 raw jug05 files, 586
parsed as player pages (200 distinct players by name+birth date, 161 with more than one capture), 1,118 jug05 rows,
5,345 players-source rows. The parser replica used for the raw pass copies the regexes and the row loop of
parse_jug05 (:311-348) unchanged. UNVERIFIED: the exact flip date; the real-calendar meaning of the two labels; the
45 post-flip rows with no comparable ficha row; whether the 14 new 2006 conflicts are real differences; the id 320
identity; the cause of the 2000-2003 conflicts; the exact page-level totals after a fix.
