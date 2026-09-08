"""Phase 1 enumeration: CDX inventory of the retired bsnpr.com stats engine.

The old league site published a season-leaders database at
`bsnpr.com/estadisticas/lideres.asp?anio=YYYY...` with Wikipedia citations
running anio=1957 -> anio=2004. Those URLs now 404. This module asks the
Wayback CDX API what survived, writes the raw API responses to
`data/raw/cdx/` byte-for-byte (PC5), and derives an inventory + coverage
matrix from them.

Enumeration only. No snapshot bulk-fetching happens here (that is Phase 2).

Run: `python -m src.wayback_cdx`
"""

from __future__ import annotations

import csv
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import unquote, urlsplit

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_CDX_DIR = REPO_ROOT / "data" / "raw" / "cdx"
INTERIM_DIR = REPO_ROOT / "data" / "interim"
DOCS_DIR = REPO_ROOT / "docs"

CDX_ENDPOINT = "http://web.archive.org/cdx/search/cdx"
TARGET_URL_PATTERN = "bsnpr.com/estadisticas*"

# Descriptive, contactable-via-repo, no PII. PC6.
USER_AGENT = "bsn-archivo/0.1 (historical BSN research archive; polite sequential crawler)"

REQUEST_DELAY_S = 1.5          # PC6: >= 1s between requests
MAX_RETRIES = 5
BACKOFF_BASE_S = 2.0
TIMEOUT_S = 60

# Wikipedia citations for lideres.asp run 1957..2004. This is the window the
# coverage matrix must account for (T1.4).
ANIO_MIN = 1957
ANIO_MAX = 2004

ANIO_RE = re.compile(r"anio=(\d{4})", re.IGNORECASE)


# --------------------------------------------------------------------------- #
# Polite HTTP                                                                  #
# --------------------------------------------------------------------------- #
_last_request_at = 0.0


def polite_get(url: str, *, params: dict | None = None, session: requests.Session) -> requests.Response:
    """Sequential GET with inter-request spacing and exponential backoff.

    Retries on 429 and 5xx only. 4xx (other than 429) is returned as-is for the
    caller to record — a 404 from the CDX API is itself a finding.
    """
    global _last_request_at

    for attempt in range(1, MAX_RETRIES + 1):
        elapsed = time.monotonic() - _last_request_at
        if elapsed < REQUEST_DELAY_S:
            time.sleep(REQUEST_DELAY_S - elapsed)

        try:
            resp = session.get(url, params=params, timeout=TIMEOUT_S)
        except requests.RequestException as exc:
            if attempt == MAX_RETRIES:
                raise
            wait = BACKOFF_BASE_S * (2 ** (attempt - 1))
            print(f"  ! request error ({exc.__class__.__name__}); retry {attempt}/{MAX_RETRIES} in {wait:.0f}s", file=sys.stderr)
            time.sleep(wait)
            continue
        finally:
            _last_request_at = time.monotonic()

        if resp.status_code == 429 or resp.status_code >= 500:
            if attempt == MAX_RETRIES:
                return resp
            wait = BACKOFF_BASE_S * (2 ** (attempt - 1))
            retry_after = resp.headers.get("Retry-After")
            if retry_after and retry_after.isdigit():
                wait = max(wait, float(retry_after))
            print(f"  ! HTTP {resp.status_code}; retry {attempt}/{MAX_RETRIES} in {wait:.0f}s", file=sys.stderr)
            time.sleep(wait)
            continue

        return resp

    return resp  # pragma: no cover - loop always returns above


# --------------------------------------------------------------------------- #
# T1.2 — CDX enumeration                                                       #
# --------------------------------------------------------------------------- #
def fetch_cdx(session: requests.Session) -> dict[str, Path]:
    """Fetch the CDX inventory and write raw responses to data/raw/cdx/ (PC5).

    Two queries:
      * `collapsed` — the exact query specified in the task queue (T1.2),
        one row per unique urlkey.
      * `all` — the same URL pattern with no collapse, so every capture of
        every URL is visible. The coverage matrix (T1.4) needs this: a
        urlkey-collapsed result can surface a redirect and hide a 200 for
        the same page.

    Both raw JSON bodies are persisted unmodified. Re-running with the files
    already present does not re-fetch (PC5: re-parse must never need re-fetch).
    """
    RAW_CDX_DIR.mkdir(parents=True, exist_ok=True)

    queries = {
        "collapsed": {
            "url": TARGET_URL_PATTERN,
            "output": "json",
            "limit": 50000,
            "collapse": "urlkey",
        },
        "all": {
            "url": TARGET_URL_PATTERN,
            "output": "json",
            "limit": 50000,
        },
    }

    written: dict[str, Path] = {}
    for name, params in queries.items():
        out_path = RAW_CDX_DIR / f"cdx_estadisticas_{name}.json"
        if out_path.exists() and out_path.stat().st_size > 0:
            print(f"[cdx] {name}: cached at {out_path.relative_to(REPO_ROOT)} ({out_path.stat().st_size} bytes)")
            written[name] = out_path
            continue

        print(f"[cdx] {name}: querying {CDX_ENDPOINT} {params}")
        resp = polite_get(CDX_ENDPOINT, params=params, session=session)
        if resp.status_code != 200:
            print(f"  ! CDX query '{name}' returned HTTP {resp.status_code}", file=sys.stderr)
            resp.raise_for_status()

        out_path.write_bytes(resp.content)
        print(f"  -> {out_path.relative_to(REPO_ROOT)} ({len(resp.content)} bytes)")
        written[name] = out_path

    return written


# --------------------------------------------------------------------------- #
# T1.3 — inventory CSV                                                         #
# --------------------------------------------------------------------------- #
def _load_cdx_rows(path: Path) -> list[dict]:
    """Parse a CDX json response into a list of dict rows keyed by the header."""
    data = json.loads(path.read_text())
    if not data:
        return []
    header, *rows = data
    return [dict(zip(header, row)) for row in rows]


_SCRIPT_RE = re.compile(r"/estadisticas/([a-z0-9_\-]+\.asp)\b", re.IGNORECASE)


def _classify_endpoint(original: str) -> str:
    """The `.asp` script name under /estadisticas/ (e.g. `lideres.asp`), else `other`.

    T1.3 asks only for lideres.asp / campeonatos.asp / other, but the archive
    holds ~20 distinct stats scripts (posiciones, enciclopedia, mvp, finales,
    per-category leader pages). Recording the real script name costs nothing and
    the coverage doc (T1.4) and spec (T1.6) need the full picture.
    """
    m = _SCRIPT_RE.search(unquote(original))
    return m.group(1).lower() if m else "other"


def _extract_anio(original: str) -> str:
    m = ANIO_RE.search(unquote(original))
    return m.group(1) if m else ""


def _query_string(original: str) -> str:
    return urlsplit(unquote(original)).query


def build_inventory(all_cdx_path: Path) -> Path:
    """Write data/interim/cdx_inventory.csv from the un-collapsed CDX result."""
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    rows = _load_cdx_rows(all_cdx_path)

    out_path = INTERIM_DIR / "cdx_inventory.csv"
    fields = [
        "original_url", "timestamp", "statuscode", "mimetype",
        "digest", "endpoint", "anio", "query", "parametrized",
    ]
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for r in sorted(rows, key=lambda r: (r.get("original", ""), r.get("timestamp", ""))):
            original = r.get("original", "")
            query = _query_string(original)
            writer.writerow({
                "original_url": original,
                "timestamp": r.get("timestamp", ""),
                "statuscode": r.get("statuscode", ""),
                "mimetype": r.get("mimetype", ""),
                "digest": r.get("digest", ""),
                "endpoint": _classify_endpoint(original),
                "anio": _extract_anio(original),
                "query": query,
                "parametrized": "yes" if query.strip("?") else "no",
            })

    print(f"[inventory] {len(rows)} captures -> {out_path.relative_to(REPO_ROOT)}")
    return out_path


# --------------------------------------------------------------------------- #
# T1.4 — coverage matrix                                                       #
# --------------------------------------------------------------------------- #
def _status_bucket(codes: set[str]) -> str:
    """Collapse the set of observed status codes for one anio into one verdict."""
    has_200 = any(c == "200" for c in codes)
    has_revisit = any(c == "-" or c == "" for c in codes)          # Wayback revisit record
    has_redirect = any(c.startswith("3") for c in codes)
    has_error = any(c.startswith("4") or c.startswith("5") for c in codes)

    if has_200:
        return "200"
    if has_revisit:
        return "revisit"
    if has_redirect:
        return "redirect-only"
    if has_error:
        return "error-only"
    return "absent"


DECADES = [
    ("1957-1959", range(1957, 1960)),
    ("1960s", range(1960, 1970)),
    ("1970s", range(1970, 1980)),
    ("1980s", range(1980, 1990)),
    ("1990s", range(1990, 2000)),
    ("2000-2004", range(2000, 2005)),
]

_VERDICT_LABEL = {
    "200": "200 OK",
    "revisit": "revisit (likely 200)",
    "redirect-only": "redirect only",
    "error-only": "error only (4xx/5xx)",
    "absent": "not archived",
}


def build_coverage_matrix(inventory_path: Path) -> Path:
    """Write docs/coverage_wayback.md — per-anio, per-endpoint snapshot verdict."""
    with inventory_path.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    # endpoint -> anio(int) -> set of statuscodes, restricted to PARAMETRIZED
    # captures (a query string with anio=YYYY). The bare landing pages carry no
    # anio and are reported separately below.
    by_endpoint: dict[str, dict[int, set[str]]] = {"lideres.asp": {}, "campeonatos.asp": {}}
    for r in rows:
        ep = r["endpoint"]
        if ep not in by_endpoint or not r["anio"]:
            continue
        by_endpoint[ep].setdefault(int(r["anio"]), set()).add(r["statuscode"])

    def verdicts_for(ep: str, years: range) -> dict[int, str]:
        return {y: _status_bucket(by_endpoint[ep].get(y, set())) for y in years}

    lideres = verdicts_for("lideres.asp", range(ANIO_MIN, ANIO_MAX + 1))
    campeonatos = verdicts_for("campeonatos.asp", range(ANIO_MIN, ANIO_MAX + 1))

    # anio values seen outside the 1957-2004 window (mostly modern re-crawls)
    oow_years = sorted(y for y in by_endpoint["lideres.asp"] if y < ANIO_MIN or y > ANIO_MAX)
    out_of_window = verdicts_for("lideres.asp", range(min(oow_years or [0]), max(oow_years or [0]) + 1)) if oow_years else {}

    # bare (no query string) landing-page captures — the actually-recoverable data
    def bare_stats(ep: str) -> dict:
        cap = [r for r in rows if r["endpoint"] == ep and r["parametrized"] == "no" and r["statuscode"] == "200"]
        ts = sorted(r["timestamp"] for r in cap)
        return {
            "count": len(cap),
            "digests": len({r["digest"] for r in cap}),
            "first": ts[0][:8] if ts else "—",
            "last": ts[-1][:8] if ts else "—",
        }

    bare_lideres = bare_stats("lideres.asp")
    bare_campeonatos = bare_stats("campeonatos.asp")

    lines: list[str] = []
    lines.append("# Wayback coverage — retired bsnpr.com stats engine\n")
    lines.append(
        "Generated by `src/wayback_cdx.py` from `data/interim/cdx_inventory.csv`, "
        "itself derived from the raw CDX responses in `data/raw/cdx/`.\n"
    )
    lines.append(
        "Verdict per `anio` is the best status observed across **all parametrized "
        "captures** (`?anio=YYYY&...`) of that endpoint — a single 200 anywhere wins. "
        "`revisit` = Wayback stored a revisit record (deduplicated content, almost "
        "always pointing at a prior 200).\n"
    )
    lines.append(f"**Window:** anio {ANIO_MIN}–{ANIO_MAX} (the range of Wikipedia's `lideres.asp` citations).\n")

    lines.append("## Headline\n")
    lines.append(
        "The per-season `lideres.asp?anio=YYYY&liga=1&serie=1&grupo=BS26&B1=Ver` URLs "
        "that Wikipedia cites were **only crawled once**, on **2021-07-09** (an IABot "
        "reference-rescue run), and by that date bsnpr.com had already been rebuilt as "
        "a JS app: every one of those captures is a **302 redirect**, retried to **404** "
        "on 2025-12-19. The historic season-leader content behind those citations was "
        "**never archived**.\n"
    )
    lines.append(
        "What *did* archive: the parameter-less landing pages "
        f"`/estadisticas/lideres.asp` ({bare_lideres['count']} × HTTP 200, "
        f"{bare_lideres['digests']} distinct, {bare_lideres['first']}–{bare_lideres['last']}) and "
        f"`/estadisticas/campeonatos.asp` ({bare_campeonatos['count']} × HTTP 200, "
        f"{bare_campeonatos['digests']} distinct, {bare_campeonatos['first']}–{bare_campeonatos['last']}), "
        "plus a scattering of parametrized 200s from the 2007–2016 live era "
        "(see out-of-window table). The Phase 1 probe must establish what a bare "
        "landing page actually contains — current-season leaders at capture time, or "
        "a blank form.\n"
    )

    # --- summary counts ---
    def tally(verdicts: dict[int, str]) -> dict[str, int]:
        out: dict[str, int] = {}
        for v in verdicts.values():
            out[v] = out.get(v, 0) + 1
        return out

    lin_t = tally(lideres)
    cam_t = tally(campeonatos)
    lines.append("## Summary\n")
    lines.append("| Verdict | lideres.asp | campeonatos.asp |")
    lines.append("|---|---|---|")
    for key in ["200", "revisit", "redirect-only", "error-only", "absent"]:
        lines.append(f"| {_VERDICT_LABEL[key]} | {lin_t.get(key, 0)} | {cam_t.get(key, 0)} |")
    usable_lideres = lin_t.get("200", 0) + lin_t.get("revisit", 0)
    lines.append(f"\n**Usable `lideres.asp` seasons (200 or revisit): {usable_lideres} / {ANIO_MAX - ANIO_MIN + 1}.**\n")

    # --- per-decade ---
    lines.append("## Per-decade (lideres.asp)\n")
    lines.append("| Decade | Usable (200/revisit) | Redirect only | Error only | Not archived | Total |")
    lines.append("|---|---|---|---|---|---|")
    for label, yr_range in DECADES:
        ys = [y for y in yr_range if ANIO_MIN <= y <= ANIO_MAX]
        usable = sum(1 for y in ys if lideres[y] in ("200", "revisit"))
        redir = sum(1 for y in ys if lideres[y] == "redirect-only")
        err = sum(1 for y in ys if lideres[y] == "error-only")
        absent = sum(1 for y in ys if lideres[y] == "absent")
        lines.append(f"| {label} | {usable} | {redir} | {err} | {absent} | {len(ys)} |")

    # --- full per-year table ---
    lines.append("\n## Per-season detail — parametrized captures, 1957–2004\n")
    lines.append("| anio | lideres.asp | campeonatos.asp |")
    lines.append("|---|---|---|")
    for y in range(ANIO_MIN, ANIO_MAX + 1):
        lines.append(f"| {y} | {_VERDICT_LABEL[lideres[y]]} | {_VERDICT_LABEL[campeonatos[y]]} |")

    # --- out-of-window parametrized captures ---
    if out_of_window:
        lines.append("\n## Parametrized `lideres.asp?anio=` captures outside the window\n")
        lines.append("Modern live-era seasons that were crawled with parameters intact.\n")
        lines.append("| anio | verdict |")
        lines.append("|---|---|")
        for y in sorted(out_of_window):
            lines.append(f"| {y} | {_VERDICT_LABEL[out_of_window[y]]} |")

    # --- every stats script the archive holds ---
    lines.append("\n## Other `/estadisticas/` scripts in the archive\n")
    lines.append(
        "The old stats engine was more than two pages. Each row is one `.asp` script; "
        "`200s` counts captures that returned HTTP 200, `distinct` counts unique "
        "content digests. Candidates for later phases — not part of this one.\n"
    )
    lines.append("| script | 200s | distinct | first | last | parametrized 200s |")
    lines.append("|---|---|---|---|---|---|")
    by_script: dict[str, list[dict]] = {}
    for r in rows:
        by_script.setdefault(r["endpoint"], []).append(r)
    for script, recs in sorted(by_script.items(), key=lambda kv: -sum(1 for r in kv[1] if r["statuscode"] == "200")):
        if script in ("lideres.asp", "campeonatos.asp"):
            continue
        ok = [r for r in recs if r["statuscode"] == "200"]
        if not ok:
            continue
        ts = sorted(r["timestamp"] for r in ok)
        param_ok = sum(1 for r in ok if r["parametrized"] == "yes")
        lines.append(
            f"| {script} | {len(ok)} | {len({r['digest'] for r in ok})} | "
            f"{ts[0][:8]} | {ts[-1][:8]} | {param_ok} |"
        )

    # --- notes ---
    lines.append("\n## Notes\n")
    absent_years = [y for y in range(ANIO_MIN, ANIO_MAX + 1) if lideres[y] == "absent"]
    if absent_years:
        lines.append(f"- No parametrized `lideres.asp` capture of any status for: {_compact_ranges(absent_years)}.")
    redir_years = [y for y in range(ANIO_MIN, ANIO_MAX + 1) if lideres[y] in ("redirect-only", "error-only")]
    if redir_years:
        lines.append(f"- Capture attempted but only redirect/error (the 2021-07-09 IABot run) for: {_compact_ranges(redir_years)}.")
    usable_param_years = [y for y in range(ANIO_MIN, ANIO_MAX + 1) if lideres[y] in ("200", "revisit")]
    if usable_param_years:
        lines.append(f"- **Parametrized 200 in-window:** {_compact_ranges(usable_param_years)} — verify content in the Phase 1 probe.")
    lines.append(
        "- Bottom line: the 1957–2004 mission cannot be completed from Wayback. "
        "Treat the archive as a source for **2007-onward** landing-page snapshots only; "
        "everything earlier goes to the roadmap Phase 4 newspaper track."
    )

    out_path = DOCS_DIR / "coverage_wayback.md"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[coverage] usable lideres.asp seasons: {usable_lideres}/{ANIO_MAX - ANIO_MIN + 1} -> {out_path.relative_to(REPO_ROOT)}")
    return out_path


def _compact_ranges(years: list[int]) -> str:
    """[1958,1959,1960,1972] -> '1958–1960, 1972'."""
    if not years:
        return "(none)"
    years = sorted(years)
    parts: list[str] = []
    start = prev = years[0]
    for y in years[1:]:
        if y == prev + 1:
            prev = y
            continue
        parts.append(f"{start}–{prev}" if start != prev else f"{start}")
        start = prev = y
    parts.append(f"{start}–{prev}" if start != prev else f"{start}")
    return ", ".join(parts)


# --------------------------------------------------------------------------- #
# main                                                                         #
# --------------------------------------------------------------------------- #
def main() -> int:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    written = fetch_cdx(session)
    inventory = build_inventory(written["all"])
    build_coverage_matrix(inventory)
    print("\n[done] Phase 1 enumeration complete. Sample probe: `python -m src.fetch_samples`.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
