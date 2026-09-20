# MERGE_JUG05_AUDIT — blast radius of the career-row dedup key in `merge_jug05()`

Audit date 2026-09-20. READ-ONLY: no code, CSV, or web/ change. State: HEAD `dd8df7c`, working tree clean.
Every number and line reference below was re-read from the files or recomputed from the data in this phase.
Anything not verified directly is tagged UNVERIFIED. Nothing here has been applied.
Severity: HIGH = wrong data live on the site. MED = latent risk. LOW = cosmetic.

[PURPOSE]

`docs/session.md:4991` records a tracked bug: `merge_jug05()` can write the same real player-season
twice when the two Wayback sources spell the team differently ("blast radius unknown"). This spec measures
it: where the key is built, how many rows it duplicates, which of those are true duplicates, what else uses
the same logic, and what a fix would change on the live site. It also records the owner's recommended
decision on scope (section 1), which narrows the fix the audit first proposed.

[DECISION]

## 1. Owner decision (recommended, 2026-09-20; NOT yet applied)

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

## 2. Predicted effect of the narrower rule (recomputed; UNVERIFIED until built)

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

Proposed, not applied.

    src/parse_players.py  merge_jug05 (:386-537)
        Replace the seen-set at :408 with a mapping from (pid, season, city_token) to the stat lines already present,
        and use the same key at :455. city_token = last comma-part of normalize(team_raw) (normalize is :92).
        Collision with identical (games, points): skip the jug05 row.
        Collision with different stats: append the jug05 row as today and record a conflict.
        No collision: append as today. Never merge two rows of the same source.
        The returned dict (:536) gains a `conflicts` list.
    src/parse_players.py  main()
        Write the conflicts with _write_csv(INTERIM_DIR / "jug05_career_conflicts.csv", ...) next to the
        jug05_review.csv write (:1349). INTERIM_DIR is :65. data/interim is git-tracked (40 files, including
        jug05_review.csv and jug05_xwalk.csv).
    data/interim/jug05_career_conflicts.csv  (proposed columns)
        bsnpr_id, season, city_token, team_raw_a, source_id_a, games_a, points_a, source_url_a,
        team_raw_b, source_id_b, games_b, points_b, source_url_b
    tests/test_parse_players.py  (proposed cases; no test references merge_jug05 today)
        identical stats with different spellings -> one row; differing stats -> two rows and a logged conflict;
        two franchises in one season -> both kept; same source, same season -> both kept;
        Aguadilla-style unresolved city with identical stats -> merged.
        Data-level guards: the 276 trade pairs remain; no cross-source identical-stats pair remains.
    Regeneration: `make parse-players` (Makefile:53-54), then `make build-web-data`. data/raw/players holds 4,710
        files (enciclopedia, jug05, jugador, jugador05). The run rewrites data/clean identity outputs, which must be
        diffed to show only player_career_seasons.csv changed.
    Checks: src/verify_clean.py has no check that counts player_career_seasons rows, so nothing pins 6,467.
        tests/test_build_web_data.py:169 documents the quirk in a comment that would go stale; the test still holds.

[OPEN_QUESTIONS]

    Q1  RESOLVED by D6: the players row survives, and every merged pair is logged to
        data/interim/jug05_career_merged.csv.
    Q2  Which third source adjudicates the 125 conflicts, and why they cluster in 2000-2003 and 2005. UNVERIFIED.
    Q3  The 125 conflict seasons (79 players) stay visible as two rows on the site until adjudicated. Accept that?
    Q4  That regeneration leaves every identity output unchanged (player_id_map, players_canonical, aliases, review
        queues, bios). Expected, because they use season and club sets. UNVERIFIED until run.
    Q5  All predicted counts (5,802 rows, 6,150 built rows, 107 web files) come from the CSV and JSON at HEAD
        `dd8df7c`. UNVERIFIED until the fix is built.
    Q6  `docs/session.md:4991` still says "unknown blast radius", and the addendum at `:5022-5035` covers the
        separate exact-name tier. Update session.md in a later docs phase.
