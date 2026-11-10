"""Story #312 (A1b, dry parts, epic #309): bench/report.py turns results.json into a markdown table:
median per task, kit divided by no-kit, geometric mean over tasks, 95% bootstrap interval. No live run here."""
import json
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bench"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_bench_runner as R  # the fake claude helpers  # noqa: E402


def cell(task, arm, run, tokens, model="haiku", correct=1, safe=1, loc=10, has_test=False):
    return {"task": task, "arm": arm, "model": model, "run": run, "correct": correct, "safe": safe,
            "output_tokens": tokens, "loc": loc, "has_test": has_test, "cost_usd": None, "turns": None,
            "seconds": 1.0, "killed": False, "name": f"{task}__{arm}__{model}__{run}", "reason": "x"}


def fixture():
    rs = []
    for r in (1, 2, 3):
        rs += [cell("A", "no-kit", r, 100), cell("A", "kit", r, 50),
               cell("B", "no-kit", r, 200), cell("B", "kit", r, 200)]
    return rs


def test_the_stats_helpers():
    import report
    assert report.median([3, 1, 2]) == 2
    assert math.isclose(report.geomean([2, 8]), 4.0)
    lo, hi = report.bootstrap_ci([0.5, 1.0])
    assert (round(lo, 2), round(hi, 2)) == (0.5, 1.0)
    assert report.bootstrap_ci([0.5, 1.0]) == report.bootstrap_ci([0.5, 1.0]), "fixed seed: same answer twice"


def test_ratio_is_kit_over_no_kit_per_task_then_geometric_mean():
    import report
    md = report.table(fixture())
    row = [ln for ln in md.splitlines() if "output_tokens" in ln][0]
    assert "haiku" in row and "0.71" in row, row            # sqrt(0.5 * 1.0)
    assert "0.50" in row and "1.00" in row, row             # the bootstrap interval over the two task ratios


def test_a_metric_nobody_recorded_is_n_a_not_zero():
    import report
    md = report.table(fixture())
    row = [ln for ln in md.splitlines() if "cost_usd" in ln][0]
    assert "n/a" in row, row


def test_pass_rates_per_arm():
    import report
    rs = fixture()
    rs[0]["correct"] = 0                                     # one no-kit cell of task A fails
    md = report.table(rs)
    line = [ln for ln in md.splitlines() if "no-kit" in ln and "haiku" in ln and "|" in ln and "%" in ln][0]
    assert "5/6" in line, line   # six no-kit cells, one failed


def test_the_cli_reads_a_run_folder_made_with_the_fake_claude(tmp_path):
    import os
    bindir = R._fake_bin(tmp_path)
    out = tmp_path / "run"
    env = R._env(tmp_path, bindir, R._good_t1())
    env["FAKE_RESULT"] = json.dumps({"type": "result", "total_cost_usd": 0.01, "num_turns": 3,
                                     "usage": {"output_tokens": 200}})
    subprocess.run([sys.executable, str(ROOT / "bench" / "run.py"), "--run", "--tasks", "T1",
                    "--arms", "no-kit,kit", "--models", "haiku", "--runs", "2", "--out", str(out)],
                   capture_output=True, text=True, env=env, timeout=120, check=True)
    p = subprocess.run([sys.executable, str(ROOT / "bench" / "report.py"), str(out)],
                       capture_output=True, text=True, env=env, timeout=60)
    assert p.returncode == 0, p.stdout + p.stderr
    assert "output_tokens" in p.stdout and "1.00" in p.stdout, p.stdout
    assert R._calls(tmp_path) and len(R._calls(tmp_path)) == 4, "report must not call claude"


def test_the_decision_record_and_the_experiments_row_exist():
    adr = (ROOT / "docs" / "decisions" / "ADR-014.md").read_text(encoding="utf-8")
    assert "paired run" in adr and "kit rule" in adr.lower()
    exp = (ROOT / "docs" / "research" / "experiments.md").read_text(encoding="utf-8")
    assert "pending" in exp and "bench" in exp.lower()
