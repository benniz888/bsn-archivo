"""PHASE_65 -- fails if any emoji codepoint appears anywhere under web/ (index.html, js, css content
strings, data/*.json UI strings, sw.js, manifest), comments included. The owner reads emoji in the UI as
"made by AI" (redesign v3 05_page_specs.md). Plain text symbols stay allowed (arrows, U+2713 check,
U+25A0/25A1 squares). A rendered-DOM check for Historia and Jugadores lives in test_player_ring_overlap.py."""
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
TEXT_SUFFIXES = {".html", ".js", ".css", ".json", ".webmanifest", ".svg", ".txt", ".md", ".xml"}

# Emoji_Presentation=Yes in the BMP (the astral range U+1F000-U+1FAFF is flagged wholesale).
_BMP = [(0x231A, 0x231B), (0x23E9, 0x23EC), (0x23F0, 0x23F0), (0x23F3, 0x23F3), (0x25FD, 0x25FE),
        (0x2614, 0x2615), (0x2648, 0x2653), (0x267F, 0x267F), (0x2693, 0x2693), (0x26A1, 0x26A1),
        (0x26AA, 0x26AB), (0x26BD, 0x26BE), (0x26C4, 0x26C5), (0x26CE, 0x26CE), (0x26D4, 0x26D4),
        (0x26EA, 0x26EA), (0x26F2, 0x26F3), (0x26F5, 0x26F5), (0x26FA, 0x26FA), (0x26FD, 0x26FD),
        (0x2705, 0x2705), (0x270A, 0x270B), (0x2728, 0x2728), (0x274C, 0x274C), (0x274E, 0x274E),
        (0x2753, 0x2755), (0x2757, 0x2757), (0x2795, 0x2797), (0x27B0, 0x27B0), (0x27BF, 0x27BF),
        (0x2B1B, 0x2B1C), (0x2B50, 0x2B50), (0x2B55, 0x2B55)]
_JOINERS = {0xFE0F, 0x200D, 0x20E3}


_RX = re.compile("[\U0001F000-\U0001FAFF" + "".join(f"\\u{a:04X}-\\u{b:04X}" for a, b in _BMP)
                 + "".join(f"\\u{c:04X}" for c in sorted(_JOINERS)) + "]")


def scan(text):
    """Yield (line, col, codepoint) for every emoji codepoint in text."""
    for ln, line in enumerate(text.splitlines(), 1):
        for m in _RX.finditer(line):
            yield ln, m.start() + 1, m.group()


def _files():
    return sorted(p for p in WEB.rglob("*") if p.is_file() and p.suffix in TEXT_SUFFIXES)


def test_there_are_web_files_to_scan():
    names = {p.name for p in _files()}
    assert {"index.html", "main.css", "tabs.js", "games.js"} <= names


def test_no_emoji_codepoint_anywhere_in_web():
    bad = []
    for p in _files():
        for ln, col, ch in scan(p.read_text(encoding="utf-8")):
            bad.append(f"{p.relative_to(ROOT)}:{ln}:{col} U+{ord(ch):04X} {unicodedata.name(ch, '?')}")
    assert not bad, "emoji in web/:\n" + "\n".join(bad[:30])


def test_the_guard_catches_what_it_should():
    assert [c for _, _, c in scan("racha \U0001F525 3x")] == ["\U0001F525"]
    assert [c for _, _, c in scan("\U0001F7E9⬛")] == ["\U0001F7E9", "⬛"]
    assert [c for _, _, c in scan("❤️")] == ["️"]
    assert list(scan("■ □ ✓ → racha de 3 ñ")) == []
