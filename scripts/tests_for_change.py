#!/usr/bin/env python3
"""Story #570: print the Python test files a change can break (python tests only).

Rule: for each changed file, pick every tests/**/test_*.py whose text names the file's base name as a whole word, with or
without its extension. A changed test file picks itself. A changed .md that no test names is ignored. Any other file that no
test names, or a change list that cannot be read, prints "full suite: <reason>" first and then every test file.
Changed files: git diff origin/$BASE...HEAD plus staged, unstaged and untracked files. Prints one path per line.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path


def git_lines(root, *args):
    p = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.strip() or 'failed'}")
    return p.stdout.splitlines()


def changed_files(root, base):
    out = git_lines(root, "diff", "--name-only", f"origin/{base}...HEAD")
    out += git_lines(root, "diff", "--name-only", "HEAD")
    out += git_lines(root, "ls-files", "--others", "--exclude-standard")
    return sorted(set(out))


def select(root, changed):
    """Returns (reason or None, picked paths). A reason means the full suite."""
    tests = {p.relative_to(root).as_posix(): p.read_text(encoding="utf-8", errors="replace")
             for p in sorted(Path(root).glob("tests/**/test_*.py"))}
    picked, unnamed = set(), []
    for f in changed:
        if f in tests:
            picked.add(f)
            continue
        stem = Path(f).stem
        pat = re.compile(rf"(?<!\w)(?:{re.escape(Path(f).name)}|{re.escape(stem)})(?!\w)")
        hits = {t for t, text in tests.items() if pat.search(text)}
        if hits:
            picked |= hits
        elif f.endswith(".md") or f.startswith("tests/") and not (Path(root) / f).exists():
            continue  # a doc no test names, or a test file that was deleted
        else:
            unnamed.append(f)
    if unnamed:
        return "no test names " + ", ".join(unnamed), sorted(tests)
    return None, sorted(picked)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--base", default="dev")
    ap.add_argument("--changed", nargs="*", help="changed files; default: read them from git")
    a = ap.parse_args()
    try:
        changed = a.changed if a.changed is not None else changed_files(a.root, a.base)
    except (RuntimeError, OSError) as e:
        reason, picked = f"cannot read the changes ({e})", select(a.root, [])[1]
    else:
        reason, picked = select(a.root, changed)
    if reason:
        print(f"full suite: {reason}")
    print("\n".join(picked))


if __name__ == "__main__":
    sys.exit(main())
