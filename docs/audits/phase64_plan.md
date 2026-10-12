# PHASE_64_INICIO — plan (no code written)

Status: PLAN ONLY, awaiting owner approval. Branch `redesign-v3`. No commit, no push, nothing staged.
Refs read: 01_master_plan.md, 05_page_specs.md (Inicio), 02_brand_and_logo_spec.md, screenshots `Inicio/computer view 1`, `phone view tabs`.

## 1. What Inicio has today (measured in code)
`#heroBox` (date eyebrow, headline, dek, status line, note, 3 stat tiles) → `#hubTop` (club card or "Hola") →
`#hubGrid` (lead "Historia · tu club" card + Jugadores, Comparar, Juega, Archivo) → `#hubFoot` note →
`#hubChamps` (Últimos campeones) → `#hubPrimer` (¿Qué es el BSN?) → "La liga ahora" header + 6 accordions
(Lo próximo, Final Brava 2026, Finales anteriores, Posiciones 2026, Líderes 2026, Canales oficiales). About 15 blocks.

## 2. Keep / cut / change
| Block | Decision |
|---|---|
| hero headline + dek + status line | KEEP, slimmed. Date eyebrow stays. |
| hero note + 3 stat tiles | CUT (the stats repeat what the cards and Historia show). |
| `#hubTop` club card ("Hola, X" + crest) | CHANGE: folded into the hero card as its top row; no separate card. |
| Lead card "Historia · tu club" (cinta) | CHANGE: becomes THE hero. Cinta spans the full card width with a year axis and decade labels; dynasties solid, gaps as gaps. |
| 4 entry cards (Jugadores, Comparar, Juega, Archivo) | KEEP as one row of four. Drop the filler `ctx` sentence on each so they stop being text-heavy (strings below). |
| `#hubFoot` note | CUT (the club pill already explains itself). |
| Últimos campeones | KEEP (content block 1). |
| Lo próximo (calendar next) | KEEP (content block 2), open. |
| Final Brava, Finales anteriores, Posiciones, Líderes, Canales | CHANGE: one collapsed disclosure "Más de la liga ahora" at the bottom, content untouched. They live only on Inicio today, so cutting them would delete content. DECISION FOR OWNER: (a) this disclosure, or (b) leave each where it is until Historia/Archivo phases. Recommend (a). |
| Primer "¿Qué es el BSN?" | CHANGE: shows as the existing small link only; no big card on first view. |
| "La liga ahora" phead + lede | CUT (replaced by the disclosure summary). |
Result: header, hero, 4 cards, 2 blocks, 1 disclosure.

## 3. Layout
Desktop (>=1000): slim headline row, then hero card (crest + "N títulos de X, de A a B" left, full-width cinta with axis below),
four cards in one row, Últimos campeones and Lo próximo side by side, disclosure full width.
Phone (390): headline, hero card (cinta scrolls horizontally if the axis needs room, decade labels every 2nd), 2x2 cards (each >=44px, whole card is the target),
the two blocks stacked, disclosure. Bottom tabs unchanged.

## 4. Piculín content removed from Inicio
Found by case-insensitive search of `web/`:
- REMOVED: search placeholder `Prueba: cuándo murió Piculín · 1971 · títulos de Bayamón` (`index.html:99`), its aria-label (`index.html:100`), and both strings in `syncSearchPlaceholder()` (`js/init.js:81-82`). This is the "prueba" item.
- STAYS (not Inicio): player page, roster/index entries (`data.js:220,287,466`; `tabs.js:110,187,3496,3501,3679`; `index.html:336,551,593,699`).
- FLAG: `ASK_EXAMPLES[0]` "¿Cuándo murió Piculín?" (`tabs.js:3419`) is a chip in Archivo > Preguntar, not Inicio. Spec says remove only Inicio content, so it stays unless you say otherwise.
- Also stays: code comments naming him (`init.js:67`, `games.js:350`, `tabs.js:4974`).

## 5. Search placeholder (needs approval; names no player)
Desktop: `Prueba: títulos de Bayamón · 1971`
Phone (<640px): `Prueba: títulos de Bayamón`
aria-label: `Buscar en el archivo. Ejemplo: títulos de Bayamón o 1971.`
Both queries already work (they are in `ASK_EXAMPLES`). A club name, not a person.

## 6. Favorite-club ordering (local only)
Uses the existing profile in localStorage (`bsn:profile`, `club` key, set from the header pill / Equipos). No account, no network.
- Club chosen: hero = that club's cinta and title count; "Últimos campeones" shows first and highlights that club's years; if the club has no titles the hero says so (existing text) and still shows its cinta of zeros as gaps.
- No club: hero = Bayamón (all-time leader, computed, as today); blocks in default order.
- "Sigue donde lo dejaste": last 3 viewed players/clubs in localStorage (`bsn:recent`), shown as one row under the hero only when it has entries. Nothing stored until the person opens one. Cleared by the existing profile reset.
If storage is blocked, falls back to default order (the app's `ST` layer already handles that).

## 7. Your requests, covered
- Less clutter: section 2 (15 blocks -> 7).
- Blue highlight instead of orange outline: PHASE_61 already set `--focus` to site blue and `.ed:hover` uses blue. Step 2 sweeps every Inicio selector (cards, pill, disclosure, search, chips) for orange outline/border and fixes any left; orange stays on data (bars, sparklines, link text).
- Phone tab indicator following the route: PHASE_61 already syncs `#bottombar` from the route in `showTab`. Step 2 verifies on tap, load with hash, and back/forward in Chromium and WebKit, and adds the translateX slide (reduced-motion off) only if the current mark is not already moving with the active tab.

## 8. Build constraints
Closures only (IIFEs inside existing functions), 0 new top-level names (inventory stays 476). No emoji. Existing `🔥` appears only in comments at `tabs.js:3014,3028`; will check the UI renders none.
Verify Chromium + WebKit, 390/1000, dark + light, 0 console errors; suite baseline 704 passed, 1 xfailed, 1 known failure.

## 9. Questions
1. Section 2 disclosure: (a) or (b)?
2. Placeholder text in section 5 OK?
3. Keep the Archivo chip about Piculín?
