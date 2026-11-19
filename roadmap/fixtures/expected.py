#!/usr/bin/env python3
"""Story #81 (epic #80): capture the golden expected model from the reference Python roadmap.

The reference is a child project's own `roadmap.py` (read only, never copied here). This script feeds it the synthetic
fixture `golden-issues.json` and prints the model the JS `build()` must equal, field by field, in the JS names.
Goldens are captured, never typed: nobody edits `golden-expected.json` by hand; rerun this script instead.

Usage: python3 roadmap/fixtures/expected.py <path to the reference roadmap.py> [golden-issues.json] > roadmap/fixtures/golden-expected.json
"""
import importlib.util
import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
NOW_UTC = "2026-11-11T05:30:00Z"   # the page clock for days left and late flags; the JS test reads it from the golden


def load(path):
    spec = importlib.util.spec_from_file_location("reference_roadmap", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def flatten(data):
    """The same reshaping the reference does right after its GitHub call: label names, first doing time, check rollup."""
    issues = []
    for node in data["issues"]["nodes"]:
        node = dict(node)
        doing = sorted(t["createdAt"] for t in node.pop("timelineItems")["nodes"] if (t.get("label") or {}).get("name") == "doing")
        issues.append({**node, "labels": [l["name"] for l in node["labels"]["nodes"]], "doing_at": doing[0] if doing else None})
    prs = []
    for p in data["pullRequests"]["nodes"]:
        roll = (((p["commits"]["nodes"] or [{}])[0].get("commit") or {}).get("statusCheckRollup") or {}).get("state")
        prs.append({"number": p["number"], "title": p["title"], "headRefName": p["headRefName"], "isDraft": p["isDraft"],
                    "checks": [{"conclusion": roll}] if roll else []})
    return issues, prs


def main(argv):
    if not argv:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    ref = load(argv[0])
    fixture = argv[1] if len(argv) > 1 else os.path.join(HERE, "golden-issues.json")
    with open(fixture, encoding="utf-8") as f:
        issues, prs = flatten(json.load(f)["data"]["repository"])
    model = ref.build(issues, prs)
    ref.clock(model, datetime.strptime(NOW_UTC, "%Y-%m-%dT%H:%M:%SZ") + ref.IST)
    utc = lambda d: (d - ref.IST).strftime("%Y-%m-%dT%H:%M:%SZ") if d else None   # the reference keeps India time; the golden keeps GitHub's UTC
    nums = lambda rows: [s["number"] for s in rows]
    out = {
        "now": NOW_UTC,
        "epics": [{"number": e["number"], "title": e["title"], "state": e["state"]} for e in model["epics"]],
        "stories": [{"number": s["number"], "epic": s["epic"], "column": s["column"], "raw": s["raw"], "text": s["text"], "needsWords": s["needs_words"],
                     "pr": s["pr"]["number"] if s["pr"] else None, "milestone": s["milestone"], "prio": None if s["prio"] == 9 else s["prio"],
                     "needs": s["needs"], "blockedBy": s["blocked_by"], "started": utc(s["started"]), "cycleMin": s["cycle_min"]} for s in model["stories"]],
        "timeline": [{"day": d["day"], "stories": nums(d["stories"])} for d in model["timeline"]],
        "here": {"doing": nums(model["here"]["doing"]), "next": model["here"]["next"]["number"] if model["here"]["next"] else None},
        "next": nums(model["next"]),
        "older": nums(model["older"]),
        "milestones": [{"title": m["title"], "due": utc(m["due"]), "done": m["done"], "total": m["total"], "daysLeft": m["days_left"], "late": m["late"]} for m in model["milestones"]],
        "map": model["map"],
        "chain": nums(model["chain"]),
    }
    json.dump(out, sys.stdout, indent=1)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
