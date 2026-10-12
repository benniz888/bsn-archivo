"""Display names for the site (PHASE_72C, owner decision D2).

A DISPLAY layer only. `data/raw/` and `data/clean/` keep the source spelling byte for byte; this module
decides what `src/build_web_data.py` writes into the generated `web/data/` as `player`, next to the
untouched `player_raw`. Nothing here invents data (PC1):

  * ALL-CAPS tokens are proper-cased. Accents already in the source are kept; none are added.
  * A typo is fixed only through OVERRIDES, one entry per name, each with its evidence.
  * A truncated or surname-only name is expanded only when the very same observation row is already
    linked to a `bsnpr_id` in `player_id_map.csv` and the spelling is consistent with that player's
    canonical name. Otherwise it is left exactly as the source printed it.
  * NON_NAMES are replaced by their approved text; the AYUSO exclusion is never touched.
"""

from __future__ import annotations

import re
import unicodedata

# Source strings that are not a person, with the text shown instead. The raw cell stays in `player_raw`.
# "NO FUE SELECCIONADO" is the 1979 rookie-award row: nobody was selected. Wording approved by the owner
# (docs/strings_pending_phase72.md F1).
NON_NAMES = {"NO FUE SELECCIONADO": "No se seleccionó"}

# One entry per name. Add nothing without a source row: the comment is the evidence.
OVERRIDES: dict[str, str] = {
    # data/clean/historic_awards.csv:71 (mvp 1986, FAJARDO) reads GOERGIE; rows 69 and 70 (1984, 1985,
    # same club FAJARDO, bsnpr_id 788) read GEORGIE TORRES. The raw capture itself carries the typo
    # (data/raw/pre2007/mvp/20040405022402_JDUEAITC.html), so it is the source's, not ours.
    "GOERGIE TORRES": "Georgie Torres",
}

# Left alone, flagged in docs/audits/data_review_todo.md: the Larry / Elias Ayuso identity is open (D2).
AYUSO = re.compile(r"\bayuso\b", re.I)

_PARTICLES = {"de", "del", "la", "las", "los", "y", "van", "von", "da", "di"}
_ROMAN = {"II", "III", "IV"}
_JR_SR = {"JR": "Jr.", "SR": "Sr."}
# "Mac" is only a prefix in these surnames; MACHADO, MACIAS and MACEDO are plain names. None of them is
# in the data today; the list exists so the rule is explicit and tested.
_MAC = {"MACDONALD": "MacDonald", "MACGREGOR": "MacGregor", "MACKENZIE": "MacKenzie", "MACLEAN": "MacLean",
        "MACARTHUR": "MacArthur"}

_NICK = re.compile(r"""(?<![\w])(?:['"‘“«])([^'"’”»]+?)(?:['"’”»])""")


def _letters(s: str) -> list[str]:
    return [c for c in s if c.isalpha()]


def is_all_caps(s: str) -> bool:
    L = _letters(s)
    return len(L) >= 3 and all(c.isupper() for c in L)


def _cap(w: str) -> str:
    return w[:1].upper() + w[1:].lower()


def _word(w: str, first: bool) -> str:
    """Proper-case one word that may carry hyphens, apostrophes and a trailing period."""
    core = w.rstrip(".")
    dot = w[len(core):]
    up = core.upper()
    if up in _MAC:
        return _MAC[up] + dot
    if up in _JR_SR:
        return _JR_SR[up]
    if up in _ROMAN:
        return up + dot
    if core.lower() in _PARTICLES and not first and not dot:
        return core.lower()
    if len(core) == 1:                                   # an initial: "A."
        return core.upper() + dot
    if "-" in core:
        return "-".join(_word(p, first and i == 0) for i, p in enumerate(core.split("-"))) + dot
    if "'" in core:                                      # O'BRYANT -> O'Bryant; a longer prefix is lower-cased
        head, _, tail = core.partition("'")
        return (head.upper() + "'" + _cap(tail) if len(head) == 1 else _cap(head) + "'" + tail.lower()) + dot
    if up.startswith("MC") and len(core) > 3:           # MCCADNEY -> McCadney
        return "Mc" + core[2].upper() + core[3:].lower() + dot
    return _cap(core) + dot


def _token_is_caps(t: str) -> bool:
    L = _letters(t)
    return len(L) >= 2 and all(c.isupper() for c in L)


def proper_case(raw: str) -> str:
    """Proper-case the ALL-CAPS tokens of `raw`; mixed-case tokens are kept ("McCADNEY" is repaired to
    "McCadney", "De Jesus" is kept). Nickname quotes of any kind become «…» with a space around them."""
    s = _NICK.sub(lambda m: "«" + m.group(1).strip() + "»", raw)
    s = re.sub(r"(?<=\w)«", " «", s)
    s = re.sub(r"»(?=\w)", "» ", s)
    out, first = [], True
    for t in s.split(" "):
        if not t:
            continue
        if t.startswith("«") or t.endswith("»"):
            inner = t.strip("«»")
            core = _word(inner, first) if _token_is_caps(inner) else inner
            out.append(("«" if t.startswith("«") else "") + core + ("»" if t.endswith("»") else ""))
        elif t.startswith("Mc") and _token_is_caps(t[2:]):
            out.append("Mc" + _cap(t[2:]))
        elif _token_is_caps(t) or (len(_letters(t)) == 1 and t.isupper() and not first):
            out.append(_word(t.rstrip(","), first) + ("," if t.endswith(",") else ""))
        else:
            out.append(t)
        first = False
    return " ".join(out)


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode()
    return " ".join(re.sub(r"[^a-z ,]", " ", s).split())


def is_truncated(raw: str) -> bool:
    """A nickname opened and never closed: the source cell was cut (about 15-21 characters)."""
    return "," in raw and bool(re.search(r"""\s['"‘“][^'"’”]*$""", raw))


def is_surname_only(raw: str) -> bool:
    return "," not in raw and len(raw.split()) == 1


def consistent(raw: str, canonical: str) -> bool:
    """The canonical name really is this observation's player, not just a row that happens to share an id."""
    n_raw, n_can = _norm(re.sub(r"""\s['"‘“][^'"’”]*$""", "", raw)), _norm(canonical)
    if is_surname_only(raw):
        return n_raw == n_can.split(",")[0].split()[0]
    sur, _, given = n_raw.partition(",")
    csur, _, cgiven = n_can.partition(",")
    return bool(sur.strip()) and csur.split()[0] == sur.split()[0] and cgiven.strip().startswith(given.strip().split(" ")[0])


def display_name(raw: str, canonical: str | None = None) -> str:
    """The name to show for `raw`. `canonical` is the canonical full name of the bsnpr_id already linked to
    this exact observation (None when there is no link)."""
    if raw in NON_NAMES:
        return NON_NAMES[raw]
    if not raw or AYUSO.search(raw):
        return raw
    if raw in OVERRIDES:
        return OVERRIDES[raw]
    if canonical and (is_truncated(raw) or is_surname_only(raw)) and consistent(raw, canonical):
        return canonical
    if is_all_caps(re.sub(r"\bMc(?=[A-Z]{2})", "MC", raw)):     # "BILL McCADNEY" counts as ALL-CAPS
        return proper_case(raw)
    return raw
