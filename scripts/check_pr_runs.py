#!/usr/bin/env python3
"""Story #496 (epic #485 items 15 and 16): which check rows of a pull request head count for the merge gate.

Usage: check_pr_runs.py --pr <number> --rollup-file <statusCheckRollup JSON> --runs-file <workflow runs of the head>
  The runs file is what `gh api repos/<repo>/actions/runs?head_sha=<sha> --paginate --jq '.workflow_runs[]'` prints:
  one JSON object per run (compact or pretty, the reader takes both).
Prints the rollup rows that count, as one JSON array, and exits 0. Exits 1 with one reason line when it cannot decide.

Rules, all read from the run a check row belongs to (the run id is in the row's detailsUrl):
  0. A pull_request run counts only when its `pull_requests` list is exactly this pull request. The list holds every open
     PR on the head, so another PR in it (alone or beside this one) refuses: two pull requests share this head. An empty
     list (a fork's run, or a run after the merge) names nobody and is not counted.
  1. Rows of a `push` or `workflow_dispatch` run are dropped. Such a run skips the PR-only jobs and starts later, so its
     green `gate` could replace a red PR result.
  2. Of the pull_request runs of one workflow, only the newest (highest run_number) counts. A run that a newer run of
     the same workflow and event replaced leaves stale rows (a `test` cancelled before the matrix expanded, next to
     `test (3.12)` of the next run); they are not counted.
  Rows of every other event (pull_request_target, schedule, ...) count as before this story.
A row with no run id (a commit status from another app) counts as before. A row whose run the list does not name is
a doubt, and a doubt refuses.
"""
import argparse
import json
import re
import sys

RUN_ID = re.compile(r"/actions/runs/(\d+)")


class Refuse(Exception):
    pass


def read_runs(text):
    """Every JSON value in the text, one after the other (a compact line each, or pretty-printed objects)."""
    dec, i, out = json.JSONDecoder(), 0, []
    while True:
        while i < len(text) and text[i].isspace():
            i += 1
        if i >= len(text):
            return out
        obj, i = dec.raw_decode(text, i)
        out.append(obj)


def counted(rollup, runs, pr):
    by_id = {r["id"]: r for r in runs}
    newest, dropped = {}, set()
    for r in runs:
        event = r.get("event")
        if event in ("push", "workflow_dispatch"):
            dropped.add(r["id"])                 # rule 1: these skip the PR-only jobs and start later
        elif event == "pull_request":
            numbers = [p.get("number") for p in r.get("pull_requests") or []]
            if any(n != pr for n in numbers):    # rule 0: the list is every open PR on the head
                raise Refuse(f"two pull requests share this head ({numbers}); the run {r['id']} cannot be told from this PR's")
            if numbers != [pr]:                  # an empty list (a fork's run) names nobody
                dropped.add(r["id"])
            elif r["workflow_id"] not in newest or r["run_number"] > newest[r["workflow_id"]]["run_number"]:
                newest[r["workflow_id"]] = r
    kept = {r["id"] for r in newest.values()}
    dropped |= {r["id"] for r in runs if r.get("event") == "pull_request"} - kept   # rule 2: replaced by a newer run
    rows = []
    for row in rollup:
        m = RUN_ID.search(row.get("detailsUrl") or "")
        if not m:
            rows.append(row)
            continue
        run_id = int(m.group(1))
        if run_id not in by_id:
            raise Refuse(f"check {row.get('name') or row.get('context')} comes from run {run_id}, which is not in the workflow runs of this head")
        if run_id not in dropped:
            rows.append(row)
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pr", type=int, required=True)
    ap.add_argument("--rollup-file", required=True)
    ap.add_argument("--runs-file", required=True)
    a = ap.parse_args(argv)
    try:
        rollup = json.load(open(a.rollup_file, encoding="utf-8"))
        runs = read_runs(open(a.runs_file, encoding="utf-8").read())
        print(json.dumps(counted(rollup, runs, a.pr)))
        return 0
    except Refuse as e:
        print(str(e))
        return 1
    except (OSError, ValueError, KeyError, TypeError) as e:   # unreadable or unexpected input: a doubt refuses
        print(f"cannot read the check rows or the workflow runs ({e.__class__.__name__})")
        return 1


if __name__ == "__main__":
    sys.exit(main())
