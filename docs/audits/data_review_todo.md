# Data review to-do (PHASE_62 follow-ups)

Nothing here was applied to the game. Each item needs a source check before any tag or club is added (PC1, D1, D5).

## Disputed award tags

| Player | Tag | Conflict |
|---|---|---|
| Larry Ayuso | scoring | `scoring_titles.json` 2002 row says ELIAS AYUSO (id 574); pool says Larry. |
| Carlos Bermúdez | mvp | `mvp.json` 1978 row says Charlie Bermudez (id 334); pool says Carlos. |
| Mario Butler | mvp | `mvp.json` 1988 vs Hall-of-Fame card `mvp:0` (data.js). |
| Rubén Rodríguez | mvp | `mvp.json` 1979 vs Hall-of-Fame card `mvp:0`. |
| Neftalí Rivera | mvp | `mvp.json` 1973 vs Hall-of-Fame card `mvp:0`. |
| Rolando Frazer | mvp | `mvp.json` 1981 vs Hall-of-Fame card `mvp:0`. |

Also not added (no effect on any cell, players have no club): Ramón Rivas MVP 1989, Roberto Ríos MVP 1995.

## Players with no club list (`c: []`)

They cannot fill any club cell, and a guess for one is now reported as "sin datos" and is free. Needs source data for their clubs.

16 players: Bobby Joe Hatton, Butch Lee, Carlos Bermúdez, Daniel Santiago, Federico López, Javier Antonio Colón, Jeffrion Aubry, Jerome Mincy, José Quiñones, Lee Benson, Mario Butler, Ramón Rivas, Roberto Ríos, Rubén Rodríguez, Wilfredo Pagán, Ángel «Munch» Cruz.

## Other

- Autocomplete (`drawSugg`) matches with `norm()` only, so `Jose Ortiz` gives no suggestion although submitting it works.
- Alamo / Candido Fret and Reyes / Hector are archive-index same-name players outside the 376-player game pool.
