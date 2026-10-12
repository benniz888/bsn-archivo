"""`make data-update`: one repeatable command from the committed data to a verified web/data
(PHASE_72D, owner decision D9; design in docs/audits/phase72_audit.md section 9).

Check mode (the default) runs every stage against copies in a temp directory and writes NOTHING to a
tracked file; it prints a validation report and exits non-zero when a check fails. `--apply` repeats the
checks, writes only if all of them passed, then refreshes the asset hashes, runs the full suite and writes
docs/audits/data_update_report.md. Commits stay manual.

Stages: preflight -> game-name repair overlay (in memory) -> display-name layer -> validate ->
build_web_data into a temp dir and diff against web/data -> tests.

What it will never do (N7, docs/audits/phase72_audit.md item 3), enforced by `guard()`:
  * run `parse-players` / `sync-web-data` (not idempotent at HEAD: they re-mint merged ids);
  * run `parse-games` (a re-parse moves 365 unrelated `bsnpr_id` values). The 296 name repairs come from
    the overlay `src/apply_game_name_repair.py`, which rewrites only the damaged rows.

Run: `make data-update`                 (check mode)
     `make data-update ARGS=--apply`    (apply mode)
Exit status: 0 all green; 1 a check failed (one actionable line each); 2 usage error or a forbidden command.
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import filecmp
import gzip
import hashlib
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from src import apply_game_name_repair as agr
from src import build_web_data as b
from src import display_names as dn
from src import parse_games as pg
from src import verify_clean as vc
from src.parse_wayback import _write_csv
from src.wayback_cdx import REPO_ROOT

CLEAN = REPO_ROOT / "data" / "clean"
WEB = REPO_ROOT / "web" / "data"
REPORT_PATH = REPO_ROOT / "docs" / "audits" / "data_update_report.md"

# Values the owner expects today. A different value is a failed check, not a silent drift: review it,
# then change the constant in the same commit as the data that moved it.
EXPECTED_GONZALEZ_UNASSIGNED = 84     # 82 "Gonzalez, Javier" (Quebradillas 2001-03) + 2 blank-team 2008 rows
EXPECTED_OVERRIDES = 1
# sha256 over the 39,371 game_box_player rows outside the three repaired names (every bsnpr_id a re-parse
# would have moved is in there); recorded before the PHASE_72B repair and unchanged by it.
BOX_UNRELATED_ROWS = 39371
BOX_UNRELATED_DIGEST = "f542ac5d53902e6be16284494722df1f18b53acc241c124e8788a6661fc9ef97"
REPAIRED_NAMES = {"Lloreda, José Jaime", "Lloreda, JosÃ© Jaime", "Cotto, Rubén", "Cotto, RubÃ©n",
                  "González, Javier", "GonzÃ¡lez, Javier"}
BASELINE_SUITE = "959 passed, 1 skipped, 1 xfailed"

STAGES = ("preflight", "repair", "display", "build", "validate", "tests")
NEEDS = {"preflight": ("preflight",), "repair": ("preflight", "repair"), "display": ("preflight", "display"),
         "build": ("preflight", "repair", "build"), "validate": ("preflight", "repair", "build", "validate"),
         "tests": ("preflight", "tests")}
_FORBIDDEN = re.compile(r"parse[-_ ]?players|sync[-_ ]?web[-_ ]?data|parse[-_ ]?games", re.I)
_MOJIBAKE = re.compile("[ÃÂ\ufffd]")


class GuardError(RuntimeError):
    """A forbidden command or stage was requested."""


def guard(what) -> None:
    """Refuse the commands this pipeline must never run. `what` is a command line or a stage name."""
    text = " ".join(what) if not isinstance(what, str) else what
    if _FORBIDDEN.search(text):
        raise GuardError(
            f"refused: {text.strip()!r} names parse-players, sync-web-data or parse-games. They are not "
            "idempotent at HEAD (N7) and a parse-games re-run moves 365 bsnpr_id values; this pipeline uses "
            "the overlay src/apply_game_name_repair.py instead. See docs/data_update_runbook.md.")


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    guard(cmd)
    return subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, **kw)


@dataclass
class Result:
    stage: str
    name: str
    ok: bool
    line: str                          # one line: what was found, or what to do about it
    info: dict = field(default_factory=dict)


# ----------------------------------------------------------------------------- helpers
def _rows(path: Path) -> list[dict]:
    opener = (lambda p: gzip.open(p, "rt", encoding="utf-8", newline="")) if path.suffix == ".gz" else \
             (lambda p: p.open(encoding="utf-8", newline=""))
    with opener(path) as fh:
        return list(csv.DictReader(fh))


def _git_dirty(paths: list[str]) -> list[str]:
    out = subprocess.run(["git", "status", "--porcelain", "--", *paths], cwd=REPO_ROOT,
                         capture_output=True, text=True)
    return [l for l in out.stdout.splitlines() if l.strip()]


def box_digest(rows: list[dict]) -> tuple[int, str]:
    h, n = hashlib.sha256(), 0
    for r in rows:
        if r["player_raw"] in REPAIRED_NAMES:
            continue
        h.update("\x1f".join(r.values()).encode() + b"\n")
        n += 1
    return n, h.hexdigest()


def _scan_mojibake(root: Path, patterns: tuple[str, ...]) -> dict[str, int]:
    hits: dict[str, int] = {}
    for pat in patterns:
        for p in sorted(root.glob(pat)):
            if p.suffix == ".gz":
                with gzip.open(p, "rt", encoding="utf-8", errors="replace") as fh:
                    text = fh.read()
            else:
                text = p.read_text(encoding="utf-8", errors="replace")
            n = sum(1 for line in text.splitlines() if _MOJIBAKE.search(line))
            if n:
                hits[str(p.relative_to(root))] = n
    return hits


def _tree_files(root: Path) -> dict[str, Path]:
    return {str(p.relative_to(root)): p for p in sorted(root.rglob("*")) if p.is_file()}


# ----------------------------------------------------------------------------- stages
@dataclass
class Context:
    apply: bool = False
    skip_tests: bool = False
    tmp: Path | None = None
    results: list[Result] = field(default_factory=list)
    box_before: list[dict] = field(default_factory=list)
    box_after: list[dict] = field(default_factory=list)
    repair_log: list[dict] = field(default_factory=list)
    temp_clean: Path | None = None
    temp_web: Path | None = None
    diff: dict = field(default_factory=dict)
    counts: dict = field(default_factory=dict)
    quality: dict = field(default_factory=dict)
    flags: list[str] = field(default_factory=list)
    suite: str = ""

    def add(self, stage, name, ok, line, **info) -> Result:
        r = Result(stage, name, ok, line, info)
        self.results.append(r)
        return r


def stage_preflight(ctx: Context) -> None:
    dirty = _git_dirty(["data/clean", "data/raw", "web/data"])
    if ctx.apply:
        ctx.add("preflight", "tree", not dirty,
                "clean tree under data/clean, data/raw and web/data" if not dirty else
                f"{len(dirty)} uncommitted change(s) under data/clean, data/raw or web/data: commit or stash them, "
                "then re-run --apply")
    else:
        ctx.add("preflight", "tree", True,
                "clean tree" if not dirty else f"note: {len(dirty)} uncommitted change(s) under data/clean or "
                "web/data; the diff below is against the files on disk")
    ctx.add("preflight", "guards", True, "parse-players, sync-web-data and parse-games are refused by guard()")


def stage_repair(ctx: Context) -> None:
    """The 296-row name repair, in memory: nothing is written here."""
    ctx.box_before = _rows(CLEAN / "game_box_player.csv")
    ctx.box_after, ctx.repair_log = agr.repair(ctx.box_before, pg._load_resolver())
    left = [r for r in ctx.box_after if _MOJIBAKE.search(r["player_raw"])]
    unresolved = sum(1 for e in ctx.repair_log if not e["id_after"])
    ctx.add("repair", "game-name overlay", not left,
            f"{len(ctx.repair_log)} row(s) pending repair, {unresolved} left without an id" if not left else
            f"{len(left)} mojibake row(s) the overlay cannot repair: inspect `python -m src.apply_game_name_repair`",
            pending=len(ctx.repair_log), unresolved=unresolved)


def stage_display(ctx: Context) -> None:
    src = (REPO_ROOT / "src" / "display_names.py").read_text(encoding="utf-8")
    awards = {r["player_raw"] for r in _rows(CLEAN / "historic_awards.csv")}
    missing = [k for k in dn.OVERRIDES if k not in awards or not re.search(r"# data/clean/\w+\.csv:\d+", src.split(f'"{k}"')[0])]
    ctx.quality["overrides"] = len(dn.OVERRIDES)
    ok = not missing and len(dn.OVERRIDES) == EXPECTED_OVERRIDES
    ctx.add("display", "override list", ok,
            f"{len(dn.OVERRIDES)} override(s), each with a source row" if ok else
            (f"override {missing[0]!r} has no source row or no cited comment in display_names.py: remove it or cite a row"
             if missing else f"{len(dn.OVERRIDES)} overrides, expected {EXPECTED_OVERRIDES}: confirm with the owner, then "
             "update EXPECTED_OVERRIDES in src/data_update.py"))


def _build(ctx: Context) -> tuple[bool, str]:
    """build_web_data against a temp copy of data/clean (overlay applied) into a temp web/data."""
    tmp = ctx.tmp
    ctx.temp_clean = tmp / "data" / "clean"
    shutil.copytree(CLEAN, ctx.temp_clean)
    if ctx.repair_log:
        _write_csv(ctx.temp_clean / "game_box_player.csv", ctx.box_after, pg.BOX_COLS)
    ctx.temp_web = tmp / "web" / "data"
    saved = (b.REPO_ROOT, b.CLEAN, b.WEB)
    b.REPO_ROOT, b.CLEAN, b.WEB = tmp, ctx.temp_clean, ctx.temp_web
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            rc = b.main()
    except Exception as exc:  # noqa: BLE001 - reported as a failed check, never swallowed
        ctx.temp_web = None
        return False, f"{type(exc).__name__}: {exc}"
    finally:
        b.REPO_ROOT, b.CLEAN, b.WEB = saved
    return rc == 0, buf.getvalue()


def stage_build(ctx: Context) -> None:
    ok, out = _build(ctx)
    if not ok:
        ctx.temp_web = None
        ctx.add("build", "build_web_data (temp dir)", False,
                f"build_web_data failed in the temp dir ({out.strip().splitlines()[-1] if out.strip() else 'no output'}): "
                "run `make build-web-data` to see the full error")
        return
    old, new = _tree_files(WEB), _tree_files(ctx.temp_web)
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    changed = sorted(k for k in set(old) & set(new) if not filecmp.cmp(old[k], new[k], shallow=False))
    by_dir: dict[str, int] = {}
    for k in added + removed + changed:
        d = k.split("/")[0]
        by_dir[d] = by_dir.get(d, 0) + 1
    ctx.diff = {"added": len(added), "removed": len(removed), "changed": len(changed), "by_dir": by_dir,
                "rows_changed": len(ctx.repair_log)}
    ctx.add("build", "build_web_data (temp dir) and diff vs web/data", True,
            f"{len(changed)} changed, {len(added)} added, {len(removed)} removed file(s); "
            f"{len(ctx.repair_log)} game_box_player row(s) would change", **ctx.diff)


def _web_player_names(web: Path):
    for f in sorted((web / "seasons").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        recs = list(d.get("awards") or []) + [x for l in (d.get("leaders") or {}).values() for x in l]
        if d.get("scoring_champion"):
            recs.append(d["scoring_champion"])
        for r in recs:
            yield r
    for r in json.loads((web / "index" / "mvp.json").read_text(encoding="utf-8")):
        yield r


def stage_validate(ctx: Context) -> None:
    # 1. the existing integrity gate over data/clean and the committed web/data
    c = vc.Checker()
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        for fn in (vc.verify_champions, vc.verify_leaders, vc.verify_stats_tracked, vc.verify_coverage_gaps,
                   vc.verify_pre2007, vc.verify_players, vc.verify_identity_decisions, vc.verify_reconcile,
                   vc.verify_standings, vc.verify_player_roster_latinbasket, vc.verify_games, vc.verify_web_data):
            fn(c)
    ctx.add("validate", "verify_clean", not c.failures,
            f"{c.checks} checks, 0 failed" if not c.failures else
            f"verify_clean: {len(c.failures)} of {c.checks} checks failed, first: {c.failures[0]}: run `make verify`",
            checks=c.checks, failed=len(c.failures))

    # 2. row counts per dataset (data/clean as it will be, and the built web/data)
    for p in sorted(CLEAN.glob("*.csv")) + sorted(CLEAN.glob("*.csv.gz")):
        ctx.counts[p.name] = (len(ctx.box_after) if p.name == "game_box_player.csv" else len(_rows(p)))
    if ctx.temp_web is not None:
        mf = json.loads((ctx.temp_web / "manifest.json").read_text(encoding="utf-8"))
        ctx.counts["web/data (built)"] = mf["counts"]

    # 3. mojibake scan over what the pipeline would leave behind (0 expected)
    if ctx.temp_web is None:
        return
    hits = _scan_mojibake(ctx.temp_clean, ("*.csv", "*.csv.gz"))
    hits.update({"web/data/" + k: v for k, v in _scan_mojibake(ctx.temp_web, ("**/*.json",)).items()})
    n = sum(hits.values())
    ctx.quality["mojibake"] = n
    ctx.add("validate", "mojibake scan", n == 0, "0 lines with mojibake in data/clean and web/data" if n == 0 else
            f"{n} line(s) with mojibake, first in {next(iter(hits))}: run `python -m src.apply_game_name_repair` "
            "or fix the decoder", hits=hits)

    # 4. Javier González: rows that cannot be assigned without a guess
    gon = sum(1 for r in ctx.box_after if r["player_raw"] in ("Gonzalez, Javier", "González, Javier") and not r["bsnpr_id"])
    ctx.quality["gonzalez_unassigned"] = gon
    ctx.add("validate", "Gonzalez unassigned", gon == EXPECTED_GONZALEZ_UNASSIGNED,
            f"{gon} Javier González rows left unassigned (expected {EXPECTED_GONZALEZ_UNASSIGNED})" if
            gon == EXPECTED_GONZALEZ_UNASSIGNED else
            f"{gon} Javier González rows unassigned, expected {EXPECTED_GONZALEZ_UNASSIGNED}: review the change, then "
            "update EXPECTED_GONZALEZ_UNASSIGNED in src/data_update.py")

    # 5. bsnpr_id guarantee: every box row outside the repaired names is untouched
    n_rows, dig = box_digest(ctx.box_after)
    ok = n_rows == BOX_UNRELATED_ROWS and dig == BOX_UNRELATED_DIGEST
    ctx.quality["box_digest"] = dig[:12]
    ctx.add("validate", "bsnpr_id digest", ok,
            f"{n_rows} unrelated game_box_player rows match the recorded digest {dig[:12]}" if ok else
            f"game_box_player rows outside the repaired names changed ({n_rows} rows, digest {dig[:12]}): a bsnpr_id "
            "moved; revert, or if intended update BOX_UNRELATED_* in src/data_update.py")

    # 6. name quality in what would be published
    all_caps, truncated = set(), 0
    for r in _web_player_names(ctx.temp_web):
        shown = r.get("player") or r.get("player_raw") or ""
        raw = r.get("player_raw") or shown
        if dn.is_all_caps(shown):
            all_caps.add(shown)
        if "player" not in r and (dn.is_truncated(raw) or dn.is_surname_only(raw)):
            truncated += 1
    ctx.quality["all_caps_remaining"] = sorted(all_caps)
    ctx.quality["unresolved_truncated"] = truncated
    allowed = {n for n in all_caps if n in dn.NON_NAMES or dn.AYUSO.search(n)}
    stray = sorted(all_caps - allowed)
    ctx.add("validate", "name quality", not stray,
            f"{len(all_caps)} ALL-CAPS name(s) left on purpose, {truncated} truncated or surname-only observation(s) "
            f"without a linked id, {len(dn.OVERRIDES)} override(s)" if not stray else
            f"ALL-CAPS name(s) not handled by the display layer, e.g. {stray[0]!r}: extend display_names.py",
            all_caps=sorted(all_caps))

    # 7. Cruz / Morales: reported, never changed here
    data_js = (REPO_ROOT / "web" / "js" / "data.js").read_text(encoding="utf-8")
    tabs_js = (REPO_ROOT / "web" / "js" / "tabs.js").read_text(encoding="utf-8")
    morales = re.search(r'\{n:"Mario Morales",d:\[[^\]]*\],c:(\[[^\]]*\])', data_js)
    cruz = re.search(r'\{n:"Teófilo Cruz",d:\[[^\]]*\],c:(\[[^\]]*\])', data_js)
    sc = {r["season"]: r["champion"] for r in json.loads((ctx.temp_web / "index" / "scoring_titles.json").read_text(encoding="utf-8")) if r["champion"]}
    mvp = {r["season"]: r for r in json.loads((ctx.temp_web / "index" / "mvp.json").read_text(encoding="utf-8"))}
    conflict = (sc.get(1980, {}).get("franchise_id"), mvp.get(1980, {}).get("franchise_id"))
    held = "present" if "'teofilo|cruz':1" in tabs_js else "LIFTED"
    ctx.flags = [
        f"Mario Morales clubs {morales.group(1) if morales else '?'}: OPEN, 1980 scoring row {conflict[0]} vs 1980 MVP row {conflict[1]}",
        f"Teófilo Cruz clubs {cruz.group(1) if cruz else '?'}: quiz HOLD {held} (owner call)",
        "Larry / Elias Ayuso: untouched (owner: leave)",
        "1979 rookie row 'NO FUE SELECCIONADO': shown as printed (wording S7 pending, docs/strings_pending_phase72.md)",
    ]
    ctx.add("validate", "Cruz / Morales flags", True, f"{len(ctx.flags)} open flag(s) reported (informational)")


def _run_suite() -> str:
    res = run([sys.executable, "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider"])
    tail = [l for l in (res.stdout + res.stderr).splitlines() if l.strip()]
    return tail[-1] if tail else f"pytest exited {res.returncode} with no output"


def stage_tests(ctx: Context) -> None:
    if ctx.skip_tests:
        ctx.add("tests", "pytest", True, "skipped (--skip-tests)")
        return
    ctx.suite = _run_suite()
    failed = re.search(r"(\d+) (failed|error)", ctx.suite)
    ctx.add("tests", "pytest", not failed, f"{ctx.suite} (baseline {BASELINE_SUITE})" if not failed else
            f"{ctx.suite}: run `.venv/bin/python -m pytest -q` and fix the first failure")


# ----------------------------------------------------------------------------- report
def render_report(ctx: Context) -> str:
    L = ["# Data update report", "",
         f"Mode: {'apply' if ctx.apply else 'check (nothing written)'}. "
         f"Result: {'PASS' if all(r.ok for r in ctx.results) else 'FAIL'}.", "", "## Checks", "",
         "| Stage | Check | Result | Detail |", "|---|---|---|---|"]
    for r in ctx.results:
        L.append(f"| {r.stage} | {r.name} | {'PASS' if r.ok else 'FAIL'} | {r.line} |")
    L += ["", "## Row counts per dataset", "", "| Dataset | Rows |", "|---|---|"]
    for k, v in ctx.counts.items():
        if k.startswith("web/data"):
            L.append(f"| {k} | " + ", ".join(f"{a} {b_}" for a, b_ in sorted(v.items())) + " |")
        else:
            L.append(f"| {k} | {v} |")
    q = ctx.quality
    L += ["", "## Name quality", "",
          f"- ALL-CAPS names remaining: {len(q.get('all_caps_remaining', []))} ({', '.join(q.get('all_caps_remaining', [])) or 'none'})",
          f"- Unresolved truncated or surname-only observations: {q.get('unresolved_truncated', '?')}",
          f"- Override list size: {q.get('overrides', '?')}",
          "", "## Integrity", "",
          f"- Mojibake lines in data/clean and web/data: {q.get('mojibake', '?')} (expected 0)",
          f"- Javier González rows unassigned: {q.get('gonzalez_unassigned', '?')} (expected {EXPECTED_GONZALEZ_UNASSIGNED})",
          f"- bsnpr_id digest over {BOX_UNRELATED_ROWS} unrelated box rows: {q.get('box_digest', '?')}... "
          f"(recorded {BOX_UNRELATED_DIGEST[:12]}...)",
          "", "## Open flags (Cruz / Morales and others)", ""]
    L += [f"- {f}" for f in ctx.flags] or ["- none computed"]
    d = ctx.diff
    L += ["", "## Diff summary", "",
          f"- web/data files changed: {d.get('changed', '?')}, added: {d.get('added', '?')}, removed: {d.get('removed', '?')}",
          f"- by directory: {d.get('by_dir', {})}",
          f"- data/clean/game_box_player.csv rows that the overlay changes: {d.get('rows_changed', '?')}",
          "", "## Suite", "", f"- {ctx.suite or 'not run'} (baseline {BASELINE_SUITE})", ""]
    return "\n".join(L)


# ----------------------------------------------------------------------------- driver
def _apply(ctx: Context) -> None:
    """Writes. Reached only when every check passed."""
    if ctx.repair_log:
        agr.main(["--apply"])
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = b.main()
    ctx.add("apply", "build_web_data", rc == 0, "web/data rebuilt" if rc == 0 else
            "build_web_data failed while applying: run `make build-web-data`")
    res = run([sys.executable, "-m", "src.update_asset_hashes"])
    ctx.add("apply", "update_asset_hashes", res.returncode == 0, (res.stdout.strip().splitlines() or ["done"])[-1])
    ctx.skip_tests = False
    stage_tests(ctx)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="data_update", description=__doc__.split("\n")[0])
    ap.add_argument("--apply", action="store_true", help="write data/clean and web/data after every check passes")
    ap.add_argument("--skip-tests", action="store_true", help="check mode only: skip the full pytest run")
    ap.add_argument("--only", metavar="STAGE", help=f"run one stage ({', '.join(STAGES)}) plus what it needs")
    args = ap.parse_args(argv)
    try:
        if args.only:
            guard(args.only)
            if args.only not in STAGES or args.apply:
                print(f"error: --only takes one of {', '.join(STAGES)} and cannot be combined with --apply",
                      file=sys.stderr)
                return 2
    except GuardError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    ctx = Context(apply=args.apply, skip_tests=args.skip_tests)
    with tempfile.TemporaryDirectory(prefix="bsn_data_update_") as tmp:
        ctx.tmp = Path(tmp)
        try:
            want = set(NEEDS[args.only]) if args.only else set(STAGES)
            if "preflight" in want:
                stage_preflight(ctx)
            if "repair" in want:
                stage_repair(ctx)
            if "display" in want:
                stage_display(ctx)
            if "build" in want:
                stage_build(ctx)
            if "validate" in want and ctx.temp_web is not None:
                stage_validate(ctx)
            if not args.apply:
                if "tests" in want:
                    stage_tests(ctx)
            elif all(r.ok for r in ctx.results):
                _apply(ctx)
        except GuardError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
    report = render_report(ctx)
    ok = all(r.ok for r in ctx.results)
    if args.apply and ok:
        REPORT_PATH.write_text(report, encoding="utf-8")
    print(report)
    for r in ctx.results:
        if not r.ok:
            print(f"FAIL [{r.stage}/{r.name}]: {r.line}", file=sys.stderr)
    if args.apply and not ok:
        print("nothing was written." if not any(r.stage == "apply" for r in ctx.results) else
              "some files were written before a later step failed: review `git status`; restore with "
              "`git checkout -- data/clean web` after checking nothing else is uncommitted.", file=sys.stderr)
    print("data-update:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
