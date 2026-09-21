# Player identity triage audit -- spec

Status: AUDIT (READ-ONLY). Nothing in `data/`, `web/`, `app/` or `src/` was changed. Written 2026-09-20 at HEAD `d2cdc6f`.
Method: every count below was recomputed from the committed files or from `git show <rev>:<file>`. The working scripts live in the
session scratchpad, not in the repo. Two raw-parse checks called `parse_enciclopedia()`, `parse_jugador()` and `parse_jugador05()`
(pure readers of `data/raw/players/`); `main()` and every regeneration target were NOT run (N7).
Marker: UNVERIFIED = could not be checked from the files, or has no external ground truth.

## [PURPOSE]

Give a measured picture of the player-identity problem so a safe fix can be planned: what the identity spine is and who writes it,
how many duplicate-identity groups there really are and what kind, where sources disagree about the same person, what the minted ids
look like after the 2026-09-14 hand edits, and what a stable id would need. This document recommends a direction and a phase plan;
it decides nothing and applies nothing.

## [DECISION]

Nothing is decided here. The owner decisions this audit needs are in [OPEN_QUESTIONS]. What the audit found:

### 1. The identity spine (files, writers, hand edits)

FILE|ROWS|KEY COLUMNS|WRITER|HAND EDITS (commit)
data/clean/players_canonical.csv|3,333|bsnpr_id, canonical_name, normalized_name, apellidos, nombre, birth_date, source_id|parse_players.py main() :1476|see next line
  hand edits of canonical: merges 7aeadef 990da5b 0982e40 33f3249 dd46c86; appended 991xxx rows 3fc6967 c6e4780 4b6437f b5c0c01 (no script in src/)
data/clean/player_aliases.csv|24,208|bsnpr_id, alias, normalized_alias, alias_type, source|build_aliases :1000, written :1483|990da5b 0982e40 33f3249
data/clean/player_id_map.csv|876 (352 ids)|obs_source, player_raw, club_raw, season, bsnpr_id, match_method, club_check|build_id_map :1263, written :1490|990da5b (re-point); 26117fd awards link
data/clean/player_bios.csv|152|bsnpr_id, notes_es, birthplace, roster_team, roster_year, jersey|merge_jugador05 :771, written :1503|990da5b 33f3249 dd46c86
data/clean/player_career_seasons.csv|5,802|bsnpr_id, season, team_raw, games, points, source_id|parse_jugador + merge_jug05 :525, written :1486|990da5b 0982e40 33f3249; e82c034 (transformation)
data/clean/player_roster_latinbasket.csv|744 (342 ids)|bsnpr_id, season, franchise_id, height_cm, position_raw|build_latinbasket_roster_clean.py|none since f7f6044
app/player_crosswalk.csv|391|curated_name, bsnpr_id, verdict, confidence, evidence|hand-curated|2670254 ffcaace 84243db 4b6437f
data/interim/player_review_queue.csv|506|obs_source, player_raw, season, candidate_ids, reason|build_id_map, written :1494|none; last touched 26117fd (see 6)
data/interim/jug05_review.csv|2|name, birth_date, collides_with|merge_jug05, written :1499|none
data/interim/jugador05_review.csv|3|name, birth_date, note|merge_jugador05, written :1507|none
data/interim/jugador05_dob_conflicts.csv|5|bsnpr_id, canonical_dob, jugador05_dob|merge_jugador05, written :1511|none
data/interim/player_dob_overrides.csv|10|bsnpr_id, old_dob, new_dob, basis|hand-curated (input to apply_dob_overrides :929)|6ae72f9
data/interim/jug05_xwalk.csv|37|jug05_name, jug05_birth_date, bsnpr_id|hand-curated (input, tier 0)|aab011c d6140fd
data/interim/jugador05_xwalk.csv|26|jugador05_name, jugador05_birth_date, bsnpr_id|hand-curated (input, tier 0)|39956e3 d6140fd
data/interim/latinbasket_match_*.csv|934 in 15 files|franchise_id, season, name_raw, candidate_ids, disposition|match_latinbasket_roster.py|none
  dispositions: 744 confirmed, 183 insufficient_evidence, 3 lead_for_tier1_triage, 3 likely_distinct, 1 source_discrepancy
web/data/players/<id>.json|3,333 files|one per canonical id|build_web_data.py|derived
web/data/index/players.json|3,333|id, name, career_seasons, first/last_season|build_web_data.py|derived
web/data/index/player_xwalk.json|163|curated name -> bsnpr_id|build_web_data.py from app/player_crosswalk.csv|derived

Canonical composition: 3,303 real ids (league `?id=N`, max 13344) + 30 minted (21 `990xxx` from jug05, 9 `991xxx`: 6 wikipedia_bsn, 3 pabellon_hof).
Columns filled: birth_date 2,018 (60.6%; format M/D/YYYY, not ISO), birth_city 599, nationality 590, position 658, first/last_season 1,093.
1,073 rows have a jugador.asp profile; 2,230 have no profile (enciclopedia data only).
id_map: 876 rows, all `single-source`; methods: 770 name+season_in_career, 53 surname+season+club, 31 name+season+trunc, 21 name+season+club, 1 title.
Review queue reasons: 287 season not in known span, 123 no name match, 72 several candidates none corroborated, 24 several corroborated.
The only script that writes all nine parse_players outputs is `main()`; N7 shows it does not reproduce the committed files.
No script in `src/` writes the 9 live `991xxx` canonical rows (UNVERIFIED how they were appended; see 6).

### 2. Tier-1 / Tier-2 counts: reproduced, and why the numbers differ

Definitions, applied to `players_canonical.csv`:
T1 exact = groups of >1 id with identical `canonical_name` string. T1 normalized = identical `normalized_name` (accent/case/punctuation
folded; same counts as the route slug grouping: 57 groups, 118 ids). T1 token = identical `norm_key(canonical_name)` (sorted tokens,
order-insensitive). T2 = identical `birth_date` string (blank ignored).

REV|ROWS|T1 exact|T1 normalized|T1 token|T2   (n/m = not measured at that revision)
7aeadef (Dalmau merge, before the scan)|3,356|57|59|n/m|136
990da5b (9 merges)|3,347|56|58|n/m|128
0982e40 (Berdiel)|3,346|56|58|n/m|128
33f3249 (13 merges)|3,333|55|57|n/m|128
HEAD (dd46c86 and later, unchanged)|3,333|55|57|59|128

Resolution of the 57/136 versus 59/128 discrepancy (reproduced, not assumed):
- The RECORDED 57 and 136 are T1-exact and T2 at revision 7aeadef (3,356 rows), the last state before the 2026-09-14 merge scan. Both reproduce exactly.
- The 23 merges in 990da5b, 0982e40 and 33f3249 removed 23 rows (3,356 -> 3,333): T1 exact 57 -> 55, T2 136 -> 128.
- The MEASURED 128 is T2 at HEAD (matches). The measured 59 is T1 by sorted-token key at HEAD (an order-insensitive definition, not the recorded one).
- Warning: T1 normalized at HEAD is also 57 (the same counts as the 57 shared route slugs). That is a coincidence with the recorded 57, not the same quantity.
- Groups that differ by definition at HEAD: accent/case only: 1144/990026 "Gonzalez, Jose" vs "Jose"; 2430/2431 "DeMarco" vs "Demarco".
  Token order only: 180/194 Gonzalez Arroyo vs Arroyo Gonzalez, Antonio; 1189/1192 Gonzalez Rodriguez vs Rodriguez Gonzalez, Jose a.
- Sizes at HEAD: T1 token = 59 groups (56 of 2 ids, 2 of 3, 1 of 4; 68 pairs, 122 ids). T2 = 128 groups, 153 pairs, 268 ids.
- One T1 group is a placeholder, not a person: 1730/1731/1732 "Notienenombre Notienenombre, Notienenombre" (the source's own "no name" value).
Any fix must fix ONE definition; this audit uses T1 token and T2 exact so nothing recorded is missed.

### 3. Classification of the duplicate-identity groups

Evidence tiers (rules stated exactly; these are heuristics, not ground truth, UNVERIFIED against any external source):
T1 pair (same token name key): (a) same person = same birth date, or >=1 identical career row (same season, city token, games, points).
(b) different people = both birth dates present and years differ by >=2, or careers >=15 years apart.
(c) uncertain = anything else. Subtypes: c1 one id is a data-less stub (no DOB, span, career, id_map, roster, bio, position, nationality) 41 pairs, of which
33 have adjacent ids (|diff|<=3); c2 only one id has a DOB 4; c3 DOBs within a year but unequal 1; c4 no DOBs, careers disjoint by <15 years 1.
T2 pair (same DOB, names differ): (a) shared surname token AND compatible given name (equal token or initial) AND surname sets nested (one contains the other);
(c) shared surname but given names differ 7, given name only 5, given name compatible but second surnames conflict 2; (b) no shared surname or given name 115.
T2 (b) pairs are birthday coincidences between unrelated names, NOT duplicates; they are reported only so nobody merges on a shared DOB.
Clusters = union-find over the (a) pairs of both tiers.

CLASS|GROUPS|IDS|CAREER ROWS|ID_MAP OBS|ROSTER ROWS|NOTE
(a) same person split across ids|17 clusters (24 pairs)|37 (20 surplus)|117|22|11|4 clusters split real career rows across 2-3 ids
(b) different people sharing a name|8 pairs (8 groups)|16|17|0|6|T1 only
(c) uncertain|61 pairs|116|128|25|17|41 of them are stub twins
union of (a)(b)(c)|-|168 (1 id in both a and b)|262 of 5,802|-|-|
T2 coincidences (not duplicates)|115 pairs|-|-|-|-|shared DOB, unrelated names
Groups by tier: T1 = 8 a, 8 b, 43 c (59). T2 = 15 a, 97 b, 13 c, 3 mixed (128).

(a) Same person split across ids: all 17 clusters (ids; DOB; career rows per id):
  A01|Arroyo, Alberto / Arroyo Bermudez, Alberto C. / Arroyo Bermudez, Carlos A.|24,35,273|7/30/1979|0,15,10|id_map obs 35:2 273:6, roster 273:3
  A02|Cruz, Alvin / Cruz Torres, Alvin|73,74|4/24/1982|6,18|id_map 74:5, roster 73:5 (recorded lead)
  A03|Gonzalez Arroyo / Arroyo Gonzalez, Antonio|180,194|12/7/1959|0,3|
  A04|Travieso Pena, Carmelo (4 ids)|344,345,346,347|9/5/1975|13,0,0,0|id_map 344:4
  A05|Llovet Ayala, Francisco|721,722|5/9/1980|5,0|721's 5 rows are 1965-1969: a row predates the birth year (mis-attached)
  A06|Lopez, Ivan / Lopez Rodriguez, Ivan|951,952|5/16/1985|1,13|roster 951:1 (recorded lead)
  A07|Gonzalez Rodriguez, Jose a. / Gonzalez, Jose a.|1189,1202|1/25/1959|0,0|1189 also pairs with 1192 (DOB 7/31/1963), class b
  A08|Vigo Castillo, Julio|1378,1379|7/12/1960|0,10|
  A09|Torres Mercado, Louis|1456,1457|9/20/1956|0,0|
  A10|Mackey, Malcolm|1545,1546|7/11/1970|2,0|
  A11|Herrera, Roberto / Herrera Garcia, Roberto|2056,2057|8/13/1974|0,8|id_map 2057:1
  A12|Ruiz, Roberto / Ruiz Fernandez, Roberto|2070,2071|12/9/1980|0,0|
  A13|Allred, Lance|2427,2911|2/2/1981|1,0|id_map 2427:1
  A14|Bermudez, Eduardo / Bermudez Acevedo, Eduardo|2512,2595|9/12/1986|0,1|
  A15|Clinch, Lewis / Clinch Bryant, Lewis|2674,2691|6/29/1987|0,0|
  A16|Brower, Jayson|13300,13301|1/1/1998|0,0|a Jan-1 date; weakest of the 17
  A17|Rivera, Raul / Rivera Ramos, Raul|1947,1948|8/31/1982|1,10|1947's one row is 1963 (age -19); roster 1947:2 (recorded lead)
Recorded leads cross-check: Cruz Alvin, Lopez Ivan, Rivera Raul = (a); Figueroa Carlos 286/2631 and Mitchell Tony 12976/13157 = (b);
Acevedo Angel 12944/45/46 = (c, three empty stubs). Figueroa 333 ("Figueroa Laboy, Carlos manuel") matches neither tier (name-shape only).
A merge would retire 20 ids, leave 17 survivors (richest id per cluster), and touch: 20 canonical rows, 145 alias rows, 65 game_box_player rows,
18 career rows, 11 roster rows, 6 id_map rows, 4 bios, 1 app crosswalk row.

(b) Different people sharing a name (T1 pairs; ids; evidence):
  B1|Figueroa, Carlos|286,2631|careers 1960-61 vs 2010-17 (49 years apart)
  B2|Rivera, Rafael|1886,2800|1967-70 vs 2013 (43 years apart)
  B3|Mitchell, Tony|12976,13157|DOB 4/7/1992 vs 8/7/1989
  B4|Jackson, David|2492,2847|DOB 8/12/1982 vs 8/20/1988
  B5|Rivera Cruz, Jesus|1038,2724|DOB 4/26/1958 vs 12/24/1990
  B6|Santos Lanzot, Jose|1169,1170|DOB 1/2/1978 vs 10/20/1960
  B7|Calcano Lopez, Rafael|1854,1855|DOB 8/31/1960 vs 12/7/1962
  B8|Gonzalez Rodriguez, Jose a.|1189,1192|DOB 1/25/1959 vs 7/31/1963

(c) Uncertain. Five largest by career rows (ids; DOB; span; career rows):
  C1|Lopez Quinones, Jose a.|1199 (1/14/1966; 18 rows) + 1200 (empty stub)|stub twin, adjacent ids
  C2|Reyes, Hector|865 (1963-68; 6 rows) + 873 (1956-60; 5 rows)|no DOBs, careers disjoint by 3 years (c4)
  C3|Lopez, Edgardo|517 (1964-72; 7 rows) + 518 (empty stub)|stub twin
  C4|Ortiz, Carlos|301 (7/9/1968; 6 rows) + 302 (empty stub)|stub twin
  C5|Alamo, Candido fret|267 (1974; 1 row) + 268 (11/17/1955; 1975-76; 2 rows)|only one id has a DOB (c2)
The 41 stub twins are the league's own duplicate rows (33 on adjacent ids). D1 ("never on name alone") keeps them out of (a):
the Berdiel stub 1638 was declined on the same ground (session, 2026-09-14). Recorded (session.md :4215-4226): of the same-surname minted candidates reviewed, 13 were merged and 5 declined.
Universe beyond Tier-1/2: grouping by (first surname, first given name) gives 226 groups / 535 ids; 171 of those groups
hold names Tier-1 does not see (e.g. Figueroa 333). How many are real duplicates is UNVERIFIED (not classified).

### 4. Fields that disagree across sources for the same person

Who wins today (parse_players.py):
- birth_date, birth_city, nationality, position, names: jugador.asp PROFILE if the id has one (`build_canonical` :960, `p.get(...) or e[...]`), else enciclopedia.
- jug05 (`merge_jug05`): never overwrites; enriches career rows; DOB matched within +/-7 days.
- jugador05 (`merge_jugador05` :771): FILLS EMPTY fields only (birth date, city, nationality, position); a DOB disagreement is logged, never applied.
- Curated `player_dob_overrides.csv` (`apply_dob_overrides` :929): applied only if the current value equals `old_dob`; 10 rows (9 high, 1 low: id 417 2/20/1948 -> 7/3/1979).
- Conflicts are logged for DOB (jugador05 vs canonical) only. Enciclopedia-vs-profile, position, nationality and city disagreements are silent.

FIELD|COMPARED|DISAGREE|EXAMPLES|SOURCES
birth_date enciclopedia vs profile|743 ids with both|2|2517 4/2/1986 vs 4/21/1986; 757 4/20/1972 vs 4/20/1970|profile wins, not logged
birth_date jugador05 vs canonical|145 matched, 128 with DOB|7 (5 logged, 2 not)|139 6/21 vs 6/9/1975; 911 7/3 vs 8/3/1973|canonical wins; 757 by override; 1271 only in my replay (UNVERIFIED why)
birth_date vs career season|794 dated with a first season|11 implausible|11 Velazquez first season 1974 age 9; 721 Llovet 1965 for a 1980 birth|first season implies age <14 or >50
position jugador05 vs canonical|144|21 no overlap, 17 partial|37 Alero vs Escolta; 49 Alero vs Delantero; 151 Delantero vs Centro|canonical wins (fill-only), not logged
nationality jugador05 vs canonical|120|6|93 Puerto Rico vs Republica Dom.; 498 USA vs New York|same
birth_city jugador05 vs canonical|137|14 differ on first token|93 Carolina vs Santo Domingo; 392 Bayamon vs Catano|same
name enciclopedia vs profile|233 with profile name|19 token sets differ|13011 Soto Rivera, Joseph vs Joseph R.; 13124 Arroyo Gonzalez, Carlos Andres vs Carlos|profile wins
height|341 ids, latinbasket only|21 ids with >1 height, 9 span >=3 cm|870 196/201; 2309 201/207; 2631 197/201|no second source in the spine
career games/points jug05 vs players|665 merged, 125 conflicts on 79 players|125|see merge_jug05_audit_spec.md|two rows kept
Other measured facts: 40% of the 2,018 dated players have a day <=12, so month/day order is ambiguous; 45 pairs of players share a DOB only after a month/day swap;
4 of the 10 overrides are recorded M/D transpositions. Canonical `nationality` mixes countries and birthplaces: New York 21, California 15, NY 12, Georgia 9,
Illinois 7, Florida 5, Texas 5, Michigan 5 (79 rows are US states), plus spelling variants (USA 93 / United States 6; Rep. Dominicana / Republica Dom.).
Position vocabularies differ (canonical Spanish: Armador Escolta Alero Delantero Centro; latinbasket G F C PG SG); 24 latinbasket players change position
across seasons (mostly G <-> PG). A hard canonical-vs-latinbasket position contradiction count was not computed (UNVERIFIED).
Height and weight ("Altura", "Peso") exist in the raw jugador.asp pages (the label "Altura" appears 200 times in the first 400 pages I scanned) and in jugador05, but no parser extracts them
into the spine; the only height in the repo is latinbasket. A jugador.asp-vs-latinbasket height check is possible but needs new parsing (coverage UNVERIFIED).

### 5. The 57 shared name slugs

The route `#jugadores/jugador/<slug>` (`app/bsn_archivo.html:8090-8096`) looks up the baked pool (`PINDEX.find`, curated names, name-sorted) first,
then `PALL.find` over `index/players.json` (sorted by id, canonical names) and opens the FIRST match. So the lowest id wins and every other member is
unreachable by URL. 57 slugs are shared: 118 players (54 pairs, 2 triples, 1 quad); 61 players cannot be opened by slug, 11 of them carry career/id_map/roster data.
In 11 groups another member has more data than the one the route opens (e.g. alamo-candido-fret, carter-maurice, farmer-anthony, figueroa-carlos,
ortiz-chris, ramirez-francis, santana-edson, smith-greg); in 7 of them the opened id is an empty stub.
Class of each slug group: 7 same person (a), 7 different people (b), 43 uncertain (c). Slugs that also collide with the baked pool are UNVERIFIED (pool not in the repo).
SLUG|CLASS|IDS|ROUTE OPENS|CAREER ROWS PER ID
  acevedo-angel|c|ids 12944,12945,12946|route opens 12944|career rows 0,0,0
  alamo-candido-fret|c|ids 267,268|route opens 267|career rows 1,2
  allred-lance|a|ids 2427,2911|route opens 2427|career rows 1,0
  brower-jayson|a|ids 13300,13301|route opens 13300|career rows 0,0
  calcano-lopez-rafael|b|ids 1854,1855|route opens 1854|career rows 0,0
  carter-maurice|c|ids 1605,12972|route opens 1605|career rows 0,0
  cepeda-eliz|c|ids 2400,990012|route opens 2400|career rows 1,0
  cestero-edwin|c|ids 543,544|route opens 543|career rows 0,0
  collazo-luis|c|ids 1471,1472|route opens 1471|career rows 0,0
  cortes-diaz-carlos|c|ids 280,281|route opens 280|career rows 0,0
  cunningham-dante|c|ids 13298,13299|route opens 13298|career rows 0,0
  de-jesus-efrain|c|ids 568,569|route opens 568|career rows 0,0
  delgado-antonio|c|ids 177,178|route opens 177|career rows 0,0
  farmer-anthony|c|ids 171,172|route opens 171|career rows 0,0
  figueroa-carlos|b|ids 286,2631|route opens 286|career rows 2,7
  gonzalez-jose|c|ids 1144,990026|route opens 1144|career rows 1,0
  gonzalez-roberto|c|ids 2054,2055|route opens 2054|career rows 0,0
  gonzalez-rodriguez-luis|c|ids 1480,1481|route opens 1480|career rows 0,0
  jackson-david|b|ids 2492,2847|route opens 2492|career rows 1,0
  jackson-quinonez-gregg|c|ids 822,823|route opens 822|career rows 0,0
  johnson-demarco|c|ids 2430,2431|route opens 2430|career rows 1,0
  llovet-ayala-francisco|a|ids 721,722|route opens 721|career rows 5,0
  lopez-edgardo|c|ids 517,518|route opens 517|career rows 7,0
  lopez-quinones-jose-a|c|ids 1199,1200|route opens 1199|career rows 18,0
  lugo-felix|c|ids 667,668|route opens 667|career rows 6,0
  mackey-malcolm|a|ids 1545,1546|route opens 1545|career rows 2,0
  martinez-vega-carlos|c|ids 294,295|route opens 294|career rows 0,0
  miller-kenneth|c|ids 1401,1402|route opens 1401|career rows 0,0
  miller-muriel-isaac|c|ids 925,926|route opens 925|career rows 0,0
  mitchell-tony|b|ids 12976,13157|route opens 12976|career rows 2,0
  notienenombre-notienenombre-notienenombre|c|ids 1730,1731,1732|route opens 1730|career rows 0,0,0
  ortiz-carlos|c|ids 301,302|route opens 301|career rows 6,0
  ortiz-chris|c|ids 377,13057|route opens 377|career rows 0,1
  pellot-rosa-edwin|c|ids 553,2388|route opens 553|career rows 0,0
  quinones-antonio|c|ids 183,184|route opens 183|career rows 0,0
  ramirez-francis|c|ids 709,710|route opens 709|career rows 0,3
  reyes-hector|c|ids 865,873|route opens 865|career rows 6,5
  rivera-cruz-jesus|b|ids 1038,2724|route opens 1038|career rows 0,0
  rivera-rafael|b|ids 1886,2800|route opens 1886|career rows 4,1
  rivera-ray|c|ids 1955,1956|route opens 1955|career rows 0,0
  robinson-thomas|c|ids 13297,13304|route opens 13297|career rows 0,0
  rosario-rich|c|ids 2008,2009|route opens 2008|career rows 0,0
  saldana-miguel|c|ids 1654,1655|route opens 1654|career rows 0,0
  santana-edson|c|ids 2358,990021|route opens 2358|career rows 0,0
  santos-lanzot-jose|b|ids 1169,1170|route opens 1169|career rows 0,0
  smith-greg|c|ids 12925,13199|route opens 12925|career rows 0,0
  sosa-carrion-isaac|c|ids 2818,2819|route opens 2818|career rows 5,0
  soto-luis|c|ids 2723,2725|route opens 2723|career rows 0,0
  stewart-kebu|c|ids 1386,1387|route opens 1386|career rows 0,1
  stone-diamond|c|ids 13315,13316|route opens 13315|career rows 0,0
  strickland-mark|c|ids 1587,1588|route opens 1587|career rows 0,0
  thompson-ronald|c|ids 2097,2338|route opens 2097|career rows 0,0
  torres-mercado-louis|a|ids 1456,1457|route opens 1456|career rows 0,0
  travieso-pena-carmelo|a|ids 344,345,346,347|route opens 344|career rows 13,0,0,0
  velez-ortiz-martin-jr|c|ids 1597,1598|route opens 1597|career rows 0,0
  vigo-castillo-julio|a|ids 1378,1379|route opens 1378|career rows 0,10
  williams-corey|c|ids 402,2738|route opens 402|career rows 0,0

### 6. Minted ids (990001+)

56 minted ids have existed; 30 are live; 26 were removed by 5 commits:
COMMIT|REMOVED|WHAT
d6140fd|2 (990041, 990042)|jug05_xwalk bridges, generator-run (mint 42 -> 40)
7aeadef|1 (991001)|Dalmau -> 1962, hand edit
990da5b|9 (990017 990018 990025 990030 990034 990038 991005 991006 991011)|9 birth-date-confirmed merges, hand edit
0982e40|1 (990001)|Berdiel -> 1666, hand edit
33f3249|13 (12 x 990xxx, 991004)|13 individually reviewed merges, hand edit
Live: 21 in `990xxx` (all wayback_bsnpr_jug05) and 9 in `991xxx` (6 wikipedia_bsn, 3 pabellon_hof). 19 have a DOB, 16 have career rows (54 rows in all);
they are referenced by 3 id_map rows, 1 roster row, 4 bios, and each has a web player file (30). Three live minted ids sit in a Tier-1 group with a real id:
990012 with 2400 (Cepeda, Eliz), 990021 with 2358 (Santana, Edson), 990026 with 1144 (Gonzalez, Jose).
- The `991xxx` rows have NO alias rows (9 canonical ids without aliases, all `991xxx`), so observations can never be matched to them, and no script in `src/` creates them.
- Minted ids are positional, not stable: `pid = 990000 + n` where n is the position in a name-sorted list of the jug05 records that matched nothing
  (`parse_players.py:654-657`, base at :371). Any change to the bridges or to matching renumbers every later id.
- Hand edits deleted rows in the outputs but not in the generator inputs, so regeneration re-mints them (N7). Control run: canonical 3,333 -> 3,325,
  aliases 24,208 -> 24,182, career 6,467 -> 6,505, id_map 876 -> 888, bios 152 -> 146, review queue 506 -> 494.
- Stale references: 14 rows of `player_review_queue.csv` still list 8 retired minted ids among their candidates
  (990001 990002 990003 990009 990020 990027 990028 990036); the queue was last written before the merges. In the id columns I scanned
  (bsnpr_id, candidate_ids, collides_with across data/clean, data/interim and app/player_crosswalk.csv) no other file references a retired minted id.

### 7. Design question: a stable, source-independent player id (NOT implemented)

Today `bsnpr_id` is one site's row number. It is not a person id: the league's own table holds duplicate rows (41 stub twins, 33 on adjacent ids), our minted ids are
positional, and merging retires ids with no trace. Requirements a stable id must meet:
1. Opaque: derived from no name, date or source key, so a corrected name/DOB never changes it.
2. Never reused, never deleted: a merge marks the loser `merged_into <winner>` and keeps it resolvable (tombstone / redirect).
3. Source keys are attributes, not identity: every source's key maps to a person id with provenance (PC3).
4. Decisions are data: merge / split / "not the same person" verdicts are curated input files that the generator READS, so regenerating reproduces the committed state (this is the N7 cure).
Sketch (names illustrative):
  player_ids.csv: person_id, status (active|merged), merged_into, decided_ref
  player_source_keys.csv: person_id, source (bsnpr_enciclopedia_id, bsnpr_jug05_token, jugador05_key, pabellon_slug, wikipedia_title, latinbasket_slug, wikidata_qid),
    source_key, first_seen, evidence, confidence, decided_by, decided_at
  player_identity_decisions.csv: decision_id, kind (merge|not_same|split), person_ids, evidence, decided_by, decided_at
Legacy mapping: existing real ids and the 30 minted ids are GRANDFATHERED as person ids (identity mapping, source key `bsnpr_enciclopedia_id` for real ids), so
`players/<id>.json`, cached files and the 391-row crosswalk keep working; new persons draw from a separate counter. Each of the 26 retired minted ids becomes a
`merged` row pointing at its survivor (the 5 recorded merge commits are the evidence). The 17 (a) clusters become `merge` decisions only when the owner approves them;
the 8 (b) pairs become `not_same` decisions so no later pass re-asks.
What the league would need to supply for a real crosswalk: (1) a registry export: league player id, full name with variants, birth date (ISO, day/month order stated),
birthplace, nationality, position, height, weight; (2) the league's own list of duplicate/merged ids (the adjacent stub pairs); (3) roster history: player id, season, team, jersey;
(4) player ids on box-score rows (today matched by name; session.md records 26% resolved pre-2007 and 74% modern, not re-measured); (5) a changelog when ids are merged. Failing that, external keys
(Wikidata QIDs, latinbasket ids) can be stored as extra source keys but cover only notable players.

### 8. Reach of a fix: web/ files and deploy

Merging only the 17 (a) clusters (20 retired ids) would change: `web/data/players/`: 20 files deleted and up to 17 rewritten (survivors that gain rows); `index/players.json`: 20 entries
removed and counts changed; `games/`: 56 files (65 box rows re-pointed from a retired id); `manifest.json` (source_digest, counts.players / player_files). `starting_five/`
holds 4 files that mention cluster ids but none mention a retired id (unchanged unless a survivor changes). Seven `data/clean` files and `app/player_crosswalk.csv` would change (canonical, aliases,
id_map, bios, career, roster, game_box_player). Because those files are digest inputs and `web/data` changes, the push DEPLOYS (Pages trigger `web/**`),
and returning visitors purge cached data.
Fixing the slug route (disambiguation) is an APP change: `app/bsn_archivo.html` -> byte copy `web/index.html` (`make site`), plus browser checks (Chromium + WebKit) of the 57 routes.
Changes confined to `data/interim/` (decision files, review queue, stale-reference cleanup) do not touch `web/` and would not deploy on their own.
`make parse-players` and `make sync-web-data` stay off-limits until regeneration is idempotent (N7).

## [RATIONALE]

- Two tiers, one union: Tier-1 (name) and Tier-2 (birth date) each miss what the other sees (Cruz Alvin, Lopez Ivan and Rivera Raul are Tier-2 only). Classifying pairs
  with the evidence each side actually has keeps D1 intact: no class (a) pair rests on a name alone.
- Stub twins stay (c): 41 pairs have no data on one side. Merging them would be a guess; they are also the cheapest to fix later once the league supplies its duplicate list.
- Different-people evidence is required before a pair is called (b): a DOB year gap of 2+ or careers 15+ years apart, so a transposed date (10 recorded overrides) is not read as two people.
- A birth date is used as evidence only when the year is reliable; 40% of dates have an ambiguous day, so DOB equality is treated as strong but not proof.
- The hand edits of 2026-09-14 were correct as identity work and wrong as engineering: they changed outputs the generator still reproduces differently. The fix is to make decisions
  data, not to repeat the edits.

## [ALTERNATIVES_REJECTED]

- Identity by name or slug (status quo route): 57 collisions, first match wins.
- A hash of (name, birth date) as the id: a corrected DOB or spelling (10 overrides, 5 open conflicts) changes the id; the placeholder name collides.
- Renumbering all ids sequentially: breaks `players/<id>.json`, cached data, the crosswalk and every external reference at once.
- Automatic fuzzy merging (Tier-3 name shape, 226 groups): violates D1; the Berdiel/Dalmau reviews showed real cases need career evidence.
- Fixing by regenerating from raw: not safe (N7) until decisions are inputs.
- Wikidata QIDs as the primary id: covers only notable players.

## [INTERFACES]

- Would change (not now): `src/parse_players.py` (read decision files; stop assigning positional ids), `src/verify_clean.py` (checks: no dangling ids, every merged id
  resolves, every canonical id has aliases), `tests/test_parse_players.py` (idempotence: regenerate equals committed), `src/build_web_data.py` (skip merged ids,
  redirect stubs if wanted), `app/bsn_archivo.html` (route disambiguation; only if the owner approves), new curated files under `data/interim/` or `data/clean/`.
- Unchanged by this audit: every file. The only new file is this spec (uncommitted).
- Drift guard: none for these files today; the reconcile drift-guard pattern (generator output equals committed rows) is the model for an identity guard.

## [OPEN_QUESTIONS]

Q1. Approve the 17 (a) clusters for merging, cluster by cluster? Recommended order: the 4 with split career data first (A01 A02 A06 A17), then the rest.
Q2. Survivor rule: richest id (career rows, then DOB, then id_map/roster) as used here, or lowest id?
Q3. Stub twins (41 pairs, 33 adjacent): leave, or merge when the league confirms? Should adjacency (|id diff| <= 3) be accepted as evidence?
Q4. Retire or keep the `bsnpr_id` column name once ids are person ids? (Recommendation: keep the column, document it as an opaque person id.)
Q5. Tier-3 (226 groups / 535 ids): in scope for triage, or only after Tier-1/2?
Q6. Placeholder `Notienenombre Notienenombre, Notienenombre` (1730-1732): keep as three unidentified players, or drop from the spine? They must never be merged.
Q7. The 9 `991xxx` rows have no aliases and no generator: add aliases, and where should their source data live so they can be rebuilt?
Q8. The 14 stale review-queue rows and 5 open jugador05 DOB conflicts: resolve in the same pass?
Q9. DOB day/month order: state M/D/YYYY as the canonical format in the spec and check the 45 swap-only pairs by hand?
Q10. Route: disambiguate duplicate slugs as `<slug>-<id>` (app change, browser checks) or resolve duplicates first so collisions disappear?
Q11. Request the league registry, its duplicate-id list and box-score player ids (see 7); who asks?
Q12. Height/weight: extract from jugador.asp and jugador05 raw so cross-source height checks become possible (UNVERIFIED coverage)?
Not verified: how the 9 `991xxx` rows were created; whether any T2 (b) pair is a DOB copied to the wrong row; slug collisions with the baked pool;
how many Tier-3 groups are real duplicates; why 1271 disagrees in a jugador05 replay but not in the committed log; hard position contradictions.

## Addendum 2026-09-21: route fix (Q10) and owner rulings

- **Route fix, applied (staged, uncommitted at the time of writing).** Section 5's first-match route is replaced:
  the plain slug opens the richest member, every other member is `<slug>-<id>`, computed in the app when `PALL`
  lands (`app/bsn_archivo.html:4343`). Baseline before: 57 of 57 shared routes opened the lowest id.
- **Results.** 11 plain slugs moved to the richest member and 46 are unchanged. All 61 previously unreachable
  players now open by `<slug>-<id>` and survive a reload; all 118 are reachable. 3,333 distinct URLs; the curated
  pool has 378 names and 0 collisions with them (this resolves the section 5 UNVERIFIED item). Verified in Chromium
  and WebKit.
- **Deploy.** `web/index.html` only; the digest is unchanged, so there is no cache purge.
- **Rulings.**
- **Q1** approve clusters in batches. Batch 1 = A01, A02, A06. A17 only after its 1963 row is reviewed. Hold A05
  (rows predate the 1980 birth) and A16 (Jan-1 date). The rest are reviewed together.
- **Q2** survivor = richest id (career rows, then DOB, then id_map/roster), ties to the lowest id. Retired ids stay
  resolvable as merged_into tombstones.
- **Q3** stub twins: leave them. Adjacency is not evidence. Raise with the league.
- **Q4** keep the bsnpr_id column name, documented as an opaque person id.
- **Q5** Tier-3 is out of scope until Tier-1/2 are settled.
- **Q6** keep the three Notienenombre rows, never merge them; relabel later.
- **Q7** leave the 991xxx rows until the identity refactor (curated input file).
- **Q8** the stale review-queue rows and the 5 open DOB conflicts: resolve in one interim-only pass.
- **Q9** M/D/YYYY is canonical; hand-check the 45 swap-only pairs later.
- **Q10** route fix now (this change).
- **Q11** the owner asks the league for the registry, its duplicate-id list, roster history, box-score player ids
  and a merge changelog.
- **Q12** height/weight deferred until after the meeting.
- **Recorded for the merge phase.** The in-app rule can shift when survivors gain rows, so pin slugs in data then.
  11 of the 20 retired ids have a plain slug different from the survivor's and need a redirect map; retired ids
  resolve through merged_into tombstones.

## Addendum 2026-09-21: batch 1 merges applied

- **Decisions (owner, 2026-09-21; `data/clean/player_identity_decisions.csv`, 4 rows).** D-ID-001 merge 73 -> 74;
  D-ID-002 merge 951 -> 952; D-ID-003 merge 24 -> 35; D-ID-004 not_same 35 and 273. Tombstones
  (`player_id_tombstones.csv`, 3 rows): 73 -> 74, 951 -> 952, 24 -> 35. A retired id is never reused and stays
  resolvable.
- **Evidence for the merges.** Recorded in `docs/specs/cluster_evidence_batch1.md` (staged with this change). 73 and
  951 were dropped by the league's own enciclopedia after 2008-03-07. 24 -> 35 was conditional on the jersey: 24 and
  35 have the identical enciclopedia jersey in 76 of 76 captures (blank, then 11), and 35 wore 10 at Santurce (box
  2001-03) and 11 at Fajardo (box 2008), so the difference follows the team change. The Santurce 2006 line of 24's
  bio against 35's Guaynabo 2006 row stays UNVERIFIED.
- **35 and 273 are different people (not_same).** They share 20 Santurce games in the box scores (2001: 8, 2002: 5,
  2003: 7), jerseys 10 and 7, minutes 1-17 against 20-38. 273 matches Carlos Alberto Arroyo Bermudez (DOB 7/30/1979,
  Santurce No. 7), source en.wikipedia.org/wiki/Carlos_Arroyo, read from search results and not independently
  fetched (project.md L2). The audit's Tier-2 rule over-linked A01 through the initial-compatibility test. Player
  273's records are untouched.
- **A17 (1947/1948): finding only, no decision and no action.** 1947's DOB, bio and its 2 roster rows were inherited
  from 1948's person: the DOB came from an early enciclopedia listing and a jugador05 bio attached by exact name,
  and the roster rows sit on the lower id by the tie-break rule. 1947's own profile has an unknown DOB and one 1963
  row.
- **What changed in the data.** Canonical 3,333 -> 3,330; aliases 24,208 -> 24,203 (13 re-pointed, retired canonical
  names kept as `merged_name`, 5 duplicates dropped); career rows 5,802 -> 5,796; roster 744 and bios 152 (6 and 2
  rows re-pointed). Merged pairs 665 -> 667, stat conflicts 125 -> 126 (79 -> 80 players), trade pairs 276
  unchanged. `game_box_player`, `player_id_map` and the crosswalk had no row for a retired id.
- **Redirect design.** `build_web_data.py` writes `web/data/index/player_redirects.json` from the tombstones: `{ids:
  {24: 35, 73: 74, 951: 952}, slugs: {arroyo-alberto, arroyo-alberto-24, cruz-alvin, cruz-alvin-73, lopez-ivan,
  lopez-ivan-951}}` and counts it in the manifest (`player_redirects`: 3). A redirect key that a live player could
  hold stops the build. The app loads the file in `hydrate()`, and the router tries the curated pool, then `PSLUG`,
  then the redirects: it replaces the URL with `history.replaceState` (Back does not loop) and opens the survivor.
  `openArchivePlayer` and `showPlayer` remap a retired id through `PREDIR.ids`. `buildPlayerSlugs` and the "Mismo
  nombre" line are unaffected: none of the six ids was in a shared-slug group.
- **Deploy.** `web/data`: 24, 73 and 951 deleted; 35, 74 and 952 rewritten; `index/players.json`, `manifest.json`
  and the new `player_redirects.json` change; no games, seasons or other player file. The two curated files are now
  digest inputs, so `source_digest` goes `1832f6cda8cf` -> `048e92ee36a9` and returning visitors purge their cached
  data once (checked in both engines). `web/index.html` is the byte copy of the app.
- **Found while checking (recorded, not fixed).** The enciclopedia parser reads the birth-date column only under the
  header "Nació"; 75 of 77 captures write "Nacio", so only 2 blank canonical DOBs are affected (ids 130 and 556).
  jugador05 bios are attached to canonical rows by exact name, which put the bios of 24, 951 and 1947 on stubs.
  `player_roster_latinbasket.csv` is not in `SOURCES` (an existing gap: a roster-only change would not change the
  digest).
