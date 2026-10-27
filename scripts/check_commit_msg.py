"""Validate commit message follows Conventional Commits."""
import re
import sys

PATTERN = re.compile(
    r"^(feat|fix|docs|design|test|chore|refactor|style|perf|ci|build|release)"
    r"(\(.+\))?: .+"
)


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else ".git/COMMIT_EDITMSG"
    try:
        msg = open(path).read().strip().splitlines()[0]
    except (IndexError, FileNotFoundError):
        return 0
    if msg.startswith("Merge "):
        return 0
    if not PATTERN.match(msg):
        print(f"Bad commit message: {msg}")
        print("Use: type(scope): description")
        print("See COMMIT_GUIDELINES.md")
        return 1
    if len(msg) > 72:
        print(f"Subject too long ({len(msg)} chars, max 72)")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
