# Pre-2007 root-scheme ingest — spec

<!-- H2 structure. PHASE_3C, 2026-09-08. -->

Cross-refs: [`archive_probe_spec.md`](archive_probe_spec.md) (the PHASE_3B probe
that found this scheme), [`../coverage_root.md`](../coverage_root.md) (the
per-script CDX coverage table), `data/interim/cdx_root_inventory.csv`.

---

## [PURPOSE]

PHASE_1 enumerated only `bsnpr.com/estadisticas*`. PHASE_3B found the 2000–2002
site served leader/standings/team data from **root-level** scripts. PHASE_3C
enumerates the whole `bsnpr.com/*` space, fetches the pre-2007 leader/team-stat
tranches (all ≤500 distinct captures), and parses them to `data/clean/`.

---

## [DECISION]

**1. CDX at `bsnpr.com/*`, drop `/estadisticas/`.** `src/enumerate_root.py`.
135,005 captures; 133,454 outside `/estadisticas/`. The persisted inventory
(`cdx_root_inventory.csv`) keeps only the ~34k stats/game/player-script rows —
the rest is news/forum/image noise. `docs/coverage_root.md` tables every script.

**2. Fetch budget gate.** Owner rule: report coverage before bulk-fetching any
tranche over 500 distinct captures. PHASE_3C fetched only the ≤500 tranches
(315 distinct captures total). `src/fetch_pre2007.py` hard-refuses any script
with >500 distinct digests (`MAX_TRANCHE`).

**3. Ingested this phase** (`data/raw/pre2007/`, one GET per digest, PC5/PC6):

| script | distinct | what it is | clean output |
|---|--:|---|---|
| `lidereshistoricos.asp` | 6 | season scoring champions 1948→2004 + MVP/ROY/DPOY award histories | `historic_scoring_champions.csv`, `historic_awards.csv` |
| `lideres2000/2001/2002.asp` | 22 | per-category player season leaders, `<pre>`-formatted | `player_season_leaders_2000_2002.csv` |
| `equiposstat.asp` | 254 | per-team roster with full season box-score totals + per-game rates, 2001–2003 | `player_season_stats_2001_2004.csv`, `team_season_totals_2001_2004.csv` |
| `campeonatos.asp` (root) | 19 | champion ledger — duplicates `/estadisticas/campeonatos.asp` | *not re-parsed — PHASE_3 output stands* |
| `lideres.asp` (root) | 11 | duplicates `/estadisticas/lideres.asp` (2004–2017) | *not re-parsed* |
| `posiciones2000.asp` | 3 | 2000 standings by phase | *deferred — see open Q* |

**4. GATED — reported, NOT fetched** (each >500, owner approval needed):

| script | distinct | window | what it is |
|---|--:|---|---|
| `jugador.asp` | **5986** | 2004→2026 | per-player detail pages (`?id=N`) — the identity spine's other half |
| `pogamestat.asp` | 4059 | 2007→2021 | game box scores |
| `a2gamestatpbp.asp` | 3093 | 2001→2004 | play-by-play |
| `gameinfo.asp` | 1457 | 2007→2010 | game metadata |
| `boxscore.asp` | 1075 | 2007→2009 | box scores |
| `gamestatwide.asp` | 864 | 2001→2004 | game stats |
| `pogamestatwide2.asp` | 512 | 2004→2007 | game stats |
| `jug05.asp` / `jugador05.asp` | 600 / 600 | 2005→2007 | player pages, 2005-era scheme |

**Under 500, fetchable in a follow-up without a new gate:** `playbyplay.asp`
(460), `equipo.asp` (489), `equipo05.asp` (184), `informe.asp` (175, game
reports 2004–2006), `print_jugador.asp` (203).

**This is a roadmap-scale finding.** Box scores and play-by-play for 2001–2021
were archived. B1 (the DevTools box-score hunt) has partial answers here — a
`pogamestat.asp` / `boxscore.asp` ingest phase is now viable without the live
site.

---

## [RATIONALE]

- **Why `lidereshistoricos.asp` is the highest-value small tranche.** One page,
  4 tables: scoring champions **1948→2004** with games + total points + ppg
  (the seed `bsn_scoring_champions.csv` runs 1966–1991, ppg-only for most of
  it), and MVP / Rookie / Defensive-Player histories **1958/1964→2004** (RealGM's
  award floor is 2014-15). The 1952 row is split `* Feliciano / * Santori` with
  a footnote — carried as two `disputed` rows (PC1, mirrors D5).
- **Why `equiposstat.asp` is worth 254 fetches.** It is the only pre-2007
  source of **player-level** season stats. Per team-season it gives a
  `PUNTOS ACUMULADOS` table (season totals: `MJ CC 3P TL DFF TOT A CB B TO PT`,
  where `CC`/`3P`/`TL` are `"<attempted>-<made>"` — verified against the
  `PROMEDIO` table's percentages) and a `PROMEDIO POR JUGADOR` table (per-game
  + shooting %). 503 player-seasons, 2001–2003, 14 teams.
- **Why `campeonatos.asp` / `lideres.asp` root are not re-parsed.** Same engine,
  same content as their `/estadisticas/` equivalents, which PHASE_3 already
  parsed to `champions_from_bsnpr.csv` (1930→2020) and `player_season_leaders.csv`.
  Re-parsing would produce duplicate rows with a second `source_url`. If PHASE_4
  wants a second provenance source for a disputed champion row, the raw files
  are in `data/raw/pre2007/campeonatos/`.
- **Why `<pre>` parsing for `lideres200x`.** These pages render each leader
  table as fixed-width text in a `<pre>` block, `&nbsp;`-padded — `read_html`
  sees nothing. `_PRE_ROW` matches `"<rank>. <name> (<club>) <JJ> <stats> <prom>"`.
  `lideres2000.asp` has **surname only** (no first name) — a real D1 limitation,
  stored verbatim. Fixed-width overflow can clip a counting stat (`"101"→"01"`);
  those rows get `parse_flag=value_maybe_clipped`, never a reconstructed value.

---

## [ALTERNATIVES_REJECTED]

- **Fetch `jugador.asp` (5986) this phase** — no; over the 500 gate. It is the
  single highest-value gated tranche (per-player career pages → the D1 spine
  with `enciclopedia.asp`) and should be its own phase.
- **Fetch the game-level scripts** — no; all >500, and box-score/PBP parsing is
  a large effort deserving its own phase. Reported so the roadmap can plan it.
- **Persist the full 133k-row root inventory** — no; 25 MB of mostly news/forum
  noise. The 34k stats-relevant subset is tracked; the raw CDX JSON
  (`data/raw/cdx/cdx_root_*.json`, 46 MB) is gitignored but regenerable.
- **Coalesce `equiposstat` `CC "151-90"` to a single FG% number** — no; keep
  `fga` and `fgm` as separate nullable columns (PC2), derive rates downstream.

---

## [INTERFACES]

### `src/enumerate_root.py` (`make enumerate-root`)
`bsnpr.com/*` CDX (un-collapsed + digest-collapsed), cached to
`data/raw/cdx/cdx_root_{all,bydigest}.json`. Writes the filtered
`data/interim/cdx_root_inventory.csv` + `docs/coverage_root.md`.

### `src/fetch_pre2007.py` (`make fetch-pre2007`)
Requires `data/interim/cdx_root_inventory.csv` — gitignored (5.9 MB,
regenerable); run `make enumerate-root` first on a cold start. One GET per
digest for the `IN_SCOPE` scripts,
`raw_wayback_url` + `polite_get`. `MAX_TRANCHE=500` hard gate. `--script NAME`
for one tranche. → `data/raw/pre2007/<script>/<ts>_<digest8>.html` (+meta),
`data/interim/fetch_manifest_pre2007.csv`. Run 2026-09-08: 313 fetched, 0
failed, 2 `equiposstat` captures were live DB-error pages (skipped in parse).

### `src/parse_pre2007.py` (`make parse-pre2007`)
- `parse_lidereshistoricos()` — latest capture; section title → `scoring` /
  `mvp` / `rookie` / `defensive_player`; `*`-prefixed player → `disputed`.
- `parse_lideres_200x()` — `<pre>` blocks; `_PRE_ROW` regex; category by the
  `JJ … Prom` column signature; latest capture per `(season, category, serie)`.
- `parse_equiposstat()` — `PUNTOS ACUMULADOS` + `PROMEDIO POR JUGADOR` tables;
  `_split_att_made` for `CC/3P/TL`; `Totales` row → team totals file; latest
  capture per `(team, season, serie)`.
- All outputs carry `source_id=wayback_bsnpr_root`, `source_url`, `retrieved_at`,
  `confidence` (PC3).

### `data/clean/` outputs (PHASE_3C)
| file | rows | grain |
|---|--:|---|
| `historic_scoring_champions.csv` | 58 | season (1948–2004) |
| `historic_awards.csv` | 135 | award × season |
| `player_season_leaders_2000_2002.csv` | 403 | season × category × serie × rank |
| `player_season_stats_2001_2004.csv` | 503 | player × team × season |
| `team_season_totals_2001_2004.csv` | 38 | team × season × serie |

`src/verify_clean.py` gained `verify_pre2007()` — provenance on every row, D4
`metric_era` flip at 1970/71, 1952 dispute carried as two rows, made ≤ attempted,
contiguous ranks. 13,410 assertions total, green.

---

## [OPEN_QUESTIONS]

1. **`jugador.asp` (5986, gated)** — per-player pages. Combined with
   `enciclopedia.asp` (79, from PHASE_3B) this is the D1 canonical player table
   (name + birth year + id + career-by-season). Highest-priority follow-up phase.
2. **The game-level scripts (gated)** — `boxscore.asp`, `pogamestat.asp`,
   `a2gamestatpbp.asp` etc. Box scores + PBP, 2001–2021. Needs its own phase and
   a structure probe first. Directly relevant to B1.
3. **`equiposstat.asp` only yielded 2001–2003** despite CDX running to 2004-02 —
   the 2004 captures are either 2003-season data or DB errors. 2004 team stats
   may be recoverable from `equiposstat_print.asp` (92) or the 2004
   `lidereshistoricos` capture's context. Not chased.
4. **Standings** — `posiciones2000.asp` (3) fetched but not parsed;
   `estadisticas.asp` cluster standings (2000–2002, by phase) sit in
   `data/raw/probe/`. A `standings_pre2007.csv` is a small follow-up.
5. **Club codes** — `lideres200x` uses 5-char codes (`MOROV`, `SAN G`);
   `equiposstat` uses full names; `equiposstat` URLs use 2-letter `t=` codes
   (`BA`, `PO`). Build one code→franchise map in PHASE_4.
6. **`lideres2000.asp` surname-only** — resolving these to canonical players
   needs the birth-year/club match against the `jugador.asp` spine; until then
   they stay low-confidence rows.
