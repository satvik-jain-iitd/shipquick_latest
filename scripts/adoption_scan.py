"""Scheduled adoption scan (story #124, second layer): for each child repo in docs/children.md,
check its default branch for .github/workflows/shipquick-call.yml. Missing it, or pinned to a
ShipQuick commit more than $days old, opens (or reuses) one `feedback` issue in this repo naming
the child and the gap. A child session reports its own gaps with scripts/feedback.sh; this script
is ShipQuick noticing when a child never ran it at all.

A caller with `kit_branch: <b>` (story #225, a rule-24 child) is also checked on branch <b>: the
knowledge/shipquick_latest submodule there must equal the caller's pin, and .pre-commit-config.yaml
there must carry the ShipQuick hooks, and branch <b> must be protected with required pull request
reviews (roles.yml is read from it). That protection read needs Administration: read on a private
child's SHIPQUICK_CHILD_TOKEN. A caller without it is scanned exactly as before.

A line in docs/children.md may end with " private" (`owner/repo private`). A private child is
read with the SHIPQUICK_CHILD_TOKEN secret (fine-grained PAT, contents+metadata read only on that
repo — see docs/ADOPTION.md); public children keep the workflow's own github.token. A private
child with no SHIPQUICK_CHILD_TOKEN configured prints one line and is skipped: no daily issue,
since the scan has no way to tell "not adopted" from "can't see it". The same holds for a private
child the token cannot read (a 404 or 403). Story #260: every such skip is named in the run summary
(`skipped <repo>: private, ...`) with a count, so a skip is never silent.

Usage: python3 scripts/adoption_scan.py [--children docs/children.md] [--days 14] [--dry-run]
Needs: gh (authenticated as the build account), network. A scan problem (a child unreachable) is
reported per child, never fatal; exit 2 is a usage error only.
"""
import argparse
import base64
import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import issue_notice  # noqa: E402  (story #497: the one issue-opening helper)
import kit_branch  # noqa: E402  (the one kit_branch parser, shared with adopt.sh and review_merge.sh)

ROOT = Path(__file__).resolve().parent.parent
REPO = "satvik-jain-iitd/shipquick_latest"
PIN = re.compile(r"^\s*shipquick_ref:\s*([0-9a-f]{40})", re.M)
CHILD_TOKEN_ENV = "SHIPQUICK_CHILD_TOKEN"


CHILD_LINE = re.compile(r"([\w.-]+/[\w.-]+)(\s+private)?")


def read_children(path) -> list[tuple[str, bool]]:
    """Only a line that is exactly `owner/repo` or `owner/repo private` is a child; prose is skipped."""
    out = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        m = CHILD_LINE.fullmatch(line.split("#", 1)[0].strip())
        if m:
            out.append((m[1], bool(m[2])))
    return out


gh_api = issue_notice.gh_api   # story #497: the one gh reader, shared with scripts/nightly_full_run.py


def check_child(child: str, fetch, days: int, today: datetime.datetime) -> str | None:
    """None when adopted and fresh; otherwise one line naming the gap."""
    info = fetch(f"repos/{child}")
    if info is None:
        return f"cannot read {child} (gh api failed)"
    branch = info["default_branch"]
    call = fetch(f"repos/{child}/contents/.github/workflows/shipquick-call.yml?ref={branch}")
    if call is None:
        return f"{child}: no .github/workflows/shipquick-call.yml on {branch}"
    body = base64.b64decode(call["content"]).decode("utf-8", "replace")
    m = PIN.search(body)
    if not m:
        return f"{child}: shipquick-call.yml on {branch} has no shipquick_ref pin"
    sha = m.group(1)
    kit, bad = kit_branch.parse(body)
    if bad:
        return f"{child}: shipquick-call.yml on {branch}: {bad}"
    if kit:   # story #225: a rule-24 child keeps the submodule, the hooks and roles.yml on its kit branch
        gap = kit_branch.protection_gap(kit, fetch(f"repos/{child}/branches/{kit}/protection"))
        if gap:
            return f"{child}: {gap}"
        sub = fetch(f"repos/{child}/contents/knowledge/shipquick_latest?ref={kit}")
        if not sub or sub.get("type") != "submodule":
            return f"{child}: no knowledge/shipquick_latest submodule on kit branch {kit}"
        if sub.get("sha") != sha:
            return f"{child}: caller on {branch} pins {sha[:7]}, the submodule on kit branch {kit} is at {str(sub.get('sha'))[:7]}"
        hooks = fetch(f"repos/{child}/contents/.pre-commit-config.yaml?ref={kit}")
        if not hooks or "check_local.sh" not in base64.b64decode(hooks.get("content", "")).decode("utf-8", "replace"):
            return f"{child}: .pre-commit-config.yaml on kit branch {kit} has no ShipQuick hooks"
    commit = fetch(f"repos/{REPO}/commits/{sha}")
    if commit is None:
        return f"{child}: pinned to {sha[:7]}, which {REPO} cannot find"
    date_str = commit["commit"]["committer"]["date"]
    commit_date = datetime.datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    age = (today - commit_date).days
    if age > days:
        return f"{child}: pinned to {sha[:7]}, {age} days old (over {days})"
    return None


def open_or_comment(child: str, why: str, dry_run: bool) -> None:
    title = f"feedback: {child}: not adopted"
    body = f"Project: {child}\n\n{why}\n\nFound by the scheduled adoption scan (scripts/adoption_scan.py)."
    issue_notice.open_or_comment(REPO, "feedback", title, body, child, dry_run, api=gh_api, note=why)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--children", default=str(ROOT / "docs" / "children.md"))
    p.add_argument("--days", type=int, default=14)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    today = datetime.datetime.now(datetime.timezone.utc)
    child_token = os.environ.get(CHILD_TOKEN_ENV)
    skipped = []   # story #260: a skip is never silent; each one is named again in the summary
    for child, is_private in read_children(args.children):
        token = child_token if is_private else None
        fetch = (lambda path, t=token: gh_api(path, token=t))
        if is_private and not token:
            skipped.append(f"skipped {child}: private, no token ({CHILD_TOKEN_ENV} not set)")
            continue
        if is_private and fetch(f"repos/{child}") is None:   # a 404 or 403 with a token looks like "not adopted" too
            skipped.append(f"skipped {child}: private, cannot read it with {CHILD_TOKEN_ENV} (404 or 403)")
            continue
        why = check_child(child, fetch, args.days, today)
        if why:
            print(why)
            open_or_comment(child, why, args.dry_run)
        else:
            print(f"{child}: adopted and fresh")
    print(f"summary: {len(skipped)} skipped")
    for line in skipped:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
