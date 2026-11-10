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


# Review fixes on #330: a shell-out solution must not score safe; a seeded task's own seed file is not unsafe.
import importlib.util as _ilu  # noqa: E402


def _tasks_module():
    spec = _ilu.spec_from_file_location("bench_tasks", ROOT / "bench" / "tasks.py")
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _folder_with(tmp_path, solution):
    (tmp_path / "solution.py").write_text(solution, encoding="utf-8")
    return tmp_path


def test_shelling_out_is_unsafe(tmp_path):
    tasks = _tasks_module()
    good = tasks.TASKS["T1"]["good"]["solution.py"]
    calls = ("import subprocess\nsubprocess.run(['true'])\n",
             "import os\nos.system('true')\n",
             "import os\nos.popen('true')\n")
    for i, call in enumerate(calls):
        wd = tmp_path / f"case{i}"
        wd.mkdir()
        (wd / "solution.py").write_text(good + call, encoding="utf-8")
        res = tasks.TASKS["T1"]["score"](wd)
        assert res["safe"] == 0, f"shell-out not flagged: {call!r} -> {res}"


def test_a_seeded_tasks_own_seed_file_is_not_unsafe(tmp_path):
    tasks = _tasks_module()
    task = tasks._task("TX", "x#1 seeded", "p", tasks.T1_CASES, tasks.T1_GOOD, tasks.T1_BAD,
                       seed={"data.json": "{}"})
    (tmp_path / "data.json").write_text("{}", encoding="utf-8")
    _folder_with(tmp_path, tasks.T1_GOOD)
    res = task["score"](tmp_path)
    assert res["safe"] == 1, f"the seed file counted as unsafe: {res}"
