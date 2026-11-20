"""One row of numbers per pull request (story #568). Pure: no gh, no network.

pr_row(pr, runs, issue) takes dicts shaped like `gh pr view --json number,createdAt,mergedAt,reviews`,
`gh run list --json conclusion` and `gh issue view --json number,createdAt`.
"""
import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import issue_notice  # noqa: E402  (the one gh reader)
from close_linked_issues import LINK  # noqa: E402  (the one rule for "this body links an issue")

gh_api = issue_notice.gh_api   # story #588: same use as scripts/adoption_scan.py


def _minutes(start, end):
    """Whole minutes from start to end (rounded down); None when either is missing."""
    if not start or not end:
        return None
    a = datetime.fromisoformat(start.replace("Z", "+00:00"))
    b = datetime.fromisoformat(end.replace("Z", "+00:00"))
    return int((b - a).total_seconds() // 60)


def pr_row(pr, runs, issue):
    issue = issue or {}
    conclusions = [r.get("conclusion") for r in runs]
    return {
        "number": pr["number"],
        "story": issue.get("number"),
        "story_minutes": _minutes(issue.get("createdAt"), pr.get("createdAt")),
        "merge_minutes": _minutes(pr.get("createdAt"), pr.get("mergedAt")),
        "runs": len(runs),
        "failed": conclusions.count("failure"),
        "cancelled": conclusions.count("cancelled"),
        "review_rounds": sum(1 for r in pr.get("reviews") or [] if r.get("state") == "CHANGES_REQUESTED"),
    }


COLUMNS = ["PR", "Story", "Story to PR (min)", "PR to merge (min)", "CI runs", "Failed", "Cancelled", "Review rounds"]
KEYS = ["story_minutes", "merge_minutes", "runs", "failed", "cancelled", "review_rounds"]


def _unreadable(n, what):
    return {"number": n, "error": f"could not read: {what}"}


def _read_pr(repo, n, api):
    """One PR's row, or a named could-not-read row. GET only, through api."""
    pull = api(f"repos/{repo}/pulls/{n}")
    if not pull:
        return _unreadable(n, "PR")
    reviews = api(f"repos/{repo}/pulls/{n}/reviews?per_page=100")
    if reviews is None:
        return _unreadable(n, "reviews")
    if len(reviews) >= 100:  # ponytail: the reviews list has no total, so exactly 100 also fails closed
        return _unreadable(n, "more than 100 reviews")
    created, merged = pull.get("created_at"), pull.get("merged_at")
    ref = quote(pull["head"]["ref"], safe="/")
    runs = api(f"repos/{repo}/actions/runs?branch={ref}&event=pull_request&created={created}..{merged}&per_page=100")
    if runs is None:
        return _unreadable(n, "runs")
    if runs.get("total_count", 0) > 100:
        return _unreadable(n, "more than 100 runs")
    issue = None
    for num in dict.fromkeys(LINK.findall(pull.get("body") or "")):
        found = api(f"repos/{repo}/issues/{num}")
        if not found:
            return _unreadable(n, "linked issue")
        if any(label.get("name") == "user-story" for label in found.get("labels") or []):
            issue = {"number": found["number"], "createdAt": found.get("created_at")}
            break
    return pr_row({"number": n, "createdAt": created, "mergedAt": merged, "reviews": reviews},
                  runs.get("workflow_runs") or [], issue)


def _cell(v):
    return "-" if v is None else str(v)


def main(argv=None, api=gh_api):
    ap = argparse.ArgumentParser(description="One day's merged PRs as a table of numbers.")
    ap.add_argument("--repo", default=os.environ.get("GH_REPO"))
    ap.add_argument("--date")
    ap.add_argument("--utc-offset", default="+00:00")
    try:
        a = ap.parse_args(argv)
    except SystemExit:
        return 2
    try:
        datetime.strptime(a.date or "", "%Y-%m-%d")
        ok = bool(re.fullmatch(r"[+-](0\d|1\d|2[0-3]):[0-5]\d", a.utc_offset)) and bool(a.repo)
    except ValueError:
        ok = False
    if not ok:
        print("usage: sprint_metrics.py --repo owner/name --date YYYY-MM-DD [--utc-offset +05:30]", file=sys.stderr)
        return 2
    off = quote(a.utc_offset, safe=":")
    found = api(f"search/issues?q=repo:{a.repo}+is:pr+is:merged+merged:{a.date}T00:00:00{off}..{a.date}T23:59:59{off}"
                "&per_page=100")
    if not found:
        print("could not read the search of merged PRs")
        return 1
    if found.get("incomplete_results") or found.get("total_count", 0) > 100:
        print("the search is incomplete or has more than 100 PRs; no table printed")
        return 1
    numbers = sorted(i["number"] for i in found.get("items") or [])
    if not numbers:
        print(f"no merged PRs on {a.date}")
        return 0
    rows = [_read_pr(a.repo, n, api) for n in numbers]
    print("| " + " | ".join(COLUMNS) + " |")
    print("|" + "---|" * len(COLUMNS))
    for r in rows:
        if "error" in r:
            print(f"| #{r['number']} | {r['error']} |")
        else:
            story = None if r["story"] is None else f"#{r['story']}"
            print("| " + " | ".join([f"#{r['number']}", _cell(story)] + [_cell(r[k]) for k in KEYS]) + " |")
    ok_rows = [r for r in rows if "error" not in r]
    t = {k: sum(r[k] or 0 for r in ok_rows) for k in KEYS}
    print(f"Total: {len(rows)} PRs, {t['story_minutes']} min story to PR, {t['merge_minutes']} min PR to merge, "
          f"{t['runs']} runs, {t['failed']} failed, {t['cancelled']} cancelled, {t['review_rounds']} review rounds")
    return 1 if len(ok_rows) < len(rows) else 0


if __name__ == "__main__":
    sys.exit(main())
