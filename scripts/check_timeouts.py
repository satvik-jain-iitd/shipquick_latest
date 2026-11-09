"""Fail when a GitHub Actions job that runs on a runner has no `timeout-minutes` (story #154).

GitHub's default job limit is 360 minutes, so one stalled install step keeps a check pending
for hours. A job that calls a reusable workflow (`uses:`) cannot set it and is skipped.

Usage: python3 scripts/check_timeouts.py [workflow dir or files...]   (default .github/workflows)
Exit 0 when every job has one; exit 1 naming each `file: job` that does not.
"""
import re
import sys
from pathlib import Path

JOB = re.compile(r"^  ([A-Za-z0-9_-]+):\s*$")


# ponytail: line-based, assumes the 2-space job indent every kit workflow uses; swap for a YAML
# parser if a child writes workflows in another indent.
def missing(text: str) -> list[str]:
    out, job, body, in_jobs = [], None, [], False

    def close():
        if job and any(l.startswith("    runs-on:") for l in body) \
                and not any(l.startswith("    timeout-minutes:") for l in body):
            out.append(job)

    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" "):
            close()
            job, body, in_jobs = None, [], line.startswith("jobs:")
            continue
        m = JOB.match(line) if in_jobs else None
        if m:
            close()
            job, body = m[1], []
        elif job:
            body.append(line)
    close()
    return out


def main(args: list[str]) -> int:
    paths = [Path(a) for a in args] or [Path(".github/workflows")]
    files = [f for p in paths for f in (sorted(p.glob("*.y*ml")) if p.is_dir() else [p])]
    bad = [f"{f}: {j}" for f in files for j in missing(f.read_text(encoding="utf-8"))]
    for b in bad:
        print(f"no timeout-minutes: {b}")
    print("timeouts OK" if not bad else f"{len(bad)} job(s) without timeout-minutes")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
