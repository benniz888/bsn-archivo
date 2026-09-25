"""PHASE_1_SPLIT caching fix (approved, STEP 3). web/css/*.css and web/js/*.js are served with
the same max-age=600 HTTP cache as every other file under web/, so a visitor who has an old asset
cached could get it paired with a freshly-changed web/index.html for up to 10 minutes after a
design or data-shape change. Fix: every <link rel="stylesheet" href="css/X.css"> and
<script src="js/X.js"> tag in web/index.html carries a content-hash query string,
?v=<sha256 of the file's current bytes, first 12 hex chars> -- same convention as
manifest.json's source_digest (src/build_web_data.py:_source_digest). Nobody has to remember to
bump it by hand: this script recomputes it from the files' actual bytes and rewrites
web/index.html in place. The pre-commit hook runs it and blocks the commit if that rewrite
produces an uncommitted diff, the same pattern it already uses for web/data/ freshness.

Extends to any future web/js/*.js file with no code change here -- it globs web/css/*.css and
web/js/*.js, not a hardcoded list of filenames.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WEB = REPO_ROOT / "web"
INDEX = WEB / "index.html"

# matches <link rel="stylesheet" href="css/X.css"[?v=...]> and <script src="js/X.js"[?v=...]></script>
_TAG_RE = re.compile(
    r'<link rel="stylesheet" href="(css/[^"?]+\.css)(?:\?v=[0-9a-f]+)?">'
    r'|<script src="(js/[^"?]+\.js)(?:\?v=[0-9a-f]+)?"></script>'
)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def update() -> bool:
    """Rewrites web/index.html's asset tags with fresh content hashes. Returns True if the
    file's content changed (i.e. some hash was stale or missing)."""
    text = INDEX.read_text(encoding="utf-8")

    def repl(m: re.Match) -> str:
        rel = m.group(1) or m.group(2)
        digest = _digest(WEB / rel)
        if m.group(1):
            return f'<link rel="stylesheet" href="{rel}?v={digest}">'
        return f'<script src="{rel}?v={digest}"></script>'

    new_text = _TAG_RE.sub(repl, text)
    changed = new_text != text
    if changed:
        INDEX.write_text(new_text, encoding="utf-8")
    return changed


if __name__ == "__main__":
    changed = update()
    print("web/index.html asset hashes " + ("updated" if changed else "already current"))
