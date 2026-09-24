# Cluster evidence packets, batch 2 (A03, A04, A05)

Status: EVIDENCE ONLY (READ-ONLY). Nothing in data/, web/, app/ or src/ was changed. Written 2026-09-22 at HEAD
  087bf7c.
Source: docs/specs/identity_triage_audit_spec.md (section 3, the 17 (a) clusters; A01, A02, A06 merged in 18a0295,
  A17 held). These are the next 3 unresolved by cluster id: A03, A04, A05. Re-read against the committed CSVs, the
  raw captures in data/raw/players (read through the repo's own parse_enciclopedia and parse_jugador, never
  main()), and the raw HTML directly for the enciclopedia table rows. Every number was re-counted for this
  document.
Marker: UNVERIFIED = not checkable from the repo, or no external ground truth. No external biography was
  consulted.

## Summary

CLUSTER|IDS|RECOMMENDATION|SURVIVOR|KEY EVIDENCE
A03|180,194|MERGE|194 (3 rows, profile)|same DOB; surnames are an exact token swap of each other (Gonzalez
  Arroyo vs Arroyo Gonzalez); 180 has zero independent data
A04|344,345,346,347|MERGE all three into 344|344 (13 rows, 130 box rows)|345/346/347 are three consecutive,
  byte-identical duplicate rows of 344's own enciclopedia listing (same name, jersey, DOB, in all 77 captures)
A05|721,722|NEEDS MORE EVIDENCE|721, if merged (5 rows)|722 is a clean duplicate stub of 721 (adjacent row, same
  name/jersey/DOB); but 721's OWN profile carries a birth date (1980) that contradicts its OWN career rows
  (1965-1969) and its own bio (a 2005 roster listing) -- a pre-existing defect in the survivor, not caused by
  either id count

A03 and A05 differ from A04 in kind: A04's three empty ids sit in physically adjacent table rows across all 77
  captures (the site itself repeated one listing three times). A03's pair is 14 ids apart, with unrelated players
  listed in between -- same-DOB and swapped-surname evidence, not a repeated-row artifact. A05's pair is
  adjacent (one repeated row), but the survivor's own record is internally inconsistent.

## A03: ids 180, 194

### 1. Identity, per id
180|Gonzalez Arroyo, Antonio|8 aliases (canonical, enciclopedia, given_family_order, initial x2, normalized,
  paternal_surname x2)
  DOB 12/7/1959: no profile page: the value comes from the enciclopedia listing itself (the "Nació" column of
    its own row). No birthplace, position or nationality recorded. No jersey in any of 77 captures.
  Seasons: none (no career rows). No jugador.asp profile.
  Raw: enciclopedia only, 77 of 77 captures (2007-04-17 to 2021-09-01), name spelled "Gonzalez Arroyo" (surname
    order: Gonzalez first).
194|Arroyo Gonzalez, Antonio, nickname "tony"|10 aliases (adds nickname, nickname_surname)
  DOB 12/7/1959: own profile page (capture 2007-08-29), same value as 180's enciclopedia row. Birthplace,
    position and nationality blank on the profile itself.
  Seasons 1981-1983 (3 rows, from the profile). No jersey in any of 77 captures.
  Raw: enciclopedia, 77 of 77 captures, name spelled "Arroyo Gonzalez" (surname order: Arroyo first); profile
    capture 20070829041523.

### 2. Career rows
180 (0): none.
194 (3): 1981 Leones, Ponce 29/177; 1982 Indios, Mayaguez 7/23; 1983 Criollos, Caguas 22/135.
Overlap: none possible (180 has no rows). Gaps: none within 194's own 1981-1983 span. The union is 194's career
  as recorded, contributing nothing new or contradicting from 180.

### 3. Observations
id_map: neither id has an observation (194's seasons, 1981-1983, predate the leader/stat files the id_map draws
  on, which start in 2000). Roster (latinbasket): neither id. Bios (jugador05): neither id. Box scores: neither
  id (box data covers 2001-2003 and 2008-2013 only, outside 194's 1981-1983 span, so this is expected, not a
  contradiction). Review queue: neither id is named. App crosswalk: neither id.
Aliases: 0 overlap between 180's 8 and 194's 10 (checked exactly, by normalized_alias + alias_type): the two
  surname orderings never produce the same string, so a merge would add all 8 of 180's aliases as new rows on
  194.
Enciclopedia position: 180's row sits between two unrelated players ("...ez Rosado, Angelo Benito" before it);
  194's row is preceded by an unrelated "Arroyo Melendez, Allan" (DOB 2/20/1966). The two ids are not physically
  adjacent in the table (14 apart), and neither ever drops out of the 77 captures (both present start to end).

### 4. Recommendation
MERGE, survivor 194 (3 career rows, a real profile, the nickname "tony").
Evidence: (1) identical DOB (12/7/1959) recorded independently -- 180's from the bare enciclopedia listing,
  194's from its own profile page; (2) the two canonical names use the exact same two surname tokens
  ("Gonzalez" and "Arroyo") in reversed order, a pattern the audit already flagged elsewhere in this dataset
  (1189/1192 is the same shape); (3) 180 contributes no career row, no id_map observation, no bio, no roster row
  and no jersey across all 77 captures -- every fact it carries duplicates something 194 already has, in
  reversed order.
UNVERIFIED / needs outside check: this rests on a heuristic (DOB match + name-token reversal), not a co-
  appearance or a third source naming both the same way. No external biography was consulted for either
  "Antonio Gonzalez Arroyo" or "Antonio 'Tony' Arroyo Gonzalez". If the owner wants a second source before
  merging, that is a fair reading; nothing else in the record argues against it.
Touches: 1 canonical row, 8 alias rows, web/data/players/180.json. No career, roster, id_map, bio or box rows
  move (180 has none).

## A04: ids 344, 345, 346, 347

### 1. Identity, per id
344|Travieso Peña, Carmelo|8 aliases (canonical, enciclopedia, given_family_order, initial x2, normalized,
  paternal_surname x2)
  DOB 9/5/1975: enciclopedia listing (no profile page for any of the 4 ids). Cataño, Puerto Rico; Escolta;
    Puerto Rico -- all three from the jugador05 bio (a 2006 fill, since jugador05 records carry no career/DOB
    directly used here beyond the bio, see below). Jersey "6" in all 77 captures.
  Seasons: none recorded on the canonical row itself (has_profile: no; first/last_season blank -- the 13 career
    rows come from jug05, a separate source, not the profile fields).
345, 346, 347|Travieso Peña, Carmelo|8 aliases each, byte-identical set to 344's (same 8 normalized_alias
  strings, differing only by bsnpr_id)
  DOB 9/5/1975 on all three, from the enciclopedia listing only. No birthplace, position or nationality. Jersey
    "6" in all 77 captures, on all three ids, same as 344.
  Seasons: none. No profile page, no id_map observation, no bio, no roster row, no box row, for any of the
    three.

### 2. Career rows
344 (13, all source wayback_bsnpr_jug05): 1993 Morovis 11/105; 1994 17/154; 1995 20/293; 1996 20/247; 1997
  26/308; 1998 17/190; 1999 24/354; 2000 18/340; 2001 Bayamon 26/411; 2002 30/353; 2003 1/14; 2004 Santurce
  21/46; 2006 Santurce 17/57.
345, 346, 347 (0 each): none.
Overlap: none possible (the other three have no rows). Gap: 2005 (no row on any of the 4 ids); the jugador05
  bio (below) is dated 2006 and names Santurce, matching 344's last career row -- no contradiction. The union
  is one coherent career, entirely 344's own: Morovis 1993-2000, Bayamon 2001-2003, Santurce 2004 and 2006.

### 3. Observations
id_map: 344 has 4 observations, all single-source, all confirmed by club_check (2000 Morovis leaders, 2001 and
  2002 Bayamon leaders, 2001 Bayamon season stats). 345/346/347: none.
Bios (jugador05): 344 has 1 (captured 2006-11-19, Santurce roster 2006, jersey "06" -- matches the enciclopedia
  jersey and the last career row). 345/346/347: none.
Box scores: 344 has 130 rows, seasons 2001-2003 (BS21/BS22/BS23), all under "BAYAMON", jersey "6" throughout --
  matches the career rows and the enciclopedia jersey exactly. 345/346/347: 0 rows each.
Roster (latinbasket), review queue, app crosswalk: none of the 4 ids appear in any of them.
Raw HTML: in the first enciclopedia capture (2007-04-17), the rows for 344, 345, 346 and 347 are four
  CONSECUTIVE <tr> rows in the table, each an exact duplicate of the others (Apellidos "Travieso Peña", Nombre
  "Carmelo", Camisa "06", Nació "9/5/1975"), differing only in the id= the row's own link carries. The same
  four-row block recurs in all 77 captures; none of the 4 ids ever drops out.

### 4. Recommendation
MERGE 345, 346 and 347 into 344, survivor 344 (13 career rows, 130 box rows, 4 id_map observations, 1 bio).
Evidence: (1) the source's own enciclopedia table lists this one real listing four times in a row, with
  identical name, jersey and birth date on every one of 77 captures; (2) 345, 346 and 347 carry no independent
  fact anywhere in the archive -- no career row, no box row, no id_map observation, no bio, no roster row; (3)
  344 alone is fully corroborated across three independent sources (jug05 career rows, 2001-2003 box scores,
  2006 jugador05 bio), all agreeing on team, jersey and season.
This is the cleanest of the three clusters in this batch: unlike A03's pair, the four ids sit as adjacent,
  byte-identical rows, the same signature the earlier batch used to justify A01/A02/A06.
Touches: 3 canonical rows, 24 alias rows (8 each), 3 web/data/players/<id>.json files. No career, roster,
  id_map, bio or box rows move (345/346/347 have none).

## A05: ids 721, 722

### 1. Identity, per id
721|Llovet Ayala, Francisco|8 aliases (canonical, enciclopedia, given_family_order, initial x2, normalized,
  paternal_surname x2)
  DOB 5/9/1980 (own profile, capture 2007-08-28, age shown as 27 on the page -- consistent with a 1980 birth in
    2007). Arecibo, Puerto Rico; Delantero; Puerto Rico; height 6'4", weight 210 (from the profile text itself,
    not latinbasket -- latinbasket has no row for either id). Jersey "23" in all 77 captures.
  Seasons 1965-1969 (5 rows, from the profile's own career table -- see the anomaly below).
722|Llovet Ayala, Francisco|8 aliases, byte-identical set to 721's
  DOB 5/9/1980 on the enciclopedia listing only. No birthplace, position, nationality or profile page. Jersey
    "23" in all 77 captures, same as 721.
  Seasons: none.

### 2. Career rows
721 (5, all source wayback_bsnpr_players, from its own profile page): 1965 Capitanes, Arecibo 13/32; 1966
  10/12; 1967 18/44; 1968 10/12; 1969 16/74.
722 (0): none.
Overlap: none possible (722 has no rows). Gap: 1970-2004 (35 seasons, no row on 721). The union, as recorded,
  is NOT internally coherent by itself: the profile's own header gives age 27 in a 2007-08-28 capture (DOB
  5/9/1980), which cannot be reconciled with a person who played 1965-1969 for Capitanes de Arecibo -- that
  career would require a birth year in the mid-1940s to early 1950s, not 1980. This is bsnpr.com's own page
  (both the DOB and the 1965-1969 table sit on the single captured id=721 HTML file); it is not an artifact of
  this repo's parsing.

### 3. Observations
id_map, roster (latinbasket), review queue, app crosswalk: neither id appears in any of them.
Bios (jugador05): 721 has 1 (captured 2005-09-03, San German roster 2005, jersey "23"). This DOES fit a
  1980-born, 25-year-old player (age-consistent with the profile's own 1980 DOB), but names a different team
  (San German) and a different decade (2005) than the profile's 1965-1969 Arecibo career rows, and no career
  row exists for 2005 on either id. 722: no bio.
Box scores: neither id has a row (box data covers 2001-2003 and 2008-2013; a 2005 season, if it had games in
  this player's actual career, would not be covered either way).
Raw HTML: in the first enciclopedia capture, the rows for 721 and 722 are two consecutive <tr> rows, both
  "Llovet Ayala, Francisco", jersey "23", DOB "5/9/1980" -- the same repeated-row pattern as A04, just a pair
  instead of a quadruple. Both ids persist through all 77 captures; neither ever drops out.

### 4. Recommendation
NEEDS MORE EVIDENCE. The id-duplicate question (721 vs 722) is not the hard part: 722 is a clean duplicate stub
  (adjacent row, identical name/jersey/DOB, zero independent data of its own), the same pattern as A04's three
  extra ids, and folding it into 721 would lose nothing. Survivor if merged: 721.
What blocks a plain MERGE: 721's OWN record is internally inconsistent -- a 1980 birth date that the profile's
  own career table (1965-1969) contradicts, and a 2005 bio (jersey 23, San German) that fits the 1980 DOB but
  not the 1965-1969 Arecibo rows or team. The 1965-1969 rows most likely belong to an older, different
  "Francisco Llovet Ayala" (a father or namesake) whose data bsnpr.com itself attached to this profile page;
  UNVERIFIED which of the two identities -- if there are two -- the 1980 DOB and the 2005 bio actually
  describe, since no other source ties them together or apart.
Recommendation: hold the merge until this is resolved (which years, if any, 721 should keep), so a merge does
  not launder a pre-existing bsnpr.com data error into the published record as a "coherent career". Merging
  722 costs nothing either way and can happen whenever 721 itself is settled.
Touches if 722 alone is merged: 1 canonical row, 8 alias rows, web/data/players/722.json. No career, roster,
  id_map, bio or box rows move (722 has none). The 1965-1969 vs 1980/2005 question is unaffected by this merge
  in either direction.

## Correction (2026-09-24)

The A04 section above (lines 122 and 124) says id 344 is "corroborated across three independent sources"
(13 jug05 career rows, 130 box-score rows 2001-2003, a 2006 jugador05 bio). This was overstated: all three
are bsnpr.com pages (jug05.asp, gamestatwide.asp, jugador05.asp) -- the same site, not independent
organizations. They do still agree with each other on team, jersey and season, which is the fact the
merge decision actually rests on. The public-facing wording (D-ID-006's evidence/evidence_es in
data/clean/player_identity_decisions.csv, published to web/data/index/data_quality.json) has been
corrected to say "tres páginas de bsnpr.com ... Las tres vienen de la misma fuente" instead of
"independientes". This section of the document is left as originally written, per its own read-only
convention; this note records the correction rather than editing the lines above.
