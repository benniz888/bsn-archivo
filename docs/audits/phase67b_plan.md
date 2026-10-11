# PHASE_67B — La Temporada Perfecta: difficulty plan (measure-first, no game change)

Source: `web/js/games.js` L442-739 (draft game), POOL assembled at runtime in `web/index.html` L756-910.
Simulator: scratchpad `sim.mjs` (seeded mulberry32, seed 12345, 10,000 runs per strategy per config; POOL dumped from the live page: 376 players, 33 club keys, K=116, S=40).

## 1. Current rules (as coded)

- Draft 5 players into PG/SG/SF/PF/C. Each spin picks a random club x decade (1950s-2020s), weighted by min(candidates, 6), only among pairs with at least one unused player who fits an open slot.
- 2 free re-spins ("pases"). Player must fit the chosen slot (G fills PG/SG, F fills SF/PF, F/C fills PF/C, unrecorded position fits anywhere). Max 3 refuerzos (`import` tag). No minimum nativos.
- All stats and tags are visible on the pick cards; candidates are sorted by `rate()` best-first (so "take the top card" is the greedy strategy, handed to the player).
- `rate(p)` = 8 + tag values (mvp 9, scoring 7, 10k 5, legend 5, nba 3, champion 2) + 1.5*(ppg-12)+ + 1.1*(rpg-5)+ + 1.6*(apg-2.5)+ + 3*(spg-0.8)+ + 3*(bpg-0.5)+.
- Bonuses: >=3 nativos +8; roster spans <=2 clubs +9; spans <=2 decades +5; >=2 MVP +7; five positions filled +6.
- Wins = round(34 * logistic((total-116)/40)), total = sum(rate) + bonuses. **34-0 requires total >= 284.2.**

## 2. Key finding: the premise does not hold for "perfect"; it holds for "30+"

- A perfect season is **mathematically unreachable today**. The best legal roster in the whole pool, ignoring spins entirely (Dalmau, Morales, Torres, Terry, Frazer), totals 271 = 33-1. Needs 284.
- Measured perfect rate is 0.00% for all three strategies. What is easy is 30+ wins: greedy 21%, expert 44%.
- So lowering the perfect rate is not the problem; making 34-0 *reachable but rare* is. The target (expert 1-5%, greedy <0.5%) is supportable by the data, but only by moving the 34-0 threshold down; no rule tweak alone gets there.

## 3. Current distribution (wins, 10,000 runs each)

| Strategy | mean | median | p10 | p90 | max | 30+ wins | 34-0 |
|---|---|---|---|---|---|---|---|
| (a) random-legal | 18.4 | 18 | 11 | 26 | 33 | 2.0% | 0.00% |
| (b) greedy (top visible `rate`, skips only if no legal option) | 26.6 | 27 | 22 | 31 | 33 | 21.1% | 0.00% |
| (c) expert (full knowledge of rate and bonuses, skips when best marginal < 30) | 28.5 | 29 | 25 | 32 | 33 | 44.3% | 0.00% |

Total-score tails (base config): random p99 199 / max 244; greedy p99 230 / max 257; expert p99 242 / max 266.
Caveat: "expert" is a heuristic (marginal-value picks plus a tuned skip threshold), not a proven optimum, so a real optimal player does somewhat better. Treat expert rates as a floor.

## 4. Options (predicted by re-running the simulator)

Perfect-rate vs threshold T (base config, 34-0 awarded iff total >= T): T=235: expert 2.33 / greedy 0.57 / random 0.03; T=240: 1.31 / 0.30 / 0.02; T=245: 0.63 / 0.14 / 0.00; T=250: 0.36 / 0.10 / 0.00 (%).

| Option | Change | Strategy | mean | med | p10 | p90 | 30+ | 34-0 |
|---|---|---|---|---|---|---|---|---|
| **A. Umbral** | 34-0 iff total >= 240 (else capped at 33). Curve unchanged. | random | 18.4 | 18 | 11 | 26 | 2.0% | 0.02% |
| | | greedy | 26.6 | 27 | 22 | 31 | 21.1% | 0.30% |
| | | expert | 28.5 | 29 | 25 | 32 | 44.3% | 1.31% |
| **B. Vista parcial** | stat lines hidden on cards until placed (position, club, tags stay); 1 pase; T=235 | random | 18.4 | 18 | 11 | 26 | 2.0% | 0.03% |
| | | greedy (sees tags only) | 24.3 | 25 | 18 | 30 | 12.7% | 0.33% |
| | | expert | 27.7 | 28 | 23 | 31 | 33.7% | 1.19% |
| **C. Umbral + curva más dura** | A plus K 116->130, S 40->36 | random | 15.7 | 15 | 8 | 24 | 1.1% | 0.02% |
| | | greedy | 25.1 | 25 | 19 | 30 | 14.8% | 0.30% |
| | | expert | 27.5 | 28 | 23 | 31 | 35.6% | 1.31% |

Also measured, rejected: pases 2->1 alone barely moves greedy/random (they rarely use passes) and cuts expert 34-0 to 0.73% at T=240; pases 0 makes expert == greedy (removes the skill gap); max refuerzos 3->2 changes nothing measurable and rewrites a league rule (not recommended); removing bonuses lowers everything ~1.5 wins but doesn't separate skill levels.

### UI and string changes needed
- **A**: no UI. One constant plus a cap in `finishDraft`. Optional: show the threshold in the scoreline ("Para 34-0 hacen falta 240"). Note 33-1 becomes unreachable at the top (totals 240+ jump 32 -> 34); acceptable but should be known.
- **B**: hide `ppg/rpg/apg/PJ` line on pick cards (still shown on court after placing); pass counter 2 -> 1 in the header and button. New/changed strings (to `docs/strings_pending_phase67b.md`): "Las cifras se revelan al colocar" (card hint), header text "· 1 pase". Biggest design change: players can no longer compare numbers, so it tests memory instead of reading.
- **C**: same as A; curve constants only. No new strings.

## 5. Recommendation: **C**

It is the only option that makes both ends of the complaint true with a one-constant change: 34-0 becomes reachable (expert ~1.3%, greedy 0.3%, random ~0) and 30+ drops from 21% to 15% for greedy and 44% to 36% for expert, random median falls to 15-19 (average player usually falls short). No UI redesign, no new Spanish strings. B widens the skill gap most (greedy 12.7% vs expert 33.7% for 30+) but costs a visible UI change and removes information from a game whose cards currently teach players the stats; hold it as a follow-up if C feels too easy to the owner.

## 6. Open questions for the owner
1. Verdict string at 34-0 says "Nadie lo ha hecho de verdad — el récord real es 29-5, Bayamón 1993." This record claim is not sourced in this plan. Verify against the archive before keeping it, since a 34-0 result will now actually display it. Also "Mejor que cualquier temporada real" (30+) depends on it.
2. Accept 33-1 disappearing as an outcome, or add a proper curve (e.g. 33 for 232-239) so the top steps are 32/33/34?
3. Target tolerance: is expert ~1.3% (heuristic floor, true optimum maybe 2-3%) the right center, or move T to 235 (expert 2.3%, greedy 0.57%, which breaks the "greedy <0.5%" target)?
4. The random 0.02% is 2 runs in 10,000, a long-shot luck outlier (~0), not zero.
