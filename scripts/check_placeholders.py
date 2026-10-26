"""List template placeholders such as <PRIMARY_COLOR> that are still left (story #69).

Usage: python3 scripts/check_placeholders.py [file ...]   (default: docs/design-tokens.md)
Exit 0 when none are left, exit 1 with one line per placeholder. HTML tags and links are not placeholders.
"""
import re
import sys
from pathlib import Path

TOKEN = re.compile(r"<[A-Z][A-Z0-9_]*>")


def main(paths):
    left = []
    for path in paths:
        for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
            left += [f"{path}:{n}: {t}" for t in TOKEN.findall(line)]
    print("\n".join(left) if left else "no placeholders left")
    return 1 if left else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or ["docs/design-tokens.md"]))
