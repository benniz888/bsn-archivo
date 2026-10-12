"""PHASE_72D -- `make data-update` (src/data_update.py, owner decision D9).

Pins: check mode writes nothing to a tracked file; the guards refuse parse-players, sync-web-data and
parse-games; the report carries every field the owner asked for; a failing check blocks --apply; apply
runs its steps in order. The real check run is made once (about 15 s) with --skip-tests; the full-suite
stage is covered by monkeypatching _run_suite (the suite cannot run itself).
"""
import hashlib
import re
import subprocess
from pathlib import Path

import pytest

from src import data_update as du

ROOT = Path(__file__).resolve().parent.parent


def _tracked_digest() -> str:
    files = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True).stdout.split(b"\0")
    h = hashlib.sha256()
    for f in sorted(x for x in files if x):
        p = ROOT / f.decode()
        if p.is_file():
            h.update(f + b"\0" + hashlib.sha256(p.read_bytes()).digest())
    return h.hexdigest()


@pytest.fixture(scope="module")
def real_check(tmp_path_factory):
    """One real check-mode run on the committed data; hashes of every tracked file before and after."""
    import contextlib
    import io
    before, status_before = _tracked_digest(), du._git_dirty(["data", "web", "src", "docs", "tests"])
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = du.main(["--skip-tests"])
    after, status_after = _tracked_digest(), du._git_dirty(["data", "web", "src", "docs", "tests"])
    return {"rc": rc, "out": out.getvalue(), "err": err.getvalue(), "before": before, "after": after,
            "status_before": status_before, "status_after": status_after}


class TestCheckMode:
    def test_it_writes_nothing_to_any_tracked_file(self, real_check):
        assert real_check["before"] == real_check["after"]
        assert real_check["status_before"] == real_check["status_after"]

    def test_it_does_not_write_the_report_file(self, real_check):
        # the report goes to stdout in check mode; the file is an --apply artifact
        assert "Mode: check (nothing written)" in real_check["out"]
        assert "docs/audits/data_update_report.md" not in subprocess.run(
            ["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout

    def test_current_data_is_all_green_with_a_zero_diff(self, real_check):
        assert real_check["rc"] == 0, real_check["err"]
        out = real_check["out"]
        assert out.rstrip().endswith("data-update: PASS")
        assert "Result: PASS" in out and "| FAIL |" not in out
        assert "web/data files changed: 0, added: 0, removed: 0" in out
        assert "rows that the overlay changes: 0" in out

    def test_report_fields(self, real_check):
        out = real_check["out"]
        for needle in ("## Row counts per dataset", "| game_box_player.csv | 39669 |", "| players_canonical.csv |",
                       "| game_plays.csv.gz | 233664 |", "web/data (built)",
                       "## Name quality", "ALL-CAPS names remaining: 2 (ELIAS AYUSO, NO FUE SELECCIONADO)",
                       "Unresolved truncated or surname-only observations:", "Override list size: 1",
                       "Mojibake lines in data/clean and web/data: 0 (expected 0)",
                       "Javier González rows unassigned: 84 (expected 84)",
                       "bsnpr_id digest over 39371 unrelated box rows: f542ac5d5390",
                       "## Open flags", "Mario Morales clubs [\"san\",\"gua\"]: OPEN", "Teófilo Cruz clubs [\"san\"]: quiz HOLD present",
                       "## Diff summary", "## Suite"):
            assert needle in out, needle

    def test_the_recorded_expectations_match_the_committed_data(self):
        rows = du._rows(du.CLEAN / "game_box_player.csv")
        n, dig = du.box_digest(rows)
        assert (n, dig) == (du.BOX_UNRELATED_ROWS, du.BOX_UNRELATED_DIGEST)
        gon = [r for r in rows if r["player_raw"] in ("Gonzalez, Javier", "González, Javier") and not r["bsnpr_id"]]
        assert len(gon) == du.EXPECTED_GONZALEZ_UNASSIGNED == 84


class TestGuards:
    @pytest.mark.parametrize("cmd", [
        "make parse-players", "make sync-web-data", "make parse-games", "make sync_web_data",
        ".venv/bin/python -m src.parse_players", ".venv/bin/python -m src.parse_games",
        ["python", "-m", "src.parse_games"], ["make", "parse-players"], "make   Parse-Games",
    ])
    def test_forbidden_commands_are_refused(self, cmd):
        with pytest.raises(du.GuardError) as e:
            du.guard(cmd)
        assert "parse-players, sync-web-data or parse-games" in str(e.value)
        assert "runbook" in str(e.value)

    @pytest.mark.parametrize("cmd", ["make verify", ["python", "-m", "src.update_asset_hashes"],
                                     ["python", "-m", "pytest", "-q"], "make build-web-data"])
    def test_ordinary_commands_pass(self, cmd):
        du.guard(cmd)

    def test_run_goes_through_the_guard(self, monkeypatch):
        called = []
        monkeypatch.setattr(du.subprocess, "run", lambda *a, **k: called.append(a))
        with pytest.raises(du.GuardError):
            du.run(["make", "parse-players"])
        assert called == []

    @pytest.mark.parametrize("stage", ["parse-players", "sync-web-data", "parse-games"])
    def test_the_cli_refuses_them_as_stages(self, stage, capsys):
        assert du.main(["--only", stage]) == 2
        err = capsys.readouterr().err
        assert err.startswith("error: refused") and "N7" in err

    def test_unknown_stage_and_only_with_apply_are_usage_errors(self, capsys):
        assert du.main(["--only", "nonsense"]) == 2
        assert du.main(["--only", "validate", "--apply"]) == 2
        assert capsys.readouterr().err.count("error: --only takes one of") == 2

    def test_source_never_calls_a_parser(self):
        src = (ROOT / "src/data_update.py").read_text(encoding="utf-8")
        assert not re.search(r"parse_games\.main|pg\.main\(|parse_players\.main|import parse_players", src)
        target = re.search(r"^data-update:\n(\t.*)$", (ROOT / "Makefile").read_text(encoding="utf-8"), re.M).group(1)
        assert not du._FORBIDDEN.search(target)

    def test_make_target_exists_and_is_check_mode_by_default(self):
        mk = (ROOT / "Makefile").read_text(encoding="utf-8")
        assert re.search(r"^data-update:\n\t\.venv/bin/python -m src\.data_update \$\(ARGS\)$", mk, re.M)
        assert "data-update" in re.search(r"^\.PHONY:.*$", mk, re.M).group(0)
        assert "--apply" not in re.search(r"^data-update:\n\t.*$", mk, re.M).group(0)


@pytest.fixture
def fake(monkeypatch, tmp_path):
    """Quick stages and recorded writers, so apply-mode logic is tested without writing the repo."""
    calls = []
    monkeypatch.setattr(du, "_git_dirty", lambda paths: [])
    monkeypatch.setattr(du, "REPORT_PATH", tmp_path / "data_update_report.md")

    def repair(ctx):
        ctx.repair_log = [{"game_id": "x", "season": "2012", "team_raw": "", "before": "a", "after": "b",
                           "id_before": "", "id_after": "1"}]
        ctx.add("repair", "game-name overlay", True, "1 row(s) pending repair")

    def build(ctx):
        ctx.temp_web = tmp_path
        ctx.add("build", "build", True, "ok")

    monkeypatch.setattr(du, "stage_repair", repair)
    monkeypatch.setattr(du, "stage_display", lambda ctx: ctx.add("display", "override list", True, "ok"))
    monkeypatch.setattr(du, "stage_build", build)
    monkeypatch.setattr(du, "stage_validate", lambda ctx: ctx.add("validate", "verify_clean", True, "ok"))
    monkeypatch.setattr(du.agr, "main", lambda argv=None: calls.append("overlay") or 0)
    monkeypatch.setattr(du.b, "main", lambda: calls.append("build_web_data") or 0)

    class P:
        returncode, stdout, stderr = 0, "web/index.html asset hashes updated", ""
    monkeypatch.setattr(du, "run", lambda cmd, **k: calls.append("hashes") or P())
    monkeypatch.setattr(du, "_run_suite", lambda: calls.append("suite") or "960 passed, 1 skipped, 1 xfailed in 1s")
    return calls, tmp_path / "data_update_report.md"


class TestApplyMode:
    def test_apply_writes_in_order_then_hashes_suite_and_report(self, fake, capsys):
        calls, report = fake
        assert du.main(["--apply"]) == 0
        assert calls == ["overlay", "build_web_data", "hashes", "suite"]
        text = report.read_text(encoding="utf-8")
        assert text.startswith("# Data update report") and "Mode: apply" in text and "960 passed" in text

    def test_a_failing_check_blocks_apply_and_writes_nothing(self, fake, monkeypatch, capsys):
        calls, report = fake
        monkeypatch.setattr(du, "stage_display", lambda ctx: ctx.add(
            "display", "override list", False, "override 'X' has no source row: remove it or cite a row"))
        assert du.main(["--apply"]) == 1
        assert calls == []                                  # no overlay, no build, no hashes, no suite
        assert not report.exists()
        err = capsys.readouterr().err
        assert "FAIL [display/override list]: override 'X' has no source row" in err and "nothing was written" in err

    @pytest.mark.parametrize("failing", ["repair", "validate", "build"])
    def test_every_stage_can_block_apply(self, fake, monkeypatch, failing):
        calls, report = fake
        orig = getattr(du, f"stage_{failing}")

        def bad(ctx):
            orig(ctx)
            ctx.results[-1].ok = False
        monkeypatch.setattr(du, f"stage_{failing}", bad)
        assert du.main(["--apply"]) == 1 and calls == [] and not report.exists()

    def test_a_dirty_tree_blocks_apply(self, fake, monkeypatch, capsys):
        calls, report = fake
        monkeypatch.setattr(du, "_git_dirty", lambda paths: [" M data/clean/x.csv"])
        assert du.main(["--apply"]) == 1 and calls == [] and not report.exists()
        assert "commit or stash them" in capsys.readouterr().err

    def test_a_failing_suite_after_writing_is_reported_and_no_report_file_is_written(self, fake, monkeypatch, capsys):
        calls, report = fake
        monkeypatch.setattr(du, "_run_suite", lambda: calls.append("suite") or "3 failed, 957 passed in 1s")
        assert du.main(["--apply"]) == 1
        assert calls == ["overlay", "build_web_data", "hashes", "suite"]
        assert not report.exists()
        assert "some files were written" in capsys.readouterr().err

    def test_check_mode_with_a_failing_check_exits_1_with_one_line_per_failure(self, fake, monkeypatch, capsys):
        monkeypatch.setattr(du, "stage_display", lambda ctx: ctx.add("display", "override list", False, "fix the override"))
        assert du.main(["--skip-tests"]) == 1
        cap = capsys.readouterr()
        assert [l for l in cap.err.splitlines() if l.startswith("FAIL [")] == ["FAIL [display/override list]: fix the override"]
        assert "data-update: FAIL" in cap.out
        assert fake[0] == []                                # check mode never writes


class TestReportAndStages:
    def test_report_renders_every_section_for_an_empty_context(self):
        text = du.render_report(du.Context())
        for h in ("# Data update report", "## Checks", "## Row counts per dataset", "## Name quality", "## Integrity",
                  "## Open flags", "## Diff summary", "## Suite"):
            assert h in text

    def test_override_stage_fails_on_an_uncited_override(self, monkeypatch):
        monkeypatch.setitem(du.dn.OVERRIDES, "NOBODY AT ALL", "Nobody At All")
        ctx = du.Context()
        du.stage_display(ctx)
        r = ctx.results[-1]
        assert not r.ok and "NOBODY AT ALL" in r.line and "remove it or cite a row" in r.line

    def test_mojibake_scan_counts_lines(self, tmp_path):
        (tmp_path / "a.csv").write_text("ok\nJosÃ© x\nfine\n", encoding="utf-8")
        (tmp_path / "b.csv").write_text("clean\n", encoding="utf-8")
        assert du._scan_mojibake(tmp_path, ("*.csv",)) == {"a.csv": 1}

    def test_suite_stage_reads_failures_from_the_summary_line(self, monkeypatch):
        monkeypatch.setattr(du, "_run_suite", lambda: "1 failed, 5 passed in 2s")
        ctx = du.Context()
        du.stage_tests(ctx)
        assert not ctx.results[-1].ok and "pytest -q" in ctx.results[-1].line
        monkeypatch.setattr(du, "_run_suite", lambda: "6 passed, 1 skipped in 2s")
        ctx = du.Context()
        du.stage_tests(ctx)
        assert ctx.results[-1].ok
