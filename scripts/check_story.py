"""Story #155: a story says who does it in real life before it is Ready: the actor, the app or screen,
and how often. A story without that line was built for the wrong person on the wrong app once.

Usage:
  python3 scripts/check_story.py < story.md            check one story body
  python3 scripts/check_story.py --pr-body-file f      check every `user-story` issue the PR body links (needs gh)
The line: `Who does it: <actor>, <app or screen>, <how often>` (an issue form's `### Who does it` heading works too).
Exit 0 and "story OK", or exit 1 and the reason.
"""
import argparse
import json
import re
import subprocess
import sys

from close_linked_issues import LINK   # one rule for "this body links an issue"

INLINE = re.compile(r"^[\s>*_-]*who does it[*_]*\s*:[*_]*\s*(.*)$", re.I | re.M)
HEADING = re.compile(r"^#+\s*who does it\s*:?\s*\n+(?!#)(.*)$", re.I | re.M)
RULE_DATE = "2026-11-09"   # stories made before the rule (story #155) are skipped, never failed
SHAPE ="write `Who does it: <actor>, <app or screen>, <how often>`, for example `Who does it: the admin, admin app City screen, twice a month`"


def check(body: str) -> str | None:
    m = INLINE.search(body) or HEADING.search(body)
    if not m:
        return f"the story has no `Who does it:` line ({SHAPE})"
    value = m.group(1).strip()
    if m.re is INLINE and value.count(",") < 2:   # a value that wraps: read on to the first blank line
        more = []
        for line in body[m.end():].split("\n")[1:]:
            if not line.strip() or line.lstrip().startswith(("#", "-", "*")):   # a blank, a heading or a list line ends it
                break
            more.append(line.strip())
        value = " ".join([value, *more]).strip()
    parts = [p for p in (s.strip() for s in value.split(",")) if p]
    if not value or "<" in value or value.lower() == "_no response_" or len(parts) < 3:
        return f"`Who does it:` must name the actor, the app or screen, and how often ({SHAPE}); found: {value!r}"
    return None


def check_pr_body(body: str) -> str | None:
    for n in dict.fromkeys(LINK.findall(body)):
        out = subprocess.run(["gh", "issue", "view", n, "--json", "labels,body,createdAt"], capture_output=True, text=True)
        if out.returncode != 0:
            return f"could not read issue #{n}: {out.stderr.strip()}"
        info = json.loads(out.stdout)
        if "user-story" not in {l["name"] for l in info["labels"]}:
            continue
        if (info.get("createdAt") or "")[:10] < RULE_DATE:   # ISO dates compare as text
            print(f"skip #{n}: story created before {RULE_DATE}, when the Who does it rule began")
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
        with open(args.pr_body_file, encoding="utf-8") as f:
            why = check_pr_body(f.read())
    else:
        why = check(sys.stdin.read())
    print(why or "story OK")
    return 1 if why else 0


if __name__ == "__main__":
    sys.exit(main())
