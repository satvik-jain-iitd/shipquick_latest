"""Story size gate (ADR-020): only XS and S may be planned. M, L and XL stories must be split
before they leave Ready, so a fast coder model never carries a large change.

Usage:
  python3 scripts/check_story_size.py < story.md            check one story body
  python3 scripts/check_story_size.py --pr-body-file f      check every `user-story` issue the PR body links (needs gh)
The line: `Size: XS` (or `S`, `M`, `L`, `XL`). An issue form's `### Size (T-shirt)` heading works too.
Exit 0 and "story OK", or exit 1 and the reason.
"""
import argparse
import json
import re
import subprocess
import sys

from close_linked_issues import LINK   # one rule for "this body links an issue"

INLINE = re.compile(r"^[\s>*_-]*size[*_]*\s*:[*_]*\s*(.*)$", re.I | re.M)
HEADING = re.compile(r"^#+\s*size(?:\s*\(t-shirt\))?\.?\s*:?\s*\n+(?!#)(.*)$", re.I | re.M)
RULE_DATE = "2026-11-19"   # stories made before the rule are skipped, never failed
ALLOWED = {"XS", "S"}
SHAPE = "write `Size: XS` or `Size: S` (M, L and XL must be split first)"


def _value(body: str, m) -> str:
    value = m.group(1).strip()
    if m.re is INLINE and value.count(",") < 0:
        pass
    # a value that wraps: read on to the first blank line
    more = []
    for line in body[m.end():].split("\n")[1:]:
        if not line.strip() or line.lstrip().startswith(("#", "-", "*")):
            break
        more.append(line.strip())
    if more:
        value = " ".join([value, *more]).strip()
    # strip markdown bold/parens
    value = value.strip("*_ ").strip()
    # take first token
    tok = value.split()[0] if value.split() else ""
    return tok.upper().rstrip(".,;:")


def check(body: str) -> str | None:
    m = INLINE.search(body) or HEADING.search(body)
    if not m:
        return f"the story has no `Size:` line ({SHAPE})"
    value = _value(body, m)
    if not value or "<" in value or value.lower() == "_no response_" or value == "NO":
        return f"`Size:` must name a T-shirt size ({SHAPE}); found: {value!r}"
    if value not in {"XS", "S", "M", "L", "XL"}:
        return f"`Size:` must be one of XS, S, M, L, XL ({SHAPE}); found: {value!r}"
    if value not in ALLOWED:
        return f"`Size:` must be XS or S; {value} must be split before Ready ({SHAPE})"
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
            print(f"skip #{n}: story created before {RULE_DATE}, when the size gate began")
            continue
        why = check(info["body"] or "")
        if why:
            return f"issue #{n}: {why}"
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pr-body-file", help="check every user-story issue linked in this PR body")
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
    print("story OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
