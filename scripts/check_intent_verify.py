"""Intent-verification gate (ADR-021): before Dev starts any QA-delegated work, QA confirms Dev's say-back on the story
issue, as a comment `Intent verified by QA: <YYYY-MM-DD>`. The proof must come from a login that is not the PR author,
because the coder writes the PR body and the coder cannot pass its own gate.

Usage:
  PR_AUTHOR=<login> python3 scripts/check_intent_verify.py --pr-body-file f
      check every `user-story` issue the PR body links (needs gh). In CI PR_AUTHOR is the PR's author. Locally
      check_local.sh sets it to the logged-in gh login, which is the author of a local branch.
Exit 0 and "intent OK", or exit 1 and the reason. An empty PR_AUTHOR fails: an unknown author never passes.
"""
import argparse
import json
import os
import re
import subprocess
import sys

from close_linked_issues import LINK   # one rule for "this body links an issue"

PROOF = re.compile(r"^[\s>*_-]*intent verified by qa[*_]*\s*:[*_]*\s*(\d{4}-\d{2}-\d{2})\b", re.I | re.M)
RULE_DATE = "2026-11-19"   # stories made before the rule are skipped, never failed


def check_comments(comments, author: str) -> str | None:
    """A proof is a comment with the phrase and a date, from a login that is not the PR author (case-insensitive)."""
    for c in comments:
        login = ((c.get("author") or {}).get("login") or "").strip()
        if not login or login.lower() == author.lower():
            continue
        if PROOF.search(c.get("body") or ""):
            return None
    return "no comment `Intent verified by QA: YYYY-MM-DD` from a login other than the PR author (ADR-021)"


def check_pr_body(body: str, author: str) -> str | None:
    for n in dict.fromkeys(LINK.findall(body)):
        out = subprocess.run(["gh", "issue", "view", n, "--json", "labels,body,createdAt,comments"], capture_output=True, text=True)
        if out.returncode != 0:
            return f"could not read issue #{n}: {out.stderr.strip()}"
        info = json.loads(out.stdout)
        if "user-story" not in {l["name"] for l in info["labels"]}:
            continue
        if (info.get("createdAt") or "")[:10] < RULE_DATE:
            print(f"skip #{n}: story created before {RULE_DATE}, when the intent gate began")
            continue
        why = check_comments(info.get("comments") or [], author)
        if why:
            return f"issue #{n}: {why}"
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pr-body-file", required=True, help="the PR body; every user-story issue it links is checked")
    args = ap.parse_args()
    author = os.environ.get("PR_AUTHOR", "")
    if not author.strip():
        print("PR_AUTHOR is empty: the check cannot tell who wrote the PR, so it fails (set PR_AUTHOR to the PR's author login)")
        return 1
    why = check_pr_body(open(args.pr_body_file, encoding="utf-8").read(), author)
    if why:
        print(why)
        return 1
    print("intent OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
