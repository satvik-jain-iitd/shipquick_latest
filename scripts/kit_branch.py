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
  python3 scripts/kit_branch.py gate <owner/repo>
      story #260: exit 0 when `shipquick-checks / gate` is a required check on the default branch
      (branch protection or a ruleset), or exit 1, "gate not required ..." and the command that fixes it
  python3 scripts/kit_branch.py gate-command <owner/repo>
      prints that one command (a ruleset POST); nothing here ever runs it
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


GATE = "shipquick-checks / gate"
ACTIONS_APP = 15368   # the GitHub Actions app: only its check run may satisfy the gate, not any status poster
# Story #260: a ruleset on the default branch. It works whether or not branch protection already exists,
# and it never replaces checks the child already requires (the classic PUT .../required_status_checks does).
RULESET = json.dumps({
    "name": "shipquick gate", "target": "branch", "enforcement": "active",
    "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
    "rules": [{"type": "required_status_checks", "parameters": {
        "strict_required_status_checks_policy": False,
        "required_status_checks": [{"context": GATE, "integration_id": ACTIONS_APP}]}}],
}, separators=(",", ":"))


def gate_command(repo: str) -> str:
    return f"echo '{RULESET}' | gh api -X POST repos/{repo}/rulesets --input -"


def gate_gap(repo: str, branch: str, protection, rules) -> str | None:
    """protection: branches/<b>/protection (None = none or unreadable); rules: rules/branches/<b> (rulesets,
    None = the read failed). The gate counts only with its exact name, pinned to the GitHub Actions app."""
    if rules is None:
        return f"cannot read rules (403/404) of {repo} branch {branch}, so the gate cannot be checked. This is one test only: every other --check test still ran, each failure prints its own 'not adopted:' line, and no other line means they passed. Run: {gate_command(repo)}"
    rsc = (protection or {}).get("required_status_checks") or {}
    pinned = [c.get("app_id") for c in rsc.get("checks") or [] if c.get("context") == GATE]
    for rule in rules:
        if rule.get("type") == "required_status_checks":
            pinned += [c.get("integration_id") for c in rule.get("parameters", {}).get("required_status_checks", [])
                       if c.get("context") == GATE]
    if ACTIONS_APP in pinned:
        return None
    return (f"gate not required on {branch}: {GATE} from the GitHub Actions app ({ACTIONS_APP}) is not a required "
            f"check in its branch protection (or that cannot be read: needs Administration: read) or its rulesets. "
            f"Run: {gate_command(repo)}")


def _gh(path: str):
    r = subprocess.run(["gh", "api", path], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


def _gh_protection(repo: str, branch: str):
    return _gh(f"repos/{repo}/branches/{branch}/protection")


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
    if argv[:1] == ["gate"] and len(argv) == 2:
        info = _gh(f"repos/{argv[1]}")
        if not info:
            print(f"cannot read {argv[1]} (403/404), so the gate cannot be checked. Run: {gate_command(argv[1])}")
            return 1
        b = info["default_branch"]
        why = gate_gap(argv[1], b, _gh_protection(argv[1], b), _gh(f"repos/{argv[1]}/rules/branches/{b}"))
        print(why or f"gate required on {b}")
        return 1 if why else 0
    if argv[:1] == ["gate-command"] and len(argv) == 2:
        print(gate_command(argv[1]))
        return 0
    print(__doc__.split("Usage:", 1)[1].strip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
