"""Story #140: the one parser for .shipquick/roles.yml. Which GitHub accounts play the coder and
reviewer role, who owns the project, and where the ShipQuick kit's home repo is (for a fork). No
account name lives in any other ShipQuick script -- they all call this one.

File shape (a tiny fixed format, not full YAML -- parsed without a dependency):
  coder:
    - account-one
    - account-two
  reviewer:
    - account-three
  owner: account-three
  shipquick_repo: owner/repo

Several coders or reviewers are allowed (a list per role). Usage:
  python3 scripts/roles.py get coder|reviewer|owner|shipquick_repo [--file <path>]
Prints the value (accounts comma-separated for coder/reviewer), or exits 1 with the reason.
"""
import argparse
import re
import sys
from pathlib import Path

DEFAULT_FILE = ".shipquick/roles.yml"
LIST_ITEM = re.compile(r"^\s*-\s*(\S+)\s*$")
LIST_HEAD = re.compile(r"^(\w+):\s*$")
SCALAR = re.compile(r"^(\w+):\s*(\S+)\s*$")


def parse(text: str) -> dict:
    """{"coder": [...], "reviewer": [...], "owner": "...", "shipquick_repo": "..."}. `#` comments
    and blank lines are ignored."""
    data: dict = {}
    current_list_key = None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        m = LIST_ITEM.match(line)
        if m and current_list_key:
            data.setdefault(current_list_key, []).append(m.group(1))
            continue
        current_list_key = None
        m = LIST_HEAD.match(line)
        if m:
            current_list_key = m.group(1)
            data.setdefault(current_list_key, [])
            continue
        m = SCALAR.match(line)
        if m:
            data[m.group(1)] = m.group(2)
    return data


def load(path=DEFAULT_FILE) -> dict:
    """Raises FileNotFoundError or ValueError with a message safe to print and act on."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"no {path}: run adopt.sh <path> --coder <acct> --reviewer <acct> --owner <acct>, or fill it by hand")
    data = parse(p.read_text(encoding="utf-8"))
    missing = [k for k in ("coder", "reviewer", "owner") if not data.get(k)]
    if missing:
        raise ValueError(f"{path} is missing {', '.join(missing)} -- fill it in before any script trusts it")
    return data


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["get"])
    ap.add_argument("field", choices=["coder", "reviewer", "owner", "shipquick_repo"])
    ap.add_argument("--file", default=DEFAULT_FILE)
    a = ap.parse_args(argv)
    try:
        data = load(a.file)
    except (FileNotFoundError, ValueError) as e:
        print(str(e), file=sys.stderr)
        return 1
    value = data.get(a.field)
    if value is None:
        print(f"{a.field} is not set in {a.file}", file=sys.stderr)
        return 1
    print(",".join(value) if isinstance(value, list) else value)
    return 0


if __name__ == "__main__":
    sys.exit(main())
