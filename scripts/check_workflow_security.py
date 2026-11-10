"""Story #325 (A7): workflow security lint, stdlib only (text and indentation, no YAML library).

Two rules for .github/workflows/*.yml:
  1. A workflow triggered by pull_request_target or workflow_run must not check out the PR head: an
     actions/checkout step with a ref or repository that names github.head_ref, pull_request.head.* or
     workflow_run.head_* fails. (Checking out the base, or no ref, is fine.)
  2. Every npm ci, npm install (or npm i) run command needs --ignore-scripts on the same command (a line is
     split at &&, ||, ; and | first). A folded `>` block is one command; a literal `|` block is one per line.

Usage: python3 scripts/check_workflow_security.py [file or folder ...]   (default: .github/workflows)
Exit 0 and "workflow security OK", or exit 1 with one `FAIL <file>:<line>: <problem>` line per finding.

ponytail: reads block-style YAML by indent and one command per logical line (a trailing backslash joins
lines). A flow-style step, or a command split by an unusual construct, is not seen; swap for a parser if one shows up.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RISKY_TRIGGER = re.compile(r"\b(pull_request_target|workflow_run)\b")
RISKY_TRIGGER_KEY = re.compile(r"""^\s+(-\s*)?["']?(pull_request_target|workflow_run)["']?\s*(:|$)""")
ON_KEY = re.compile(r"""^["']?on["']?\s*:(.*)$""")
CHECKOUT = re.compile(r"^\s*(-\s+)?uses\s*:\s*actions/checkout@")
PR_HEAD_KEY = re.compile(r"^\s*(-\s+)?(ref|repository)\s*:\s*(.*)$")
PR_HEAD = re.compile(r"github\.head_ref|pull_request\.head\.|workflow_run\.head_")
RUN_KEY = re.compile(r"^\s*(-\s+)?run\s*:\s*(.*)$")
NPM_INSTALL = re.compile(r"(?<![\w-])npm\s+(ci|install|i)(?![\w-])")
LIST_ITEM = re.compile(r"^\s*-\s")


def indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def strip_comment(text: str) -> str:
    return re.sub(r"\s#.*$", "", text).strip()


def is_risky(lines: list[str]) -> bool:
    """True when the top-level `on:` names pull_request_target or workflow_run (block, inline or list form)."""
    for i, line in enumerate(lines):
        m = ON_KEY.match(line)
        if not m:
            continue
        inline = strip_comment(m.group(1))
        if inline:
            return bool(RISKY_TRIGGER.search(inline))
        for body in lines[i + 1:]:
            if not body.strip() or body.lstrip().startswith("#"):
                continue
            if body[0] not in " \t":
                break
            if RISKY_TRIGGER_KEY.match(body):
                return True
    return False


def step_span(lines: list[str], i: int) -> range:
    """The lines of the step that holds line i: from its list dash (the line's own dash counts) to the next line at or left of that dash."""
    key_col = indent_of(lines[i])
    start = i
    while start > 0 and not (LIST_ITEM.match(lines[start]) and indent_of(lines[start]) <= key_col):
        start -= 1
    if LIST_ITEM.match(lines[start]):
        dash = indent_of(lines[start])
    else:
        start, dash = i, key_col
    end = i + 1
    while end < len(lines) and (not lines[end].strip() or indent_of(lines[end]) > dash):
        end += 1
    return range(start, end)


def head_checkouts(lines: list[str]) -> list[tuple[int, str]]:
    found = []
    for i, line in enumerate(lines):
        if not CHECKOUT.match(line):
            continue
        for j in step_span(lines, i):
            m = PR_HEAD_KEY.match(lines[j])
            if m and PR_HEAD.search(m.group(3)):
                found.append((j + 1, m.group(3).strip()))
    return found


def run_commands(lines: list[str]):
    """Yield (line number, command) for each run command, joining lines that end in a backslash."""
    i = 0
    while i < len(lines):
        m = RUN_KEY.match(lines[i])
        if not m:
            i += 1
            continue
        key_col = lines[i].index("run")
        value = strip_comment(m.group(2))
        if value[:1] in ("|", ">") or not value:
            pairs, j = [], i + 1
            while j < len(lines) and (not lines[j].strip() or indent_of(lines[j]) > key_col):
                pairs.append((j + 1, lines[j].strip()))
                j += 1
            i = j
            if value[:1] == ">":   # YAML folds a > block: its lines are one command, joined with a space
                kept = [(n, t) for n, t in pairs if t and not t.startswith("#")]
                if kept:
                    yield kept[0][0], " ".join(t for _, t in kept)
                continue
        else:
            pairs, i = [(i + 1, value)], i + 1
        pending, first = "", None
        for num, text in pairs:
            if not text or text.startswith("#"):
                continue
            first = first or num
            if text.endswith("\\"):
                pending += text[:-1] + " "
                continue
            yield first, (pending + text).strip()
            pending, first = "", None
        if pending:
            yield first, pending.strip()


def check_file(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    problems = []
    if is_risky(lines):
        for num, ref in head_checkouts(lines):
            problems.append(f"{path}:{num}: checks out the PR head ({ref}) in a pull_request_target or workflow_run workflow; check out the base, or drop the ref")
    for num, line_cmd in run_commands(lines):
        for cmd in re.split(r"&&|\|\||;|\|", line_cmd):   # the flag must sit on the same command as the install
            cmd = cmd.strip()
            if NPM_INSTALL.search(cmd) and "--ignore-scripts" not in cmd:
                problems.append(f"{path}:{num}: `{cmd}` runs install scripts; add --ignore-scripts (ADR-012)")
    return problems


def main(args: list[str]) -> int:
    targets = [Path(a) for a in args] or [ROOT / ".github" / "workflows"]
    files = [f for t in targets for f in (sorted([*t.glob("*.yml"), *t.glob("*.yaml")]) if t.is_dir() else [t])]
    problems = [p for f in files for p in check_file(f)]
    for p in problems:
        print(f"FAIL {p}")
    if problems:
        return 1
    print(f"workflow security OK ({len(files)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
