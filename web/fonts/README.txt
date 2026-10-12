Self-hosted fonts (PHASE_69). No request for a font leaves this origin.

inter-latin-opsz-normal-5.3.0.woff2   Inter, variable (wght 100-900, opsz 14-32), latin subset
oswald-latin-wght-normal-5.3.0.woff2  Oswald, variable (wght 200-700), latin subset

Source: npm packages @fontsource-variable/inter@5.3.0 and @fontsource-variable/oswald@5.3.0
(files/inter-latin-opsz-normal.woff2 and files/oswald-latin-wght-normal.woff2, unmodified).
Licence: SIL Open Font License 1.1. OFL-Inter.txt and OFL-Oswald.txt are the packages' LICENSE files.

The version is in the file name on purpose: sw.js serves /fonts/ cache-first, so a new font
version must ship under a new name (and the @font-face URLs, the preloads in index.html and
the sw.js PRECACHE list must change together; tests/test_phase69_legal.py checks that).
Only the latin subset is shipped. If shipped text ever needs a latin-ext letter, that test fails
and a latin-ext subset has to be added.
