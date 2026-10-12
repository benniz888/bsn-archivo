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
# PHASE_69 (owner-approved Oct 12): L2 and L3 replace the earlier wording, and the "Los datos vienen de
# fuentes públicas..." sentence left the footer (Créditos carries the sources now).
UNOFFICIAL_LINE = ("Proyecto independiente. No es un sitio oficial del BSN. No está afiliado ni "
                    "respaldado por el Baloncesto Superior Nacional ni por sus equipos.")
PRIVACY_LINE = ("Este sitio no usa cookies ni analítica y no pide datos personales. Las tipografías se "
                 "sirven desde este mismo sitio. Tu navegador guarda en tu dispositivo tus preferencias, "
                 "tu progreso en los juegos y una copia de los datos; consulta la "
                 '<a href="#privacidad">Política de privacidad</a>.')
META_DESCRIPTION = ("Archivo histórico independiente del Baloncesto Superior Nacional, 1930–2026. "
                     "Proyecto de un aficionado, no oficial.")
TITLE = "El Archivo · Baloncesto Superior Nacional, 1930–2026"


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
        assert "El Archivo · construido por <b>bennizpr</b> · San Juan, Puerto Rico." in footer
        assert "Los datos vienen de fuentes públicas citadas en «El archivo»." not in footer
        # the old sentences this phase replaced are gone
        assert "Archivo personal." not in footer
        assert "No está afiliado al Baloncesto Superior Nacional." not in footer

    def test_the_mailto_and_instagram_links_are_present_and_correct(self):
        footer = _footer(web_text())
        # PHASE_69: the mailto link no longer opens a new tab (a mail client does not need one)
        assert '<a href="mailto:benniz.8008@gmail.com">' in footer
        assert '<a href="https://www.instagram.com/bennizpr/" target="_blank" rel="noopener">' in footer
        # both links open in a new tab with noopener, as specified -- no bare/unlinked repeat of either
        assert footer.count('href="mailto:benniz.8008@gmail.com"') == 1
        assert footer.count('href="https://www.instagram.com/bennizpr/"') == 1

    def test_error_and_oficial_appear_only_where_approved(self):
        footer = _footer(web_text())
        # "error" appears exactly once, inside the approved contact line
        assert len(re.findall(r"error", footer, re.I)) == 1
        assert "un error o quieres que retiremos" in footer
        # "equivocad" never appears; "oficial" appears once, in the approved "No es un sitio oficial del BSN."
        assert not re.search(r"equivocad", footer, re.I)
        assert len(re.findall(r"oficial", footer, re.I)) == 1
        assert "No es un sitio oficial del BSN." in footer

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
        assert '<meta property="og:site_name" content="El Archivo">' in head
        # PHASE_71 (owner-approved): the share title is the bare name; TITLE stays the document <title> default.
        assert '<meta property="og:title" content="El Archivo">' in head
        assert f'<meta property="og:description" content="{META_DESCRIPTION}">' in head
        assert '<meta property="og:url" content="https://bsnarchivo.com/">' in head
        assert '<meta name="twitter:card" content="summary_large_image">' in head   # PHASE_71: was "summary"
        assert '<meta name="twitter:title" content="El Archivo">' in head
        assert f'<meta name="twitter:description" content="{META_DESCRIPTION}">' in head

    def test_og_image_is_the_phase71_absolute_url_and_nothing_else_is_shared_as_an_image(self):
        # Was "no og:image tag exists" (PHASE_69 era, there was no image file). PHASE_71 added web/img/brand/og.png.
        text = web_text()
        assert text.count('property="og:image"') == 1 and text.count('name="twitter:image"') == 1
        assert '<meta property="og:image" content="https://bsnarchivo.com/img/brand/og.png">' in text

    def test_error_and_equivocad_never_appear_in_the_head_and_oficial_only_in_the_approved_text(self):
        head = _head(web_text())
        assert not re.search(r"error", head, re.I) and not re.search(r"equivocad", head, re.I)
        # "oficial" appears exactly 3 times: description + og:description + twitter:description, all
        # the same approved "no oficial" phrase
        assert len(re.findall(r"oficial", head, re.I)) == 3
        assert all("no oficial" in m for m in re.findall(r".{0,20}oficial", head, re.I))
