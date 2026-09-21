# FOREIGN_SLOT_CHECK — jug05 pages that show another player's line

Audit date 2026-09-21. READ-ONLY: no code, CSV or web/ change; this file is the only output (uncommitted).
State: HEAD `baf9be0`, tree clean before this file. Every count was recomputed in this phase from the 600 raw jug05
captures (586 parse as player pages), data/clean/player_career_seasons.csv, the interim logs and web/data (scratch
scripts, no regeneration target). Anything not verified directly is tagged UNVERIFIED. "ficha" = the jugador.asp
players source; "slot" = the newest-season row of a jug05 page, labelled 2005; "line" = (team, games, points).

[VERDICT]

A jug05 page can show another player's line. It is rare: 4 lines in the slot (8 players, 11 captures) and 1 page
with 3 foreign rows in the 2001 block. 5 published rows rest on such a line (ids 4, 313, 1208 and 49); they add 278
points and 56 games to 4 players' "Totales del archivo" and make two of the 235 trade pairs (1208 and 49). No other
kind of row is affected by what the data can show, but a foreign line whose owner has no capture cannot be seen
this way (UNVERIFIED extent). The mechanism is page-level and tied to the `r` URL parameter; why the page mixes two
players is UNCLEAR.

[T1] Lines that appear in the slot of two or more different players' captures

Method: for every capture the rows labelled 2005 (both rows of a two-team slot count), as (team, games, points);
players = same normalised name, split by birth date only when two dates are given (197 players, 193 distinct slot
lines). 5 lines are shared by two or more players; 0 of them are 0/0. One is not a leak: Martinez, Freddie
(PONCE 25/102) is one person under two birth-date spellings (4/10/1976 and 4/10/1978), same career rows and same `r`.

    line|players|captures|capture dates
    BAYAMON 24/211|Carmona, Abel; Cruz, Alvin|3|2006-06-18, 2006-09-17, 2006-11-19
    GUAYNABO 9/43|Allen, Ramel; Ayala, Jose|2|2006-10-06, 2006-12-06
    GUAYAMA 9/6|Santiago, Carlos; Santiago, Ricardo|3|2006-10-09, 2006-11-19, 2006-12-12
    HUMACAO 4/8|Babilonia, Luis; Saez, Joel|3|2006-08-29, 2006-10-10, 2006-12-06
    total: 4 lines, 8 players, 11 captures

Crawl windows (capture days grouped by gaps of more than 25 days; pages in brackets): W0 2005-04-09..05-07 [89],
W1 2005-08-19..10-01 [47], W2 2006-02-24 [11], W3 2006-04-27 [2], W4 2006-05-28..07-13 [58], W5 2006-08-25..10-10
[87], W6 2006-11-19..12-16 [191], W7 2007-02-23..24 [31], W8 2007-03-28..04-04 [70]. All 11 captures are after the
slot flip: W4 1 (Carmona 06-18), W5 5, W6 5. No shared line occurs in W0-W3 or W7-W8.
Outside the slot, 4 lines of 1,015 (labels 1998-2004, non-0/0) appear on two or more players: 3 of them on one page
(T4); the fourth (2000 CAGUAS 1/0, Anderson, David and Gates, Prentiss) is a coincidence, UNVERIFIED as such.

[T2] Whose line is it

Rules. (a) foreign: the line equals another player's line (ficha row, or their own page under the same `r`) and the
player's own evidence contradicts it: a later stable capture of theirs shows another line, or their ficha has another
line for the season. (b) consistent: the player's ficha row equals the line, or the sum of their rows does.
(c) unresolved: no evidence of their own either way (no ficha row, one capture).

    capture|player (id)|line|class|why
    2006-06-18|Carmona, Abel (4)|BAYAMON 24/211|a|no ficha; his other rows are Coamo; = Cruz's ficha row; same r
    2006-09-17|Carmona, Abel (4)|BAYAMON 24/211|a|same as above
    2006-11-19|Cruz, Alvin (74)|BAYAMON 24/211|b|ficha 2006 Bayamon 24/211
    2006-10-06|Ayala, Jose (1208)|GUAYNABO 9/43|a|ficha 2006 Bayamon 6/3 and a later capture (r=00530) show that
    2006-12-06|Allen, Ramel (1912)|GUAYNABO 9/43|c|no ficha, one capture; the r is his, likely his own
    2006-10-09|Santiago, Carlos (313)|GUAYAMA 9/6|a|no ficha, one capture; = Ricardo's ficha row; same r, r2, r3
    2006-11-19|Santiago, Ricardo (2000)|GUAYAMA 9/6|b|ficha 2006 Guayama 9/6
    2006-12-12|Santiago, Ricardo (2000)|GUAYAMA 9/6|b|ficha 2006 Guayama 9/6
    2006-08-29|Babilonia, Luis (881)|HUMACAO 4/8|a|his two later captures show ARECIBO 6/6; same r as Saez's page
    2006-10-10|Babilonia, Luis (881)|HUMACAO 4/8|a|same
    2006-12-06|Saez, Joel (990032)|HUMACAO 4/8|c|no ficha (minted id), one capture

Counts: (a) 6 captures on 4 players, (b) 3 captures on 2 players, (c) 2 captures on 2 players. Class (a) hits the slot
of captures from 2006-06-18 to 2006-10-10 only; of the lines found this way, none is in a capture from 2006-10-11 on
(Ayala and Babilonia show their own later).
Outside the slot: the page of Rivera, Alexander (id 49), captured 2006-11-19, has four rows labelled 2001: CAGUAS 7/19
(his; ficha Caguas 6/19), and three that are other players' 2001 lines: CAGUAS 25/265 (Rivas, Luis, same day),
COAMO 11/18 (Leon, Francisco) and PONCE 3/0 (Mendez, Osvaldo). His ficha has one 2001 row. All three: class (a).

[T3] Mechanism

Found: (1) the slot line follows the `r` parameter of the capture URL: 5 of 5 `r` values used by two different names
show the identical slot line (post-flip, 156 distinct `r` values with a slot row); in each pair both pages carry the
same `r` (00034, 00602, 00061, 00554; 00053 is the one person). (2) The same URL gave different names on different days
in 3 pairs (r, r2, r3 all equal: Allen and Ayala, Santiago and Santiago, Babilonia and Saez), and the same URL gave
different slot lines (Babilonia r=00528: Humacao 4/8 on 2006-10-10, Arecibo 6/6 on 2006-12-08). (3) Not previous-fetch:
in every pair the victim's capture is weeks or months BEFORE the owner's (5 months for Carmona and Cruz). (4) Not
neighbours by id: 4 and 74, 1208 and 1912, 313 and 2000, 881 and 990032. (5) The foreign rows on Rivera's page are
2001 rows of players with other `r` values (00089, 00096, 00097). So the mismatch is inside the page (the slot row and
the name or history come from different records). What decides which record: UNCLEAR.

[T4] Exposure in the published data

    row|season|team games/points|source capture|relabelled|merged|season total|conflict|class
    id 4 Carmona, Abel|2006|BAYAMON 24/211|2006-09-17|yes|no|no|no|a
    id 313 Santiago, Carlos|2006|GUAYAMA 9/6|2006-10-09|yes|no|no|no|a
    id 1208 Ayala Perla, Jose Anibal|2006|GUAYNABO 9/43|2006-10-06|yes|no|no|no|a
    id 49 Rivera Cruz, Alexander|2001|COAMO 11/18|2006-11-19|no|no|no|no|a
    id 49 Rivera Cruz, Alexander|2001|PONCE 3/0|2006-11-19|no|no|no|no|a
    id 1912 Allen, Ramel|2006|GUAYNABO 9/43|2006-12-06|yes|no|no|no|c
    id 990032 Saez, Joel|2006|HUMACAO 4/8|2006-12-06|yes|no|no|no|c

5 rows rest on a class (a) line, all kept as jug05-only rows: none merged (a foreign line cannot equal the player's
own ficha row), none a season total, none a conflict, so none appears in Calidad de datos. 3 are among the 145
relabelled rows and among the 31 unchecked relabelled rows that have no twin (of those 31: 3 class a, 2 class c and
26 with no evidence either way, UNVERIFIED). Rivera's fourth foreign row, 2001 CAGUAS 25/265, is not published: the
dedup key (id, season, city) dropped it behind his own CAGUAS 7/19.
"Totales del archivo" include all 5: 278 points and 56 games in all, on 4 players (id 4: 211 points / 24 games, id
313: 6 / 9, id 1208: 43 / 9, id 49: 18 / 14). ids 4 and 313 show a 2006 season that only this line supports. The
rows of 1208 (Guaynabo against Bayamon in 2006) and of 49 (Coamo and Ponce next to Caguas in 2001) each make one of
the 235 trade pairs.
One more finding, out of scope: 5 minted ids (990007, 990019, 990023, 990024, 990033) carry the same career rows as
existing ficha ids (2204, 388, 757, 763, 1205).

[T5] Smallest fix (NOT applied)

Class (a): move the 5 rows out of player_career_seasons.csv into a provenance log, data/interim/jug05_foreign_rows.csv
(id, season, team, games, points, source_url, capture date, the other player's id or name, reason), from a CURATED list
keyed by source_url + row (like the tombstones), applied by a small idempotent script with --check. A detector would
not be safe: shared lines also occur by chance. Rule for a future regeneration: read the same list before the fold.
Class (c): keep and log as unresolved (no change). Class (b): none.
Predicted (simulated): career CSV 5,683 -> 5,678 rows; conflicts 94 and merged 767 unchanged; trade pairs 235 ->
233 (1208 in 2006, 49 in 2001); 4 player files change (4, 313, 1208, 49), index/players.json (career_seasons),
data_quality.json (optionally a count), manifest.json (digest; the new log is a digest input if published). Totals:
-278 points and -56 games over 4 players; ids 4 and 313 lose their 2006 season. A deploy purges visitors' cached
data once. Needs an owner decision (a curated exclusion).

[T6] Wording if the fix is deferred

Calidad de datos would need a neutral note: "En 5 filas, una página de jug05 muestra la línea de otro jugador
(dos jugadores comparten la misma línea). Siguen en el archivo y se cuentan en los totales hasta que se revisen."
No "error". Until then the 2 class (c) rows and the 26 rows with no evidence are shown as if verified.

[T7] Verification

Recomputed here: 586 pages, 197 players, 193 slot lines, the 4 shared lines and 11 captures, the r tests, the 5 + 2
rows in the CSV and the logs, the totals from web/data/players. UNVERIFIED: foreign lines whose owner has no
capture; the 26 unchecked rows; why the page mixes records; whether the 2000 CAGUAS 1/0 pair is a coincidence.

[DECISION AND RESULT] (owner, 2026-09-21; applied in PHASE_FOREIGN_SLOT_APPLY)

The 5 rows of class (a) that are published are excluded from the career data and logged: id 4 (2006 BAYAMON
24/211), id 313 (2006 GUAYAMA 9/6), id 1208 (2006 GUAYNABO 9/43) and id 49 (2001 COAMO 11/18 and 2001 PONCE 3/0).
Class b (Cruz 74, Santiago Ricardo 2000) and class c (Allen 1912, Saez 990032) stay. The 5 minted ids that carry
the same rows as ficha ids (990007, 990019, 990023, 990024, 990033) are out of scope.

Applied as a curated list with per-row evidence (`data/interim/jug05_foreign_lines.csv`), a shared rule
(`parse_players.drop_foreign_rows`), `src/apply_jug05_foreign_rows.py` (--check, idempotent) and a provenance log
(`data/interim/jug05_foreign_rows.csv`). Result, read back from the files: 5 rows removed, career CSV 5,683 -> 5,678,
trade pairs 235 -> 233, merged 767 and conflicts 94 unchanged, totals -278 points and -56 games over the 4 players.
Calidad de datos got one more note and `data_quality.json` got `counts.foreign_rows` (5) and the 5 rows. Details:
data_quality_view_spec.md, section 9.

