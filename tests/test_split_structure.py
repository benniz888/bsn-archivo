"""PHASE_1_SPLIT structural checks. Written in STEP 1, before any file is actually split (there are
no <link rel=stylesheet> or <script src=...> tags yet) -- they pass vacuously today and start
enforcing real invariants as each extraction commit lands, so a later step can't silently ship a
broken reference or an uncovered sw.js path prefix."""
import re

import pytest

from src.wayback_cdx import REPO_ROOT

WEB = REPO_ROOT / "web"
INDEX = WEB / "index.html"
SW = WEB / "sw.js"

_LINK_RE = re.compile(r'<link\s+rel="stylesheet"\s+href="([^"]+)">')
_SCRIPT_SRC_RE = re.compile(r'<script\s+src="([^"]+)"[^>]*></script>')
_INLINE_SCRIPT_RE = re.compile(r"<script(?![^>]*\ssrc=)[^>]*>(.*?)</script>", re.S)


def _linked_assets():
    html = INDEX.read_text(encoding="utf-8")
    return _LINK_RE.findall(html), _SCRIPT_SRC_RE.findall(html)


class TestLinkedAssetsResolve:
    def test_every_stylesheet_link_resolves_to_a_real_file(self):
        css_hrefs, _ = _linked_assets()
        for href in css_hrefs:
            assert (WEB / href).is_file(), href

    def test_every_script_src_resolves_to_a_real_file(self):
        _, js_srcs = _linked_assets()
        for src in js_srcs:
            assert (WEB / src).is_file(), src


class TestServiceWorkerCoversTheSplitPaths:
    def test_sw_js_classifies_css_and_js_paths_as_shell_assets(self):
        text = SW.read_text(encoding="utf-8")
        assert "function isShellAsset(url)" in text
        assert "url.pathname.includes('/css/')" in text
        assert "url.pathname.includes('/js/')" in text

    def test_every_linked_asset_path_matches_the_sw_shell_asset_prefixes(self):
        css_hrefs, js_srcs = _linked_assets()
        for href in css_hrefs:
            assert "/css/" in ("/" + href), href
        for src in js_srcs:
            assert "/js/" in ("/" + src), src

    def test_the_shell_asset_handler_is_network_first_not_stale_while_revalidate(self):
        text = SW.read_text(encoding="utf-8")
        block = text[text.index("if (isShellAsset(url)) {"):text.index("if (!isDataJson(url)) return;")]
        assert "await fetch(req)" in block and "res.ok" in block  # network first, cache on success
        assert "cache.match(req)) || Response.error()" in block  # fallback is THIS file's own entry only


class TestExactlyOneInlineScriptOnceSplit:
    @pytest.mark.xfail(reason="PHASE_1_SPLIT not complete: the main <script> block is still inline",
                        strict=True)
    def test_index_html_has_exactly_one_inline_script_the_theme_init_block(self):
        html = INDEX.read_text(encoding="utf-8")
        inline = _INLINE_SCRIPT_RE.findall(html)
        assert len(inline) == 1
        assert "localStorage.getItem('bsn:theme')" in inline[0]
