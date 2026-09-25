"""PHASE_1_SPLIT harness self-test. Through STEP 1, nothing had been split and web_text() was a
no-op (proven then). STEP 2 moved <style> into web/css/main.css; STEP 3 moved 18 hand-curated
constants into web/js/data.js. web/index.html on its own is no longer byte-identical to the
pre-split app BY DESIGN -- web_text() is what has to keep proving the underlying text is still the
same, by splicing the linked files back in, in their original positions. Every other test that
uses web_text() (tests/_web_text.py's own module docstring lists them) is only as trustworthy as
this file.

STEP 10 (cleanup): app/bsn_archivo.html became an archived pointer, so it stopped being usable as
the ground truth these tests check web_text() against. The ground truth now is a frozen git blob:
app/bsn_archivo.html AS OF 714849f, the last commit where it still held the real, pre-split
content (STEP 9's commit -- verified directly: `git show 714849f:app/bsn_archivo.html` is 663,135
bytes, the known original size, not the pointer paragraph). That commit doesn't move, so this
stays exactly as reliable a check as comparing to the live file used to be."""
import re
import subprocess

from src.wayback_cdx import REPO_ROOT
from tests._web_text import DATA_JS, INDEX, web_text

_FROZEN_ORIGINAL_COMMIT = "714849f"


def _frozen_app_html() -> bytes:
    """app/bsn_archivo.html's exact bytes as of the last commit before it became a pointer."""
    out = subprocess.run(["git", "show", f"{_FROZEN_ORIGINAL_COMMIT}:app/bsn_archivo.html"],
                          cwd=REPO_ROOT, capture_output=True, check=True)
    return out.stdout


class TestWebTextReconstructsTheOriginal:
    def test_web_text_equals_the_frozen_pre_split_original_byte_for_byte(self):
        assert web_text().encode("utf-8") == _frozen_app_html()

    def test_web_index_html_alone_no_longer_matches_the_frozen_original(self):
        # STEP 2: this is now the EXPECTED state, not a drift bug -- index.html links css/main.css
        # instead of inlining it. web_text() (checked above) is the thing that must still match;
        # a raw index.html-vs-original compare is retired as a direct check, not just weakened.
        assert INDEX.read_bytes() != _frozen_app_html()

    def test_web_text_actually_splices_something_in_not_a_silent_no_op(self):
        # guards against the splice regex quietly matching zero tags and web_text() collapsing
        # back to "just read index.html" without anyone noticing. Hrefs carry a ?v=<hash> query
        # (src/update_asset_hashes.py) so this matches the href up to that, not the whole tag.
        index_text = INDEX.read_text(encoding="utf-8")
        assert web_text() != index_text
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
