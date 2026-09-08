"""PHASE_3B_PROBE_ARCHIVE — sample-fetch and inspect the archived bsnpr.com
`/estadisticas/` scripts that PHASE_2 did not process, to decide whether any
deserves a full ingest phase.

Sample only. No bulk fetch, no interim/clean output. Raw captures land in
`data/raw/probe/` (gitignored) byte-for-byte (PC5); polite sequential fetch
with backoff (PC6).

Run: `python -m src.probe_archive`
"""

from __future__ import annotations

import json
import re
import sys
from io import StringIO
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

from src.wayback_cdx import REPO_ROOT, USER_AGENT, polite_get
from src.fetch_samples import raw_wayback_url
from src.parse_wayback import decode_html

PROBE_DIR = REPO_ROOT / "data" / "raw" / "probe"

# (label, wayback_timestamp, original_url) — chosen from data/interim/cdx_inventory.csv
# for distinct content digests spread across the archived date range.
TARGETS: list[tuple[str, str, str]] = [
    # enciclopedia.asp — all param-less, 79 distinct 200s 2007–2021
    ("enciclopedia", "20070417033701", "http://www.bsnpr.com:80/estadisticas/enciclopedia.asp"),
    ("enciclopedia", "20090131225016", "http://bsnpr.com:80/estadisticas/enciclopedia.asp"),
    ("enciclopedia", "20120621143253", "http://www.bsnpr.com:80/estadisticas/enciclopedia.asp"),
    ("enciclopedia", "20140221044849", "http://www.bsnpr.com:80/estadisticas/enciclopedia.asp"),
    ("enciclopedia", "20210901033342", "https://www.bsnpr.com/estadisticas/enciclopedia.asp"),
    # lideres_e.asp — bare + parametrized (grupo/serie/anio)
    ("lideres_e", "20070509063614", "http://www.bsnpr.com:80/estadisticas/lideres_e.asp?"),
    ("lideres_e", "20070505021750", "http://www.bsnpr.com:80/estadisticas/lideres_e.asp?grupo=BS26&serie=1"),
    ("lideres_e", "20120507150047", "http://www.bsnpr.com:80/estadisticas/lideres_e.asp?grupo=BS19&serie=1&anio=2012"),
    ("lideres_e", "20140325161450", "http://bsnpr.com:80/estadisticas/lideres_e.asp?anio=2014"),
    ("lideres_e", "20200601011619", "https://www.bsnpr.com/estadisticas/lideres_e.asp?anio=2019"),
    # livestats.asp — bare + ?live=1&onlylive=1
    ("livestats", "20130428111459", "http://www.bsnpr.com:80/estadisticas/livestats.asp"),
    ("livestats", "20130831145105", "http://www.bsnpr.com:80/estadisticas/livestats.asp?live=1&onlylive=1"),
    ("livestats", "20140420063328", "http://www.bsnpr.com:80/estadisticas/livestats.asp"),
    ("livestats", "20170708152714", "http://www.bsnpr.com:80/estadisticas/livestats.asp"),
    # estadisticas.asp — the 2001–2002 pre-lideres cluster
    ("estadisticas2001", "20010803075616", "http://bsnpr.com:80/estadisticas.asp?t=3"),
    ("estadisticas2001", "20011124124233", "http://www.bsnpr.com:80/estadisticas.asp"),
    ("estadisticas2001", "20020616014253", "http://www.bsnpr.com:80/estadisticas.asp"),
    ("estadisticas2001", "20020616014713", "http://www.bsnpr.com:80/estadisticas2001.asp"),
    ("estadisticas2001", "20021005144039", "http://www.bsnpr.com:80/estadisticas.asp"),
]


def fetch_all(session: requests.Session) -> list[dict]:
    PROBE_DIR.mkdir(parents=True, exist_ok=True)
    out: list[dict] = []
    for i, (label, ts, url) in enumerate(TARGETS, 1):
        fname = f"{label}_{ts}.html"
        fpath = PROBE_DIR / fname
        raw_url = raw_wayback_url(ts, url)
        if fpath.exists() and fpath.stat().st_size > 0:
            print(f"[{i}/{len(TARGETS)}] cached {fname}")
        else:
            print(f"[{i}/{len(TARGETS)}] GET {raw_url}")
            try:
                resp = polite_get(raw_url, session=session)
            except requests.RequestException as exc:
                print(f"    ! {exc.__class__.__name__}: {exc}", file=sys.stderr)
                continue
            if resp.status_code != 200:
                print(f"    ! HTTP {resp.status_code}", file=sys.stderr)
                continue
            fpath.write_bytes(resp.content)
            (PROBE_DIR / f"{fname}.meta.json").write_text(json.dumps(
                {"label": label, "wayback_timestamp": ts, "original_url": url,
                 "raw_wayback_url": raw_url, "content_length": len(resp.content)}, indent=2))
        out.append({"label": label, "ts": ts, "url": url, "path": fpath})
    return out


def inspect(path: Path) -> None:
    raw = path.read_bytes()
    html = decode_html(raw)
    soup = BeautifulSoup(html, "html.parser")
    text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))

    print(f"\n{'=' * 78}\n{path.name}  ({len(raw)} bytes)")
    title = soup.find("title")
    print(f"  <title>: {title.get_text(strip=True) if title else '—'}")

    # selects (season / group pickers) — what range the engine could serve
    for sel in soup.find_all("select"):
        opts = [o.get("value") or o.get_text(strip=True) for o in sel.find_all("option")]
        yrs = [o for o in opts if re.fullmatch(r"(19|20)\d\d", str(o))]
        if yrs:
            print(f"  <select name={sel.get('name')!r}>: years {min(yrs)}–{max(yrs)} ({len(opts)} options)")

    # iframes / scripts pointing at external stat providers
    for tag in soup.find_all(["iframe", "script"]):
        src = tag.get("src", "")
        if src and any(k in src.lower() for k in ("genius", "livestats", "fiba", "synergy", "widget", "feed")):
            print(f"  external {tag.name}: {src}")
    for m in re.findall(r"(matchId|gameId|game_id|match_id|fixtureId)\s*[=:]\s*['\"]?(\w+)", html):
        print(f"  id hint: {m[0]}={m[1]}")

    try:
        tables = pd.read_html(StringIO(html))
    except Exception as exc:  # noqa: BLE001 - probe tool: any parse failure is a finding
        print(f"  read_html: {exc.__class__.__name__}")
        tables = []
    print(f"  read_html: {len(tables)} table(s)")
    for j, t in enumerate(tables):
        shape = f"{t.shape[0]}x{t.shape[1]}"
        cols = [re.sub(r"\s+", " ", str(c))[:22] for c in t.columns][:8]
        looks_player = any(
            re.search(r"jugador|player|nombre|apellido", str(c), re.I) for c in t.columns
        )
        flag = "  <-- player-level" if looks_player else ""
        if t.shape[0] >= 1 and t.shape[1] >= 2:
            print(f"    [{j}] {shape} {cols}{flag}")
    # year mentions in body text — is there pre-2007 content?
    body_years = sorted(set(re.findall(r"\b(19[5-9]\d|20[0-1]\d)\b", text)))
    if body_years:
        print(f"  years in body text: {body_years[0]}–{body_years[-1]} "
              f"({'incl. pre-2007' if any(y < '2007' for y in body_years) else '2007+ only'})")
    print(f"  text sample: {text[:260]}")


def main() -> int:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    fetched = fetch_all(session)
    print(f"\n{len(fetched)}/{len(TARGETS)} captures available. Inspecting:\n")
    for rec in fetched:
        inspect(rec["path"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
