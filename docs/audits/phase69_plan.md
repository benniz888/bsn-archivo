# PHASE_69 STEP 1: legal / privacy / accessibility / fonts plan

Read-only audit plus plan. Nothing under `web/` or `tests/` was modified. Drafts of the public Spanish text are in `docs/legal_drafts_phase69.md` (all DRAFT, numbered L1..). Evidence date: 2026-10-12, branch `redesign-v3` @ 16db24a, clean tree.

Method: grep of `web/`, plus Playwright (Chromium and WebKit, 1000px, `web/` served locally on :8124) which loaded the app, visited all 5 sections and their 36 views (`showView`), `inicio` and `perfil`, opened the three games, and recorded every request, `localStorage`, `sessionStorage`, cookies, IndexedDB, and Cache Storage. Script: scratchpad `net69.mjs`.

---

## 1. Audit

### 1.1 External network requests (the shipped app)

Recorded on a full session, both engines. **Every non-local request goes to Google Fonts, and nothing else.**

| Origin | What | Where in code | Observed |
|---|---|---|---|
| `fonts.googleapis.com` | 2 stylesheets (Inter, Oswald) | `web/index.html:52` (Inter `ital,opsz,wght@...400..800; italic 400`), `:56` (Oswald 500/600/700) | 2 requests, both engines |
| `fonts.gstatic.com` | woff2 files | resolved by the two stylesheets | Chromium 3 files: Inter 73,016 B, Inter 37,544 B, Oswald 21,412 B (sizes via curl of the exact URLs). WebKit 4 files (one extra Inter file) |
| `fonts.googleapis.com` / `fonts.gstatic.com` | 2 `preconnect` hints | `web/index.html:50-51` | open a TLS connection to Google before any font is needed |

Per-view check: no view adds any further external request (the `extPerView` map was empty for all 36 views, Inicio, Perfil and the 3 games).

Searched and **not present**: `<script src>` to a third party (all 7 scripts are same-origin `js/*.js`), analytics, tag managers, `<iframe>`, `<embed>`, `<video>`, `<audio>`, `@import`, CSS `url(http...)`, remote images. All `<img>` are same-origin (`web/index.html:62`, `:82`, brand marks). The only other absolute URLs in the code are:
- `<a href>` outbound **links** (no resource load, user must click): `web/js/tabs.js:301-308` (bsnpr.com, YouTube, Instagram, TikTok, X, Facebook, App Store, Google Play) and the footer Instagram link `web/index.html:469`.
- `w3.org` strings in `web/css/main.css` (SVG data-URI namespace, not requests).
- `mailto:` in the footer.

The app is hosted on GitHub Pages (verified: live response header `server: GitHub.com`, `via: 1.1 varnish`, `cache-control: max-age=600`). The host necessarily sees visitor IP addresses in its normal request handling; this is outside the app's code and must be disclosed (see drafts L16 and open question Q4 in `docs/legal_drafts_phase69.md`).

Service worker: `web/sw.js` only handles same-origin GETs (`if (url.origin !== self.location.origin) return;` at the fetch listener), so it never touches Google Fonts.

### 1.2 Device storage

Checked `localStorage`, `sessionStorage`, IndexedDB, cookies, Cache Storage. **Cookies: none. `sessionStorage`: none. IndexedDB: none.** (Playwright: `cookies=[]`, `sessionStorage=[]`, `indexedDB.databases()=[]`.)

All `localStorage` writes go through the `ST` wrapper (`web/js/helpers.js:151-172`, prefix `bsn:`), except the theme read in the head script (`web/index.html:30`). A memory fallback is used if storage is blocked.

| Key (`bsn:` prefix) | Purpose | Written at | Personal data? |
|---|---|---|---|
| `theme` | light / dark / auto | `web/js/tabs.js:5018` (`saveProfile`), read at `web/index.html:30` | No |
| `club` | favourite club id | `tabs.js:5017` | No (a preference) |
| `profile` | JSON `{v,name,club,theme,start,primer}`; `name` is **free text, max 24 chars, typed by the user** | `tabs.js:4987-5017`, input at `tabs.js:4741` | **Yes, if the user types a real name.** Only user-entered field in the app. Never sent anywhere |
| `recent` | last 3 players / clubs opened | `helpers.js:164-168`; cleared by `resetProfile` (`tabs.js:4846`) | No identity, but is browsing history on the device |
| `hlbest` | best streak in Sube y Baja | `games.js:796` | No |
| `streak` | daily-game stats `{cur,best,played,last,totalScore,immaculate}` | `games.js:180-217` | No |
| `grid:YYYY-MM-DD` | today's and yesterday's Cuadricula answers; older ones deleted | `games.js:171`, cleanup `games.js:196-197` | No |
| `quiz:recent` | last 10 players served in Quien soy | `tabs.js:5299` | No |
| `data:<path>` (e.g. `data:index/players.json`, `data:manifest.json`, `data:seasons/2026.json`, ...) | offline copy of site data | `helpers.js:193` | No (it is the public archive) |
| `data:digest` | version stamp of that copy | `helpers.js:203` | No |

Observed in the Playwright run: 13 keys, of which `bsn:data:index/players.json` is 722,655 characters (the largest). Total is dominated by the data copy.

Service worker caches (`web/sw.js`): `bsn-shell-v2` (HTML, CSS, JS, brand icons, manifest, favicon; 8 entries observed) and `bsn-data` (per-entity JSON; 1 entry observed). Public site content only, no personal data. `sw.js` is registered at `web/index.html:1142-1143`.

User controls that already exist: **"Descargar mis datos"** (`exportProfile`, `tabs.js:4812`, exports every `bsn:*` key as JSON) and **"Restaurar preferencias"** (`resetProfile`, `tabs.js:4834`). Important gap: `resetProfile` deliberately does NOT delete `streak`, `hlbest`, `grid:*`, `quiz:recent`, or the `data:` copy (it says so in its own message, `tabs.js:4840-4842`). **There is no in-app "delete everything" control.** The privacy text must therefore tell users to clear site data in the browser, unless the owner approves adding a control (Q5 in the drafts).

Inaccuracy to fix: `web/index.html:400` (Perfil lede) says "no hay servidor". The site is served by a host that logs requests; the sentence is about data, not literally true. Needs an owner-approved rewording (draft L10).

### 1.3 Footer, quoted exactly (`web/index.html:464-471`)

```
El Archivo · construido por <b>bennizpr</b> · San Juan, Puerto Rico.<br>
Los datos vienen de fuentes públicas citadas en «El archivo». Proyecto independiente de un aficionado. No está afiliado ni respaldado por el Baloncesto Superior Nacional ni por sus equipos.<br>
Este sitio no usa cookies ni analítica. Las tipografías vienen de Google Fonts, por lo que Google recibe tu dirección IP. Tu navegador guarda solo tus preferencias (tema y club favorito), tu progreso en los juegos y una copia de los datos para que el sitio funcione sin conexión.<br>
¿Ves un error o quieres que retiremos algo? Escríbenos a <a href="mailto:benniz.8008@gmail.com" ...>benniz.8008@gmail.com</a> o por Instagram <a href="https://www.instagram.com/bennizpr/" ...>@bennizpr</a>.
```

Facts about it:
- It is the only place the Google IP disclosure appears. It becomes **false** the moment fonts are self-hosted, so the font change and the footer text must ship in the same release.
- It already carries a no-affiliation statement (owner-approved Sep 24). So option A (drafts L2 / L32) is the current state of the site, not a new choice.
- "(tema y club favorito)" understates the storage: it omits the optional name, recent items, quiz history, and the 700 KB data copy. The privacy page will be more complete; the footer line should be shortened and point to it.
- The two links render **15 px tall** (measured at 390 and 1000 px: 148x15 and 64x15). The project rule is >= 44 px. Footer font is 12.5 px (`css/main.css:2215`).
- Footer is `<footer class="foot">` after `</main>`, so it is a `contentinfo` landmark.
- `target="_blank"` on the `mailto:` link is unnecessary.

Other public meta text: `<meta name="description">` and OG / Twitter descriptions say "Proyecto de un aficionado, no oficial." (`web/index.html:7,12,16`). No `og:image`. Search placeholder / aria-label unaffected.

### 1.4 BSN marks, logos, images

- **No league logo, crest or photo file exists in the repo.** `web/img/crest/` and `web/img/player/` hold only `.gitkeep`; `web/data/manifest.json` has `"assets": {}`, so the `imgTry` layer emits no `<img>` (`tabs.js:472`). Confirmed again in the Playwright run: zero image requests other than the brand marks.
- **Club identities are drawn in code:** `crestSVG` (`tabs.js:609`) and `crest` (`tabs.js:640`) render per-franchise emblems/mascots in club colours; comments at `tabs.js:489, 499` call them "original" illustrations. The app tells users so at `tabs.js:3469` ("Todos los escudos y retratos están dibujados en SVG con los colores reales del club..."). Residual risk: club names, mascots and colours depict real clubs' identities even though no league file is used. See drafts Q14.
- **Brand assets under `web/img/brand/` (10 files, all added in commit d0a2763, 2026-10-10):** `logo_mark_64/128` (.png and .webp), `favicon_16/32.png`, `apple_touch_icon_180.png`, `icon_192/512.png`, `icon_maskable_512.png`; plus `web/favicon.ico`. Provenance recorded in `docs/specs/redesign_v3/02_brand_and_logo_spec.md`: the owner picked "Logo Options/logos-04.png" and the files were "generated" from it. **Who or what created the original artwork, and under what rights, is NOT recorded anywhere in the repo: UNKNOWN.** The mark reads "EL ARCHIVO" and contains an orange ball and a folder; it does not contain "BSN" text. Whether any element resembles a third-party mark is not verified. See drafts Q2.
- **BSN naming in public text** (not exhaustive, text only, no logos): footer (no-affiliation line), title/meta (`El Archivo · Baloncesto Superior Nacional, 1930–2026`), glossary (`BSN`, `Final Brava`, `La Más Dura`), outbound links to the league's accounts (`tabs.js:301-308`, "Official site", "The league's own app").
- **Third-party editorial content:** `tabs.js:1509` shows league-app news headlines ("Titulares vistos en la app oficial del BSN el 2 de septiembre de 2026. Solo los títulos, resumidos"), and `tabs.js:1573` a standings capture "Fuente: app oficial del BSN, 2 sep 2026". `data.js`/`tabs.js` comments say 2026 player totals derive from the league's official export (`POOL_BSN26`, `bsn_2026_official.csv`, per PHASE_60). Whether the league permits reuse is unknown; the league was emailed Sep 22 with no reply (master plan). See drafts Q15.
- **Fonts:** Inter and Oswald, both OFL 1.1 (verified from the `@fontsource` package licence files, which carry the full OFL text and the copyright lines for "The Inter Project Authors (https://github.com/rsms/inter)" and "The Oswald Project Authors (https://github.com/googlefonts/OswaldFont)").

### 1.5 Wikipedia-derived data: where and whether attributed

Where used (public text and data):
- `web/js/data.js:121, 363, 369` (arena names "carried from Wikipedia"; franchise table; team-page plan sources).
- `web/js/tabs.js:360` (municipality pages from es.wikipedia.org), `:2198` (UI label "Colores de Wikipedia" vs "Colores aproximados" from `f.colorSrc==='wiki'`), `:3402-3463` (data-quality / coverage text: 1945 disputed champion, MVP table, career leaders "vienen de Wikipedia", season pages 2009/2016/2017/2018/2024+), `:3715-3880` (per-player Hall of Fame bios, each with `src:'Wikipedia ...'`), `:4141`, `:6862-6874`.
- `web/data/index/franchises.json`, `web/data/index/career_leaders.json` (contain "Wikipedia" strings in notes/provenance).
- Backing data: `docs/project.md` L2 (Wikipedia CC BY-SA, "attribution must be machine-tracked via `sources`").

**Attribution today:** the name "Wikipedia" is cited as a source in many places, but there is **no licence statement anywhere**: no "CC BY-SA 4.0", no link to the licence, no link to the specific articles, no "changes were made" notice, no pointer to a credits page (`grep -i "cc by|licen|creative commons"` over `web/index.html`, `web/js`, `web/css` returned nothing relevant). So attribution is partial (credit by name) and the licence terms are not met as written. PHASE_69 Credits page closes the main gap. Drafts Q6 asks the owner whether bios are verbatim, close paraphrase, or facts only, because share-alike applies to adapted text.

The master plan also says "RealGM and latinbasket handling stays exactly as decided (no new mentions)". The app already names RealGM in public strings (`tabs.js:434-435, 3406-3407`, `data.js:121`), but the Credits draft does **not** add RealGM / latinbasket (drafts Q7).

### 1.6 Accessibility state (what is verifiably true today)

| Item | State | Evidence |
|---|---|---|
| `lang` | OK: `<html lang="es">` | `web/index.html:2` |
| Landmarks | `header`, `nav aria-label="Secciones"` (rail), `main`, `footer` present | `index.html:79,125,140,464`. `#bottombar` is `role=tablist` aria-label "Navegación principal" (`index.html:483`), not a `nav`. `<main>` has no `id` |
| Skip link | **Missing** (no `a[href="#main"]`, `.skip`) | measured |
| Headings | One `<h1>` per panel | `index.html:210,273,294,366,399,417` |
| Focus visible | Global `:focus-visible{outline:2px solid var(--focus)}` (`css/main.css:322`, `:775`) plus component rules. **Gap:** `.cell:focus-visible` sets `outline:none` and relies on a border-colour and scale change | `css/main.css:2103` (the season ribbon in Historia) |
| Focus on route change | **Not managed**: after `showTab('perfil')` the active element is `BODY` | measured in Playwright |
| Reduced motion | Many `@media (prefers-reduced-motion: reduce)` blocks (`css/main.css:323, 659, 671, 766, 779, 810, 1794, 1861, 1908, 2088, 3033, 3081`) and JS checks (`helpers.js:142`, `tabs.js:1151, 1184`). Splash and every animation not individually audited | partial |
| Zoom / scaling | **Fails**: `<meta name="viewport" content="..., maximum-scale=1, user-scalable=no, ...">` blocks pinch zoom on browsers that honour it (WCAG 1.4.4) | `index.html:5` |
| Tap targets | Backlog exists | `docs/audits/phase60_tap_targets.md`; PHASE_68 commit "Fix ... tap targets". Footer links 15 px (above) |
| Contrast | Audited in earlier phases (token sweep, PHASE_68b `p68b_contrast`). Open items: rank badges 1-3 flagged 1.14-1.41:1, "probably a false positive" and unverified (`phase68_archivo_audit.md` A16) | do not claim full AA |
| Alt text | Brand `<img>` are `alt=""` (decorative; the wordmark is text and the mark button has `aria-label`). SVG crests: 31 `aria-hidden` / `role=img` occurrences in `tabs.js`; per-crest alt coverage not audited in this step | partial |
| Search / form labels | `#hubSearch` has `aria-label`; `#profName` label coverage not checked | partial |
| Document title per route | Single static `<title>`; does not change by route | `index.html` |
| Keyboard operation of tab sets | Roving tabindex on rail tabs (`tabs.js:_showPanel`) | partial, no trap test run here |

PHASE_69 can only truthfully claim a **target** (WCAG 2.2 AA, per the spec) and list these gaps. Not run in this step: screen reader testing, axe/Lighthouse, full keyboard walk (planned for PHASE_71).

---

## 2. Fonts: self-host Inter and Oswald

### 2.1 What the CSS really uses (measured)

- Families: `Inter` (body, `css/main.css:290`; SVG text `tabs.js:636`), `Oswald` only via `--font-display` (`css/main.css:2268`) on short numerals and titles.
- Inter weights requested in CSS: 400 (5), 500 (2), 600 (47), 700 (70), 800 (18), 300 (1). 300 maps to 400 today because Google is only asked for 400-800; no regression if we keep that. Browser default bold (`<b>`, headings via `font-weight:800` rule at `css/main.css:316`) is covered by the same range.
- Oswald: 500, 600, 700 requested; code also sets 800 (`tabs.js:3182`, `css/main.css`), which clamps to 700 in the variable font (range 200-700) just as it does now.
- Inter italic: one rule, `.nodata{font-style:italic}` (`css/main.css:1238`). Google currently ships an italic 400 file for it.
- Features: `font-variant-numeric:tabular-nums`, `font-feature-settings:"tnum","cv05"`. **Verified with fontTools:** the Google-served Inter file and the fontsource latin files expose the same GSUB set (`calt ccmp dnom frac locl numr pnum tnum`); `cv05` is absent in both, so it is a no-op today and stays one. Axes match: Google `opsz 14-32, wght 100-900`; fontsource `-opsz-` file the same.
- Characters: scanned every `.html/.css/.js/.json` under `web/` (including all ~3,300 `data/players/*.json`). Only 9 distinct characters fall outside the Latin subset range: `→ ▲ ▼ ─ ═ ≈ ■ □ ⇄`, all symbols that Google's `latin` subset also lacks (they fall back to a system font now and will keep doing so; no change). **No latin-ext letters are used anywhere.** No escaped `\uXXXX` letters either.

### 2.2 Files and bytes

Source: npm packages `@fontsource-variable/inter@5.3.0` and `@fontsource-variable/oswald@5.3.0` (both OFL-1.1), fetched with `npm pack` and measured. woff2 only.

| File to ship | Source file in the package | Bytes | Covers |
|---|---|---|---|
| `web/fonts/inter-latin-opsz-normal-5.3.0.woff2` | `files/inter-latin-opsz-normal.woff2` | **72,920** | Inter, wght 100-900 + opsz 14-32, latin; exact parity with what Google serves today |
| `web/fonts/oswald-latin-wght-normal-5.3.0.woff2` | `files/oswald-latin-wght-normal.woff2` | **28,488** | Oswald, wght 200-700, latin |
| `web/fonts/OFL-Inter.txt` | `LICENSE` | 4,477 | OFL text + Inter copyright line |
| `web/fonts/OFL-Oswald.txt` | `LICENSE` | 4,388 | OFL text + Oswald copyright line |

- **Added bytes: 101,408 B of font data** (+ 8,865 B of licence text, + about 0.7 KB of `@font-face` CSS in `main.css`), about **111 KB in the repo**. Font bytes on the wire per first visit: **101,408 B**.
- **Removed:** the 2 Google stylesheets, 3 (Chromium) / 4 (WebKit) gstatic font files (131,972 B observed in Chromium, sizes via curl), 2 preconnect handshakes. Net on first visit in Chromium: **about 30.6 KB less** and 5 fewer requests, and zero third-party origins.
- Alternative considered: Inter without opsz (`inter-latin-wght-normal.woff2`, 48,256 B) saves 24.7 KB but changes large-size glyph shapes slightly (no optical sizing above 14 px), which would invalidate the screenshots approved in earlier phases. **Not recommended** unless the owner wants the bytes.
- Alternative considered: static per-weight files. Inter latin 400/500/600/700/800 = 5 files, about 121 KB; Oswald 500/600/700 = 3 files, 38,116 B. Larger and more requests than the variable files. Rejected.

**Italic:** recommendation is to ship **no italic file**. The browser synthesises an oblique for the single `.nodata` rule. An Inter italic latin file would add 51,832 B (wght only) for one rule. This is a visible (tiny) change, flagged for the owner in Q12(b) of the drafts file.

**latin-ext:** recommendation is to ship **latin only**. The measured scan shows no latin-ext characters in any shipped text. A `unicode-range` latin-ext face would cost 0 bytes on the wire until used but would add 85,068 B (Inter) + 23,952 B (Oswald) to the repo. Instead a test fails if any shipped text uses a character in the latin-ext ranges, which tells the owner to add the subset the day a name like "Ł" appears.

### 2.3 CSS, display and preload

```css
@font-face{font-family:'Inter';font-style:normal;font-weight:100 900;font-display:swap;
  src:url(../fonts/inter-latin-opsz-normal-5.3.0.woff2) format('woff2');
  unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}
@font-face{font-family:'Oswald';font-style:normal;font-weight:200 700;font-display:swap; /* same src/unicode-range pattern */ }
```
- Family names stay exactly `Inter` and `Oswald`, so no other CSS rule and no SVG `font-family` attribute changes.
- **`font-display: swap`**, same behaviour as today's `display=swap` in the Google URLs: text is visible at once in the fallback, then swaps. `optional` would avoid layout shift but can leave a first-time visitor on the fallback for the whole visit, which is worse for a brand-led presentation.
- **Preload both files** in `<head>`: `<link rel="preload" href="fonts/inter-latin-opsz-normal-5.3.0.woff2" as="font" type="font/woff2" crossorigin>` and the same for Oswald (Oswald is used above the fold on Inicio). `crossorigin` is required for font preloads even same-origin. Placed after the theme script. This removes the CSS-then-font waterfall, so the swap is rarely visible. The Google `preconnect`/`stylesheet` links (4 lines, `index.html:50-56`, plus the PHASE_2 comment) are deleted.
- Font URL is relative to `css/main.css` (`../fonts/...`). Opening `index.html` from `file://` also works (bonus: no network at all).

### 2.4 `sw.js` changes

1. Bump `SHELL` `'bsn-shell-v2'` to `'bsn-shell-v3'`. `activate` drops every cache not in `KEEP`, so the old shell (with the old footer and Google links) is evicted. The comment at the top of `sw.js` already prescribes a bump "whenever the shell's markup changes shape", and the new routes and footer do.
2. Add both woff2 files to `PRECACHE` so fonts work offline on the first load after install (the precache is best-effort; a miss does not block install).
3. Route `/fonts/` requests: add `|| url.pathname.includes('/fonts/')` to `isShellAsset` (network-first like the other shell assets) **or** a dedicated cache-first branch. Recommendation: cache-first for `/fonts/`, because the filenames are versioned (`-5.3.0`) and so immutable. Either way no code path needs an exception for other origins.
4. Update the header comment (lists what `bsn-shell` holds).
5. Cache name is bumped by hand; there is no automatic invalidation, so the plan makes the bump a checked test (section 6).

### 2.5 Interaction with the pre-commit `?v=` hashing

- `.githooks/pre-commit` runs `src/update_asset_hashes.py` when `web/css|js` or `web/index.html` is staged. Its regex matches only `<link rel="stylesheet" href="css/X.css">` and `<script src="js/X.js"></script>`. **The new `<link rel="preload" href="fonts/...">` lines do not match, so they are left untouched and get no `?v=`.** That is intended: font filenames are versioned.
- `main.css` bytes change (new `@font-face`), `tabs.js` bytes change (PANELS), `index.html` changes: the hook will rewrite the `?v=` hashes and **block the commit** until `web/index.html` is staged with the refreshed hashes. The COMMIT step must stage `web/index.html` last, after running `.venv/bin/python -m src.update_asset_hashes`, and `src/verify_clean.py` (it checks each tag's hash equals the file's sha256[:12]) must pass.
- `max-age=600` on GitHub Pages applies to the woff2 as well. Harmless: a new font version gets a new filename.
- No new `web/js/*.js` file is needed, so no new hashed tag is needed.

### 2.6 Confirmation: no Google request remains

After the change, nothing in `web/` references `fonts.googleapis.com` or `fonts.gstatic.com`. Verification (to be done in the build step, listed here as acceptance criteria):
1. `grep -rE "googleapis|gstatic" web/` returns nothing (also asserted by a pytest).
2. The Playwright script that produced this audit (`net69.mjs`) is re-run in Chromium and WebKit over all views and must report **only `localhost`** origins and a `fonts` request count of 2 (both served from `/fonts/`).
3. Fonts verified loaded: `document.fonts.check('600 16px Inter')` and `'700 16px Oswald'` true, and `document.fonts` shows both faces `loaded`, in both engines.
4. Offline: with the service worker active, set the context offline, reload, fonts still render.
5. Screenshots at 390 and 1000 px compared against the pre-change ones: no layout shift.

---

## 3. The four pages, routes and footer

### 3.1 Routes, using the existing hash router (no new mechanism)

The router already supports a panel with no nav button: `perfil`. `PANELS = [...TABS.map(t=>t[0]),'perfil']` (`tabs.js:921`); `applyHash` ends with `if(PANELS.includes(a)){... showTab(a)}` (`tabs.js:6852-6856`); `showTab` -> `_showPanel` (`helpers.js:93`, `tabs.js:1124`) toggles `section[hidden]` by id and updates the hash. So:

- Add four static `<section id="privacidad|terminos|accesibilidad|creditos" hidden role="tabpanel" aria-label="...">` blocks to `web/index.html` (same shape as `#perfil`, `index.html:395`), each with an `<h1 class="big">` and the page text. **Content is plain HTML, so no JS function is needed.**
- Change one line: `const PANELS=[...TABS.map(t=>t[0]),'perfil','privacidad','terminos','accesibilidad','creditos'];` (`tabs.js:921`).
- Links are plain `<a href="#privacidad">` etc. `hashchange` -> `applyHash` -> `showTab`. Back/forward and deep links work for free. Legacy / unknown hashes still fall back to Inicio.
- **No new top-level names** (closures only, per `session.md`): zero new functions or globals; the inventory baseline (476) is unaffected because a const keeps its name. Run `tests/harness/inventory.py` anyway at the end of the build.
- Nav side effects verified from code: `_showPanel` iterates `NAV` and `#bottombar a` and finds no match, so no rail/bottom tab stays selected (same as `perfil`). Good: a legal page is not a section.
- **Small optional improvement (recommended, in scope for these 4 pages only):** after `_showPanel` for one of the four ids, move focus to the panel's `h1` (`tabindex="-1"`, or set it in the markup) so keyboard and screen-reader users land on the page they opened rather than on `BODY`. This is a 2-3 line edit inside `_showPanel`, no new names. If the owner prefers zero JS change beyond PANELS, the statement must list "focus is not moved on route change" as a known gap (the draft already does).
- **Document title:** unchanged by route today. Out of scope; listed as a known gap.

### 3.2 Where they link from

1. **Footer on every page** (all four links). The footer is global and lives after `</main>`.
2. **Perfil** (`#perfil`): one line under the "Descargar mis datos / Restaurar preferencias" buttons: pointer to `#privacidad` ("Qué se guarda en este navegador y cómo borrarlo"). That is where a user thinks about stored data.
3. **Inicio:** one small, quiet link row at the bottom of the Inicio panel: "Sobre este archivo: Créditos y fuentes · Privacidad". The footer is already directly below Inicio, so this is the lightest possible addition; **owner decides** if even this is wanted (owner decision). Not a card; no emoji.
4. **Archivo > Cobertura y fuentes**: a link to `#creditos` next to the source list, because that is where a reader looks for licences.
5. `#terminos` references `#archivo/calidad` (data-quality page) as required by the drafts.

### 3.3 Footer layout

Structure (inside the existing `<footer class="foot">`, still the `contentinfo` landmark):

```
[tri rule]
Identity + status (existing owner-approved wording, edited only where it becomes false)
<nav aria-label="Información legal">  Privacidad | Términos | Accesibilidad | Créditos </nav>
Corrections line + Contacto (email, Instagram) as 44px targets
```
- **390 px:** the legal `nav` is a 2x2 grid (`grid-template-columns:1fr 1fr`), each link `min-height:44px`, `display:flex; align-items:center`, text left-aligned, no wrapping inside a cell; stacked above the contact line. No horizontal scroll. Footer text 12.5 px stays; link text could go to `--fs-xs` token (flag if a non-exact literal-to-token mapping arises, per the saved token-scale rule).
- **1000 px:** one row, `display:flex; flex-wrap:wrap; gap`, links with `min-height:44px` and horizontal padding so the hit area is >= 44 x 44 px; separators drawn with `border-left` on the items (CSS), not text bullets, so screen readers do not read them.
- Email and Instagram links: `display:inline-flex; align-items:center; min-height:44px`. This fixes the 15 px footer targets in the spec's own backlog. Drop the unnecessary `target="_blank"` on the `mailto:`.
- Colours: existing tokens only (`--ink-3` text on the page background is the existing footer pair; links use the existing link colour). Contrast >= 4.5:1 must be measured for the final pair; focus ring via the global `:focus-visible` rule. No emoji (guarded by `tests/test_no_emoji_in_web.py`).
- Legal pages themselves: reuse `.panel`, `.phead`, `.tri`, `.lede`, `.card`/`.note`, `h3.sec` classes already in `main.css`. Long-form text with `max-width` for readable line length (about 65ch), no new component. Estimated CSS: footer (about 25 lines) + `.legal` prose (about 15 lines). New rules only via existing `--sp-*`/`--fs-*` tokens.

### 3.4 Perfil and footer text corrections (needs owner approval, listed in `strings_pending_phase69.md` at build)

- Footer privacy sentence: replace the Google Fonts sentence (draft L3).
- Perfil lede (`index.html:400-401`): "no hay servidor" is not accurate (Q4); proposed wording in draft L10.

---

## 4. Files that will change (build step)

| File | Change |
|---|---|
| `web/index.html` | remove Google preconnect/stylesheet lines (50-56); add 2 font preloads; add 4 `<section>` pages; rewrite footer; Perfil and Inicio link lines; (decision) viewport zoom tokens |
| `web/css/main.css` | 2 `@font-face`; footer + legal-page rules |
| `web/js/tabs.js` | `PANELS` array (line 921); optional focus-to-h1 (inside `_showPanel`) |
| `web/sw.js` | `SHELL` v3, `PRECACHE` + fonts, `/fonts/` route, header comment |
| `web/fonts/` (new) | 2 woff2 + 2 OFL text files (+ a short `README.txt` naming source package and version) |
| `docs/strings_pending_phase69.md` (new) | every new/changed public string, for owner approval |
| `docs/session.md` | phase exit log |
| `tests/test_phase69_legal.py` (new) | see section 6 |
| `tests/test_fonts_selfhosted.py` (new) | see section 6 |

Not touched: `data/`, `src/`, `web/data/`, other `web/js/*.js`. `tests/test_web_text.py` has a known byte-test failure on the baseline; the new strings must not make it worse (check before/after).

---

## 5. Decisions and risks to surface (full list in the drafts file, "OPEN QUESTIONS FOR OWNER")

1. Footer and font change must land in the same release (the Google sentence is false afterwards).
2. Viewport zoom lock (`index.html:5`) is a real WCAG 1.4.4 failure; one-line fix, but input font sizes were not re-checked for iOS focus-zoom (`#hubSearch`, `#askInput` use 16 px, good; `#profName` not checked). Recommend removing `maximum-scale=1, user-scalable=no` in PHASE_69 and verifying at 390 px in WebKit.
3. No "delete all my data" control exists.
4. Brand artwork provenance unknown; league data / headline reuse unknown; league has not replied.
5. Wikipedia licence statement missing today.

## 6. New tests (to write in the build step)

`tests/test_phase69_legal.py` (static, no browser, in the style of the other `tests/test_*` files):
- the four sections exist in `web/index.html` with ids `privacidad terminos accesibilidad creditos`, each `hidden`, each with exactly one `<h1>`;
- `PANELS` in `web/js/tabs.js` contains all four ids;
- footer contains links `href="#privacidad"`, `#terminos`, `#accesibilidad`, `#creditos` inside one `nav` with an `aria-label`;
- footer no longer contains "Google Fonts" or "Google recibe";
- every `href="#..."` legal link resolves to an existing section id;
- no emoji (reuse the existing helper) in the new sections;
- CC BY-SA 4.0 attribution text and the licence URL are present in `#creditos`, plus the "changes were made" sentence;
- no `target="_blank"` without `rel="noopener"` in the footer.

`tests/test_fonts_selfhosted.py`:
- `grep` over `web/` finds no `googleapis` / `gstatic` / `preconnect`;
- each `url()` in an `@font-face` resolves to a file; each file starts with the woff2 magic `wOF2`; sizes within the documented values;
- both `OFL-*.txt` exist and contain "SIL OPEN FONT LICENSE";
- `sw.js` `SHELL` is not `bsn-shell-v2`, `PRECACHE` lists both woff2 files;
- `index.html` preload hrefs equal the `@font-face` files and carry `crossorigin`;
- no character in shipped text (html/css/js/json under `web/`) falls in the latin-ext ranges (fails with a pointer to add the latin-ext subset).

Browser verification (not pytest, per the Redesign v3 rules): Chromium and WebKit, 390 and 1000 px, one phone and one desktop screenshot per page (4 pages x 2 = 8, plus the footer on Inicio at both widths); request recording as in 2.6; keyboard walk to each footer link, Enter, focus lands on the page `h1`, Escape/Back works; tap-target measurement of every footer link >= 44 px in both widths; offline reload.

Report format for the build step: PHASE / DONE / VERIFIED / NEXT, `git diff --stat`, `git status --short`. No commit, no push.
