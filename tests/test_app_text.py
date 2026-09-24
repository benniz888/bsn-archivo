"""PHASE_1_SPLIT STEP 0c proof. Right now, nothing has been split yet -- app_text() must return
exactly what web/index.html already contains, and that must be byte-identical to
`git show HEAD:app/bsn_archivo.html` on this branch. This is the harness's own self-test: every
later test that switches from APP.read_text() to app_text() is only as trustworthy as this."""
import subprocess

from src.wayback_cdx import REPO_ROOT
from tests._app_text import INDEX, app_text


def _head_app_html() -> bytes:
    out = subprocess.run(["git", "show", "HEAD:app/bsn_archivo.html"], cwd=REPO_ROOT,
                          capture_output=True, check=True)
    return out.stdout


class TestAppTextReconstructsTheOriginal:
    def test_app_text_equals_web_index_html_today(self):
        # today there is no <link rel=stylesheet> or <script src=...> yet, so app_text() is a no-op
        assert app_text() == INDEX.read_text(encoding="utf-8")

    def test_app_text_equals_git_head_app_bsn_archivo_html_byte_for_byte(self):
        assert app_text().encode("utf-8") == _head_app_html()

    def test_web_index_html_is_still_byte_identical_to_app_bsn_archivo_html(self):
        app_html = (REPO_ROOT / "app" / "bsn_archivo.html").read_bytes()
        assert INDEX.read_bytes() == app_html
