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
DONE_RULE_DATE = "2026-11-10"   # story #310 (A0): a story made before this has no Done when check
DONE_WHEN = re.compile(r"^[\s>*_-]*done when[*_]*[ \t]*:[*_]*[ \t]*(\S.*)$", re.I | re.M)   # [ \t], never \s: a newline must not be read as the value
DONE_HEADING = re.compile(r"^#+\s*done when\s*:?\s*$", re.I | re.M)
BIG_SIZES = {"size:M", "size:L", "size:XL"}
SHAPE ="write `Who does it: <actor>, <app or screen>, <how often>`, for example `Who does it: the admin, admin app City screen, twice a month`"


def empty_value(value: str) -> bool:
    """No answer: nothing, a placeholder in angle brackets, or the form's `_No response_` (one helper for every field)."""
    return not value or "<" in value or value.lower() == "_no response_"


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
    if empty_value(value) or len(parts) < 3:
        return f"`Who does it:` must name the actor, the app or screen, and how often ({SHAPE}); found: {value!r}"
    return None


def check_done_when(body: str) -> str | None:
    """A user story says how to know it is done, in one runnable or visible line (story #310, A0)."""
    m = DONE_WHEN.search(body)
    if m:
        return None if not empty_value(m.group(1).strip()) else _done_why()
    h = DONE_HEADING.search(body)
    if h:
        for line in body[h.end():].split("\n"):
            if line.lstrip().startswith("#"):   # the next section ends the Done when section
                break
            if line.strip():
                return None if not empty_value(line.strip()) else _done_why()
    return _done_why()


def _done_why() -> str:
    return "the story has no `Done when:` line: write one runnable or visible condition, for example `Done when: python3 -m unittest tests.test_desk is green.`"


def size_warning(labels) -> str | None:
    """A size above S is a warning, not a fail: the story should be split (rule 18, story #310)."""
    big = sorted(BIG_SIZES & set(labels))
    if not big:
        return None
    return f"{big[0]} is above the XS or S cap: split the story, or say in the issue why it cannot be split"


def check_pr_body(body: str) -> str | None:
    for n in dict.fromkeys(LINK.findall(body)):
        out = subprocess.run(["gh", "issue", "view", n, "--json", "labels,body,createdAt"], capture_output=True, text=True)
        if out.returncode != 0:
            return f"could not read issue #{n}: {out.stderr.strip()}"
        info = json.loads(out.stdout)
        if "user-story" not in {l["name"] for l in info["labels"]}:
            continue
        created = (info.get("createdAt") or "")[:10]   # ISO dates compare as text
        if created < RULE_DATE:
            print(f"skip #{n}: story created before {RULE_DATE}, when the Who does it rule began")
            continue
        why = check(info["body"] or "")
        if why:
            return f"issue #{n}: {why}"
        if created >= DONE_RULE_DATE:
            why = check_done_when(info["body"] or "")
            if why:
                return f"issue #{n}: {why}"
        names = [l["name"] for l in info["labels"]]
        warn = size_warning(names)
        if warn:
            print(f"warn: #{n} {warn}")
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
