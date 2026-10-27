"""Close the story issues a merged PR links with "Closes #N".

GitHub only auto-closes when a PR merges into the default branch.
Feature PRs here merge into dev, so their issues stay open. This script
closes them by hand, after one yes from the owner.

Usage:
    python3 scripts/close_linked_issues.py <pr-number>         # dry run: list only
    python3 scripts/close_linked_issues.py <pr-number> --yes   # close them

Rules:
- Only a PR whose state is MERGED counts. Open or closed-unmerged: exit 1.
- Merged into the default branch: nothing to do, GitHub did it.
- Only issues linked by Closes/Fixes/Resolves #N. Never epics (label `epic`).
- Already closed issues are skipped.
"""
import json
import re
import subprocess
import sys

LINK = re.compile(r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#(\d+)", re.I)


def gh(*args):
    out = subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout
    return json.loads(out) if "--json" in args else out


def main() -> int:
    if len(sys.argv) < 2 or not sys.argv[1].isdigit():
        print(__doc__)
        return 2
    pr_number, do_close = int(sys.argv[1]), "--yes" in sys.argv

    # `gh repo view` ignores GH_REPO and reads the folder's git remotes (issue #88); `gh api` honours it.
    default = json.loads(gh("api", "repos/{owner}/{repo}"))["default_branch"]
    pr = gh("pr", "view", str(pr_number), "--json", "state,baseRefName,body")
    base = pr["baseRefName"]

    if pr["state"] != "MERGED":
        print(f"PR #{pr_number} is {pr['state']}, not MERGED. Closing nothing.")
        return 1
    if base == default:
        print(f"PR #{pr_number} merged into default branch {default}. GitHub closes the issues itself.")
        return 0

    to_close, skipped = [], []
    for n in dict.fromkeys(LINK.findall(pr["body"] or "")):
        info = gh("issue", "view", n, "--json", "state,labels")
        labels = {l["name"] for l in info["labels"]}
        if "epic" in labels:
            skipped.append((n, "epic, never closed by a PR"))
        elif info["state"] != "OPEN":
            skipped.append((n, f"already {info['state'].lower()}"))
        else:
            to_close.append(n)

    print(f"PR #{pr_number} merged into {base} (default is {default}).")
    for n, why in skipped:
        print(f"  skip  #{n}: {why}")
    for n in to_close:
        print(f"  close #{n}")
    if not to_close:
        print("Nothing to close.")
        return 0
    if not do_close:
        print(f"Dry run. Re-run with --yes to close {len(to_close)} issue(s).")
        return 0

    comment = f"Done in PR #{pr_number} (merged to {base})."
    for n in to_close:
        gh("issue", "close", n, "--comment", comment)
        print(f"  closed #{n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
