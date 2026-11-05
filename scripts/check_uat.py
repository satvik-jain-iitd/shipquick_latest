"""Validate the "## UAT on dev (<link>)" section of a dev -> main PR body (story #120, docs/templates/uat-checklist.md).
A new user who has never seen the app must be able to follow every story line with no questions: an Open: line
(the exact link or screen, with test data), numbered one-action steps, and an Expected: line with exact text.

Usage: python3 scripts/check_uat.py < section_text
Exit 0 and "UAT OK", or exit 1 and the reason (first failure wins).
"""
import re
import sys

CHECKBOX = re.compile(r"^- \[[ x]\] (.+)$")
STORY = re.compile(r"^#\d+ \S")
KNOWN_BUGS = re.compile(r"^Known bugs going to production: \S")
OPEN = re.compile(r"^\s*Open:\s*\S", re.M)
STEP = re.compile(r"^\s*\d+\.\s*\S", re.M)
EXPECTED = re.compile(r"^\s*Expected:\s*\S", re.M)
FIXED = ("Old flows still work", "Design matches the approved boards")


def check(text: str) -> str | None:
    lines = [l.rstrip() for l in text.strip().splitlines()]
    if not lines:
        return "the UAT section is empty"

    story_count = 0
    seen_fixed = set()
    known_bugs = False
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        m = CHECKBOX.match(line.strip())
        if m:
            label = m.group(1).strip()
            if label in FIXED:
                seen_fixed.add(label)
                i += 1
                continue
            if not STORY.match(label):
                return f"a checklist line is neither a story (#n ...) nor a known fixed item: {label}"
            story_count += 1
            i += 1
            body_lines = []
            while i < n and not CHECKBOX.match(lines[i].strip()) and not KNOWN_BUGS.match(lines[i].strip()):
                body_lines.append(lines[i])
                i += 1
            body = "\n".join(body_lines)
            if not OPEN.search(body):
                return f"no Open: line: {label}"
            if not STEP.search(body):
                return f"no numbered steps: {label}"
            if not EXPECTED.search(body):
                return f"no Expected: line: {label}"
            continue
        if KNOWN_BUGS.match(line.strip()):
            known_bugs = True
            i += 1
            continue
        return f"a line in the UAT section is neither a checklist item nor the Known bugs line: {line.strip()[:60]}"

    if story_count == 0:
        return "no story lines in the UAT section"
    missing = [f for f in FIXED if f not in seen_fixed]
    if missing:
        return f"missing checklist line: {missing[0]}"
    if not known_bugs:
        return 'missing "Known bugs going to production:" line'
    return None


def main() -> int:
    why = check(sys.stdin.read())
    print(why or "UAT OK")
    return 1 if why else 0


if __name__ == "__main__":
    sys.exit(main())
