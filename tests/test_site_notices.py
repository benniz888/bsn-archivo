"""PHASE_SITE_NOTICES — footer contact/unofficial-status/privacy lines and head meta/OG/Twitter tags.
Pure app text, no data. Every string below is the owner-approved exact text; this file pins it
verbatim so a future edit can't silently reword it.

STEP 10 (cleanup): reads web_text() (tests/_web_text.py), not app/bsn_archivo.html (now an
archived pointer, docs/specs/app_split_spec.md) -- web_text() reconstructs the exact same "whole
app text" app/bsn_archivo.html used to be, splicing web/css/main.css back into a real <style> tag,
so _head()/_footer() below are unchanged from before the split."""

import re

from tests._web_text import web_text

CONTACT_LINE = ("¿Ves un error o quieres que retiremos algo? Escríbenos a "
                 "benniz.8008@gmail.com o por Instagram @bennizpr.")
UNOFFICIAL_LINE = ("Proyecto independiente de un aficionado. No está afiliado ni respaldado por "
                    "el Baloncesto Superior Nacional ni por sus equipos.")
PRIVACY_LINE = ("Este sitio no usa cookies ni analítica. Las tipografías vienen de Google Fonts, "
                 "por lo que Google recibe tu dirección IP. Tu navegador guarda solo tus preferencias "
                 "(tema y club favorito), tu progreso en los juegos y una copia de los datos para que "
                 "el sitio funcione sin conexión.")
META_DESCRIPTION = ("Archivo histórico independiente del Baloncesto Superior Nacional, 1930–2026. "
                     "Proyecto de un aficionado, no oficial.")
TITLE = "BSN Archivo · Baloncesto Superior Nacional, 1930–2026"


def _head(text):
    return text[:text.index("<style>")]


def _footer(text):
    return text[text.index('<footer class="foot">'):text.index("</footer>") + len("</footer>")]


class TestFooter:
    def test_the_three_new_sentences_are_the_approved_exact_text(self):
        footer = _footer(web_text())
        assert UNOFFICIAL_LINE in footer
        assert PRIVACY_LINE in footer
        # the contact line's plain text is split around two <a> tags in the markup; check the pieces
        assert "¿Ves un error o quieres que retiremos algo? Escríbenos a" in footer
        assert "o por Instagram" in footer
        assert footer.count("@bennizpr") == 1 and "benniz.8008@gmail.com" in footer

    def test_the_kept_sentences_are_untouched(self):
        footer = _footer(web_text())
        assert "BSN Archivo · construido por <b>bennizpr</b> · San Juan, Puerto Rico." in footer
        assert "Los datos vienen de fuentes públicas citadas en «El archivo»." in footer
        # the old sentences this phase replaced are gone
        assert "Archivo personal." not in footer
        assert "No está afiliado al Baloncesto Superior Nacional." not in footer

    def test_the_mailto_and_instagram_links_are_present_and_correct(self):
        footer = _footer(web_text())
        assert '<a href="mailto:benniz.8008@gmail.com" target="_blank" rel="noopener">' in footer
        assert '<a href="https://www.instagram.com/bennizpr/" target="_blank" rel="noopener">' in footer
        # both links open in a new tab with noopener, as specified -- no bare/unlinked repeat of either
        assert footer.count('href="mailto:benniz.8008@gmail.com"') == 1
        assert footer.count('href="https://www.instagram.com/bennizpr/"') == 1

    def test_error_and_oficial_appear_only_where_approved(self):
        footer = _footer(web_text())
        # "error" appears exactly once, inside the approved contact line
        assert len(re.findall(r"error", footer, re.I)) == 1
        assert "un error o quieres que retiremos" in footer
        # "equivocad"/"oficial" never appear in the footer at all (the approved "no oficial" is in <head>)
        assert not re.search(r"equivocad", footer, re.I)
        assert not re.search(r"oficial", footer, re.I)

    def test_web_asset_wiring_is_intact(self):
        # STEP 10 (cleanup): app/bsn_archivo.html is now an archived pointer (docs/specs/
        # app_split_spec.md), so a byte-compare against it is retired. What this checks now,
        # exactly (same three things src.verify_clean.verify_web_data() checks under `make
        # verify` -- exercised here too so a plain `pytest` run alone still catches drift, the
        # way the old byte-copy test did): every <link>/<script src> tag in web/index.html
        # resolves to a real file under web/, each one's ?v= content hash matches that file's
        # current bytes, and the split's 426-declaration inventory still has exactly the name set
        # recorded in tests/harness/inventory_main_HEAD.json (the frozen pre-split baseline).
        from src.verify_clean import Checker, verify_web_data
        c = Checker()
        verify_web_data(c)
        assert not c.failures, c.failures


class TestHeadTags:
    def test_the_meta_description_is_the_approved_exact_text(self):
        head = _head(web_text())
        assert f'<meta name="description" content="{META_DESCRIPTION}">' in head

    def test_the_og_and_twitter_tags_are_present_and_correct(self):
        head = _head(web_text())
        assert '<meta property="og:type" content="website">' in head
        assert '<meta property="og:site_name" content="BSN Archivo">' in head
        assert f'<meta property="og:title" content="{TITLE}">' in head
        assert f'<meta property="og:description" content="{META_DESCRIPTION}">' in head
        assert '<meta property="og:url" content="https://bsnarchivo.com/">' in head
        assert '<meta name="twitter:card" content="summary">' in head
        assert f'<meta name="twitter:title" content="{TITLE}">' in head
        assert f'<meta name="twitter:description" content="{META_DESCRIPTION}">' in head

    def test_no_og_image_tag_exists(self):
        text = web_text()
        assert "og:image" not in text

    def test_error_and_equivocad_never_appear_in_the_head_and_oficial_only_in_the_approved_text(self):
        head = _head(web_text())
        assert not re.search(r"error", head, re.I) and not re.search(r"equivocad", head, re.I)
        # "oficial" appears exactly 3 times: description + og:description + twitter:description, all
        # the same approved "no oficial" phrase
        assert len(re.findall(r"oficial", head, re.I)) == 3
        assert all("no oficial" in m for m in re.findall(r".{0,20}oficial", head, re.I))
