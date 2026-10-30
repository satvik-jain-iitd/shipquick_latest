"""Scheduled adoption scan (story #124, second layer): for each child repo in docs/children.md,
check its default branch for .github/workflows/shipquick-call.yml. Missing it, or pinned to a
ShipQuick commit more than $days old, opens (or reuses) one `feedback` issue in this repo naming
the child and the gap. A child session reports its own gaps with scripts/feedback.sh; this script
is ShipQuick noticing when a child never ran it at all.

Usage: python3 scripts/adoption_scan.py [--children docs/children.md] [--days 14] [--dry-run]
Needs: gh (authenticated as the build account), network. A scan problem (a child unreachable) is
reported per child, never fatal; exit 2 is a usage error only.
"""
import argparse
import base64
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "satvik-jain-iitd/shipquick_latest"
PIN = re.compile(r"^\s*shipquick_ref:\s*([0-9a-f]{40})", re.M)


def read_children(path) -> list[str]:
    out = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line and "/" in line:
            out.append(line)
    return out


def gh_api(path):
    r = subprocess.run(["gh", "api", path], capture_output=True, text=True)
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
    for child in read_children(args.children):
        why = check_child(child, gh_api, args.days, today)
        if why:
            print(why)
            open_or_comment(child, why, args.dry_run)
        else:
            print(f"{child}: adopted and fresh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
