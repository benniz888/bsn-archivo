# PHASE_1_SPLIT verification harness

Lives at `tests/harness/` — **never under `web/`** (nothing here is published to Pages) and
**never imported by pytest** (`.mjs`/`.json` files aren't test-collected; `inventory.py` is a
standalone script, not a test module). Reused at every step of the split so "before" is always a
real, committed artifact, not a re-run against a moving target.

## Contents

- `capture.mjs` — Playwright script. Captures, per route, normalized rendered DOM (outerHTML of
  the route's container, whitespace-collapsed, plus a sha256 hash for quick diffing), a computed-
  style sample (a fixed set of selectors x properties), an accessibility-tree snapshot, console
  errors and failed requests. Runs Chromium + WebKit, 1000px + 390px, for the 6 top-level tabs,
  `#archivo/calidad`, and 5 named player pages (721, 152, 578, 194, 344) — 12 routes x 4 configs =
  48 files per snapshot run. **Deterministic**: `addInitScript` seeds `Math.random()` (an LCG, not
  a constant, so code that calls it more than once per render still varies reproducibly) and pins
  `Date` to a fixed instant, both before any page script runs. Proven: two consecutive captures of
  the identical, unmodified code now produce identical hashes for all 48 files (see below).
- `inventory.py` — extracts every top-level `function`/`const`/`let`/`var` name declared at
  column 0 inside the app's main `<script>` block (name, line, kind). Run before and after a
  structural change; the **set of names** must be identical, only `line` (and, once split,
  `file`) may differ. Single-file form (`inventory(path)`) is unchanged since STEP 0, still what's
  used against the untouched `app/bsn_archivo.html`. STEP 3 added a multi-file form
  (`inventory_multi(paths)`, used when the CLI gets more than one source path, or a single
  non-`.html` one) that tags each declaration with which file it came from -- a plain `.js` file
  has no `<script>` tags to bound the scan, so the whole file counts as one script region. CLI:
  `python3 tests/harness/inventory.py <output.json> <path> [<path> ...]`.
- `baseline/*.json` — one file per `<route>__<engine>__<width>__<label>.json`.
  - `main_27c16a4_det` — **the baseline to compare against.** Deterministic capture (the fixed
    seed above), from `main` at `27c16a4` (`git archive`, no branch switch), before Playwright's
    `Math.random`/`Date` fix landed in `capture.mjs` was even possible to trust.
  - `main_27c16a4` (no `_det` suffix) — the **original, non-deterministic** STEP 0 capture. Kept
    only as evidence for a real finding: two back-to-back captures of unmodified `main@27c16a4`
    gave different `tab:juega` DOM (`app/bsn_archivo.html:6826`, a `Math.random()`-seeded preview
    board, unrelated to the split). **Do not use this label as a comparison baseline** — it isn't
    reproducible by construction.
- `inventory_main_HEAD.json` — the pre-split function/const inventory, from `app/bsn_archivo.html`
  alone (single-file form). Ground truth: this file never changes, since `app/bsn_archivo.html`
  doesn't.
- `inventory_web_split.json` — same 426 declarations, same names, tagged with `file` via the
  multi-file form. STEP 3: 408 `web/index.html` / 18 `web/js/data.js`. STEP 4: 385
  `web/index.html` / 18 `web/js/data.js` / 23 `web/js/helpers.js`. Regenerate after any later step
  moves more code: `python3 tests/harness/inventory.py tests/harness/inventory_web_split.json
  web/index.html web/js/data.js [<more files as they appear>]`.

## Running it

Needs Playwright's Node package; this repo has no `package.json` (Python-first project, PC7).
Point `NODE_PATH` at wherever Playwright is installed for this environment, e.g.:

```
NODE_PATH=/private/tmp/bsn_harness/node_modules node tests/harness/capture.mjs \
  http://localhost:8933 tests/harness/baseline --label=<some-label>
```

(serve `web/` first: `python3 -m http.server 8933 --directory web`). If no such install exists,
`npm install playwright && npx playwright install chromium webkit` anywhere and point `NODE_PATH`
there.

```
python3 tests/harness/inventory.py tests/harness/inventory_main_HEAD.json app/bsn_archivo.html
python3 tests/harness/inventory.py tests/harness/inventory_web_split.json web/index.html web/js/data.js web/js/helpers.js
```

## Comparing a new snapshot to the baseline

Load both labels' JSON files for the same route+engine+width and diff `domHash` first (cheap);
fall back to `domText` for a real diff when the hash differs. `styles` and `a11y` compare the same
way. `consoleErrors`/`failedRequests` must both be empty in every file, before and after.
