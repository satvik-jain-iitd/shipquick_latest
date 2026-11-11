"""Story #319 (A15): a PR that changes code names the test file it turned red first, and that file is in the PR diff.

Usage:
  python3 scripts/check_tdd.py --body-file f --base origin/dev [--repo .] [--base-branch dev] [--head-branch feat/x]
Exit 0 with "tdd OK" or "tdd exempt: <why>"; exit 1 with the reason.

Assumptions (docs/assumptions.md, rows for story #319):
- A code file is any changed file that is not a .md or .txt file and not under docs/ or pm/.
- A PR with no code file is docs-only and exempt. A PR into main (promotion) or from main (back-merge) is exempt.
- The `## Red` section runs to the next `## ` heading. A test is named by its path, `tests/test_x.py`, optionally
  followed by `::test_name`, or a node:test file `roadmap/x.test.js` (story #81); the path must equal a file in the diff
  (added, modified or renamed, not deleted).
"""
import argparse
import re
import subprocess
import sys

RED = re.compile(r"^##\s+red\s*$", re.I | re.M)
NEXT_H2 = re.compile(r"^##\s", re.M)
TEST_PATH = re.compile(r"[\w./-]*(?:test_\w*\.py|\w+\.test\.js)")   # pytest files, and node:test files (story #81, roadmap/*.test.js)
DOC_SUFFIXES = (".md", ".txt")
DOC_DIRS = ("docs/", "pm/")
SHAPE = "write a `## Red` section that names the test file you saw fail, for example `- tests/test_widget.py::test_widget_rejects_empty`"


def is_code(path: str) -> bool:
    return not (path.endswith(DOC_SUFFIXES) or path.startswith(DOC_DIRS))


def exempt_reason(changed, base_branch, head_branch):
    if base_branch == "main":
        return "a promotion into main"
    if head_branch == "main":
        return "a back-merge from main"
    if not any(is_code(p) for p in changed):
        return "docs-only PR, no code file changed"
    return None


def red_section(body: str):
    """The text under `## Red`, or None when the body has no such heading."""
    m = RED.search(body)
    if not m:
        return None
    nxt = NEXT_H2.search(body, m.end())
    return body[m.end(): nxt.start() if nxt else len(body)]


def check(body, changed, base_branch="", head_branch=""):
    """Return (True, message) for a pass or an exemption, (False, reason) for a fail."""
    why = exempt_reason(changed, base_branch, head_branch)
    if why:
        return True, f"tdd exempt: {why}"
    section = red_section(body)
    if section is None:
        return False, f"the PR changes code but has no `## Red` section; {SHAPE}"
    named = [m.group(0).lstrip("./") for m in TEST_PATH.finditer(section)]
    if not named:
        return False, f"the `## Red` section names no test; {SHAPE}"
    missing = [n for n in dict.fromkeys(named) if n not in changed]
    if missing:
        return False, f"the `## Red` section names {', '.join(missing)}, which is not in the PR diff; name a test file this PR changes"
    return True, f"tdd OK: {', '.join(dict.fromkeys(named))}"


def changed_files(base, repo):
    out = subprocess.run(
        ["git", "-C", repo, "diff", "--name-only", "--diff-filter=ACMRT", "-M", f"{base}...HEAD"],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        raise SystemExit(f"could not read the diff against {base}: {out.stderr.strip()}")
    return [line for line in out.stdout.splitlines() if line]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--body-file", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--base-branch", default="")
    ap.add_argument("--head-branch", default="")
    args = ap.parse_args()
    with open(args.body_file, encoding="utf-8") as f:
        body = f.read()
    ok, msg = check(body, changed_files(args.base, args.repo), args.base_branch, args.head_branch)
    print(msg)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
