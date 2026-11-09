"""Story #153 (part 2 of #146) and #161: a render link can be approved on the code diff alone. So the
approving review's own body must name the PR's board and say the render was compared with it:
`Render: <board> -- matches` (case-insensitive; "match", "matches", "matching"; any dash).
Only a PR with a filled `Design board:` line needs it. scripts/review_merge.sh calls this only when the
PR's repo has configured docs/screens.txt, the same PRs check_frontend_design.sh asks a `Render:` line of.

Usage: python3 scripts/check_design_reviewed.py --pr-body-file <f> --review-body-file <f>
Exit 0 and "design review OK", or exit 1 and the reason.
"""
import argparse
import re
import sys

BOARD = re.compile(r"^Design board:[ \t]*(.*?)[ \t]*$", re.M)
COMPARED = re.compile(r"^\W*render:\s*(.+?)\s+[-–—]+\s*match(?:es|ing)?\b", re.I | re.M)


def check(pr_body: str, review_body: str) -> str | None:
    m = BOARD.search(pr_body)
    board = m.group(1).strip() if m else ""   # strip: a GitHub web-edited body ends lines with \r\n
    if not board or board.startswith("<"):
        return None
    named = [b.strip().strip("`").strip() for b in COMPARED.findall(review_body)]
    if any(b.lower() == board.strip("`").lower() for b in named):
        return None
    if named:
        return f"match failed: the PR names board `{board}`, the approval says `{named[0]}`; write `Render: {board} -- matches`"
    return f"the approving review does not say the render was compared with the board: write `Render: {board} -- matches` in the approval body"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pr-body-file", required=True)
    ap.add_argument("--review-body-file", required=True)
    a = ap.parse_args()
    with open(a.pr_body_file, encoding="utf-8") as p, open(a.review_body_file, encoding="utf-8") as r:
        why = check(p.read(), r.read())
    print(why or "design review OK")
    return 1 if why else 0


if __name__ == "__main__":
    sys.exit(main())
