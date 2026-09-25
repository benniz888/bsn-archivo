"""PHASE_1_SPLIT harness self-test. Through STEP 1, nothing had been split and app_text() was a
no-op (proven then). STEP 2 moved <style> into web/css/main.css; STEP 3 moved 18 hand-curated
constants into web/js/data.js. web/index.html on its own is no longer byte-identical to
app/bsn_archivo.html BY DESIGN -- app_text() is what has to keep proving the underlying text is
still the same, by splicing the linked files back in, in their original positions. Every later
test that switched from APP.read_text() to app_text() is only as trustworthy as this file."""
import re
import subprocess

from src.wayback_cdx import REPO_ROOT
from tests._app_text import DATA_JS, INDEX, app_text


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
        # back to "just read index.html" without anyone noticing. Hrefs carry a ?v=<hash> query
        # (src/update_asset_hashes.py) so this matches the href up to that, not the whole tag.
        index_text = INDEX.read_text(encoding="utf-8")
        assert app_text() != index_text
        assert re.search(r'<link rel="stylesheet" href="css/main\.css(\?v=[0-9a-f]+)?">',
                          index_text)
        assert re.search(r'<script src="js/data\.js(\?v=[0-9a-f]+)?"></script>', index_text)
        assert "<style>" not in index_text

    def test_step3_named_constants_are_gone_from_index_html_and_live_in_data_js(self):
        # the 18 hand-curated constants named in the STEP 3 instruction: declared exactly once,
        # in web/js/data.js, and not declared (only possibly USED) in web/index.html's own script.
        names = ["F", "RECENT", "HOF", "RETIRED", "REF_RULES", "ON_THIS_DAY", "POOL", "VENUES",
                 "FIVE_2026", "SEASON_STATE", "POOL_2026", "POOL_RGM", "POOL_PATCH",
                 "PLAYERS_NEW", "MESES", "DIAS", "CATS", "HL_SETS"]
        data_text = DATA_JS.read_text(encoding="utf-8")
        index_text = INDEX.read_text(encoding="utf-8")
        for name in names:
            decl_re = re.compile(r"^(?:const|let|var) " + re.escape(name) + r"\s*=", re.M)
            assert len(decl_re.findall(data_text)) == 1, f"{name} not declared once in data.js"
            assert not decl_re.search(index_text), f"{name} still declared in index.html"
