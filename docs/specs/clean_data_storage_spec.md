# Spec: Clean-Data Storage Format (large tables)

## [PURPOSE]

`data/clean/` is the deliverable. It is **not** reliably regenerable from a
fresh clone: `data/raw/` is gitignored, and rebuilding it means re-fetching
~10,000 Wayback captures under the PC6 polite-crawl throttle (≥1 s/request,
sequential) — a multi-day job, and the archived captures may not even still
resolve. So every `data/clean/` table must live in the repo in a form git can
carry indefinitely.

One table breaks that: `game_plays.csv` — the play-by-play event log.

| | rows | raw CSV | gzip -9 |
|---|---|---|---|
| game_plays (2001–2003, `a2gamestatpbp.asp`) | 233,665 | 65.3 MB | 2.7 MB |

Problems with committing it raw:

1. **GitHub warns at 50 MB, hard-blocks at 100 MB.** 65 MB already trips the
   warning. `playbyplay.asp` (460 captures, ungated, queued) and any future
   modern-PBP ingest push it toward the block.
2. **History churn.** `make parse-games` rewrites the whole file (rows are
   re-sorted and re-derived) every ingest session. Each run adds a fresh
   multi-MB blob to history forever; CSV regenerations delta poorly against
   each other. Two revisions already committed.
3. The file is 233k rows — never eyeballed, never usefully `git diff`-ed. Its
   plain-text form buys nothing that offsets 1–2.

This is a P2 (storage-architecture) call per `docs/global.md` [PAUSE_CONDITIONS];
logged here per [SPEC_AND_HANDOFF_PROTOCOL] H1/H2.

## [DECISION]

**Commit large clean tables gzip-compressed (`<name>.csv.gz`), read and
written transparently by a shared helper. Keep them as single logical files —
do not split.**

Applies now to: `game_plays.csv` → **`game_plays.csv.gz`**.

Mechanism:

- `src/parse_wayback.open_clean_text(path, mode)` — the one place that knows
  the convention. On a `.gz` suffix it wraps `gzip.GzipFile(..., mtime=0,
  compresslevel=9)` in a UTF-8 `TextIOWrapper`; otherwise a plain
  `path.open`. `mtime=0` pins the gzip header clock so byte-identical input
  produces byte-identical output — a no-op reparse yields an empty git diff.
- `_write_csv` (shared, `src/parse_wayback.py`) routes through it. A parser
  opts a table in **only** by giving it a `.csv.gz` path — see
  `src/parse_games.py` `_write_csv(CLEAN / "game_plays.csv.gz", ...)`.
- `src/verify_clean.py` `_clean_path()` resolves a bare name to whichever of
  `<name>` / `<name>.gz` exists; `_read()` / `_exists()` use it. Consumers
  keep asking for `"game_plays.csv"`.
- `pandas.read_csv` reads `.gz` natively (`compression='infer'`), so any
  future pandas-side consumer needs no special handling.

**Threshold for opting a table in:** raw CSV **> ~20 MB** on disk. Today only
`game_plays.csv` qualifies. `game_box_player.csv` (10 MB, growing with the
held `pogamestat` 2007–09 tranches) is the next candidate — when it crosses
~20 MB, change its `_write_csv` path to `.csv.gz` and delete the tracked
`.csv`; no other code change is needed.

**Not done:** rewriting history to purge the existing 65 MB
`game_plays.csv` blob (commits `2d1928c`, `7f09013`). It packs to ~7 MB, the
whole `.git` dir is 10 MB, and a purge is a `git filter-repo` + force-push =
P1 + G4, needing explicit owner approval. Flag for a future cleanup pass if
`.git` growth becomes a real problem; not worth it now.

## [RATIONALE]

- **24× smaller, one file, zero new dependencies.** `gzip` is stdlib; pandas
  and the `csv` module read `.gz` transparently. Nothing to install, no clone
  prerequisite, no CI step.
- **Kills the churn.** Each regen now adds ~2.7 MB to history, not ~65 MB,
  and `mtime=0` means a reparse with unchanged data adds *nothing*.
- **Smallest blast radius.** One helper, one parser line, one verify helper.
  No consumer signature changes.
- **Boring and proven (C4).** Gzipped CSV is a standard interchange format
  for large tabular data.
- **Reversible.** `gunzip data/clean/game_plays.csv.gz` restores the plain
  file; flip the parser path back. No format lock-in.
- **The plain-text loss is already sunk.** A 233k-row file that is fully
  re-sorted every parse produces no reviewable diff and is never read by eye.
  `zcat` / `zgrep` / `pandas` cover every real access pattern.

## [ALTERNATIVES_REJECTED]

- **Git LFS.** Solves history churn and keeps one logical file, but: adds
  `git lfs install` as a clone/CI prerequisite (owner is one week into git;
  the repo has App-Store publish ambitions); GitHub free LFS is 1 GB storage
  + **1 GB/month bandwidth**, and every clone of a growing multi-MB file eats
  that fast; and a missing LFS checkout leaves a ~130-byte pointer file that
  `pandas.read_csv` will "successfully" parse as garbage — a silent-corruption
  mode this project's provenance culture (PC1/PC3) specifically rejects.
- **Split by season** (`game_plays/game_plays_2001.csv`, …). Bounds each file
  and aligns with the tranche = (script, year) fetch unit, but pushes
  directory-globbing into the parser, `verify_clean`, and every future
  consumer (reconcile, PBP→`bsnpr_id` linking, PHASE_5 web build) — real
  surface area for a problem gzip closes with one helper. Each partition also
  still churns its own multi-MB blob per regen. Kept in reserve: if any
  single gzipped partition ever approaches the 50 MB warning, split *then*
  gzip the parts.
- **Split by season + gzip each.** Best churn profile, but combines the
  moving-parts cost of splitting with no benefit over plain gzip until a
  single season's PBP is itself huge (not in sight — `a2gamestatpbp` is
  2001–2004 only, ~100k rows/season).
- **Parquet.** Columnar, ~2–3 MB, typed (would help PC2 NULL≠0). Rejected as
  premature: adds a binary format and a pyarrow hard-dependency for the
  pipeline, loses `zgrep`-ability, and the typing win is cosmetic while the
  clean tables are still consumed mostly as strings. Revisit if a clean table
  ever needs real columnar analytics in-repo.
- **Leave it; deal with it in PHASE_5.** `docs/specs/app_data_sync_spec.md`
  chunks PBP into per-game JSON for the *web* artifact, which does dissolve
  the single-file problem — but only for `web/data/`, and PHASE_5 has not
  started. `data/clean/game_plays.csv` remains the pipeline's canonical PBP
  table (consumed by `verify`, and by the not-yet-built reconcile / linking
  passes) regardless of what the web build emits. It needs its own answer now.

## [INTERFACES]

- **Write:** `src/parse_wayback._write_csv(path, rows, fieldnames)` — gzips
  iff `path.suffix == ".gz"`. Deterministic (`mtime=0`, level 9).
- **Open (either side):** `src/parse_wayback.open_clean_text(path, mode)` →
  UTF-8 text handle, `newline=""` (csv-module contract), gzip-aware.
- **Read by name:** `src/verify_clean._read("game_plays.csv")` and
  `_exists("game_plays.csv")` resolve `.csv` → `.csv.gz` automatically via
  `_clean_path()`. New consumers should copy that resolve-then-open pattern,
  or just use `pandas.read_csv(path)` (native `.gz` support).
- **On-disk contract:** exactly one of `data/clean/<name>.csv` or
  `data/clean/<name>.csv.gz` exists for a given table, never both. The parser
  that owns the table picks. `.gitignore` carries neither — both are tracked
  deliverables.
- **Filenames:** `<name>.csv.gz` (double extension), snake_case (C1).

## [OPEN_QUESTIONS]

1. **`game_box_player.csv` (10 MB, growing).** Default: leave plain until it
   crosses ~20 MB, then flip to `.csv.gz` (one-line change, mechanism already
   in place). Not done now to keep this change minimal and because it's still
   comfortably diff-able-ish and under the warning.
2. **History purge of the existing 65 MB blob.** Default: don't. `.git` is
   10 MB. Revisit only if repeated large-blob commits bloat it past, say,
   100 MB — then a single `git filter-repo` pass + force-push, with owner
   approval (P1/G4).
3. **Compression codec.** Default gzip (stdlib, universal). zstd is ~2× faster
   and a bit smaller but adds a dependency. Not worth it at 2.7 MB / one file.
4. **Should `verify` assert the on-disk form** (e.g. fail if
   `game_plays.csv` reappears plain and >20 MB)? Deferred — low value, and
   it'd fire during a legitimate `gunzip`-to-inspect. Revisit if the
   convention gets violated by accident.
