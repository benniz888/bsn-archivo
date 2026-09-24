"""PHASE_1_SPLIT harness self-test. Through STEP 1, nothing had been split and app_text() was a
no-op (proven then). STEP 2 moved <style> into web/css/main.css, so web/index.html on its own is
no longer byte-identical to app/bsn_archivo.html BY DESIGN -- app_text() is what has to keep
proving the underlying text is still the same, by splicing the linked file back in. Every later
test that switched from APP.read_text() to app_text() is only as trustworthy as this file."""
import subprocess

from src.wayback_cdx import REPO_ROOT
from tests._app_text import INDEX, app_text


def _head_app_html() -> bytes:
    out = subprocess.run(["git", "show", "HEAD:app/bsn_archivo.html"], cwd=REPO_ROOT,
                          capture_output=True, check=True)
    return out.stdout


class TestAppTextReconstructsTheOriginal:
    def test_app_text_equals_app_bsn_archivo_html_byte_for_byte(self):
        app_html = (REPO_ROOT / "app" / "bsn_archivo.html").read_bytes()
        assert app_text().encode("utf-8") == app_html

    def test_app_text_equals_git_head_app_bsn_archivo_html_byte_for_byte(self):
        assert app_text().encode("utf-8") == _head_app_html()

    def test_web_index_html_alone_no_longer_matches_app_bsn_archivo_html(self):
        # STEP 2: this is now the EXPECTED state, not a drift bug -- index.html links css/main.css
        # instead of inlining it. app_text() (checked above) is the thing that must still match;
        # a raw index.html-vs-app.html compare is retired as a direct check, not just weakened.
        app_html = (REPO_ROOT / "app" / "bsn_archivo.html").read_bytes()
        assert INDEX.read_bytes() != app_html

    def test_app_text_actually_splices_something_in_not_a_silent_no_op(self):
        # guards against the splice regex quietly matching zero tags and app_text() collapsing
        # back to "just read index.html" without anyone noticing
        assert app_text() != INDEX.read_text(encoding="utf-8")
        assert '<link rel="stylesheet" href="css/main.css">' in INDEX.read_text(encoding="utf-8")
        assert "<style>" not in INDEX.read_text(encoding="utf-8")
