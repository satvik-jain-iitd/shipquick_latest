#!/usr/bin/env python3
"""UI coverage gate (story #216, rule 38). Stdlib only.

Reads the two counted lists, docs/research/android-m3-components.md and docs/research/ios-swiftui-components.md.
Fails when: a Count line does not equal its table rows; a row has no doc or contract in ui/components/<Name>/;
a row's doc leaves that platform null (or names a type no row names); two Android rows share a folder; a row has
no `android-<name>` or `ios-<name>` topic in ui/integration/docs/; a doc sets a platform that no row names (extra).
An iOS row maps to its doc by "Our doc" (iOS-only) or by its M3 twin's folder in the Android list (shared).
Rows must run 1 to N; a missing list file is a FAIL line. A doc that several rows share must match ROW_MAP row
for row, so deleting a row (and lowering Count) still fails.
Web: when ui/tool/node_modules/@astryxdesign/core exists, a name our integration serves (a topic, or a component it
registers, as a literal list only) must not equal a core doc name, case and dashes ignored. Core with no docs, or
fewer than --core-floor (100), fails. Without core it prints a skip and passes, unless --require-web (CI) is given.
usage: check_ui_coverage.py [--require-web]
"""
import argparse
import json
import re
import sys
from pathlib import Path

from check_ui_docs import read_doc

KIT = Path(__file__).resolve().parent.parent
CORE = KIT / "ui" / "tool" / "node_modules" / "@astryxdesign" / "core"
IOS_ONLY = "none (iOS-only)"
CORE_FLOOR = 100   # core 0.7.11 has 254 *.doc.mjs under src/; far fewer means its layout moved
# A doc that several rows share holds one name, so this map is what makes each of its rows count.
# Deleting a row from a list means editing this protected file too (rule 37), so it is never silent.
# Each row is named by its HIG component (column 2), since two Menu rows share the type SwiftUI.Menu.
ROW_MAP = {"ios": {
    "Menu": ["Context menus", "Menus", "Pop-up buttons", "Pull-down buttons"],
    "BottomSheet": ["Action sheets", "Sheets"],
    "TextField": ["Text fields", "Virtual keyboards"],
}}


def table(path, label):
    """(numbered table rows as cell lists, errors). Rows must run 1 to N, and N must equal the Count line."""
    if not path.is_file():
        return [], [f"{label} list: file not found: {path}"]
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^Count: (\d+)$", text, re.M)
    rows = [cells for line in text.splitlines() if line.startswith("|")
            for cells in [[c.strip() for c in line.strip().strip("|").split("|")]] if cells[0].isdigit()]
    errs = []
    n = int(m.group(1)) if m else None
    if n != len(rows):
        errs.append(f"{label} list: Count line says {n}, the table has {len(rows)} rows")
    nums = [int(r[0]) for r in rows]
    if nums != list(range(1, len(rows) + 1)):
        errs.append(f"{label} list: row numbers must run 1 to {len(rows)} with no gap or repeat, got {nums}")
    return rows, errs


# Only `components: ['A', "B"]`; a variable or a call there would hide what is served.
LITERAL_LIST = re.compile(r"""\bcomponents\s*:\s*\[\s*(?:(['"])[^'"]*\1\s*,?\s*)*\]""")


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
    ap.add_argument("--core-floor", type=int, default=CORE_FLOOR, help="fewest core docs that count as a real install")
    ap.add_argument("--row-map", type=Path, help="JSON {platform: {doc: [types]}} in place of ROW_MAP (tests)")
    a = ap.parse_args(argv)
    errs = []

    docs = {}
    for folder in sorted(p for p in a.components.iterdir() if p.is_dir()) if a.components.is_dir() else []:
        d, c = folder / f"{folder.name}.doc.mjs", folder / f"{folder.name}.contract.json"
        if d.exists() and c.exists():
            docs[folder.name] = read_doc(d).get("platforms", {})

    android_rows, e1 = table(a.android_list, "Android")
    ios_rows, e2 = table(a.ios_list, "iOS")
    errs += e1 + e2
    row_map = json.loads(a.row_map.read_text(encoding="utf-8")) if a.row_map else ROW_MAP

    # platform -> {doc name: set of types its rows name}
    want = {"android": {}, "ios": {}}
    m3_folder, ios_rows_of = {}, {}
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
        ios_rows_of.setdefault(name, []).append(r[1])
    mapped = row_map.get("ios", {})
    for name in sorted(set(mapped) | {n for n, rs in ios_rows_of.items() if len(rs) > 1}):
        have, need = set(ios_rows_of.get(name, [])), set(mapped.get(name, []))
        if name not in mapped:
            errs.append(f"ios {name}: {len(have)} rows share this doc, but the row map (ROW_MAP) does not list them: {sorted(have)}")
        elif have != need:
            errs.append(f"ios {name}: the row map lists {sorted(need - have)} missing from the list"
                        + (f", and the list has {sorted(have - need)} not in the row map" if have - need else ""))

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

    text = a.integration.read_text(encoding="utf-8") if a.integration.exists() else ""
    served = [p.name[:-len(".doc.mjs")] for p in a.topics.glob("*.doc.mjs")] if a.topics.is_dir() else []
    for m in re.finditer(r"\bcomponents\s*:", text):
        lit = LITERAL_LIST.match(text, m.start())
        if not lit:
            errs.append(f"web: {a.integration.name} sets components to something other than a literal list of names")
            continue
        served += [q[1:-1] for q in re.findall(r"'[^']*'|\"[^\"]*\"", lit.group(0))]
    if a.core.is_dir():
        core = {key(p.name[:-len(".doc.mjs")]): p.name[:-len(".doc.mjs")] for p in (a.core / "src").rglob("*.doc.mjs")}
        if not core:
            errs.append(f"web: no core docs found under {a.core / 'src'}; reinstall with npm ci --ignore-scripts in ui/tool")
        elif len(core) < a.core_floor:
            errs.append(f"web: only {len(core)} core docs under {a.core / 'src'}, below the floor of {a.core_floor}; did core's layout change?")
        errs +=[f"web: our name '{s}' shadows core's '{core[key(s)]}'; rename it" for s in served if key(s) in core]
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
