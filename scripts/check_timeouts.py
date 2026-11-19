"""Fail when a GitHub Actions job that runs on a runner has no `timeout-minutes` (story #154).

GitHub's default job limit is 360 minutes, so one stalled install step keeps a check pending
for hours. A job that calls a reusable workflow (`uses:`) cannot set it and is skipped.

Usage: python3 scripts/check_timeouts.py [workflow dir or files...]   (default .github/workflows)
Exit 0 when every job has one; exit 1 naming each `file: job` that does not.
"""
import re
import sys
from pathlib import Path

KEY = re.compile(r"""^( +)(["']?)([A-Za-z0-9_-]+)\2\s*:\s*(?:#.*)?$""")
NO_JOBS = "(jobs: found, but no job could be read; write one job per line, block style)"


def indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


# ponytail: reads block-style YAML by indent, no YAML dependency (CI installs only pytest). A
# flow-style `jobs: {...}` is reported as NO_JOBS, never passed; swap for a parser if that matters.
def missing(text: str) -> list[str]:
    lines = [l for l in text.splitlines() if l.strip() and not l.lstrip().startswith("#")]
    out, i = [], 0
    while i < len(lines):
        if not re.match(r"^jobs\s*:", lines[i]):
            i += 1
            continue
        i += 1
        jobs = []
        job_indent = indent(lines[i]) if i < len(lines) and lines[i].startswith(" ") else 0
        while i < len(lines) and lines[i].startswith(" "):
            m = KEY.match(lines[i])
            if m and indent(lines[i]) == job_indent:
                jobs.append([m[3], []])
            elif jobs:
                jobs[-1][1].append(lines[i])
            i += 1
        for name, body in jobs:
            key_indent = min((indent(l) for l in body), default=0)
            keys = {l.strip().split(":", 1)[0].strip().strip("\"'") for l in body if indent(l) == key_indent}
            if "runs-on" in keys and "timeout-minutes" not in keys:
                out.append(name)
        if not jobs:
            out.append(NO_JOBS)
    return out


def main(args: list[str]) -> int:
    paths = [Path(a) for a in args] or [Path(".github/workflows")]
    files = [f for p in paths for f in (sorted(p.glob("*.y*ml")) if p.is_dir() else [p])]
    bad = []
    for f in files:
        text = f.read_text(encoding="utf-8")
        if not re.search(r"^jobs\s*:", text, re.M):
            # story #174: zero jobs fails, never a silent pass (a root-indented file still runs
            # on GitHub, so its jobs may have no timeout), same as the flow-style NO_JOBS case.
            bad.append(f"{f}: no jobs found (write `jobs:` at column 0, block style)")
            continue
        bad += [f"{f}: {j}" for j in missing(text)]
    for b in bad:
        print(f"no timeout-minutes: {b}")
    print("timeouts OK" if not bad else f"{len(bad)} job(s) without timeout-minutes")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
