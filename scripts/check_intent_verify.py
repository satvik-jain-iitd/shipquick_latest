"""Intent-verification gate (ADR-021): before Dev starts any QA-delegated work, Dev sends a say-back
(what it understood, planned approach, "am I doing this right?") and waits for QA confirmation.
The confirmation is recorded in the PR body as `Intent verified by QA: <YYYY-MM-DD>`.

Usage:
  python3 scripts/check_intent_verify.py < pr-body.md            check one PR body
  python3 scripts/check_intent_verify.py --pr-body-file f      check every `user-story` issue the PR body links (needs gh)
Exit 0 and "intent OK", or exit 1 and the reason.
"""
import argparse
import json
import re
import subprocess
import sys

from close_linked_issues import LINK   # one rule for "this body links an issue"

INLINE = re.compile(r"^[\s>*_-]*intent verified by qa[*_]*\s*:[*_]*\s*(.*)$", re.I | re.M)
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
RULE_DATE = "2026-11-19"   # stories made before the rule are skipped, never failed


def check(body: str) -> str | None:
    m = INLINE.search(body)
    if not m:
        return "the PR body has no `Intent verified by QA: <YYYY-MM-DD>` line (ADR-021)"
    value = m.group(1).strip()
    if not DATE_RE.search(value):
        return f"`Intent verified by QA:` must carry a date YYYY-MM-DD (ADR-021); found: {value!r}"
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
            print(f"skip #{n}: story created before {RULE_DATE}, when the intent gate began")
            continue
        why = check(body)
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
    print("intent OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
