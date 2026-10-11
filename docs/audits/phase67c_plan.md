# PHASE_67C — ¿Quién soy? clues: plan (Step 1, read-only)

Branch redesign-v3. Nothing under `web/` was edited. Scratch scripts ran from the session scratchpad against the served site. Samples: `docs/audits/phase67c_samples.md`.

## 1. How the ladder works today (`web/js/tabs.js` ~4987–5115)

- Six clues, three guesses, points 60/40/25/15/10/5 by clues shown. `clueList(p)` builds a fixed order for every player:
  1. Decades: "Jugó en los 1980s y los 2000s." (`POOL.d`)
  2. Status: import / native from `POOL.t`; otherwise the literal line "Su estatus no está registrado."
  3. Position via `posEs` (`POOL.pos`); otherwise "no está registrada."
  4. Career ppg, exact number (`POOL.ppg`); otherwise "nunca se registró."
  5. Every club (`POOL.c` → `F[c].name`); otherwise "Su club no está registrado en el archivo."
  6. `POOL.b` bio sentence, else `statClue` (rpg+apg, then spg+bpg).
- Pool: `newQuiz()` filters `d.length && (b || rpg/apg/spg/bpg != null)` and picks uniformly. Result: all 376 POOL players qualify, so the filter excludes nobody.
- Guess check: `norm(name).includes(guess)` with guess ≥ 3 chars. A substring is accepted, so "dal" is right for both Dalmaus and "ort" for any name containing it. Not in scope; flagged.

Why the clues are weak (measured on the 376):
- Clue 1: 279 of 376 (74%) are 2020s players. For them it says "los 2020s" and removes nothing.
- Clue 2: 299 of 376 (80%) have no import/native tag, so they get a dead clue ("no está registrado") in slot 2.
- Clue 3: 283 of 376 (75%) have `posSrc:"perfil"`: the position is computed from the player's own rates (see `data.js` comment), not a listed position. Presented as fact, it is not reliably true. Only 93 (curated block) have a position that was set by hand.
- Clue 4: exact ppg (e.g. 21.6) is checkable but not something fans remember; 32 players have none.
- Clue 5: the full club list is unique for many players but arrives at clue 5 as a flat list.
- Clue 6: the bio. 93 players have one. Bio sentences often contain the answer (nicknames, MVP years). One is still English: Piculín, "«Piculín». Reached the NBA and came home to finish."
- Same ladder shape for everyone: no honors clue, no per-player ordering, no leak checks.
- The pool is 74% 2020s RealGM stat-line players; only 38 carry legend/MVP/figura/10k tags. A random draw is mostly obscure players.

## 2. Data inventory (fields usable as clues)

| Field | Source | Coverage (of 376) | Reliable? |
|---|---|---|---|
| Decades `d` | POOL | 376 | Yes, but 74% say 2020s: weak |
| Status `t` import/native | POOL | 77 | Yes where present; missing for 299 |
| Position `pos` | POOL | 376 | Only 93 curated; 283 computed from rates (`posSrc:perfil`): do not use as a fact |
| ppg / rpg / apg | POOL | 344 / 339 / 337 | Yes, career averages; bucketing is safer than exact |
| spg/bpg, gp, ns | POOL (RealGM block) | ~328 | Yes, recent seasons only |
| Clubs `c` | POOL | 360 (16 empty) | Mostly; conflict: Mario Morales [san] vs STONE "Mets de Guaynabo"; old players list only one club |
| Best season `hi`, season rows `ss` | POOL (RealGM, 2012+) | 314 / 154 | Yes |
| Bio sentence `b` | POOL | 93 | Yes (hand-written); 1 English line; some leak nickname |
| Honors: MVP, scoring titles, finals MVP, rookie, defensive | MVP_YEARS, SCORING, SEASON_AWARDS, FINALS_BY_YEAR, `seasons/*.json` | ~54 players | Yes but coverage is partial → phrase as "al menos N". Name join is first+last token and must be spot-checked |
| Titles by player | `ss` ∩ `F.won`; `players/*.json` career ∩ season champion | ~30 | Floor only (partial coverage) → "al menos" |
| Height, birthplace, birth year | BIO | 12 / 14 / 14 | Yes, but only 17 BIO players |
| Career span | HOF / LEADERS yrs | 18 | Yes; near-unique |
| Legend reasons `legendWhy` | POOL | 24 | Yes |
| Jersey numbers | RETIRED | club-level only | No per-player link; not usable |
| Nationality | `players/*.json`, BIO | sparse | Not usable |

Name issues: no mojibake survives in any pool name (build-time repair is in). `Diego Gonzalez Pellot` and `Bryan Gonzalez Colon` lack the accent, which is cosmetic here because guesses go through `norm()`. The legacy player index joins only 24 pool players by name + decade overlap (the other 2020s players are not in it), so career-based facts barely help.

## 3. Proposed ladder design

Order (hard → easy), each slot picks the best available fact of that kind:
1. Era shape (decade span or "N décadas") or status: broad.
2. Style: ppg bucket or rpg/apg (rounded for ≥ 8 rpg / ≥ 5 apg).
3. Position, only when curated (never `posSrc:perfil`) or height from BIO.
4. Clubs (names or count), or best season.
5. Honor: MVP / scoring title / finals MVP / rookie / defensive / campeonatos ("al menos N").
6. Bio sentence (clean, no nickname/name), the near-giveaway.

Selection and leak rules:
- L1: No name token (≥ 4 letters) or nickname («…») in clues 1–5. A bio with a nickname or English text is not used as the final clue until rewritten (owner approval).
- L2: After clue 1, ≥ 150 pool players remain; after 2, ≥ 40; after 3, ≥ 10 (counting players with a missing field as "could match", so thin data can never look tighter than it is). No clue before 5 may leave a single candidate.
- L3: Any clue that only 1–2 pool players satisfy (exact career span, height, a unique club pair) cannot appear before clue 4; a unique club combination is not allowed before clue 5.
- L4: Counts built from partial coverage use "al menos".
- L5: Positions computed from rates (`posSrc:perfil`) and the dead "no está registrado" lines are never shown.
- L6: Minimum 4 distinct clue types in 5+ clues; clue 6 is the bio if it passes L1.
- Thin players are excluded from the pool; they are not padded.

Selection of the player: weight the draw so legends are not drowned out. Three bands, e.g. Fácil (legend/MVP/HOF-tagged), Medio (pre-2020s or with an honor), Difícil (2020s stat players), drawn 40/35/25 with no repeat in a session. (Open question for the owner.)

## 4. Samples

10 ladders in `docs/audits/phase67c_samples.md`: Dalmau and Torres (very famous), Hodge, Browne, Butler (mid), Blondet, Plummer, Diallo (lesser), Cruz and Báez (1950s–70s). Flagged: Hodge (unique club pair at clue 4), Butler (clues 3–4 near-unique, no clubs, MVP join unverified), Plummer (vague clue 1), Cruz (club unverified, conflicting Morales record), Báez (excluded: 2 clues).

## 5. Counts and difficulty spread

Rules applied to all 376, unknown fields counted as "might match":
- Tier A (≥ 5 clues, ≥ 4 types, no early unique): **100**
- Tier B (4 clues, ≥ 3 types): **36**
- Excluded (X): **240**. 208 have fewer than 4 usable clues (2020s RealGM players with only ppg / clubs / best season), 32 fail the leak rules.
- Usable pool: 136 of 376 (36%). By first decade: 2020s 85, 2010s 24, pre-2010 27 (of 44 pre-2010 players). 25 of the 38 legend/MVP-tagged players land in A, 2 in B, 11 excluded.
- Expected difficulty: 27 easy (the legend/MVP-tagged players in A+B, expected to solve in 3–5 clues), the other 109 split between medium (pre-2020s or with an honor, about 4–5 clues) and hard (2020s stat lines, usually all six). The medium/hard split is an estimate, not measured; the 27 is counted.
- Per-season award files add nothing measurable (A/B counts 100/36 vs 100/37 without them), so the runtime needs no new fetches: MVP_YEARS, SEASON_AWARDS, SCORING, FINALS_BY_YEAR, HOF, BIO, F.won, `ss` are already loaded.

## 6. Recommended build (after approval)

1. Replace the internals of `clueList(p)` and `newQuiz()` in `tabs.js` with a closure-only generator implementing section 3 (0 new top-level names). Candidate counting runs once, memoised on `QZ`/closure state.
2. Pool = tiers A+B (136 now), computed at runtime so it grows automatically as fields fill in; show no clue for a field that is not present.
3. Weighted band draw, no repeat per session.
4. Translate Piculín's bio (needs approved wording).
5. Plural fix in La Temporada Perfecta: `games.js:629`, replace `${DR.skips} pases` with `${DR.skips} ${DR.skips===1?'pase':'pases'}` (also gives "0 pases", "2 pases"). Line 547's "No quedan pases." is unchanged.
6. Strings in `docs/strings_pending_phase67c.md`: new clue templates, the "al menos" forms, the plural. Tests: a static test of the generator rules over all pool players (no name leak, ≥ 4 types, nobody unique before clue 5), plus Chromium + WebKit at 390 and 1000 px.
7. Out of scope unless asked: substring guess matching, the Mario Morales club conflict, MVP name join verification.

Decisions needed from the owner: band weights; whether to hand-write clean final sentences for the 11 excluded legends/MVPs (that would move them into the pool); and whether to fix the guess matching.
