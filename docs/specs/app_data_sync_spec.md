# Spec: App Data Sync

## [PURPOSE]

The current app (`app/bsn_archivo.html`) is a single self-contained file with data
baked in as JS constants. That architecture was right at 45 players. It cannot
survive the current dataset: 3,303 players, ~25k aliases, 1,287 games, 39,669
box-score rows, 233,664 play-by-play events — and growing (jug05 fetch,
historic follow-up, and PBP linking are all still queued). PC7
(single-file, no build step) was flagged as unsustainable at this scale but
never formally superseded. This spec supersedes it and unblocks
`PHASE_5_APP_SYNC`.

Concretely, this decides: how does data get from `data/clean/*.csv` (and the
identity spine, and PBP) into something the app can load, without the app
loading all of it on every visit.

## [DECISION]

**Static JSON, generated at build time, fetched at runtime. No backend, no
database server.**

1. A new `make build-web-data` target reads `data/clean/*` (champions,
   franchises, career leaders, scoring champions, box scores, PBP, identity
   spine) and emits a tree of small JSON files under `web/data/`:

   ```
   web/data/
     manifest.json                 # build timestamp, row counts, data version
     index/
       players.json                # lightweight: id, name, years, position, club — full 3,303, used for search
       seasons.json                # season -> champion, runner-up, confidence
       franchises.json             # the 28 franchises, static, ships in full
     players/
       <bsnpr_id>.json             # one player's full career: totals, per-season lines, honors
     seasons/
       <year>.json                 # season summary: standings if known, leaders, awards
     games/
       <season>/
         <game_id>.json             # box score for one game
         <game_id>_pbp.json         # play-by-play for one game, ONLY if actor_raw is linked
   ```

2. Hosting: GitHub Pages, served from the same repo (`bsn-archivo`) via a
   `gh-pages` branch or `/docs` build output. Zero server cost, zero new infra
   to learn, matches the existing "deploys free, installs as PWA" decision.

3. The app shell fetches JSON on demand (`fetch('data/players/273.json')`)
   instead of reading from embedded constants. A service worker caches
   fetched files for offline/PWA use — the storage-wrapper pattern
   (silent fallback, never throws) already used for `localStorage` extends
   naturally to caching fetched JSON.

4. Rebuild cadence: data changes happen in batch ingest sessions, not live.
   `make build-web-data` reruns and the JSON tree is committed + redeployed
   after each session. No real-time sync problem exists because there is no
   live write path.

## [RATIONALE]

- **Matches actual usage pattern.** "Show me one player's career" should cost
  one small fetch, not a 3,303-player load. Chunking by entity (player, game,
  season) is the direct fix for the problem PC7 named.
- **Matches your skill set and constraints.** No server to provision, patch,
  or pay for. You're a SQL/Excel/Power BI analyst who's one week into
  git/terminal — a static-file pipeline is a `make` target you already know
  how to run, not a service you have to keep alive.
- **Matches the app-direction decision already made.** Web + PWA + free
  hosting was chosen specifically because it "deploys free... produces a
  *link* that can be sent to the Federación or players." A database server
  would reintroduce hosting cost and ops burden that decision was made to
  avoid.
- **Reinforces the `game_plays` storage fix.** The pipeline table is already
  gzipped (65 MB → 2.7 MB, `docs/specs/clean_data_storage_spec.md`); splitting
  PBP per-game for the *web* artifact means the app also never loads events
  for games nobody is viewing.
- **Boring and proven (C4).** Static-JSON-plus-client-fetch is how every
  Basketball-Reference-style static archive actually works. No novel
  infrastructure risk.

## [ALTERNATIVES_REJECTED]

- **Keep codegen / embed everything in one file.** Rejected — this is the
  status quo PC7 already flagged as broken at this scale. Every player load
  would ship the whole archive.
- **Client-side SQLite (sql.js/wasm), one DB file, real SQL queries in the
  browser.** Appealing (real joins, one file, no per-entity chunking to
  design) but wrong for this project's shape: a single unified DB file grows
  with every ingest phase and reintroduces the "download the whole archive to
  see one player" problem, plus adds a wasm SQL engine as a dependency where
  a plain `fetch()` already does the job. Worth revisiting only if the
  per-entity JSON approach turns out to need real cross-entity queries the
  client can't do cheaply (e.g., "every game a player scored 30+ in").
- **Real backend + database (Node/Python API + Postgres/SQLite server).**
  Rejected for now. Nothing in this app needs live writes, user accounts, or
  real-time data — it's a static archive rebuilt in batches. A backend adds
  hosting cost, an attack surface, and an ops burden with no corresponding
  benefit yet. Revisit only if/when there's a genuine live-write feature
  (user submissions, comments, live-season score updates via a real API).

## [INTERFACES]

- **Build contract:** `make build-web-data` — deterministic (same input CSVs
  + identity spine → byte-identical JSON output, so reruns produce clean git
  diffs, not full-tree rewrites every time).
- **Fetch contract:** app JS fetches by id/season/game key, matching the
  `bsnpr_id` / season / `game_id` keys already established in the pipeline.
  A failed or missing fetch renders the existing "N of 15 categories were
  never recorded" style gap message — never a silent zero, consistent with
  the NULL ≠ 0 rule already in force.
- **Naming:** all new dirs/files `snake_case` (C1), consistent with the rest
  of the repo.
- **PBP gating:** a game's `_pbp.json` is only generated once `actor_raw` has
  been matched to `bsnpr_id` for that game (ties to the still-open PBP
  linking task). Until then, that game simply has no PBP file — not a
  half-linked one — same "show gaps, don't fabricate" rule already governing
  the rest of the archive.

## [DEPLOY]

Resolved 2026-09-09 (PHASE_5 5G). `web/` is the GitHub Pages site root.
GitHub's "deploy from a branch" only offers `/` or `/docs` (no arbitrary
folder), and `/docs` already holds this framework's Tier-1/2/3 files — so
`web/` is published by a **GitHub Actions workflow**
(`.github/workflows/pages.yml`, the standard `upload-pages-artifact` +
`deploy-pages` template). No `gh-pages` branch; the workflow is fire-and-forget.

```
web/
  index.html   committed byte-copy of app/bsn_archivo.html (`make site`)
  .nojekyll     stops Jekyll from touching data/
  sw.js         service worker (5E)
  data/         make build-web-data output (committed)
```

- `app/bsn_archivo.html` stays the source of truth; `web/index.html` is a
  build artifact like `web/data/`. `make verify` fails if the copy drifts
  (`verify_web_data` byte-compares them). Git stores one shared blob while
  they're identical.
- The shell is base-path-agnostic (`DATA.base = new URL('data/',
  location.href)`, `register('sw.js')`, inline data-URI manifest/icons, zero
  absolute `/…` paths), so it runs unchanged under the project-pages prefix
  `/<repo>/`. SW scope becomes `/<repo>/`.
- **Image assets** (5G-A). Crests and portraits render as SVG; a real file is
  an optional override. Drop `web/img/crest/<app-key>.png` (or `.svg`/`.jpg`/
  `.webp`) or `web/img/player/<name-slug>.jpg` and run `make build-web-data` —
  it scans `web/img/` into `manifest.json`'s `assets` map, and the app emits an
  `<img>` **only** for a listed base (one request, no extension probing, no
  404s for the ones you don't have). No `web/img/` files → `assets: {}` → pure
  SVG.

**One manual action (owner):** repo **Settings → Pages → Build and deployment
→ Source: "GitHub Actions" → Save.** The next push runs the workflow (visible
in the Actions tab, ~1 min). Custom domain, if ever wanted, goes in the same
Pages settings and needs a `web/CNAME` file.

**Redeploy after an ingest session:**
```
make parse-players ...        # whatever changed
make build-web-data           # new source_digest in web/data/manifest.json
make site                     # only if the shell changed
make verify && make test
git add web app docs && git commit && git push
```
The push triggers `pages.yml` only if `web/` changed (a docs-only commit
doesn't redeploy).
On the next visit `DATA.syncVersion()` sees the new digest, clears the
`localStorage` cache and posts `purge-data` to the service worker, which drops
`bsn-data`; fresh JSON loads. No cache-busting query strings needed.

## [OPEN_QUESTIONS]

These have defaults proposed below so they don't block starting the build
target, but they're flagged because they're genuinely your call:

1. **GitHub Pages vs Cloudflare Pages.** Default: GitHub Pages — repo's
   already there, zero new accounts. Revisit only if load times or traffic
   become a real problem (unlikely at this data size).
2. **Ship PBP in the MVP at all?** 233,664 events is a lot even chunked, and
   linking is still incomplete. Default: box scores ship in full; PBP tab is
   gated per-game behind the linking pass, shown as a "beta"/incomplete
   section rather than withheld from the UI entirely.
3. **Static per-player pages for shareability/SEO** (useful for bennizpr —
   a shareable player-page link) vs pure client-side fetch with no
   pre-rendered HTML. Default: defer — not needed for a personal-use MVP,
   revisit once you want to send specific player links to people.
4. **Search depth.** The 3,303-entry lightweight player index is small enough
   to load in full and search client-side by substring; the 25k-alias table
   is small enough to fold into that same index. Default: ship it that way,
   no server-side search needed at this scale.
