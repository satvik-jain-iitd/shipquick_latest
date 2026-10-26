"""The pull request body must link its issue with `Closes #<n>` (story #70, docs/PR_RULES.md section 5). `Fixes #<n>` and `Resolves #<n>` count too: the rule is the LINK regex of close_linked_issues.py.

Usage: python3 scripts/check_closes.py --title "<PR title>" --author "<PR author login>" < body.md
Exit 0 and "Closes link OK", or exit 1 and the reason.
Exempt: titles that start with `release:` or `chore:` (also `release(scope):`, `chore(deps):`), which are release, sync and back-merge pull requests, and Dependabot.
The roadmap counts a story as done only when its issue is closed, so a story PR without a link leaves the page wrong.
"""
import argparse
import re
import sys

from close_linked_issues import LINK   # one rule for "this body links an issue", shared with the script that closes the issues

DEPENDABOT = ("dependabot[bot]", "app/dependabot")   # the login in the Actions event, and the one `gh pr view --json author` prints
EXEMPT_TITLE = re.compile(r"^(release|chore)(\([^)]*\))?!?: ")


def check(title: str, author: str, body: str) -> str | None:
    if EXEMPT_TITLE.match(title) or author in DEPENDABOT:
        return None
    if not LINK.search(body):
        return "the body has no `Closes #<n>` line (write the issue number, for example `Closes #70`). Release, sync and chore pull requests are exempt by title prefix."
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--author", default="")
    args = parser.parse_args()
    why = check(args.title, args.author, sys.stdin.read())
    print(why or "Closes link OK")
    return 1 if why else 0


if __name__ == "__main__":
    sys.exit(main())
