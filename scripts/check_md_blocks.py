"""Check markdown files for unclosed code blocks.

Reads the files git knows (tracked, or new and not ignored), so a gitignored file never fails the local hook while CI,
which has only the checkout, passes (bug #79). Outside a git repo it reads every .md under the current folder.
"""
import glob
import os
import subprocess
import sys


def md_files() -> list:
    r = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z", "--", "*.md"], capture_output=True, text=True)
    if r.returncode != 0:
        return [f for f in glob.glob("**/*.md", recursive=True) if ".git/" not in f]
    return [f for f in r.stdout.split("\0") if f and os.path.isfile(f)]   # a tracked file deleted from the tree is not read


def main() -> int:
    bad = []
    for f in md_files():
        ticks = open(f).read().count("```")
        if ticks % 2 != 0:
            bad.append(f)
    if bad:
        print("Unclosed code blocks in:", bad)
        return 1
    print("Markdown blocks OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
