"""Story #331 (A1a-2, epic #309): the bench cell runner and --rescore. Zero real API calls: a fake
`claude` on PATH logs its argv and env, writes solution.py into its cwd, and is the only thing run."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "bench" / "run.py"
FAKE = """#!{py}
import json, os, sys, time
with open(os.environ["FAKE_LOG"], "a") as f:
    f.write(json.dumps({{"argv": sys.argv[1:], "cwd": os.getcwd(),
                         "env": {{k: os.environ.get(k, "") for k in
                                  ("CLAUDE_CODE_DISABLE_CLAUDE_MDS", "CLAUDE_CODE_DISABLE_AUTO_MEMORY")}}}}) + "\\n")
if os.environ.get("FAKE_MODE") == "hang":
    time.sleep(60)
with open("solution.py", "w") as f:
    f.write(open(os.environ["FAKE_SOLUTION"]).read())
print(json.dumps({{"type": "result", "result": "done"}}))
"""


def _fake_bin(tmp_path):
    bindir = tmp_path / "bin"
    bindir.mkdir()
    fake = bindir / "claude"
    fake.write_text(FAKE.format(py=sys.executable), encoding="utf-8")
    fake.chmod(0o755)
    return bindir


def _env(tmp_path, bindir, solution_text, mode="ok"):
    sol = tmp_path / "good_solution.py"
    sol.write_text(solution_text, encoding="utf-8")
    return {**os.environ, "PATH": f"{bindir}{os.pathsep}{os.environ['PATH']}",
            "FAKE_LOG": str(tmp_path / "calls.jsonl"), "FAKE_SOLUTION": str(sol), "FAKE_MODE": mode}


def _calls(tmp_path):
    p = tmp_path / "calls.jsonl"
    return [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []


def _good_t1():
    sys.path.insert(0, str(ROOT / "bench"))
    import tasks
    return tasks.TASKS["T1"]["good"]["solution.py"]


def test_one_cell_per_arm_runs_and_uses_the_real_flags(tmp_path):
    bindir = _fake_bin(tmp_path)
    out = tmp_path / "run"
    p = subprocess.run([sys.executable, str(BENCH), "--run", "--tasks", "T1", "--arms", "no-kit,kit",
                        "--models", "haiku", "--runs", "1", "--workers", "2", "--out", str(out)],
                       capture_output=True, text=True, env=_env(tmp_path, bindir, _good_t1()), timeout=120)
    assert p.returncode == 0, p.stdout + p.stderr
    for arm in ("no-kit", "kit"):
        assert (out / f"T1__{arm}__haiku__1" / "work" / "solution.py").exists(), arm
    calls = _calls(tmp_path)
    assert len(calls) == 2, calls
    for c in calls:
        argv = c["argv"]
        for flag in ("--permission-mode", "bypassPermissions", "--output-format", "json",
                     "--setting-sources", "project,local", "--strict-mcp-config", "--disallowedTools", "Bash"):
            assert flag in argv, (flag, argv)
        assert argv[argv.index("--model") + 1] == "claude-haiku-5-5"
        assert c["env"] == {"CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1", "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"}
        assert c["cwd"].endswith("work"), c["cwd"]          # the agent works in its own folder
    kit = [c for c in calls if "--append-system-prompt" in c["argv"]]
    assert len(kit) == 1, "only the kit arm gets the rules"


def test_rescore_gives_the_same_scores_and_makes_no_claude_call(tmp_path):
    bindir = _fake_bin(tmp_path)
    out = tmp_path / "run"
    env = _env(tmp_path, bindir, _good_t1())
    subprocess.run([sys.executable, str(BENCH), "--run", "--tasks", "T1", "--arms", "kit",
                    "--models", "haiku", "--runs", "1", "--out", str(out)],
                   capture_output=True, text=True, env=env, timeout=120, check=True)
    before = json.loads((out / "results.json").read_text())["results"]
    calls_before = len(_calls(tmp_path))
    p = subprocess.run([sys.executable, str(BENCH), "--rescore", str(out)],
                       capture_output=True, text=True, env=env, timeout=120)
    assert p.returncode == 0, p.stdout + p.stderr
    after = json.loads((out / "results.json").read_text())["results"]
    assert [(r["correct"], r["safe"]) for r in after] == [(r["correct"], r["safe"]) for r in before]
    assert before[0]["correct"] == 1 and before[0]["safe"] == 1
    assert len(_calls(tmp_path)) == calls_before, "rescore called claude"


def test_a_hung_cell_is_killed_at_the_timeout(tmp_path):
    bindir = _fake_bin(tmp_path)
    out = tmp_path / "run"
    t0 = time.monotonic()
    p = subprocess.run([sys.executable, str(BENCH), "--run", "--tasks", "T1", "--arms", "no-kit",
                        "--models", "haiku", "--runs", "1", "--timeout", "2", "--out", str(out)],
                       capture_output=True, text=True, env=_env(tmp_path, bindir, _good_t1(), mode="hang"),
                       timeout=120)
    assert time.monotonic() - t0 < 60, "the hung cell was not killed"
    assert p.returncode == 0, p.stdout + p.stderr
    cell = json.loads((out / "T1__no-kit__haiku__1" / "cell.json").read_text())
    assert cell["killed"] is True


def test_unknown_task_or_arm_is_refused(tmp_path):
    bindir = _fake_bin(tmp_path)
    for extra in (["--tasks", "T99"], ["--arms", "magic"]):
        p = subprocess.run([sys.executable, str(BENCH), "--run", "--models", "haiku", "--runs", "1",
                            "--out", str(tmp_path / "x"), *extra],
                           capture_output=True, text=True, env=_env(tmp_path, bindir, _good_t1()), timeout=120)
        assert p.returncode != 0, extra
    assert _calls(tmp_path) == []
