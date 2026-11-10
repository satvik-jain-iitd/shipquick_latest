"""Story #327 (A11): the shortcut ledger. Lists every `shortcut:` or `ponytail:` comment in tracked source.

A comment is tagged `no-trigger` when it has no upgrade trigger. The trigger rule (ASSUMED, see docs/assumptions.md):
  1. a verb (add, upgrade, switch, move, replace, use, swap) followed later in the same sentence by `when` or `if`
     ("add a dict index when the list passes 10000 rows"), or
  2. `upgrade to` / `upgrade when`, or
  3. a `when` clause with a condition word (matters, passes, exceeds, grows, reaches, becomes, needs, hits,
     goes over, is over, is above) ("when throughput matters").
Anything else is `no-trigger`. Only the comment's own text is read: no network, no install, stdlib only.

Usage:
  python3 scripts/check_shortcuts.py                 list every shortcut, print the count (warn-only: exit 0)
  python3 scripts/check_shortcuts.py --write         also append one row per shortcut to docs/follow-ups.md
                                                     (a row already there, found by its [sc:...] key, is skipped)
  --root DIR   scan DIR instead of this repo (tests use a temp copy)
Skipped: tests/ and fixtures/ folders, vendored or built folders, markdown, and any file that is not UTF-8.
"""
import argparse
import datetime
import hashlib
import re
import subprocess
import sys
from pathlib import Path

MARK = re.compile(r"(?:#|//|/\*|<!--|--|;)\s*(shortcut|ponytail):\s*(.*)$")
TRIGGER = re.compile(
    r"\b(add|upgrade|switch|move|replace|use|swap)\b(?:(?!\.\s)[^;])*?\b(?:when|if)\b"
    r"|\bupgrade (?:to|when)\b"
    r"|\bwhen\b(?:(?!\.\s)[^;])*?\b(?:matters|passes|exceeds|grows|reaches|becomes|needs|hits|goes over|is over|is above)\b",
    re.I,
)
SOURCE = {".py", ".sh", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".swift", ".kt", ".kts", ".java", ".yml", ".yaml", ".toml", ".css", ".html", ".rb", ".go", ".rs"}
SKIP_PARTS = {"tests", "test", "fixtures", "vendor", "vendored", "third_party", "node_modules", "Pods", ".build", "build"}
ROW_KEY = "[sc:{}]"


def tracked_sources(root: Path):
    out = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True, check=True).stdout
    for rel in out.splitlines():
        p = Path(rel)
        if p.suffix not in SOURCE or SKIP_PARTS & set(p.parts):
            continue
        yield rel


def scan(root: Path):
    """(path, line_no, marker, text, has_trigger) for every marker comment in tracked source."""
    hits = []
    for rel in tracked_sources(root):
        try:
            lines = (root / rel).read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(lines, 1):
            m = MARK.search(line)
            if not m:
                continue
            text = re.sub(r"\s*(\*/|-->)\s*$", "", m.group(2)).strip()
            hits.append((rel, n, m.group(1), text, bool(TRIGGER.search(text))))
    return hits


def key_of(rel: str, text: str) -> str:
    """Stable across line moves: the file and the normalised comment text."""
    norm = " ".join(text.split())
    return hashlib.sha1(f"{rel}|{norm}".encode("utf-8")).hexdigest()[:12]


def write_rows(root: Path, hits) -> int:
    fu = root / "docs" / "follow-ups.md"
    text = fu.read_text(encoding="utf-8")
    today = datetime.date.today().isoformat()
    rows, seen = [], set()
    for rel, n, marker, body, trig in hits:
        key = key_of(rel, body)
        if key in seen or ROW_KEY.format(key) in text:
            continue
        seen.add(key)
        tag = "has trigger" if trig else "no-trigger"
        cell = body.replace("|", "\\|")
        rows.append(f"| {today} | `{marker}:` `{rel}` (line {n}): \"{cell}\" {ROW_KEY.format(key)} ({tag}) | "
                    "Logged by the shortcut ledger (story #327). Each shortcut needs an upgrade trigger or a named ceiling. | "
                    "reviewer (shipquick-qa) | open |")
    if not rows:
        return 0
    lines = text.split("\n")
    table_ends = [i for i, ln in enumerate(lines) if ln.startswith("|")]
    at = table_ends[-1] + 1 if table_ends else len(lines)
    lines[at:at] = rows
    fu.write_text("\n".join(lines), encoding="utf-8")
    return len(rows)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    hits = scan(root)
    for rel, n, marker, text, trig in hits:
        tag = "ok" if trig else "no-trigger"
        print(f"{rel}:{n}: {tag} {marker}: {text}")
    bare = sum(1 for h in hits if not h[4])
    print(f"shortcut ledger: {len(hits)} comment(s), {bare} no-trigger")
    if args.write:
        print(f"wrote {write_rows(root, hits)} row(s) to docs/follow-ups.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
