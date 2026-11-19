"""Acceptance-criteria traceability (M5d): a story must give stable AC IDs and map each to a test.

Usage:
  python3 scripts/check_ac_trace.py < story.md
  python3 scripts/check_ac_trace.py --pr-body-file f
A story body should contain lines like `AC-1: ...` and a `Tests: AC-1 -> tests/test_x.py::test_y` mapping.
Exit 0 and "ac OK", or exit 1 and the reason. Stories created before 2026-11-19 are skipped.
"""
import argparse
import json
import re
import subprocess
import sys

from close_linked_issues import LINK

# An AC is defined by a line that starts `AC-<n>:`; a mention in prose does not define one.
DEFINE_RE = re.compile(r"^\s*(AC-\d+)\s*:", re.M)
TESTS_LINE_RE = re.compile(r"^\s*tests?\s*[:=]", re.I | re.M)
MAP_RE = re.compile(r"(AC-\d+)\s*->\s*([^\s;,]+)::([^\s;,]+)")
RULE_DATE = "2026-11-19"


def check(body: str) -> str | None:
    defined = list(dict.fromkeys(DEFINE_RE.findall(body)))
    if not defined:
        return "story has no acceptance-criteria IDs (a line that starts `AC-1:`, `AC-2:`, ...)"
    if not TESTS_LINE_RE.search(body):
        return "story has no `Tests:` line that maps each AC id to path::test_name"
    mapped = {ac for ac, _, _ in MAP_RE.findall(body)}
    unmapped = [a for a in defined if a not in mapped]
    if unmapped:
        return f"{', '.join(unmapped)} not mapped on a Tests line (write `AC-n -> path::test_name`)"
    stray = sorted(mapped - set(defined))
    if stray:
        return f"Tests maps {', '.join(stray)}, which the story does not define"
    return None


def check_pr_body(body: str) -> str | None:
    for n in dict.fromkeys(LINK.findall(body)):
        out = subprocess.run(["gh", "issue", "view", n, "--json", "labels,body,createdAt"], capture_output=True, text=True)
        if out.returncode != 0:
            return f"could not read issue #{n}: {out.stderr.strip()}"
        info = json.loads(out.stdout)
        if "user-story" not in {l["name"] for l in info["labels"]}:
            continue
        if (info.get("createdAt") or "")[:10] < RULE_DATE:
            print(f"skip #{n}: story created before {RULE_DATE}")
            continue
        why = check(info["body"] or "")
        if why:
            return f"issue #{n}: {why}"
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pr-body-file")
    args = ap.parse_args()
    if args.pr_body_file:
        body = open(args.pr_body_file).read()
        why = check_pr_body(body)
    else:
        body = sys.stdin.read()
        why = check(body)
    if why:
        print(why)
        return 1
    print("ac OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
