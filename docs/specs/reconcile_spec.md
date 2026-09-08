# Reconcile — spec

<!-- H2 structure. PHASE_4, 2026-09-08. -->

Cross-refs: `docs/project.md` [DOMAIN_RULES] D2/D3/D4/D5/D6,
[`wayback_ingest_spec.md`](wayback_ingest_spec.md),
[`pre2007_ingest_spec.md`](pre2007_ingest_spec.md),
[`identity_spine_spec.md`](identity_spine_spec.md).

---

## [PURPOSE]

Cross-check the parsed archive data against the inherited Wikipedia-derived seed
CSVs, producing (a) a merged view for the ~90 % of rows where the two agree and
(b) **one flagged-conflicts file** for the rest. Per the owner's instruction:
where two sources disagree the row records both values and both sources and is
left flagged — **no conflict is resolved automatically** (also PC1).

---

## [DECISION]

**1. Two independent sources → `verified`.** Where the Wikipedia seed and the
bsnpr `campeonatos.asp` ledger (crawled from the league's own site, not
Wikipedia) name the same champion for a season, that row's confidence rises to
`verified` — the strongest tier. 87 of 98 champion seasons clear this bar.

**2. City → franchise resolution is table-driven and season-aware.** The bsnpr
ledger names champions by *city*; the seed by *franchise*. `CITY_MAP` in
`src/reconcile.py` maps each normalized city to a `franchise_id`, with
per-season exception notes for the cases where the mapping is contested:
- `SAN JUAN / 1936` — seed says "Club Nautico de San Juan", not Capitalinos.
- `SAN JUAN / 1945` — D5 (EN-wiki Capitalinos vs ES-wiki Santos de San Juan).
- `HUMACAO`, `MANATI` — multiple franchises over time; flagged `*` (per-season).

**3. Franchise lineage (D2) is encoded as events, not folded into the master.**
`franchise_events.csv` carries each relocation / rename / merge / split /
hiatus as a dated row with its own `confidence`. The genuinely murky ones are
`disputed`:
- Brujos de Guayama → Osos de Manatí (2022), *but* an "Atenienses de Manatí"
  (2014–17) and the seed's "Osos founded 2014" make the Osos identity itself
  unclear.
- Grises de Humacao → Criollos de Caguas (2023) — revival of the 1976–2006
  Criollos, or a rename of Grises? Unresolved.
- "Santos de San Juan" vs "Capitalinos de San Juan" — same club renamed, or
  two clubs? Bears on D5.

**4. The conflicts file is the deliverable, not a scratch pad.**
`reconcile_conflicts.csv`: `topic, season, source_a, value_a, source_b,
value_b, agree_on, note`. Every row names two distinct sources with two values
and picks neither. `verify` asserts both sides are populated. Current contents
(5):

| topic | season | source A | source B |
|---|---|---|---|
| champion | 1936 | en.wiki: Club Nautico de San Juan | bsnpr: SAN JUAN (city) |
| champion | 1945 | en.wiki: Capitalinos de San Juan | es.wiki: Santos de San Juan (D5) |
| runner_up | 1968 | en.wiki: Cardenales de Rio Piedras | bsnpr: PONCE (city) |
| scoring_champion | 1971 | seed: Teofilo Cruz (22.4 ppg) | bsnpr historic: Frank Cortés (566 pts) |
| scoring_champion | 1974 | seed: Hector Blondet (25.1 ppg) | bsnpr historic: Raymond Dalmau (799 pts) |

**5. A conflict on one slot does not taint the other.** 1968's *champion*
(Cangrejeros / Santurce) is agreed by both sources → `champion_franchise_id`
is filled; only the runner-up is left blank and flagged. Likewise 1945's
runner-up (Gallitos de la UPR) is agreed.

**6. D-rule handling in `champions_reconciled.csv`:**
- **D3** — `1942` (agree) and `1942-1943` (bsnpr_only, note "seed folds this
  into 1942") are both present as distinct season keys.
- **D4** — `scoring_champions_reconciled.csv` carries `metric_era`
  (total_points ≤ 1970, ppg from 1971); the 1971/1974 conflicts are noted as
  possibly the total-vs-ppg-leader distinction, not an outright data error.
- **D6** — `1953` → `agreement=no_champion`, note "NO SE TERMINÓ (PONCE VS SAN
  GERMAN)"; seed and bsnpr concur there was no champion. 2024 runner-up
  (Osos de Manatí) is `seed_only`, noted "bsnpr campeonatos.asp ends at 2020".

---

## [RATIONALE]

- **Why the seed name and the bsnpr city are treated as independent sources.**
  The seed CSV cites `en.wikipedia.org/.../Baloncesto_Superior_Nacional`. The
  bsnpr ledger is a Wayback capture of `bsnpr.com/estadisticas/campeonatos.asp`
  — the league's own record, edited by different people. When they concur it is
  genuine corroboration, not circular.
- **Why 1968 is a conflict and not "bsnpr is wrong".** The bsnpr captures
  *themselves* disagreed on the 1968 runner-up (PONCE in some, RIO PIEDRAS in
  others — already flagged `disputed` in `champions_from_bsnpr.csv`). The seed
  says Cardenales de Rio Piedras. Two of three signals say Rio Piedras — but
  "mostly" is not "resolved", and the owner asked not to pick. Flagged.
- **Why the scoring conflicts get a hedged note.** `lidereshistoricos.asp` is
  titled "CAMPEONES ANOTADORES" and for 1974 lists Dalmau with 799 *total*
  points and 25.0 ppg; the seed lists Blondet at 25.1 ppg. If bsnpr ranked by
  total points (the pre-1971 rule) past the D4 boundary, both could be
  "correct" for their metric. The note says so; it does not adjudicate.
- **Why club codes are a separate small table.** `lideres200x` (5-char),
  `equiposstat` roster pages (full names) and `equiposstat` URLs (2-letter
  `t=`) each use a different code scheme. One `club_code_map.csv` lets PHASE_4+
  turn "club consistency" into the second corroboration signal the identity
  spine's matcher wants (`identity_spine_spec` Q2). `CA` / `CO` are flagged
  ambiguous (Caguas vs Carolina; Coamo).

---

## [ALTERNATIVES_REJECTED]

- **Auto-resolving 1968 to Rio Piedras on a 2-of-3 majority** — rejected;
  explicit owner instruction not to pick winners, and PC1.
- **Dropping `1942-1943`** to match the seed's title counts — rejected (D3): fix
  the key, not the number.
- **Re-parsing root `campeonatos.asp` / `lideres.asp` as extra sources** —
  rejected (D-018): same engine as the `/estadisticas/` versions, would inflate
  `n_captures` without adding an independent voice. The raw files remain
  available if a specific disputed row needs a third look.
- **A single "champions" table replacing both inputs** — rejected. The seed and
  `champions_from_bsnpr.csv` stay as-is (they carry things the reconciled view
  drops — the seed's pre-1930s context, bsnpr's coach + capture provenance).
  `champions_reconciled.csv` is a derived join, regenerable.
- **Game-pool rebuild** — deferred to its own phase; needs the identity spine
  finished and a decision on which seasons/players are solid enough to seed a
  game.

---

## [INTERFACES]

### `src/reconcile.py` (`make reconcile`)
Pure and deterministic — no network, reads only `data/clean/`. Franchise
knowledge (`FRANCHISES`, `FRANCHISE_EVENTS`, `CITY_MAP`, `CLUB_CODES`) is
module data with D2/D5 citations in comments. Helpers unit-tested in
`tests/test_reconcile.py`: `ncity`, `resolve_city`, `resolve_seed_name`.

### `data/clean/` outputs
| file | rows | grain |
|---|--:|---|
| `franchises.csv` | 33 | franchise master (seed 28 + 5 names only in game rows) |
| `franchise_events.csv` | 8 | D2 lineage events, each with `confidence` |
| `city_franchise_map.csv` | 25 | normalized city → franchise_id + season flags |
| `club_code_map.csv` | 29 | lideres200x / equiposstat codes → franchise_id |
| `champions_reconciled.csv` | 98 | season × {champion, runner-up}, `agreement` status |
| `scoring_champions_reconciled.csv` | 68 | season, merged seed + historic + 2007+ leaders |
| `reconcile_conflicts.csv` | 5 | the flagged conflicts — both sources, no winner |

`verify_clean.py` → `verify_reconcile()`: franchise ids unique + referenced ids
real; every conflict row has two populated sides + two distinct sources; the 5
known conflicts are all flagged; agree→verified, conflict→disputed + a note;
D3 (`1942-1943` kept), D4 (`metric_era` flip), D6 (`1953` no_champion).

---

## [OPEN_QUESTIONS]

1. **The 5 flagged conflicts** — need the owner (or a third source: ES-wiki
   directly, the Federación, newspapers). Do not clear them without a decision.
2. **`franchise_events` `disputed` rows** (Brujos/Osos, Grises/Criollos,
   Santos/Capitalinos) — same: a lineage decision is the owner's.
3. **`club_code_map` `CA`/`CO`** — confirm which team each 2-letter code meant
   per season from the `equiposstat` URLs actually fetched.
4. **Applying `player_id_map` to the observation tables** — not done here. Once
   the identity spine's tranche B completes, a follow-up joins `bsnpr_id` into
   `player_season_leaders*` / `player_season_stats_2001_2004` and works the
   review queue with the club-code map.
5. **`historic_scoring_champions` 1948–1965 and 1992–2004** (`historic_only`,
   31 seasons) — no second source yet. ES-wiki has a scoring-leaders list;
   fetching it would corroborate or conflict these.
6. **Career leaders / records** — `bsn_career_leaders.csv` and `bsn_records.csv`
   not yet reconciled against anything computable. D7 (career tables ~5 yr
   stale — treat as floors) still stands.
7. **Game-pool rebuild** — its own phase. The reconciled champions + the
   identity spine + the 2001–2003 player stats are the inputs.
