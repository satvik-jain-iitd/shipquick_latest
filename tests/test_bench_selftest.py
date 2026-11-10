"""Story #311 (A1a, epic #309): `python3 bench/run.py --selftest` checks every task's good and bad reference
and makes ZERO API calls. Vendored from ponytail (MIT, DietrichGebert, copyright kept in bench/LICENSE.ponytail.txt)."""
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUN = ROOT / "bench" / "run.py"


def fake_claude_path(tmp_path):
    """A `claude` on PATH that records every call. The selftest must leave the log absent."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "claude-calls.log"
    fake = bin_dir / "claude"
    fake.write_text(f"#!/usr/bin/env bash\necho called >> '{log}'\nexit 0\n", encoding="utf-8")
    fake.chmod(0o755)
    return {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"}, log


def test_selftest_makes_no_claude_call(tmp_path):
    env, log = fake_claude_path(tmp_path)
    r = subprocess.run([sys.executable, str(RUN), "--selftest"], capture_output=True, text=True, env=env, timeout=600)
    assert r.returncode == 0, r.stdout + r.stderr
    assert not log.exists(), "the selftest called claude"


def test_selftest_checks_at_least_ten_tasks_and_every_one_passes(tmp_path):
    env, _ = fake_claude_path(tmp_path)
    r = subprocess.run([sys.executable, str(RUN), "--selftest"], capture_output=True, text=True, env=env, timeout=600)
    m = re.search(r"selftest (\d+)/(\d+) tasks pass", r.stdout)
    assert m, r.stdout
    passed, total = int(m.group(1)), int(m.group(2))
    assert total >= 10 and passed == total, r.stdout


def test_a_broken_reference_fails_the_selftest():
    # the instrument must catch a bad selftest: a task whose bad reference scores as safe must fail the run
    import importlib.util
    spec = importlib.util.spec_from_file_location("bench_run", RUN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    broken = {"broken": {"seed": {}, "good": {"f.txt": "x"}, "bad": {"f.txt": "x"}, "axis": "safe",
                         "score": lambda d: {"correct": 0, "safe": 1, "reason": "always fails"}}}
    assert mod.selftest(broken) > 0


def test_no_tasks_is_a_failure_not_a_silent_pass(tmp_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("bench_run", RUN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.selftest({}) > 0


def test_the_ponytail_license_is_kept_next_to_the_vendored_code():
    lic = (ROOT / "bench" / "LICENSE.ponytail.txt").read_text(encoding="utf-8")
    assert "MIT License" in lic and "DietrichGebert" in lic
