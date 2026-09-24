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
  48 files per snapshot run.
- `inventory.py` — extracts every top-level `function`/`const`/`let`/`var` name declared at
  column 0 inside the app's main `<script>` block (name, line, kind). Run before and after a
  structural change; the **set of names** must be identical, only `line` (and eventually `file`)
  may differ.
- `baseline/*.json` — one file per `<route>__<engine>__<width>__<label>.json`. The `main_27c16a4`
  label is the pre-split baseline, captured from `main` at that exact commit.
- `inventory_main_HEAD.json` — the pre-split function/const inventory.

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
python3 tests/harness/inventory.py app/bsn_archivo.html tests/harness/inventory_main_HEAD.json
```

## Comparing a new snapshot to the baseline

Load both labels' JSON files for the same route+engine+width and diff `domHash` first (cheap);
fall back to `domText` for a real diff when the hash differs. `styles` and `a11y` compare the same
way. `consoleErrors`/`failedRequests` must both be empty in every file, before and after.
