# PHASE_71 STEP 1 — Performance and accessibility audit

Branch `redesign-v3` at 1b731cf (clean tree). Date 2026-10-12. Read-only audit: no file under `web/`, `tests/` or any existing doc was changed; this is the only file created.

## 0. Method and caveats

- Served `web/` on 127.0.0.1:8123 with a small Node static server (gzip on text, `Cache-Control: max-age=600`, 404 for missing paths) to approximate GitHub Pages. Python's `http.server` does not compress, so it was not used. Real GitHub Pages headers were **not** measured (unverified); nothing here was run against bsnarchivo.com.
- Lighthouse (npm `lighthouse`, Chromium 1194 from Playwright, headless) once per route and mode, fresh profile each run (cold cache). Mobile = Lighthouse default (simulated Slow 4G, 4x CPU). Desktop = desktop preset (10 Mbps, no CPU throttle). **One run per cell, no medians**: scores move a few points run to run (see P20).
- The app is one document with hash routes, so every route downloads the same shell (same bytes, 24–27 requests). Byte and request counts differ only by lazy per-entity JSON. Per-route differences in Performance are mostly noise plus the extra JSON; do not read them as route-specific costs.
- axe-core (npm) via Playwright, Chromium 1194 and WebKit (Playwright build), 390 and 1000px wide, light and dark (`colorScheme` emulation; the resolved `data-theme` matched in all 208 runs). 26 routes x 2 engines x 2 widths x 2 themes = 208 page loads, 0 load errors. Service worker blocked for these runs. axe waited for the splash to disappear plus 0.9 s.
- axe "incomplete" (needs manual review) items are not counted as violations: color-contrast (208 runs, mostly gradient or image backgrounds), label-content-name-mismatch (108) and aria-valid-attr-value (48) are listed in section 4.
- Route set used: Inicio; Historia (landing, la cinta, temporada 2025); Jugadores (landing, buscar, one player page José «Piculín» Ortiz, líderes, récords); Equipos (landing, Bayamón); Juega (hub, Cuadrícula, Temporada Perfecta, ¿Quién soy?, Sube y Baja); Archivo (landing, Preguntar, A la medida, Cobertura, Calidad); Perfil; #privacidad, #terminos, #accesibilidad, #creditos. Games were measured in their initial state only (nothing played). Comparar, Salón and other sub-views were not measured.
- Not verified: real screen readers, real devices, real GitHub Pages response headers and 404 page, field (CrUX) numbers, Safari offline.

## 1. Lighthouse scores

### 1.1 Mobile

| Route | Hash | Perf | A11y | BP | SEO | LCP s | CLS | TBT ms | KiB | Req |
|---|---|---|---|---|---|---|---|---|---|---|
| Inicio | #inicio | 65 | 96 | 100 | 100 | 2.12 | 0.83 | 398 | 569 | 24 |
| Historia | #historia | 65 | 100 | 100 | 100 | 2.26 | 0.83 | 392 | 569 | 24 |
| Historia/cinta | #historia/cinta | 65 | 100 | 100 | 100 | 2.26 | 0.83 | 399 | 569 | 24 |
| Historia/temporada 2025 | #historia/temporada/2025 | 65 | 100 | 100 | 100 | 2.26 | 0.83 | 377 | 569 | 25 |
| Jugadores | #jugadores | 66 | 96 | 100 | 100 | 2.26 | 0.83 | 372 | 569 | 24 |
| Jugadores/buscar | #jugadores/buscar | 64 | 97 | 100 | 100 | 2.41 | 0.83 | 405 | 569 | 25 |
| Jugadores/jugador | #jugadores/jugador/jose-piculin-ortiz | 62 | 98 | 100 | 100 | 2.56 | 0.83 | 434 | 569 | 27 |
| Jugadores/lideres | #jugadores/lideres | 65 | 96 | 100 | 100 | 2.26 | 0.83 | 395 | 569 | 25 |
| Jugadores/records | #jugadores/records | 64 | 96 | 100 | 100 | 2.26 | 0.83 | 405 | 569 | 24 |
| Equipos | #equipos | 64 | 97 | 100 | 100 | 2.26 | 0.83 | 418 | 569 | 24 |
| Equipos/equipo bay | #equipos/equipo/bay | 64 | 99 | 100 | 100 | 2.26 | 0.83 | 436 | 569 | 25 |
| Juega | #juega | 66 | 96 | 100 | 100 | 2.26 | 0.83 | 368 | 569 | 24 |
| Juega/cuadricula | #juega/cuadricula | 65 | 97 | 100 | 100 | 2.26 | 0.83 | 402 | 569 | 24 |
| Juega/temporada | #juega/temporada | 63 | 96 | 100 | 100 | 2.56 | 0.83 | 383 | 569 | 24 |
| Juega/quiensoy | #juega/quiensoy | 59 | 100 | 100 | 100 | 3.38 | 0.89 | 362 | 569 | 24 |
| Juega/subeybaja | #juega/subeybaja | 58 | 96 | 100 | 100 | 3.39 | 0.83 | 386 | 569 | 24 |
| Archivo | #archivo | 56 | 96 | 100 | 100 | 3.38 | 0.83 | 469 | 569 | 24 |
| Archivo/preguntar | #archivo/preguntar | 57 | 97 | 100 | 100 | 3.46 | 0.83 | 411 | 569 | 24 |
| Archivo/constructor | #archivo/constructor | 63 | 97 | 100 | 100 | 2.26 | 0.83 | 450 | 569 | 24 |
| Archivo/cobertura | #archivo/cobertura | 57 | 97 | 100 | 100 | 3.39 | 0.83 | 415 | 569 | 24 |
| Archivo/calidad | #archivo/calidad | 62 | 99 | 100 | 100 | 2.41 | 1.12 | 451 | 569 | 25 |
| Perfil | #perfil | 65 | 91 | 100 | 100 | 2.26 | 0.83 | 392 | 569 | 24 |
| Privacidad | #privacidad | 58 | 96 | 100 | 100 | 3.37 | 0.83 | 412 | 569 | 24 |
| Terminos | #terminos | 58 | 96 | 100 | 100 | 3.38 | 0.83 | 386 | 569 | 24 |
| Accesibilidad | #accesibilidad | 59 | 100 | 100 | 100 | 3.38 | 0.83 | 365 | 569 | 24 |
| Creditos | #creditos | 59 | 97 | 100 | 100 | 3.38 | 0.83 | 373 | 569 | 24 |

### 1.2 Desktop

| Route | Hash | Perf | A11y | BP | SEO | LCP s | CLS | TBT ms | KiB | Req |
|---|---|---|---|---|---|---|---|---|---|---|
| Inicio | #inicio | 82 | 97 | 100 | 100 | 0.98 | 0.35 | 24 | 567 | 24 |
| Historia | #historia | 81 | 97 | 100 | 100 | 0.95 | 0.38 | 24 | 567 | 24 |
| Historia/cinta | #historia/cinta | 82 | 97 | 100 | 100 | 0.95 | 0.35 | 32 | 567 | 24 |
| Historia/temporada 2025 | #historia/temporada/2025 | 82 | 100 | 100 | 100 | 0.95 | 0.35 | 25 | 567 | 25 |
| Jugadores | #jugadores | 81 | 97 | 100 | 100 | 0.95 | 0.37 | 22 | 567 | 24 |
| Jugadores/buscar | #jugadores/buscar | 82 | 97 | 100 | 100 | 0.96 | 0.35 | 21 | 567 | 25 |
| Jugadores/jugador | #jugadores/jugador/jose-piculin-ortiz | 82 | 99 | 100 | 100 | 0.96 | 0.35 | 21 | 567 | 27 |
| Jugadores/lideres | #jugadores/lideres | 82 | 97 | 100 | 100 | 0.98 | 0.35 | 22 | 567 | 25 |
| Jugadores/records | #jugadores/records | 82 | 97 | 100 | 100 | 0.96 | 0.35 | 23 | 567 | 24 |
| Equipos | #equipos | 82 | 97 | 100 | 100 | 0.96 | 0.35 | 22 | 567 | 24 |
| Equipos/equipo bay | #equipos/equipo/bay | 82 | 96 | 100 | 100 | 0.95 | 0.35 | 22 | 567 | 25 |
| Juega | #juega | 81 | 100 | 100 | 100 | 0.97 | 0.37 | 21 | 567 | 24 |
| Juega/cuadricula | #juega/cuadricula | 82 | 100 | 100 | 100 | 0.96 | 0.35 | 23 | 567 | 24 |
| Juega/temporada | #juega/temporada | 82 | 97 | 100 | 100 | 0.95 | 0.35 | 22 | 567 | 24 |
| Juega/quiensoy | #juega/quiensoy | 79 | 100 | 100 | 100 | 0.98 | 0.43 | 65 | 567 | 24 |
| Juega/subeybaja | #juega/subeybaja | 78 | 97 | 100 | 100 | 0.95 | 0.48 | 24 | 567 | 24 |
| Archivo | #archivo | 82 | 97 | 100 | 100 | 0.96 | 0.35 | 24 | 567 | 24 |
| Archivo/preguntar | #archivo/preguntar | 78 | 97 | 100 | 100 | 0.95 | 0.49 | 22 | 567 | 24 |
| Archivo/constructor | #archivo/constructor | 82 | 97 | 100 | 100 | 0.96 | 0.35 | 22 | 567 | 24 |
| Archivo/cobertura | #archivo/cobertura | 82 | 97 | 100 | 100 | 0.96 | 0.35 | 24 | 567 | 24 |
| Archivo/calidad | #archivo/calidad | 76 | 99 | 100 | 100 | 0.96 | 0.71 | 22 | 567 | 25 |
| Perfil | #perfil | 82 | 91 | 100 | 100 | 0.96 | 0.35 | 22 | 567 | 24 |
| Privacidad | #privacidad | 82 | 97 | 100 | 100 | 0.96 | 0.35 | 21 | 567 | 24 |
| Terminos | #terminos | 82 | 97 | 100 | 100 | 0.95 | 0.35 | 24 | 567 | 24 |
| Accesibilidad | #accesibilidad | 82 | 97 | 100 | 100 | 0.95 | 0.35 | 21 | 567 | 24 |
| Creditos | #creditos | 82 | 97 | 100 | 100 | 0.96 | 0.35 | 22 | 567 | 24 |

Transfer is compressed bytes over the wire (Lighthouse `total-byte-weight`) with gzip from my server. The wire total is about 569 KiB (mobile) / 567 KiB (desktop) for every route; the largest items are in section 5.

Reading the table:
- Best Practices 100 and SEO 100 everywhere. Lighthouse's SEO score does not check `og:image`, canonical, robots or sitemap (see P01, P14).
- Mobile Performance 56–66 (the lowest, 56–59, on Archivo, Preguntar, Cobertura, ¿Quién soy?, Sube y Baja and the legal pages). TBT 360–470 ms, simulated LCP 2.1–3.5 s, simulated TTI about 5 s.
- Observed (unthrottled trace) LCP was 95 ms: the splash is the LCP element. The simulated 2.1–3.5 s is Lighthouse's model of the same page on a slow phone.
- CLS 0.83 mobile and 0.35 desktop on nearly every route (1.12 / 0.71 on Archivo/calidad). All of it occurs in the first ~300 ms **while the splash overlay covers the page** (P03).
- Lighthouse Accessibility between 91 and 100 and it flips between runs of identical markup (P20). The persistent real finding is Perfil at 91.

## 2. axe-core results

Violation instances (rule x page-run, all 208 runs): **critical 8, serious 140, moderate 140, minor 0**.
De-duplicated (rule, route, selector) over engines/widths/themes: **critical 4, serious 40, moderate 31**.
Chromium and WebKit produced identical sets (same rules in every configuration pair).

| Rule | Impact | Runs (of 208) | Routes | Selectors (up to 4) |
|---|---|---|---|---|
| label-content-name-mismatch | serious | 108 | 26 | `button[onclick="openGame('cuadricula')"]`<br>`button[onclick="openGame('temporada')"]`<br>`button[onclick="openGame('quiensoy')"]`<br>`button[onclick="openGame('subeybaja')"]` |
| region | moderate | 104 | 26 | `#bottombar` |
| heading-order | moderate | 32 | 4 | `#playerInfo > h3`<br>`.eq-tlw > .sub`<br>`.sub:nth-child(2)`<br>`h3:nth-child(2)` |
| color-contrast | serious | 24 | 6 | `button[data-y="1953"]`<br>`.rp-stats > .ed-eye`<br>`button[onclick="setGMode('practice')"]`<br>`#draftGame > div:nth-child(2) > .card:nth-child(1) > div:nth-child(1)` |
| aria-allowed-attr | critical | 8 | 1 | `button[onclick="setTheme('auto')"]`<br>`button[onclick="setTheme('light')"]`<br>`button[onclick="setTheme('dark')"]`<br>`div[aria-label="¿Qué es el BSN?"] > button[onclick="showPrimer()"]` |
| scrollable-region-focusable | serious | 8 | 1 | `.legal.panel > div:nth-child(7)` |
| landmark-unique | moderate | 4 | 1 | `.tall.tblwrap[role="region"]` |

Violations per configuration (sum over 26 routes):

| Config | Violations |
|---|---|
| chromium 390px light | 40 |
| chromium 390px dark | 34 |
| chromium 1000px light | 38 |
| chromium 1000px dark | 32 |
| webkit 390px light | 40 |
| webkit 390px dark | 34 |
| webkit 1000px light | 38 |
| webkit 1000px dark | 32 |

Per-rule detail (all with the same results in Chromium and WebKit):

- **aria-allowed-attr (critical)**: Perfil only, all 8 configs. `aria-selected="true"` on the theme buttons `setTheme('auto'|'light'|'dark')` and on `showPrimer()` ("¿Qué es el BSN?"). `aria-selected` is not valid on a plain button.
- **color-contrast (serious)**: light theme only (dark clean). `--ink-3` #5A6C8E on #E1E9F5 = **4.32:1** (needs 4.5): Historia/cinta and temporada (`button[data-y="1953"]`), player page `.rp-stats > .ed-eye`, Cuadrícula `setGMode('practice')`, Perfil `setTheme('light'|'dark')` and `showPrimer()`. Temporada Perfecta `#draftGame ... .card > div`: #E8B23A on #FFFFFF = **1.93:1** at 11px bold (a team-colour label on a white card; team-colour text on light surface).
- **label-content-name-mismatch (serious)**: `header .mark` on all 26 routes (aria-label "Ir a Inicio" does not contain the visible "EL ARCHIVO"), and the four game-shelf tiles `openGame(...)` on the Juega hub. WCAG 2.5.3 Label in Name; breaks voice-control users saying the visible words.
- **scrollable-region-focusable (serious)**: #privacidad, `.legal.panel > div:nth-child(7)`, a horizontally scrollable block with nothing focusable inside.
- **heading-order (moderate)**: player page `#playerInfo > h3`; team page `.eq-tlw > .sub`; Calidad `.sub`; Perfil `h3` (jumps from h1 to h3/h4).
- **region (moderate)**: `#bottombar` is outside any landmark; only at 390px (all 26 routes, both engines).
- **landmark-unique (moderate)**: Archivo/calidad, a `.tblwrap[role="region"]` with no accessible name (390px only).

axe "incomplete" (manual review needed, not counted above): color-contrast on every route (Inicio: `#clubPillName`, `.hero > .ed-eye`, `.hero-headline` — gradient/image backgrounds axe cannot resolve), aria-valid-attr-value on Inicio (1), label-content-name-mismatch (108). **Unverified**: the Inicio hero text contrast over its background.

Lighthouse also reported splash color-contrast failures (#111622 on #070C18, 1.08:1) on 37 of 52 runs. The values are mid-fade colours captured while the splash animates in; axe, run after the splash has gone, never sees them. Treated as a lab artifact, not a finding. **Unverified** whether any frame of the splash text is actually below contrast for a user.

## 3. Manual checks

| Check | Result |
|---|---|
| Keyboard, Inicio (390 and 1000, 90 Tab presses) | No focus trap, no focus on hidden elements, every focused element had a visible outline or ring. Order follows the page. 90 presses did not reach the end of the page (long page). First stop after load is "Leer qué es el BSN" because focus starts at `main` after the load; the skip link is only first on a cold Tab from the document start (not re-tested separately; the PHASE_69 report verified it). Two consecutive stops with the same label ("BAY Vaqueros de Bayamón — camp…" in `.champ-strip`) — may be two different seasons, **unverified**. |
| Keyboard, one game (Cuadrícula, 1000) | 70 presses, no trap, no hidden stops, visible focus on all. Starts in the rail (theme, club, section links), then game controls. Board cells were not played. |
| Keyboard, Perfil (1000) | 80 presses, no trap, visible focus. Starts at the name input, then the club tiles. |
| Escape / dialog focus return | Verified in PHASE_69 for the delete-data dialog; not re-run here. |
| Document title per route | **Identical on all 26 routes**: "El Archivo · Baloncesto Superior Nacional, 1930–2026" (including the player page, a team page and the legal pages). P02. |
| `<html lang>` | `es` on all routes. OK. |
| One h1 per view | Exactly 1 visible h1 on every route. But the section pages share one h1 across all their sub-views (Historia/Jugadores/Equipos/Juega all say the section name even on "La Cuadrícula", Perfil of a team, etc.); only Inicio, the player page, and the legal pages have a specific h1. |
| Landmarks | `header`, `main#main`, `footer` and the legal `nav` ("Información legal") present on all routes. The rail (`nav` "Secciones") is hidden at 390px; the bottom bar at 390px is not a landmark (axe `region`). |
| Images / SVG | 1 visible `img` per route (header mark, `alt=""`, decorative, accompanied by text). No `img` without `alt`. SVG: 15–75 per view; the only unlabelled, non-hidden ones are 5 on Inicio/Historia/Jugadores landings (class names not captured; **unverified** whether they are decorative). |
| Form labels | No unlabelled visible input, select or textarea on any route (aria-label, label or title present). |
| `color-scheme` | No `<meta name="color-scheme">` and CSS `color-scheme` computes to `normal`. Native scrollbars, form controls and overscroll can stay light under the dark theme (P18). Visual effect **unverified**. `theme-color` meta is updated per theme by the head script. |
| Reduced motion | With `prefers-reduced-motion: reduce`: 0 running animations or transitions at 0.3 s and at 3.3 s. Without it: splash ball bounce and shadow animate. CSS has a global reduce rule (main.css:333) plus per-component rules; JS smooth scroll is gated (helpers.js:142, tabs.js:1161, 1194). **Pass.** |
| Offline after first load (Chromium, SW active) | Shell cache `bsn-shell-v3` 19 entries, `bsn-data` 1 then 3 after visiting a player and the cinta. Offline reload of #inicio renders (title, h1, 2.4k chars of text). Previously visited player page and cinta render offline. A **never-visited** player deep link offline shows the Jugadores landing with no message (P16). Equipos/Bayamón renders. WebKit offline **not tested** (Playwright WebKit cannot reload offline). |
| Service worker update path | Tested on a copy of `web/` (port 8124), not on the repo. Editing `SHELL` to `bsn-shell-v4` and calling `registration.update()`: new worker installed and activated, `bsn-shell-v3` deleted, `bsn-shell-v4` populated, data cache kept; a changed `<title>` in index.html appeared after reload. **The cache-name bump works.** `skipWaiting` + `clients.claim` take over immediately (no "new version" prompt). A change to `js/helpers.js` with the same `?v=` hash did **not** reach the page on reload (served from the HTTP cache, `max-age=600` on my server, same as GitHub Pages' default 10 min): the `?v=` hash in index.html is the only thing that makes a code change reach users, and index.html itself can be HTTP-cached up to 10 min (P15). Data changes rely on `manifest.json` `source_digest` -> `purge-data`; not exercised here (unverified). |
| Manifest | Valid JSON, `name`/`short_name` "El Archivo", `display: standalone`, `start_url`/`scope` ".", icons 192 and 512 (any) and a 512 maskable, all three files exist at the declared size (PNG RGB). No `id`, no `lang`, no screenshots, `orientation: portrait` (locks landscape on tablets), `theme_color` fixed dark while the app has a light theme. Installability itself **not tested** in a browser (P17). |
| Icons | `favicon.ico` (16/32/48 inside), `favicon_16/32.png`, `apple_touch_icon_180.png` (180x180), all present. |
| Open Graph / Twitter | Present: og:type, og:site_name ("El Archivo"), og:title, og:description, og:url (`https://bsnarchivo.com/`), twitter:card=summary, twitter:title, twitter:description. **Missing: og:image, twitter:image, og:locale, canonical link.** No social-preview image file exists anywhere in `web/` (largest brand image is the 512 px icon), so there is no image to check for the new name. P01. |
| robots.txt / sitemap.xml / 404.html / CNAME | None of the four exists under `web/`. The Pages workflow uploads `web/` as is (the custom domain, if configured, lives in repo Settings; **unverified**). P14. |
| 404 on hash routes | A hash never reaches the server, so `/#anything` always returns the 200 shell; an unknown hash silently falls to Inicio (tabs.js applyHash, no "not found" state). A real path such as `/jugadores` returns GitHub Pages' default 404 (no custom `404.html`; **page not fetched**, unverified). |

## 4. Layout shift detail

`PerformanceObserver` in Chromium, no throttling: 390px total about 0.82 (0.281 + 0.078 + 0.462 + 0), 1000px about 0.49. Sources: `.hubpair` (Inicio, twice), `.wrap`, `.legalrow`, `.liga.hubmore`, `#bottombar`. Every shift happens between 160 and 300 ms, and in every entry the splash was still displayed. The user sees a stable splash, then the finished page. Lighthouse and Chrome's CLS metric still count these shifts; whether the field CLS (CrUX/real devices) is affected is **unverified**. The mid-page `hubpair` (806 px tall) and the footer `wrap` are rendered empty then filled by the boot script.

## 5. Payload

### 5.1 Ten biggest files in `web/`

| # | File | Bytes | gzip -6 | Loaded at startup? |
|---|---|---|---|---|
| 1 | data/index/players.json | 722,777 | 84,941 | **Yes, every route** (eager) |
| 2 | js/tabs.js | 493,507 | 165,493 | Yes (sync script) |
| 3 | css/main.css | 230,601 | 69,504 | Yes (render-blocking stylesheet) |
| 4 | img/brand/icon_512.png | 148,037 | 143,978 | Only as manifest/precache (SW install precaches it) |
| 5 | data/games/2008/BS20084006.json | 123,665 | 2,147 | No (on demand) |
| 6 | data/index/data_quality.json | 92,193 | 14,187 | No (Calidad view) |
| 7 | img/brand/icon_maskable_512.png | 87,735 | 82,777 | SW precache only |
| 8 | index.html | 82,915 | 28,096 | Yes |
| 9 | data/games/2008/BS20084004.json | 79,655 | 1,769 | No |
| 10 | js/data.js | 78,693 | 23,627 | Yes (sync script) |

Next: inter woff2 72,920 (already compressed, preloaded), oswald woff2 28,488. Whole tree: 4,799 files, about 29 MB (`data/` 28 MB; `data/players` 3,326 files, 13 MB; `data/games` 1,292 files, 13 MB). Game JSON compresses 60:1 (123 KB -> 2 KB); cause (pretty-printing or repeated keys) **not investigated**; it does not affect first load but makes the Pages artifact larger.

### 5.2 First-load requests (Inicio, mobile run, 24 requests)

Document 28 KB, main.css 70 KB, 7 JS files (tabs.js 166 KB, data.js 24 KB, games.js 18 KB, init.js 9 KB, player.js 8 KB, helpers.js 7 KB, data-quality.js 6 KB), 2 fonts (73 KB + 29 KB), logo, manifest, favicon_32, icon_192 (35 KB, fetched by the manifest scan), and these JSON files: manifest, franchises, scoring_titles, player_xwalk, player_redirects, **players.json (85 KB gz, 723 KB raw)**, mvp, seasons/2026. Per-player files (`data/players/<id>.json`) and everything else load lazily on navigation: a player page adds 2–3 requests (27 total).

### 5.3 JS cost

- Scripts are 7 classic sync `<script>` tags at the end of the body, no defer or module, all executed before the shell reveals.
- Lighthouse bootup, Inicio mobile (4x CPU): `init.js` 1,456 ms total (883 ms scripting), which includes everything it triggers: it builds the markup for every panel from `tabs.js` at boot. `tabs.js` parse/compile 48 ms (own scripting 15 ms). `data.js` was under Lighthouse's reporting threshold; **no separate figure** (unverified). Unattributable 324 ms, HTML 231 ms. Desktop: init.js 357 ms.
- Long tasks (mobile): 288 ms and 171 ms in init.js, plus six at 50–82 ms. Main-thread: script evaluation 1.05 s, style/layout 0.44 s.
- Unused JS 36 KiB (22% of tabs.js); unused CSS 60 KiB (89% of main.css at first paint).

## 6. Findings

Severity: high = fix before the PR goes live; med = fix in the build step if cheap; low = backlog. Effort S/M/L. "Changes visuals/behavior" = does the proposed fix risk altering either.

| ID | Sev | Finding and evidence | Proposed fix | Effort | Visuals / behavior risk |
|---|---|---|---|---|---|
| P01 | high | No social preview: no `og:image`/`twitter:image`, `twitter:card=summary`, no image file exists, no canonical, no `og:locale`. Any shared link shows a bare card, without the brand. | Design one 1200x630 PNG with the final name (owner approves art), add `og:image` (absolute URL), `og:image:alt`, `twitter:card=summary_large_image`, `<link rel=canonical href=https://bsnarchivo.com/>`, `og:locale es_PR`. | S (M if art needs design) | No UI change. New asset; PHASE_73 may own the art |
| P02 | high | Same `<title>` on all 26 routes; a screen-reader user, history list and tab strip cannot tell views apart (WCAG 2.4.2). | In `_showPanel`/`showView`/`showPlayer`/`showTeam` set `document.title` to "<View> · El Archivo" (player/team name for detail pages) and restore the default on Inicio. | S | Behavior only (title bar, history). Needs strings |
| P03 | med | CLS 0.83 mobile / 0.35 desktop on every route (Lighthouse) from `.hubpair`, `.wrap`, `#bottombar`, `.legalrow` populating at 160–300 ms, all under the splash. Likely invisible to users, but counts in lab and possibly field CLS (unverified). | Give those containers reserved min-heights or build them before the splash reveals; confirm with the same observer. | M | Low; must not move the first visible frame |
| P04 | med | Mobile Perf 56–66, TBT 360–470 ms, simulated TTI about 5 s. Cause: sync boot builds every panel (init.js 1.46 s throttled), 493 KB tabs.js executes up front. | Build non-visible panels lazily on first show (or on idle) and add `defer` to the scripts; split tabs.js by section. | L | Behavior risk: deep links, search index and games assume everything is built; needs the full test suite |
| P05 | med | `players.json` 723 KB raw (85 KB gz) is fetched and parsed on every route for search/slugs. | Keep it, but fetch after first paint, or ship a slimmer index (id, name, norm, years) and lazy-load the rest. Coordinates with the data work. | M | Behavior risk: deep links to players wait on the index |
| P06 | med | Light theme `--ink-3` #5A6C8E on #E1E9F5 = 4.32:1 on 7 elements; #E8B23A on white 1.93:1 (Temporada Perfecta cards). Breaks the project's 4.5:1 rule. | Darken light `--ink-3` by one step (about #55688A, to be computed); give the draft-card label a dark text colour or a team-colour chip with contrasting text. | S | Small visible change in light theme; owner approval of the new token value |
| P07 | med | `aria-selected` on non-tab buttons (Perfil theme buttons, "¿Qué es el BSN?"): axe critical. | Use `aria-pressed` for the 3 theme buttons (or role=radio in a radiogroup); drop it from the primer button. | S | AT-only; no visual change |
| P08 | med | Label in Name: `header .mark` aria-label "Ir a Inicio" vs visible "EL ARCHIVO 1930 — 2026"; game tiles likewise. 26 routes. | aria-label that starts with the visible text: "El Archivo, ir a Inicio"; tile labels containing the title. | S | AT-only. New strings |
| P09 | med | No `robots.txt`, `sitemap.xml`, `404.html`. Deep paths get GitHub's default 404; unknown hashes silently go to Inicio. | Add robots.txt (allow all + sitemap), a one-URL sitemap, a Spanish 404.html linking home. Do not list hash URLs. | S | None for existing pages |
| P10 | med | Update path: index.html and sw.js are served with `max-age=600`; after a deploy, users can run old HTML/JS up to 10 min; code only reaches users if the `?v=` hash changed (which needs `update_asset_hashes` before commit). `skipWaiting`+`claim` swap workers mid-session without a notice. | Keep the hash step as a verify gate (a test that fails when hashes are stale); optionally add a "Hay una versión nueva" prompt. Cache bump itself works (tested). | S (test) / M (prompt) | Prompt adds UI |
| P11 | low | `.legal.panel` block in #privacidad scrolls with no focusable content (axe serious). | `tabindex="0"` plus an accessible name on the scrolling block, or let it wrap. | S | Focus ring appears on that block |
| P12 | low | `#bottombar` not in a landmark (390px, 26 routes). Calidad `.tblwrap[role=region]` has no name. | Make the bottom bar a `nav` named like the rail ("Secciones"); name each table region or drop the role. | S | AT-only |
| P13 | low | Heading order skips on the player page (`#playerInfo h3`), team page (`.eq-tlw .sub`), Calidad, Perfil. | Restyle with classes rather than level jumps, or fix levels. | S | Risk of visual change if CSS targets `h3`/`h4` |
| P14 | low | Section pages reuse one h1 for all sub-views ("Juega" while on La Cuadrícula). | Make the sub-view name the h1 or add a visible/SR h2 per view; covered by P02's title naming. | M | Focus-to-h1 logic in `_showPanel` would change |
| P15 | low | No `color-scheme`: computed `normal`; native scrollbars/inputs may stay light in dark theme (visual effect unverified). | `:root[data-theme=dark]{color-scheme:dark}` and light likewise; add meta. | S | Visible: scrollbars, native controls, overscroll |
| P16 | low | Offline, a never-visited player/team/season shows the section landing with no message. | Show a "Sin conexión: esta página aún no se guardó" state when a data fetch fails offline. | M | New UI state |
| P17 | low | Manifest: no `id`, `lang`, screenshots; `orientation: portrait` locks tablets; fixed dark `theme_color`. | Add `id`, `lang: es`, drop orientation lock, optional screenshots. | S | Install behavior on tablets |
| P18 | low | First-load unused CSS 60 KiB (89%) and unused JS 36 KiB. | Split per-section CSS only after P04; not worth doing alone (no build step). | L | Risky with the no-build rule |
| P19 | low | Game JSON 60:1 compressible (123 KB -> 2 KB): pretty-printing or repetition inflates the 29 MB artifact. Cause unverified. | Data pipeline question (minified output). | S–M | None for UI; belongs to data phase |
| P20 | info | Lighthouse accessibility flips between 91–100 for identical pages (splash caught mid-fade; LH reports splash contrast 1.05–1.08:1 on 37 runs). Treat axe as the authority. Perfil stays 91 (aria-allowed-attr, heading-order). | If a CI Lighthouse gate is added, wait for the splash to be gone. | S | None |
| P21 | info | Duplicate-looking consecutive Tab stops on Inicio `.champ-strip` ("BAY Vaqueros de Bayamón — camp…" twice). | Check whether these are distinct seasons; if not, remove the duplicate. | S | Unverified |

Things that passed: Best Practices 100 and SEO 100 on all routes; no console or page errors on any route; one h1 per view; `lang=es`; form labels; no image without alt; focus visible on every stop tested; no keyboard traps; reduced motion honored; offline shell and visited pages; cache-name bump evicts the old cache; self-hosted fonts (0 third-party requests seen in Lighthouse); manifest icons exist at declared sizes.

## 7. Proposed fix scope for a build step (ranked)

1. P02 per-route titles (S, high value, low risk).
2. P01 social preview image + canonical + OG completeness (S, art needs owner).
3. P07 + P08 + P11 + P12: ARIA corrections and label-in-name (S, AT-only, no visual change). Clears every critical and most serious axe items.
4. P06 contrast tokens (S; owner approves the light `--ink-3` value and the draft-card label colour). Clears the remaining serious axe items.
5. P09 robots.txt, sitemap.xml, 404.html (S).
6. P10 hash-gate test for stale `?v=` + decision on an update prompt.
7. P15 color-scheme (S; check screenshots in both engines first).
8. P03 reserve heights to remove the layout shifts (M).
9. P13, P14 heading structure (S–M).

Out of scope for this build step because of risk: P04 (lazy panels / splitting tabs.js), P05 (lazy players index), P18 (CSS split).

## 8. Deferred

- To PHASE_72 (data): P05 index slimming if it changes data shape, P19 game JSON size, whether the `manifest.json` digest -> purge path reaches users (unverified), the content of `players.json` fields used at startup.
- To PHASE_73 (look): social-preview artwork (P01), light-theme token values (P06), `color-scheme` visuals (P15), any change to the splash, hero or landing layouts (P03), the offline state design (P16).
- Not done / not measured: real devices, VoiceOver/NVDA/TalkBack, Safari offline, installability test, the production GitHub Pages headers and 404 page, field Core Web Vitals, repeat-visit (warm cache) performance, Comparar/Salón/other sub-views, game play states.

## 9. New Spanish strings the fixes would need (text only, for owner approval)

- P02 page titles: "Historia · El Archivo", "Jugadores · El Archivo", "Equipos · El Archivo", "Juega · El Archivo", "Preguntar · El Archivo", "A la medida · El Archivo", "Cobertura y fuentes · El Archivo", "Calidad de datos · El Archivo" (the Archivo section is titled by view to avoid "Archivo · El Archivo"), "Perfil · El Archivo", "Política de privacidad · El Archivo", "Términos de uso · El Archivo", "Declaración de accesibilidad · El Archivo", "Créditos y fuentes · El Archivo", "<Nombre del jugador> · El Archivo", "<Nombre del equipo> · El Archivo", "La Cuadrícula · El Archivo", "La Temporada Perfecta · El Archivo", "¿Quién soy? · El Archivo", "Sube y Baja · El Archivo".
- P08 header mark label: "El Archivo, ir a Inicio". Game tile labels: "<Título del juego>: abrir" (e.g. "La Cuadrícula: abrir").
- P12 bottom bar landmark: reuse the existing "Secciones". Table region names: "Tabla: <título de la tabla>".
- P11 scrolling block name: "Tabla de datos, desplazable".
- P01 `og:image:alt`: "El Archivo — Baloncesto Superior Nacional, 1930–2026".
- P09 404 page: "No encontramos esa página." / "Volver al inicio".
- P10 update prompt (only if chosen): "Hay una versión nueva de El Archivo." / "Actualizar".
- P16 offline state: "Sin conexión. Esta página todavía no se ha guardado en tu dispositivo."

## 10. Deferred by PHASE_71 STEP 2 (appended 2026-10-12)

- **P05** (players.json loaded on every route): not touched, too risky for this step. Stays in PHASE_72 with the data-shape work.
- **P04** (lazy panels, split tabs.js): attempted by reading, SKIPPED. `finishBoot()` calls `buildViews()`, which folds every section's markup (split on `h3.sec` / `h4.sub`) into views and builds the subnav, the landings and the search/deep-link wiring from that complete DOM. Building non-visible panels on first show means reworking that contract (per-section view construction, deep links into an unbuilt section, the Archivo/Equipos splitters that match heading text), well past 100 changed lines and into the DOM shape the function-inventory and harness baselines pin. Left for a dedicated phase; the mobile TBT/TTI numbers stay as measured.
- **P03 cause and fix**: the builders (BOOT, `init.js`) fill `.hubpair`, `.liga`, `.legalrow`, the footer wrapper and `#bottombar` in the first ~300 ms while the splash covers the page; the boxes move as their content arrives. Fixed with one CSS rule (`visibility:hidden` on exactly those boxes while `#splash:not(.gone)` exists; hidden boxes are not scored for layout shift, layout and JS measurements are unchanged). Hiding the whole shell was tried first: CLS 0.00 but mobile LCP 2.1 s -> 5.1 s because the hero would then first paint at the end of the 3 s splash floor, so it was narrowed to the moving boxes.
- **P13 partly**: player page, club page, Calidad and Perfil jumps are fixed (h3/h4 -> h2, same computed style, verified identical in both engines). Not touched: landing/section views that still split on `h3.sec` / `h4.sub` (they sit under the section h1 and are not flagged by axe).
- **P14** (one h1 per section across sub-views), **P15** (`color-scheme`), **P16** (offline state), **P17** (manifest), **P18**, **P19**, **P20**, **P21**: not in the step 2 scope; unchanged. P15 and the offline state are PHASE_73 (visual).
- **P09 precache**: `robots.txt`, `sitemap.xml` and `404.html` are NOT in the service worker precache. A 404 is never served through a cached navigation (the worker only caches `res.ok`), and `cache.addAll` fails as a whole if any entry 404s, so adding them gains nothing and adds risk. `sw.js` is unchanged, so its cache name stays `bsn-shell-v3`.
