#!/usr/bin/env python3
"""Story #446: no commit subject over 72 characters on a branch's own commits.

  check_commit_subjects.py --base origin/dev [--max 72]

Looks at `<base>..HEAD`, merge commits left out (`--no-merges`; a plain commit that merely starts with "Merge " is checked) and
the exact form git writes for a revert, `Revert "<subject>"`, which quotes a subject that may itself be long. Prints
every long subject with its commit and length and exits 1; prints `commit subjects OK` and exits 0 when none is long; a base
that does not exist is exit 2 (an error is never a pass). Stdlib only. The same rule as the commit-msg hook, run on the
commits already made: CI runs it on a pull request, check_local.sh runs it before a push."""
import argparse
import re
import subprocess
import sys


REVERT = re.compile(r'^Revert ".+"$')   # git revert's own title; nothing looser is exempt


def main(argv=None):
    ap = argparse.ArgumentParser(prog="check_commit_subjects.py", add_help=False)
    ap.add_argument("--base", required=True)
    ap.add_argument("--max", type=int, default=72)
    a = ap.parse_args(argv)
    try:
        ok = subprocess.run(["git", "rev-parse", "--verify", "-q", a.base + "^{commit}"], capture_output=True, text=True)
        if ok.returncode != 0:
            print(f"check_commit_subjects.py: no such base `{a.base}` (fetch it first)", file=sys.stderr)
            return 2
        log = subprocess.run(["git", "log", "--no-merges", "--format=%h%x09%s", f"{a.base}..HEAD"], capture_output=True, text=True)
    except OSError as e:
        print(f"check_commit_subjects.py: cannot run git ({e})", file=sys.stderr)
        return 2
    if log.returncode != 0:
        print(f"check_commit_subjects.py: git log failed: {log.stderr.strip()}", file=sys.stderr)
        return 2
    bad = []
    for line in log.stdout.splitlines():
        h, _, subject = line.partition("\t")
        if len(subject) > a.max and not REVERT.match(subject):
            bad.append((h, subject))
    for h, subject in bad:
        print(f"commit subject over {a.max} characters ({len(subject)}): {h} {subject}")
    if bad:
        print("Reword each one to 72 characters or fewer (COMMIT_GUIDELINES.md).")
        return 1
    print("commit subjects OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
