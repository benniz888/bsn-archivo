# Player identity spine — spec

<!-- H2 structure. PHASE_3D, 2026-09-08. Implements D1. -->

Cross-refs: `docs/project.md` [DOMAIN_RULES] D1,
[`pre2007_ingest_spec.md`](pre2007_ingest_spec.md) (Q1 — this is that follow-up),
[`archive_probe_spec.md`](archive_probe_spec.md) (found `enciclopedia.asp`).

---

## [PURPOSE]

D1 names player-identity resolution as the #1 data-integrity risk. This phase
builds the canonical spine it needs: a table of every BSN player keyed by the
league's own id, with `canonical_name`, accent-stripped `normalized_name`,
`birth_date`, an alias table, and — where a profile page exists — position,
nationality and career span. It then links the name strings in the observation
tables (`player_season_*`, `historic_scoring_champions`) to those ids, sending
everything it cannot corroborate to a review queue rather than guessing.

---

## [DECISION]

**1. The canonical ids are the league's, not ours.** `enciclopedia.asp` and
`/jugadores/jugador.asp?id=N` both carry an integer `id`. That id *is*
`bsnpr_id`. There is **no fuzzy de-duplication within the canonical table** —
D1's dedup risk is about linking observations to players, not inventing a player
list. Two enciclopedia rows with the same name and different ids stay two rows.

**2. Two sources, `enciclopedia.asp` is the spine.**

| tranche | source | yields | volume |
|---|---|---|---|
| A | `enciclopedia.asp` (77 distinct captures, 2007–2021) | id + `Apellidos` + `Nombre` (may carry a nickname) + `Camisa` + `Nació` (birth date) for every player | **3,303 distinct ids**, 1,987 with a birth year |
| B | `/jugadores/jugador.asp?id=N` (latest capture per id) | heading = full name incl. nickname; profile table (birth city + date, position, height, weight); career-by-season stat table | **1,079 distinct ids** — enrichment only |

Tranche B is fetched one capture per id (the latest — most complete). It is slow
(Wayback throttles hard); the fetch is idempotent and `parse_players` runs on
whatever subset is present, so it can complete across sessions.

**3. `normalized_name` = accent-stripped, lowercased, punctuation collapsed.**
`normalize("Álamo López, Ángel 'Junito'")` → `"alamo lopez, angel junito"`.
Every canonical row and every alias carries its normalized form; `verify`
asserts they are pure ASCII (D1).

**4. Alias table — one row per (id, alias, type).** Types generated per player:
`canonical`, `normalized`, `enciclopedia` (the raw `Nombre` field),
`given_family_order` (Western "Nombre Apellidos"), `paternal_surname`
("Apellido, Nombre" on the first surname token — Spanish sources drop the
maternal surname), `given_first_only` ("Arroyo, Carlos A." → "Arroyo, Carlos" —
deliberately ambiguous), `initial` ("Carmona, A." — how `equiposstat` writes
names), `nickname`, `nickname_surname`. ~24k aliases for 3.3k players.

**5. Observation → id matching obeys "never on name alone" (D1).** For each
distinct `(obs_source, player_raw, club_raw, season)`:
- candidate ids = exact match of `normalize(player_raw)` against an alias, else
  the order-insensitive `norm_key` (sorted tokens).
- a candidate is **corroborated** only if the observed season falls within its
  career span (`jugador.asp` season table, or `first_season..last_season`,
  ±1 year).
- **exactly one corroborated candidate** → `player_id_map.csv`,
  `match_method = name+season_in_career`.
- **one name candidate, not corroborated** (no profile yet, or season outside
  span) → `player_review_queue.csv`, reason recorded. *Not* the id map.
- **>1 corroborated**, or **>1 candidate none corroborated**, or **no name
  match** → review queue with the candidate ids + reason.

`player_id_map.csv` therefore only ever contains season-corroborated links. As
tranche B fills in career spans, rows migrate from the review queue to the map
on the next `parse_players` run.

---

## [RATIONALE]

- **Why season-in-career is the corroboration, not birth year.** D1 says match
  on "birth year + first season + primary club". The observation rows carry
  none of birth year — only name, club, season. `jugador.asp` gives the career
  span; the season test is the strongest signal available from the observation
  side. Club consistency is a planned second signal (needs the club-code map,
  PHASE_4). Until then a season-in-span match with a unique candidate is the bar.
- **Why `given_first_only` aliases are deliberately ambiguous.** "Arroyo,
  Carlos" genuinely could be Carlos A. Arroyo (id 273) or Carlos Andrés Arroyo
  (id 13124). Emitting the alias for *both* and letting the season test decide
  is correct — id 273's career covers 2001, id 13124's does not, so
  "Arroyo, Carlos / SANTU / 2001" resolves to 273. Without the season test it
  would (rightly) go to review.
- **Why `1/1/1900` is nulled.** The source writes an unknown DOB as `1/1/1900`
  (2 players). Kept as a real date it would poison any birth-year match (PC2).
- **Why the older `/jugador.asp` (2004–06, opaque `r2=` tokens) is skipped.**
  No clean integer id; ~1,300 captures on a dead URL scheme. The modern
  `?id=N` scheme + `enciclopedia.asp` already cover the player set. Revisit only
  if a specific pre-2005 player is missing.

---

## [ALTERNATIVES_REJECTED]

- **Fuzzy string matching (Levenshtein / token-set ratio) for the id map** —
  rejected. It is exactly the "match on name alone" D1 forbids. Truncated names
  (`"Ayuso, Elias 'Lar"`), surname-only rows (`lideres2000`), and initials go to
  review, where a human (or a later phase with the club-code map) resolves them.
- **Assigning our own player ids** — rejected. The league's ids exist and are
  stable across captures; inventing a parallel scheme adds a mapping to maintain.
- **Merging the two "Arroyo, Carlos" ids because the name collides** — rejected.
  They are different people. D1's dedup concern is the opposite error.
- **Fetching all 4,893 `/jugadores/jugador.asp` captures** — rejected; 1,079
  distinct ids, one (latest) capture each is enough for a profile.

---

## [INTERFACES]

### `src/fetch_players.py` (`make fetch-players`)
`--tranche A|B`, `--limit N`. Tranche A from `data/interim/cdx_inventory.csv`
(PHASE_1), tranche B from `data/raw/cdx/cdx_root_all.json` (needs
`make enumerate-root` first). One GET per digest (A) / per id, latest capture
(B); `polite_get`; progress every 25. → `data/raw/players/{enciclopedia,jugador}/`,
`data/interim/fetch_manifest_players.csv` (merged across partial runs).

### `src/parse_players.py` (`make parse-players`)
Pure functions unit-tested in `tests/test_parse_players.py`: `strip_accents`,
`normalize`, `norm_key`, `extract_nickname`, `strip_nickname`, `clean_dob`.
Runs on whatever raw files are present — re-run as tranche B lands.

### `data/clean/` outputs
| file | grain | notes |
|---|---|---|
| `players_canonical.csv` | one row per `bsnpr_id` | `has_profile` flags the tranche-B subset |
| `player_aliases.csv` | (id, alias, type) | `normalized_alias` accent-free |
| `player_career_seasons.csv` | (id, season, team_raw) | from `jugador.asp`; games + points |
| `player_id_map.csv` | (obs_source, player_raw, club_raw, season) → id | season-corroborated links only |

### `data/interim/player_review_queue.csv`
Everything the id map could not take: `candidate_ids`, `candidate_names`,
`reason` ∈ {no canonical name match · unique name, season not in career span ·
multiple players match name + season · multiple name candidates, none
corroborated}.

### `src/verify_clean.py` → `verify_players()`
`bsnpr_id` unique + integer; `canonical_name` present; `normalized_name` /
`normalized_alias` lowercase + ASCII (D1); provenance on every canonical row;
birth_year plausible (1920–2010); `first_season ≤ last_season`; every alias +
every id-map row points at a real id; **every id-map `match_method` names a
corroboration beyond the name (D1)**; no observation is both mapped and queued.

---

## [OPEN_QUESTIONS]

1. **Tranche B completion.** At throttled Wayback rates ~1,079 profiles is a
   multi-hour fetch. Until it finishes, most `player_id_map` corroboration
   falls back to `first_season..last_season` from whatever profiles exist, and
   the review queue is larger than it will be. Re-run `parse_players` after the
   fetch completes.
2. **Club-code map (PHASE_4).** `lideres200x` uses 5-char codes (`MOROV`),
   `equiposstat` full names, `equiposstat` URLs 2-letter (`BA`). A code→franchise
   map turns club consistency into a second corroboration signal and clears much
   of the "multiple players match name + season" bucket.
3. **Pre-2007 players with no enciclopedia entry** (~219 "no canonical name
   match", mostly `historic_scoring_champions` 1948–1970 and `lideres2000`
   surname-only). Candidates: the old `/jugador.asp` scheme, `jug05.asp`, or a
   manual seed list for the ~50 historic scoring champions.
4. **Truncated observation names** (`"Ayuso, Elias 'Lar"`, `"Morales, Mario
   'Qui"`) — the leader-table cell width clips them. A prefix-aware alias match
   (surname exact + given-name prefix) would resolve these safely when the
   season also corroborates; not done yet (kept in review).
5. **Multiple birth dates for one id** across enciclopedia captures — not yet
   seen, but `parse_enciclopedia` takes the first non-null and does not check
   for disagreement. Add a conflict flag if it ever fires.
