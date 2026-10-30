"""Story #131: a disable comment or a new ignore-file entry, on an ADDED line, fails a PR unless its
body names the ADR that justifies it. The config a check reads can't be loosened by the same PR the
check is supposed to be judging -- a silent `eslint-disable` is exactly that kind of loosening.

Usage: python3 scripts/check_disable_comments.py --base <ref> [--repo <path>] [--body-file <f>]
Exit 0 and "no disable comments on added lines", or exit 1 and the list of hits (first line: a reason).
"""
import argparse
import re
import subprocess
import sys

DISABLE = re.compile(r"eslint-disable|stylelint-disable|swiftlint:disable|@ts-nocheck|@Suppress\(")
# Only the file types these linters actually read: a Python or Markdown file that defines, tests,
# or documents this very check has to contain these strings as data, not as a real disable directive.
CODE_EXT = re.compile(r"\.(ts|tsx|js|jsx|mjs|cjs|vue|svelte|astro|css|scss|less|swift|kt|kts|m|mm)$")
IGNORE_FILE = re.compile(r"(^|/)\.?[\w-]*ignore$")
ADR_LINE = re.compile(r"^ADR:\s*docs/decisions/ADR-\d+\.md\s*$", re.M)


def added_lines(diff_text: str):
    """(path, text) for every truly-added line (a "+" line, never the "+++" file header)."""
    path = None
    out = []
    for line in diff_text.splitlines():
        if line.startswith("+++ "):
            p = line[4:].strip()
            path = None if p == "/dev/null" else re.sub(r"^b/", "", p)
            continue
        if line.startswith("+") and not line.startswith("+++") and path:
            out.append((path, line[1:]))
    return out


def check(diff_text: str, pr_body: str) -> str | None:
    hits = []
    for path, text in added_lines(diff_text):
        if CODE_EXT.search(path) and DISABLE.search(text):
            hits.append(f"{path}: {text.strip()[:80]}")
        elif IGNORE_FILE.search(path) and text.strip() and not text.strip().startswith("#"):
            hits.append(f"{path}: new ignore-file entry: {text.strip()[:80]}")
    if not hits:
        return None
    if ADR_LINE.search(pr_body or ""):
        return None
    return "disable comment(s) or ignore-file entries added on new lines, with no ADR named (`ADR: docs/decisions/ADR-NNN.md`):\n" + "\n".join(hits)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="the branch this PR is diffed against, e.g. origin/dev")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--body-file")
    a = ap.parse_args()
    diff = subprocess.run(["git", "diff", "--unified=0", f"{a.base}...HEAD"], cwd=a.repo, capture_output=True, text=True, check=True).stdout
    body = open(a.body_file, encoding="utf-8").read() if a.body_file else ""
    why = check(diff, body)
    print(why or "no disable comments on added lines")
    return 1 if why else 0


if __name__ == "__main__":
    sys.exit(main())
