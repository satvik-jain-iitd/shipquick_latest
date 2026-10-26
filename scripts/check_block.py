"""Check a teammate block has the right shape (docs/TEAM_PROTOCOL.md).

Usage:
    python3 scripts/check_block.py [file]     # stdin if no file

Takes the first fenced block if there is one, else all the text.
Exit 0 and "Block OK", or exit 1 and a one-line reason (first failure wins).
A block "To owner" also needs a time word (Now / After <event> / Not yet) on every
numbered line and exactly one "Merge: now | not yet | nothing to merge" line.
"""
import re
import sys

HEADER = re.compile(r"^To [a-z][a-z0-9 -]*, from [a-z][a-z0-9 -]*, re \S.*:$")
NUMBERED = re.compile(r"^\d+\. \S")
LAST = re.compile(r"^(Need from you: \S.*|Nothing needed from you\.)$")
SECRET = re.compile(r"ghp_\w{20,}|sk-\w{20,}|AKIA[0-9A-Z]{16}|-----BEGIN")
# Blocks to the owner say the exact instant: a time word per line, one Merge: line.
OWNER_LINE = re.compile(r"^\d+\. (Now|After [^:]+|Not yet): \S")
MERGE_LINE = re.compile(r"^Merge: (now|not yet|nothing to merge)\b")
MAX_WORDS = 120


def block_of(text: str) -> str:
    fenced = re.search(r"```[^\n]*\n(.*?)```", text, re.S)
    return fenced.group(1) if fenced else text


def check(text: str) -> str | None:
    lines = [l.rstrip() for l in block_of(text).strip().splitlines()]
    if not lines:
        return "empty block"
    if not HEADER.match(lines[0]):
        return f"bad header: {lines[0]}"
    if not any(NUMBERED.match(l) for l in lines):
        return "no numbered line"
    if not LAST.match(lines[-1]):
        return f"bad last line: {lines[-1]}"
    if lines[0].startswith("To owner,"):
        for l in lines:
            if NUMBERED.match(l) and not OWNER_LINE.match(l):
                return f"owner line without a time word: {l}"
        if sum(1 for l in lines if MERGE_LINE.match(l)) != 1:
            return "owner block needs one Merge: line"
    words = len(" ".join(lines).split())
    if words > MAX_WORDS:
        return f"over {MAX_WORDS} words ({words})"
    if SECRET.search(" ".join(lines)):
        return "looks like a secret"
    return None


def main() -> int:
    text = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
    why = check(text)
    print(why or "Block OK")
    return 1 if why else 0


if __name__ == "__main__":
    sys.exit(main())
