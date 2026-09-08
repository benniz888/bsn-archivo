# BSN Historical Data — First Pull

Everything below was extracted by hand from public sources today. It is a starting corpus and a source map, not a finished database. Every row is `confidence = single-source` until verified against a second source.

---

## THE MAIN FINDING

Wikipedia's BSN Scoring Champion article cites its numbers to the **old bsnpr.com stats engine**, at this URL pattern:

```
https://www.bsnpr.com/estadisticas/lideres.asp?anio=YYYY&liga=1&serie=1&grupo=BS26&B1=Ver
```

The citations run from **`anio=1957` through `anio=2004`**, all retrieved in July 2021.

That means the league's own site published a season-leaders database going back to **1957** — thirteen years earlier than any aggregator, and 54 years further back than RealGM. There was also a `estadisticas/campeonatos.asp` endpoint for championships.

I confirmed those URLs now return 404. The site was rebuilt as a JavaScript app and the ASP-era pages are gone from the live web.

**They should still be in the Wayback Machine.** This is the single highest-value action in the whole project:

1. Query the CDX API for everything archived under the old stats path:
   ```
   http://web.archive.org/cdx/search/cdx?url=bsnpr.com/estadisticas*&output=json&limit=50000&collapse=urlkey
   ```
2. That returns every archived URL plus timestamps. Filter for `lideres.asp` and note which `anio` values were captured.
3. Fetch each snapshot with the `id_` suffix to get raw HTML without the archive chrome:
   ```
   https://web.archive.org/web/{timestamp}id_/{original_url}
   ```
4. Parse the tables. These are old-school server-rendered HTML tables — trivial to parse with pandas `read_html`.

If the crawl coverage is good, this collapses roughly half of Phase 4 into a weekend. If coverage is patchy, you still learn exactly which seasons you need to chase in newspaper archives, which is worth knowing before you set foot in a library.

Do this before anything else. Archived pages don't get more archived over time.

---

## FILES

### `bsn_champions_by_season.csv` — 96 rows, 1930–2025
Season, champion, runner-up, confidence, notes.

Reconstructed by inverting Wikipedia's per-franchise "years won / years runner-up" table into a season-indexed view. Coverage:
- **95 of 96 seasons** have a champion (99%)
- **93 of 96** have both champion and runner-up (97%)
- `1953` — no champion listed. Either no season was held, or Wikipedia's franchise table is incomplete. Verify.
- `2024` — champion known (Criollos de Caguas), runner-up missing from the source table. It was Osos de Manatí; left blank rather than filled from memory. Confirm and patch.

**Known conflict, unresolved:** for 1945, the English Wikipedia franchise table credits **Capitalinos de San Juan**, while the Spanish Wikipedia champions list credits **Santos de San Juan**. Both list Gallitos de la UPR as runner-up. These may be the same club under different names or a genuine error. The file currently carries the English version. Flag it; don't quietly pick one.

Also note the `1942-1943` season, which the Spanish source lists separately from `1942` (San Germán won both). This reconstruction folds them into 1942, so the season count is off by one against sources that split them. Your schema needs a season key that can represent a split-year season.

### `bsn_career_leaders.csv` — 30 rows
All-time top 10 in points, rebounds, and assists, each with total, games played, per-game average, position, and career span. This is the deepest per-player data available anywhere without archival work, and it reaches back to careers beginning in **1957** (Teófilo Cruz).

Caveat: Wikipedia flags these tables as roughly five years stale. Christian Dalmau and Wilfredo Pagán played past the apparent cutoff. Treat as a floor, not a current standing.

### `bsn_scoring_champions.csv` — 26 rows, 1966–1991
Season scoring leaders. Note the metric changes: through 1969–70 the title went to the **total points** leader, and from 1970–71 onward to the **points-per-game** leader. The `metric` column preserves this, which matters — comparing 602 total points to 22.4 ppg is meaningless.

This is partial. The source table starts at 1956–57 and runs to the present; I captured the middle. The rest is a straightforward fetch of the same Wikipedia article's full table.

Highlight: Georgie Torres won it seven times (1977, 1978, 1979, 1984, 1985, 1986, 1987), peaking at 35.5 ppg in 1987.

### `bsn_records.csv` — 11 rows
League records with holder, value, season, and context. Includes Neftalí Rivera's 79-point game in 1974 (34 field goals, all two-pointers — the three-point line didn't exist yet) and Jonathan García's 33 assists in 2012, which is an unofficial world record.

### `bsn_franchises.csv` — 28 rows
Every franchise found, active and defunct, with city, founding year, status, and title count. This is the seed for the franchise-lineage table. Note Brujos de Guayama → Osos de Manatí is captured in `status`; the other lineage cases (Grises → Criollos, Tiburones + Capitalinos → Cangrejeros, Indios ↔ Taínos) still need encoding as events.

---

## COVERAGE MATRIX

| Data | Earliest | Latest | Source | Method |
|---|---|---|---|---|
| Champion / runner-up | 1930 | 2025 | Wikipedia | done, in this pull |
| League records | 1969 | 2012 | Wikipedia | done, in this pull |
| Career leaders (top 10) | 1957 | ~2018 | Wikipedia | done, in this pull |
| Season scoring leaders | 1957 | present | Wikipedia | partial — finish the fetch |
| Season leaders, all categories | **1957** | 2004 | **Wayback / old bsnpr.com** | **highest priority** |
| Full player season stats | 2011 | present | RealGM | Phase 2 scrape |
| Awards | 2014 | present | RealGM | Phase 2 scrape |
| Box scores | ? | present | bsnpr.com / Genius | needs DevTools recon |
| Everything else pre-2004 | 1930 | 2004 | newspaper archives | Phase 4, ongoing |

---

## WHAT THIS DOESN'T CONTAIN

Per-player season averages for every player, every season. That data does not exist in any fetchable public source before 2011, and the honest answer is that it may not exist in digital form at all before the old bsnpr.com database — whose real depth is still unknown until someone runs the Wayback query above.
