"""Test-impact manifest validator (ADR-023).

Validates .shipquick/test-impact.yml (or a given file) against the strict schema.
Usage:
  python3 scripts/check_test_impact.py [--file PATH] [--require] [--json]
Exit 0 on valid, 1 on invalid. With --require, a missing file also fails.
"""
import argparse
import json
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

TOP_LEVEL_KEYS = {"version", "languages", "global_impact", "mappings", "contract_groups", "full_suite_commands"}
REQUIRED_LANG_KEYS = {"id", "source", "tests", "runner", "command"}
LANG_KEYS = REQUIRED_LANG_KEYS | {"exclude", "full_suite"}
MAPPING_KEYS = {"source", "tests"}
CONTRACT_KEYS = {"id", "tests"}


def validate(data) -> list[str]:
    errors = []
    if not isinstance(data, dict):
        return ["manifest must be a YAML mapping"]
    unknown = set(data) - TOP_LEVEL_KEYS
    if unknown:
        errors.append(f"unknown top-level keys: {sorted(unknown)}")
    if "version" not in data:
        errors.append("missing required key: version")
    elif data["version"] != 1:
        errors.append(f"version must be 1, got {data['version']!r}")

    # languages
    langs = data.get("languages", [])
    if langs is None:
        langs = []
    if not isinstance(langs, list):
        errors.append("languages must be a list")
        langs = []
    ids = set()
    for i, lang in enumerate(langs):
        if not isinstance(lang, dict):
            errors.append(f"languages[{i}] must be a mapping")
            continue
        missing = REQUIRED_LANG_KEYS - set(lang)
        if missing:
            errors.append(f"languages[{i}] missing keys: {sorted(missing)}")
        extra = set(lang) - LANG_KEYS
        if extra:
            errors.append(f"languages[{i}] unknown keys: {sorted(extra)}")
        lid = lang.get("id")
        if lid is not None:
            if lid in ids:
                errors.append(f"duplicate language id: {lid!r}")
            ids.add(lid)
        for key in ("source", "tests", "exclude"):
            val = lang.get(key)
            if val is not None and not (isinstance(val, list) and all(isinstance(x, str) and x.strip() for x in val)):
                errors.append(f"languages[{i}].{key} must be a list of non-empty strings")
        if lang.get("tests") == []:
            errors.append(f"languages[{i}].tests must not be empty")
        if lang.get("source") == []:
            errors.append(f"languages[{i}].source must not be empty")
        for key in ("runner", "command", "full_suite"):
            val = lang.get(key)
            if val is not None and not (isinstance(val, str) and val.strip()):
                errors.append(f"languages[{i}].{key} must be a non-empty string")

    # global_impact
    gi = data.get("global_impact", [])
    if gi is None:
        gi = []
    if not isinstance(gi, list) or not all(isinstance(x, str) and x.strip() for x in gi):
        errors.append("global_impact must be a list of non-empty strings")

    # mappings
    mappings = data.get("mappings", [])
    if mappings is None:
        mappings = []
    if not isinstance(mappings, list):
        errors.append("mappings must be a list")
        mappings = []
    msrcs = set()
    for i, m in enumerate(mappings):
        if not isinstance(m, dict):
            errors.append(f"mappings[{i}] must be a mapping")
            continue
        extra = set(m) - MAPPING_KEYS
        if extra:
            errors.append(f"mappings[{i}] unknown keys: {sorted(extra)}")
        if "source" not in m or "tests" not in m:
            errors.append(f"mappings[{i}] must have source and tests")
            continue
        src = m["source"]
        if isinstance(src, str):
            srcs = [src]
        elif isinstance(src, list) and all(isinstance(x, str) for x in src):
            srcs = src
        else:
            errors.append(f"mappings[{i}].source must be a string or list of strings")
            srcs = []
        for s in srcs:
            if s in msrcs:
                errors.append(f"duplicate mapping source: {s!r}")
            msrcs.add(s)
        tests = m["tests"]
        if not (isinstance(tests, list) and tests and all(isinstance(x, str) and x.strip() for x in tests)):
            errors.append(f"mappings[{i}].tests must be a non-empty list of strings")

    # contract_groups
    cg = data.get("contract_groups", [])
    if cg is None:
        cg = []
    if not isinstance(cg, list):
        errors.append("contract_groups must be a list")
        cg = []
    cids = set()
    for i, c in enumerate(cg):
        if not isinstance(c, dict):
            errors.append(f"contract_groups[{i}] must be a mapping")
            continue
        extra = set(c) - CONTRACT_KEYS
        if extra:
            errors.append(f"contract_groups[{i}] unknown keys: {sorted(extra)}")
        if "id" not in c or "tests" not in c:
            errors.append(f"contract_groups[{i}] must have id and tests")
            continue
        if c["id"] in cids:
            errors.append(f"duplicate contract group id: {c['id']!r}")
        cids.add(c["id"])
        if not (isinstance(c["tests"], list) and c["tests"] and all(isinstance(x, str) for x in c["tests"])):
            errors.append(f"contract_groups[{i}].tests must be a non-empty list of strings")

    # full_suite_commands
    fsc = data.get("full_suite_commands", {})
    if fsc is None:
        fsc = {}
    if not isinstance(fsc, dict) or not all(isinstance(k, str) and isinstance(v, str) and v.strip() for k, v in fsc.items()):
        errors.append("full_suite_commands must be a mapping of non-empty strings")

    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=".shipquick/test-impact.yml")
    ap.add_argument("--require", action="store_true", help="fail if file is missing")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    path = Path(args.file)
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    if not path.exists():
        if args.require:
            print(f"manifest missing: {path}")
            return 1
        print(f"manifest not found: {path} (skipped)")
        return 0
    try:
        data = yaml.safe_load(path.read_text())
    except Exception as e:
        print(f"manifest unreadable: {e}")
        return 1
    if data is None:
        data = {}
    errors = validate(data)
    if args.json:
        print(json.dumps({"ok": not errors, "errors": errors}))
    else:
        if errors:
            for e in errors:
                print(e)
            print("manifest INVALID")
        else:
            print("manifest OK")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
