"""List template placeholders such as <PRIMARY_COLOR> that are still left (story #69), and the roadmap.json stub (story #76).

Usage: python3 scripts/check_placeholders.py [file ...]   (default: docs/design-tokens.md, and roadmap.json when it exists)
Exit 0 when none are left, exit 1 with one line per placeholder. HTML tags and links are not placeholders.
scripts/adopt.sh writes a roadmap.json stub whose vision says "Write one line here"; a stub left in place is reported too.
"""
import re
import sys
from pathlib import Path

TOKEN = re.compile(r"<[A-Z][A-Z0-9_]*>")
STUB = "Write one line here"   # the vision text adopt.sh puts in a new roadmap.json


def main(paths):
    left = []
    for path in paths:
        for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
            left += [f"{path}:{n}: {t}" for t in TOKEN.findall(line)]
            if STUB in line:
                left.append(f"{path}:{n}: the vision is still the adopt.sh stub (\"{STUB}\")")
    print("\n".join(left) if left else "no placeholders left")
    return 1 if left else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or ["docs/design-tokens.md"] + (["roadmap.json"] if Path("roadmap.json").exists() else [])))
