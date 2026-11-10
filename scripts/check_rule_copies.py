#!/usr/bin/env python3
"""Rule-copy canary (story #316, epic #309). Stdlib only.

Idea borrowed from Ponytail's scripts/check-rule-copies.js (MIT, read only). Two checks:

1. Each --child CLAUDE.md carries the kit rule block unchanged between the markers
   `<!-- shipquick-rules:start -->` and `<!-- shipquick-rules:end -->`. The kit block is every
   line from the rule 0 line to the end of the kit CLAUDE.md. Compared after CRLF -> LF and
   trimming outer blank lines. Marker placement for a child: docs/ADOPTION.md.
2. Each load-bearing phrase is present in the kit file(s) it names (CLAUDE.md, and a skill that restates the rule). A missing phrase names
   the file and the phrase.

Usage: scripts/check_rule_copies.py [--kit-root DIR] [--child CLAUDE.md ...]
"""
import argparse
import difflib
from pathlib import Path

HERE = Path(__file__).resolve().parent
START = "<!-- shipquick-rules:start -->"
END = "<!-- shipquick-rules:end -->"

# (rule number in CLAUDE.md, exact phrase, files that must carry it).
# Plain substring match, not a regex (upgrade when a phrase needs wildcards). Rule 33 is also restated in
# the shipquick-feedback skill, so that phrase names both files (review of #335).
PHRASES = [
    (0, "run `scripts/mode.sh get`", ("CLAUDE.md",)),
    (4, "Work only from GitHub issues", ("CLAUDE.md",)),
    (5, "failing test first", ("CLAUDE.md",)),
    (12, "Merge only when all gates pass", ("CLAUDE.md",)),
    (19, "Teammate blocks:", ("CLAUDE.md",)),
    (20, "Radar first", ("CLAUDE.md",)),
    (22, "The build account (`klickbae8yt-star`) makes every commit, push and PR", ("CLAUDE.md",)),
    (30, "The reviewer leaves comments on every changed file", ("CLAUDE.md",)),
    (37, "Harden the gate before enforcing anything new", ("CLAUDE.md",)),
    (33, 'at least three "Why" lines', ("CLAUDE.md", "skills/shipquick-feedback/SKILL.md")),
    (38, "Library first", ("CLAUDE.md",)),
]


def norm(text):
    return text.replace("\r\n", "\n").strip()


def kit_block(kit_text):
    # shortcut: the kit block runs from the rule 0 line to the end of the file. A rule that
    # sits after a second numbered list would need its own end marker. upgrade then.
    lines = kit_text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("0. "):
            return norm("\n".join(lines[i:]))
    return None


def check_child(path, kit_text):
    if not path.is_file():
        return [f"FAIL {path}: child CLAUDE.md not found"]
    text = path.read_text(encoding="utf-8")
    if text.count(START) != 1 or text.count(END) != 1 or text.index(START) > text.index(END):
        return [f"FAIL {path}: needs the line {START} above the kit rules and the line {END} below them "
                f"(placement: docs/ADOPTION.md)"]
    body = text.split(START, 1)[1].split(END, 1)[0]
    expected = kit_block(kit_text)
    actual = norm(body)
    if actual == expected:
        return []
    diff = list(difflib.unified_diff(expected.splitlines(), actual.splitlines(),
                                     "kit CLAUDE.md", str(path), lineterm="", n=0))
    return [f"FAIL {path}: the rule block between the markers differs from the kit CLAUDE.md:"] + diff[2:10]


def check_phrases(kit_root):
    failures = []
    for rule, phrase, files in PHRASES:
        for rel in files:
            target = kit_root / rel
            if not target.is_file():
                failures.append(f"FAIL {rel}: file missing (it must carry rule {rule})")
            elif phrase not in target.read_text(encoding="utf-8"):
                failures.append(f'FAIL {rel}: missing phrase of rule {rule}: "{phrase}"')
    return failures


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--kit-root", default=str(HERE.parent), help="the kit folder (default: this script's parent)")
    ap.add_argument("--child", action="append", default=[], help="a child CLAUDE.md to compare with the kit block")
    args = ap.parse_args(argv)

    kit_root = Path(args.kit_root)
    kit_path = kit_root / "CLAUDE.md"
    if not kit_path.is_file():
        print(f"FAIL {kit_path}: kit CLAUDE.md not found")
        return 1
    kit_text = kit_path.read_text(encoding="utf-8")

    failures = []
    if kit_block(kit_text) is None:
        failures.append("FAIL CLAUDE.md: no rule 0 line (a line starting with `0. `) to compare children with")
    failures += check_phrases(kit_root)
    for child in args.child:
        failures += check_child(Path(child), kit_text)

    if failures:
        for line in failures:
            print(line)
        print("rule copies: FAIL. Copy the kit rules again from the kit CLAUDE.md, then re-run.")
        return 1
    print(f"ok rule copies: {len(PHRASES)} phrases present; {len(args.child)} child block(s) match the kit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
