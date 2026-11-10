#!/usr/bin/env python3
"""ShipQuick bench (story #311, A1a, epic #309). Selftest only: no live run here (that is A1b).

  python3 bench/run.py --selftest           every task's good reference must score correct and safe; its bad
                                            reference must be caught on the task's axis. Zero API calls.
  python3 bench/run.py --selftest --only ID one task

Parts of this file come from ponytail's benchmarks/agentic/run.py (MIT, DietrichGebert, 2026). The licence
text is kept in bench/LICENSE.ponytail.txt. The task list is bench/tasks.py.
"""
import argparse
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def _write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


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
    ap = argparse.ArgumentParser(description="ShipQuick bench, selftest only (story #311)")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--only", default=None)
    a = ap.parse_args(argv)
    if not a.selftest:
        ap.error("only --selftest exists in A1a; the live run is story #312 (A1b)")
    import tasks
    return 1 if selftest(tasks.TASKS, a.only) else 0


if __name__ == "__main__":
    sys.exit(main())
