"""Story #146 (PR #152 review): a project whose docs/screens.txt names a real screen must also run
`screens.sh --check` somewhere in its own CI, or the render gate is configured but never actually
run -- the screen can drift forever with every check still green.

Usage: python3 scripts/check_screens_wired.py --screens-file <path> --workflows-dir <path>
Exit 0 and "screens wired OK" (or "no screens configured: check skipped"), or exit 1 and the reason.
"""
import argparse
import re
import sys
from pathlib import Path

CHECK_CALL = re.compile(r"screens\.sh\s+--check")


def real_lines(screens_text: str) -> list:
    return [l for l in screens_text.splitlines() if l.strip() and not l.strip().startswith("#")]


def decide(screens_text: str, workflow_texts: list) -> str | None:
    if not real_lines(screens_text):
        return None
    if any(CHECK_CALL.search(text) for text in workflow_texts):
        return None
    return ("docs/screens.txt names a screen, but no workflow in .github/workflows runs "
            "`screens.sh --check` -- add that step to your own ci.yml (docs/SCREENS.md), or the "
            "render gate is configured but never run")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--screens-file", required=True)
    ap.add_argument("--workflows-dir", required=True)
    a = ap.parse_args(argv)
    p = Path(a.screens_file)
    screens_text = p.read_text(encoding="utf-8") if p.is_file() else ""
    wf_dir = Path(a.workflows_dir)
    workflow_texts = [f.read_text(encoding="utf-8") for f in sorted(wf_dir.glob("*.yml"))] if wf_dir.is_dir() else []
    why = decide(screens_text, workflow_texts)
    if why is None:
        print("screens wired OK" if real_lines(screens_text) else "no screens configured: check skipped")
        return 0
    print(why)
    return 1


if __name__ == "__main__":
    sys.exit(main())
