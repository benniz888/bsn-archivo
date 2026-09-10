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
   to the section, which opens with its featured block + a chip rail of
   sub-sections — the same content as the desktop mega-panel.

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

### 8.2 — mega-menu (pending)

Desktop hover/focus dropdown per nav item — grouped link columns + one featured
block; mouse-leave / Esc / scroll dismiss; keyboard nav. Mobile: each section
opens with its featured block + a restyled `foldSections` chip rail.

### 8.3 — editorial blocks (pending)

`.ed-*` CSS + a sparkline SVG helper; rebuild `buildHub` + the Inicio hero;
rebuild `showPlayer` and `showTeam` heros (mockups C and B from the proposal).

## [ALTERNATIVES_REJECTED]

- **6 top-level** (Ahora as its own item). Owner merged Ahora into Inicio —
  the home page does double duty as the live view.
- **Keep the mobile top tab row.** Removed — the bottom bar is the mobile nav;
  addresses the tall-mobile-header thread.
- **Editorial treatment everywhere now.** Scoped to the 3 anchor surfaces;
  quick-fact pairs elsewhere are a later pass.
