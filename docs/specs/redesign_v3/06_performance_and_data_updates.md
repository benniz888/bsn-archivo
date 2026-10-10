# Performance and data updates

## Performance (PHASE_71, after the redesign; plus cheap wins in PHASE_61)
The prompt you found is good; it assumes a server and a database. This site is static, so adapt it:

> You are a senior web performance engineer. This is a static site (GitHub Pages, hash router, service worker, JSON data in web/data). First inspect and report; change nothing. Establish a baseline you actually measure: Lighthouse mobile (throttled) against the live site and a local build; total transferred bytes per route; JS parse/execute time; largest images; number and size of JSON files fetched per route; service-worker precache size. Never invent a number; say what you measured and how. Rank bottlenecks by user impact, effort, confidence. Check: oversized/unoptimized images (WebP/AVIF, width/height, lazy loading), data files fetched whole when a slice would do, sequential fetches that can run in parallel, work repeated on every route change, long tables rendered all at once (paginate or window), render-blocking fonts (self-host Inter and Oswald, `font-display: swap`, preload the two used weights), unused CSS/JS, animation on layout properties (use transform/opacity only), cache headers vs service-worker behavior (the known `cache:'no-store'` finding in `web_structure_ios_path_spec_v2.md`). Give a short plan and ask approval before anything architectural or data-sensitive. Fix the smallest high-impact items first, in small batches, re-verifying accessibility, caching and data correctness after each. Finish by re-running the same baseline and reporting before/after, every file changed and why, expected user impact, trade-offs. No broad rewrite.

Changes from the original: removed database-index and API-call checks (no backend); added service-worker/cache semantics, self-hosted fonts, table windowing, and the Lighthouse mobile profile.

Do the optimization pass AFTER the redesign so you do not tune pages you are about to replace. Set up the image pipeline early (PHASE_61): all new images WebP/AVIF with explicit dimensions and lazy loading.

## How data gets updated
Current setup (from the project docs): the pipeline lives in the repo. `src/build_web_data.py` builds `web/data/*.json` from the cleaned data; `verify_clean.py` checks it (346k+ checks as of Sep 24); the service worker and `DATA.syncVersion()` pick up a new digest; Pages deploys on push to `main`. Hard rules: never write to `data/clean/` by hand, never run `make parse-players` without approval.

So "drop a file in a folder" is close but not the whole story, because data from the league arrives in different shapes. Recommended flow (PHASE_72):
1. Put the league's new files in `data/incoming/<yyyy-mm-dd>/` (new folder, never overwrites).
2. Run one command (proposed: `make update-data`) that: validates the schema (columns, types, duplicate keys), diffs against current data, prints a human summary ("12 new games, 3 changed scores"), STOPS on anything suspicious, and writes a report to `docs/data_updates/<date>.md`.
3. You read the summary. If good, the command rebuilds `web/data`, runs `verify_clean.py` and the tests.
4. Commit and push as usual; Pages deploys; the app syncs by digest.
Keep the `confidence`, `notes` and `source` columns visible in the UI (they cover the "unsupported claims" requirement).

Live in-season data (standings, box scores) is NOT part of this. The earlier decision stands: complement bsnpr.com, historical only. Live data would need a licensed feed plus a backend; revisit only if the league agrees to share data.
