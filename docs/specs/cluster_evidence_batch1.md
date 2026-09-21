# Cluster evidence packets, batch 1 (A01, A02, A06, A17)

Status: EVIDENCE ONLY (READ-ONLY). Nothing in data/, web/, app/ or src/ was changed. Written 2026-09-21 at HEAD
  01264b9.
Source: docs/specs/identity_triage_audit_spec.md (clusters A01, A02, A06, A17), re-read against the committed CSVs,
  the raw captures in data/raw/players (read through the repo's own parse_enciclopedia, parse_jugador,
  parse_jugador05 and parse_jug05, never main()), and git. Every number was re-counted for this document.
Marker: UNVERIFIED = not checkable from the repo, or no external ground truth. No external biography was consulted.

## Summary

CLUSTER|IDS|RECOMMENDATION|SURVIVOR|KEY EVIDENCE
A01|24,35,273|SPLIT: MERGE 24 into 35 only; DO NOT MERGE 273|35 (15 rows)|35 and 273 share 20 box-score games (1-17
  min vs 20-38 min)
A02|73,74|MERGE|74 (18 rows)|5 of 73's 6 rows identical to 74's; league dropped 73 in 2008; same DOB on both
  profile pages
A06|951,952|MERGE|952 (13 rows)|951's only row is identical to 952's; league dropped 951 in 2008; no game with both
  ids
A17|1947,1948|NEEDS MORE EVIDENCE (lean DO NOT MERGE)|none (1948 keeps its record)|1947's only row is 1963; its DOB
  is inherited, not its own

Batch 1 as approved (A01, A02, A06) therefore becomes: A02 and A06 as clusters, A01 narrowed to 24 -> 35.
The audit's rule over-linked A01: "Alberto C." and "Carlos A." matched through the initial-compatibility test.

## A01: ids 24, 35, 273

### 1. Identity, per id
24|Arroyo, Alberto|6 aliases (canonical, enciclopedia, given_family_order, initial, normalized, paternal_surname)
  DOB 7/30/1979: the canonical value comes from the jugador05 bio (fill); Rio Piedras; Escolta; Puerto Rico (all
    jugador05).
  Seasons: none. Height: none. No jugador.asp profile page. Enciclopedia: 77 captures, jersey 11 in the last one.
35|Arroyo Bermudez, Alberto C., nickname "berti"|12 aliases (adds nickname, nickname_surname, given_first_only x2)
  DOB 7/30/1979 (profile 2008-08-03; enciclopedia 77 of 77 captures); Rio Piedras; Escolta; Puerto Rico.
  Seasons 1996-2008 (13). Height: none. Jersey in box scores: 10 (66 rows) and 11 (11 rows, 2008 Fajardo).
  Raw: enciclopedia, profile capture 20080803163146, jug05 record "Arroyo, Alberto" (DOB 7/30/1979, Escolta,
    1996-2005).
273|Arroyo Bermúdez, Carlos A.|10 aliases
  DOB 7/30/1979 (profile 2017-07-15; enciclopedia: unknown from 2007-04 to 2007-11, 7/30/1979 from 2007-12-04 on,
    64 captures).
  Fajardo; Armador; Puerto Rico; seasons 1996-2017 (10 rows); height 188 cm (latinbasket: 2015 Santurce, 2017-18
    Fajardo, PG).
  Jersey 7 (enciclopedia, 65 box rows, latinbasket 2017-18). Raw: enciclopedia, profile capture 20170715120129.
  app/player_crosswalk.csv maps the curated "Carlos Arroyo" to 273 (verdict auto, confidence 9).

### 2. Career rows (season team games/points)
35 (15 rows, players source unless marked): 1996 Fajardo 12/20; 1997 Fajardo 8/33; 1998 Santurce 10/17; 1999
  Santurce 14/34; 2000 Santurce 10/5; 2001 Santurce 12/14 and jug05 12/26 (a logged conflict); 2002 Santurce 11/20;
  2003 Santurce 17/38; 2004 Santurce 10/18; 2005 Santurce 6/11 and jug05 Guaynabo 20/21; 2006 Guaynabo 20/21; 2007
  Fajardo 16/14; 2008 Fajardo 12/5
273 (10 rows): 1996 Fajardo 34/371; 1997 Fajardo 32/543; 1998 Santurce 29/243; 1999 Santurce 30/457; 2000 Santurce
  28/480; 2001 Santurce 8/164; 2002 Santurce 10/200; 2003 Santurce 1/14; 2015 Santurce 33/597; 2017 Fajardo 27/443
Overlap: 8 seasons (1996-2003), the same team in every one, 0 identical rows: 35 has 5-38 points a season, 273 has
  14-543. Gaps: 35 has 2004-2008 alone; 273 has 2015 and 2017 alone. The union is NOT one coherent career: two
  lines on one team-season.

### 3. Observations that reference each id
id_map: 35 has 2 (Tier-2 "Arroyo, A." Santurce 2001, 2003); 273 has 6 (awards 1996, leaders 2001-02 and 2018,
  Tier-2 "Arroyo, C.").
Tier-2 season stats list them as separate lines on the same team: 2001 Arroyo C. jersey 7, 8 games, 164 pts, 259
  min; 2001 Arroyo A. jersey 10, 12 games, 14 pts, 58 min; 2003 Arroyo C. 1 game, 14 pts; 2003 Arroyo A. 11 games,
  17 pts.
Box scores (game_box_player.csv): 35 has 77 rows (67 games), 273 has 65 rows (56 games). 20 games have BOTH ids
  (2001: 8, 2002: 5, 2003: 7), all Santurce, jerseys 10 and 7. 35 played 1-17 minutes (median 4), 273 played 20-38
  (median 30), and 273 played more in all 20. Example BS21013 (2001-05-19): "Arroyo, Alberto" jersey 10, 3 min, 2
  pts; "Arroyo, Carlos" jersey 7, 28 min, 22 pts. One person cannot have two lines in one game.
Roster (latinbasket): 273 has 3 rows; 24 and 35 have none. Bios: 24 has one (jugador05, captured 2006-11-19,
  Santurce 2006, jersey 10, Rio Piedras, "rapidez y buen tiro a larga distancia, puede jugar de armador y
  escolta"). The bio was attached to 24 because its name matched 24's canonical name exactly.

### 4. Why three ids
- 24: the enciclopedia's own stub "Arroyo, Alberto". In the first capture (2007-04-17) it carried DOB 7/30/1979,
  the same as 35; the league later blanked it (76 captures show unknown) but kept the row, with jersey 11 like 35.
- 35: Alberto C. Arroyo Bermudez, "Berti", escolta, born Rio Piedras: has a profile and the jug05 record.
- 273: Carlos A. Arroyo Bermúdez, armador, born Fajardo, jersey 7: the curated "Carlos Arroyo".
The third differs by given name AND by birthplace, position, jersey, minutes and stat lines, and shares games with
  the second: it is a different person, not a naming variant. The same two surnames and the same DOB suggest
  brothers (twins?): UNVERIFIED. The shared DOB is itself uncertain: 273's DOB only appeared in the enciclopedia on
  2007-12-04, after 35's had been there since the first capture, so one of the two may be a copy. The repo cannot
  say which.

### 5. Recommendation
- 35 <-> 273: DO NOT MERGE. Evidence: 20 games with both on the floor (jerseys 10 and 7, 1-17 vs 20-38 minutes), 8
  shared team-seasons with 0 identical rows, two separate Tier-2 lines, different birthplace and position.
- 24 -> 35: MERGE, survivor 35. Evidence: the same DOB 7/30/1979 in the league's 2007 listing and in the jugador05
  bio; the bio's jersey 10, Santurce and Rio Piedras match 35 (box jersey 10, Santurce 1998-2005, profile city Rio
  Piedras); 24 has no career rows, no id_map, no roster and no box rows, so nothing can conflict. Weakest point:
  the bio's Santurce 2006 does not match 35's 2006 row (Guaynabo); the page may list the 2006-07 roster.
  UNVERIFIED.
- What the 24 -> 35 merge touches: 1 canonical row, 6 alias rows, 1 bio row (re-pointed), web/data/players/24.json.
  "NEEDS MORE EVIDENCE" is a fair reading if the owner wants a second source for 24; nothing else is at stake.

## A02: ids 73, 74

### 1. Identity, per id
73|Cruz, Alvin|6 aliases; DOB 4/24/1982 (profile 2008-04-06); Río Piedras, Puerto Rico; Armador; Puerto Rico
  Seasons 2000-2002 (profile) plus 3 jug05 rows; height 186 cm (latinbasket: 2010 Ponce, 2014-18 Arecibo; jersey
    28).
  Raw: enciclopedia in only 17 of 77 captures (2007-04-17 to 2008-03-07), profile page, jug05 record "Cruz, Alvin".
74|Cruz Torres, Alvin|8 aliases; DOB 4/24/1982 (profile 2017-08-17; enciclopedia 77 of 77); San Juan, Puerto Rico;
  Armador
  Seasons 1998-2017 (18 rows); jerseys 10, 28, 82 (enciclopedia). Raw: enciclopedia, profile capture
    20170817055003.

### 2. Career rows
73 (6): 1998 Bayamon 9/12 (jug05); 1999 Bayamon 10/15 (jug05); 2000 Bayamon 8/9; 2001 Bayamon 11/60; 2002 Bayamon
  20/87; 2005 Bayamon 24/211 (jug05)
74 (18): 1998 Bayamon 9/12; 1999 10/15; 2000 8/9; 2001 11/60; 2002 20/87; 2005 11/134; 2006 24/211; 2007 16/149;
  2008 Carolina 32/181; 2009 Carolina 18/251; 2010 Ponce 29/329; 2011 Quebradillas 3/8; 2012 Quebradillas 26/125;
  2013 Guaynabo 36/175; 2014-2017 Arecibo 32/62, 33/175, 28/46, 27/90
Overlap: 6 seasons. 5 rows are IDENTICAL (games and points) in both ids. The 6th, jug05 2005 24/211, equals 74's
  2006 row (24/211): a season-label difference (jug05 2005 vs profile 2006), which would surface as a stat conflict
  after a merge. Gaps: 2003-2004 have no row on either id. Every 73 row is already contained in 74, so the union is
  one coherent career: Bayamon 1998-2007, Carolina 2008-09, Ponce 2010, Quebradillas 2011-12, Guaynabo 2013,
  Arecibo 2014-17.

### 3. Observations
id_map: 74 has 5 (leaders 2009-2014); 73 has none. Review queue: 2 rows list both ids as candidates ("Cruz, Alvin"
  2020, "Cruz, A." 2001): a merge would resolve them. Roster: 73 has 5 rows (2010 Ponce; 2014 and 2016-2018
  Arecibo; #28, 186 cm); they sit on the lower id only by the tie-break rule in the roster build (not evidence),
  and they fit 74 (jersey 28, same teams).
Box: 74 has 278 rows (2008-2013); 73 has none; no game has both ids. jug05 merged log: 3 rows on 73 (2000-2002).
Enciclopedia timeline: 73 got DOB 4/24/1982 on 2008-01-04 (same as 74) and was gone from the next capture after
  2008-03-07. Only 19 ids ever vanish from the enciclopedia, and 16 of them have a same-surname, same-given-name id
  that persists.

### 4. Recommendation
MERGE, survivor 74 (18 rows, 278 box rows, 5 id_map rows, the full profile).
Evidence: (1) five identical (season, team, games, points) rows on two separate profile pages; (2) DOB 4/24/1982 on
  both profile pages, and in the league's list two months before it dropped 73; (3) same position and country, and
  Río Piedras is a district of San Juan; (4) the league itself removed 73; (5) no co-appearance in any game.
Touches: 1 canonical row, 6 aliases, 6 career rows (5 duplicates plus the jug05 2005 row), 5 roster rows, 2
  review-queue rows, 3 jug05 merged-log rows, web/data/players/73.json. No box rows, id_map rows, bios or game
  files.

## A06: ids 951, 952

### 1. Identity, per id
951|Lopez, Ivan|6 aliases; the profile page exists but is empty (no DOB, city, position or nationality)
  Canonical DOB 5/16/1985, Aguadilla, Delantero and Puerto Rico all come from the jugador05 bio (fill), attached by
    exact name.
  Seasons 2002-2002 (1 row); height 208 cm (latinbasket 2013 Ponce, C/F). Raw: enciclopedia in 17 of 77 captures
    (last 2008-03-07), profile capture 20070829041642, jugador05 bio (Ponce 2005, captured 2005-04-15).
952|Lopez Rodriguez, Ivan|8 aliases; DOB 5/16/1985 (profile 2013-04-28; enciclopedia 77 of 77); Aguadilla;
  Delantero; Puerto Rico
  Seasons 2002-2013 (13 rows); jerseys 13, 31, 52. Raw: enciclopedia, profile capture 20130428001411, jug05 "Lopez,
    Iván" (DOB 5/16/1985, Delantero; its career rows are attached to 952).

### 2. Career rows
951 (1): 2002 Mayaguez 2/3.
952 (13): 2002 Mayaguez 2/3; 2005 Isabela 22/123; 2005 Bayamon 8/36 and jug05 Bayamon 3/0 (a logged conflict); 2006
  Coamo 4/22; 2006 Bayamon 17/135; 2007 Bayamon 24/229; 2008 Bayamon 23/162; 2009 Bayamon 14/54; 2010 Mayaguez
  23/98; 2011 Bayamon 28/56; 2012 Humacao-Carolina 7/23; 2013 Ponce 1/0
Overlap: 2002, identical (games and points) and the same team. Nothing else is on 951, so 951 is a subset of 952
  and the union is one coherent career (2002 to 2013). 2005 and 2006 show two teams each (in-season moves); 2005
  also has a logged conflict.

### 3. Observations
Bio: 951 has the jugador05 bio. Its roster team (Ponce 2005) is not among 952's 2005 rows (Isabela, Bayamon);
  whether he was on Ponce's early 2005 roster is UNVERIFIED. Roster: 951 has 1 row (2013 Leones de Ponce, 208 cm),
  placed on the lower id by the roster tie-break; 952's career has 2013 Ponce and 952 has 38 Ponce box rows in
  2013. id_map: none on either.
Box: 952 has 88 rows (2008-2013); 951 none; no game has both ids. Review queue: none. jug05 merged log: 952 has 1
  row.
Enciclopedia: 951 never had a DOB there and vanished after 2008-03-07, the same capture as 73.

### 4. Recommendation
MERGE, survivor 952 (13 rows, 88 box rows, the full profile).
Evidence: (1) 951's only row equals 952's 2002 row exactly, and the jug05 record for "Lopez, Iván" has the same
  2002 Mayaguez line; (2) the league removed 951 from its list in 2008 while 952 stayed through 2021; (3) the 951
  bio's DOB, city and position (5/16/1985, Aguadilla, Delantero) match 952's own profile; (4) height 208 cm and C/F
  fit 952's 2013 Ponce season; (5) no game has both ids.
Touches: 1 canonical row, 6 aliases, 1 career row (a duplicate), 1 bio row (re-pointed), 1 roster row (re-pointed),
  web/data/players/951.json. Weakest point: the DOB is not independent (it came through the bio), but points (1)
  and (2) are.

## A17: ids 1947, 1948

### 1. Identity, per id
1947|Rivera, Raul|6 aliases; own profile page: DOB 1/1/1900 (the source's "unknown"), position "No se sabe", no
  city
  Canonical DOB 8/31/1982, birthplace New York and position Centro come from the jugador05 bio (fill), attached by
    exact name.
  Seasons 1963-1963 (1 row); height 215 cm (latinbasket 2009-10 Arecibo, C, jersey 14: placed here by the tie-break
    rule).
  Raw: enciclopedia, 77 captures (DOB 8/31/1982 in the first capture only, unknown in the other 76; no jersey),
    profile capture 20070930203415, jugador05 bio (Santurce 2005, jersey 08, New York, captured 2005-03-22).
1948|Rivera Ramos, Raul|8 aliases; DOB 8/31/1982 (profile 2009-10-04 and enciclopedia 77 of 77); New York; Centro
  Nationality "New York" (a birthplace in a nationality field); seasons 2001-2009 (10 rows); jerseys 23, 14
    (enciclopedia). Raw: enciclopedia, profile capture 20091004043908, jug05 record "Rivera, Raúl" (DOB 8/31/1982,
    Centro, 2001-2005).

### 2. Career rows
1947 (1): 1963 Capitanes de Arecibo, 12 games, 23 points (players source, the profile page of id 1947).
1948 (10): 2001 San German 5/1 and jug05 5/2 (a logged conflict); 2002 San German 10/3; 2004 Mayaguez 15/30; 2005
  Coamo jug05 23/94 and players 28/84 (a logged conflict); 2006 Coamo 23/94; 2007 Arecibo 26/154; 2008 Arecibo
  22/33; 2009 Arecibo 26/65
Overlap: none. Gap: 1963 to 2001 (38 years). A player born in 1982 cannot have a 1963 row, so the union is not one
  coherent career without discarding the 1963 row.

### 3. The 1963 row
- Source: data/raw/players/jugador/1947_20070930203415.html, the id's own jugador.asp profile (Wayback capture of
  2007-09-30). The page shows "Rivera, Raul", DOB 1/1/1900 (age 107), position unknown, one row "1963 | Capitanes,
  Arecibo | JJ 12 | PTS 23" and "Temporadas: 1". It is stored as the players-source career row for id 1947.
- Is it an older Raul Rivera? It looks like it. The page itself carries no 1982 DOB. The source has 29 career rows
  for 1963 in all (this one included) across 8 franchises, four of them Capitanes de Arecibo, so a 1963 row is
  normal for this source.
- Is it a typo for 2003? Not supported: the box scores cover Arecibo 2003 (403 rows) and no Rivera appears there
  (Rivera rows on Arecibo exist for 2001, 2002, 2008-2010 and 2013 only). Coverage of that box data is UNVERIFIED.
- Where the 1982 data on 1947 comes from: the league's first enciclopedia capture (2007-04-17) gave 1947 the DOB
  8/31/1982, the same as 1948, and the league blanked it afterwards. The canonical DOB, city and position were
  filled from a jugador05 bio that describes the 1982-born center (same DOB, New York, Centro) and matched 1947
  only because its name equals "Rivera, Raul". The jug05 record for the same person carries the 2001-2005 rows that
  belong to 1948. So the DOB is an inherited attribute, not evidence that 1947's own pages describe the same man.

### 4. Observations
id_map: 1948 has 3 (Tier-2 "Rivera, R." 2001-02), all flagged club_check "contradicts": the observed clubs differ
  from 1948's own. Roster: 1947 has 2 rows (Arecibo 2009-10, jersey 14, 215 cm); jersey 14 is 1948's enciclopedia
  jersey, and 1948 has box rows for Arecibo 2008-2010 ("Rivera, Raul": 58, 49 and 1), so those two rows belong to
  1948. Bio: 1947 has the jugador05 bio (Santurce 2005, #08); 1948's 2005 rows are Coamo, so the bio's team is
  UNVERIFIED. Box: 1948 has 141 rows; 1947 none. Review queue and crosswalk: nothing.

### 5. Recommendation
NEEDS MORE EVIDENCE, leaning DO NOT MERGE. A merge would attach a 1963 row to a 1982-born player.
- Established: the DOB, city, position, bio and both roster rows sitting on 1947 describe 1948's person.
- Not established: whether 1947 is (a) an older Raul Rivera whose only record is the 1963 row, or (b) a stub with a
  wrong season. (b) has no support in the box data; (a) has support in the source's own 1963 rosters, but only
  circumstantially.
- Suggested follow-up, separate from any merge: re-point the bio and the 2 roster rows to 1948 and let 1947 keep
  only its 1963 row and unknown DOB. It needs an owner decision and, if the league has one, a 1963 Arecibo roster
  to check the row.
- Merge cost if the owner still wants it: 1 canonical row, 6 aliases, 1 career row (the 1963 one, to be dropped or
  kept), 1 bio row, 2 roster rows, web/data/players/1947.json.

## Side findings (not part of any recommendation)
- Bio attachment: jugador05 bios are attached to a canonical row by exact-name match, which put the bios of 24, 951
  and 1947 on the enciclopedia stubs of persons whose own ids are 35, 952 and 1948. Those clusters' DOBs are
  inherited this way.
- Header bug: parse_enciclopedia only reads the birth-date column when its header is "Nació". 75 of the 77 captures
  write "Nacio", so their birth dates are ignored. The effect on the spine is small: 2 ids with a blank canonical
  DOB have a real one in a capture (130: 7/1/1976, 556: 6/5/1983), and 13 ids change DOB between captures (e.g.
  1700: 2/13/1965 once, 2/13/1972 in 76).
- League cleanup: 19 ids vanish from the enciclopedia before the last capture; 5 of them at the 2008-03-07 capture,
  including 73 and 951. Sixteen have a same-name id that persists.
- Roster tie-break: the 8 latinbasket rows on known duplicate pairs sit on the lower id by rule; treat them as
  unresolved.

## What was not verified
- Whether 35 and 273 are twins or one DOB is a copy. Whether Alberto's 2006 Santurce bio line is right.
- Whether 951's Ponce 2005 and 1947's Santurce 2005 roster lines match a real roster.
- Whether the box data is complete for Arecibo 2003. Whether jug05's 2005 label equals the profile's 2006 season.
- Anything outside the repo (the league's own registry, biographies).
