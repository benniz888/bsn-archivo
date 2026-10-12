# PHASE_66C inventory: "BSN Archivo" -> "El Archivo"

Searched (case-insensitive) `bsn archivo`, `bsnarchivo`, `archivo bsn`, plus `bsn-archivo` and `bsn_archivo` for identifiers. Excluded as history: docs/audits, docs/specs, docs/session.md entries, docs/research.
No README.md exists in the repo. No `apple-touch-startup-image` links exist. `document.title` is never set in JS; the single static `<title>` is the only page title.

## A. Brand name shown to users or machines: CHANGED (12 sites)
| # | file:line | old | new |
|---|---|---|---|
| 1 | web/index.html:8 | `<title>BSN Archivo · Baloncesto Superior Nacional, 1930–2026` | `El Archivo · Baloncesto Superior Nacional, 1930–2026` |
| 2 | web/index.html:10 | og:site_name `BSN Archivo` | `El Archivo` |
| 3 | web/index.html:11 | og:title `BSN Archivo · …` | `El Archivo · …` |
| 4 | web/index.html:15 | twitter:title `BSN Archivo · …` | `El Archivo · …` |
| 5 | web/index.html:48 | apple-mobile-web-app-title `BSN Archivo` | `El Archivo` |
| 6 | web/index.html:49 | application-name `BSN Archivo` | `El Archivo` |
| 7 | web/index.html:70 | splash wordmark `BSN ARCHIVO` | `EL ARCHIVO` |
| 8 | web/index.html:90 | header wordmark `BSN ARCHIVO` | `EL ARCHIVO` |
| 9 | web/index.html:472 | footer `BSN Archivo · construido por` | `El Archivo · construido por` |
| 10 | web/manifest.webmanifest:2-3 | name `BSN Archivo`, short_name `BSN` | `El Archivo`, `El Archivo` (short_name was the league acronym used as the app label) |
| 11 | web/js/games.js (Cuadrícula share text, drawBoard) | `BSN Archivo · La Cuadrícula #n` | `El Archivo · La Cuadrícula #n` |
| 12 | web/js/games.js:736 (Temporada share text) | `BSN Archivo · La Temporada Perfecta` | `El Archivo · La Temporada Perfecta` |
Tests updated: tests/test_site_notices.py:24, 47, 93.

## B. Technical identifiers: LEFT (not edited)
- Domain/URLs: `bsnarchivo.com` (web/index.html og:url, tests/test_site_notices.py:96, many docs), `benniz888.github.io/bsn-archivo`.
- Repo/dir name `bsn-archivo`; file names `app/bsn_archivo.html`, `bsn-archivo-<date>.json` download name (web/js/tabs.js:4782), User-Agent `bsn-archivo/0.1` (src/wayback_cdx.py:36).
- Cache names (`bsn-shell-v2`, `bsn-data`), storage keys (`bsn:*`), CSS classes (`markname`, `splashname`).
- Frozen test baselines under tests/harness/baseline/*.json (old DOM snapshots of main@27c16a4; they must stay as recorded).

## C. Ambiguous / not user-facing: LEFT, listed for the owner
- app/bsn_archivo.html:3 `<title>BSN Archivo — archived pointer</title>`: archived pointer page, not the app; English text.
- web/sw.js:1 and web/css/main.css:2: code comments naming the project (`BSN Archivo — service worker`, `BSN ARCHIVO — design system`).
- docs/project.md:1 and :6 (`NAME: BSN Archivo`): Tier 2 instruction file; changing governance files is the owner's call.
- docs/research/*.md, docs/strings_pending_phase61.md:13, docs/specs/redesign_v3/*: historical text. 01_master_plan.md:49 and 02_brand_and_logo_spec.md:28 still say the wordmark is "BSN ARCHIVO"; superseded by this phase.
- Uses of "BSN" for the league (Baloncesto Superior Nacional) everywhere else: untouched.
