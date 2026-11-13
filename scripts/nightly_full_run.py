#!/usr/bin/env python3
"""Story #497 (epic #485 item 7): a nightly full run of every CI job on dev, with one issue when it is red.

The change map (scripts/change_map.py, ADR-018) skips slow jobs by path. This is the net under it: once a night every job
runs, so a hole in the map shows within a day.

A scheduled run uses the workflow files of the default branch, not dev. So the timer (.github/workflows/nightly.yml) only
starts this script, and the script dispatches ci.yml on `dev` itself: every job then checks out dev, and the change map
already turns every area on for an event that is not a pull request or a push. No second rule.

  nightly_full_run.py [--repo owner/name] [--ref dev] [--wait-minutes 150] [--dry-run]
      1. dispatch ci.yml on the ref, find the run it started, wait for it (up to --wait-minutes);
      2. a green run opens nothing;
      3. a red run opens one issue (label `nightly`) that names each bad job and says whether it failed or never got a
         machine; a later red night comments on the same open issue (the shared helper, scripts/issue_notice.py).
  --dry-run dispatches nothing and changes nothing: it reads the latest dispatched run and prints what it would do.
Needs: gh, authenticated (GH_TOKEN) with actions: write and issues: write.
Exit 1 when the night cannot be read or reported: a failed dispatch, run list, run state, jobs list or issue list, or an
issue or comment that did not land. Never silence and never a guess: GitHub shows the red night to someone.
"""
import argparse
import datetime
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import issue_notice  # noqa: E402

TITLE = "nightly: the full CI run on dev is red"
LABEL = "nightly"
WORKFLOW = "ci.yml"
BAD = {"failure", "timed_out", "cancelled", "action_required", "startup_failure", "stale"}
FIND_SECONDS = 600   # how long a dispatched run may take to show up
POLL_SECONDS = 60
READ_FAILURES = 3    # failed reads of the run's state in a row before the night ends red


class NightError(Exception):
    """The night cannot be read: dispatch, run list, run state or jobs list failed."""


def classify(job):
    """None for a good job; otherwise (kind, detail). kind is "failed", "never got a machine" (only a job still queued or
    waiting at the deadline) or "cancelled before it started" (a completed job no runner took, cancelled with its run)."""
    status, conclusion = job.get("status"), job.get("conclusion")
    no_machine = not job.get("runner_name") and not (job.get("steps") or [])
    if status != "completed":   # queued, waiting or in progress at the deadline
        if status in ("queued", "waiting", "pending"):
            return "never got a machine", f"still {status} at the deadline, no runner took it"
        return "failed", f"still {status} at the deadline"
    if conclusion in BAD:
        if no_machine and conclusion == "cancelled":
            return "cancelled before it started", "cancelled, no runner took it"
        return "failed", f"conclusion {conclusion}" + (", no runner took it" if no_machine else "")
    return None   # success, skipped or neutral: the gate job judges the whole run


def problems(run, jobs):
    """The bad jobs of a run. An empty list is a green night."""
    if run is None:
        return [{"job": f"{WORKFLOW} run", "kind": "never got a machine", "detail": "the dispatched run did not appear"}]
    if run.get("status") == "completed" and run.get("conclusion") == "success":
        return []
    found = []
    for j in jobs:
        c = classify(j)
        if c:
            found.append({"job": j.get("name", "?"), "kind": c[0], "detail": c[1]})
    if len(found) > 1:   # the gate fails because another job did: name the real job, not the gate beside it
        found = [p for p in found if p["job"] != "gate"]
    return found or [{"job": f"{WORKFLOW} run", "kind": "failed", "detail": f"the run ended {run.get('status')}/{run.get('conclusion')} with no bad job"}]


def issue_text(run, found, today):
    url = (run or {}).get("html_url", "no run was found")
    sha = ((run or {}).get("head_sha") or "")[:7] or "unknown"
    lines = [f"The full CI run on dev was red on {today}.", "", f"Run: {url}", f"Commit: {sha}", "", "Jobs:"]
    lines += [f"- {p['job']}: {p['kind']} ({p['detail']})" for p in found]
    lines += ["", "Found by the nightly full run (scripts/nightly_full_run.py). A later red night comments here; close this issue when dev is green."]
    return "\n".join(lines)


def report(repo, run, jobs, today, api, run_cmd, dry_run=False):
    """"green", or what issue_notice did: "opened", "commented #<n>" or "dry-run"."""
    found = problems(run, jobs)
    if not found:
        return "green"
    if not dry_run:
        made = run_cmd(["gh", "label", "create", LABEL, "-R", repo, "--description", "Red nights of the full CI run on dev",
                        "--color", "D93F0B", "--force"], check=False)
        if made.returncode != 0:   # not fatal by itself: the issue create below fails when the label is really missing
            print(f"warning: gh label create {LABEL} failed (exit {made.returncode})")
    return issue_notice.open_or_comment(repo, LABEL, TITLE, issue_text(run, found, today), TITLE, dry_run, api=api, run=run_cmd)


def _ts(iso):
    return datetime.datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp()


def find_run(repo, ref, since, api, sleep, now, limit=FIND_SECONDS):
    """The newest dispatched run of ci.yml on the ref created at or after `since` (a minute of slack), or None."""
    start = now()
    while True:
        data = api(f"repos/{repo}/actions/workflows/{WORKFLOW}/runs?event=workflow_dispatch&branch={ref}&per_page=10")
        if data is None:   # "cannot read" is not "no run yet"
            raise NightError(f"cannot read the {WORKFLOW} runs of {repo}")
        for r in data.get("workflow_runs", []):
            if _ts(r["created_at"]) >= since - 60:
                return r
        if now() - start >= limit:
            return None
        sleep(POLL_SECONDS)


def wait_done(repo, run, deadline_seconds, api, sleep, now):
    """Poll the run until it is completed or the deadline passes; return the last state read."""
    start, failures, state = now(), 0, run
    while True:
        read = api(f"repos/{repo}/actions/runs/{run['id']}")
        if read is None:
            failures += 1
            if failures >= READ_FAILURES:
                raise NightError(f"cannot read run {run['id']} of {repo} ({failures} reads in a row failed)")
        else:
            failures, state = 0, read
            if state.get("status") == "completed":
                return state
        if now() - start >= deadline_seconds:
            return state
        sleep(POLL_SECONDS)


def nightly(repo, ref, wait_minutes, api=issue_notice.gh_api, run_cmd=subprocess.run, sleep=time.sleep, now=time.time, today=None, dry_run=False):
    today = today or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    started = now()
    if not dry_run:
        sent = run_cmd(["gh", "api", "-X", "POST", f"repos/{repo}/actions/workflows/{WORKFLOW}/dispatches", "-f", f"ref={ref}"], check=False)
        if sent.returncode != 0:
            raise NightError(f"cannot dispatch {WORKFLOW} on {ref} of {repo} (exit {sent.returncode})")
    run = find_run(repo, ref, 0 if dry_run else started, api, sleep, now, limit=0 if dry_run else FIND_SECONDS)   # a dry run looks once
    if run is None:
        return report(repo, None, [], today, api, run_cmd, dry_run)
    run = wait_done(repo, run, wait_minutes * 60, api, sleep, now)
    listed = api(f"repos/{repo}/actions/runs/{run['id']}/jobs?per_page=100")
    if listed is None:
        raise NightError(f"cannot read the jobs of run {run['id']} of {repo}")
    jobs = listed.get("jobs", [])
    return report(repo, run, jobs, today, api, run_cmd, dry_run)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", "satvik-jain-iitd/shipquick_latest"))
    ap.add_argument("--ref", default="dev")
    ap.add_argument("--wait-minutes", type=int, default=150)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    try:
        print(f"nightly full run on {a.repo}@{a.ref}: {nightly(a.repo, a.ref, a.wait_minutes, dry_run=a.dry_run)}")
    except (NightError, issue_notice.IssueError) as e:
        print(f"nightly full run on {a.repo}@{a.ref}: cannot finish: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
