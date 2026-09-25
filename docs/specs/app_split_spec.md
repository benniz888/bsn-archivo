# The static-site split: `app/bsn_archivo.html` → `web/`

Status: complete, PHASE_1_SPLIT steps 0–10, branch `phase-1-split`. `web/` is the site; `app/` is
an archived pointer (see section 6).

## 1. What this was and why

Through 2026-09-24 the whole site was one file, `app/bsn_archivo.html` (~8,500 lines, ~663 KB):
markup, every rule of CSS, and the entire app in one inline `<script>`. `web/index.html` was a
byte-for-byte copy of it, plus `web/data/*.json`, `web/sw.js` and the PWA manifest bits. That
worked, but a single 663 KB file is hard to navigate, hard to diff, and was going to get harder to
work with as more BSN league data arrives (the stated long-term motivation — an iOS wrapper — was
explicitly out of scope for this phase).

This phase turned `web/` into a conventional multi-file static site with **zero visual change and
zero behavioral change** — a pure refactor. No bundler, no framework, no build step, no
dependencies (see `[PROJECT_OVERRIDES] O1` in `docs/project.md`); every file here is served
exactly as written, and new data can drop into `web/data/` without touching any of this.

## 2. The file map

`web/index.html` now holds structure, the theme-init `<script>` (FOUC prevention, unchanged,
still inline and first), and a short list of `<script src="js/*.js?v=<hash>">` tags loading, in
this order:

| File | What it holds | Declarations |
|---|---|---|
| `web/css/main.css` | Every CSS rule (was the inline `<style>` block) | n/a |
| `web/js/data.js` | The big hand-curated constants: `F`, `RECENT`, `HOF`, `RETIRED`, `REF_RULES`, `ON_THIS_DAY`, `POOL`, `VENUES`, `FIVE_2026`, `SEASON_STATE`, `POOL_2026`, `POOL_RGM`, `POOL_PATCH`, `PLAYERS_NEW`, `MESES`, `DIAS`, `CATS`, `HL_SETS` | 18 |
| `web/js/helpers.js` | `$`/`el`/`esc`/`slug`/`norm`/`num`/`dash`/`pct`, routing (`showTab`, `setHash`, `showView`), storage (`MEM`/`ST`/`DATA`), the DOB formatter, the puzzle PRNG (`mulberry32` and friends) | 23 |
| `web/js/player.js` | The archive player page: `buildPlayerIndex` through `renderArchiveCard`, plus the disputed-row tag/tooltip formatters (`dqFlag`/`dqTag`/`disputeFlag`/`disputeTag`) | 15 |
| `web/js/data-quality.js` | The `#archivo/calidad` tab whole: `ensureDQ`, `buildDQ`, `openDQ`, `drawDQ`, `drawDQTable`, and their state | 12 |
| `web/js/games.js` | Three of the four archive games: Cuadrícula + Temporada Perfecta, and Sube y Baja | 58 |
| `web/js/tabs.js` | Every remaining tab-rendering function, the fourth game (¿Quién soy?), navigation-building code (`buildNav`, the mega-menu, `_showPanel`), the view-router (`buildViews` and friends), and (STEP 10 cleanup) `MVP_YEARS`/`SEASON_AWARDS`/`FINALS_BY_YEAR`/`OWNERS`, appended at the end of the file — their consumers (`buildMVPYears`, `buildSeasonAwards`, `buildFinalsByYear`, `buildOwners`) already lived here; step 9 had flagged them as misplaced tab data but left them inline, out of its own authorized scope | 267 |
| `web/js/init.js` | `hydrate()` and the boot sequence (`ARRANQUE`: `splashProgress`, `hideSplash`, `finishBoot`, `runBoot`, ...) | 7 |
| `web/index.html`'s own inline `<script>` | Whatever is left — see section 3 | 26 |

426 top-level declarations total, unchanged from the original file (verified at every step —
`tests/harness/inventory.py`, see section 5). Run
`python3 tests/harness/inventory.py <out.json> web/index.html web/js/*.js` for the exact,
current, name-by-name map; `tests/harness/inventory_web_split.json` is the last generated
snapshot, checked in.

## 3. What's still inline, and why

Not everything could move. Three different reasons kept things in `web/index.html`'s own
`<script>`, deliberately, not as an oversight:

1. **Data and data-derivation, not a specific tab or boot machinery** — the `CAPA DE IDIOMA` IIFE
   (`(function translate(){...})()`, overlays Spanish display text onto data already in
   `data.js`), and the whole `DERIVED` section (`champOf`/`ruOf`/`deriveChampions`,
   `YEARS`/`LAST`/`NSEASONS`/`FKEYS`/`ACTIVE`/`NOTES`/`POOL_NAME_ALIAS`/`FAME_W`/`fame`, plus
   several more merge/derive IIFEs). `deriveChampions()` does run at the script's own top level,
   but synchronously, before `runBoot()` ever starts — a different thing from "the boot
   sequence" itself, which is why it didn't go to `init.js`.
2. **`THEME`** (`THEME_BAR`/`THEME_ICON`/`THEME_NEXT`/`THEME_ES`, `osTheme`, `resolvedTheme`,
   `currentTheme`, `applyTheme`, `setTheme`, `toggleTheme`, `initTheme`) — kept inline by explicit
   decision, and necessary regardless because of point 3.
3. **A load-order hazard: `const BOOT=[...]`, `CAT_KEYS`, `GRID_CLUBS`.** These are the two real
   bugs this phase caught, both only by the real-browser offline test, never by a static or
   byte-offset check:
   - `GRID_CLUBS = FKEYS.filter(...)` (step 7) is a top-level `const`, evaluated the instant its
     script runs — unlike every other cross-file reference in this split, which is safely
     deferred inside a function body and only resolved once every script has loaded. `FKEYS` is
     computed in this inline remainder, which loads dead last, so moving `GRID_CLUBS` to an
     earlier-loading file threw `ReferenceError: FKEYS is not defined` at that file's own load
     time — which aborts the REST of that file's top-level code too, not just the one bad line.
   - `BOOT` (step 8) is the same shape of bug on an *array* of function references instead of a
     single one: `['tema',initTheme]` is the one entry, out of ~50, that points at something
     (`initTheme`, THEME) that stays inline. Moving the whole array broke the same way.

   **The lesson, for anyone extending this split further:** a group's correct byte *position* in
   the original file is a completely different question from whether it's *safe to move*. Check
   every `const`/`let` initializer's own top-level expression (not just its shape) and every
   bare array/object literal for function references, before moving — not after a broken
   real-browser test.

## 4. The reconstruction mechanism (`tests/_web_text.py`)

While the split was in progress, `tests/_app_text.py::app_text()` reconstructed
`app/bsn_archivo.html`'s exact original byte stream from the split `web/` tree, so every test that
used to scan the single file kept working against `app_text()` instead, and so each step could
prove nothing was lost or reordered.

**STEP 10 (cleanup) retired the comparison, not the mechanism.** `app/bsn_archivo.html` stopped
being a meaningful comparison target the moment it became the archived pointer (section 6), so no
test compares against it byte-for-byte any more (`tests/test_web_text.py`'s self-test compares
against a frozen git blob instead — see below). But the module itself — renamed
`tests/_web_text.py`, its one function renamed `app_text()` → `web_text()` — turned out to still
be necessary and was **kept, not deleted**: several tests need "the whole app's current text" for
a substring check whose target genuinely spans more than one split file (the Calidad de datos
view's markup/state/render functions, for one, now live across `web/index.html`,
`web/js/tabs.js`, and `web/js/data-quality.js`). `web_text()` is the only thing that can still
answer that question correctly. This was found, and fixed, only after the pointer replacement
(item 2) landed and a full `pytest` run turned up more breakage than the narrow "5 tests" scope
first assumed — `tests/test_data_quality.py`, `tests/test_site_notices.py`,
`tests/test_dob_format.py`, and `tests/test_route_slugs.py` all read `app/bsn_archivo.html`
directly (not through `app_text()`) in places beyond their one named byte-copy test; all four were
repointed to `web_text()` the same way. A separate, more consequential instance of the same thing
turned up in **production code, not a test**: `src/build_web_data.py`'s `_parse_app_mvp()` (feeds
`web/data/index/mvp.json`, via `build_mvp()`) and `diff_app_champions()` (a print-only sanity
check) both parsed baked JS directly out of `app/bsn_archivo.html`; both were repointed to read
`web/js/tabs.js` and `web/js/data.js` respectively — the data they parse didn't move, only its
file. This section is kept, historical narrative intact, since the same mechanism (or its lessons)
will apply again if the remaining inline content ever gets split further.

The core idea: every extracted block is a `(group_start_marker, preceding_anchor)` pair.
`preceding_anchor` is exact original text that survives, byte for byte, in the reconstruction
*so far*, immediately before where the block used to sit — the block is spliced back in right
after it. `group_start_marker` is the exact text the split-out file's own block begins with, used
to cut that file back into its original pieces.

Blocks don't reassemble file-by-file (all of `data.js`, then all of `helpers.js`, ...): a later
step's block can sit, in the true original document, between two blocks that moved in an earlier
step — or even between a block and text that's still inline. So every block from every file goes
into ONE list, `_INSERTION_ORDER`, sorted by where its marker's true byte offset falls in
`app/bsn_archivo.html` — the one file that never changed throughout the whole phase, and so the
only reliable ground truth for "what really came before what." Reconstruction plays that list
back in order, splicing each block into the growing reconstruction.

This surfaced real bugs, not just bookkeeping: a later step could move something that an
*earlier* step's block was anchored on (steps 4, 6, 7, 9), and step 8 alone collided with 15 of
the 25 anchors that existed before it — every one resolved by checking `app/bsn_archivo.html`'s
own byte offsets before finalizing, the same discipline used for the load-order hazards in
section 3.

## 5. Verification standard used at every step

- **`tests/harness/capture.mjs`**: 48 deterministic captures (6 tabs + `#archivo/calidad` + 5
  named player pages, × Chromium/WebKit × 1000px/390px) — DOM, computed styles, accessibility
  tree, console errors, failed requests, all diffed against the frozen baseline
  `tests/harness/baseline/*__main_27c16a4_det.json` (from `main@27c16a4`, before any of this
  phase started, with `Math.random`/`Date` seeded so captures are reproducible).
- **`tests/harness/inventory.py`**: the 426-declaration name-by-name map (section 2), verified
  unchanged (same names, same count) at every step.
- **`src/update_asset_hashes.py`**: every `<link>`/`<script src>` carries a
  `?v=<sha256 of the file's own bytes, first 12 hex chars>` query string, recomputed by
  `.githooks/pre-commit` whenever `web/css/` or `web/js/` changes, so a visitor can never get a
  stale asset paired with a fresh page.
- **A real-browser offline test per step** (Playwright, a throwaway `/tmp` copy of `web/`): old
  build cached with its own old `sw.js`, swap in the new build, N online loads, then go offline
  and reload — this is what caught the `GRID_CLUBS` and `BOOT` bugs (section 3), neither of which
  a static or byte-offset check could have found.
- `pytest` and `python -m src.verify_clean` — assertion count grew, never shrank, as the split
  progressed (see `docs/session.md`'s phase entry for this phase, and the `verify_clean.py`/test
  docstrings themselves for the current checks). STEP 10's `verify_web_data()` rewrite (the
  `app_text()`-vs-`app.html` byte compare retired) checks three different things instead — every
  `web/index.html` asset tag resolves to a real file, every `?v=` hash matches its file's current
  bytes, and the split's declaration inventory still matches the frozen pre-split name set — and
  the same check is exercised from plain `pytest` too (one test per downstream file that used to
  carry the byte-copy assertion), not just `make verify`.

## 6. `app/bsn_archivo.html` after the split

`app/bsn_archivo.html` is now a one-paragraph pointer to this document and to `web/`. It is kept,
not deleted — an archived record that the single-file app existed and where it went — but it is no
longer read by any test, build step, or the deployed site. `web/` is the sole source of truth. That
last clause took two passes to actually make true: the first pass (item 2, replacing the file's
content) surfaced every remaining reader the hard way, via a full `pytest` run gone red — five
tests, four more test files beyond the ones named, and one production module
(`src/build_web_data.py`) all still read the old file directly. All were found and repointed in
the same step (section 4) before this sentence was allowed to stand.
