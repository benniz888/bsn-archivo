# Audit: BSN Archivo (`bsn_archivo.html`) — 1 September 2026

Method: parse check → static adversarial read against `audit-checklist.md` → headless Playwright
smoke tests on the failure paths → app-vs-CSV data cross-check → cross-device/theme sweep.
Harness: `smoke_bsn.py` (derived from `scripts/smoke_harness.py`), plus `crosscheck2.js`.

---

## Inventory

- **Source of truth:** `F` (32 franchises, each with `won[]` / `ru[]` year arrays), `POOL` (45 players),
  plus flat constant tables (`LEADERS`, `RECORDS`, `SCORING`, `HOF`, `ON_THIS_DAY`, `STANDINGS`, `RECENT`).
  `champOf` / `ruOf` are derived by inverting `F` at load — no season array is ever materialised.
- **Persists:** `localStorage` only, three keys under a `bsn:` prefix — `grid:YYYY-MM-DD` (today's board answers),
  `streak` (cur/best/played/last/totalScore), `club` (favourite franchise). `ST` wrapper falls back to an
  in-memory `MEM` object and never throws. No IndexedDB, no service worker, no sync, no crypto, no secrets.
- **Computed on the fly:** everything. Grid boards regenerate from `mulberry32(puzzleNo()*7919+n)`;
  only the *answers* are stored, never the board. Streak is the sole materialised aggregate.
- **State changes:** `submitGuess` → `drawBoard` + `saveDaily`; `choose`/`spin` → `drawPicks`;
  `newQuiz`/`guessQuiz` → `drawQuiz`; select-change handlers re-render their own panel. No global dispatch —
  each writer calls its own renderer, so there is no stale-view mechanism to fail.
- **Boot:** a flat, unguarded list of 16 builder calls at the bottom of the script.
- **Third-party:** Google Fonts (CSS + gstatic) and outbound links only. No API calls.

---

## Verdict

**Ship with caveats — for personal use. Do not pitch it in this state.**

Nothing here loses real data and nothing is a security hole, so there are no Criticals. But two things
would embarrass the build in front of an audience: **every crest and portrait in the app currently renders
a broken-image blob over the drawn SVG** (the drop-in image layer is dead, and `summary.md` records it as
working), and **a single malformed value in `localStorage` renders 11 of 16 sections empty.**

Single biggest risk: **the daily board persists answers with no schema version and no shape validation.**
Growing the game pool is the #1 item on your roadmap — the day you do it, every stored board restores its
old answers onto a differently-generated grid and reports a score that was never earned.

---

## Findings

### [HIGH] One malformed `localStorage` value blanks 11 of 16 sections

- **What:** If `bsn:grid:<today>` holds JSON that parses but isn't the expected shape, `loadOrStartDaily()`
  throws. `buildJuega()` is the 5th of 16 builder calls in a flat, unguarded sequence, so the throw kills
  the 11 that follow. Confirmed: ribbon 0 cells, season table 0 rows, grid 0 cells — a shell app with
  working nav and nothing inside it.
- **Repro:** Seed `localStorage['bsn:grid:2026-09-01'] = '{"board":[]}'` (no `ans` key) or `'{"ans":"nope"}'`
  and load. Both reproduce. Shapes that survived: `null`, a 2×2 `ans`, and `ans` holding unknown players.
- **Root cause:** `ST.json()` guards `JSON.parse` but nothing guards what comes out of it. `saved.ans.forEach`
  assumes an array; anything else throws past the wrapper. And because boot is one long comma-free run of
  statements, an exception anywhere is an exception everywhere after it. This is the same shape as a SQL
  script with no transaction boundaries — one bad row and the rest of the batch never executes.
- **Risk:** App appears broken with no error message. Recovery requires clearing site data, which no
  ordinary user will work out.
- **Fix:** Two lines in `loadOrStartDaily` — `if(saved && Array.isArray(saved.ans) && saved.ans.length===3)`
  before the restore loop. Then wrap each builder call in the boot sequence so one failure degrades one
  section instead of eleven.

### [HIGH] Stored answers have no schema stamp and their correct/incorrect verdict is trusted on restore

- **What:** `saveDaily` writes only `{ans}` — not the rows, columns, or the pool version the board was built
  from. `loadOrStartDaily` regenerates the board from the seed, then splices the saved answers back in
  **by position**, keeping each answer's stored `ok` flag verbatim. Nothing checks that the restored name
  is in `POOL`, that it actually fits the cell it lands in, or that the board is the same board.
- **Repro:** Seed `bsn:grid:<today>` with `{"ans":[[{"name":"Ghost Player","ok":true},null,null],[null,null,null],[null,null,null]]}`.
  The app boots, renders "Ghost Player" as a correct answer with a rarity score, and decrements `left` to 8.
  A fully forged 9-cell board restores as a finished 9/9.
- **Root cause:** The classic undeclared-version-field failure. `ok` is a *verdict about a board*, but it's
  stored as if it were a *fact about a player*. As long as the board never changes, the two are
  indistinguishable — which is exactly why this passes every test until the pool changes.
- **Risk:** Silently wrong score, and a wrong `totalScore`/`played` written into the streak record.
  Near-certain to fire: "grow the game pool" is your top roadmap item, and the seeded shuffle draws from
  `POOL`, so adding one player re-deals every historical board.
- **Fix:** Store `{v:1, rows, cols, ans}`. On load, restore only if `v` matches and the saved `rows`/`cols`
  equal the regenerated ones; otherwise discard and start clean. Recompute `ok` from `fits()` rather than
  trusting the stored flag.

### [HIGH] Career-leaders row contradicts its own arithmetic, and the wrong number feeds both games

- **What:** Assists rank 8 — Raymond Dalmau, 2,302 assists in 537 games, shown as **5.1 per game**.
  2302 ÷ 537 = 4.3. All nine other assist rows check out to ±0.05, and Dalmau's own points and rebounds
  rows both reconcile against the same 537 games. This one number is the only self-contradiction in the
  entire dataset, and the table displays total, games, and per-game side by side, so it's visible.
- **Repro:** `node crosscheck2.js` — internal check `LEADERS per_game vs total/gp`. Also present in
  `bsn_career_leaders.csv`, so it is inherited from the source, not introduced by the app.
- **Root cause:** Source data, shipped unflagged. Either the total or the games figure is wrong for this
  row and Wikipedia never reconciled them.
- **Risk:** Three downstream effects, all silent. (1) In "per game" mode the bar chart ranks him 4th
  instead of 8th. (2) `POOL` carries `apg:5.1`, which clears the `>=4.5` "real distributor" threshold in
  34-0 and awards a +7% roster bonus that 4.3 would not. (3) The ¿Quién soy? clue states 5.1 as fact.
  For an app whose entire pitch is that it shows its gaps rather than smoothing them, an unflagged
  contradiction is the worst possible defect.
- **Fix:** Cheapest honest option — add `1966–1985` Dalmau to `NOTES`-style flagging in the leaders table
  ("total and per-game disagree; source unreconciled") and set `POOL` `apg:null` so the games stop
  treating it as verified. Real fix is one line in the Wayback/newspaper pass.

### [HIGH] The image drop-in layer does not work; every crest and portrait renders a broken-image blob

- **What:** `imgTry()` emits `onerror="...var c=["img/crest/bay.png","img/crest/bay.svg",...];..."`.
  The double quotes from `JSON.stringify` terminate the double-quoted HTML attribute. Chrome truncates
  `onerror` to its first 30 characters — `var n=this.dataset.i|0;var c=[` — and parses the rest of the
  array as five junk boolean attributes on the `<img>`.
- **Repro:** Open the app with the `img/` folders empty (your current shipped state), go to Franchises,
  let images settle. Measured: **53 images, 52 broken, 0 hidden, 52 `SyntaxError: Unexpected end of input`
  page errors.** Screenshot shows clipped grey alt text ("Vaqueros de Bayamón logo") sitting over the
  crest abbreviation on every card. Second test: dropped a real `img/crest/bay.svg` in place — `src`
  stayed on `bay.png`, `data-i` stayed `0`, image stayed broken. Only `.png` will ever load.
- **Root cause:** A string containing `"` interpolated into a `"`-delimited attribute. The browser is
  doing exactly what the markup says; the markup is malformed. Both halves of the feature die at once —
  the extension fallback chain and the `display='none'` that was supposed to reveal the SVG beneath.
- **Risk:** No data harm, but it's on every screen, it's on the app's signature visual element, and
  `summary.md` records "Zero images = perfect render", which is false. The documented
  "drop a logo in, no code change" promise silently only honours the first extension.
- **Fix:** Stop putting code in the attribute. Emit the `<img>` with `data-chain` holding the
  comma-joined paths and no `onerror`, then attach one delegated `error` listener (capture phase) in JS
  that advances the chain and hides on exhaustion. One handler for all 53 images, no quoting problem.

### [LOW] Streak resets on the day after a spring-forward DST change

- **What:** `saveDaily` computes yesterday as `new Date(Date.now()-86400000)`. On the day after a
  spring-forward the previous local day is only 23 hours long, so subtracting a fixed 24 hours from a
  time before 01:00 lands two calendar days back.
- **Repro:** `America/New_York` at 2026-03-09 00:30 → `todayStamp` 2026-03-09, computed yesterday
  2026-03-07 (gap of 2). Same in `Pacific/Auckland` on 2026-09-28. `America/Puerto_Rico` is correct
  because PR does not observe DST.
- **Root cause:** Doing calendar arithmetic in milliseconds. A day is not always 86,400,000 ms.
- **Risk:** A user in a DST zone who finishes between midnight and 01:00 that morning loses their streak.
  Zero impact in Puerto Rico today; matters the moment this ships beyond the island.
- **Fix:** `const y=new Date(); y.setDate(y.getDate()-1);` — `setDate` is DST-aware.

### [LOW] `ST.set` swallows write failures, so a failed save looks like a successful one

- **What:** `set()` writes to `MEM` first, then attempts `localStorage` inside a bare `catch(e){}`.
  If the write fails (quota, Safari private mode, a locked-down container), the session behaves normally
  and the data silently vanishes on reload.
- **Root cause:** The memory fallback is doing double duty — it's both the sandbox fallback *and* the
  error handler, so a genuine failure is indistinguishable from a normal sandboxed run.
- **Risk:** Low today; payloads are a few hundred bytes and quota is megabytes. Rises if you ever persist
  more.
- **Fix:** Track whether the last `localStorage` write succeeded and show a one-line note on the Juega tab
  when it hasn't ("progress won't survive a reload in this browser").

### [LOW] "Here is the rest of {month}" shows events from other months

- **What:** When the current month has no dated events, `buildToday` prints "…here is the rest of January"
  and then lists the five earliest events overall — April, May, September.
- **Repro:** Load with the clock at 2027-01-15 or 2027-06-10. `ON_THIS_DAY` covers months 4, 5, 7, 8, 9,
  10 and 12 only, so this fires for five months of the year.
- **Root cause:** The copy is written for the `near.length` branch but the fallback branch reuses it.
- **Fix:** Separate string for the fallback: "Nothing recorded in {month}. The earliest events in the
  archive:".

### [LOW] The one season the archive most wants to explain is unsearchable

- **What:** `buildSearch` indexes a season only `if(champOf[y])`, so 1953 — the documented gap, with its
  own note in the season table and its own entry in Sources — returns "Nothing in the archive matches that."
- **Fix:** Index every year in `YEARS`; use `NOTES[y]` as the subtitle when there's no champion.

### [LOW] Career-leaders bars and table disagree on ordering

- **What:** Switching the mode selector to "per game" re-sorts `#leadBars` but `#leadBody` always renders
  in the original total-based order. Both are on screen at once, so rank 1 in the chart is row 4 in the
  table directly beneath it.
- **Fix:** Sort both from the same array, or label the table "by career total" so the difference is stated.

### [LOW] "Rarity" describes the cell, not the pick

- **What:** `Math.round(GB.sol[i][j].length/POOL.length*100)` is the share of the pool that fits *the cell*.
  Every player who solves that cell sees the same number, whether they named the only valid answer or the
  most obvious of five. Immaculate Grid's rarity is per-pick and is what makes score-sharing interesting.
- **Note:** This is a product question, not a defect — the number is directionally correct and not lying.
  Flagging it for `app-critic`, not for a fix here.

---

## Cleared

Tested and solid:

- **Reload durability.** Played 4 cells, reloaded: identical board, identical answers, `left` correct at 5.
- **No double-count on the streak.** Completed a board, reloaded, toggled Daily→Practice→Daily.
  `played` stayed 1, `left` stayed 0, `used` stayed 9. The `st.last!==todayStamp()` guard holds.
- **Practice mode is fully isolated.** Nine picks in Practice wrote nothing to the daily key and never
  created a `bsn:streak` record.
- **Parse and runtime.** `node --check` clean. Across a full sweep — all 13 tabs, both HOF sorts, both
  leaders selectors, all 32 franchise cards, 40 complete 34-0 drafts, 60 quiz rounds, standings selector,
  season filters — **zero page errors other than the `imgTry` SyntaxError**.
- **Data integrity vs. the CSVs.** All 30 career-leader rows, all 11 records, all 26 scoring champions, and
  all 96 champion/runner-up pairs match their source CSV exactly. Two intentional divergences:
  Bayamón 18 vs 17 (the provisional 2026 title) and San Germán 13 vs 14 (the 1942–43 fold) — both
  disclosed in the Sources tab, verified in the rendered text.
- **`F` internal consistency.** 97 seasons, 96 champions, 94 runners-up, zero duplicate champions, zero
  duplicate runners-up, no club listed as its own runner-up, no out-of-range years. 1953's ribbon cell is
  correctly `disabled`, so `showSeason(1953)` — which would throw on `F[undefined].name` — is unreachable.
- **Null ≠ zero.** No `POOL` player carries a `0` where a `null` belongs. `finishDraft` counts and reports
  the missing categories rather than scoring them as zero.
- **Boundary inputs.** Empty search, 1-character search, no-match search, unicode and accented names
  (`norm()` strips diacritics correctly — "dalmau" returns both Dalmaus), 34-0 pool exhaustion, quiz
  clue exhaustion. All handled.
- **XSS.** All interpolation runs through `esc()` or `textContent`. `<img src=x onerror=alert(1)>` typed
  into global search injected zero nodes.
- **Secrets.** Nothing matching key/token/secret/password/Bearer/supabase anywhere in the file.
- **Chart bounds.** All 21 plotted ppg values (21.9–35.5) fall inside the hardcoded 20–36 axis.
- **Standings arithmetic.** 2009: 11 rows, every team's W+L = 30, matching the declared game count.
- **Offline.** No network dependency but Google Fonts, which degrades to the declared system stack.
- **Cross-device.** Desktop 1280, tablet 834, mobile 390 and 360, light and dark: zero horizontal
  overflow, zero touch targets under 32px, no clipped or unreachable controls. The 12 "offscreen" nav
  buttons at mobile width are inside `.navscroll` with `overflow-x:auto` — intended horizontal scroll,
  not a break.

## Skipped

- **Crypto / sync confidentiality / key handling** — no crypto, no Supabase, no network writes.
- **IndexedDB ↔ localStorage reconciliation, eviction, `navigator.storage.persist()`** — localStorage only,
  three small keys.
- **Service-worker cache staleness, offline sync-resume, PWA install** — no service worker, no manifest.
- **Money integrity, split correctness, float drift** — no monetary values anywhere.
- **Recurring-item materialisation** — nothing recurs; the only date-derived state is one board per day,
  computed not stored.
- **Stale-view-after-dispatch** — there is no dispatch layer; each writer calls its own renderer directly,
  and the full control sweep confirmed first-render and post-change correctness on every panel.

---

# Fix log — all ten items closed, 2 September 2026

Every finding above has been fixed and re-verified. `reverify2.py` reproduces the whole table below.

| # | Sev | Finding | Fix | Verified by |
|---|---|---|---|---|
| 1 | HIGH | Malformed storage blanks 11 of 16 sections | Shape guard in `loadOrStartDaily`; boot sequence is now an array walked with per-builder `try/catch` that logs the failing function name | 8 hostile shapes all boot to ribbon 97, seasons 97, teams 32, grid 9, 0 errors |
| 2 | HIGH | No schema stamp; stored verdicts trusted | `{v,rows,cols,ans}` written; restore requires `v===GRID_SCHEMA` and matching axes; `ok` recomputed from `fits()`; unknown or repeated names dropped | Stale-axes save discarded with an on-screen notice; forged `ok:true` recomputed to `false`; unknown name dropped |
| 3 | HIGH | Dalmau assists row contradicts its own arithmetic | Dagger + footnote in the leaders table, row in Sources "Known gaps", `POOL` `apg:null` | `apg` is `null`; the `>=4.5` distributor bonus no longer trips; footnote renders |
| 4 | HIGH | Image drop-in layer dead | Chain moved to `data-chain`; one capture-phase `error` listener walks it and hides on exhaustion | `bay.svg` loads with only `.svg` present (`data-i=1`); no-file crest walks to `data-i=3` then hides; 52 → 0 broken-visible; 52 → 0 page errors |
| 5 | LOW | Streak resets after spring-forward | `setDate(getDate()-1)` instead of `-86400000` | New York, Auckland, Puerto Rico, and the fall-back case all return a 1-day gap |
| 6 | LOW | `ST.set` swallowed write failures | `ST.wrote` flag; `drawStorageNote()` renders a warning under the streak strip | With `setItem` forced to throw: `ST.wrote:false` and the notice appears |
| 7 | LOW | "Rest of {month}" listed other months | Separate copy for the no-events-this-month branch | January and June now read "Nothing in the archive is dated to {month} at all" |
| 8 | LOW | 1953 unsearchable | Index every year; `showSeason` handles a season with no champion | Search returns 1953; readout reads "This season is a gap in the archive, not a blank" |
| 9 | LOW | Bars and table sorted differently | Table renders from the same sorted `rows` array | Order matches in both career-total and per-game modes |
| 10 | LOW | "Rarity" mislabelled a per-cell figure | Relabelled "N of 45 fit" | Cell reads "1 of 45 fit" |

## Post-fix state

- `node --check` clean.
- **Zero page errors** across the full sweep: 13 tabs, 32 franchise cards, every ribbon cell, 20 drafts, 40 quiz rounds, all three leaders selectors, both HOF sorts. Was 152 before the audit.
- No empty sections under any tested storage state.
- Desktop 1280, tablet 834, mobile 390 and 360, light and dark: zero horizontal overflow, zero broken visible images, zero touch targets under 32px.
- CSV cross-check: the only remaining divergences are the three documented ones — Bayamón 18 vs 17 (provisional 2026 title), San Germán 13 vs 14 (1942–43 fold), Dalmau's assists (now flagged in two places) — plus `POOL apg=null`, which is deliberate.

## Not fixed, because fixing them would mean inventing data

- **1953** still has no champion. **1945** is still disputed between the two Wikipedias. **San Germán** still shows 13. **2026** is still provisional. All four are disclosed in the UI; they close with the Wayback pull, not with code.
- **True per-pick rarity** in La Cuadrícula needs the pool to be much larger than 45. That is a product change — `app-critic`, not this pass.

---

# Second pass — three more, found by auditing what the first pass skipped

Asked whether anything remained, I went looking in the areas the first audit had not touched:
multi-day time behaviour, storage growth over years, and accessibility. Three real issues.

### [MEDIUM] A tab left open past midnight served the wrong day's board and lost the answers

- **What:** `GB` was built once at page load, but `todayStamp()` and `puzzleNo()` kept moving.
  Past midnight the grid on screen was still yesterday's while the streak strip read the new
  puzzle number, and `saveDaily` wrote those answers under **today's** key carrying **yesterday's**
  axes. The #2 fix then correctly discarded them on the next load — and blamed the pool.
- **Repro:** Freeze the clock at 2026-09-02 23:55, answer three cells, advance fifteen minutes,
  answer two more. Before: `puzzle 246`, `rows que,car,san` (day 245's axes), both keys written.
- **Fix:** The board now carries `GB.day`. `checkRollover()` re-deals when the date changes, runs
  before every guess and on a 60-second interval, and the notice states the real reason.
- **Verified:** After midnight the axes change to day 246's, the new answer lands on the new board,
  and yesterday's three answers stay under yesterday's key.

### [LOW] Daily board keys accumulated forever and were never cleaned up

- **What:** Only today's `bsn:grid:YYYY-MM-DD` is ever read, but every day written one and nothing
  removed it. Seeded 400 days: all 400 survived a full session. Roughly 50KB at 400 days, 460KB
  over a decade — under quota, but unbounded and growing.
- **Fix:** `pruneOldBoards()` on load keeps today and yesterday, drops the rest.
- **Verified:** 400 seeded keys → 0. Today's key survives a played session and restores on reload.

### [LOW] Nothing was announced to screen readers

- **What:** Zero `aria-live` regions. Guess verdicts, quiz results, draft results, search results and
  the season readout all updated silently.
- **Fix:** `role="status"` and `aria-live="polite"` on `#gMsg`, `#qMsg`, `#dResult`, `#gsRes`, `#readout`.
- **Note:** Images all have alt text and every button has an accessible name, so this was the gap.
  A full accessibility pass — focus management, contrast ratios, keyboard traversal of the grid —
  has still not been done.

## What remains genuinely unaudited

- **Whether the data is true.** Every check so far compared the app to its own CSVs. Nothing has been
  checked against reality. All 97 champions, 30 leader rows, 26 scoring titles, the HOF figures, arena
  capacities and the 34-0 season could be wrong and this audit would still report clean.
- **Any browser but Chromium.** No WebKit, no Firefox. Safari private mode throws on `localStorage`;
  the #6 fix should handle it but has not been tested there.
- **Any real device.** Viewport emulation is not an iPhone — safe-area insets, dynamic type and
  momentum scroll are untested.
- **A full accessibility audit,** beyond the live regions above.
- **Performance.** 134KB, 53 inline SVG crests, a 97-row table with no virtualisation. Never profiled.
