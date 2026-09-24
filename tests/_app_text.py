"""PHASE_1_SPLIT STEP 0c. app_text() reconstructs the text every existing test scanned before the
split: it reads web/index.html and, for each <link rel="stylesheet" href="..."> and each
<script src="..."> it finds (in document order), splices that file's content in place of the tag.
Today (nothing split yet) there are no such tags, so app_text() == web/index.html's own bytes --
proven byte-identical to `git show HEAD:app/bsn_archivo.html` by test_app_text.py. Once the split
lands, this keeps every test that did `APP.read_text()` working unchanged: swap that call for
app_text() and every existing substring/regex assertion still finds what it's looking for, because
the reconstructed string is byte-identical to the pre-split file by construction.
"""
import re

from src.wayback_cdx import REPO_ROOT

WEB = REPO_ROOT / "web"
INDEX = WEB / "index.html"

_LINK_RE = re.compile(r'<link\s+rel="stylesheet"\s+href="([^"]+)">')
_SCRIPT_SRC_RE = re.compile(r'<script\s+src="([^"]+)"[^>]*></script>')


def app_text() -> str:
    html = INDEX.read_text(encoding="utf-8")

    def sub_link(m):
        path = WEB / m.group(1)
        return "<style>" + path.read_text(encoding="utf-8") + "</style>"

    def sub_script(m):
        path = WEB / m.group(1)
        return "<script>" + path.read_text(encoding="utf-8") + "</script>"

    html = _LINK_RE.sub(sub_link, html)
    html = _SCRIPT_SRC_RE.sub(sub_script, html)
    return html
