"""Backlog item 7, Phase B — parse the 103 fetched latinbasket.com roster
pages into `data/interim/latinbasket_roster_raw.csv`. Unresolved to
canonical player ids at this stage (Phase C); PC5 — raw HTML untouched.

**Real finding: this isn't one template, it's (at least) three**, spanning
the ~2009-2020 crawl window. Checked directly per file, not assumed one
shape for all (the lesson from the 2018 stage-table bug in
`parse_latinbasket.py`):

1. **`flat_bo`** (29 files, ~2009-2013 era): a real `<table>` whose header
   row is `# | Name | CM | Pos | Bo | NAT` (`Bo` = 2-digit birth **year** —
   exact, not inferred). Matches this archive's original scoping
   description of the source.
2. **`flat_age`** (8 files, ~2017+ era, mostly reached via the richer
   `?Page=1` capture the Phase A fetcher now prefers): same shape, header
   `# | Name | CM | Pos | Age | NAT | FR | TO | Former Team | Agent` — a
   real site redesign that swapped birth year for age and added tenure
   (`FR`/`TO`) + former-team + agent, plus a stable
   `latinbasket.com/player/.../<id>` per row.
3. **`widget`** (43 files): a "half-court" position-slot widget
   (`class="playerPosition"`) on the Starting-Five/Reserve tabs. Ten named
   slots per team-season (jersey, height, position, **age**, nationality,
   `latinbasket_player_id`, profile link) plus additional "deep bench"
   names nested in a popup with only name + height + age — no jersey, no
   position, no profile link. Both tiers kept, tagged by `completeness`.
4. **`photo_strip`** (remaining files with neither of the above — a real,
   disclosed gap, not fabricated around): these pages are a "team home"
   teaser, not the roster (`?Page=1`/"Full Roster" is the real roster;
   Phase A already tried it — either no such capture was ever archived, or
   it was, but every archived copy is a Wayback-captured CAPTCHA wall, not
   real content). What *is* real on the teaser: a small photo strip of a
   handful of named players linking to `/player/.../<id>`. Extracted as
   name + `latinbasket_player_id` only — real signal, not discarded just
   because the page around it is thin (PC4).

**Birth-year precision is not uniform** — `flat_bo` gives an exact 2-digit
birth year; `flat_age`/`widget` only give age, so `approx_birth_year` here
is `season - age`, off by up to 1 depending on the (unknown) exact
birthday, and is written as a *derived* field, never conflated with a
real `birth_year_2digit` value. `photo_strip` gives neither.

**Name order is not uniform either** — `flat_*` tables list "Surname
GivenName" (e.g. "Pellot-Rosa Jesse"); `widget`/`photo_strip` give
"GivenName Surname" (photo alt text / mediumfont label). Both are kept
as-is in `name_raw` with `name_order` recorded — reordering here would be
exactly the kind of silent normalization D1 warns against; Phase C's
identity matching needs the real source shape, not a guess at it.

Run: `python -m src.parse_latinbasket_roster`
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from pathlib import Path

from bs4 import BeautifulSoup

from src.wayback_cdx import REPO_ROOT

RAW_DIR = REPO_ROOT / "data" / "raw" / "latinbasket_roster"
MANIFEST = REPO_ROOT / "data" / "interim" / "fetch_manifest_latinbasket_roster.csv"
OUT_PATH = REPO_ROOT / "data" / "interim" / "latinbasket_roster_raw.csv"

FIELDNAMES = [
    "franchise_id", "season", "season_source", "template", "section",
    "jersey_number", "name_raw", "name_order", "height_cm", "position_raw",
    "birth_year_2digit", "age", "approx_birth_year", "nationality_raw",
    "years_from", "years_to", "former_team_raw",
    "eurobasket_player_id", "latinbasket_player_id", "profile_url",
    "completeness", "source_id", "source_url", "retrieved_at", "confidence",
]

EUROBASKET_ID_RE = re.compile(r"PlayerID=(\d+)")
LATINBASKET_ID_RE = re.compile(r"/player/[^/]+/[^/]+/[^/]+/(\d+)")
HEIGHT_RE = re.compile(r"(\d{2,3})")
WIDGET_PAREN_RE = re.compile(r"\((\d{2,3})-([A-Za-z/]+)-(\d{1,2})\)")


def _find_flat_table(soup: BeautifulSoup) -> tuple[list[str], list] | tuple[None, None]:
    """Header-anchored, not positional: a real roster table's header row is
    individual `<td>` cells whose (usually bold) text starts `# | Name`.
    Handles both the `Bo`-column and `Age`-column eras with the same code
    by keying off the header labels rather than column position."""
    for table in soup.find_all("table"):
        rows = table.find_all("tr", recursive=False)
        if len(rows) < 2:
            continue
        header_cells = rows[0].find_all("td", recursive=False)
        if len(header_cells) < 4:
            continue
        labels = []
        for c in header_cells:
            b = c.find("b")
            label = (b.get_text(strip=True) if b else c.get_text(strip=True))
            labels.append(label.rstrip(":").strip())
        if labels[:2] != ["#", "Name"]:
            continue
        return labels, rows[1:]
    return None, None


def _ids_from_href(href: str | None) -> tuple[str | None, str | None]:
    if not href:
        return None, None
    eb = EUROBASKET_ID_RE.search(href)
    lb = LATINBASKET_ID_RE.search(href)
    return (eb.group(1) if eb else None, lb.group(1) if lb else None)


def _parse_flat_table(labels: list[str], data_rows: list, base: dict) -> list[dict]:
    # Real, confirmed finding (2026-09-14, Phase C santeros_aguada batch):
    # the two flat-table eras don't just swap Bo-for-Age, they also swap
    # name order - `flat_bo` renders "Surname GivenName" ("Pellot-Rosa
    # Jesse"), `flat_age` renders "GivenName Surname" ("Elias Ayuso",
    # "Kyle Vinales") - checked across multiple `flat_age` files, 100%
    # consistent. A hardcoded surname_first here silently broke the
    # family-name-prefix fallback match for every `flat_age` row with a
    # dropped/added surname token (exact-name matches were unaffected -
    # `norm_key` is order-agnostic - which is exactly why this went
    # unnoticed until a row needed the fallback tier).
    is_bo_era = "Bo" in labels
    template = "flat_bo" if is_bo_era else "flat_age"
    name_order = "surname_first" if is_bo_era else "given_first"
    out = []
    for tr in data_rows:
        cells = tr.find_all("td", recursive=False)
        if len(cells) != len(labels):
            continue  # a real structural mismatch (e.g. a section divider row) - skip, don't guess
        texts = [c.get_text(" ", strip=True) for c in cells]
        row = dict(zip(labels, texts))
        if not row.get("Name"):
            continue
        name_cell = cells[labels.index("Name")]
        a = name_cell.find("a")
        eurobasket_id, latinbasket_id = _ids_from_href(a.get("href") if a else None)
        height_m = HEIGHT_RE.match(row.get("CM", ""))
        season_int = int(base["season"])
        age = row.get("Age", "").strip() or None
        birth_2d = row.get("Bo", "").strip() or None
        # Real bug, found 2026-09-14 (leones_ponce 2017): a row can be a
        # genuine placeholder/data-entry gap for an otherwise-real player
        # (checked the raw HTML directly: jersey/height/pos all blank or
        # "0", `Bo` literally "0") - treating that "0" as a real 2-digit
        # birth year fabricated a birth year (2000) out of a data gap.
        # "0" is never a real age or Bo value for an adult pro player.
        if age == "0":
            age = None
        if birth_2d == "0":
            birth_2d = None
        approx_birth_year = str(season_int - int(age)) if age and age.isdigit() else None
        out.append({
            **base, "template": template, "section": "roster",
            "jersey_number": row.get("#", "").strip() or None,
            "name_raw": row["Name"], "name_order": name_order,
            "height_cm": height_m.group(1) if height_m else None,
            "position_raw": row.get("Pos", "").strip() or None,
            "birth_year_2digit": birth_2d, "age": age,
            "approx_birth_year": approx_birth_year,
            "nationality_raw": row.get("NAT", "").strip() or None,
            "years_from": row.get("FR", "").strip() or None,
            "years_to": row.get("TO", "").strip() or None,
            "former_team_raw": row.get("Former Team", "").strip() or None,
            "eurobasket_player_id": eurobasket_id, "latinbasket_player_id": latinbasket_id,
            "profile_url": a.get("href") if a else None,
            "completeness": "full",
        })
    return out


def _parse_widget(soup: BeautifulSoup, base: dict) -> list[dict]:
    out = []
    for tab_id, section in (("tab_s5", "starting_five"), ("tab_rs", "reserve")):
        tab = soup.find(id=tab_id)
        if tab is None:
            continue
        for ptable in tab.find_all("table", class_="playerPosition"):
            trs = ptable.find_all("tr")
            if len(trs) < 2:
                continue
            name_td = trs[0].find_all("td")
            mediumfont = trs[0].find("td", class_="mediumfont")
            smallfont = trs[1].find("td", class_="smallfont") if len(trs) > 1 else None
            img = trs[0].find("img")
            full_name = img.get("alt") if img else None
            jersey = None
            if mediumfont:
                m = re.match(r"#(\d+)", mediumfont.get_text(" ", strip=True))
                jersey = m.group(1) if m else None
            height_cm = position_raw = age = None
            if smallfont:
                pm = WIDGET_PAREN_RE.search(smallfont.get_text(" ", strip=True))
                if pm:
                    height_cm, position_raw, age = pm.group(1), pm.group(2), pm.group(3)
            pop = ptable.find_next_sibling("div", class_="popDiv") or ptable.parent.find("div", class_="popDiv")
            profile_url = None
            latinbasket_id = None
            if pop:
                a = pop.find("a", href=re.compile(r"/player/"))
                if a:
                    profile_url = a.get("href")
                    _, latinbasket_id = _ids_from_href(profile_url)
            season_int = int(base["season"])
            approx_birth_year = str(season_int - int(age)) if age and age.isdigit() else None
            if full_name:
                out.append({
                    **base, "template": "widget", "section": section,
                    "jersey_number": jersey, "name_raw": full_name, "name_order": "given_first",
                    "height_cm": height_cm, "position_raw": position_raw,
                    "birth_year_2digit": None, "age": age, "approx_birth_year": approx_birth_year,
                    "nationality_raw": None, "years_from": None, "years_to": None,
                    "former_team_raw": None, "eurobasket_player_id": None,
                    "latinbasket_player_id": latinbasket_id, "profile_url": profile_url,
                    "completeness": "full",
                })
            # deep-bench names nested in the popup: "Name (HEIGHT-AGE)", no jersey/pos/link
            if pop:
                for btd in pop.find_all("td"):
                    txt = btd.get_text(" ", strip=True)
                    bm = re.match(r"^([A-Za-zÀ-ÿ'.\-\s]+)\((\d{2,3})-(\d{1,2})\)$", txt)
                    if not bm:
                        continue
                    bname, bheight, bage = bm.group(1).strip(), bm.group(2), bm.group(3)
                    approx_by = str(season_int - int(bage)) if bage.isdigit() else None
                    out.append({
                        **base, "template": "widget", "section": section,
                        "jersey_number": None, "name_raw": bname, "name_order": "given_first",
                        "height_cm": bheight, "position_raw": None,
                        "birth_year_2digit": None, "age": bage, "approx_birth_year": approx_by,
                        "nationality_raw": None, "years_from": None, "years_to": None,
                        "former_team_raw": None, "eurobasket_player_id": None,
                        "latinbasket_player_id": None, "profile_url": None,
                        "completeness": "partial",
                    })
    return _dedupe_widget_rows(out)


def _norm_name_key(name: str) -> str:
    stripped = "".join(c for c in unicodedata.normalize("NFD", name) if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", stripped.lower()).strip()


def _dedupe_widget_rows(rows: list[dict]) -> list[dict]:
    """The half-court widget repeats a bench player once per starter he
    backs up (real depth-chart data, e.g. one reserve behind two different
    starting positions) plus again in his own tab's primary slot — the
    same real person, not distinct rows for a roster count. Collapse to
    one row per player, keyed by normalized name (bench mentions never
    carry a `latinbasket_player_id` to key on — that's exactly the case
    being collapsed), keeping the fullest record: `full` beats `partial`,
    and among equals the one carrying a jersey number wins."""
    best: dict[str, dict] = {}
    order: list[str] = []
    for r in rows:
        key = _norm_name_key(r["name_raw"])
        cur = best.get(key)
        if cur is None:
            best[key] = r
            order.append(key)
            continue
        cur_score = (cur["completeness"] == "full", cur["jersey_number"] is not None)
        r_score = (r["completeness"] == "full", r["jersey_number"] is not None)
        if r_score > cur_score:
            best[key] = r
    return [best[k] for k in order]


def _parse_photo_strip(soup: BeautifulSoup, base: dict) -> list[dict]:
    out = []
    seen_ids = set()
    for a in soup.find_all("a", href=re.compile(r"/player/")):
        img = a.find("img")
        full_name = img.get("alt") if img else None
        if not full_name:
            continue
        _, latinbasket_id = _ids_from_href(a.get("href"))
        dedup_key = latinbasket_id or full_name
        if dedup_key in seen_ids:
            continue
        seen_ids.add(dedup_key)
        out.append({
            **base, "template": "photo_strip", "section": "teaser",
            "jersey_number": None, "name_raw": full_name, "name_order": "given_first",
            "height_cm": None, "position_raw": None,
            "birth_year_2digit": None, "age": None, "approx_birth_year": None,
            "nationality_raw": None, "years_from": None, "years_to": None,
            "former_team_raw": None, "eurobasket_player_id": None,
            "latinbasket_player_id": latinbasket_id, "profile_url": a.get("href"),
            "completeness": "partial",
        })
    return out


WOMENS_PROFILE_RE = re.compile(r"/player/[^\"']*Women=1")


def _is_womens_content(html: str) -> bool:
    """**Real, confirmed finding (2026-09-14, Phase C sanity check)**: some
    team pages serve the WOMEN'S team's roster under the exact same team
    URL/id as the men's team the franchise-name filter matched, with no
    marker at all on the team page's own URL (Phase A's `Women=1`
    query-param check only looks at the page URL, which stays clean) - the
    tell only shows up on the per-player profile links *inside* the page
    (`/player/.../<id>?Women=1`), one per real roster slot. Confirmed on
    `gigantes_carolina_2014`/`_2017` (11 and 9 such links respectively, one
    per player extracted) by reading the actual page content, not
    inferred from names. A threshold of >=2 avoids one-off nav noise
    (`usbasket.com/WNBA/...`-style links are never `/player/` paths, so
    they never match this regex at all — checked directly, this is not a
    guessed threshold)."""
    return len(WOMENS_PROFILE_RE.findall(html)) >= 2


def parse_file(html_path: Path, manifest_row: dict) -> list[dict]:
    html = html_path.read_text(encoding="utf-8", errors="replace")
    if _is_womens_content(html):
        return []
    soup = BeautifulSoup(html, "lxml")
    base = {
        "franchise_id": manifest_row["franchise_id"],
        "season": manifest_row["season"],
        "season_source": manifest_row["season_source"],
        "source_id": "latinbasket",
        "source_url": manifest_row["original_url"],
        "retrieved_at": manifest_row["timestamp"],
        "confidence": "single-source",
    }
    labels, data_rows = _find_flat_table(soup)
    if labels:
        return _parse_flat_table(labels, data_rows, base)
    if 'class="playerPosition"' in html:
        rows = _parse_widget(soup, base)
        if rows:
            return rows
    return _parse_photo_strip(soup, base)


def main() -> int:
    manifest_rows = [r for r in csv.DictReader(MANIFEST.open(encoding="utf-8")) if r["status"] == "ok"]
    all_rows: list[dict] = []
    template_counts: dict[str, int] = {}
    excluded_womens: list[str] = []
    for mrow in manifest_rows:
        html_path = RAW_DIR / mrow["local_file"]
        html = html_path.read_text(encoding="utf-8", errors="replace")
        if _is_womens_content(html):
            excluded_womens.append(f"{mrow['franchise_id']} {mrow['season']}")
            print(f"  [{mrow['franchise_id']} {mrow['season']}] EXCLUDED - women's team content "
                  f"under this team id (see _is_womens_content docstring)")
            continue
        rows = parse_file(html_path, mrow)
        all_rows.extend(rows)
        for r in rows:
            template_counts[r["template"]] = template_counts.get(r["template"], 0) + 1
        print(f"  [{mrow['franchise_id']} {mrow['season']}] {len(rows)} rows "
              f"({rows[0]['template'] if rows else 'empty'})")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(all_rows)

    print()
    if excluded_womens:
        print(f"[parse_latinbasket_roster] EXCLUDED as women's-team content, not a data gap "
              f"but not BSN men's data either: {excluded_womens}")
    print(f"[parse_latinbasket_roster] {len(all_rows)} rows from "
          f"{len(manifest_rows) - len(excluded_womens)} pages -> "
          f"{OUT_PATH.relative_to(REPO_ROOT)}")
    print(f"  by template: {template_counts}")
    full = sum(1 for r in all_rows if r["completeness"] == "full")
    print(f"  completeness: {full} full, {len(all_rows) - full} partial")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
