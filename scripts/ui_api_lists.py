#!/usr/bin/env python3
"""Story #231: the full UI API lists, generated from each library's own public API. Stdlib only.

Android: the API dump of androidx.compose.material3 at a pinned stable release (AOSP
`compose/material3/material3/api/current.txt`). iOS: Apple's SwiftUI documentation JSON (every type that
conforms to View, and every View modifier on the presentation and control pages).

--fetch downloads the sources and saves a small extract of each under docs/research/sources/.
The default run parses those saved extracts offline and writes docs/research/android-m3-api.md and
docs/research/ios-swiftui-api.md. --check writes nothing: it exits 1 when a saved extract does not match
the sha256 in its list, or a list does not match what its extract gives.

usage: ui_api_lists.py [--fetch] [--check]
"""
import argparse
import base64
import hashlib
import json
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
RESEARCH = KIT / "docs" / "research"
SOURCES = RESEARCH / "sources"
ANDROID_SRC, IOS_SRC = SOURCES / "android-m3-api-extract.txt", SOURCES / "ios-swiftui-extract.json"
ANDROID_MD, IOS_MD = RESEARCH / "android-m3-api.md", RESEARCH / "ios-swiftui-api.md"
DATE = "2026-11-09"

# Material 3 1.4.0 is the latest stable on Google's release page (read 2026-11-09). The commit is the end of
# the "these commits" link in its release note, so the pin is a fixed commit, not a moving branch.
M3_VERSION = "1.4.0"
M3_COMMIT = "5113b82a4ed6416d6344efa50e41db8cb65928ff"
M3_URL = ("https://android.googlesource.com/platform/frameworks/support/+/" + M3_COMMIT
          + "/compose/material3/material3/api/current.txt")
M3_RELEASES = "https://developer.android.com/jetpack/androidx/releases/compose-material3"

APPLE = "https://developer.apple.com/tutorials/data"
APPLE_PAGE = "https://developer.apple.com"
# The SwiftUI collection pages whose View modifiers count: presentation (first four) and control (last three).
MODIFIER_PAGES = ["modal-presentations", "toolbars", "search", "navigation",
                  "controls-and-indicators", "menus-and-commands", "text-input-and-output"]

HEADER = re.compile(r"^// shipquick: (\w+): (.*)$")
PACKAGE = re.compile(r"^package ([\w.]+) \{")
CLASS = re.compile(r"^  (.*?)public (?:[a-z]+ )*(?:class|interface|enum|@interface) ([\w.]+)")
METHOD = re.compile(r"^    method (.*?)public (?:[a-z]+ )*[^ (]+ ([\w$-]+)\(")


def sha(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- Android

def file_family(kt):
    """`ButtonKt` -> Button, `AndroidMenu_androidKt` -> Menu: the source file a top-level function lives in."""
    name = re.sub(r"(_\w+)?Kt$", "", kt)
    return name[7:] if name.startswith("Android") and name[7:8].isupper() else name


def parse_android(text):
    """(entries, left_out) from current.txt lines. A name with several overloads is one entry."""
    found, classes, pkg, cls = {}, [], "", None
    for line in text.splitlines():
        if m := PACKAGE.match(line):
            pkg = m.group(1)
        elif m := CLASS.match(line):
            cls = m.group(2)
            if "." not in cls and not cls.endswith("Kt"):
                classes.append((cls, pkg, m.group(1)))
        elif (m := METHOD.match(line)) and "runtime.Composable " in m.group(1) and "@BytecodeOnly" not in m.group(1):
            annots, name = m.group(1), m.group(2)
            static = " static " in line.split("(", 1)[0]
            if not static and (not name[:1].isupper() or cls.endswith("Defaults")):
                continue   # slot helpers of a Defaults object are listed with that object
            e = found.setdefault(name, {"name": name, "package": pkg, "home": cls, "static": static, "overloads": []})
            e["overloads"].append(annots)
    families = {file_family(e["home"]) for e in found.values() if e["static"]}

    def family_of(stem):
        if stem in families:
            return stem
        if stem in found and found[stem]["static"]:
            return file_family(found[stem]["home"])
        return max((f for f in families if stem.startswith(f)), key=len, default=stem)

    entries, left = [], []
    for e in found.values():
        name = e["name"]
        if e["static"]:
            fam = file_family(e["home"])
            if name[:1].isupper():
                kind, what = ("component" if name == fam else "variant"), "composable"
            else:
                kind, what = "supporting", ("remember" if name.startswith("remember") else "helper")
        else:
            fam = family_of(re.sub(r"(Box)?Scope$", "", e["home"]))
            kind, what = "variant", "scope composable"
        live = [a for a in e["overloads"] if "@Deprecated" not in a]
        row = {"name": name, "kind": kind, "what": what, "family": fam, "package": e["package"],
               "experimental": bool(live) and all("Experimental" in a for a in live)}
        (entries if live else left).append(row if live else {**row, "reason": "Deprecated in current.txt (`@Deprecated` on every overload)"})
    for name, pkg, annots in classes:
        m = re.match(r"(.+?)(Defaults|Colors|State)$", name)
        if not m:
            continue
        row = {"name": name, "kind": "supporting", "what": {"Defaults": "defaults", "Colors": "colors", "State": "state holder"}[m.group(2)],
               "family": family_of(m.group(1)), "package": pkg, "experimental": "Experimental" in annots}
        (left.append({**row, "reason": "Deprecated in current.txt (`@Deprecated` on the class)"}) if "@Deprecated" in annots else entries.append(row))
    order = {"component": 0, "variant": 1, "supporting": 2}
    entries.sort(key=lambda r: (r["family"].lower(), order[r["kind"]], r["name"].lower()))
    left.sort(key=lambda r: r["name"].lower())
    return entries, left


def android_extract(full):
    """Only the lines the parser reads; a method line is cut after its first `(`, so the saved file stays small."""
    keep = [line if not line.startswith("    ") else line.split("(", 1)[0] + "(" for line in full.splitlines()
            if PACKAGE.match(line) or CLASS.match(line) or (METHOD.match(line) and "runtime.Composable " in line and "@BytecodeOnly" not in line)]
    head = [f"// shipquick: source: {M3_URL}", f"// shipquick: version: {M3_VERSION}", f"// shipquick: fetched: {DATE}",
            f"// shipquick: upstream_sha256: {sha(full)}", f"// shipquick: upstream_lines: {len(full.splitlines())}"]
    return "\n".join(head + keep) + "\n"


def headers(text):
    return {m.group(1): m.group(2) for line in text.splitlines() if (m := HEADER.match(line))}


def android_md(extract):
    h = headers(extract)
    entries, left = parse_android(extract)
    rows = [f"| {i} | `{r['name']}` | {r['kind']} | {r['what']} | {r['family']} | `{r['package']}` | {'yes' if r['experimental'] else '-'} |"
            for i, r in enumerate(entries, 1)]
    return "\n".join([
        "# Android: the full Compose Material 3 API list (story #231)",
        "",
        "Generated by `python3 scripts/ui_api_lists.py`. Do not edit by hand. `--check` fails when this file is stale.",
        "",
        f"Source (Tier A, Google's AOSP source): {h['source']}",
        f"Version: `androidx.compose.material3:material3:{h['version']}`, the latest stable on {M3_RELEASES} (read {h['fetched']}).",
        f"Date: {h['fetched']}",
        f"Upstream file sha256: `{h['upstream_sha256']}` ({h['upstream_lines']} lines, too big to save).",
        f"Saved extract: `docs/research/sources/{ANDROID_SRC.name}` sha256 `{sha(extract)}`",
        "",
        *summary(entries, left),
        "",
        "How to read it:",
        "- One row is one name. Its overloads are one row.",
        "- `component`: a top-level composable with the same name as its source file (Button in Button.kt).",
        "- `variant`: another composable of that file (FilledTonalButton in Button.kt), or a composable of a scope.",
        "- `supporting`: `remember...`, other lower-case composables, `*Defaults`, `*Colors` and `*State` classes.",
        "- Family: the source file, or for a class, the family its name starts with. It is a hint for the family docs.",
        "- `@BytecodeOnly` lines are left out: they are the compiled twins of the lines above them.",
        "",
        "| # | Entry | Kind | What | Family | Package | Experimental |",
        "|---|---|---|---|---|---|---|",
        *rows,
        "",
        *left_table(left),
    ]) + "\n"


def summary(entries, left):
    n = {k: sum(r["kind"] == k for r in entries) for k in ("component", "variant", "supporting", "modifier")}
    parts = ", ".join(f"{k}: {v}" for k, v in n.items() if v or k != "modifier")
    return [f"Count: {len(entries)}", f"Kinds: {parts}. Left out: {len(left)}."]


def left_table(left):
    return ["## Left out, with the reason", "", f"Left out: {len(left)}", "", "| Entry | Reason |", "|---|---|",
            *[f"| `{r['name']}` | {r['reason']} |" for r in left]]


# ---------------------------------------------------------------- iOS

def ios_since(platforms):
    """(iOS since, reason it is left out or None) from a page's metadata.platforms."""
    ios = next((p for p in platforms or [] if p.get("name") == "iOS"), None)
    if ios is None:
        names = ", ".join(p["name"] for p in platforms or []) or "none"
        return None, f"Apple lists no iOS availability (only: {names})"
    if ios.get("unavailable"):
        return None, "Apple marks it unavailable on iOS"
    if ios.get("deprecatedAt") or ios.get("deprecated"):
        msg = f": {ios['message']}" if ios.get("message") else ""
        return None, f"Apple marks it deprecated on iOS {ios.get('deprecatedAt', '')}".rstrip() + msg
    return ios.get("introducedAt", "-"), None


def view_conformers(view_page):
    """[(title, url)] of every type the View page lists under Conforming Types."""
    refs = view_page["references"]
    return [(refs[i]["title"], refs[i]["url"]) for s in view_page.get("relationshipsSections", [])
            if s["type"] == "conformingTypes" for i in s["identifiers"]]


def page_modifiers(page):
    """[(title, url)] of the View instance methods a SwiftUI collection page links to."""
    refs = page["references"]
    return [(refs[i]["title"], refs[i]["url"]) for s in page.get("topicSections", []) for i in s["identifiers"]
            if refs.get(i, {}).get("url", "").startswith("/documentation/swiftui/view/")]


def ios_family(name):
    if "." in name:
        return re.sub(r"(Style)?(Configuration|Content|Collection|Builder)$", "", name.split(".", 1)[0]) or name
    if m := re.fullmatch(r"Default(\w+?)(Label|Actions|Shape)?", name):
        return m.group(1)
    return name


def parse_ios(extract):
    """(entries, left_out) from the saved extract."""
    entries, left = [], []
    for t in extract["types"]:
        name = t["name"]
        support = "." in name or (name.startswith("Default") and name != "Default")
        row = {"name": name, "kind": "supporting" if support else "component",
               "what": ("configuration part" if "." in name else "default part") if support else "view type",
               "family": ios_family(name), "url": t["url"]}
        since, why = ios_since(t["platforms"])
        (left.append({**row, "reason": why}) if why else entries.append({**row, "since": since}))
    by_base = {}
    for m in extract["modifiers"]:
        by_base.setdefault(m["title"].split("(", 1)[0], []).append(m)
    for base, group in by_base.items():
        got = [ios_since(m["platforms"]) for m in group]
        live = [s for s, why in got if not why]
        row = {"name": base, "kind": "modifier", "what": f"view modifier, {len(group)} overload(s)",
               "family": group[0]["page"], "url": group[0]["url"]}
        if live:
            entries.append({**row, "since": min(live, key=lambda v: [int(x) for x in re.findall(r"\d+", v)] or [0])})
        else:
            left.append({**row, "reason": got[0][1]})
    order = {"component": 0, "supporting": 1, "modifier": 2}
    entries.sort(key=lambda r: (order[r["kind"]], r["family"].lower(), r["name"].lower()))
    left.sort(key=lambda r: r["name"].lower())
    return entries, left


def ios_md(extract_text):
    extract = json.loads(extract_text)
    entries, left = parse_ios(extract)
    rows = [f"| {i} | `{r['name']}` | {r['kind']} | {r['what']} | {r['family']} | {r['since']} | {APPLE_PAGE}{r['url']} |"
            for i, r in enumerate(entries, 1)]
    return "\n".join([
        "# iOS: the full SwiftUI API list (story #231)",
        "",
        "Generated by `python3 scripts/ui_api_lists.py`. Do not edit by hand. `--check` fails when this file is stale.",
        "",
        f"Source (Tier A, Apple's documentation JSON): {extract['source']}",
        f"Version: Apple's SwiftUI documentation as served on {extract['fetched']} (Apple gives the data no version number).",
        f"Date: {extract['fetched']}",
        f"Saved extract: `docs/research/sources/{IOS_SRC.name}` sha256 `{sha(extract_text)}`",
        "",
        *summary(entries, left),
        "",
        "How to read it:",
        "- `component`: a type on the Conforming Types list of Apple's `View` page.",
        "- `supporting`: a part of one of those types (`ButtonStyleConfiguration.Label`) or a default part (`DefaultShareLinkLabel`).",
        "- `modifier`: a View modifier linked from a presentation or control page: " + ", ".join(MODIFIER_PAGES) + ".",
        "  Its overloads are one row. The family is the page it sits on.",
        "- iOS since: Apple's `introducedAt` for iOS. For a modifier, the earliest of its overloads.",
        "- Left out: only what Apple says is not on iOS, or deprecated on iOS, with Apple's own words.",
        "",
        "| # | Entry | Kind | What | Family | iOS since | Apple page |",
        "|---|---|---|---|---|---|---|",
        *rows,
        "",
        *left_table(left),
    ]) + "\n"


# ---------------------------------------------------------------- fetch, write, check

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "shipquick-ui-api-lists"})
    for attempt in (1, 2, 3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except OSError:
            if attempt == 3:
                raise


def apple_json(url_path):
    return json.loads(get(f"{APPLE}{url_path}.json"))


def fetch():
    SOURCES.mkdir(parents=True, exist_ok=True)
    full = base64.b64decode(get(M3_URL + "?format=TEXT")).decode("utf-8")
    ANDROID_SRC.write_text(android_extract(full), encoding="utf-8")
    types = view_conformers(apple_json("/documentation/swiftui/view"))
    mods = []
    for page in MODIFIER_PAGES:
        p = apple_json(f"/documentation/swiftui/{page}")
        mods += [(t, u, p["metadata"]["title"]) for t, u in page_modifiers(p)]
    mods = list(dict.fromkeys(mods))
    with ThreadPoolExecutor(8) as pool:
        tplat = list(pool.map(lambda tu: apple_json(tu[1])["metadata"].get("platforms"), types))
        mplat = list(pool.map(lambda m: apple_json(m[1])["metadata"].get("platforms"), mods))
    only_ios = lambda ps: [p for p in ps or [] if p.get("name") == "iOS"] or [{"name": p["name"]} for p in ps or []]
    extract = {"source": f"{APPLE}/documentation/swiftui/view.json and {APPLE}/documentation/swiftui/<page>.json",
               "fetched": DATE,
               "types": [{"name": t, "url": u, "platforms": only_ios(p)} for (t, u), p in zip(types, tplat)],
               "modifiers": [{"title": t, "url": u, "page": pg, "platforms": only_ios(p)} for (t, u, pg), p in zip(mods, mplat)]}
    IOS_SRC.write_text(json.dumps(extract, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def pinned(md_path):
    m = re.search(r"^Saved extract: `[^`]+` sha256 `([0-9a-f]{64})`$", md_path.read_text(encoding="utf-8"), re.M) if md_path.is_file() else None
    return m.group(1) if m else None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fetch", action="store_true", help="download the sources and save the extracts first")
    ap.add_argument("--check", action="store_true", help="write nothing; exit 1 when a list or extract is stale")
    ap.add_argument("--sources", type=Path, default=SOURCES)
    ap.add_argument("--out", type=Path, default=RESEARCH)
    a = ap.parse_args(argv)
    if a.fetch and not a.check:
        fetch()
    jobs = [(a.sources / ANDROID_SRC.name, a.out / ANDROID_MD.name, android_md),
            (a.sources / IOS_SRC.name, a.out / IOS_MD.name, ios_md)]
    errs = []
    for src, md, make in jobs:
        if not src.is_file():
            errs.append(f"{src}: saved source not found; run python3 scripts/ui_api_lists.py --fetch")
            continue
        text = src.read_text(encoding="utf-8")
        want = make(text)
        if not a.check:
            md.write_text(want, encoding="utf-8")
            print(f"wrote {md}: {want.splitlines()[[l.startswith('Kinds:') for l in want.splitlines()].index(True)]}")
            continue
        if pinned(md) != sha(text):
            errs.append(f"{md.name}: its pinned sha256 does not match {src.name}; run python3 scripts/ui_api_lists.py")
        elif md.read_text(encoding="utf-8") != want:
            errs.append(f"{md.name}: stale, it does not match {src.name}; run python3 scripts/ui_api_lists.py")
    for e in errs:
        print("FAIL", e)
    if not errs and a.check:
        print("OK: both API lists match their saved sources")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
