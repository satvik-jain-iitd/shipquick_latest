"""Story #319 (A15): a PR that changes code names the test file it turned red first, and that file is in the PR diff.

Usage:
  python3 scripts/check_tdd.py --body-file f --base origin/dev [--repo .] [--base-branch dev] [--head-branch feat/x]
Exit 0 with "tdd OK" or "tdd exempt: <why>"; exit 1 with the reason.

Assumptions (docs/assumptions.md, rows for story #319):
- A code file is any changed file that is not a .md or .txt file and not under docs/ or pm/.
- A PR with no code file is docs-only and exempt. A kit bump (story #454: the `knowledge/shipquick_latest` pin plus only files adopt.sh writes) and a gate-files PR (story #491: only files in scripts/gate_files.txt) are exempt too. The exempt set is the pin plus both list files, read from those files. A PR into main (promotion) or from main (back-merge) is exempt.
- The `## Red` section runs to the next `## ` heading. A test is named by its path, `tests/test_x.py`, optionally
  followed by `::test_name`, or a node:test file `roadmap/x.test.js` (story #81); the path must equal a file in the diff
  (added, modified or renamed, not deleted).
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

RED = re.compile(r"^##\s+red\s*$", re.I | re.M)
NEXT_H2 = re.compile(r"^##\s", re.M)
# Story #502 (feedback #501): the test file names the `## Red` section may name, one line per runner. Add a line to add a runner.
TEST_NAMES = [
    r"test_\w*\.py",                                   # pytest (story #319)
    r"\w+_test\.py",                                   # pytest or unittest, any folder
    r"\w+\.test\.(?:jsx|tsx|mjs|cjs|js|ts)(?![\w])",     # node:test, jest, vitest (story #81, roadmap/*.test.js)
    r"\w+\.spec\.(?:jsx|tsx|mjs|cjs|js|ts)(?![\w])",     # playwright, jasmine, angular (TypeScript children, #501)
    r"\w+_test\.go",                                   # go test
    r"\w+Tests?\.kt",                                  # kotlin (junit, kotest)
    r"\w+Tests?\.swift",                               # swift (XCTest)
]
TEST_PATH = re.compile(r"[\w./-]*(?:" + "|".join(TEST_NAMES) + r")(?!\w|\.\w)")   # FooTest.kts and x.test.tsx.snap are not tests; "x.test.ts." ends a sentence
TOKEN = re.compile(r"[\w./-]+\.\w+")   # a file-like word in the `## Red` section
DOC_SUFFIXES = (".md", ".txt")
DOC_DIRS = ("docs/", "pm/")
# Story #454: a kit bump moves the pin and rewrites the files adopt.sh owns. There is nothing to put a test on.
# The list of those files is one file, scripts/adopt_files.txt (exact paths); a test keeps it in step with adopt.sh.
BUMP_PIN = "knowledge/shipquick_latest"
# Story #491 (feedback #490): the gate files of a kit-branch child (scripts/gate_files.txt, ADR-017) are copied by
# `adopt.sh --gate-files`, a PR with no code of its own, so they are exempt too. Both lists are read here, never typed again.


class ListError(Exception):
    """A list file is missing, unreadable or empty. The check stops with one line; it never guesses the exempt set."""


def _list(name):
    try:
        text = (Path(__file__).resolve().parent / name).read_text(encoding="utf-8")
    except OSError:
        raise ListError(f"tdd: cannot read scripts/{name}; restore it, the exempt list is not guessed") from None
    paths = {line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#")}
    if not paths:
        raise ListError(f"tdd: scripts/{name} lists no paths; the exempt list is not guessed")
    return paths


try:
    BUMP_FILES = {BUMP_PIN} | _list("adopt_files.txt") | _list("gate_files.txt")
    LIST_ERROR = ""
except ListError as err:
    BUMP_FILES = {BUMP_PIN}
    LIST_ERROR = str(err)
SHAPE = "write a `## Red` section that names the test file you saw fail, for example `- tests/test_widget.py::test_widget_rejects_empty`"


def is_code(path: str) -> bool:
    return not (path.endswith(DOC_SUFFIXES) or path.startswith(DOC_DIRS))


def is_bump_file(path: str) -> bool:
    return path in BUMP_FILES


def exempt_reason(changed, base_branch, head_branch):
    if base_branch == "main":
        return "a promotion into main"
    if head_branch == "main":
        return "a back-merge from main"
    code = [p for p in changed if is_code(p)]
    if not code:
        return "docs-only PR, no code file changed"
    if BUMP_PIN in changed and all(is_bump_file(p) for p in code):
        return "a kit bump, only the ShipQuick pin and files adopt.sh writes changed"
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
        for tok in dict.fromkeys(TOKEN.findall(section)):   # story #502 point 4: only when the section names no test at all
            if tok in changed and not TEST_PATH.fullmatch(tok):
                return False, (f"the `## Red` section names {tok}, which is in the PR diff but is not a known test file name "
                               f"(see TEST_NAMES in scripts/check_tdd.py); name the test file, not a fixture or data file")
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
    if LIST_ERROR:
        print(LIST_ERROR)
        return 1
    with open(args.body_file, encoding="utf-8") as f:
        body = f.read()
    ok, msg = check(body, changed_files(args.base, args.repo), args.base_branch, args.head_branch)
    print(msg)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
