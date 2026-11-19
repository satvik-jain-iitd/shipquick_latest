"""Flaky-test registry validator (M5b).

Validates .shipquick/flaky-tests.json. A quarantined test must have an owner, issue, reason,
quarantine date, and expiry. An expired quarantine fails the check.

Usage:
  python3 scripts/check_flaky.py [--file PATH] [--json]
Exit 0 on valid, 1 on invalid/expired.
"""
import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEFAULT = ROOT / ".shipquick" / "flaky-tests.json"

REQUIRED = {"test_id", "path", "owner", "issue", "reason", "quarantined_on", "expires_on", "status"}
VALID_STATUS = {"active", "quarantined", "fixed", "expired"}
VALID_TIER = {"pr", "post-merge", "nightly", "manual"}


def parse_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def validate(entries) -> list[str]:
    errors = []
    if not isinstance(entries, list):
        return ["registry must be a JSON array"]
    seen = set()
    today = date.today()
    for i, e in enumerate(entries):
        if not isinstance(e, dict):
            errors.append(f"entry {i} must be an object")
            continue
        missing = REQUIRED - set(e)
        if missing:
            errors.append(f"entry {i} missing: {sorted(missing)}")
            continue
        extra = set(e) - (REQUIRED | {"last_failure", "tier", "run_url"})
        if extra:
            errors.append(f"entry {i} unknown keys: {sorted(extra)}")
        tid = e["test_id"]
        if tid in seen:
            errors.append(f"duplicate test_id: {tid!r}")
        seen.add(tid)
        if e["status"] not in VALID_STATUS:
            errors.append(f"entry {i} invalid status: {e['status']!r}")
        if e.get("tier") and e["tier"] not in VALID_TIER:
            errors.append(f"entry {i} invalid tier: {e['tier']!r}")
        for key in ("owner", "issue", "reason", "path", "test_id"):
            if not isinstance(e[key], str) or not e[key].strip():
                errors.append(f"entry {i}.{key} must be a non-empty string")
        qd = parse_date(e["quarantined_on"])
        if qd is None:
            errors.append(f"entry {i}.quarantined_on must be YYYY-MM-DD")
        ed = parse_date(e["expires_on"])
        if ed is None:
            errors.append(f"entry {i}.expires_on must be YYYY-MM-DD")
        if qd and ed and ed < qd:
            errors.append(f"entry {i}: expires_on before quarantined_on")
        if e["status"] == "quarantined" and ed and ed < today:
            errors.append(f"entry {i}: quarantine expired on {ed} (test {tid!r})")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=str(DEFAULT))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    path = Path(args.file)
    if not path.exists():
        print("registry not found; treating as empty")
        entries = []
    else:
        try:
            entries = json.loads(path.read_text())
        except Exception as e:
            print(f"registry unreadable: {e}")
            return 1
    errors = validate(entries)
    if args.json:
        import json as _j
        print(_j.dumps({"ok": not errors, "errors": errors, "count": len(entries) if isinstance(entries, list) else 0}))
    else:
        if errors:
            for e in errors:
                print(e)
            print("flaky registry INVALID")
        else:
            print(f"flaky registry OK ({len(entries)} entries)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
