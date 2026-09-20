# MERGE_JUG05_AUDIT — blast radius of the career-row dedup key in `merge_jug05()`

Audit date 2026-09-20. READ-ONLY: no code, CSV, or web/ change. State: HEAD `dd8df7c`, working tree clean.
Every number and line reference below was re-read from the files or recomputed from the data in this phase.
Anything not verified directly is tagged UNVERIFIED. Nothing had been applied when this was written; the
decisions were applied afterwards (section 5). The audit text itself is as run.
Severity: HIGH = wrong data live on the site. MED = latent risk. LOW = cosmetic.

[PURPOSE]

`docs/session.md:4991` records a tracked bug: `merge_jug05()` can write the same real player-season
twice when the two Wayback sources spell the team differently ("blast radius unknown"). This spec measures
it: where the key is built, how many rows it duplicates, which of those are true duplicates, what else uses
the same logic, and what a fix would change on the live site. It also records the owner's recommended
decision on scope (section 1), which narrows the fix the audit first proposed.

[DECISION]

## 1. Owner decision (2026-09-20; APPLIED in a8aa002 and e82c034, see section 5)

    D1  Merge a cross-source pair only when the stats are identical (same games and same points).
        That is class (a): 665 groups = 628 in franchises the city map resolves + 37 in franchises it lacks
        (Cayey 19, Aguadilla 11, Villalba 6, Cabo Rojo 1).
    D2  Leave the 125 stat-conflict groups (class c) as two rows. Log both stat lines to
        data/interim/jug05_career_conflicts.csv and adjudicate later with a third source.
        jug05 has the higher points in 55 of them, the players source in 51, and 19 have equal points but
        different games. There is no blanket preference rule.
    D3  Keep the 276 trade pairs (189 players; one player-season, two different franchises) separate,
        and pin that with a test.
    D4  Key on the city token (last comma-part of normalize(team_raw)), not on resolve_club alone.
        resolve_club alone finds 756 of the 790 groups and misses 34.
    D5  Out of scope: identity triage (Tier-1 and Tier-2 duplicate players) and J16 (franchises the city
        map lacks). Neither is folded into this fix.
    D6  On a merge the players row survives (owner, 2026-09-20; this settles the working assumption below).
        Every merged pair is logged to data/interim/jug05_career_merged.csv with the columns pid, season,
        franchise_id, games, points, players_source_url, jug05_source_url, so the cross-source corroboration
        and the dropped jug05 source_url are preserved. 665 rows; franchise_id is blank for the 37 pairs in
        franchises the city map lacks. The file is tracked, not published and not a digest input, so it adds
        no web/ file. Section 2 and [INTERFACES] were written before D6 and list only the conflicts file.

Working assumption, not stated by the owner: when a pair is merged, the `players` row survives and the
`jug05` row is skipped (the stats are identical, so no value changes; the team string shown does).

## 2. Predicted effect of the narrower rule (recomputed; confirmed when built, actuals in section 5)

    data/clean/player_career_seasons.csv   6,467 -> 5,802 rows (-665); jug05 rows 1,118 -> 453, players rows 5,349 unchanged
    data/interim/jug05_career_conflicts.csv   new, 125 rows (tracked directory; not published, not a digest input)
    built career rows across web/data/players   6,815 -> 6,150
    web/data files that change: 105 x players/<id>.json + index/players.json + manifest.json = 107 files
      index/players.json: career_seasons changes for the same 105 players, sum -665
      manifest.json: source_digest changes (player_career_seasons.csv is a digest input)
    unchanged: seasons/, games/, starting_five/, franchises.json, and the 1 player whose only duplicates are conflicts
    a push containing these web/ files deploys and purges visitors' cached data once

Residual after the narrow rule: the 125 conflict groups (79 players; seasons 2000: 17, 2001: 51, 2002: 18,
2003: 3, 2005: 36) stay visible as two rows until adjudicated. 78 of those 79 players are also among the 105.
Class (a) pairs in the built career[]: 642 distinct (player, season) pairs; `stats` sits on exactly one row in
83, on neither in 559, on both in 0; no roster object in any. build_career_rows_by_pid attaches stats to the
first row of a season and base rows precede jug05 rows, so the surviving players row should keep its stats
(UNVERIFIED until built). Staging data/clean triggers the pre-commit hook (`.githooks/pre-commit:25`), which
needs the rebuilt web/data staged. data/interim alone does not trigger it.

## 3. Findings J1-J16 (audit as run). J12-J15 were proposals under the broad rule; see section 1

J1 | location
    merge_jug05 is src/parse_players.py:386-537 (def :386; the return statement is :536-537).
    The nested _union_career is :452-463. main() calls it once, at :1315, after parse_jugador() :1310 and
    before build_id_map :1324 and the CSV write :1336. No test references it (grep of tests/: 0 files).

J2 | key (HIGH)
    have = {(r["bsnpr_id"], int(r["season"]), normalize(r["team_raw"])) for r in career}     (:408)
    k = (pid, yr, normalize(team))                                                          (:455)
    normalize (:92-96) lowercases, strips accents and quotes, and keeps commas, so "caguas" != "criollos, caguas".
    The key holds no source and no franchise, so the same real season under two spellings is two keys.

J3 | reproduction, player 1995 (HIGH)
    2002  "CAGUAS"            wayback_bsnpr_jug05     23 games  53 pts   key ('1995', 2002, 'caguas')
    2002  "Criollos, Caguas"  wayback_bsnpr_players   23 games  53 pts   key ('1995', 2002, 'criollos, caguas')
    2003 (25/199) and 2004 (29/511) repeat the same shape. Both spellings resolve to criollos_caguas.
    jug05 row:    https://web.archive.org/web/20061119230912id_/http://www.bsnpr.com/jug05.asp?r2=462686RWYM&r3=00050&r=00024&e=CAGUAS
    players row:  https://web.archive.org/web/20170715115934id_/http://www.bsnpr.com:80/jugadores/jugador.asp?id=1995&e=

J4 | producers and consumers
    Base rows: parse_jugador() -> wayback_bsnpr_players, 5,349 rows. Appended rows: parse_jug05() (:315) ->
    wayback_bsnpr_jug05, 1,118 rows. Readers of the CSV: build_web_data.py:615 (no dedup), parse_games.py:54-55
    (season sets), parse_players.py:1150 and :1160 (season and club sets), match_latinbasket_roster.py:89 (a set of
    pid, fid, season). Duplicates are inert for the set-based readers. The right-shaped key already exists at
    build_latinbasket_roster_clean.py:107-110: (bsnpr_id, season, franchise_id).

J5 | Manatí interaction: none
    merge_jug05 calls no resolver. jug05 rows span 1980-2005 and none contains "manat". All Manatí rows are
    2015-2016, all from the players source. Commit 9a458b8 changed two resolvers, not this key. The F2 Manatí
    duplicates were a different mechanism (the latinbasket roster join on franchise_id).

J6 | impact (HIGH: wrong data live on 106 player pages)
    player_career_seasons.csv has 6,467 rows. Cross-source duplicate groups by (player, season, city token): 790.
    Every group is exactly 2 rows, one players and one jug05. 106 players, 26 seasons (1980-2005).
    753 are franchise-resolved; the built web/data/players JSON holds the same 753 groups (0 differences).
    37 are in franchises absent from city_franchise_map.csv. 790 of the 1,118 jug05 rows (71%) duplicate a
    players row.

J7 | distribution, the 753 franchise-resolved groups (628 class a + 125 class c)
    Top 10 franchise_id: criollos_caguas 79, vaqueros_bayamon 78, leones_ponce 67, piratas_quebradillas 67,
    cangrejeros_santurce 60, atleticos_san_german 55, titanes_morovis 52, brujos_guayama 52, indios_mayaguez 48,
    capitanes_arecibo 42 (20 franchises in all).
    By 5-year bucket: 1980-84 5, 1985-89 20, 1990-94 93, 1995-99 204, 2000-04 391, 2005 40 (peak 89 in 2004).
    Top players by duplicate seasons: 1575 (25), 989 (19), 498, 555, 1011 and 1462 (18 each), 509 (17), 1970 (16),
    2290 (15), 1127 (14). 61 players have 5 or more.

J8 | classes
    (a) same franchise, format-only, identical games and points: 665 (628 resolved + 37 unresolved).
    (b) legitimate two stints in one season for the same franchise: 0. No same-source repeat exists anywhere.
        Legitimate multi-club seasons exist but are different franchises, so they are not key collisions:
        276 (player, season) pairs, 189 players.
    (c) same franchise, format differs, stats disagree: 125. Games equal in 22, points equal in 19.
        jug05 points higher in 55, players points higher in 51, equal points with different games in 19.

J9 | stats and roster placement, all 790 groups (758 distinct player-season pairs in the built career[])
    `stats` on exactly one row in 129 pairs, on neither in 629, on both in 0. No pair carries a roster object.

J10 | other merge steps (MED, latent)
    Only merge_jug05 uses a raw team string as a dedup key (:408 and :455). merge_jugador05 (:624) is
    enrich-only and never touches career rows. build_id_map (:1116) uses season and club sets. parse_jug05 dedups
    exact tuples only (0 same-source duplicates in the data). build_career_rows_by_pid does no dedup and inherits
    the CSV. Any future source appended to `career` needs the same key.

J11 | identity backlog: a different problem, not folded
    The key includes the player id, so merge_jug05 cannot see one person under two ids. 0 of the 106 affected
    players is a minted 990001+ id (16 minted ids have career rows, all jug05-only). Recomputed Tier-1 and Tier-2
    groups are 59 and 128 against 57 and 136 recorded, with no stored list, so the definitions may differ.
    Overlap with those recomputed groups: Tier-1 0, Tier-2 17 of 106. UNVERIFIED.
    Note for later: when triage merges two ids, their career rows will collide on this key.

J12 | fix (a), proposed under the broad rule; superseded by D4
    Key on a resolved franchise with a city-token fallback. Measured: the city token finds all 790 groups and
    has 0 groups whose rows resolve to more than one distinct franchise; resolve_club alone finds 756.

J13 | fix (b), retained as D3
    Never merge same-source rows and never merge rows that resolve to different franchises. Pin the 276 trade
    pairs with a test.

J14 | fix (c), proposed under the broad rule; REJECTED by D2
    The audit proposed keeping the players row for all 125 conflicts. The owner keeps both rows instead, so no
    jug05 value is discarded. Which source is more accurate is UNVERIFIED (see [OPEN_QUESTIONS]).

J15 | web impact under the broad rule; superseded by section 2
    Merging all 790 groups would have changed 108 web files and taken the built career rows to 6,025.

J16 | adjacent gap, out of scope (LOW-MED)
    build_web_data's city-only resolver leaves 181 career rows with franchise_id null: Tiburones, Aguadilla 37;
    Toritos, Cayey 36; Tainos, Cabo Rojo 25; CAYEY 24; Caciques-Gallitos, Humacao-Isabela 17; Avancinos,
    Villalba 14; others. city_franchise_map.csv lacks AGUADILLA, CAYEY, VILLALBA and CABO ROJO. This is why 37
    duplicates escape a franchise-keyed count.

## 4. Examples (each pair re-read from the CSV; format: player | season | franchise | rows as source games/points)

    (a) format-only, identical stats
    EX-a1 | 1995 | 2002 | criollos_caguas        | "CAGUAS" (jug05 23/53) vs "Criollos, Caguas" (players 23/53)
    EX-a2 | 158  | 2003 | indios_mayaguez       | "Indios, Mayaguez" (players 11/9) vs "MAYAGUEZ" (jug05 11/9)
    EX-a3 | 35   | 1996 | cariduros_fajardo     | "Cariduros, Fajardo" (players 12/20) vs "FAJARDO" (jug05 12/20)
    EX-a4 | 35   | 1998 | cangrejeros_santurce  | "Cangrejeros, Santurce" (players 10/17) vs "SANTURCE" (jug05 10/17)
    EX-a5 | 50   | 1992 | leones_ponce          | "Leones, Ponce" (players 14/13) vs "PONCE" (jug05 14/13)

    (b) legitimate multi-club seasons: different franchises, not key collisions
    EX-b1 | 37   | 2016 | "Atenienses, Manati" (players 11/139) and "Brujos, Guayama" (players 26/378)
    EX-b2 | 42   | 2015 | "Cangrejeros, Santurce" (11/115) and "Indios, Mayaguez" (24/270)
    EX-b3 | 81   | 2006 | "Atleticos, San German" (13/126) and "Maratonistas, Coamo" (13/136)
    EX-b4 | 89   | 1974 | "Capitanes, Arecibo" (1/0) and "Indios, Mayaguez" (22/318)
    EX-b5 | 119  | 1990 | "Brujos, Guayama" (21/352) and "Polluelos, Aibonito" (8/118)

    (c) same franchise, format differs, stats disagree
    EX-c1 | 1737 | 2005 | cangrejeros_santurce  | "Cangrejeros, Santurce" (players 30/428) vs "SANTURCE" (jug05 1/16)
    EX-c2 | 2074 | 2005 | leones_ponce          | "Leones, Ponce" (players 32/635) vs "PONCE" (jug05 14/229)
    EX-c3 | 35   | 2001 | cangrejeros_santurce  | "Cangrejeros, Santurce" (players 12/14) vs "SANTURCE" (jug05 12/26)
    EX-c4 | 37   | 2001 | indios_mayaguez       | "Indios, Mayaguez" (players 5/16) vs "MAYAGUEZ" (jug05 4/16)
    EX-c5 | 37   | 2005 | vaqueros_bayamon      | "BAYAMON" (jug05 13/253) vs "Vaqueros, Bayamon" (players 28/408)

## 5. Status (added 2026-09-20; findings above unchanged)

Status as of `e82c034` (pushed 2026-09-20, deployed by Pages run 35539162083). Format: ID | status | commit | note

    D1  RESOLVED | e82c034 | 665 identical-stats pairs merged (628 franchise-resolved + 37 in franchises the city map lacks)
    D2  RESOLVED | e82c034 | 125 stat-conflict groups kept as two rows and logged to jug05_career_conflicts.csv
    D3  RESOLVED | e82c034 | 276 trade pairs untouched, pinned by tests/test_career_dedup.py
    D4  RESOLVED | e82c034 | keyed on the city token; a bare city names no franchise, so it is no evidence against a named row
    D5  RESOLVED | e82c034 | kept out of scope as decided: identity triage and J16 were not touched
    D6  RESOLVED | e82c034 | the players row survives; every merged pair is logged to jug05_career_merged.csv
    Prerequisite | a8aa002 | Tier-2 stats now attach to the career row of the recorded team (build_web_data.py:608),
                              which the dedup would otherwise have broken in 5 trade seasons

Predicted against built (section 2), all confirmed:

    player_career_seasons.csv rows          6,467 -> 5,802   (predicted 5,802)
    built career rows, web/data/players     6,815 -> 6,150   (predicted 6,150)
    web files changed by e82c034            107 = 105 player files + index/players.json + manifest.json (predicted 107)
    merged 665, conflicts 125, trade pairs 276, 37 merged rows with a blank franchise_id (all as decided)
    lossless against a8aa002: 51 stats objects moved onto their same-team twin with identical content;
        0 seasons lost stats, 0 gained, 0 non-null fields dropped, 0 values changed
    correction to section 2: it said the surviving row "should keep its stats (UNVERIFIED)"; measured, the stats
        move onto it (the 51 above), because the site build puts a season's stats on the first row of the team

Differences from what the sections above proposed:

    the fold lives in src/parse_players.py and merge_jug05 calls it at the end; the raw-string key stays as a guard
    the franchise guard compares only rows that both name a franchise. The first version blocked 16 groups (a dry
        run gave 650 merged and 124 conflicts instead of 665 and 125): a bare city ("GUAYNABO") resolves to the
        city-map franchise while "Conquistadores, Guaynabo" resolves to its own nickname key
    both logs use `bsnpr_id` (not `pid`) and carry jug05_retrieved_at; the tests are a new file, not test_parse_players.py

Superseded:

    The prediction that regenerating leaves every identity output unchanged (Q4, and the regeneration step in
    [INTERFACES]) is FALSE. A control run of `make parse-players` on unmodified code changed all 9 files it writes
    (docs/session.md N7). The fix therefore did not regenerate: the identity outputs were untouched by construction.
    Of the 33 data/clean files only player_career_seasons.csv changed; the other 32 are byte-identical to HEAD.
    J12, J14 and J15 stay superseded by section 1, as marked in section 3.

Open:

    Q2, Q3  125 stat conflicts on 79 players remain visible as two rows (seasons 2000: 17, 2001: 51, 2002: 18,
            2003: 3, 2005: 36) until a third source adjudicates them
    J16     181 career rows had a null franchise_id at audit time; 144 remain (the dedup merged 37 duplicates in them)
    J11     recomputed tier counts 59 and 128 do not match the recorded 57 and 136; UNVERIFIED
    651/2001  the Tier-2 record's team (Titanes de Morovis) has no career row that season, so its stats sit on the
            first row (the fallback): found while building a8aa002
    main()  parse_players main() has never executed the new log-writer wiring (source-checked by a test only):
            UNVERIFIED by execution; the first real run must check both logs

[RATIONALE]

The defect is in the key, not in the data: the two sources describe one real season, one as "Nick, City" and
one as a bare city, and `normalize()` keeps them apart. When the numbers are identical (665 groups) the two rows
are the same record and merging loses nothing but a second spelling. When they differ (125 groups) the audit
cannot tell which source is right: jug05 is higher in 55, the players source in 51, and the point gaps run up to
412 (jug05 minus players: -412 to +155). Merging those would silently discard one source's numbers, so they stay as two rows and
are logged for adjudication with a third source (PC1, PC4: show the gaps, do not resolve them quietly).
The conflicts cluster in seasons 2000-2003 and 2005 (none in 2004; 2001 has 51). The cause is UNVERIFIED; a
partial-season jug05 snapshot is one guess (player 37, 2005: 13 games against 28), not a finding.
The city token is the right key because it is what the two spellings share. It found all 790 groups, and the
clean false-merge check found 0 city-token groups whose rows resolve to more than one distinct franchise.
The residual risk is a player with two franchises from one city in one season and identical stats across sources.
The proposed merge is cross-source only, which guards that case; none exists in the data today.

[ALTERNATIVES_REJECTED]

    - A blanket preference (always keep players, or always keep jug05) for all 790 groups. The 55 versus 51 split
      gives no evidence for either, and it would discard real numbers.
    - Keying on a resolved franchise only (resolve_club, or the build_web_data resolver). resolve_club finds 756
      groups and the city-map resolver 753; both miss the franchises the city map lacks.
    - Merging the 125 conflicts and keeping the players row (audit finding J14). Rejected by the owner (D2).
    - Deduplicating in build_web_data instead of the merge step. The clean CSV would stay duplicated, against the
      raw -> interim -> clean flow (PC5).
    - Adding a confidence column to player_career_seasons.csv to mark conflicts. A schema change (P2), and the
      file already lacks a confidence column today. Deferred.
    - Folding this fix into identity triage or into J16. Different problems (D5).

[INTERFACES]

As built (commit e82c034; prerequisite a8aa002). Written as a proposal; corrections are marked.

    src/parse_players.py  fold_cross_source_career (:443), city_token (:408), write_career_logs (:504)
        ONE shared function decides every fold, keyed on (bsnpr_id, season, city token). city_token is the last
        comma-part of normalize(team_raw). It folds a jug05 row only into a row of another source, only when games
        AND points are identical, and the players row survives. Different stats: both rows stay and a conflict is
        logged. Two rows that both name a franchise and resolve apart are never folded (a bare city names none).
        It never folds two rows of one source. Pure: it does not mutate its input and returns (kept, merged, conflicts).
    src/parse_players.py  merge_jug05 (:525)
        Calls the fold once at the end (:675) and updates `career` in place; the returned dict gains `merged` and
        `conflicts`. Correction: the proposal replaced the seen-set and the key with the city-token key. The
        raw-string key survives (:550, :597) only as the guard against the same jug05 row being offered twice.
    src/parse_players.py  main() (:1464, :1502)
        Passes j05["merged"] and j05["conflicts"] to write_career_logs. Checked by a test that reads the source,
        never executed here (UNVERIFIED by execution; see section 5).
    src/apply_career_dedup.py  main (:29)
        Applies the same function to the committed data/clean/player_career_seasons.csv IN PLACE. Deterministic and
        idempotent: a second run leaves the CSV and both logs byte-identical. `--check` writes nothing and exits 1
        when a pair would merge. It rewrites the CSV only when something merges, and kept rows stay in file order.
        Run as `python -m src.apply_career_dedup [--check]`; it is not a Makefile target.
    data/interim/jug05_career_merged.csv  (665 rows)
        bsnpr_id, season, franchise_id, games, points, players_source_url, jug05_source_url, jug05_team_raw,
        jug05_retrieved_at
        franchise_id is blank for the 37 pairs in franchises the city map lacks. New pairs are ADDED to those already
        logged, so a second run cannot empty the file.
    data/interim/jug05_career_conflicts.csv  (125 rows)
        bsnpr_id, season, city_token, team_raw_a, source_id_a, games_a, points_a, source_url_a,
        team_raw_b, source_id_b, games_b, points_b, source_url_b, jug05_retrieved_at
        a is the players row and b the jug05 row. Recomputed from the rows that remain, and overwritten each run.
    jug05_retrieved_at  (both logs)
        The fetch time of the jug05 row: the removed row in the merged log, row b in the conflicts log. It is
        provenance the wayback timestamp inside the URL does not carry. Blank if none (0 blank today).
    tests/test_career_dedup.py  (new file, 32 tests; the proposal put them in tests/test_parse_players.py)
        Rule fixtures, merge_jug05, the apply script, a log-writer round trip, and pins on the committed files for
        665 / 125 / 276 and for player 1995.
    Regeneration: CORRECTED. The proposed step (`make parse-players`, then `make build-web-data`) was wrong and is
        superseded. Regeneration is NOT idempotent at HEAD: a control run on unmodified code changed all 9 files it
        writes (docs/session.md N7), because the committed identity outputs carry hand edits (commits 0982e40,
        990da5b, 33f3249 and dd46c86, all 2026-09-14). The fix was applied as a transformation of the committed CSV
        instead, so the identity outputs were untouched by construction: of the 33 data/clean files only
        player_career_seasons.csv changed. Do not run `make parse-players` at HEAD.
    Checks: src/verify_clean.py has no check that counts player_career_seasons rows, so nothing pinned 6,467.
        tests/test_build_web_data.py:169 documents the quirk in a comment that is now stale; the test still holds.

[OPEN_QUESTIONS]

    Q1  RESOLVED by D6: the players row survives, and every merged pair is logged to
        data/interim/jug05_career_merged.csv.
    Q2  Which third source adjudicates the 125 conflicts, and why they cluster in 2000-2003 and 2005. UNVERIFIED.
    Q3  The 125 conflict seasons (79 players) stay visible as two rows on the site until adjudicated. Accept that?
    Q4  SUPERSEDED (the prediction was false): that regeneration leaves every identity output unchanged. See
        [INTERFACES] and section 5. The fix did not regenerate; the identity outputs were untouched by construction.
    Q5  RESOLVED: the predicted counts were built and confirmed; the actuals are in section 5.
    Q6  RESOLVED: `docs/session.md` now records the fix (the PHASE_2C log). The old entry at `:4991` and the addendum
        at `:5022-5035` are left in place as history.
