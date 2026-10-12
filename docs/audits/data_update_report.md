# Data update report

Mode: apply. Result: PASS.

## Checks

| Stage | Check | Result | Detail |
|---|---|---|---|
| preflight | tree | PASS | clean tree under data/clean, data/raw and web/data |
| preflight | guards | PASS | parse-players, sync-web-data and parse-games are refused by guard() |
| repair | game-name overlay | PASS | 0 row(s) pending repair, 0 left without an id |
| display | override list | PASS | 1 override(s), each with a source row |
| build | build_web_data (temp dir) and diff vs web/data | PASS | 0 changed, 0 added, 0 removed file(s); 0 game_box_player row(s) would change |
| validate | verify_clean | PASS | 346768 checks, 0 failed |
| validate | mojibake scan | PASS | 0 lines with mojibake in data/clean and web/data |
| validate | Gonzalez unassigned | PASS | 84 Javier González rows left unassigned (expected 84) |
| validate | bsnpr_id digest | PASS | 39371 unrelated game_box_player rows match the recorded digest f542ac5d5390 |
| validate | name quality | PASS | 2 ALL-CAPS name(s) left on purpose, 90 truncated or surname-only observation(s) without a linked id, 1 override(s) |
| validate | Cruz / Morales flags | PASS | 4 open flag(s) reported (informational) |
| apply | build_web_data | PASS | web/data rebuilt |
| apply | update_asset_hashes | PASS | web/index.html asset hashes already current |
| tests | pytest | PASS | 996 passed, 1 skipped, 1 xfailed in 440.66s (0:07:20) (baseline 959 passed, 1 skipped, 1 xfailed) |

## Row counts per dataset

| Dataset | Rows |
|---|---|
| bsn_career_leaders.csv | 30 |
| bsn_champions_by_season.csv | 97 |
| bsn_franchises.csv | 28 |
| bsn_records.csv | 11 |
| bsn_scoring_champions.csv | 26 |
| champions_from_bsnpr.csv | 92 |
| champions_reconciled.csv | 98 |
| city_franchise_map.csv | 29 |
| city_franchise_season_overrides.csv | 2 |
| club_code_map.csv | 29 |
| franchise_events.csv | 9 |
| franchises.csv | 34 |
| game_box_player.csv | 39669 |
| game_results.csv | 1287 |
| historic_awards.csv | 135 |
| historic_scoring_champions.csv | 58 |
| leader_coverage_gaps.csv | 16 |
| player_aliases.csv | 24180 |
| player_bios.csv | 152 |
| player_career_seasons.csv | 5678 |
| player_id_map.csv | 876 |
| player_id_tombstones.csv | 7 |
| player_identity_decisions.csv | 6 |
| player_roster_latinbasket.csv | 744 |
| player_season_leaders.csv | 1250 |
| player_season_leaders_2000_2002.csv | 403 |
| player_season_stats_2001_2004.csv | 503 |
| players_canonical.csv | 3326 |
| reconcile_conflicts.csv | 2 |
| scoring_champions_reconciled.csv | 68 |
| seasons_stats_tracked.csv | 14 |
| standings.csv | 57 |
| standings_coverage_gaps.csv | 5 |
| team_season_totals_2001_2004.csv | 38 |
| game_plays.csv.gz | 233664 |
| web/data (built) | career_leaders 3, data_quality 94, franchises 33, game_files 1292, mvp 47, player_files 3326, player_redirects 7, player_xwalk 163, players 3326, records 11, scoring_titles 68, season_files 98, seasons 98, seasons_with_awards 47, seasons_with_leaders 15, seasons_with_scoring_champ 57, seasons_with_standings 14, starting_five_files 17 |

## Name quality

- ALL-CAPS names remaining: 2 (ELIAS AYUSO, NO FUE SELECCIONADO)
- Unresolved truncated or surname-only observations: 90
- Override list size: 1

## Integrity

- Mojibake lines in data/clean and web/data: 0 (expected 0)
- Javier González rows unassigned: 84 (expected 84)
- bsnpr_id digest over 39371 unrelated box rows: f542ac5d5390... (recorded f542ac5d5390...)

## Open flags (Cruz / Morales and others)

- Mario Morales clubs ["san","gua"]: OPEN, 1980 scoring row cangrejeros_santurce vs 1980 MVP row mets_guaynabo
- Teófilo Cruz clubs ["san"]: quiz HOLD present (owner call)
- Larry / Elias Ayuso: untouched (owner: leave)
- 1979 rookie row 'NO FUE SELECCIONADO': shown as printed (wording S7 pending, docs/strings_pending_phase72.md)

## Diff summary

- web/data files changed: 0, added: 0, removed: 0
- by directory: {}
- data/clean/game_box_player.csv rows that the overlay changes: 0

## Suite

- 996 passed, 1 skipped, 1 xfailed in 440.66s (0:07:20) (baseline 959 passed, 1 skipped, 1 xfailed)
