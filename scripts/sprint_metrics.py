"""One row of numbers per pull request (story #568). Pure: no gh, no network.

pr_row(pr, runs, issue) takes dicts shaped like `gh pr view --json number,createdAt,mergedAt,reviews`,
`gh run list --json conclusion` and `gh issue view --json number,createdAt`.
"""
from datetime import datetime


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
