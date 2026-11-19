#!/usr/bin/env python3
"""Coverage ratchet (story #579, step 1 of 2): pass or fail for each changed file. Python files only.

judge(baseline, current, changed, min_new) is pure: baseline and current map path -> percent, changed is a list of paths.
It returns one row per changed file: {"path", "verdict" ("pass" or "fail"), "reason"}.

Command line: check_coverage.py --baseline FILE --current FILE --changed FILE [--min-new PERCENT]
The two reports are coverage.py JSON reports (`coverage json`); the changed file holds one path per line. Only paths that end
in .py and are not under tests/ are judged. Exit 0 when every row passes, 1 when any row fails or any input cannot be read.

Fail closed: both reports are read first; a report that is missing, not JSON, has no `files` map, or has a file with no number
in summary.percent_covered ends the run with exit 1. Nothing is ever skipped.
A changed file that is not in the baseline is new and must reach --min-new; it never gets a baseline of 0.
A changed file that is not in the current report fails.
Not here: running the tests, coverage, git, check_local.sh or CI (step 2).
"""
import argparse
import json
import sys
from pathlib import Path

# The owner sets the real number before step 2 wires this in; 80.0 is a placeholder.
MIN_NEW = 80.0


class ReportError(Exception):
    pass


def read_report(path):
    """Returns {path: percent}. Raises ReportError naming the file and the reason."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise ReportError(f"{path}: cannot read the report ({e})")
    files = data.get("files") if isinstance(data, dict) else None
    if not isinstance(files, dict):
        raise ReportError(f"{path}: the report has no `files` map")
    out = {}
    for name, info in files.items():
        pct = info.get("summary", {}).get("percent_covered") if isinstance(info, dict) else None
        if isinstance(pct, bool) or not isinstance(pct, (int, float)):
            raise ReportError(f"{path}: {name} has no number in summary.percent_covered")
        out[name] = float(pct)
    return out


def judge(baseline, current, changed, min_new=MIN_NEW):
    rows = []
    for path in changed:
        if path not in current:
            rows.append({"path": path, "verdict": "fail", "reason": "not in the current report"})
        elif path not in baseline:
            ok = current[path] >= min_new
            rows.append({"path": path, "verdict": "pass" if ok else "fail",
                         "reason": f"new file: {current[path]} against the floor {min_new}"})
        else:
            ok = current[path] >= baseline[path]
            rows.append({"path": path, "verdict": "pass" if ok else "fail",
                         "reason": f"{baseline[path]} -> {current[path]}"})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--current", required=True)
    ap.add_argument("--changed", required=True)
    ap.add_argument("--min-new", type=float, default=MIN_NEW)
    a = ap.parse_args()
    try:
        baseline = read_report(a.baseline)
        current = read_report(a.current)
        lines = Path(a.changed).read_text(encoding="utf-8").splitlines()
    except ReportError as e:
        print(f"FAIL {e}")
        return 1
    except OSError as e:
        print(f"FAIL {a.changed}: cannot read the changed list ({e})")
        return 1
    changed = [p.strip() for p in lines if p.strip().endswith(".py") and not p.strip().startswith("tests/")]
    rows = judge(baseline, current, changed, a.min_new)
    for r in rows:
        print(f"{r['verdict']} {r['path']}: {r['reason']}")
    return 0 if all(r["verdict"] == "pass" for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
