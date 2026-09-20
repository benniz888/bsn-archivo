# MANATI_AUDIT — blast radius of `_team_resolver()`'s Manatí handling

Audit date 2026-09-19. READ-ONLY: no code, data, or commits changed. Every line
number and count below was re-checked against the file during this audit
(commands run against the working tree at `b0accd2`, tree clean). Anything not
checked directly is tagged UNVERIFIED.

[PURPOSE]

Size the damage from `_team_resolver()` mapping the city `MANATI` to
`osos_manati` regardless of season (first logged in `docs/session.md:4932-4944`
as "unknown blast radius, own scoping pass needed"). Deliver: where the
function lives, what Manatí handling it contains, who calls it, which outputs
it feeds, which rows are wrong, and a proposed (unapplied) fix per item.

Severity: HIGH = wrong data live on the site. MED = latent risk. LOW = cosmetic.
"Live" here means committed in `web/data/` (served from `main:/web` per
`Makefile` site target); the deployed site itself was not fetched (UNVERIFIED).

[DECISION]

## 1. Location

`_team_resolver()` is defined once: `src/build_web_data.py:410-420` (def at 410,
docstring 411-413, `return resolve` at 420). Only definition in the repo
(`grep -rn _team_resolver` over the whole tree, excluding `.git`/`.venv`).

## 2. Manatí handling inside it

None. The function contains zero Manatí literals. It is a pure lookup over
`city_franchise_map.csv`:

    src/build_web_data.py:416   city[_norm(r["normalized_city"])] = r["franchise_id"]
    src/build_web_data.py:419   return city.get(_norm(team_raw))

The only effective Manatí mapping is one CSV row, inherited transitively:

    data/clean/city_franchise_map.csv:15
    MANATI,osos_manati,*: Manati: Atenienses 2014-17 then Osos 2022+ — verify per season

The row's own note already says it is era-blind. The function's docstring
(`:412-413`) scopes it to "the 2001-2013 game seasons", which is stale: it now
also resolves 2015-16 career rows (see F1).

Related Manatí special cases elsewhere (context, not part of the function):

    src/reconcile.py:153        "MANATI": ("osos_manati", {"*": "Manati: Atenienses 2014-17 then Osos 2022+ — verify per season"})   (generator of the CSV row above)
    src/parse_latinbasket.py:88 ("2015", "MANATI"): ("atenienses_manati", "single-source", ...)   (CITY_OVERRIDES, standings parse only)
    src/parse_latinbasket.py:91 ("2016", "MANATI"): ("atenienses_manati", "single-source", ...)
    src/fetch_latinbasket_roster.py:88   "atenienses-de-manati": "atenienses_manati"
    src/reconcile.py:64,67,82,93         osos_manati / atenienses_manati / brujos_guayama seeds + relocated_renamed event
    app/franchise_key_map.csv:13,24,30   man=osos_manati, guy=brujos_guayama, ate=atenienses_manati

## 3 and 4. Callers and the output each feeds

Format: file | line | function | output fed

    src/build_web_data.py | 285 | _scoring_club_resolver (called by build_scoring_titles :315) | web/data/index/scoring_titles.json (scoring champions)
    src/build_web_data.py | 491 | build_mvp | web/data/index/mvp.json (HTML app data, MVP table)
    src/build_web_data.py | 608 | build_career_rows_by_pid (feeds build_players_index and build_players_detail) | web/data/players/<id>.json career[] (HTML app data)
    src/build_web_data.py | 820 | build_seasons_detail (via _standings_from_games :758) | web/data/seasons/<season>.json standings.rows, games-derived seasons only
    src/build_web_data.py | 911 | build_starting_fives | web/data/starting_five/<app_key>.json
    src/build_web_data.py | 997 | build_games | web/data/games/<season>/<gid>.json teams.a/b.franchise_id
    tests/test_build_web_data.py | 418 | TestHelpers.test_team_resolver | none (asserts SANTURCE and "Nowhere" only)

Outputs NOT fed by the resolver (checked): champions (`champion_franchise_id`
comes from `champions_reconciled.csv`, built by `reconcile.py`), franchises
(`franchises.json` from `franchises.csv`), records (`build_records`,
`build_web_data.py:393-404`), career leaders (`build_career_leaders`,
`:369-390`). None of the six call sites is in those functions.

Non-caller readers of the same map (same era-blind row):
`src/parse_players.py:923` (`_load_club_resolver`),
`src/parse_latinbasket.py:45,97-99` (`_load_city_map`),
`src/reconcile.py:256` (writer).

Measured Manatí footprint per source file (rows whose team string contains
"manat", normalized): game_results 0, game_box_player 0,
player_season_stats_2001_2004 0, player_season_leaders 0,
historic_scoring_champions 0, bsn_scoring_champions 0, historic_awards 0,
player_career_seasons **19**. So of the six call sites only `:608` has any live
hits. The rest are latent.

## 5-7. Findings

Format: ID | SEV | row identifier | current | expected | evidence | proposed fix

    F1 | HIGH | player_career_seasons.csv rows with team_raw "Atenienses, Manati": 2015 x8, 2016 x11 (19 rows, 14 bsnpr_ids: 37 87 772 1094 1739 1995 2033 2290 2459 2682 2700 2782 13010 13011) | franchise_id osos_manati in web/data/players/<id>.json career[] (19 rows); app shows "Osos de Manati" and links showTeam('man') | franchise_id atenienses_manati | build_web_data.py:617 calls resolve_team(team_raw.split(",")[-1]) which drops the nickname and leaves "Manati"; city_franchise_map.csv:15 maps it to osos_manati; franchises.csv:11 has osos_manati founded 2023 so a 2015/2016 row cannot belong to it; app/bsn_archivo.html:4559-4560 and :4641-4644 render F[ak].name in place of team_raw; built-file count matches CSV count (8+11=19, 14 files) | Make the resolver season-aware (see F3), pass season at :617 and :632, rebuild web/data
    F2 | HIGH | 6 player-seasons: (1094,2015) (13011,2015) (1995,2015) (1739,2016) (1995,2016) (772,2016) | career[] has two rows for one season: stats row labeled osos_manati plus a roster-only row labeled atenienses_manati with games=null points=null | one row: atenienses_manati carrying games, points and roster | build_web_data.py:643-644 attaches the latinbasket roster only on (season, franchise_id) match; the F1 mislabel defeats the match so :650-653 synthesizes a second row; seen directly in web/data/players/1995.json, 1739.json, 772.json, 1094.json, 13011.json | No separate fix, resolves with F1; add test that no (bsnpr_id, season) carries both Manati ids
    F3 | MED | resolver contract, src/build_web_data.py:418 resolve(team_raw) has no season parameter | MANATI resolves to osos_manati in every season; 0 of the 19 resolutions to it are correct and no row exists that legitimately resolves to it | era-scoped: Manati 2015-2016 to atenienses_manati, 2023+ to osos_manati | all six call sites (285 491 608 820 911 997) have a season in scope but cannot pass it; any future bare "MANATI" row from 2015-16 game, leader or scoring data mislabels silently; today those sources hold 0 Manatí rows so latent | resolve(team_raw, season=None) with season-scoped overrides loaded from data, unchanged behavior when season is omitted, docstring corrected
    F4 | MED | generator drift: src/reconcile.py (make reconcile, Makefile:56-57) rewrites city_franchise_map.csv, franchises.csv, franchise_events.csv | on-disk files differ from reconcile.py constants: city map HUMACAO (reconcile.py:152 grises_humacao vs CSV caciques_humacao); franchises.csv has a caciques_humacao row the generator lacks and a different grises_humacao row; franchise_events.csv has toritos_cayey to caciques_humacao 2005 and grises_humacao to criollos_caguas 2024 that the generator lacks, and the generator dates that rename 2023 | generator and disk agree | in-memory diff run this audit (no writes); commit 77a3aae edited the CSVs directly; reconcile is not a dependency of build-web-data (Makefile:80-81) so it only bites on a manual re-run (whether anyone re-runs it is UNVERIFIED) | Before any Manatí fix, sync reconcile.py to the on-disk truth or retire it as generator, so the fix cannot be reverted and Humacao is not regressed
    F5 | MED | franchises.csv:14 atenienses_manati founded 2014, status "defunct 2017" (also reconcile.py:67, bsn_franchises.csv:14; web/data/index/franchises.json founded 2014 end 2017) | 2014 to 2017 shown on site | UNVERIFIED; archive evidence supports only 2015 and 2016 | standings.csv has Manati rows for 2015 and 2016 only; no Manati row in 2014 or 2017 standings and none in player_career_seasons for 2014 or 2017; session.md:4265-4266 cites franchises.csv itself (circular); fetch_latinbasket_roster.py:17 gives 2015-2018 but those are captures under one latinbasket id, not seasons played; franchises.csv:14 source label "derived:champion/scoring rows" though no champion or scoring row names Atenienses | Get an independent source (es.wikipedia article or Federacion) before editing; if 2015-2016 holds, store first and last season played separately from founded/dissolved; correct the source label
    F6 | LOW | bsn_franchises.csv:11 Osos de Manati founded 2014, active | founded 2014 | founded 2023 (franchises.csv:11) | franchise_events.csv:2 note says the seed conflated Osos with Atenienses; bsn_franchises.csv is read only for its city column (parse_wayback.py:212-215) so the wrong value reaches no output; franchises.json shows 2023 correctly; a franchise_founded conflict topic exists at reconcile.py:491 (UNVERIFIED that it covers Osos) | Leave the seed untouched, confirm the conflict record, no code change
    F7 | LOW | Brujos to Osos year labels | bsn_franchises.csv:29 and docs/project.md D2 say 2022; franchises.csv:30, franchise_events.csv:2, reconcile.py:82 and :93, app/franchise_key_map.csv:13 and :24 say 2023; franchises.json has brujos_guayama end 2023 and osos_manati founded 2023, both claiming 2023 | event season 2023 kept; brujos end 2022 (last season as Brujos); Oct 2022 sale noted | franchise_events.csv:2 note says sold 17 Oct 2022, played as Osos from 2023 (es.wikipedia per the note, not re-fetched here, UNVERIFIED); where end is derived was not traced | Set brujos end to last season played; reword project.md D2 to "sold 2022, Osos from 2023" (Tier-2 owner touch, already queued in session.md)
    F8 | LOW | bsn_champions_by_season.csv:96 and champions_reconciled.csv:97, 2024 runner_up Osos de Manati | consistent with franchises (osos_manati exists from 2023); source column cites the base en.wikipedia article while the note says confirmed from the 2024 season page; docs/project.md D6 still says the 2024 runner-up is blank | source = the 2024 season page; D6 updated | Cross-check otherwise clean: this is the only Manatí champion or runner-up row; Brujos runner-up 1991 (csv:63) and 1994 (csv:66) match franchises.json finals_lost; titles 0 for Osos, Atenienses, Brujos matches the champions CSV (no champion row names them); the 2024 fact itself is UNVERIFIED externally | Owner confirms, patch source URL with provenance, edit D6
    F9 | LOW | parse_players.py:923-969 _load_club_resolver (identity club corroboration) | "Atenienses, Manati" returns atenienses_manati (correct, run this audit); bare "Manati" and "Osos, Manati" return osos_manati | bare-city era-aware | correct for the nickname form only because the synthetic nick_city key (:967-968) happens to equal the franchise_id; bare-city strings stay era-blind | When F3 lands, share one override loader instead of a second copy; add regression test on "Atenienses, Manati"
    F10 | LOW | app/player_crosswalk.csv lines 10 (Alex Abreu 12998), 124 (Chris Ortiz 13057), 143 (Jonathan Garcia 1094), 144 (Jonathan Rodriguez 2516) | evidence text cites club osos_manati | UNVERIFIED | origin of the osos_manati club in these strings not traced; parse_players today returns atenienses_manati for "Atenienses, Manati", so it does not explain 1094; strings are static evidence text and feed no output | Trace after F1 by regenerating parse_players; only then decide if any are legitimate 2023+ Osos observations
    F11 | LOW | tests/test_build_web_data.py:417-420 test_team_resolver | asserts SANTURCE and "Nowhere" only | asserts Manati 2015 and 2016 to atenienses_manati and 2023+ to osos_manati | no test locks either era | Add with the F3 fix

## Finding status (added 2026-09-20; findings above unchanged)

Status as of HEAD `9a458b8`. Both fixing commits are LOCAL and UNPUSHED
(`origin/main` = `b0accd2`). The finding text above is the audit as run on
2026-09-19; line numbers in it refer to the tree at `b0accd2` and have since
shifted. Format: ID | status | commit | note

    F1  | RESOLVED | 9a458b8 | 19 career rows now atenienses_manati; 14 web/data/players files rebuilt; 0 osos_manati career rows remain
    F2  | RESOLVED | 9a458b8 | 6 duplicate player-seasons are single rows with games, points and roster; career rows 6,821 -> 6,815
    F3  | RESOLVED | 9a458b8 | resolve(team_raw, season=None) reads data/clean/city_franchise_season_overrides.csv via src/city_season_overrides.py; docstring corrected
    F4  | RESOLVED | 4dd4198 | reconcile.py synced to the on-disk CSVs; 7-file drift guard in tests/test_reconcile.py; only difference is quote-only at franchises.csv:21 (parsed rows equal, accepted by owner)
    F5  | OPEN     | -       | "2014-2017" still shown on team page ate; archive supports only 2015-2016; UNVERIFIED; overrides deliberately exclude 2014 and 2017; needs an independent source
    F6  | OPEN     | -       | seed left untouched; verified 2026-09-20 that the only franchise_founded conflict is Criollos de Caguas (reconcile.py:528) and reconcile_conflicts.csv has no Osos or Atenienses row, so the seed's "Osos founded 2014" is not flagged anywhere
    F7  | OPEN     | -       | 2022 vs 2023 labels unchanged; needs a Tier-2 owner edit to docs/project.md D2; where brujos end is derived not yet traced
    F8  | OPEN     | -       | needs owner confirmation of the 2024 runner-up source; docs/project.md D6 still says blank
    F9  | RESOLVED | 9a458b8 | parse_players._load_club_resolver reads the same overrides; 0 differences across 1,354 real (club string, season) pairs; regression tests in tests/test_city_season_overrides.py
    F10 | OPEN     | -       | origin of osos_manati in app/player_crosswalk.csv evidence lines 10, 124, 143, 144 not traced
    F11 | RESOLVED | 9a458b8 | era-aware and unchanged-default assertions in TestHelpers plus TestManatiCareerRows

New findings from the fix work, not part of F1-F11 (details in docs/session.md):
team pages with no starting-five file log a 404 (ate, man, hum, vil; pre-existing);
the reconcile.py "seed:" source-label branch can never fire; player 1995 shows
Criollos de Caguas twice for 2002-2004 (the known merge_jug05 bug); and
parse_latinbasket.CITY_OVERRIDES still duplicates the Manatí override in code.

## Reconciled discrepancies (per the "resolve before reporting" rule)

- `docs/session.md:4911` says `web/data/seasons/2015-2016.json`. Actual files
  are `2015.json` and `2016.json` (verified with `ls`; `session.md:4972` agrees).
  Both already carry `atenienses_manati` for Manatí (D2 fix is live).
- `docs/session.md:4934-4936` says the bug touches `player_career_seasons.csv`
  and `player_season_stats_2001_2004.csv`. Measured: 0 Manatí rows in the
  latter (2001-2004 seasons only). Real footprint is `player_career_seasons.csv`
  alone.
- Atenienses span: 2014-2017 (franchises.csv), 2015-2018 (latinbasket id
  captures), 2015-2016 (observed rows). See F5.
- Relocation year: 2022 vs 2023. See F7.
- Task asked to quote Manatí literals inside the function. There are none;
  see section 2.

## Appendix: the 19 F1 rows

Format: bsnpr_id | season | games | points (all `team_raw` "Atenienses, Manati",
source `wayback_bsnpr_players`)

    1094|2015|43|408    1995|2015|42|415    2033|2015|44|700    2682|2015|37|119
    2700|2015|27|179    2782|2015|27|21     13010|2015|24|392   13011|2015|26|102
    37|2016|11|139      87|2016|1|0         772|2016|18|19      1094|2016|8|81
    1739|2016|34|225    1995|2016|34|311    2033|2016|24|319    2290|2016|11|63
    2459|2016|1|0       2682|2016|36|255    13011|2016|12|132

[RATIONALE]

The defect is not in the function body. It is a data-shape gap: the map is
keyed by city only, the resolver has no season input, and the career path
(`:617`) also discards the nickname before lookup. The two Manatí franchises
share a city and never overlap in time (Atenienses 2015-2016 in the archive,
Osos 2023+), so a season key resolves them with no ambiguity. Season is already
in scope at every call site. F2 is the same bug compounding with the item-7
roster wiring: the roster join keys on franchise_id, so a wrong id splits one
player-season into two rows. That is why the fix belongs in the resolver and
not in the roster code.

The site is currently wrong for exactly 14 player files. Season, games,
starting-five, scoring-title and MVP outputs are unaffected today.

Predicted effect of the F1 fix (not run): 14 `web/data/players/*.json` files
change; the 6 F2 pairs collapse to one row each; `osos_manati` no longer appears
in any player file; `manifest.json` source digest changes; nothing else moves.
Confirm with `git diff --stat web/data` after a rebuild.

[ALTERNATIVES_REJECTED]

- Repoint `city_franchise_map.csv` MANATI to `atenienses_manati`: fixes 2015-16
  but breaks any 2023+ Osos row the moment one is ingested.
- Pass the full string (`"Atenienses, Manati"`) instead of `split(",")[-1]` and
  resolve by nickname only: fixes the 19 rows without a season argument, but
  any bare `MANATI` row stays ambiguous. Acceptable as a cross-check inside the
  season-aware fix, not as the fix.
- Rewrite `team_raw` in `player_career_seasons.csv`: the source string is
  already correct; only the resolver is wrong.
- Hand-edit `web/data/players/*.json`: generated output, reverted on rebuild.
- Extend `parse_latinbasket.CITY_OVERRIDES`: only reaches the standings/roster
  parse, not `build_web_data`'s career path (that is why D2 fixed 2 rows and
  left the 19).

[INTERFACES]

Proposed, not applied. Owner decision needed on placement (see Q2).

- `_team_resolver()` returns `resolve(team_raw: str, season: int | str | None = None)`.
  With `season=None` behavior is byte-identical to today.
- Season-scoped overrides in one data file, for example
  `data/clean/city_franchise_season_overrides.csv` with columns
  `normalized_city, season_from, season_to, franchise_id, note`. Rows:
  `MANATI, 2015, 2016, atenienses_manati`; `MANATI, 2023, , osos_manati`.
  Migrate `parse_latinbasket.CITY_OVERRIDES` (`:73-94`) into it so there is one
  source. `parse_players._load_club_resolver` reads the same file.
- Call-site edits: `build_web_data.py` `:617`, `:632` (career, pass `r["season"]`
  and `season`), `:506` (`yr`), `:777` (season `s`), `:959` (`season`),
  `:1017`, `:1019` (`season`), and `_scoring_club_resolver` `:299-304`.
- Tests: extend `test_team_resolver` (F11); add a career-build test that no
  `(bsnpr_id, season)` carries both Manatí ids (F2).
- Verification after the fix: `make test`, `make verify`, rebuild, then
  `git diff --stat web/data` shows only the 14 player files.

[OPEN_QUESTIONS]

- Q1. Atenienses de Manatí's true first and last seasons (F5). Needs an
  independent source; nothing in the archive supports 2014 or 2017.
- Q2. Owner decision (P2 architecture): season overrides in a new CSV
  (recommended) or a code constant? And F4: sync `reconcile.py` to the on-disk
  files first, or retire it as the generator?
- Q3. Origin of `osos_manati` in the four `player_crosswalk.csv` evidence
  strings (F10). Untraced.
- Q4. Is the deployed site identical to committed `web/data/`? Not fetched.
- Q5. Should Brujos to Osos be shown as one continuous franchise on the `man`
  page? Currently separate ids linked by an event (D2 design). Not a defect
  here; noted because `man` shows only 2023+ history.
