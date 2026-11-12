#!/usr/bin/env python3
"""Story #485 (ADR-018): one change map decides which slow CI jobs run, and the gate proves the result.

  change_map.py decide --base <ref> --head <ref> --event <name> --map <file> [--outputs <GITHUB_OUTPUT file>]
      Prints one JSON line {"android", "ios", "all", "reasons"}. With --outputs it appends android=, ios= and decision=.
      Fails closed: every doubt turns every area on. Doubts: not a pull request; the diff cannot be read; the map is
      missing, empty or broken; the map or this file changed in the PR; a changed path no row names (the reason names
      the path and says which row to add). A change to one phone job's own steps in ci.yml turns that job's area on;
      a change to the ui-changes job or the header of ci.yml turns every area on.
  change_map.py gate --decision <file> --needs <file> [--map <file>]
      Exit 0 when every job of an on area has result success, and every job of an off area has skipped or success.
      Exit 1 and one line per wrong job otherwise. A job with no result is wrong. --needs is toJSON(needs) of the gate.

Stdlib only. The map is JSON on purpose: the standard library reads no YAML (#464).
"""
import argparse
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path

GUARDED = {"scripts/change_map.json", "scripts/change_map.py"}
CI_PATH = ".github/workflows/ci.yml"


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def all_on(reason):
    return {"android": True, "ios": True, "all": True, "reasons": [reason]}


def matches(path, patterns):
    for p in patterns:
        if p.endswith("/**"):
            if path.startswith(p[:-2]):
                return True
        elif "/" not in p:
            if "/" not in path and fnmatch.fnmatchcase(path, p):
                return True
        elif fnmatch.fnmatchcase(path, p):
            return True
    return False


def job_block(text, name):
    """The text of one job of ci.yml, from its key to the next two-space key. None when it is not there."""
    inside, out = False, []
    for line in text.split("\n"):
        if re.match(r"^  [A-Za-z0-9_-]+:\s*$", line):   # a job key: the block ends at the next one
            if inside:
                break
            inside = line.strip() == f"{name}:"
            continue
        if inside:
            out.append(line)
    return "\n".join(out) if inside else None


def decision_parts(text):
    """The header of ci.yml (before `jobs:`) and the ui-changes job, the two parts that decide which jobs run."""
    return text.split("\njobs:", 1)[0], job_block(text, "ui-changes")


def load_map(path):
    m = json.loads(Path(path).read_text(encoding="utf-8"))
    areas, free = m["areas"], m["free"]
    assert isinstance(areas, dict) and areas and isinstance(free, list)
    for spec in areas.values():
        assert isinstance(spec["paths"], list) and spec["paths"] and isinstance(spec["jobs"], list)
        assert isinstance(spec.get("except", []), list)
    return areas, free


def decide(base, head, event, map_path):
    if event != "pull_request":
        return all_on(f"the event is {event!r}, not a pull request")
    try:
        areas, free = load_map(map_path)
    except Exception as e:  # missing, empty, broken or wrong shape: every area on
        return all_on(f"the map {map_path} is missing, empty or broken ({e.__class__.__name__})")
    try:
        mb = git("merge-base", base, head).strip()
        names = git("diff", "--name-only", "--no-renames", mb, head).split()
    except subprocess.CalledProcessError:
        return all_on(f"the diff of {base} and {head} cannot be read")
    if any(n in GUARDED for n in names):
        return all_on("the map or its reader changed in this PR, so nothing is skipped on this run")
    on, reasons = {a: False for a in areas}, []
    for n in names:
        hit = [a for a, spec in areas.items() if matches(n, spec["paths"]) and not matches(n, spec.get("except", []))]
        if hit:
            for a in hit:
                on[a] = True
            continue
        if matches(n, free):
            continue
        return all_on(f"{n}: no row in scripts/change_map.json names this path; add a row (an area, or free if it needs no slow job)")
    try:
        base_ci = git("show", f"{mb}:{CI_PATH}")
        head_ci = git("show", f"{head}:{CI_PATH}")
    except subprocess.CalledProcessError:
        return all_on(f"{CI_PATH} cannot be read at {mb} or {head}")
    if decision_parts(base_ci) != decision_parts(head_ci):
        return all_on(f"{CI_PATH}: the header or the ui-changes job changed, so nothing is skipped on this run")
    for area, spec in areas.items():
        for job in spec["jobs"]:
            if job_block(base_ci, job) != job_block(head_ci, job):
                on[area] = True
                reasons.append(f"{job}: its own steps changed in ci.yml, so area {area} runs")
    return {"android": on.get("android", False), "ios": on.get("ios", False), "all": False, "reasons": reasons}


def gate(decision, needs, areas):
    wrong = []
    for area, spec in areas.items():
        on = bool(decision.get(area))
        for job in spec["jobs"]:
            res = (needs.get(job) or {}).get("result")
            if res is None:
                wrong.append(f"{job}: no result in the needs of the gate (area {area} is {'on' if on else 'off'})")
            elif on and res != "success":
                wrong.append(f"{job}: {res}, but area {area} is on, so it must succeed")
            elif not on and res not in ("skipped", "success"):
                wrong.append(f"{job}: {res}, but area {area} is off, so it may only be skipped")
    return wrong


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("decide")
    d.add_argument("--base", required=True)
    d.add_argument("--head", default="HEAD")
    d.add_argument("--event", required=True)
    d.add_argument("--map", required=True)
    d.add_argument("--outputs")
    g = sub.add_parser("gate")
    g.add_argument("--decision", required=True)
    g.add_argument("--needs", required=True)
    g.add_argument("--map", default=str(Path(__file__).resolve().parent / "change_map.json"))
    a = ap.parse_args(argv)
    if a.cmd == "decide":
        try:
            out = decide(a.base, a.head, a.event, a.map)
        except Exception as e:  # any crash inside the reader is a doubt: every area on
            out = all_on(f"the reader failed ({e.__class__.__name__}); fails closed")
        print(json.dumps(out, sort_keys=True))
        if a.outputs:
            with open(a.outputs, "a", encoding="utf-8") as f:
                f.write(f"android={str(out['android']).lower()}\nios={str(out['ios']).lower()}\n")
                f.write("decision=" + json.dumps({"android": out["android"], "ios": out["ios"], "all": out["all"]}, sort_keys=True) + "\n")
        return 0
    decision = json.loads(Path(a.decision).read_text(encoding="utf-8"))
    needs = json.loads(Path(a.needs).read_text(encoding="utf-8"))
    areas, _ = load_map(a.map)
    wrong = gate(decision, needs, areas)
    for line in wrong:
        print(f"gate: {line}")
    if not wrong:
        print("gate: every phone job matches the change map")
    return 1 if wrong else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
