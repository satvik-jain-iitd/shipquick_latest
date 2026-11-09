"""Story #225: the one reader for `kit_branch:` in a child's shipquick-call.yml, shared by adopt.sh,
adoption_scan.py and review_merge.sh, plus the rule for that branch's protection.

A rule-24 child reads its submodule pin, hooks and .shipquick/roles.yml from the kit branch. So a
direct push to that branch could add an account to roles.yml. The kit branch must be protected
and must require pull request reviews.

Usage:
  python3 scripts/kit_branch.py parse < shipquick-call.yml
      prints the branch (nothing when unset); exit 1 and the reason when the value is bad
  python3 scripts/kit_branch.py protection <owner/repo> <branch>
      exit 0 "protected", or exit 1 and the reason (needs gh; reading protection needs Administration: read)
"""
import json
import re
import subprocess
import sys

LINE = re.compile(r"^\s*kit_branch:(.*)$", re.M)
NAME = re.compile(r"[A-Za-z0-9_][A-Za-z0-9._/-]*")


def parse(text: str) -> tuple[str | None, str | None]:
    """(branch, None), (None, None) when unset, or (None, reason) when the value is not a plain branch name."""
    m = LINE.search(text)
    if not m:
        return None, None
    raw = m.group(1)
    if "${{" in raw:
        return None, "kit_branch must be a plain branch name, not a ${{ }} expression"
    value = re.sub(r"(^|\s)#.*$", "", raw).strip().strip("'\"")
    if not NAME.fullmatch(value) or ".." in value or value.endswith((".lock", "/", ".")):
        return None, f"kit_branch is not a branch name: {value!r}"
    return value, None


def protection_gap(branch: str, data) -> str | None:
    """data: GitHub's branches/<b>/protection answer, or None when the call failed (404 = not protected)."""
    if not data:
        return (f"kit branch {branch} has no branch protection, or it cannot be read (the token needs "
                "Administration: read). Protect it and require pull request reviews")
    if not data.get("required_pull_request_reviews"):
        return f"kit branch {branch} is protected but does not require pull request reviews, so a direct push can change roles.yml"
    return None


def _gh_protection(repo: str, branch: str):
    r = subprocess.run(["gh", "api", f"repos/{repo}/branches/{branch}/protection"], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


def main(argv: list[str]) -> int:
    if argv[:1] == ["parse"] and len(argv) == 1:
        branch, why = parse(sys.stdin.read())
        if why:
            print(why)
            return 1
        if branch:
            print(branch)
        return 0
    if argv[:1] == ["protection"] and len(argv) == 3:
        why = protection_gap(argv[2], _gh_protection(argv[1], argv[2]))
        print(why or "protected")
        return 1 if why else 0
    print(__doc__.split("Usage:", 1)[1].strip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
