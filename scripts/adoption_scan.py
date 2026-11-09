"""Scheduled adoption scan (story #124, second layer): for each child repo in docs/children.md,
check its default branch for .github/workflows/shipquick-call.yml. Missing it, or pinned to a
ShipQuick commit more than $days old, opens (or reuses) one `feedback` issue in this repo naming
the child and the gap. A child session reports its own gaps with scripts/feedback.sh; this script
is ShipQuick noticing when a child never ran it at all.

A caller with `kit_branch: <b>` (story #225, a rule-24 child) is also checked on branch <b>: the
knowledge/shipquick_latest submodule there must equal the caller's pin, and .pre-commit-config.yaml
there must carry the ShipQuick hooks. A caller without it is scanned exactly as before.

A line in docs/children.md may end with " private" (`owner/repo private`). A private child is
read with the SHIPQUICK_CHILD_TOKEN secret (fine-grained PAT, contents+metadata read only on that
repo — see docs/ADOPTION.md); public children keep the workflow's own github.token. A private
child with no SHIPQUICK_CHILD_TOKEN configured prints one line and is skipped: no daily issue,
since the scan has no way to tell "not adopted" from "can't see it".

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

ROOT = Path(__file__).resolve().parent.parent
REPO = "satvik-jain-iitd/shipquick_latest"
PIN = re.compile(r"^\s*shipquick_ref:\s*([0-9a-f]{40})", re.M)
KIT = re.compile(r"^\s*kit_branch:\s*['\"]?([\w./-]+)", re.M)
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


def gh_api(path, token=None):
    env = dict(os.environ)
    if token:
        env["GH_TOKEN"] = token
    r = subprocess.run(["gh", "api", path], capture_output=True, text=True, env=env)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


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
    k = KIT.search(body)
    if k:   # story #225: a rule-24 child keeps the submodule and the hooks on its kit branch
        kit = k.group(1)
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


def scan_child(child: str, is_private: bool, fetch, days: int, today, has_token: bool) -> tuple[str | None, bool]:
    """Returns (message_or_None, should_file_issue). A private child with no secret is reported
    but never filed, since a 404 from a missing token looks identical to "not adopted"."""
    if is_private and not has_token:
        return (f"{child}: private, no {CHILD_TOKEN_ENV} configured — skipping (no daily issue)", False)
    return (check_child(child, fetch, days, today), True)


def open_or_comment(child: str, why: str, dry_run: bool) -> None:
    low_child = child.lower()
    existing = gh_api(f"repos/{REPO}/issues?labels=feedback&state=open") or []
    match = next((i for i in existing if low_child in i.get("title", "").lower()), None)
    title = f"feedback: {child}: not adopted"
    body = f"Project: {child}\n\n{why}\n\nFound by the scheduled adoption scan (scripts/adoption_scan.py)."
    if dry_run:
        print(f"[dry-run] would {'comment on #' + str(match['number']) if match else 'open'}: {why}")
        return
    if match:
        subprocess.run(["gh", "issue", "comment", str(match["number"]), "-R", REPO, "--body", body], check=False)
    else:
        subprocess.run(["gh", "issue", "create", "-R", REPO, "--label", "feedback", "--title", title, "--body", body], check=False)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--children", default=str(ROOT / "docs" / "children.md"))
    p.add_argument("--days", type=int, default=14)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    today = datetime.datetime.now(datetime.timezone.utc)
    child_token = os.environ.get(CHILD_TOKEN_ENV)
    for child, is_private in read_children(args.children):
        token = child_token if is_private else None
        fetch = (lambda path, t=token: gh_api(path, token=t))
        why, should_file = scan_child(child, is_private, fetch, args.days, today, bool(token))
        if why:
            print(why)
            if should_file:
                open_or_comment(child, why, args.dry_run)
        else:
            print(f"{child}: adopted and fresh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
