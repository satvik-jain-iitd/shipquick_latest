"""The shared loop of the story checks: the issues a PR body links, the `user-story` label, the rule date.

linked_stories(body, rule_date) yields (number, info) for every linked user-story issue made on or after rule_date.
A story made before it is skipped, never failed, and the skip is said. A gh failure raises StoryReadError.
Used by check_ac_trace.py. check_story.py, check_story_size.py and check_intent_verify.py still carry their own copy of
this loop; moving them here is a separate story (#564 review point 4).
"""
import json
import subprocess

from close_linked_issues import LINK   # one rule for "this body links an issue"


class StoryReadError(Exception):
    pass


def linked_stories(body: str, rule_date: str, fields: str = "labels,body,createdAt"):
    for n in dict.fromkeys(LINK.findall(body)):
        out = subprocess.run(["gh", "issue", "view", n, "--json", fields], capture_output=True, text=True)
        if out.returncode != 0:
            raise StoryReadError(f"could not read issue #{n}: {out.stderr.strip()}")
        info = json.loads(out.stdout)
        if "user-story" not in {l["name"] for l in info["labels"]}:
            continue
        if (info.get("createdAt") or "")[:10] < rule_date:
            print(f"skip #{n}: story created before {rule_date}, when the rule began")
            continue
        yield n, info
