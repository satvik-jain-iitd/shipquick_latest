#!/usr/bin/env python3
"""ShipQuick bench (story #311, A1a, epic #309). Selftest only: no live run here (that is A1b).

  python3 bench/run.py --selftest           every task's good reference must score correct and safe; its bad
                                            reference must be caught on the task's axis. Zero API calls.
  python3 bench/run.py --selftest --only ID one task
  python3 bench/run.py --run --tasks T1 --arms no-kit,kit --models haiku --runs 1 --out DIR
                                            one headless `claude -p` per cell (story #331, A1a-2). Live: costs money.
  python3 bench/run.py --rescore DIR        recompute every score from the saved workdirs. Zero API calls.

Parts of this file come from ponytail's benchmarks/agentic/run.py (MIT, DietrichGebert, 2026). The licence
text is kept in bench/LICENSE.ponytail.txt. The task list is bench/tasks.py.
"""
import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

# Story #331. Model ids are the Claude 5 family ids from the environment notes; the flags are the ones
# ponytail's runner uses, so an arm differs only by the rules text it is given.
MODELS = {"haiku": "claude-haiku-5-5", "sonnet": "claude-sonnet-5-5"}
ARMS = ("no-kit", "kit")
CELL_TIMEOUT = 600
BASE_FLAGS = ["--permission-mode", "bypassPermissions", "--output-format", "json",
              "--setting-sources", "project,local", "--strict-mcp-config", "--disallowedTools", "Bash"]
CELL_ENV = {"CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1", "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"}


def _write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _kill_group(proc):
    """End this cell's own process group only, never the session that started the run."""
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError):
        proc.kill()


def run_cell(tid, arm, model, run_no, out_dir: Path, claude: str, timeout: int, rules: str | None) -> dict:
    """One headless claude -p in its own folder. The agent writes into work/; logs sit beside it, so the
    score never sees them."""
    name = f"{tid}__{arm}__{model}__{run_no}"
    cell = out_dir / name
    work = cell / "work"
    work.mkdir(parents=True, exist_ok=True)
    for fn, content in tasks_module().TASKS[tid].get("seed", {}).items():
        _write(work / fn, content)
    cmd = [claude, "-p", tasks_module().TASKS[tid]["prompt"], "--model", MODELS[model], *BASE_FLAGS]
    if rules:
        cmd += ["--append-system-prompt", rules]
    env = {**os.environ, **CELL_ENV}
    killed = False
    t0 = time.monotonic()
    with open(cell / "claude.json", "wb") as so, open(cell / "claude.stderr.txt", "wb") as se:
        proc = subprocess.Popen(cmd, cwd=str(work), stdout=so, stderr=se, env=env, start_new_session=True)
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            killed = True
            _kill_group(proc)
            proc.wait()
            se.write(f"\n[KILLED after {timeout}s timeout]".encode())
    cell_meta = {"name": name, "arm": arm, "model": model, "run": run_no, "task": tid,
                 "killed": killed, "returncode": proc.returncode, "seconds": round(time.monotonic() - t0, 1),
                 **read_metrics(cell / "claude.json")}
    (cell / "cell.json").write_text(json.dumps(cell_meta, indent=2), encoding="utf-8")
    return {**cell_meta, **score_work(tid, work)}


def read_metrics(path: Path) -> dict:
    """Cost, output tokens and turns from claude's JSON. A field that is not there is None, never 0."""
    none = {"cost_usd": None, "output_tokens": None, "turns": None}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return none
    if isinstance(data, list):   # a verbose run is a list of events; the result event is the last dict
        data = next((d for d in reversed(data) if isinstance(d, dict) and d.get("type") == "result"), {})
    if not isinstance(data, dict):
        return none
    usage = data.get("usage") if isinstance(data.get("usage"), dict) else {}
    return {"cost_usd": data.get("total_cost_usd"), "output_tokens": usage.get("output_tokens"),
            "turns": data.get("num_turns")}


def score_work(tid, work: Path) -> dict:
    r = tasks_module().TASKS[tid]["score"](work)
    sol = work / "solution.py"
    text = sol.read_text(encoding="utf-8") if sol.exists() else ""
    # shortcut: a test counts when solution.py has a `def test_` or a top-level assert; no test files are
    # allowed in the folder (extra files are unsafe). Upgrade when a task seeds a test file.
    return {"correct": r["correct"], "safe": r["safe"], "reason": r["reason"],
            "loc": len([ln for ln in text.splitlines() if ln.strip()]),
            "has_test": bool(re.search(r"^\s*def test_|^assert ", text, re.M))}


def tasks_module():
    import tasks
    return tasks


def default_out() -> Path:
    """A fresh folder in the system temp dir, outside any repo."""
    return Path(tempfile.mkdtemp(prefix="shipquick-bench-"))


def inside_git(path: Path) -> bool:
    """True when path, or its nearest existing parent, is in a git work tree. --setting-sources project,local
    would then load that repo's .claude settings into every arm, so a run folder must never be there."""
    anc = path
    while not anc.exists() and anc != anc.parent:
        anc = anc.parent
    try:
        r = subprocess.run(["git", "-C", str(anc), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    except OSError:
        return False
    return r.returncode == 0


def run_all(task_ids, arms, models, runs, workers, timeout, out_dir: Path, rules_text: str) -> list:
    claude = shutil.which("claude")
    if not claude:
        raise SystemExit("claude CLI not found on PATH")
    out_dir.mkdir(parents=True, exist_ok=True)
    jobs = [(t, a, m, r) for t in task_ids for a in arms for m in models for r in range(1, runs + 1)]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(run_cell, t, a, m, r, out_dir, claude, timeout,
                               rules_text if a == "kit" else None) for (t, a, m, r) in jobs]
        results = [f.result() for f in futures]
    (out_dir / "results.json").write_text(json.dumps({"results": results}, indent=2), encoding="utf-8")
    print_table(results)
    return results


def print_table(results):
    for r in results:
        flag = "killed" if r.get("killed") else ""
        print(f"{'ok ' if r['correct'] else '   '}{r['name']:32} correct={r['correct']} safe={r['safe']} {flag} {r['reason']}")
    print(f"ran {len(results)} cells")


def rescore(out_dir: Path) -> list:
    """Recompute every score from the saved workdirs. No claude call."""
    if not out_dir.is_dir():
        raise SystemExit(f"no run folder at {out_dir}")
    results = []
    for cell in sorted(p for p in out_dir.iterdir() if p.is_dir() and p.name.count("__") == 3):
        tid, arm, model, run_no = cell.name.split("__")
        if tid not in tasks_module().TASKS:
            continue
        meta = json.loads((cell / "cell.json").read_text(encoding="utf-8"))
        results.append({**meta, **score_work(tid, cell / "work")})
    (out_dir / "results.json").write_text(json.dumps({"results": results, "rescored": True}, indent=2), encoding="utf-8")
    print_table(results)
    return results


def selftest(task_table, only=None) -> int:
    """Returns the number of failures (0 is a pass). With no tasks it fails: nothing was verified."""
    passed = total = 0
    for tid, task in task_table.items():
        if only and tid != only:
            continue
        total += 1
        axis = task.get("axis", "safe")
        ok_all = True
        for kind in ("good", "bad"):
            with tempfile.TemporaryDirectory() as d:
                for fn, content in {**task.get("seed", {}), **task[kind]}.items():
                    _write(Path(d) / fn, content)
                r = task["score"](Path(d))
            ok = (r["correct"] == 1 and r["safe"] == 1) if kind == "good" else (r[axis] == 0)
            print(f"{'ok ' if ok else 'XX '} {tid:14} {kind:4} correct={r['correct']} safe={r['safe']} axis={axis}  {r['reason']}")
            ok_all = ok_all and ok
        passed += int(ok_all)
    if total == 0:
        print("selftest 0/0 tasks pass: no tasks are registered, so nothing was verified")
        return 1
    print(f"selftest {passed}/{total} tasks pass")
    return total - passed


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="ShipQuick bench (story #311, #331)")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--only", default=None)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--rescore", default=None, metavar="DIR")
    ap.add_argument("--tasks", default=None, help="comma list, default all")
    ap.add_argument("--arms", default="no-kit,kit")
    ap.add_argument("--models", default="haiku")
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--timeout", type=int, default=CELL_TIMEOUT)
    ap.add_argument("--out", default=None)
    ap.add_argument("--kit-rules", default=str(ROOT / "CLAUDE.md"))
    a = ap.parse_args(argv)
    tasks = tasks_module()
    if a.selftest:
        return 1 if selftest(tasks.TASKS, a.only) else 0
    if a.rescore:
        rescore(Path(a.rescore).resolve())
        return 0
    if not a.run:
        ap.error("pick one: --selftest, --run or --rescore")
    task_ids = [t.strip() for t in a.tasks.split(",")] if a.tasks else list(tasks.TASKS)
    arms = [x.strip() for x in a.arms.split(",")]
    models = [x.strip() for x in a.models.split(",")]
    for t in task_ids:
        if t not in tasks.TASKS:
            ap.error(f"unknown task {t}")
    for x in arms:
        if x not in ARMS:
            ap.error(f"unknown arm {x}; arms are {', '.join(ARMS)}")
    for m in models:
        if m not in MODELS:
            ap.error(f"unknown model {m}; models are {', '.join(MODELS)}")
    out = Path(a.out).resolve() if a.out else default_out()
    if inside_git(out):
        ap.error(f"--out {out} is inside a git work tree: the project settings there would load into every arm. "
                 "Use a folder outside any repo, or leave --out off for a temp folder")
    rules_text = Path(a.kit_rules).read_text(encoding="utf-8")
    run_all(task_ids, arms, models, a.runs, a.workers, a.timeout, out, rules_text)
    print(f"run folder: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
