#!/usr/bin/env python3
"""Story #422 (F5, epic #86): every job in checks.yml except `features`, `adoption` and `gate` is wired to exactly one feature
flag (read in its `if:` from the `features` job's output), and the `gate` waits for all of them and fails only on a failed or
cancelled job, never on a skipped one. A job added with no flag fails this check, named. Text only (CI has no PyYAML).

  check_features_wiring.py [--workflow PATH] [--defaults PATH]    exit 0 clean, 1 with one problem per line
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UNFLAGGED = {"features", "adoption", "gate"}
FLAG = re.compile(r"fromJSON\(needs\.features\.outputs\.flags\)\['([^']+)'\]")


def split_jobs(text):
    body = text.split("\njobs:\n", 1)[1]
    parts = re.split(r"^  ([a-z][a-z0-9-]*):[ \t]*\n", body, flags=re.M)
    return {parts[i]: parts[i + 1] for i in range(1, len(parts) - 1, 2)}


def job_if(block):
    m = re.search(r"^    if: (.*)$", block, re.M)
    return m.group(1) if m else ""


def gated_jobs(text):
    """{job: flag id} for every job that reads a flag in its `if:`."""
    return {n: FLAG.findall(job_if(b))[0] for n, b in split_jobs(text).items() if n not in UNFLAGGED and FLAG.findall(job_if(b))}


def gate_needs(text):
    m = re.search(r"needs: \[([^\]]*)\]", split_jobs(text)["gate"])
    return [x.strip() for x in m.group(1).split(",")] if m else []


def problems(text, defaults):
    out, jobs = [], split_jobs(text)
    for n, b in jobs.items():
        if n in UNFLAGGED:
            continue
        ids = FLAG.findall(job_if(b))
        if len(ids) != 1:
            out.append(f"job `{n}` reads {len(ids)} feature flags in its if: (it needs exactly one, from scripts/features_default.json)")
            continue
        if ids[0] not in defaults:
            out.append(f"job `{n}` reads the unknown flag `{ids[0]}`")
        elif defaults[ids[0]].get("locked"):
            out.append(f"job `{n}` reads the locked flag `{ids[0]}`: a locked feature has no switch")
        if not re.search(r"^    needs: \[features\]", b, re.M):
            out.append(f"job `{n}` does not have `needs: [features]`")
        if "needs.features.result == 'success'" not in job_if(b):
            out.append(f"job `{n}` does not check `needs.features.result == 'success'` before reading the flag")
    if "gate" not in jobs:
        return out + ["no `gate` job"]
    needs = gate_needs(text)
    for n in jobs:
        if n != "gate" and n not in needs:
            out.append(f"the gate does not wait for job `{n}` (add it to `needs:` of gate)")
    g = jobs["gate"]
    if "contains(needs.*.result, 'failure')" not in g or "contains(needs.*.result, 'cancelled')" not in g:
        out.append("the gate must fail on a failed or cancelled job")
    if "'skipped'" in g:
        out.append("the gate must not fail on a skipped job: a switched-off feature is skipped")
    return out


def job_runs(text, job, flags, event="pull_request", base_ref="dev"):
    """Evaluate a job's `if:` for a features map {id: bool}: True when the job runs, False when it is skipped."""
    expr = job_if(split_jobs(text)[job])
    expr = FLAG.sub(lambda m: repr(bool(flags[m.group(1)])), expr)
    expr = expr.replace("needs.features.result == 'success'", "True")
    expr = re.sub(r"github\.event_name == '([^']+)'", lambda m: repr(m.group(1) == event), expr)
    expr = re.sub(r"github\.base_ref == '([^']+)'", lambda m: repr(m.group(1) == base_ref), expr)
    expr = expr.replace("&&", " and ").replace("||", " or ")
    if re.search(r"[A-Za-z_.]+\.[A-Za-z_.]+", expr.replace("True", "").replace("False", "")):
        raise ValueError(f"job {job}: cannot evaluate `{expr}`")
    return bool(eval(expr, {"__builtins__": {}}, {}))   # only True, False, and, or, parentheses remain


def main(argv=None):
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--workflow", default=str(ROOT / ".github" / "workflows" / "checks.yml"))
    ap.add_argument("--defaults", default=str(ROOT / "scripts" / "features_default.json"))
    a = ap.parse_args(argv)
    found = problems(Path(a.workflow).read_text(encoding="utf-8"), json.loads(Path(a.defaults).read_text(encoding="utf-8"))["features"])
    for p in found:
        print(p)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
