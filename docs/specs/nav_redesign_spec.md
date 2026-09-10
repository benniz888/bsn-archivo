# Spec: PHASE_8 — navigation, layout & visual-composition redesign

Builds on PHASE_7 (`redesign_spec.md`) — same Inter type scale, `--sp-*`
spacing, palette, motion tokens. This phase is structure + composition, not a
re-theme.

References (pattern, not literal look): Apple.com (whitespace, confident type,
restrained colour), Airbnb.com (browsable cards, clear active-state nav),
Basketball-Reference (density, ≤2 clicks), StatMuse (editorial stat blocks —
headline + one line + a visual, not a number in a box).

## [DECISION]

Owner-approved 2026-09-11:

1. **5 top-level nav.** The wordmark is **Inicio** — home *and* the live
   "Ahora" view (absorbs the old Hoy). Top strip = `Historia · Jugadores ·
   Equipos · Juega · Archivo`. **Consulta** folds into **Archivo** (ex-Fuentes)
   and gets *more* prominent via the persistent hero ask-bar.
2. **Editorial blocks** (StatMuse style) on the anchor surfaces only:
   Inicio hero + hub cards, `showPlayer` hero, `showTeam` hero. Dense data
   tables keep PHASE_7's BR density untouched.
3. **Club picker** moves off the header into the Equipos mega-menu featured
   block (and the top of the Equipos section on mobile). Header = wordmark ·
   theme · gear.
4. **Mobile:** top tab row removed; bottom bar carries all 6
   (`Inicio · Historia · Jugadores · Equipos · Juega · Archivo`). Tapping goes
   to the section landing, which lists its views.

Owner-approved 2026-09-11 (revision — supersedes the scroll-anchor model of
commit 8.2):

5. **Each nav section is a view router**, not one long scroll. Every former
   `h3.sec` block, plus the pre-heading content, is a **focused view** with its
   own `#section/view` URL. A `.subnav` pill rail under the section title
   switches them. Still one HTML file, JS-driven views (no build step, opens
   from `file://`).
6. **The nav word opens a section landing** — an overview page listing the
   section's views (a plain link grid in 8.2b, an editorial card grid in 8.3).
   Bare `#historia` → that landing.
7. **Sub-nav = a pill row under the section title.** Horizontal-scroll on
   mobile. Replaces the `.jump` chip rail and the disclosure folds entirely
   (`foldSections`, `revealNode`, the desktop ≥1120px auto-expand block — all
   removed).
8. **8.3 editorial blocks link to real views** (`#section/view` /
   `showView(...)`), never scroll anchors.
9. **Rollout:** one commit for the router (8.2b), then 8.3.

## [COMMITS]

### 8.1 — IA + nav shell (DONE)

- `#hoy` merged into `#inicio`: hub grid + `#heroBox` stay at top, then a
  `.phead` "La liga ahora" + the seven Hoy `h3.sec` blocks (Lo próximo · Final
  Brava · Finales anteriores · Posiciones 2026 · Líderes 2026 · En esta fecha ·
  Canales). `#hoy` section deleted.
- `#consulta` merged into `#fuentes`, renamed `#archivo`: `.phead` "El archivo"
  → ask input (pre-fold) → `h3.sec` Constructor de consultas · Cobertura del
  archivo (`#coverage` + `#sourcesBox`) · Calendario y cobertura · Glosario.
- `TABS` 8→6 (`inicio` first, then the 5); `NAV = TABS.slice(1)` drives the
  desktop strip, `BOTTOM = TABS.map(t=>t[0])` the mobile bar (6). `buildNav`
  and `showTab`'s aria loop use `NAV`.
- `applyHash` `MOVED`: `hoy`/`calendario` → `inicio`, `consulta`/`fuentes` →
  `archivo` (PHASE_6's `records`/`refuerzos` → `historia` kept).
- `buildSources` writes to `$('#sourcesBox')`; `HUB` trimmed to the 5 sections
  (+ Comparar), `hoy` card dropped; prose "Ver Fuentes" → "Ver «El archivo»".
- Active-underline: full-width under the label, active weight 800.
- No mega-menu yet — nav items are plain `showTab`. Harness:
  `scratchpad/ia_harness.mjs`.

### 8.2 — mega-menu (DONE — routing superseded by 8.2b)

- **`NAV_MENU`** — data for the 5 sections: `cols` (grouped `[label, target]`
  link lists) + a `feat` key. Targets are either an `h3.sec`/`h4.sub` heading
  prefix (accent-insensitive) resolved by **`goSection(tab, needle)`** — which
  `showTab`s, opens the fold via `revealNode(foldbody)` and smooth-scrolls — or
  a `__key` dispatched through **`MEGA_ACT`** (`__cmp` → Comparar view,
  `__daily`/`__perfect`/`__quiz`/`__hl` → `openGame(id)`, `__ask` → focus the
  ask input, `__active`/`__gone` → `goEl` to the crest grids).
- **Desktop:** `#megaPanel` inside `nav.tabs` (`position:absolute; top:100%`).
  `openMega(id)` on `mouseenter`/`focus` of a nav button → renders
  `.mega-inner` (`.mega-cols` + `.mega-feat`), `.open` fades it in. `mouseleave`
  → `scheduleClose` (140ms, cancelled by re-entering the button or the panel).
  `Escape` and any `scroll` → `closeMega`. `aria-haspopup`/`aria-expanded` on
  the buttons.
- **`megaFeat(k)`** — the featured block: `topfranq` (most-titled franchise,
  crest + N + line), `compare` (Torres ⇄ Morales), `myteam` (club picker,
  re-rendered on club change), `daily` (today's Cuadrícula #N), `gap`
  ("antes de 2011 no hay estadística por temporada"). Plain in 8.2; 8.3 makes
  these full editorial blocks.
- **Mobile:** `@media(max-width:859px)` hides `nav.tabs` entirely (bottom bar
  is the nav) and `.mega`. `buildMega()` drops a `.secfeat` (= the same
  `megaFeat` block) at the top of each nav section, and the `foldSections`
  `.jump` chip rail is enlarged (`--fs-sm`, 7×14 padding) as the section's
  sub-nav.
- Harnesses: `scratchpad/mega_harness.mjs` (menu data integrity, every target
  resolves, CSS gates) + `mega_dom_harness.mjs` (open/close, aria, mobile
  no-op, `megaGo` dispatch).

### 8.2b — section view router (DONE)

Turns the five nav sections into view routers. One reviewable commit.

**Routing model** — one HTML file, JS views. `showTab(section)` toggles the 7
`<section>` panels (was `showTab`'s whole job; now `_showPanel`); the new
`showView(section, view)` toggles the `.view` divs inside a section — same
mechanism, one level deeper.

- **`buildViews()`** (replaces `foldSections`) runs once in `finishBoot` after
  every builder. Per-section config `VIEW_MAP`: `split` selector (`h3.sec`, or
  `h4.sub` for Equipos), a `pre` slug for the content before the first heading,
  a `map` of heading-text → `[slug,label]`, plus `adopt` (an existing hidden
  container → a view, e.g. `#jugComparar`), `detail` (a view reached only via a
  handler, not the subnav, e.g. `#teamDetail` → `equipo`), `drop` (dead markup),
  `host` (split a child, not `.panel` — `#jugBuscar`). Juega is custom: the
  pre-stage content (`streakStrip`/`storageNote`/`gameShelf`) is `__landing`,
  each `.stage` is a view. Each section gets a synthetic **`__landing`** view
  (featured block + link grid) prepended, and a **`.subnav`** pill rail after
  the `.phead`.
- **Views** —
  `historia`: `cinta` (pre) · titulos · dinastias · finales · premios · refuerzos · temporadas.
  `jugadores`: `buscar` (pre) · comparar (adopted) · lideres · records · salon · nba · dirigentes · canchas.
  `equipos`: activos · duenos · desaparecidos · retirados · `equipo` (detail-only).
  `juega`: `__landing` (shelf) · cuadricula · temporada · quiensoy · subeybaja.
  `archivo`: `preguntar` (pre) · constructor · cobertura (grid + `#sourcesBox`) · calendario · glosario.
- **URLs** — `#historia`, `#historia/dinastias`, `#historia/temporada/1971`
  (season detail, renders in `cinta`), `#jugadores/jugador/<slug>` (in
  `buscar`), `#jugadores/comparar/a/b`, `#equipos/equipo/<key>`,
  `#juega/cuadricula`, `#archivo/glosario`, … `showView` writes the hash;
  `setHash` guards a re-entrancy echo (`HASH_ECHO`) so the `hashchange`
  listener doesn't double-route. Every navigation is a history entry —
  back/forward walk the view history.
- **`applyHash`** — two-token parse + expanded `MOVED`:
  `hoy`/`calendario`→`inicio`, `records`→`jugadores/records`,
  `refuerzos`→`historia/refuerzos`, `consulta`→`archivo/preguntar`,
  `fuentes`→`archivo/cobertura`; shape redirects `#historia/<year>`→
  `historia/temporada/<year>`, `#equipos/<key>`→`equipos/equipo/<key>`,
  `#jugador/<slug>`→`jugadores/jugador/<slug>`, `#comparar/a/b`→
  `jugadores/comparar/a/b`. Unknown → `#inicio`.
- **Mega-menu** — `NAV_MENU` targets are now view slugs (or `section/slug` to
  cross over); `megaGo` → `showView`. `goSection`/`goEl`/`MEGA_ACT` deleted.
  `megaFeat` blocks head each landing (`buildLanding`); `paintLandingFeats`
  re-renders them on club change (was `buildMega`'s `.secfeat` drop).
- **Retired:** `foldSections`, `revealNode` (repurposed → surface a hidden
  view), `goSection`, `goEl`, `MEGA_ACT`, `buildMega`, `#jugMode` markup, the
  `.jump`/`.fold*` CSS, the `@media(min-width:1120px)` auto-expand block, the
  `.secfeat` CSS.
- **Detail entry points re-pointed:** `showTeam` → `showView('equipos','equipo')`
  + `setHash`; `showPlayer` → `showView('jugadores','buscar')` + `setHash`;
  `showSeason` → `showView('historia','cinta')` + `setHash`; `setJugView`
  (shim), `cmpPreset`, `cmpFromPlayer`, `openGame`/`closeGame`, `hubAsk` and the
  glossary buttons all route through `showView`.
- **Layout-measurement audit:** no builder reads `offsetWidth`/`clientWidth`/
  `getBoundingClientRect` (charts are SVG `viewBox` + CSS scale), and all
  render fine while their view is `hidden` — no rebuild-on-show registry
  needed.
- **Boot default** writes `#inicio` to the URL (harmless; not
  `replaceState` — accepted).
- Harnesses: `scratchpad/view_router_harness.mjs` (menu→view integrity,
  `applyHash` redirect table, behavioural stub of `_showPanel`/`showView`/
  `syncSubnav`/`setHash`) + updated `ia_harness`, `mega_harness`,
  `mega_dom_harness`, `nav_motion_harness`.

### 8.3 — editorial blocks

Owner-approved 2026-09-11: hub = **1 lead + 4 secondary** (Historia lead;
Jugadores / Comparar / Juega / Archivo secondary); hero leads with the
**season-state countdown** + reigning champion; **"La liga ahora"** gets a
native `<details>` collapse on mobile.

#### 8.3a — `.ed-*` system + Inicio hero/hub (DONE)

- **Mini visuals** (`spark`, `sparkBars`, `dotgrid`) — viewBox-only SVG painted
  with `currentColor`, no layout read. `spark` = polyline (+ `opts.area` band,
  `opts.dot` endpoint); `sparkBars` = one `<rect>` per value (`opts.scale` for
  %); `dotgrid` = 3×3.
- **`.ed`** block — eyebrow · `.ed-row` (headline `.ed-stat` + `.ed-viz`) ·
  `.ed-phrase` · `.ed-ctx` · `.ed-act` (arrow, grows on hover). `edBlock(o)`
  builds one; `o.go` is the onclick (`showView(...)` / `cmpPreset(...)`).
- **`.edhub`** — CSS grid: `.ed-lead` spans the row, four secondary below
  (1col <620, 2col 620–1000, 4col ≥1000).
- **`buildHub`** rebuilt: `HUB` array + `hubNum` deleted. Five blocks —
  **lead** Historia (the profile club's title comb, or Bayamón the all-time
  leader; `sparkBars` of title years) → `#historia/cinta`; **Jugadores**
  (`PALL`/`PINDEX` count + `spark` of the top-7 career-points) → `#jugadores/buscar`;
  **Comparar** (`cmpMiniViz` two-bar, degrades to nothing on `file://`) →
  `cmpPreset`; **Juega** (`#<puzzleNo>` + `dotgrid`) → `#juega/cuadricula`;
  **Archivo** ("2011" + `sparkBars` of `COVERAGE`) → `#archivo/cobertura`.
- **`buildHero`** — adds an `.ed-eye` (today's date) and the champion's title
  `sparkBars` in the trophy foot; `t2` computed (bicampeonato / máximo / récord).
- **Inicio markup reordered:** `#heroBox` → `#hubTop` → `.hubsearch` →
  `#hubGrid` → `#hubFoot` → `#hubPrimer` (was: hub grid first, hero buried).
- **"La liga ahora"** — the 7 blocks wrapped in `<details class="liga">`
  (first `open`). Mobile: native disclosure, chevron via `::before`. Desktop
  ≥860px: `summary` styled as a plain header (`pointer-events:none`), and
  `.liga:not([open])>:not(summary){display:block}` forces all content visible.
  No JS — the Inicio replacement for the deleted `foldSections`.
- Harness: `scratchpad/edhub_harness.mjs`.

#### 8.3b — `showPlayer` + `showTeam` heros (pending)

Editorial hero above the existing card: one defining number + a `spark`
(player: per-season points from `web/data`; team: titles by year), then the
full strip / kv-list / roster unchanged.

#### 8.3c — section landings + `megaFeat` (pending)

The five `__landing` link grids → editorial cards (eyebrow + one line per
view). `megaFeat` blocks get the matching mini visual. All links `#section/view`.

## [ALTERNATIVES_REJECTED]

- **6 top-level** (Ahora as its own item). Owner merged Ahora into Inicio —
  the home page does double duty as the live view.
- **Keep the mobile top tab row.** Removed — the bottom bar is the mobile nav;
  addresses the tall-mobile-header thread.
- **Editorial treatment everywhere now.** Scoped to the 3 anchor surfaces;
  quick-fact pairs elsewhere are a later pass.
- **Scroll-anchor sub-navigation (commit 8.2).** Each mega-menu item / mobile
  chip scrolled to a heading within one long section page. Replaced in 8.2b by
  real per-view routes — the owner wanted each item to be its own focused
  page, and 8.3's editorial blocks needed real link targets.
- **Split `#sourcesBox` into its own `procedencia` view.** Kept inside
  `cobertura` for 8.2b (one `buildSources` innerHTML write; splitting means
  restructuring that builder). Revisit if the Archivo menu needs the
  granularity.
- **`history.replaceState` for in-app navigation.** Used `location.hash =`
  (a history entry per view) so Back walks the view trail — the "separate
  pages" feel the owner asked for.
