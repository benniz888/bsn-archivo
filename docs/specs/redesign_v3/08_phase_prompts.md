# Phase prompts (paste one per sitting, `/clear` between)

## Shared header (already in every prompt below; included once here for reference)
```
HARD LIMITS: no deletion outside /tmp without asking, never make parse-players, no writes to data/clean/, no force-push, no git reset/clean/rebase. Build phases: do NOT commit, do NOT push. Stage nothing.
RULES: read docs/specs/redesign_v3/01_master_plan.md first. Never fabricate data. New or changed public Spanish strings go to docs/strings_pending_<phase>.md (proposed text), not into the UI as final. Contrast >= 4.5:1 text / 3:1 graphics, tap targets >= 44px, visible focus, prefers-reduced-motion respected, no emoji in UI. Verify in Chromium AND WebKit at 390px and 1000px; one phone + one desktop screenshot per page. Run the test suite (baseline 676 passed, 1 xfailed, 1 known failure tests/test_web_text.py).
REPORT (<= 12 lines): PHASE / DONE / VERIFIED / NEXT + git diff --stat + git status --short. Then STOP and wait for my approval.
Screens for reference are in ~/Desktop/newredesign/ (Inicio, Historia, Jugadores, Equipos, Juega, Archivo, Logo Options).
```

## PHASE_60_AUDIT (read-only, Sonnet low)
```
PHASE_60_AUDIT. READ-ONLY: change no repo files; write outputs only under /tmp and in docs/audits/phase60_*.md (new files).
1. Confirm you are on branch redesign-v3 (created from an up-to-date main; if not, STOP and tell me). Report HEAD and whether the latest "Deploy Pages" run on main is green (query the GitHub API directly).
2. Baseline: Lighthouse mobile (throttled) on the live site for #inicio, #historia, #jugadores, #equipos, #juega, #archivo; bytes transferred per route; size of web/js/*.js, web/css/main.css, web/data/*; image inventory with sizes. State exactly what you measured and how. Invent nothing.
3. Third-party requests and embeds (hosts contacted at load), localStorage keys, service-worker cache contents.
4. docs/image_rights.csv: every file under web/img/ (file, subject, apparent source, license/status). Flag, do not delete.
5. Claims audit: grep for testimonials/ratings/superlatives/"oficial"/"verificado"/100%; list with proposed neutral rewording.
6. Find: (a) the Inicio content referencing Piculin's death; (b) every emoji codepoint in web/; (c) the mobile tab-indicator code and why it stays on Inicio; (d) the sticky-header scroll offset; (e) every control under 44px (the backlog list).
7. For La Cuadricula: list the criterion functions and the name-normalization code; do NOT fix yet.
8. Existing tests and inventory rules I must respect when adding functions (read docs/session.md).
Write one summary file docs/audits/phase60_summary.md. Report in the standard format.
```

## PHASE_61_SHELL (Sonnet low)
```
PHASE_61_SHELL. Read 02_brand_and_logo_spec.md and the "Inicio header" part of 05_page_specs.md. Use the generated icons in docs/specs/redesign_v3/assets/logo/ (copy into web/img/ and web/ as needed).
Do: replace the brand mark (desktop: mark + "BSN ARCHIVO" wordmark top-left; phone: mark only, accessible name kept); favicon set, apple-touch-icon, manifest icons incl. maskable, theme-color; update the service-worker precache list and bump the cache version; move the search field into the header (desktop full, phone icon that expands); reserve an "Iniciar sesion" slot (hidden until accounts are approved); fix the phone tab indicator + active tab so they follow the route on load/back/forward; scroll-padding for the sticky header; subnav pill edge fade + active pill scrolled into view; selected/active outline uses site blue not orange; new images WebP/AVIF with width/height and lazy loading where applicable. Light theme: 1px outline on the logo tile.
Do not touch page content beyond this. Strings to docs/strings_pending_phase61.md. Report, then stop.
```

## PHASE_62_CUADRICULA_FIX (Sonnet MEDIUM)
```
PHASE_62_CUADRICULA_FIX. Correctness bug: valid answers are rejected. Follow "La Cuadricula" in 05_page_specs.md. First write tests/test_cuadricula_exhaustive.py that, for every cell of every puzzle the generator can produce (daily and practice), enumerates all players satisfying both criteria from the data and asserts the game accepts each under every accepted spelling variant. Run it, show me the failing categories with counts and 5 examples each, THEN fix the root cause(s). Add the honest rejection reason text (strings to docs/strings_pending_phase62.md). No visual redesign in this phase. Report with the before/after failure counts, then stop.
```

## PHASE_63_TABLES
```
PHASE_63_TABLES. Implement the "Shared data table" section of 05_page_specs.md as one component and apply it to Historia, Jugadores and Archivo tables first (club pages and final-series tables next phase). Keep CSV/copy buttons, sorting (aria-sort), filters. Before building, list the per-table phone column decisions for my approval in the report of a short plan step: write the plan to docs/audits/phase63_plan.md and STOP; build only after I reply "approved".
```

## PHASE_64_INICIO / 65 / 66 / 67A-D / 68 (same pattern)
```
PHASE_<NN>_<NAME>. Read the matching section of docs/specs/redesign_v3/05_page_specs.md and 01_master_plan.md. Step 1: write the keep/cut/change list and the proposed layout (desktop + phone) to docs/audits/phase<NN>_plan.md and STOP for my approval. Step 2 (after "approved"): build, verify, report.
```
Specifics to remember per phase:
- 64 Inicio: the Piculin item is removed only from Inicio (list exactly what).
- 65 Historia + Jugadores: add the emoji test guard; fix the circle-over-label bug with a visual test.
- 66 Equipos: club lore only from existing TEAM_LORE or sourced research (source for every line, my approval per string); jerseys are generic SVG, colors marked "aproximados".
- 67B Temporada Perfecta: run the seeded Monte Carlo first and show me the distribution before changing the curve. Use Sonnet medium.
- 67C Quien Soy: show me 10 sample clue ladders for 10 players for approval before wiring them in. Use Sonnet medium.
- 67D Sube y Baja: restyle only.

## PHASE_69_LEGAL (Haiku drafts + Sonnet wiring)
```
PHASE_69_LEGAL. Read 04_legal_privacy_spec.md. Use the chores agent to draft docs/legal_drafts/{privacidad,terminos,cookies,accesibilidad,creditos,aviso_legal}.md in Spanish from REAL inventories (storage keys, hosts, sources) found in PHASE_60. Leave clearly marked placeholders for details only I can provide (legal name, mailing address). Do not publish them. Build the routes and footer links only after I approve the text. Self-host Inter and Oswald in this phase (then update the privacy line).
```

## PHASE_70_ACCOUNTS (GATED: provider approved + PHASE_69 pages live; no giveaway or marketing features)
Do not start until you have approved the provider in `03_accounts_spec.md` and PHASE_69 pages exist. Before building, run: "Use the planner agent to review 03_accounts_spec.md against the repo for gaps; report only." Then build in the order listed in the spec. A lawyer reads Privacy, Terms and giveaway rules before the sign-in button goes live.

## PHASE_71_PERF_A11Y
Use the adapted prompt in `06_performance_and_data_updates.md`.

## PHASE_72_DATA_UPDATE
```
PHASE_72_DATA_UPDATE. Propose, then (after approval) build the flow in 06_performance_and_data_updates.md: data/incoming/<date>/, one command that validates, diffs, prints a human summary and stops on anything suspicious, writes docs/data_updates/<date>.md. Never write to data/clean/ outside the existing pipeline. Add tests.
```

## PUSH step (only when I say so; pushes redesign-v3 only, never main)
```
PUSH ONLY. Push the current branch redesign-v3 to origin (no force). Do not touch main. Confirm the branch name before pushing and report the result.
```
The live site changes only when redesign-v3 is merged into main through a pull request in the GitHub web page, which you do yourself at the end.

## COMMIT step (after you approve a phase)
```
COMMIT ONLY. Do NOT push. git status --short must match exactly: <paste the list from the report>; stop if any other path appears. Stage by explicit path only (never git add -A or .). Verify git diff --cached --stat. Commit message: imperative subject <= 72 chars. Trailers: Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com> and the Claude-Session line. Report the hash, staged files, whether the pre-commit hook changed web/index.html (should only refresh ?v= hashes), and confirm nothing was pushed.
```
