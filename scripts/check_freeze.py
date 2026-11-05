"""Story #126: a release freeze is a mechanism, not a sentence. `.shipquick/freeze` on `main`
carries `reason:` and `until:` lines; while it exists, a merge into `main` refuses. A freeze past
its `until:` date does not lift itself — it still refuses, with a STALE flag, until someone runs
`freeze.sh off` or renews it.

Usage: python3 scripts/check_freeze.py [--today YYYY-MM-DD] < freeze_file_content
No content (file absent, or empty stdin): exit 0, "not frozen".
Frozen: exit 1, the reason and until-date (or "STALE" past the until-date).
"""
import datetime
import re
import sys

FIELD = re.compile(r"^\s*(reason|until)\s*:\s*(\S.*)$", re.M | re.I)


def check(content: str | None, today: datetime.date) -> str | None:
    if not content or not content.strip():
        return None
    fields = {k.lower(): v.strip() for k, v in FIELD.findall(content)}
    reason = fields.get("reason", "(no reason given)")
    until_str = fields.get("until", "")
    try:
        until = datetime.date.fromisoformat(until_str)
    except ValueError:
        return f"frozen: {reason} (no valid until: date — add one, freeze.sh does not lift this itself)"
    if today > until:
        return f"frozen (STALE, was until {until}): {reason} — it does not lift itself; run freeze.sh off or renew with --until"
    return f"frozen until {until}: {reason}"


def main() -> int:
    today_str = None
    args = sys.argv[1:]
    if args and args[0] == "--today":
        today_str = args[1]
    today = datetime.date.fromisoformat(today_str) if today_str else datetime.date.today()
    why = check(sys.stdin.read(), today)
    print(why or "not frozen")
    return 1 if why else 0


if __name__ == "__main__":
    sys.exit(main())
