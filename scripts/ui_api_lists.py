#!/usr/bin/env python3
"""Story #231: the full UI API lists, generated from each library's own public API. Stdlib only.

Android: the API dump of androidx.compose.material3 at a pinned stable release (AOSP
`compose/material3/material3/api/current.txt`), plus the `@Deprecated` message of each deprecated entry from its
Kotlin source at the same commit. iOS: Apple's SwiftUI documentation JSON: every type on the `View` page's
Conforming Types list, and every View modifier the `View` page and its collection pages link to.

Nothing is left out. A deprecated entry, or one Apple does not offer on iOS, is a row with a `status`, the exact
data field it was read from, and the replacement (the vendor's own words) or the iOS alternative.

--fetch downloads the sources and saves small extracts under docs/research/sources/ (split into files under
500 KB). The default run parses those saved extracts offline and writes docs/research/android-m3-api.md and
docs/research/ios-swiftui-api.md. --check writes nothing: it exits 1 when a saved extract does not match the
sha256 its list pins, or a list does not match what its extracts give.

usage: ui_api_lists.py [--fetch] [--check]
"""
import argparse
import base64
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
RESEARCH = KIT / "docs" / "research"
SOURCES = RESEARCH / "sources"
ANDROID_SRC, IOS_SRC = SOURCES / "android-m3-api-extract.txt", SOURCES / "ios-swiftui-extract.json"
ANDROID_MD, IOS_MD = RESEARCH / "android-m3-api.md", RESEARCH / "ios-swiftui-api.md"
DATE = "2026-11-09"
MAX_FILE = 450_000   # the pre-commit limit is 500 KB; an extract over this splits into -2, -3 ... files

# Material 3 1.4.0 is the latest stable on Google's release page (read 2026-11-09). The commit is the end of
# the "these commits" link in its release note, so the pin is a fixed commit, not a moving branch.
M3_VERSION = "1.4.0"
M3_COMMIT = "5113b82a4ed6416d6344efa50e41db8cb65928ff"
AOSP = "https://android.googlesource.com/platform/frameworks/support/+/" + M3_COMMIT + "/compose/material3/material3"
M3_URL = AOSP + "/api/current.txt"
M3_RELEASES = "https://developer.android.com/jetpack/androidx/releases/compose-material3"

APPLE = "https://developer.apple.com/tutorials/data"
APPLE_PAGE = "https://developer.apple.com"

# Family hints for a name that starts with no family (review of PR #233): SheetState and SheetValue are bottom sheet API.
FAMILY_HINTS = {"Sheet": "BottomSheet"}
# SwiftUI types that hold views together but draw nothing of their own (review of PR #233). They stay rows,
# with category `plumbing`, and are documented together in one or two family docs.
PLUMBING = {"AnyShape", "AnyView", "DebugReplaceableView", "EditableCollectionContent", "EmptyView", "EquatableView",
            "FillShapeView", "GroupElementsOfContent", "GroupSectionsOfContent", "LabeledControlGroupContent",
            "LabeledToolbarItemGroupContent", "ModifiedContent", "OffsetShape", "OutlineSubgroupChildren",
            "PlaceholderContentView", "PresentedWindowContent", "PreviewModifierContent", "RotatedShape", "ScaledShape",
            "StrokeBorderShapeView", "StrokeShapeView", "Subview", "SubviewsCollection", "SubviewsCollectionSlice",
            "TransformedShape", "TupleContent", "TupleView"}
# The iOS alternative for each entry Apple does not offer on iOS. Apple's data names none, so this is our choice
# (confidence 0.7). Each value is a live row of the iOS list, or "none" when iOS has no such surface (a Mac window,
# a visionOS volume, the Touch Bar, the Digital Crown). The generator fails on a value that is not a live row, and a
# new unavailable entry fails until it is added here.
IOS_ALTERNATIVES = {
    # types
    "DefaultSettingsLinkLabel": "Link", "SettingsLink": "Link", "HelpLink": "Link", "TextFieldLink": "TextField",
    "DefaultWindowVisibilityToggleLabel": "none", "WindowVisibilityToggle": "none", "MenuButton": "Menu",
    "HSplitView": "NavigationSplitView", "VSplitView": "VStack", "GeometryReader3D": "GeometryReader",
    "ZStackContent3D": "ZStack", "GlassBackgroundEffectConfiguration.Content": "GlassEffectContainer",
    # modifiers with an iOS twin
    "textInputSuggestions": "searchSuggestions", "textInputCompletion": "searchCompletion",
    "toolbarItemHidden": "toolbarVisibility", "toolbarForegroundStyle": "toolbarColorScheme",
    "defaultWheelPickerItemHeight": "pickerStyle", "horizontalRadioGroupLayout": "pickerStyle",
    "menuButtonStyle": "menuStyle", "ornament": "toolbar", "glassBackgroundEffect": "glassEffect",
    "alternatingRowBackgrounds": "listRowBackground", "listRowPlatterColor": "listRowBackground",
    "listRowHoverEffect": "hoverEffect", "listRowHoverEffectDisabled": "hoverEffectDisabled", "hoverEffectGroup": "hoverEffect",
    "padding3D": "padding", "scaledToFill3D": "scaledToFill", "scaledToFit3D": "scaledToFit", "aspectRatio3D": "aspectRatio",
    "rotation3DLayout": "rotation3DEffect", "perspectiveRotationEffect": "rotation3DEffect", "transform3DEffect": "transformEffect",
    "visualEffect3D": "visualEffect", "onGeometryChange3D": "onGeometryChange", "onLongTouchGesture": "onLongPressGesture",
    "prefersDefaultFocus": "defaultFocus", "onCopyCommand": "copyable", "onCutCommand": "cuttable", "onPasteCommand": "pasteDestination",
    "onDeleteCommand": "swipeActions", "onMoveCommand": "onKeyPress", "pageCommand": "onKeyPress", "onExitCommand": "onKeyPress",
    "onPlayPauseCommand": "onKeyPress", "onCommand": "onKeyPress", "onModifierKeysChanged": "onKeyPress",
    "dialogSeverity": "alert", "dialogPreventsAppTermination": "none", "presentationPreventsAppTermination": "none",
    "presentedWindowStyle": "sheet", "presentedWindowToolbarStyle": "toolbar", "accessibilityQuickAction": "accessibilityAction",
    # no iOS surface: visionOS volumes and immersion, macOS windows and Touch Bar, watchOS crown and complications, tvOS
    **{name: "none" for name in (
        "directTouchSystemGesturesDisabled", "preferredSurroundingsEffect", "spatialOverlay", "spatialOverlayPreferenceValue",
        "breakthroughEffect", "contentCaptureProtected", "upperLimbVisibility", "volumeBaseplateVisibility",
        "accessoryWidgetGroupStyle", "windowDismissBehavior", "windowFullScreenBehavior", "windowMinimizeBehavior",
        "windowResizeAnchor", "windowResizeBehavior", "preferredWindowClippingMargins", "touchBar", "touchBarItemPrincipal",
        "touchBarCustomizationLabel", "touchBarItemPresence", "chart3DRenderingStyle", "modifierKeyAlternate",
        "handPointerBehavior", "manipulable", "manipulationGesture", "pointerVisibility", "pointerStyle", "focusScope",
        "focusSection", "dragPreviewsFormation", "dropPreviewsFormation", "digitalCrownAccessory", "digitalCrownRotation",
        "onImmersionChange", "onWorldRecenter", "immersiveEnvironmentPicker", "onVolumeViewpointChange",
        "supportedVolumeViewpoints", "exportsItemProviders", "importsItemProviders", "exportableToServices",
        "importableFromServices", "presentationBreakthroughEffect", "onWebViewImmersiveEnvironmentRequest",
        "webViewContextMenu", "continuityDevicePicker", "cameraAnchor", "foveatedStreamingPauseSheet",
        "groupActivityAssociation", "tabletopGame", "complicationForeground")},
}

HEADER = re.compile(r"^// shipquick: (\w+): (.*)$")
DEPRECATION = re.compile(r"^// shipquick: deprecation: (\S+) (\{.*\})$")
NUMBERED = re.compile(r"^(\d+)\t")
PACKAGE = re.compile(r"^package ([\w.]+) \{")
CLASS = re.compile(r"^  (.*?)public (?:[a-z]+ )*(class|interface|enum|@interface) ([\w.]+)")
METHOD = re.compile(r"^    method (.*?)public (?:[a-z]+ )*([^ (]+) ([\w$-]+)\(")
WHAT = {"class": "class", "interface": "interface", "enum": "enum", "@interface": "annotation"}


def sha(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- Android

def file_family(kt):
    """`ButtonKt` -> Button, `AndroidMenu_androidKt` -> Menu: the source file a top-level function lives in."""
    name = re.sub(r"(_\w+)?Kt$", "", kt)
    return name[7:] if name.startswith("Android") and name[7:8].isupper() else name


def replacement_of(dep):
    """The replacement Google names: the call in `ReplaceWith`, else the name after "Renamed to" / "Replaced with" /
    "Use" / "introduction of" in the message ("Not necessary with the introduction of Slider state" -> SliderState)."""
    msg = dep.get("message", "")
    if m := re.search(r"(?:Renamed to|Replaced with)\s+`?([A-Za-z_][\w.]*)", msg):
        return m.group(1)
    if m := re.match(r"\s*([A-Za-z_][\w.]*)\(", dep.get("replaceWith") or ""):
        return m.group(1)
    if m := re.search(r"\b[Uu]se (?:the )?`?([A-Za-z_][\w.]*)", msg):
        return m.group(1)
    if m := re.search(r"introduction of ([A-Z]\w*) (state|State)\b", msg):
        return m.group(1) + "State"
    return None


def parse_android(text, need_deps=True):
    """Every row from current.txt lines (or the saved extract). A name with several overloads is one row."""
    found, classes, deps, pkg, cls = {}, [], {}, "", ""
    for n, line in enumerate(text.splitlines(), 1):
        if m := DEPRECATION.match(line):
            deps[m.group(1)] = json.loads(m.group(2))
            continue
        if m := NUMBERED.match(line):   # an extract line keeps its current.txt line number
            n, line = int(m.group(1)), line[m.end():]
        if m := PACKAGE.match(line):
            pkg = m.group(1)
        elif m := CLASS.match(line):
            cls = m.group(3)
            if "." not in cls and not cls.endswith("Kt"):
                classes.append({"name": cls, "package": pkg, "annots": m.group(1), "what": WHAT[m.group(2)], "line": n})
        elif (m := METHOD.match(line)) and "runtime.Composable " in m.group(1) and "@BytecodeOnly" not in m.group(1):
            annots, ret, name = m.group(1), m.group(2), m.group(3)
            static = " static " in line.split("(", 1)[0]
            if not static:
                if not name[:1].isupper():
                    continue   # a lower-case member is part of its class's row (ButtonDefaults.buttonColors)
                name = f"{cls}.{name}"
            e = found.setdefault(name, {"name": name, "package": pkg, "home": cls, "static": static, "ret": ret, "overloads": []})
            e["overloads"].append((annots, n))
    families = {file_family(e["home"]) for e in found.values() if e["static"] and e["name"][:1].isupper()}
    class_names = {c["name"] for c in classes}

    def family_of(stem):
        hint = next((v for k, v in FAMILY_HINTS.items() if stem.startswith(k)), None)
        if hint:
            return hint
        if stem in families:
            return stem
        # The longest composable or family the name starts with: TopAppBarScrollBehavior -> TopAppBar -> AppBar.
        named = {n: file_family(e["home"]) for n, e in found.items() if e["static"] and n[:1].isupper()}
        named.update({f: f for f in families})
        best = max((n for n in named if stem.startswith(n)), key=len, default=None)
        return named[best] if best else stem

    def class_family(name):
        return family_of(re.sub(r"(Defaults|Colors|State)$", "", name) or name)

    def status(name, deprecated, where):
        if not deprecated:
            return {"status": "-", "replacement": "", "detail": "-"}
        dep = deps.get(name)
        if dep is None:
            if need_deps:
                raise ValueError(f"{name}: deprecated in current.txt, but no saved deprecation message; run --fetch")
            return {"status": "deprecated", "replacement": "", "detail": where}
        rep = replacement_of(dep)
        if not rep:
            raise ValueError(f"{name}: its @Deprecated message names no replacement: {dep}")
        return {"status": "deprecated", "replacement": rep,
                "detail": f"replacement: `{rep}`; {where}; message: \"{dep['message']}\" ({dep['source']})"}

    rows = []
    for e in found.values():
        name = e["name"]
        if not e["static"]:
            home = e["home"]
            fam = class_family(home) if home.endswith("Defaults") else family_of(re.sub(r"(Box)?Scope$", "", home))
            kind, what = "variant", "defaults slot composable" if home.endswith("Defaults") else "scope composable"
        elif name[:1].isupper():
            fam = file_family(e["home"])
            kind, what = ("component" if name == fam else "variant"), "composable"
        else:
            ret = e["ret"].rsplit(".", 1)[-1]
            fam = class_family(ret) if name.startswith("remember") and ret in class_names else file_family(e["home"])
            kind, what = "supporting", ("remember" if name.startswith("remember") else "helper")
        live = [a for a, _ in e["overloads"] if "@Deprecated" not in a]
        lines = [str(n) for _, n in e["overloads"]]
        where = f"`@Deprecated` on every overload: current.txt line{'s' if len(lines) > 1 else ''} {', '.join(lines)} (class `{e['home']}`)"
        rows.append({"name": name, "kind": kind, "what": what, "family": fam, "package": e["package"], "home": e["home"],
                     "experimental": bool(live) and all("Experimental" in a for a in live), **status(name, not live, where)})
    for c in classes:
        m = re.match(r".+?(Defaults|Colors|State)$", c["name"])
        what = {"Defaults": "defaults", "Colors": "colors", "State": "state holder"}[m.group(1)] if m else c["what"]
        where = f"`@Deprecated` on the class line: current.txt line {c['line']}"
        rows.append({"name": c["name"], "kind": "supporting", "what": what, "family": class_family(c["name"]),
                     "package": c["package"], "home": c["name"], "experimental": "Experimental" in c["annots"],
                     **status(c["name"], "@Deprecated" in c["annots"], where)})
    # A family with no live component of its own name gets one `family` row, so the family doc itself is counted.
    live_components = {r["name"] for r in rows if r["kind"] == "component" and r["status"] == "-"}
    for fam in sorted({r["family"] for r in rows if r["kind"] in ("component", "variant")} - live_components):
        pkg = next(r["package"] for r in rows if r["family"] == fam)
        rows.append({"name": fam, "kind": "family", "what": "family", "family": fam, "package": pkg, "home": "",
                     "experimental": False, "status": "-", "replacement": "", "detail": "-"})
    order = {"family": 0, "component": 1, "variant": 2, "supporting": 3}
    rows.sort(key=lambda r: (r["family"].lower(), order[r["kind"]], r["name"].lower()))
    return rows


def android_extract(full, deps=None):
    """Only the lines the parser reads, each as `<current.txt line number><tab><text>`; a method line is cut after
    its first `(`, so the saved file stays small. Saved deprecation messages follow as header lines."""
    keep = [f"{n}\t" + (line if not line.startswith("    ") else line.split("(", 1)[0] + "(")
            for n, line in enumerate(full.splitlines(), 1)
            if PACKAGE.match(line) or CLASS.match(line) or (METHOD.match(line) and "runtime.Composable " in line and "@BytecodeOnly" not in line)]
    dep_lines = [line for line in full.splitlines() if DEPRECATION.match(line)]
    dep_lines += [f"// shipquick: deprecation: {k} {json.dumps(v, ensure_ascii=False)}" for k, v in sorted((deps or {}).items())]
    head = [f"// shipquick: source: {M3_URL}", f"// shipquick: version: {M3_VERSION}", f"// shipquick: fetched: {DATE}",
            f"// shipquick: upstream_sha256: {sha(full)}", f"// shipquick: upstream_lines: {len(full.splitlines())}"]
    return "\n".join(head + dep_lines + keep) + "\n"


def kotlin_deprecation(source, name):
    """{"message", "replaceWith"} of the `@Deprecated(...)` right before the declaration of `name` (a fun, class or
    object) in a Kotlin file, or None when that declaration has no `@Deprecated` of its own."""
    simple = name.rsplit(".", 1)[-1]
    for m in re.finditer(rf"\b(?:fun|class|object|interface)\s+(?:[\w.<>, ]+\.)?{re.escape(simple)}\b\s*[(<{{:]?", source):
        start = source.rfind("@Deprecated(", 0, m.start())
        if start < 0:
            continue
        depth, i = 0, start + len("@Deprecated")
        for i in range(i, len(source)):
            depth += {"(": 1, ")": -1}.get(source[i], 0)
            if depth == 0:
                break
        if not re.search(r"[{}]|\bfun\b|\bval\b|\bclass\b", re.sub(r"\([^()]*\)", "", source[i + 1:m.start()])):
            break   # only annotations and modifiers sit between this @Deprecated and the declaration
    else:
        return None
    args = source[start:i + 1]
    msg = (re.search(r"message\s*=\s*((?:\"(?:[^\"\\]|\\.)*\"\s*\+?\s*)+)", args)
           or re.match(r"@Deprecated\(\s*((?:\"(?:[^\"\\]|\\.)*\"\s*\+?\s*)+)", args))   # the message as the first argument
    rw = re.search(r"ReplaceWith\(\s*\"((?:[^\"\\]|\\.)*)\"", args)
    return {"message": "".join(re.findall(r"\"((?:[^\"\\]|\\.)*)\"", msg.group(1))) if msg else "",
            "replaceWith": rw.group(1) if rw else ""}


def kotlin_path(package, home):
    """`TabRowKt` -> src/commonMain/.../TabRow.kt; `AndroidMenu_androidKt` -> src/androidMain/.../AndroidMenu.android.kt."""
    base, pkg = re.sub(r"Kt$", "", home), package.replace(".", "/")
    if "_" in base:
        name, plat = base.split("_", 1)
        return f"{AOSP}/src/{plat}Main/kotlin/{pkg}/{name}.{plat}.kt"
    return f"{AOSP}/src/commonMain/kotlin/{pkg}/{base}.kt"


def headers(text):
    return {m.group(1): m.group(2) for line in text.splitlines() if (m := HEADER.match(line)) and m.group(1) != "deprecation"}


def counts(rows, extra=()):
    kinds = {}
    for r in rows:
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    status = {s: sum(r["status"] == s for r in rows) for s in ("-", "deprecated", "unavailable-ios")}
    lines = [f"Count: {len(rows)}",
             "Kinds: " + ", ".join(f"{k}: {v}" for k, v in sorted(kinds.items())) + ".",
             f"Status: stable: {status['-']}, deprecated: {status['deprecated']}, unavailable-ios: {status['unavailable-ios']}.",
             *extra]
    return lines


def android_md(files):
    (name, extract), = files.items()
    h = headers(extract)
    rows = parse_android(extract)
    table = [f"| {i} | `{r['name']}` | {r['kind']} | {r['what']} | {r['family']} | `{r['package']}` | "
             f"{'yes' if r['experimental'] else '-'} | {r['status']} | {r['detail']} |" for i, r in enumerate(rows, 1)]
    return "\n".join([
        "# Android: the full Compose Material 3 API list (story #231)",
        "",
        "Generated by `python3 scripts/ui_api_lists.py`. Do not edit by hand. `--check` fails when this file is stale.",
        "",
        f"Source (Tier A, Google's AOSP source): {h['source']}",
        f"Version: `androidx.compose.material3:material3:{h['version']}`, the latest stable on {M3_RELEASES} (read {h['fetched']}).",
        f"Date: {h['fetched']}",
        f"Upstream file sha256: `{h['upstream_sha256']}` ({h['upstream_lines']} lines, too big to save).",
        f"Saved extract: `docs/research/sources/{name}` sha256 `{sha(extract)}`",
        "",
        *counts(rows),
        "",
        "How to read it:",
        "- One row is one name. Its overloads are one row. Nothing is left out.",
        "- `component`: a top-level composable with the same name as its source file (Button in Button.kt).",
        "- `variant`: another composable of that file (FilledTonalButton in Button.kt), a composable of a scope,",
        "  or a composable inside a `*Defaults` object (`SliderDefaults.Thumb`).",
        "- `supporting`: `remember...` and other lower-case composables, and every public top-level class, interface,",
        "  enum and annotation (`*Defaults`, `*Colors`, `*State`, `SnackbarData`, `ColorScheme`).",
        "- `family`: a family with no live component of its own name (AppBar holds TopAppBar and BottomAppBar).",
        "- Family: the source file; for a class, the family its name starts with; for `remember...`, the family of the",
        "  class it returns. It is the hint for the family docs.",
        "- Status: `deprecated` when every overload has `@Deprecated`. Detail names those current.txt lines, the",
        "  replacement Google names, and Google's message from the Kotlin source at the same commit.",
        "- `@BytecodeOnly` lines are not rows: they are the compiled twins of the lines above them.",
        "",
        "| # | Entry | Kind | What | Family | Package | Experimental | Status | Detail |",
        "|---|---|---|---|---|---|---|---|---|",
        *table,
    ]) + "\n"


# ---------------------------------------------------------------- iOS

def ios_status(platforms):
    """(status, iOS since, the exact `metadata.platforms` field and value) of one Apple page."""
    ios = next((p for p in platforms or [] if p.get("name") == "iOS"), None)
    if ios is None:
        names = ", ".join(p["name"] for p in platforms or []) or "none"
        return "unavailable-ios", "-", f"`metadata.platforms[]` has no `iOS` entry (names: {names})"
    if ios.get("unavailable"):
        return "unavailable-ios", "-", "`metadata.platforms[iOS].unavailable`: `true`"
    field = "deprecatedAt" if ios.get("deprecatedAt") else "deprecated" if ios.get("deprecated") else None
    if field:
        value = ios[field] if field == "deprecatedAt" else "true"
        msg = "".join(f", `{k}`: \"{ios[k]}\"" for k in ("renamed", "message") if ios.get(k))
        return "deprecated", ios.get("introducedAt", "-"), f"`metadata.platforms[iOS].{field}`: `{value}`{msg}"
    return "-", ios.get("introducedAt", "-"), ""


def apple_replacement(field_text):
    """The name Apple names instead: its `renamed` field, else "use X" or "with X" in its message."""
    m = (re.search(r"`renamed`: \"([A-Za-z_][\w.]*)", field_text) or re.search(r"\b[Uu]se\s+[.`]*([A-Za-z_][\w]*)", field_text)
         or re.search(r"\bwith\s+`?([A-Z]\w*)", field_text))
    return m.group(1) if m else None


def view_conformers(view_page):
    """[(title, url)] of every type the View page lists under Conforming Types."""
    refs = view_page["references"]
    return [(refs[i]["title"], refs[i]["url"]) for s in view_page.get("relationshipsSections", [])
            if s["type"] == "conformingTypes" for i in s["identifiers"]]


def page_modifiers(page):
    """[(title, url)] of the View instance methods (a title with `(`) a SwiftUI page links to."""
    refs = page["references"]
    return [(refs[i]["title"], refs[i]["url"]) for s in page.get("topicSections", []) for i in s["identifiers"]
            if refs.get(i, {}).get("url", "").startswith("/documentation/swiftui/view/") and "(" in refs[i]["title"]]


def modifier_pages(page):
    """The View collection pages (`view-presentation`, `view-input-and-events`, ...) a page links to."""
    refs = page["references"]
    return list(dict.fromkeys(refs[i]["url"].rsplit("/", 1)[1] for s in page.get("topicSections", []) for i in s["identifiers"]
                              if refs.get(i, {}).get("url", "").startswith("/documentation/swiftui/view-")))


def ios_family(name):
    if "." in name:
        return re.sub(r"(Style)?(Configuration|Content|Collection|Builder)$", "", name.split(".", 1)[0]) or name
    if m := re.fullmatch(r"Default(\w+?)(Label|Actions|Shape)?", name):
        return m.group(1)
    return name


def parse_ios(extract, alternatives=None):
    """Every row from the saved extract: each View type and each View modifier (its overloads as one row)."""
    alternatives = IOS_ALTERNATIVES if alternatives is None else alternatives
    rows = []
    for t in extract["types"]:
        name = t["name"]
        support = "." in name or (name.startswith("Default") and name != "Default")
        st, since, field = ios_status(t["platforms"])
        rows.append({"name": name, "kind": "supporting" if support else "component",
                     "what": ("configuration part" if "." in name else "default part") if support else "view type",
                     "family": ios_family(name), "url": t["url"], "category": "plumbing" if name in PLUMBING else "-",
                     "status": st, "since": since, "field": field})
    by_base = {}
    for m in extract["modifiers"]:
        by_base.setdefault(m["title"].split("(", 1)[0], []).append(m)
    for base, group in by_base.items():
        got = [ios_status(m["platforms"]) for m in group]
        live = [since for st, since, _ in got if st == "-"]
        dep = [g for g in got if g[0] == "deprecated"]
        st, since, field = ("-", min(live, key=lambda v: [int(x) for x in re.findall(r"\d+", v)] or [0]), "") if live else dep[0] if dep else got[0]
        if st != "-" and len(group) > 1:
            field = f"every overload ({len(group)}): " + "; ".join(dict.fromkeys(f for _, _, f in got))
        rows.append({"name": base, "kind": "modifier", "what": f"view modifier, {len(group)} overload(s)",
                     "family": group[0]["page"], "url": group[0]["url"], "category": "-",
                     "status": st, "since": since, "field": field})
    live_names, errs = {r["name"] for r in rows if r["status"] == "-"} | {"none"}, []
    for r in rows:
        r["replacement"], r["detail"] = "", "-"
        if r["status"] == "deprecated":
            r["replacement"] = apple_replacement(r["field"]) or ""
            if not r["replacement"]:
                errs.append(f"{r['name']}: Apple's deprecation names no replacement")
            r["detail"] = f"{r['field']}; replacement: `{r['replacement']}`"
        elif r["status"] == "unavailable-ios":
            alt = alternatives.get(r["name"])
            if alt is None:
                errs.append(f"{r['name']}: not on iOS; add its iOS alternative to IOS_ALTERNATIVES")
            elif alt not in live_names:
                errs.append(f"{r['name']}: its iOS alternative {alt} is not a live row of the iOS list")
            r["replacement"] = alt or ""
            r["detail"] = f"{r['field']}; iOS alternative (ours, Apple names none): `{alt}`"
    if errs:
        raise ValueError("; ".join(errs))
    order = {"component": 0, "supporting": 1, "modifier": 2}
    rows.sort(key=lambda r: (order[r["kind"]], r["family"].lower(), r["name"].lower()))
    return rows


def merge_ios(files):
    """One extract from its files: the first holds the header and types, every file adds modifiers."""
    parts = [json.loads(files[k]) for k in sorted(files, key=lambda k: int(re.search(r"(\d*)\.json$", k).group(1) or 1))]
    return {**parts[0], "modifiers": [m for p in parts for m in p.get("modifiers", [])]}


def ios_md(files):
    extract = merge_ios(files)
    rows = parse_ios(extract)
    table = [f"| {i} | `{r['name']}` | {r['kind']} | {r['what']} | {r['family']} | {r['since']} | {r['category']} | "
             f"{r['status']} | {r['detail']} | {APPLE_PAGE}{r['url']} |" for i, r in enumerate(rows, 1)]
    pins = [f"Saved extract: `docs/research/sources/{k}` sha256 `{sha(v)}`" for k, v in sorted(files.items())]
    return "\n".join([
        "# iOS: the full SwiftUI API list (story #231)",
        "",
        "Generated by `python3 scripts/ui_api_lists.py`. Do not edit by hand. `--check` fails when this file is stale.",
        "",
        f"Source (Tier A, Apple's documentation JSON): {extract['source']}",
        f"Version: Apple's SwiftUI documentation as served on {extract['fetched']} (Apple gives the data no version number).",
        f"Date: {extract['fetched']}",
        *pins,
        "",
        *counts(rows, [f"Category: plumbing: {sum(r['category'] == 'plumbing' for r in rows)}."]),
        "",
        "How to read it:",
        "- Nothing is left out. A row Apple deprecates, or does not offer on iOS, has a status.",
        "- `component`: a type on the Conforming Types list of Apple's `View` page.",
        "- `supporting`: a part of one of those types (`ButtonStyleConfiguration.Label`) or a default part (`DefaultShareLinkLabel`).",
        "- `modifier`: a View modifier that the `View` page or one of its collection pages (`view-presentation`,",
        "  `view-input-and-events`, ...) links to. Its overloads are one row. The family is the page it sits on.",
        "- Category `plumbing`: a type that holds views together and draws nothing itself (`TupleView`, `AnyView`).",
        "- iOS since: Apple's `introducedAt` for iOS. For a modifier, the earliest live overload.",
        "- Status and detail: the exact `metadata.platforms` field and value from the row's own Apple page, then the",
        "  replacement from Apple's deprecation message, or for `unavailable-ios` the iOS alternative we chose.",
        "",
        "| # | Entry | Kind | What | Family | iOS since | Category | Status | Detail | Apple page |",
        "|---|---|---|---|---|---|---|---|---|---|",
        *table,
    ]) + "\n"


# ---------------------------------------------------------------- fetch, write, check

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "shipquick-ui-api-lists"})
    for attempt in (1, 2, 3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404 or attempt == 3:
                raise
            time.sleep(5 * attempt)   # googlesource and Apple answer 429 under load; back off and retry
        except OSError:
            if attempt == 3:
                raise
            time.sleep(5 * attempt)


def apple_json(url_path):
    return json.loads(get(f"{APPLE}{url_path}.json"))


def kotlin_files(package):
    """Every .kt file URL of a package in commonMain and androidMain at the pinned commit (gitiles JSON listing)."""
    urls = []
    for plat in ("common", "android"):
        base = f"{AOSP}/src/{plat}Main/kotlin/{package.replace('.', '/')}"
        try:
            listing = json.loads(get(base + "/?format=JSON").decode("utf-8").split("\n", 1)[1])
        except OSError:
            continue
        urls += [f"{base}/{e['name']}" for e in listing["entries"] if e["name"].endswith(".kt")]
    return urls


def fetch_android():
    full = base64.b64decode(get(M3_URL + "?format=TEXT")).decode("utf-8")
    deps, files, texts = {}, {}, {}
    for r in parse_android(android_extract(full), need_deps=False):
        if r["status"] != "deprecated":
            continue
        guess = kotlin_path(r["package"], r["home"])
        files.setdefault(r["package"], kotlin_files(r["package"]))
        stem = lambda u: u.rsplit("/", 1)[1].split(".", 1)[0]
        # The file named by its Kt class first, then files whose name starts the entry's name, longest first.
        order = [guess] + sorted((u for u in files[r["package"]] if r["home"].startswith(stem(u)) or r["name"].startswith(stem(u))),
                                 key=lambda u: -len(stem(u))) + files[r["package"]]   # then every other file
        for url in dict.fromkeys(order):
            if url not in texts:
                try:
                    texts[url] = base64.b64decode(get(url + "?format=TEXT")).decode("utf-8")
                except OSError:
                    texts[url] = ""
            if dep := kotlin_deprecation(texts[url], r["name"]):
                deps[r["name"]] = {**dep, "source": url}
                break
        else:
            raise ValueError(f"{r['name']}: no @Deprecated(...) found before its declaration in {len(order)} files from {guess}")
    ANDROID_SRC.write_text(android_extract(full, deps), encoding="utf-8")


def fetch_ios():
    view = apple_json("/documentation/swiftui/view")
    types = view_conformers(view)
    mods, seen, queue = [(t, u, "View") for t, u in page_modifiers(view)], set(), modifier_pages(view)
    while queue:   # collection pages can link further collection pages
        page = queue.pop(0)
        if page in seen:
            continue
        seen.add(page)
        p = apple_json(f"/documentation/swiftui/{page}")
        mods += [(t, u, p["metadata"]["title"]) for t, u in page_modifiers(p)]
        queue += modifier_pages(p)
    mods = list({u: (t, u, pg) for t, u, pg in reversed(mods)}.values())[::-1]   # one per url, first page wins
    with ThreadPoolExecutor(8) as pool:
        tplat = list(pool.map(lambda tu: apple_json(tu[1])["metadata"].get("platforms"), types))
        mplat = list(pool.map(lambda m: apple_json(m[1])["metadata"].get("platforms"), mods))
    only_ios = lambda ps: [p for p in ps or [] if p.get("name") == "iOS"] or [{"name": p["name"]} for p in ps or []]
    head = {"source": f"{APPLE}/documentation/swiftui/view.json and the {APPLE}/documentation/swiftui/view-<topic>.json pages it links",
            "fetched": DATE, "types": [{"name": t, "url": u, "platforms": only_ios(p)} for (t, u), p in zip(types, tplat)]}
    all_mods = [{"title": t, "url": u, "page": pg, "platforms": only_ios(p)} for (t, u, pg), p in zip(mods, mplat)]
    chunks, cur = [], []
    for m in all_mods:   # split so no saved file passes MAX_FILE
        cur.append(m)
        if len(json.dumps(cur, indent=1, ensure_ascii=False)) > MAX_FILE - 120_000:
            chunks.append(cur)
            cur = []
    chunks.append(cur)
    for old in SOURCES.glob("ios-swiftui-extract*.json"):
        old.unlink()
    for i, chunk in enumerate(chunks, 1):
        body = {**head, "modifiers": chunk} if i == 1 else {"modifiers": chunk}
        path = IOS_SRC if i == 1 else SOURCES / f"ios-swiftui-extract-{i}.json"
        path.write_text(json.dumps(body, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def pinned(md_path):
    text = md_path.read_text(encoding="utf-8") if md_path.is_file() else ""
    return dict(re.findall(r"^Saved extract: `docs/research/sources/([^`]+)` sha256 `([0-9a-f]{64})`$", text, re.M))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fetch", action="store_true", help="download the sources and save the extracts first")
    ap.add_argument("--check", action="store_true", help="write nothing; exit 1 when a list or extract is stale")
    ap.add_argument("--sources", type=Path, default=SOURCES)
    ap.add_argument("--out", type=Path, default=RESEARCH)
    a = ap.parse_args(argv)
    if a.fetch and not a.check:
        SOURCES.mkdir(parents=True, exist_ok=True)
        fetch_android()
        fetch_ios()
    jobs = [([a.sources / ANDROID_SRC.name], a.out / ANDROID_MD.name, android_md),
            (sorted(a.sources.glob("ios-swiftui-extract*.json")) or [a.sources / IOS_SRC.name], a.out / IOS_MD.name, ios_md)]
    errs = []
    for srcs, md, make in jobs:
        missing = [s for s in srcs if not s.is_file()]
        if missing:
            errs += [f"{s}: saved source not found; run python3 scripts/ui_api_lists.py --fetch" for s in missing]
            continue
        files = {s.name: s.read_text(encoding="utf-8") for s in srcs}
        want = make(files)
        if not a.check:
            md.write_text(want, encoding="utf-8")
            print(f"wrote {md}: " + " ".join(l for l in want.splitlines() if l.startswith(("Count:", "Kinds:", "Status:", "Category:"))))
            continue
        have = {k: sha(v) for k, v in files.items()}
        if pinned(md) != have:
            errs.append(f"{md.name}: the extract sha256 it pins {pinned(md)} does not match the saved files {have}; run python3 scripts/ui_api_lists.py")
        elif md.read_text(encoding="utf-8") != want:
            errs.append(f"{md.name}: stale, it does not match {', '.join(files)}; run python3 scripts/ui_api_lists.py")
    for e in errs:
        print("FAIL", e)
    if not errs and a.check:
        print("OK: both API lists match their saved sources")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
