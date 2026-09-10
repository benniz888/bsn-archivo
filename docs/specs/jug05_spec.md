# Spec: PHASE_3H_JUG05 — the 2005-era player pages

## [PURPOSE]

`jug05.asp` is bsnpr.com's 2005–2007 per-player page: an "Estadísticas
Jugador" heading with `Apellido, Nombre`, a `Ciudad / Nacimiento / Edad /
Posición / Altura / Peso` bio table, and a career-by-season stat table. Same
identity-spine value as `jugador.asp` (which `parse_jugador` already reads),
richer stat columns, different era.

The lever it pulls: `identity_spine_spec.md` Q3. ~106 + ~361 rows in the
player review queue are stuck because their `players_canonical` career table
has no seasons at/near the observed season, so `build_id_map`'s
season-corroboration test has nothing to test against. `jug05.asp` supplies
those pre-2007 career spans.

## [DECISION]

Owner-approved 2026-09-09.

1. **Dedup by CDX digest** — `jug05.asp` has no `?id=N`; pages are keyed only by
   an opaque `r2` token + an `e=<city>` roster context, so many URLs resolve to
   identical content. One HTTP GET per distinct digest (latest capture of that
   digest). `data/raw/cdx/cdx_root_all.json` → 1,257 status-200 captures →
   **600 distinct digests**.

2. **Gated tranches by capture year** — 600 > `MAX_TRANCHE` (500). Fetched as
   three ungated per-year tranches: 2005 ≈ 145, 2006 ≈ 353, 2007 ≈ 102 — each
   under the gate, no `--force`. `make fetch-jug05` runs all three in sequence.
   (The earlier "≈409, ungated" figure was a mis-derivation; `coverage_root.md`
   always listed 600.)

3. **PC6 single stream** — one fetcher, `polite_get` spacing (1.5 s) + 429/5xx
   backoff, reusing `fetch_players._fetch_one`. Nothing else touches Wayback
   while it runs. Raw bytes written unmodified to
   `data/raw/players/jug05/<digest>.html` + `.meta.json`, never re-fetched (PC5).
   ~600 requests ≈ 15 min.

4. **Parse into the spine, never minting an id (D1).** `parse_jug05()` in
   `parse_players.py`, new `source_id = wayback_bsnpr_jug05`. jug05 has no
   league id, so a jug05 player can only:
   - **enrich an existing canonical row** when `name + birth_date` matches one
     of the 3,303 → career rows union into `player_career_seasons` (deterministic
     sort, new source_id);
   - otherwise land in the **review queue** as a name+birth candidate — never
     force-mapped (PC1).

   The measurable outcome is the review-queue / id_map delta after the next
   `make parse-players`.

## [INTERFACES]

- `src/fetch_jug05.py` — `make fetch-jug05` (`--year`, `--limit`, `--force`).
  Manifest: `data/interim/fetch_manifest_jug05.csv` (one row per digest, merged
  across per-year runs).
- `parse_jug05()` — reads `data/raw/players/jug05/*.html`. Two known layout
  quirks:
  - the bio table appears either as header-row + value-row, or one `<tr>` split
    into 12 `<td>` (6 labels + 6 values). Match on the label text, take the next
    6 non-empty cells.
  - the career table's numeric `<td>`s are sometimes merged into one string
    (`'44% 20 14 70% 29 1.0 72 2.5 29 217 7.48'`). Walk `<tr>`/`<td>` manually;
    fall back to a fixed-width numeric regex when a row has fewer cells than the
    header. Only `season`, `team_raw`, `JJ`, `PTS` are kept for the spine.
- `clean_field` / D-042 / D-046 name sentinels apply unchanged.

## [ALTERNATIVES_REJECTED]

- **Dedup by query string (550 → gated, needs `--force`).** More requests for
  the same content; violates the spirit of PC5. Rejected in favour of digest.
- **`jugador05.asp`** (406 param-200s, same era) — a likely-adjacent scheme.
  Out of scope for this phase; noted as a possible follow-up once the jug05
  delta is measured.
- **Manual seed list for the ~50 pre-1970 historic scoring champions** — the
  other Q3 candidate. Not mutually exclusive; deferred.

## [RESULT] (2026-09-09)

600 pages → **200 distinct players** (deduped by name + birth date — the same
player has several pages under different `r`/`r2` tokens). `merge_jug05` runs
a 3-tier match against `players_canonical`:

| tier | test | n | action |
|---|---|--:|---|
| enrich | exact name+year, OR canonical apellidos ⊇ jug05 apellidos (token-prefix) + given[0] + birth date ±7d | **123** | union career rows |
| mint | no canonical match at all | **42** | new canonical `990001`+ (D-047) |
| review | name + birth-year collides with a canonical but the fuller match fails | **35** | `jug05_review.csv`, spine unchanged |

**+1,031 career-season rows** (877 to existing players). Net: `player_id_map`
649 → **661**, review queue 602 → **590**, `players_canonical` 3,303 → **3,345**.

## [OPEN_QUESTIONS]

1. **RESOLVED — owner chose (a):** mint with flagged synthetic ids (`990001`+,
   `source_id=wayback_bsnpr_jug05`, `has_profile=jug05`). D-047.
2. `jug05_review.csv` (35) — nickname bridges ("Larry" Ayuso = Elías, "Bobby"
   Brannen = Robert) and spelling variants (Jefrey/Jeffrion Aubry). A
   prefix/nickname-aware pass could resolve most; deferred to the owner.
3. `jugador05.asp` (406 param-200s, same era) — not fetched. Possible follow-up.
