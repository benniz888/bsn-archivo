"""T1.5 — sample probe. Fetch exactly THREE Wayback snapshots and report the
table shape `pandas.read_html` sees in each. This is a probe, not the ingest;
Phase 2 does the bulk fetch after approval.

Sample selection is constrained by what actually archived (see
`docs/coverage_wayback.md`). The task queue asked for one 1960s, one 1980s and
one 2000s `lideres.asp` snapshot. The 1957–2004 parametrized pages were never
archived with content — every in-window capture except `anio=1986` is a 302 from
the 2021-07-09 IABot run. So the probe covers what exists:

  1. lideres.asp?anio=1986...      — the ONLY archived historic parametrized
                                      season. Stands in for the 1980s and tells
                                      us the per-season table shape.
  2. lideres.asp   (no params)     — earliest live-era landing page (2007).
                                      Stands in for the 2000s; establishes what
                                      a parameter-less capture contains.
  3. campeonatos.asp (no params)   — earliest live-era capture (2007). The
                                      second endpoint; likely the full finals
                                      history. Replaces the impossible 1960s
                                      lideres snapshot.

Run: `python -m src.fetch_samples`
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pandas as pd
import requests

from src.wayback_cdx import REPO_ROOT, USER_AGENT, polite_get

SAMPLES_DIR = REPO_ROOT / "data" / "raw" / "samples"

# (label, wayback_timestamp, original_url) — see module docstring for rationale.
SAMPLES = [
    (
        "lideres_anio1986_20170804",
        "20170804230003",
        "http://www.bsnpr.com/estadisticas/lideres.asp?anio=1986&liga=1&serie=1&d=&mes=&dia=&l=&tabla=&grupo=BS26&B1=Ver",
    ),
    (
        "lideres_bare_20070529",
        "20070529091448",
        "http://bsnpr.com:80/estadisticas/lideres.asp?",
    ),
    (
        "campeonatos_bare_20070422",
        "20070422043423",
        "http://www.bsnpr.com:80/estadisticas/campeonatos.asp",
    ),
]

RAW_SUFFIX = "id_"  # F4: raw HTML without archive chrome


def raw_wayback_url(timestamp: str, original_url: str) -> str:
    return f"https://web.archive.org/web/{timestamp}{RAW_SUFFIX}/{original_url}"


def fetch_one(label: str, timestamp: str, original_url: str, session: requests.Session) -> Path:
    """Fetch to data/raw/samples/<label>.html, byte-for-byte (PC5). Cached."""
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    html_path = SAMPLES_DIR / f"{label}.html"
    meta_path = SAMPLES_DIR / f"{label}.meta.json"

    if html_path.exists() and html_path.stat().st_size > 0:
        print(f"[sample] {label}: cached ({html_path.stat().st_size} bytes)")
        return html_path

    url = raw_wayback_url(timestamp, original_url)
    print(f"[sample] {label}: GET {url}")
    resp = polite_get(url, session=session)
    if resp.status_code != 200:
        print(f"  ! HTTP {resp.status_code} — not saving", file=sys.stderr)
        resp.raise_for_status()

    html_path.write_bytes(resp.content)
    meta_path.write_text(json.dumps({
        "label": label,
        "wayback_timestamp": timestamp,
        "original_url": original_url,
        "raw_wayback_url": url,
        "final_url": resp.url,
        "content_length": len(resp.content),
        "content_type": resp.headers.get("Content-Type", ""),
    }, indent=2))
    print(f"  -> {html_path.relative_to(REPO_ROOT)} ({len(resp.content)} bytes)")
    return html_path


def probe_tables(label: str, html_path: Path) -> None:
    """Report what pandas.read_html extracts: table count, shape, columns."""
    raw = html_path.read_bytes()
    print(f"\n=== {label} ===")
    print(f"file: {html_path.relative_to(REPO_ROOT)} ({len(raw)} bytes)")
    try:
        tables = pd.read_html(io.BytesIO(raw))
    except ValueError as exc:
        print(f"  read_html: NO TABLES ({exc})")
        return
    except Exception as exc:  # noqa: BLE001 - probe must report, not crash
        print(f"  read_html: FAILED ({exc.__class__.__name__}: {exc})")
        return

    print(f"  read_html: {len(tables)} table(s)")
    for i, df in enumerate(tables):
        cols = [str(c) for c in df.columns]
        print(f"  [table {i}] shape={df.shape[0]}x{df.shape[1]}  columns={cols}")
        # first data row often reveals whether header row was mis-detected
        if not df.empty:
            first = [str(v) for v in df.iloc[0].tolist()]
            print(f"            row0={first}")


def main() -> int:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    if len(SAMPLES) != 3:
        print(f"! SAMPLES must hold exactly 3 entries (has {len(SAMPLES)})", file=sys.stderr)
        return 1

    paths = [fetch_one(*s, session=session) for s in SAMPLES]
    for (label, _, _), path in zip(SAMPLES, paths):
        probe_tables(label, path)
    print("\n[done] Probe complete. Findings feed docs/specs/wayback_ingest_spec.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
