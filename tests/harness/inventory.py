"""STEP 0b (PHASE_1_SPLIT harness). Inventories every top-level function/const/let/var declared at
column 0 inside app/bsn_archivo.html's main <script> block (the one starting after the inline
theme-init script, i.e. NOT the FOUC-prevention block). Column-0 is this file's own convention for
top-level declarations throughout (verified: every named example checked this session started at
line-start, no indentation). Run again after the split and diff the two JSON files -- the set of
names must be identical; only the "line" field is allowed to change (and "file" gains a real value).

STEP 3: once code starts living in more than one file (web/index.html's own inline <script> plus
web/js/*.js), a single-file inventory can't show the whole picture any more -- pass several paths
and each declaration is tagged with which one it came from. A plain .js file has no <script> tags
to bound the scan, so the whole file counts as one script region.

Usage: python3 tests/harness/inventory.py <output.json> <path> [<path> ...]
"""
import json
import re
import sys
from pathlib import Path

FUNC_RE = re.compile(r"^(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(")
DECL_RE = re.compile(r"^(const|let|var)\s+(.+?);?\s*$")
NAME_RE = re.compile(r"^([A-Za-z_$][\w$]*)")


def names_in_decl(rest):
    """'GB=null, GMODE=\"daily\"' -> ['GB', 'GMODE']. Splits on top-level commas only (not inside
    (), [], {} or a string), since several lines declare more than one name."""
    names, depth, in_str, quote, buf = [], 0, False, "", ""
    i = 0
    while i < len(rest):
        ch = rest[i]
        if in_str:
            buf += ch
            if ch == quote and rest[i - 1] != "\\":
                in_str = False
        elif ch in "'\"`":
            in_str, quote = True, ch
            buf += ch
        elif ch in "([{":
            depth += 1
            buf += ch
        elif ch in ")]}":
            depth -= 1
            buf += ch
        elif ch == "," and depth == 0:
            names.append(buf)
            buf = ""
        else:
            buf += ch
        i += 1
    if buf.strip():
        names.append(buf)
    out = []
    for n in names:
        m = NAME_RE.match(n.strip())
        if m:
            out.append(m.group(1))
    return out


def find_main_script_bounds(lines):
    starts = [i for i, l in enumerate(lines, 1) if l.rstrip() == "<script>"]
    ends = [i for i, l in enumerate(lines, 1) if l.rstrip() == "</script>"]
    # the main block is the one right before the LAST </script> and after the first one (theme-init)
    return starts[-1], ends[-1]


def _scan(lines, start, end):
    """start/end are 1-indexed, end exclusive-of-the-closing-tag the way find_main_script_bounds
    returns them (i.e. the scannable region is lines[start..end-2] 0-indexed)."""
    out = []
    for i in range(start, end - 1):
        line = lines[i]
        lineno = i + 1
        m = FUNC_RE.match(line)
        if m:
            out.append({"kind": "function", "name": m.group(1), "line": lineno})
            continue
        m = DECL_RE.match(line)
        if m:
            kind, rest = m.group(1), m.group(2)
            for n in names_in_decl(rest):
                out.append({"kind": kind, "name": n, "line": lineno})
    return out


def inventory(path):
    """Single-file form (an .html with the main <script>...</script> block) -- unchanged since
    STEP 0, still what's used against the untouched app/bsn_archivo.html."""
    lines = open(path, encoding="utf-8").readlines()
    start, end = find_main_script_bounds(lines)
    return {"script_bounds": [start, end], "declarations": _scan(lines, start, end)}


def inventory_multi(paths):
    """STEP 3 form: one or more files, each declaration tagged with which one it came from. An
    .html file is scanned the same way as inventory() (bounded by its main <script> block); any
    other file (web/js/*.js) has no <script> tags to bound it, so the whole file is the region."""
    out = []
    for path in paths:
        lines = open(path, encoding="utf-8").readlines()
        rel = str(Path(path))
        if path.endswith(".html"):
            start, end = find_main_script_bounds(lines)
        else:
            start, end = 0, len(lines) + 1  # whole file, same [start, end) convention as above
        for d in _scan(lines, start, end):
            d["file"] = rel
            out.append(d)
    return {"declarations": out}


if __name__ == "__main__":
    dst = sys.argv[1]
    srcs = sys.argv[2:]
    if len(srcs) == 1 and srcs[0].endswith(".html"):
        result = inventory(srcs[0])
    else:
        result = inventory_multi(srcs)
    json.dump(result, open(dst, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    names = [d["name"] for d in result["declarations"]]
    dupes = {n for n in names if names.count(n) > 1}
    bounds = result.get("script_bounds", "n/a (multi-file)")
    print(f"{len(result['declarations'])} declarations, {len(set(names))} unique names, "
          f"script block {bounds}")
    if dupes:
        print(f"NOTE: names declared more than once at top level (re-declared/reset lower in the "
              f"file, not necessarily a bug): {sorted(dupes)}")
