# Spec: PHASE_3I — the historic scoring-title seed

Cross-refs: `identity_spine_spec.md` Q3 (this closes it), `docs/project.md` D1.

## [PURPOSE]

`identity_spine_spec.md` Q3: ~300 review-queue rows are stuck because the named
player has no `jugador.asp` profile, so `build_id_map` has no career span to
test the observed season against. The deepest, most valuable slice is the
**scoring champions 1948–2004** — Raúl Feliciano, Pachín Vicens, Teo Cruz,
Johnny Báez, Georgie Torres, Rolando Frazer, Mario Morales … every one a
league legend, every one already in `players_canonical` (the enciclopedia has
them), every one parked in review.

## [DECISION]

Owner-approved 2026-09-10: "yes — a title record corroborates a unique name
match"; scope = **historic champions only**.

1. **Scoring titles are a season attestation.** `historic_scoring_champions.csv`
   / `scoring_champions_reconciled.csv` are bsnpr.com's own records pages naming
   the season's scoring champion. For a review row whose name resolves to
   **exactly one** canonical candidate, that record corroborates the season —
   stronger than the `first_season..last_season ±1` heuristic already in use,
   and D1-compatible (not "name alone": name **+** a league per-season record).

2. **`seed_historic_spans(canon, aliases)`** — a pre-step before `build_id_map`.
   `_title_seasons()` maps `norm_key(champion name) → {season}`; for a name that
   resolves (via the alias/norm_key index) to a single canonical id, its
   `first_season`/`last_season` are extended to span the title years.
   `n_seasons` is left untouched — a title run is not a season count. Then
   `build_id_map`'s existing `in_career` test corroborates the observation
   naturally; where the pre-step couldn't resolve a unique id (ambiguous alias
   index) `build_id_map` adds a `match_method = name+season+title` branch.

3. **`app/player_crosswalk.csv` as an additive alias source.** The owner-curated
   crosswalk (verdict `auto`/`review`, id present) is fed into `build_id_map`'s
   alias index — it resolves clean-name review rows the alias table's
   comma-forms miss (Georgie Torres → 788, Edwin Pellot → 553). Additive only;
   it never removes an existing candidate.

4. **`data/interim/player_historic_seed.csv`** — a small hand-curated override
   (`observed_name, bsnpr_id, confidence, note`) for the residue the auto
   matcher can't split: a dup-canonical champion (Anthony Farmer → 172, the row
   with a birth year) and a nickname gap (Willie Simms → id 2314 "Simms,
   William"). **Authoritative** — replaces the candidate set for that name.
   No new canonical rows are minted; every historic champion already exists.

## [INTERFACES]

- `parse_players.seed_historic_spans` / `_title_seasons` / `_crosswalk_name_ids`
  / `_historic_seed_ids`. `build_id_map` gains `match_method = name+season+title`
  and the two curated sources.
- `build_web_data.build_scoring_titles` resolves a `bsnpr_id` on each
  champion / `dual.ppg` via `player_id_map.csv` (64/68 rows).
- App: `scoring_titles.json` → `SCORING[i][5] = bsnpr_id`; the "Campeones de
  anotación" table renders the champion name as a **Ficha** button when
  resolved (`showPlayer(name, id)` → archive card + season observations).
- `verify_clean`: `player_historic_seed` rows target a real id + carry a note;
  the `match_method` D1 check already accepts "…season…".

## [ALTERNATIVES_REJECTED]

- **Minting new canonical rows for the champions.** Not needed — all are in the
  enciclopedia. D-047 wouldn't cover them anyway (no birth date + no career
  table from a league profile source).
- **`lideres2000` bare-surname bucket (63) / `Surname, Initial` (35) / truncated
  modern names (84).** Distinct mechanisms (club-corroborated surname/prefix
  matching, spec Q4). Deferred — owner scoped this phase to historic champions.
- **Seeding `n_seasons` from the title count.** A title run (7 titles across
  1948–55) is not "7 seasons played". Left blank — genuinely unknown.

## [RESULT] (2026-09-10)

`[historic-seed] 40 canonical career spans seeded/extended from scoring titles`.

| | before | after |
|---|--:|--:|
| `player_id_map` | 668 | **716** (+48) |
| review queue | 583 | **535** (−48) |
| historic-champion review rows | 39 (of 58 obs) | **0** |
| `name+season+title` links | 0 | 4 (the rest resolve as `name+season_in_career` off the seeded span) |
| `scoring_titles.json` rows with a `bsnpr_id` | 0 | **64 / 68** |

`players_canonical` unchanged at **3,343** (no minting). Deterministic through
parse + build (`manifest.json` md5 `206fee5fa09ea51bb4d13948bbb5a33c`).
`make verify` PASS, `make test` 169 passed.

## [OPEN_QUESTIONS]

1. The Teo Cruz canonical DOB (`1/8/1948`) makes him 12 at his 1960 title — a
   plain enciclopedia error, not a mis-link (he is the only Teófilo Cruz
   Downs). Candidate for a future `player_dob_overrides.csv` row if a better
   source turns up.
2. `identity_spine_spec.md` Q4 (truncated / surname-only observation names) is
   the remaining review-queue lever — a separate phase.
