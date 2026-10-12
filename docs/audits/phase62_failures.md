# PHASE_62 failures (before any fix)

Source: `tests/test_cuadricula_exhaustive.py` + `tests/harness/grid_probe.mjs` (drives the site's real `submitGuess()` in Chromium). Universe: 665 cells (every row club x column axis the generator can emit; 382 have at least one solution), 376 players in POOL, 1858 (player, spelling) guesses.

## A. Valid player, valid cell, spelling rejected (name matching)

| category | failed / tried | rejecting function | 5 examples (name -> typed -> game resolved) |
|---|---|---|---|
| padded | 357 / 357 | norm() helpers.js:30 -> trim() only; inner double spaces survive, so norm(input) never equals norm(name) | Christian Dalmau -> `  Christian  Dalmau ` -> not found; Larry Ayuso -> `  Larry  Ayuso ` -> not found; Ángel Rodríguez -> `  Ángel  Rodríguez ` -> not found; Renaldo Balkman -> `  Renaldo  Balkman ` -> not found; Gary Browne -> `  Gary  Browne ` -> not found |
| suffix_with_comma | 10 / 13 | norm() does not remove commas: "benito santiago, jr" != "benito santiago jr" | Benito Santiago Jr. -> `Benito Santiago, Jr.` -> not found; Stephen Thompson Jr. -> `Stephen Thompson, Jr.` -> not found; Tony Bishop Jr -> `Tony Bishop, Jr.` -> not found; Jameer Nelson Jr -> `Jameer Nelson, Jr.` -> not found; Anthony Cowan Jr -> `Anthony Cowan, Jr.` -> not found |
| dots_spaced | 5 / 17 | norm() deletes "." but keeps the space: "q j peterson" != "qj peterson" | Q.J. Peterson -> `Q. J. Peterson` -> not found; A.D. Vassallo -> `A. D. Vassallo` -> not found; D.J. Hogg -> `D. J. Hogg` -> not found; E.J. Crawford -> `E. J. Crawford` -> not found; L.J. Figueroa -> `L. J. Figueroa` -> not found |
| hyphen_as_space | 5 / 5 | norm() keeps "-": "hollis jefferson" is not a substring of "hollis-jefferson" | Rondae Hollis-Jefferson -> `Rondae Hollis Jefferson` -> not found; Zhaire Jahi-Ihme Smith -> `Zhaire Jahi Ihme Smith` -> not found; Georgie Pacheco-Ortiz -> `Georgie Pacheco Ortiz` -> not found; Ivan Gandia-Rosa -> `Ivan Gandia Rosa` -> not found; Wilmer Lugo-Sanchez -> `Wilmer Lugo Sanchez` -> not found |
| no_nickname | 4 / 4 | norm() strips the quote marks, not the nickname word: "jose ortiz" != "jose piculin ortiz" (nickKey/stripNick exist, helpers.js:48-49, but Cuadricula does not use them) | José «Piculín» Ortiz -> `José Ortiz` -> not found; Juan «Pachín» Vicéns -> `Juan Vicéns` -> not found; Robert «Tractor» Traylor -> `Robert Traylor` -> not found; Raúl «Tinajón» Feliciano -> `Raúl Feliciano` -> not found |

All other spellings tried (exact, lower, upper, accent-less, straight quotes, suffix dropped, dots removed) resolve correctly.

## B. Valid player missing from a cell (criterion data)

Cells where an independent fact says the player qualifies but the game's `solutions()` omits them: **15 cells**, 8 distinct players.

| criterion | distinct players | rejecting predicate | examples |
|---|---|---|---|
| a:mvp | 1 | `CATS.mvp` = curated `p.t.includes('mvp')` (data.js:513); tag missing although `mvp.json` lists the award | Jaime Frontera |
| a:p20 | 1 | `CATS.p20` (data.js:530) reads `p.hi[1]`, which for most players is only the 2026 official line, ignoring the per-season `ss` rows | Brandon Knight |
| a:scoring | 6 | `CATS.scoring` = curated `p.t.includes('scoring')` (data.js:514); the tag was never added although `scoring_titles.json` lists the title | Al Thornton, Christian Dalmau, Juan «Pachín» Vicéns, Mike Harris, Paris Bass |

Wrong players accepted into a cell (false positives): **0**.

### Not counted as failures: need an owner decision (nothing applied)

- Larry Ayuso / scoring: table row says ELIAS AYUSO (2002); pool says Larry
- Carlos Bermúdez / mvp: table row says Charlie Bermudez (1978); pool says Carlos
- Mario Butler / mvp: mvp.json 1988 vs Hall-of-Fame card mvp:0
- Rubén Rodríguez / mvp: mvp.json 1979 vs Hall-of-Fame card mvp:0
- Neftalí Rivera / mvp: mvp.json 1973 vs Hall-of-Fame card mvp:0
- Rolando Frazer / mvp: mvp.json 1981 vs Hall-of-Fame card mvp:0

## C. Fragment matching (`POOL.find(norm(x.n).includes(v))`, first hit wins)

- typed `Candido Fret` -> not found
- typed `Alamo` -> not found
- typed `Alamo, Candido Fret` -> not found
- typed `Hector Reyes` -> not found
- typed `Reyes` -> Justin Reyes
- typed `Hector` -> Héctor Blondet
- typed `Zzzz Nobody` -> not found
- typed `ab` -> Pablo Alicea
- typed `Dalmau` -> Raymond Dalmau
- typed `Blondet` -> Héctor Blondet

Expected: `ab`, `Dalmau` (two players) -> not found/ask; `Blondet` (one) -> Héctor Blondet. `Candido Fret`, `Alamo`, `Hector Reyes` are archive-index players that are not in the game pool: not found is correct.

## D. Phase-60 suspect points, resolved

1. First-substring-hit: **occurs** (section C).
2. `norm` gaps: **occur** (section A: commas, spaced initials, hyphens, inner spaces, nickname word).
3. Duplicate `p.n` in POOL: **does not occur** (376 names, 376 distinct).
4. Missing `t`/`pos`/`hi`: players with no club or no tags are never wrongly matched (PC2 holds); the real data failure is stale curated tags and `hi` (section B). Players with no club data (`c: []`) cannot appear in any club cell: a data gap, not fixable without inventing data.

## E. After the fixes

Same probe, same oracle: 28/28 tests in `tests/test_cuadricula_exhaustive.py` pass (before: 9 failed). Full suite 704 passed, 1 xfailed, 1 known failure (`test_web_text` frozen-original, unchanged).

| item | before | after |
|---|---|---|
| spellings rejected: padded / `, Jr.` / `Q. J.` / hyphen / nickname dropped | 357 / 10 / 5 / 5 / 4 | 0 / 0 / 0 / 0 / 0 |
| cells omitting a qualifying player | 15 (7 players on scoring/MVP, 1 on 20+ ppg) | 0 |
| wrong players accepted into a cell | 0 | 0 (guarded by tests) |
| fragment `Dalmau` / `ab` | first match / first match | not charged, asks for more |

Fixes: `submitGuess` matching (`gk` fold + unique-fragment rule, games.js), `CATS.p20` best-season over `ss` (data.js), `addArchiveTags` IIFE for 6 scoring + 1 MVP tag with archive evidence (index.html), per-criterion rejection reason (placeholder text, see `docs/strings_pending_phase62.md`).

## F. Left for the owner (nothing applied, nothing invented)

- **Disputed tags** (listed in section B): Larry Ayuso (table says ELIAS AYUSO), Carlos Bermúdez (table says Charlie Bermudez), and MVP rows for Butler, Rodríguez, Rivera, Frazer, which contradict the Hall-of-Fame cards' `mvp:0`. Same stance as D5.
- **MVP rows with no club in the pool** (Ramón Rivas 1989, Roberto Ríos 1995): the `mvp` tag would change no cell, because rows are clubs and these players have `c: []`. Not added.
- **Players with no club list** (`c: []`, e.g. Ramón Rivas, Butch Lee, Daniel Santiago): can never fill a club cell. Needs source data, not code.
- **Alamo / Candido Fret, Reyes / Hector**: archive-index same-name players, not in the 376-player game pool; the game answers "no está en la nómina". Typing only `Hector` resolves to Héctor Blondet because it is the one pool player containing it (unique-fragment rule, unchanged policy).
- Autocomplete (`drawSugg`) still matches with `norm()` only, so typing `Jose Ortiz` shows no suggestion although submitting it works.
