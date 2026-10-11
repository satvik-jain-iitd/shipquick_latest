"""Check markdown files for unclosed code blocks."""
import glob
import sys


def main() -> int:
    bad = []
    for f in glob.glob("**/*.md", recursive=True):
        if ".git/" in f:
            continue
        ticks = open(f).read().count("```")
        if ticks % 2 != 0:
            bad.append(f)
    if bad:
        print("Unclosed code blocks in:", bad)
        return 1
    print("Markdown blocks OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
