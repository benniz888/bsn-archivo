# PHASE_72_AUDIT — Data fixes (read-only)

Branch `data-fixes-v1`, created from `main` at 374e58b (merge of PR #3), clean tree. Date 2026-10-12. Nothing under `web/`, `src/`, `data/` or `tests/` was edited. Files written: this audit, `docs/strings_pending_phase72.md`, and a `docs/session.md` entry. Everything else was run from the scratchpad (scripts, dumps, two dry-run parses that wrote only there).

## 0. Baseline and method

**Suite baseline (full `pytest -q`, no `-x`, on `main` before any work): 856 passed, 1 failed, 1 xfailed, 402.95 s.**
The one failure is pre-existing and unrelated: `tests/test_web_text.py::TestWebTextReconstructsTheOriginal::test_web_text_equals_the_frozen_pre_split_original_byte_for_byte` (first byte difference at index 131: `v` vs `m`). It fails on clean `main`. Fix it or retire it in 72A; every later phase compares against "856 passed / 1 failed" and not against zero.

Method. Source rows were traced in `data/clean/*.csv` and `data/raw/**`; the app's in-memory tables were dumped by loading `web/` in Chromium (Playwright from `/private/tmp/bsn_harness`) and reading `POOL`, `HOF`, `NBA_PLAYERS`, `SEASON_AWARDS`, `MVP_YEARS`, `LEADERS`, `RECORDS` and `clueList.init().G`; the pre-overlay source literals were read with `node:vm` from `web/js/data.js` and `web/js/tabs.js`. Confidence labels: **high** = reproduced from a primary row or a byte-level check; **medium** = consistent evidence, no independent source; **low** = plausible, unverified.

Important structural fact for items 5, 6 and 7: `web/index.html:636-868` holds a Spanish overlay IIFE ("CAPA DE IDIOMA", `translate()`) that overwrites the English literals in `web/js/data.js` and `web/js/tabs.js` at load time (`HOF_ES`, `REC_ES`, `NBA_ES`, `STONE_ES`, `BIO_ES`, and others). The source files still hold English; what a visitor sees is the overlay.

---

## 1. Rebounds conflict: Rubén Rodríguez 6,178 vs Mario Butler 8,236

**Both numbers come from the same seed file, so they are not two sources disagreeing.**

| Number | Where | Row |
|---|---|---|
| 6,178 (Récords) | `data/clean/bsn_records.csv:3` ("Most rebounds, career", Ruben Rodriguez, 6178, note "631 games") -> `web/data/index/records.json` -> `RECORDS` (`web/js/tabs.js:164`, shown via `REC_ES`, `web/index.html:697`) | one of 11 rows |
| 6,178 and 8,236 (Líderes) | `data/clean/bsn_career_leaders.csv:12-13` (rebounds rank 1 Mario Butler 8236 / 779 gp / 10.6; rank 2 Ruben Rodriguez 6178 / 631 gp / 9.8) -> `LEADERS` (`web/js/tabs.js:105-106`) | two of 30 rows |

Both CSVs were added in the scaffold commit `195fc2a` (2026-09-07, "inherited research corpus", from Wikipedia per `docs/research/README.md`). Neither file has provenance columns (no `source_id`, `source_url`, `retrieved_at`, `confidence`), which already breaks PC3 for these 41 rows. `docs/specs/reconcile_spec.md:238` records that neither was ever reconciled against anything.

Cross-check against the identity spine (`data/clean/player_career_seasons.csv`, from the league's own `jugador.asp` pages):

- Rubén Rodríguez = `bsnpr_id` **2113** ("Rodriguez Leon, Ruben", b. 1953, 1969-1991, Vaqueros de Bayamón only). Games summed over his 23 season rows: **631**, identical to the Líderes/Récords games figure. Points summed: 11,549.
- Mario Butler = `bsnpr_id` **1575** ("Butler Graham, Mario Alberto", b. 1957, 1980-2008, 30 rows). Games summed: **789**. Líderes says 779. The difference of 10 is exactly the 2001 duplicate stint (row "Cangrejeros, Santurce" 11 games plus row "SANTURCE" 10 games, same season, 2001), so 779 is the de-duplicated figure.
- Butler led the 1986 league in rebounds at 15.2 per game (457 in 30 games, `data/clean/player_season_leaders.csv:42`) and has 7 Defensive Player rows (`historic_awards.csv:22-32`). A 10.6 career average over 779 games is consistent with that profile; 6,178 would imply 7.9 per game over the same games.
- The spine stores games and points per season only. There are **no per-season rebound totals** in the repo, so neither career total can be recomputed.

**Verdict.** The two lists cannot both be right. The evidence favors Butler as the all-time leader: his games reconcile to the spine, his average is internally consistent, and D7 says these tables are floors, which means a stale list can understate Butler but cannot make Rodríguez the leader. The Récords row is the same 6,178 that sits in rank 2 of Líderes, which points to the record having been keyed from the wrong row (or from a list that predates Butler's career). Whether 8,236 itself is exact cannot be determined without an outside source.

- **Confidence:** medium-high (about 80%) that Butler is the leader; low-medium that 8,236 is exact.
- **Proposed fix (72F):** (a) do not edit either total yet; (b) add an explicit `confidence=disputed` flag to the Récords row and show the existing `.warn` note on both views until sourced; (c) fetch an independent career-rebound figure (RealGM career page, es.wikipedia "Anexo:Líderes", or the league's own `lidereshistoricos.asp` if archived) and then either change the Récords row to Butler or remove it; (d) add provenance columns to both CSVs.
- **Related:** the Dalmau assists row (2,302 / 537 = 4.3, listed 5.1) is the same class of inherited defect (`docs/research/audit_bsn_archivo_2026_09_01.md:84`); `docs/audits/data_review_todo.md` has a possible resolution (a different Dalmau, 455 games) that is unverified.
- **Risk:** low if only flagging; medium if the Récords row changes (it feeds Ask answers, ¿Quién soy? record clues, Sube y Baja).
- **Needs owner:** **yes**, for which source counts as independent and whether to publish a "disputed" note.

---

## 2. A02 — name quality

Scope: every person-name string the site renders from `web/data/seasons/*.json` (awards, leaders, scoring champion), `web/data/index/mvp.json` and `web/data/index/scoring_titles.json`. 562 distinct strings, 1,800 occurrences. Script: scratchpad `a02*.py` (counts below are reproducible from the published JSON).

**Cause of each class (the raw bytes decide where the fix can live):**

| Cause | Distinct | Occurrences | Where it enters | Evidence |
|---|---|---|---|---|
| C1. ALL-CAPS "FIRST LAST" | 111 | 287 | Pre-2005 historic tables (`historic_awards.csv`, `historic_scoring_champions.csv`), parsed verbatim from `lidereshistoricos.asp?t=3` | `data/clean/historic_awards.csv:69-71` |
| C2. Truncated at a fixed-width source cell | 44 | 156 | The league's own leader pages cut the player cell at about 15-21 characters before the club in parentheses | raw: `Morales, Mario 'Qui        (Mets)`, `Butler, Mario Albe         (Titanes)`, `Ayuso, Elias 'Lar          (Capi` (`data/raw/lideres/*`). Two kinds: unclosed nickname quote (22 names, for example `Morales, Mario 'Qui`, `Lee, Alfred 'Bu`) and plain given-name cut (22 names, for example `Butler, Mario Albe`, `Rivera, Carlos Rub`, `Han, Francis Jo`). 18 of the cut names have a given-name prefix match in `players_canonical.csv` (for example `Butler Graham, Mario Alberto`). |
| C3. Surname only | 42 | 83 | 2000-2002 leader boards (`player_season_leaders_2000_2002.csv`) print the surname alone | `Alicea`, `Carter`, `Dalmau` |
| C4. Typos in the source | 9 | 19 | The source itself | `GOERGIE TORRES` is in the raw capture (`data/raw/pre2007/mvp/20040405022402_JDUEAITC.html`) and `historic_awards.csv:71`; also `Casian0` (zero for o, 2000), `JOHNY BAEZ` (4), `ALEJANDO 'BIMBO' CARMONA`, `FITZROY BROW` (canonical: `Brow Wilkinson, Fitzroy`, so this may be correct), `Priutt, Shawn` (canonical `Pruitt, Shaun`), `Houroutunier, Rolando`, `Honeycut`. Each needs an id before it is rewritten. |
| C5. Nickname or short form (overlaps C1) | 6 | 33 | `TEO CRUZ` (17), `PACHIN VICENS`, `JOHNY`, `MARIO ‘QUIJOTE’MORALES` (missing space, 2) | the app already tolerates these in `build_web_data.py:_mvp_name_match` |
| C6. Not a person | 2 | 2 | `NO FUE SELECCIONADO` (1979 rookie row, means no award was given), `TEO CRUZ Y BILL McCADNEY` (1966 defensive row, two people in one cell) | `web/data/seasons/1979.json`, `1966.json` |
| C7. Unaccented | not measured | n/a | The league's own data strips accents (`Rodriguez, Ruben`); 344 strings are already clean and resolve to an alias case- and accent-insensitively | not a defect to "fix" without an id; some canonical names are also unaccented |
| C8. Format mix | 405 "Last, First", 112 CAPS, 45 "First Last" | | three source formats on one page | |

C4-C6 overlap C1-C3 (a typo can also be ALL-CAPS); the first three rows are exclusive counts from one classifier, the rest are additional flags on the same strings. 17 strings resolve to nothing in the alias table (including the C4 typos). Only 15 of the 111 ALL-CAPS strings resolve to exactly one alias; the rest need the `bsnpr_id` already attached in `mvp.json` / `scoring_titles.json` (91 of 101 ALL-CAPS records there carry one).

**Proposed normalization rule (applied in `src/build_web_data.py`, never in `data/clean/` and never in raw, per PC5):**
1. If the record has a `bsnpr_id` (or `player_id_map.csv` links `player_raw` + season to one), display `display_name(bsnpr_id)` = given name + paternal surname from `players_canonical.csv` (`nombre`, first token of `apellidos`), accents kept as stored. Maternal surname dropped.
2. Else if the string is a known truncation (C2) and its unclosed nickname tail is removed, resolve the remaining `Surname, Given` by alias + season-in-career (the rule `player_id_map.csv` already uses); accept only a unique hit.
3. Else if ALL-CAPS: title-case with a particle list (`de`, `del`, `la`, `Mc`) and a nickname-quote pass; keep accents absent rather than inventing them.
4. Else leave the raw string unchanged. Log it in the validation report.
5. Never merge on name alone (D1); every rewrite needs id or an override row.

**Manual overrides (new file `data/overrides/name_overrides.csv`, columns `raw,season_scope,display,bsnpr_id,reason,confidence`):**

| Raw | Proposed | Basis | Confidence |
|---|---|---|---|
| `GOERGIE TORRES` (MVP 1986, Fajardo) | `Georgie Torres` | typo; adjacent rows 1984 and 1985 read `GEORGIE TORRES`; same club | high |
| `NO FUE SELECCIONADO` (rookie 1979) | row suppressed or shown as "sin selección" | not a person | high (needs owner for wording) |
| `TEO CRUZ Y BILL McCADNEY` (defensive 1966) | two rows, ids 2200 and the McCadney id | two people in one cell; `BILL McCADNEY` also appears alone 5 times with no id | medium |
| `Casian0` (2000) | `Casiano` plus id | zero for letter o; id needed from season-in-career | medium |
| `ALEJANDO 'BIMBO' CARMONA` (rookie 2002) | `Alejandro «Bimbo» Carmona` | missing r; not in `players_canonical.csv`, so no id | low until an id exists |
| `Ayuso, Elias 'Lar` (14 occurrences) and `Ayuso, Larry` vs `ELIAS AYUSO` (scoring 2002) | decide on one person | `docs/audits/data_review_todo.md` already lists Larry/Elias as a conflict; id 574 | needs owner |
| `Butler, Mario Albe`, `Morales, Mario 'Qui`, `Ayuso, Elias 'Lar` | resolve to ids 1575, 1584, 574 | unique prefix + club + season | high |
| the other 15 truncations that have a canonical prefix match (for example `Avila, Victor Man`, `Cruz, Ismael Yom`, `Han, Francis Jo`, `Rivera, Carlos Rub`) | resolve to canonical id | prefix + club + season in career; accept only a unique hit | high-medium |
| surname-only strings (42) | leave raw; link only where the board has one club + season match | cannot be resolved by name alone | n/a |

- **Risk:** medium. It changes about 1,100 rendered strings across `web/data/seasons/**`, `mvp.json`, `scoring_titles.json`, and the tests that read names. A "before/after names" diff in the validation report makes it reviewable.
- **Needs owner:** yes for the display style (accents, nickname quotes, whether to drop the maternal surname) and the Ayuso identity; no for pure typo corrections once an id exists.

---

## 3. Mojibake root cause in `src/parse_games.py`

**Exact cause.** `src/parse_games.py:144` (gamestatwide), `:217` (boxscore and pogamestat) and `:354` (a2gamestatpbp) all do `p.read_bytes().decode("cp1252", "replace")` for every raw page. 10,474 files sit under `data/raw/games/`. Some pages carry UTF-8 text, and cp1252 reads each UTF-8 accent as two characters (`é` is bytes `C3 A9`, which cp1252 shows as `Ã©`). Byte-level reproduction over every raw page with non-ASCII bytes:

| Sub-directory | Pages with non-ASCII | Pure cp1252 | Valid UTF-8 | **Mixed** (UTF-8 names inside a cp1252 page) | Declared `charset=` |
|---|---|---|---|---|---|
| a2gamestatpbp | 3,091 | 3,091 | 0 | 0 | none |
| gamestatwide | 864 | 864 | 0 | 0 | none |
| boxscore | 261 | 261 | 0 | 0 | iso-8859-1 |
| pogamestat | 904 (plus 117 ASCII) | 247 | 392 | **265** | utf-8 on 650, iso-8859-1 on 247, none on 7 |

The 392 valid-UTF-8 pages are all `pogamestat`; the 265 mixed pages are also `pogamestat` and are the ones that declare `utf-8` yet fail a strict UTF-8 decode: the name cells are UTF-8 (`Jos\xc3\xa9`), the footer has a UTF-8 `©` (`C2 A9`) next to a single-byte cp1252 `™` (`0x99`), which is invalid UTF-8. So the page encoding cannot be taken from the declaration or from a whole-page test. Across the 4,216 pure-cp1252 pages, a scan for UTF-8 multibyte sequences finds **0** matches (no false-positive risk). No byte cp1252 leaves undefined appears in these pages (0 U+FFFD from `errors="replace"`), so the damage is reversible.

**Records already damaged** (the only ones in `data/clean/`, `data/interim/` and `web/data/`; `grep -P "Ã|Â|\x{FFFD}"` finds nothing else):

| `player_raw` in `data/clean/game_box_player.csv` | Rows | Games | Seasons | Should read | Resolves to (after the fix) |
|---|---|---|---|---|---|
| `Lloreda, JosÃ© Jaime` | 118 | 79 | 2011-2013 | `Lloreda, José Jaime` | id 2690 |
| `Cotto, RubÃ©n` | 120 | 75 | 2011-2013 | `Cotto, Rubén` | id 2675 |
| `GonzÃ¡lez, Javier` | 58 | 30 | 2012-2013 | `González, Javier` | id 2513 |

Total **296 rows**, 3 distinct names. Of them, 170 rows sit on fully-UTF-8 pages and **126 on mixed pages (115 pages)**. Other accented text in these pages (`Nelson Colón`, `Carlos Calcaño`, `Omar González`, `Flor Meléndez`, `Angel López Panelli`, page chrome) is not parsed into any table. `web/data/` is already clean because `src/build_web_data.py:_read` repairs the three names at build time (display-only).

**Proposed fix, and a correction to the earlier proposal.** The fix recorded in `docs/audits/data_review_todo.md` ("decode as UTF-8 first, fall back to cp1252") is **not enough**: a whole-page strict UTF-8 attempt repairs only the 170 rows on fully-UTF-8 pages and leaves the 126 on mixed pages (verified by dry run, below). The decode has to work per byte sequence. In `src/parse_games.py` replace the three decode calls with one helper:

```python
_UTF8_SEQ = re.compile(rb"[\xc2-\xdf][\x80-\xbf]|[\xe0-\xef][\x80-\xbf]{2}|[\xf0-\xf4][\x80-\xbf]{3}")

def _decode(raw: bytes) -> str:
    """Pages mix encodings (UTF-8 names inside a cp1252 page), so a whole-page test is wrong."""
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        pass
    out, pos = [], 0
    for m in _UTF8_SEQ.finditer(raw):
        out.append(raw[pos:m.start()].decode("cp1252", "replace"))
        out.append(m.group().decode("utf-8"))
        pos = m.end()
    out.append(raw[pos:].decode("cp1252", "replace"))
    return "".join(out)
```

Add a test that parses one fully-UTF-8 page and one mixed page and asserts `José` and `Rubén` survive; keep the `build_web_data.py` repair as a guard (it becomes a no-op).

**Dry runs (scratchpad only; the real `src.parse_games.main()` with `read_bytes` wrapped and `_write_csv` redirected; nothing written to the repo):**

| Run | `game_box_player.csv` rows differing from committed | Mojibake rows left |
|---|---|---|
| Control (parser unchanged) | 365 (`bsnpr_id` only) | 296 |
| Whole-page UTF-8 first | 535 (365 id drift + 170 names) | **126** |
| Per-sequence decoder (above) | **661** = 365 id drift + 296 names with their new ids | **0** |

`game_results.csv` and `game_plays.csv.gz` are byte-identical in all runs (1,287 and 233,664 rows).

**Second finding: `parse-games` is not idempotent at HEAD.** Even the unchanged control re-parse changes 365 `bsnpr_id` values in the committed file: 360 gain an id, 5 lose one, all in 2001-2003 (`Santiago, Eddin` -> 502 for 153 rows, `Cruz, Alvin` -> 74 for 63, `Casablanca, Fernando` -> 688 for 45, `Sanchez, Angel` -> 129 for 32, `Berdiel, Miguel` -> 1666 for 25, and `Mounneke, Gabriel` 770 -> blank for 5). The cause is the identity spine moving after the games were parsed (the 2026-09 dedup and hand edits; see N7). So regenerating is not "exactly 3 names, 296 rows, nothing else", as `data_review_todo.md` and the PHASE_66 note assume. Choose before 72C: (a) regenerate and review all 661 rows, or (b) write an overlay (`src/apply_game_name_repair.py`, modeled on `apply_career_dedup.py`) that rewrites only the 296 `player_raw` and their ids and leaves the other 365 drifted ids alone. Recommendation: (b), because it keeps the diff to what was asked and defers the 365 id changes to the identity triage.

- **Confidence:** high on cause, fix and counts (all reproduced).
- **Risk:** medium via (a), low via (b).
- **Needs owner:** yes, to choose (a) or (b) (either rewrites `data/clean/game_box_player.csv`).

---

## 4. The 303 players with no structured honors

Reproduced exactly: of the 376 players in `POOL`, **303** have none of the four structured honor sources `clueList` reads (a matched award year, a title from `ss` rows x `F.won`, an all-time rank row from `LEADERS`, or a `STONE` coliseum). 73 have at least one; 69 of the 376 are playable in ¿Quién soy?; 4 of the 73 with an honor are still not playable (Teófilo Cruz and Mario Butler are held, Sammy Betancourt has no averages, Ramón Rivas is short of other fields). No player without an honor is playable.

Grouped by what is missing and whether the repo has a trustworthy source:

| Group | Count | What is missing | Source in repo? | Can it be filled from the repo? |
|---|---|---|---|---|
| **A.** They played only in seasons for which there is **no award table at all** (2012, 2013, 2015, 2019, 2020, 2021, 2023) | 35 | any award, MVP, scoring, rookie, defensive, sixth-man row for those years | `SEASON_AWARDS` covers 2009, 2016-18, 2024-26; `MVP_YEARS` adds 2010, 2011, 2014, 2022; finals MVP 2024-26 | **No.** Needs the league's award lists for those seasons (outside data). |
| **B.** Played in a season that has award rows, won none | 86 | nothing is missing for their awards; they are true negatives for those honors. Missing fields that would give them a last clue: per-player titles, all-league teams, leaderboard finishes beyond rank 1 | `player_season_leaders.csv` (11 categories, ranks 1-10, 12 seasons) | **Partly.** 7 of the 86 are rank-1 in scoring, rebounds or assists in a covered season and could gain a structured honor: Larry Ayuso (scoring 2002, disputed identity), Lee Benson (rebounds 2008), Jeffrion Aubry (rebounds 2009), Thomas Robinson (rebounds 2021), David Stockton (assists 2021), Leon Williams (rebounds 2014), Peter John Ramos (rebounds 2013). The matching rule must stay first+last token plus a season inside the player's decades (D1). |
| **C.** **No per-season stat rows at all** (`ss` empty) | 182 | everything per-season; titles cannot be derived because they come from `ss` x `F.won` | 167 have `ppg`/`rpg` from the 2026 RealGM-derived `POOL_BSN26` and no earlier seasons; the other 15 are older (for example Butch Lee, Jerome Mincy, Ángel «Munch» Cruz, Daniel Santiago, J. J. Barea, Robert Traylor, Jonathan García) | **No.** 2022-2025 per-season lines and titles need outside data (RealGM or the league export). The older 15 have no season rows in `jugador.asp`. |

Overlaps are none (A + B + C = 303). By first decade: 256 start in the 2020s, 37 in the 2010s, 5 in the 2000s, 2 in the 1980s, 2 in the 1990s, 1 in the 1970s. 271 have no `t` (tag) at all; 6 have no club; 12 have no ppg.

**Cannot be filled without outside data:** all of groups A and C (217 players), and the 79 group-B players with no rank-1 row. Full name lists are in appendix 4.

- **Proposed fix:** (72D) add a repo-derived honor source for the 6 clean cases (Ayuso held back) as `data/clean/player_honors_derived.csv` with provenance; for A and C, request award and per-season data, then load it through the same table.
- **Risk:** medium; honors feed 4 games and the Perfil tier.
- **Needs owner:** yes: whether single-source leaderboard #1 rows count as "honors", and approval to fetch outside data (P5).

---

## 5. English one-liners

Counted at two layers, because the source literals are English and a runtime overlay translates them (`web/index.html:636-868`).

| Table | Source location | Source strings | English in source | Overlay | English at runtime |
|---|---|---|---|---|---|
| `HOF[].role` | `web/js/data.js:166-232` (18 entries) | 18 roles | **18 of 18** | `HOF_ES` (`index.html:640`), 18 of 18 keys match | **0** |
| `HOF[].hon` and `.note` | same | 57 strings | about 42 English (for example "3× scoring champion", "Inducted 7 October 2012…") | `HOF_ES` | 0 |
| `POOL[].b` | `web/js/data.js:269-369` (45 bios) + 48 added elsewhere | 93 at runtime | **44 of the 45** in `data.js` | `BIO_ES` (`index.html:820-867`), 45 keys | **1** |
| `NBA_PLAYERS` | `web/js/tabs.js:184-192` | 7 | **7 of 7** | `NBA_ES` (`index.html:720-727`) | 0 |
| `SEASON_AWARDS` | `web/js/tabs.js:7025+` | 44 rows | **0** | none needed | 0 |
| `RECENT` (dead data) | `web/js/data.js:108-163` (56 lines: "97th season · 21 March – 28 June", "Most valuable player", "Defender of the year", "Sixth man", "Coach of the year") | 4 seasons of award rows | all English | **none** | not displayed: `RECENT` is referenced nowhere else in `web/js/` or `index.html` |
| Also English in source | `data.js:350` `b:"Sixth man of the year in 2026."`, `data.js:320` `b:"779 points in 33 games to win the 2025 MVP."` (both overlaid by `BIO_ES`, `index.html:860` and `:845`); `cab.note` "The Indios de Mayagüez under a different name and city." (`data.js`, `F.cab`; overlay not checked) | | | | |

**The one English line a visitor can see:** `POOL` entry `José «Piculín» Ortiz`, `b: "«Piculín». Reached the NBA and came home to finish."` (`data.js:288`). Root cause: `BIO_ES` is keyed `'José Ortiz'` (`index.html:829`) but the pool name is `José «Piculín» Ortiz`, so the override never matches. A Spanish string already exists for him (`'«Piculín». Llegó a la NBA y volvió a casa a terminar.'`), so this is a key fix, not new text. Since PHASE_67C no bio is shown in ¿Quién soy?, so it is only visible where `POOL.b` is rendered (Perfil/Jugadores).

**Provenance (git).** The English text was in the scaffold commit `195fc2a` (2026-09-07) and moved unchanged: `46a0c5a` (2026-09-09, "replace stale bsn_archivo.html with the real current file") -> `65bca96` (2026-09-09, Pages deploy) -> `21ab6df` (2026-09-24, extract `js/data.js`) -> `499a2d6` (2026-09-25, retire `app/bsn_archivo.html`). The Spanish overlay (`HOF_ES`, `BIO_ES`, `NBA_ES`) first appears in `46a0c5a` and also moved with the same commits, so there was never a version where the Spanish was edited into the source tables.

**Strings that need Spanish (not translated here):**
- Needs Spanish at runtime now: **1**, the Piculín bio (resolved by re-keying; text already exists).
- Source-layer English that is currently masked: 18 `HOF.role`, about 42 `HOF.hon`/`note`, 44 `POOL.b`, 7 `NBA_PLAYERS`, plus `cab.note`. If the overlay is ever removed, all become visible.
- English with **no** overlay and not displayed: the whole `RECENT` block (`data.js:108-163`). Either delete it as dead data or translate it before it is ever wired in; it also carries "97th season" style labels.

- **Proposed fix (72B):** re-key `BIO_ES`; then decide between (a) keep the overlay and add a test that fails if any runtime string is English, or (b) move the Spanish text into the source tables and delete the overlay. (b) is the durable choice but touches ~110 strings, so it needs owner approval of every changed public string.
- **Risk:** low for the re-key; medium for (b).
- **Needs owner:** (b) yes (strings); the re-key no.

---

## 6. Hard-coded numbers in `web/js` (and `index.html`)

PHASE_68 already made the main counts derived (`YEARS.length`, `FKEYS.length`, `MVP_YEARS.length`, `LAST`), so what is left is smaller. Method: regexes for a number plus a count noun in every file under `web/js/` and in `web/index.html`; targeted greps for 97, 98, 3,303, 376, 385, 1930, 2025, 2026; the `COVERAGE` tables.

**Should be derived from data or one config:**

| # | Location | Value | Derive from |
|---|---|---|---|
| H1 | `tabs.js:1440` | "98.ª temporada" | `YEARS.length + 1` (or `SEASON_STATE`) |
| H2 | `tabs.js:3582` | `let FIN_YEAR=2026` | `Math.max(...Object.keys(FINALS_BY_YEAR))` |
| H3 | `tabs.js:4407` | label "Finales juego a juego (2024, 2025, 2026)" | keys of `FINALS_BY_YEAR` |
| H4 | `tabs.js:1674`, `:2261` | `2026: W-L` tag | `SEASON_STATE` year |
| H5 | `player.js:226` | "3.303 jugadores" and fallback `385` | `PALL.length`, `PINDEX.length` |
| H6 | `tabs.js:2782`, `:3445` | Dalmau "2.302 asistencias en 537 juegos … 4,3 … 5,1" duplicated in prose | the `LEADERS` row |
| H7 | `tabs.js:3443` | "13 títulos" (San Germán, 1942-43) | `F.sge.won.length` |
| H9 | `games.js:722`, `:742` | `34` games in a perfect season (`wins===34`, `34-w`) | a `SEASON_STATE.games` field |
| H10 | `tabs.js:261`, `:1556`, `:4969`, `:4972`, `:4985`, `:5062`, `:5064`; `index.html:184` | "34 juegos", "12 equipos" in prose | one config value, or leave as stated league rule (see below) |
| H11 | `tabs.js:3419` and `init.js:388-397` | **two different `COVERAGE` tables** (for example 1950s = 20 in `tabs.js`, 30 in `init.js`; 2010s = 60 vs 75) with a footnote calling the percentages an "estimación editorial" | the manifest counts; or drop the percentages |
| H12 | `index.html:7,8,14,19,67,83,87` | "1930-2026" in titles, meta, splash | build-time constant; meta tags cannot be JS-derived without a build step (PC7), so keep static and add to the season checklist |

**Hard-coded facts in prose or overlays that duplicate data (a row changing means these go stale; derive where cheap):** `index.html:663,675,682,696,697,845,850` (HOF/REC/BIO overlays repeat points, games and rebounds), `tabs.js:3764,3774,3785,3888,3908,3917` (ages, seasons in bios), `tabs.js:430,442` ("41 años", "96 años"). These are sourced statements, not counts; they need a source check, not derivation.

**Fine to leave:** `helpers.js:240` `EPOCH=Date.UTC(2026,0,1)` (daily-game seed; it must not move), hex/color math, SVG paths, `NUM_WORDS_ES_APOCOPE`.

- **H11 deserves owner attention:** the percentages are unsourced numbers (PC1), and the two copies already disagree.
- **Risk:** low; all are UI strings or constants with a data source in the page.
- **Needs owner:** H11 (keep, source, or drop); H10 (league rules are facts about 2026 and could change).

---

## 7. Label conflicts

**Defensive award.** Dominant form: **"Defensor del Año"**.

| Form | Count | Where |
|---|---|---|
| Defensor del Año | 6 | `tabs.js:434`, `:5225` (`AWL.def`), `:7048`, `:7056`, `:7067`; `data.js:454` |
| Defensor del año (lowercase año) | 1 | `index.html:855` (`BIO_ES` Moses Brown) |
| **Defensa del Año** | 1 definition, renders **41 rows** | `tabs.js:1937` `SEASON_AW.defensive_player`, used for every 1958-2004 season detail; the league's own historic page also prints `DEFENSA DEL AÑO` (`docs/specs/historic_followup_spec.md:62-63`) |
| Jugador Defensivo del Año | 1 | `tabs.js:3839` (Butler's `life` prose: "Siete veces Jugador Defensivo del Año") |
| DPOY | internal only | `src/parse_players.py:75`, specs |

So a visitor sees "Defensa del Año" for 41 historic seasons and "Defensor del Año" for 2024-2026, for what is probably the same award. The data key is `defensive_player` in all of them (`web/data/seasons/*`: 41 rows).

**Sixth man.** Dominant form: **"Sexto Hombre"** (the three archive-label rows in `SEASON_AWARDS`: `tabs.js:435`, `:5226`, `:7050`, `:7068`, 4 occurrences). Variants: **"Sexto hombre del año"** (`index.html:860`, Christian López), **"Sixth man"** (English, `data.js:115` as a tuple label) and **"Sixth man of the year in 2026."** (`data.js:350`, English bio, masked by `BIO_ES`). The other "del Año" awards read "Novato del Año" (8), "Progreso del Año" (5). Case drift: "Novato del año" (5), "Progreso del año" (2), "Defensor del año" (1) vs. capital Año.

**Proposed fix (72B):** one label table (`AWARD_LABELS`) read by `SEASON_AW`, `AWL`, `SEASON_AWARDS` and the `BIO_ES` overlay; the owner picks the official names. Add a test that every award string in the app belongs to the table.

- **Confidence:** high on the counts; the correct official names are unknown.
- **Risk:** low.
- **Needs owner:** **yes** (official names: "Defensor" vs "Defensa", "Sexto Hombre" vs "Sexto hombre del año", and capitalization). Already listed in `data_review_todo.md` "string fixup 3".

---

## 8. Identity and club items

### 8a. Atenienses de Manatí -> Cariduros de Fajardo
- Claim: `web/js/data.js:94-95` `ate.note = "Se mudó a Fajardo en 2017."`; `docs/project.md` D2 lists it as a relocation; `data/clean/franchises.csv:14` says `relocated 2017 -> Fajardo`, source column "owner 2026-09-20 + primerahora.com…".
- Evidence against treating it as a lineage fact: (1) `data/clean/franchise_events.csv` has no event linking the two; (2) `franchises.csv:17` has Cariduros de Fajardo as a separate franchise (1973-2023, "derived:champion/scoring rows"), so Cariduros already existed for decades; (3) Cariduros appear in the 2018 and 2019 leaders (`web/data/seasons/2018.json`, `2019.json`), consistent with a continuous club, not a 2017 arrival; (4) the archive shows Atenienses only in 2015 and 2016 (`docs/specs/manati_audit_spec.md` F5); (5) per `data_review_todo.md`, the cited URLs were taken from search results and never fetched, and es.wikipedia `Cariduros_de_Fajardo` returned 404 on Oct 10.
- **Confidence:** the note is unverified (high), and the lineage "Atenienses became Cariduros" is contradicted by the repo's own franchise table (medium).
- **Proposed fix:** remove the claim from `ate.note` (or replace it with "Jugó en el BSN en 2015 y 2016", which the archive supports), keep `franchises.csv` status as `ended 2017`, and correct D2.
- **Needs owner:** **yes** (the claim originates from the owner on 2026-09-20 and is written into D2 of `project.md`).

### 8b. Javier González vs Gonzalez
Three spellings in `game_box_player.csv`, none with a `bsnpr_id`:

| Spelling | Rows | Seasons | Team | Candidate |
|---|---|---|---|---|
| `Gonzalez, Javier` | 82 | 2001-2003 | QUEBRADILLAS (all 82) | id 1006 "Gonzalez Otero, Javier" (no birth data, no season rows, `has_profile=no`) |
| `González, Javier` | 2 | 2008 | blank | none (id 2513 starts in 2011) |
| `GonzÃ¡lez, Javier` | 58 | 2012-2013 | Santurce 57, Humacao 1 | id 2513 "González López, Javier" (b. 1989, Armador, Humacao 2012 with 3 games, Santurce 2013 with 20, `player_career_seasons.csv`) |

The earlier note ("one player under three spellings") is not supported: the 2001-03 Quebradillas rows cannot be id 2513 (his first season is 2011), and the 2012-13 Santurce/Humacao rows match 2513's club-seasons. The item 3 dry run confirms it independently: once the mojibake is decoded, the existing resolver assigns **id 2513 to all 58 `GonzÃ¡lez` rows** with no change to its rules. **Most likely two different players**, plus 2 unresolvable 2008 rows. Both ids share the alias `Gonzalez, Javier` (type `paternal_surname`), which is why name-only matching would merge them.
- **Confidence:** medium-high for 58 -> 2513; medium for 82 -> 1006 (no season rows to corroborate); the 2 rows stay unresolved.
- **Proposed fix:** extend the resolver's club tiebreak (the one `player_id_map.csv` used for 16 rows) to box scores, so 2012-13 rows resolve to 2513 and the rest stay unresolved; do not merge.
- **Needs owner:** only if they want 1006 asserted without season evidence.

### 8c. Teófilo Cruz club
`POOL.c = ['san']` (Cangrejeros de Santurce); ¿Quién soy? holds him out. Evidence for: MVP 1962, 1967, 1970, 1971 all list Santurce (`web/data/index/mvp.json`, id 2200); scoring titles 1960 and 1962 list Santurce (`scoring_titles.json`). He has **no** season rows in `jugador.asp` (0 of the spine's rows), and played 1957-1982 (HOF), so other clubs are not excluded.
- **Confidence:** high that Santurce is correct for those six seasons; unknown whether it is his only club.
- **Fix:** keep `c=['san']`, remove the `HOLD` entry only if the owner accepts "six season rows, club list may be incomplete" for clues that say "Jugó con…".
- **Needs owner:** yes (the clue wording is a completeness claim).

### 8d. Mario Morales club
`POOL.c = ['san']` but `STONE`, `HOF` and the Coliseo say Mets de Guaynabo. MVP rows 1980, 1982, 1983, 1993 all list **Guaynabo** (`mets_guaynabo`, id 1584); scoring title 1993 lists Guaynabo; **scoring title 1980 lists Cangrejeros de Santurce** (`scoring_titles.json`) while the MVP row for the same 1980 season says Guaynabo, an internal conflict. No season rows in `jugador.asp` for id 1584.
- **Confidence:** high that both clubs are real for him; the 1980 contradiction is unresolved (a mid-season move, or a source error).
- **Fix:** set `c=['san','gua']` (or the franchise id the Mets map to) with the 1980 note; do not choose one.
- **Needs owner:** yes (club list and the 1980 note).

### 8e. Legends with no structured final clue
Seven of the 30 `legend`/`figura` players are not playable:

| Player | Honor fields | Why not playable | In-repo source? |
|---|---|---|---|
| J. J. Barea | none | no award, rank, title, club count or averages | `NBA_PLAYERS` only (free text) |
| Jerome Mincy | none | same; no clubs | none |
| Butch Lee | none | same; no clubs; NBA note is free text | `NBA_PLAYERS` note |
| Jonathan García | none | POOL ppg 0.7 / rpg 0.3 / apg 1.2 for a 33-assist record holder looks like an RGM sample artifact | record row (removed from clue use) |
| Sammy Betancourt | scoring titles | no ppg/rpg/apg or club count, so the earlier clues leave one candidate too soon | `SCORING` rows |
| Teófilo Cruz | mvp, scoring, rank | held (8c) | |
| Mario Butler | mvp, rank | held (item 1; MVP 1988 join; no club) | |

- **Fix:** none derivable from the repo for the first four; Betancourt needs career averages or a club count.
- **Needs owner:** yes (accept them as non-playable, or supply a source).

---

## 9. Proposed data-update flow (design only, nothing built)

One command, `make data-update`, wrapping `python -m src.data_update`, default mode **check** (writes to a temp directory and reports a diff against the committed `data/clean/` and `web/data/`), with `--apply` to write.

```
make data-update                # check mode, exit 1 on any gate failure
make data-update ARGS=--apply   # write data/clean and web/data, never commits
```

Stages, each idempotent and runnable alone with `--only <stage>`:
1. **preflight**: clean tree for `data/clean` and `web/data`; `.venv` present; **refuse to run `parse-players` or `sync-web-data`** (N7: they are not idempotent at HEAD; this pipeline calls neither).
2. **parse**: only parsers whose control run (unchanged code, output to a temp dir) reproduces the committed output byte for byte. `parse-games` fails that test today (365 `bsnpr_id` drift, item 3), so it stays out of the default run until the drift is resolved or absorbed by an overlay; each parser gets its own control-run entry in the report. Raw is read-only (PC5).
3. **normalize**: the existing overlays in a fixed order (`apply_career_dedup`, `apply_jug05_*`, `apply_identity_decisions`) plus the new game-name repair overlay and the display-name override layer; each supports `--check`.
4. **validate** (`src/verify_clean` plus a new report, below); any new failure blocks stage 5.
5. **regenerate web/data**: `src.build_web_data` only.
6. **test**: `pytest -q`; compare against the recorded baseline (856 passed, 1 known failure until fixed).

**Validation report** (`data/reports/data_update_YYYYMMDD.md`, git-ignored, summarized on stdout): row counts per clean table before/after; provenance columns complete (PC3); NULL vs 0 scan (PC2); mojibake scan (`Ã`, `Â`, U+FFFD) over `data/clean` and `web/data`; English-string scan over the tables in item 5; name-quality counts per cause (item 2); box-score invariant (`2*FG2+3*FG3+FT==PTS`, 39,663 of 39,669 hold today); career-leader ratio check (total/games vs average, flags Dalmau); RECORDS vs LEADERS agreement (flags item 1); award-label vocabulary (item 7); identity coverage (box `bsnpr_id` resolution 55%); franchise lineage coverage; a diff summary of every changed row by table.

Commits remain manual (P4); the pre-commit hook (`.githooks/pre-commit`) already enforces a fresh `web/data/`.

---

## 10. Proposed build split (ordered by risk, lowest first)

| Phase | Scope | Files touched | Risk | Gate |
|---|---|---|---|---|
| **72A** | Pipeline and validation report only; no data changes. Includes fixing or retiring the one failing baseline test. | `Makefile`, new `src/data_update.py`, new `src/validate_report.py`, new `tests/test_data_update.py`, `tests/test_web_text.py` (or retire it), `.gitignore` (`data/reports/`) | low (additive) | baseline is the starting point; report prints the audit's counts as the "before" |
| **72B** | Web-layer fixes with no data change: `BIO_ES` key for Piculín; one award-label table; derive H1-H7, H9; English-string test; Cariduros note removal; `COVERAGE` unification | `web/index.html`, `web/js/tabs.js`, `web/js/data.js`, `web/js/init.js`, `web/js/player.js`, `web/js/games.js`, new `tests/test_labels_72.py`, `tests/test_no_english_runtime.py`, `docs/strings_pending_phase72.md` | low-medium | owner approves award names and every changed string; Chromium + WebKit at 390 and 1000 |
| **72C** | Mojibake root fix (per-sequence decoder) and repair of the 296 rows. Recommended: overlay `src/apply_game_name_repair.py` rewriting only those rows and their ids; alternative: full `parse-games` regeneration, which also moves 365 unrelated `bsnpr_id` values | `src/parse_games.py`, new `src/apply_game_name_repair.py`, new `tests/test_parse_games_decode.py`, `data/clean/game_box_player.csv` (and, only for the regeneration option, `game_results.csv`, `game_plays.csv.gz`), then `web/data/games/**`, `web/data/starting_five/*` | medium (overlay: low) | diff is exactly 296 rows (overlay) or 661 rows (regeneration), reviewed row by row; `tests/test_web_data_encoding.py` stays green |
| **72D** | Name normalization layer | new `src/normalize_names.py`, new `data/overrides/name_overrides.csv`, `src/build_web_data.py`, new `tests/test_name_normalization.py`, regenerated `web/data/seasons/**`, `index/mvp.json`, `index/scoring_titles.json` | medium | before/after name diff in the report; owner approves override list and display style |
| **72E** | Identity and club items | `src/parse_players.py`-free overlay (`src/apply_identity_decisions.py`), `data/clean/franchise_events.csv`, `data/clean/franchises.csv`, `web/js/data.js` (`ate`, Cruz, Morales `c`), box-score club tiebreak in `src/parse_games.py` | medium-high | owner decisions on 8a, 8c, 8d; no merge on name alone (D1) |
| **72F** | Honors and rebounds: derived rank-1 honors (6 players), RECORDS/LEADERS resolution, provenance columns on `bsn_records.csv` and `bsn_career_leaders.csv`, outside data for 2012-2023 awards and 2022-2025 seasons | `data/clean/` (new `player_honors_derived.csv`), `src/build_web_data.py`, `web/js/tabs.js`, tests | highest | needs outside data (P5, paid or network) and owner sign-off |

N7 applies to every phase: none of them may run `make parse-players` or `make sync-web-data`.

---

## 11. Owner decisions needed

1. Item 1: what counts as an independent source for career rebounds, and whether to show a "disputed" note meanwhile.
2. Item 2: display style for names (accents, nickname quotes, drop maternal surname); Larry vs Elias Ayuso; wording for `NO FUE SELECCIONADO`.
3. Item 3: approve the `parse-games` regeneration (rewrites `data/clean/`).
4. Item 4: whether leaderboard-#1 rows count as honors; approval to fetch outside data (P5).
5. Item 5: keep the Spanish overlay or move the text into the source tables (about 110 strings).
6. Item 6: keep, source or drop the `COVERAGE` percentages; whether league-rule numbers (34 games, 12 teams) become config.
7. Item 7: official names: Defensor vs Defensa del Año; Sexto Hombre vs Sexto hombre del año; capitalization.
8. Item 8: Atenienses -> Cariduros claim and D2 in `project.md`; Cruz and Morales club lists and the Morales 1980 contradiction; legends that stay non-playable.

---

## Appendix 4 — the 303 by group

**A (35):** Alade Aminu; Alejandro Carmona Sanchez; Alex Morales; Angel Nunez; Angel Suero; Archie Goodwin; Benito Santiago Jr.; Braxton Key; Chaundee Brown Jr.; D.J. Hogg; Dewan Hernandez; Diamond Stone; Emmy Andujar; Frank Gaines; Gilberto Clavell; Greg Smith; Guillermo Diaz; Ike Diogu; Isaac Sosa; James Ennis; Jessie Govan; Juan Miguel Suero; Kalin Lucas; L.J. Figueroa; Melo Trimble; Mitchell Creek; Nick Minnerath; Ricky Sanchez; Robert Glenn; Tai Wesley; Tony Bishop Jr; Tyreke Evans; Weyinmi Efejuku Rose; Will Daniels; Zavier Simpson.

**B (86):** A.D. Vassallo; Alex Galindo; Alize Johnson; Angel Matias; Ben McCauley; Ben Moore; Brandon Costner; Brandon Goodwin; Brandon Knight; Brian Conklin; Bryce Cotton; Bryn Forbes; Cameron McGriff; Chane Behanan; Cheick Diallo; Chinanu Onuaku; Christopher Ortiz; Damien Wilkins; David Laury; David Stockton; DeMarcus Cousins; Deonte Burton; Gabe York; Gaby Belardo; Georgie Pacheco-Ortiz; Grant Basile; Hassan Whiteside; Ismael Cruz; Ismael Romero; Ivan Gandia-Rosa; Jack McVeigh; Jahlil Okafor; Jahvari Josiah; Jalen Crutcher; Jameer Nelson Jr; Jared Sullinger; Jaylen Nowell; Jaysean Paige; Jezreel De Jesus; Joel Soriano; John Meeks; Jordan Howard; Jordan Murphy; Josh Perkins; Justin Keenan; Kaleb Werson; Kay Felder; Kobi Simmons; Kristian Doolittle; Kyle Vinales; Larry Ayuso; Leon Williams; Malik Beasley; Maxwell Abmas; Mike Young; Milton Doyle; Montrezl Harrell; Nathan Sobey; Nathaniel Mason; Nick Perkins; Nick Rakocevic; Norris Cole; Peter John Ramos; Phillip Wheeler; Q.J. Peterson; Ramses J. Melendez Vega; Ricky Ledo; Rigoberto Mendoza; Rondae Hollis-Jefferson; Sam Waardenburg; Sam Young; Scottie James; Stevie Thompson; Tai Odiase; Terrence Jones; Terrico White; Theo Pinson; Thomas Robinson; Timothy Soares; Torrey Craig; Tyquan Rolon; Tyrell Harrison; Victor Rudd; Von Wafer; Will Barton; Will Martinez.

**C (182, no per-season rows):** Admiral Schofield; Aleem Ford; Alejandro Ralat; Alejandro Vazquez; Alexander Franklin; Alexander Kappos; Anthony Cowan Jr; Anthony Morales; Antonio Gordon; Antonio Ralat; Arguster Daniels IV; Arnaldo Toro; Avry Holmes; Bradley Camacho; Brady Manek; Brandon Boyd; Bryan Gonzalez Colon; Bryan Powell; Butch Lee; Cady Lalanne; Carlos A Colon; Carlos Emory; Carlos Yao Lopez; Chris Brady; Chris Gaston; Chris McCullough; Chris Ortiz; Christian Lopez Santiago; Christian M. Negron; Christian Pizarro Rios; Corey Jae Crowder; Corey McKeithan; D J Wilson; Damian Jones; Daniel Rosado; Daniel Santiago; Darius Bazley; Darnell Hinson; David Scott James Jr; Davon Jefferson; Deandre Pinckney; Denis Clemente; Derek Reese; Derrick Walton; Devin Williams; Devon Collier; Diego Gonzalez Pellot; Dimencio Vaughn; Dyondre Dominguez; E.J. Crawford; Elijah Hughes; Emmanuel Andujar; Enrique Ramos; Eric Ayala; Eugene German; Evander Ortiz Colon; Felix A. Rivera Vega; Fernando Caballero Acevedo; Gabriel J. Belardo; Geancarlo Peguero; George Alexander Hamilton; Gerardo Texeira; Gian Clavell; Giancarlo Rosado; Gianfranco Grafals; Giovanni Santiago; Harold Perez Abreu; Hiram Huertas; Hunter Tyson; Ian Clark; Ibrahima Sylla; Isaiah Hicks; Isaiah Palermo; Isaiah Pineiro; Isiah Gaiter; Iván Gandía; J. J. Barea; Ja Kair Sanchez; Jack Edward McVeigh; Jacob Wiley; Jae Crowder; Jalen Bernard Crutcher; Jamarion Sharp; Jamil Wilson; Jampier Lezcano; Janiel Jafet Romer; Jared Ruiz; Jase Febres; Javier Ezquerra; Jay Shawn Alvarez; Jayden Martinez; Jaylin Galloway; Jeff Early Jr.; Jeffrion Aubry; Jerome Mincy; Jesus A. Cruz Galarza; Jevin Nikolas Muniz; John Brown III; John Holland; John Jenkins lll; Johned Walker; Jonathan García; Jonathan Rodriguez; Jonathan Zhao Olmos; Jordan Daniel Cintron; Jorge Brian Diaz; Jorge L. Matos; Jorge L. Pacheco; Jorge Luis Torres; Jose Carlos Placer Diaz; Jose Roman Angueira; Joseph Bull; Joshua Denton; Joshua Rivera; Josue Erazo; Juan Pablo Pineiro; Julian Torres; Justin Reyes; Kendall Munson; Kendric Davis; Kenneth Faried; Kenneth Santos Velez; Kevin Allen; Kevin Maura Colon; Khary Mauras; Kyle Rose; Leandro Allende; Lee Benson; Luis D. Cuascut; Luis Henriquez; Luis Hernandez; Luis Lopez Martinez; Luis Moya; Luis Rivera Rosario; Malachi Smith; Malik Williams; Manny Camper; Manuel Camper; Marlon Hargis; Marvin Eliel Mantilla; Matthew Lee; Michael J. Bruesewitz; Michael O Connell; Miguel Martinez; Neftali Acevedo Diaz; Neftali Alvarez; Nick Lucena; Noah Horchler; Oenis Medina; Olumiye Oni; Omar Figueroa; Onzie Branch; Owen Perez; Rafael A. Pinzon Duperoy; Raymond Cintron Jr; Reinaldo Santana; Richard Nunez; Rico Hopping; Robert «Tractor» Traylor; Robiel Morales; Ruben Cotto; Ryan Arcidiacono; Ryan Pearson; Rychell Janga; Stephen Thompson Jr.; Terence Davis; Theophilus A. Pinson Jr.; Timajh Parker; Tjader Fernandez; Tory San Antonio; Tyler Cook; Tyler Davis; Tyler Polo; Vicktor Lakhin; Wilfredo Rodriguez Valentin; William Cruz Rodriguez; Wilmer Lugo-Sanchez; Xavier Zambrana; Yahir Cordero Melendez; Ysmael Romero; Zhaire Jahi-Ihme Smith; Ángel «Munch» Cruz.
