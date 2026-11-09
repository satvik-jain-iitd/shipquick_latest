#!/usr/bin/env python3
"""UI coverage gate (story #216, rule 38). Stdlib only.

Reads the two counted lists, docs/research/android-m3-components.md and docs/research/ios-swiftui-components.md.
Fails when: a Count line does not equal its table rows; a row has no doc or contract in ui/components/<Name>/;
a row's doc leaves that platform null (or names a type no row names); two Android rows share a folder; a row has
no `android-<name>` or `ios-<name>` topic in ui/integration/docs/; a doc sets a platform that no row names (extra).
An iOS row maps to its doc by "Our doc" (iOS-only) or by its M3 twin's folder in the Android list (shared).
Web: when ui/tool/node_modules/@astryxdesign/core exists, a name our integration serves (a topic, or a component it
registers) must not equal a core doc name, case and dashes ignored. Without core it prints a skip and passes,
unless --require-web (CI) is given.
usage: check_ui_coverage.py [--require-web]
"""
import argparse
import re
import sys
from pathlib import Path

from check_ui_docs import read_doc

KIT = Path(__file__).resolve().parent.parent
CORE = KIT / "ui" / "tool" / "node_modules" / "@astryxdesign" / "core"
IOS_ONLY = "none (iOS-only)"


def table(path):
    """(count from the `Count: N` line or None, numbered table rows as cell lists)."""
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^Count: (\d+)$", text, re.M)
    rows = [cells for line in text.splitlines() if line.startswith("|")
            for cells in [[c.strip() for c in line.strip().strip("|").split("|")]] if cells[0].isdigit()]
    return (int(m.group(1)) if m else None), rows


def key(name):
    return re.sub(r"[-_]", "", name).lower()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--android-list", type=Path, default=KIT / "docs" / "research" / "android-m3-components.md")
    ap.add_argument("--ios-list", type=Path, default=KIT / "docs" / "research" / "ios-swiftui-components.md")
    ap.add_argument("--components", type=Path, default=KIT / "ui" / "components")
    ap.add_argument("--topics", type=Path, default=KIT / "ui" / "integration" / "docs")
    ap.add_argument("--integration", type=Path, default=KIT / "ui" / "integration" / "astryx.integration.mjs")
    ap.add_argument("--core", type=Path, default=CORE)
    ap.add_argument("--require-web", action="store_true", help="fail when core is not installed (CI)")
    a = ap.parse_args(argv)
    errs = []

    docs = {}
    for folder in sorted(p for p in a.components.iterdir() if p.is_dir()) if a.components.is_dir() else []:
        d, c = folder / f"{folder.name}.doc.mjs", folder / f"{folder.name}.contract.json"
        if d.exists() and c.exists():
            docs[folder.name] = read_doc(d).get("platforms", {})

    android_n, android_rows = table(a.android_list)
    ios_n, ios_rows = table(a.ios_list)
    for label, n, rows in (("Android", android_n, android_rows), ("iOS", ios_n, ios_rows)):
        if n != len(rows):
            errs.append(f"{label} list: Count line says {n}, the table has {len(rows)} rows")

    # platform -> {doc name: set of types its rows name}
    want = {"android": {}, "ios": {}}
    m3_folder = {}
    for r in android_rows:
        name = r[2].strip("`").rstrip("/").rsplit("/", 1)[-1]
        if name in want["android"]:
            errs.append(f"Android row {r[0]} ({r[1]}): folder {name} is already used by another row")
        want["android"].setdefault(name, set()).add(r[3].strip("`"))
        m3_folder[r[1]] = name
    for r in ios_rows:
        name = r[6].strip("`") if r[5] == IOS_ONLY else m3_folder.get(r[5])
        if not name:
            errs.append(f"iOS row {r[0]} ({r[1]}): its M3 twin '{r[5]}' is not a row of the Android list")
            continue
        want["ios"].setdefault(name, set()).add(r[2].strip("`"))

    for platform, names in want.items():
        for name, types in names.items():
            if name not in docs:
                errs.append(f"{platform} {name}: missing doc or contract in {a.components / name}")
                continue
            got = docs[name].get(platform)
            if not got:
                errs.append(f"{platform} {name}: platforms.{platform} is not set (rows name {', '.join(sorted(types))})")
            elif got not in types:
                errs.append(f"{platform} {name}: platforms.{platform} is {got}, but its rows name {', '.join(sorted(types))}")
            if not (a.topics / f"{platform}-{name.lower()}.doc.mjs").exists():
                errs.append(f"{platform} {name}: missing topic {platform}-{name.lower()}; run python3 scripts/ui_topics.py")
        errs += [f"{platform} {name}: extra, platforms.{platform} is set but no row of the list names it"
                 for name, plat in docs.items() if plat.get(platform) and name not in names]

    if a.core.is_dir():
        core = {key(p.name[:-len(".doc.mjs")]): p.name[:-len(".doc.mjs")] for p in (a.core / "src").rglob("*.doc.mjs")}
        served = [p.name[:-len(".doc.mjs")] for p in a.topics.glob("*.doc.mjs")] if a.topics.is_dir() else []
        text = a.integration.read_text(encoding="utf-8") if a.integration.exists() else ""
        for block in re.findall(r"components\s*:\s*\[([^\]]*)\]", text):
            served += re.findall(r"['\"]([^'\"]+)['\"]", block)
        errs += [f"web: our name '{s}' shadows core's '{core[key(s)]}'; rename it" for s in served if key(s) in core]
    elif a.require_web:
        errs.append(f"web: core not found at {a.core}; run npm ci --ignore-scripts in ui/tool")
    else:
        print("skip web: run npm ci --ignore-scripts in ui/tool")

    for e in errs:
        print("FAIL", e)
    if errs:
        return 1
    print(f"OK: {len(android_rows)} Android and {len(ios_rows)} iOS rows covered, {len(docs)} docs, no extra")
    return 0


if __name__ == "__main__":
    sys.exit(main())
