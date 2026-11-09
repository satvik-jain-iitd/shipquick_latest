"""Story #217: write the compile proofs, ui/android/proof/ApiProof.kt and ui/ios/proof/ApiProof.swift.

Each proof calls every component with every prop its contract names under `platforms.android` or
`platforms.ios`, by that exact name. CI compiles them against the real libraries (Compose Material 3,
SwiftUI), so a wrong or invented prop name fails the build. CI compiles only; nothing is run.

The prop names come from the contracts. This script holds only what a contract cannot say: which call
a prop belongs to (SPECS), a value for each type, and which Swift params have no label. A component
whose doc names a platform API but has no spec here fails the script, so nothing is skipped silently.
@OptIn is added per proof function from Google's current.txt extract, so a wrong opt-in fails too.

What the proof does not prove (limits, not bugs):
- A spec `v` override is not type-proved against the contract: it is compiled, so a value of the wrong type fails
  in the compiler, but nothing checks that it matches the contract's prop type.
- A Kotlin `{}` lambda does not prove arity: `{}` compiles for a callback of any number of parameters.
  The proof shows the prop name exists, not the callback's signature. Swift closures with `_ in` do check arity.

Usage: python3 scripts/ui_proof.py            write both proof files
       python3 scripts/ui_proof.py --check    exit 1 when a proof file is missing or stale
       python3 scripts/ui_proof.py --check --root <dir>   check against another components folder (tests)
"""
import argparse
import json
import re
import sys
from pathlib import Path

from check_ui_docs import read_doc

KIT = Path(__file__).resolve().parent.parent
SRC = KIT / "ui" / "components"
OUT = {"android": KIT / "ui" / "android" / "proof" / "ApiProof.kt",
       "ios": KIT / "ui" / "ios" / "proof" / "ApiProof.swift"}
EXTRACT = KIT / "docs" / "research" / "sources" / "android-m3-api-extract.txt"
OPTINS = ("ExperimentalMaterial3Api", "ExperimentalMaterial3ExpressiveApi")

# One spec per component: "t" the call with @GROUP@ holes, "g" which props go in which hole (in Swift
# argument order), "v" a value for one prop, "p" Swift props passed without a label. A prop no group
# names goes to @ARGS@, so a new or invented contract prop always lands in a real call.
# A value may hold a hole of its own (NavigationBar puts the items inside `content`).
ANDROID = {
    "AppBar": {"t": "TopAppBar(@ARGS@)"},
    "AppBarColumn": {"t": "AppBarColumn(@ARGS@)"},
    "AppBarRow": {"t": "AppBarRow(@ARGS@)"},
    "Badge": {"t": "BadgedBox(@ARGS@)"},
    "BottomSheet": {"t": "ModalBottomSheet(@ARGS@)"},
    "BottomSheetScaffold": {"t": "BottomSheetScaffold(@ARGS@)"},
    "Button": {"t": "Button(onClick = {}) {}"},
    "Card": {"t": "Card(@ARGS@)"},
    "Carousel": {"t": "HorizontalMultiBrowseCarousel(@ARGS@)"},
    "Checkbox": {"t": "Checkbox(@ARGS@)"},
    "Chip": {"t": "FilterChip(@ARGS@)"},
    "DatePicker": {"t": "DatePicker(@ARGS@)"},
    "DatePickerDialog": {"t": "DatePickerDialog(@ARGS@)"},
    "DateRangePicker": {"t": "DateRangePicker(@ARGS@)"},
    "Dialog": {"t": "AlertDialog(@ARGS@)"},
    "Divider": {"t": "HorizontalDivider(@ARGS@)"},
    "FloatingActionButton": {"t": "FloatingActionButton(@ARGS@)"},
    "Icon": {"t": "Icon(@ARGS@)"},
    "IconButton": {"t": "IconButton(@ARGS@)"},
    "List": {"t": "ListItem(@ARGS@)"},
    "MaterialTheme": {"t": "MaterialTheme(@ARGS@)"},
    "Menu": {"t": "DropdownMenu(@ARGS@)"},
    "NavigationBar": {"t": "NavigationBar(@ARGS@)", "g": {"ITEM": ["selected", "onClick", "icon", "label"]},
                      "v": {"content": "{ NavigationBarItem(@ITEM@) }"}},
    "NavigationDrawer": {"t": "ModalNavigationDrawer(@ARGS@)"},
    "NavigationRail": {"t": "NavigationRail(@ARGS@)"},
    "OutlinedTextField": {"t": "OutlinedTextField(@ARGS@)"},
    "ProgressIndicator": {"t": "LinearProgressIndicator(@ARGS@)", "v": {"progress": "{ 0.5f }"}},
    "RadioButton": {"t": "RadioButton(@ARGS@)"},
    "Scaffold": {"t": "Scaffold(@ARGS@)", "v": {"floatingActionButtonPosition": "FabPosition.End"}},
    "SearchBar": {"t": "SearchBar(@ARGS@)"},
    "SecureTextField": {"t": "SecureTextField(@ARGS@)", "v": {"textObfuscationMode": "TextObfuscationMode.RevealLastTyped"}},
    "SegmentedButton": {"t": "SingleChoiceSegmentedButtonRow { SegmentedButton(@ARGS@) }",
                        "v": {"shape": "SegmentedButtonDefaults.itemShape(index = 0, count = 1)"}},
    "ShortNavigationBar": {"t": "ShortNavigationBar(@ARGS@)", "v": {"arrangement": "ShortNavigationBarArrangement.Centered"}},
    "Slider": {"t": "Slider(@ARGS@)", "v": {"value": "0.5f"}},
    "Snackbar": {"t": "SnackbarHost(remember { SnackbarHostState() }) { data -> Snackbar(@ARGS@) }",
                 "v": {"snackbarData": "data"}},
    "SnackbarHost": {"t": "val hostState = remember { SnackbarHostState() }\n"
                          "LaunchedEffect(hostState) { hostState.showSnackbar(@SHOW@) }\n"
                          "SnackbarHost(@ARGS@)",
                     "g": {"SHOW": ["message", "actionLabel", "withDismissAction", "duration"]},
                     "v": {"hostState": "hostState", "duration": "SnackbarDuration.Short"}},
    "Surface": {"t": "Surface(@ARGS@)"},
    "SwipeToDismissBox": {"t": "SwipeToDismissBox(@ARGS@)"},
    "Switch": {"t": "Switch(@ARGS@)"},
    "Tab": {"t": "Tab(@ARGS@)"},
    "Tabs": {"t": "PrimaryTabRow(@ARGS@)", "v": {"selectedTabIndex": "0"}},
    "Text": {"t": "Text(\"x\", @ARGS@)"},
    "TextField": {"t": "TextField(@ARGS@)"},
    "TimePicker": {"t": "TimePicker(@ARGS@)"},
    "TimePickerDialog": {"t": "TimePickerDialog(@ARGS@)"},
    "Tooltip": {"t": "TooltipBox(@ARGS@)"},
    "TooltipLabel": {"t": "Label(@ARGS@)"},
    "WideNavigationRail": {"t": "WideNavigationRail(@ARGS@)"},
}
K_NAMED = {
    "TopAppBarScrollBehavior": "TopAppBarDefaults.pinnedScrollBehavior()",
    "SheetState": "rememberModalBottomSheetState()",
    "BottomSheetScaffoldState": "rememberBottomSheetScaffoldState()",
    "Dp": "16.dp",
    "CarouselState": "rememberCarouselState { 1 }",
    "DatePickerState": "rememberDatePickerState()",
    "DateRangePickerState": "rememberDateRangePickerState()",
    "ColorScheme": "lightColorScheme()",
    "Typography": "Typography()",
    "Shapes": "Shapes()",
    "DrawerState": "rememberDrawerState(DrawerValue.Closed)",
    "TextFieldState": "rememberTextFieldState()",
    "Shape": "RectangleShape",
    "ClosedFloatingPointRange<Float>": "0f..1f",
    "SwipeToDismissBoxState": "rememberSwipeToDismissBoxState()",
    "TextStyle": "MaterialTheme.typography.bodyMedium",
    "KeyboardOptions": "KeyboardOptions.Default",
    "TimePickerState": "rememberTimePickerState()",
    "PopupPositionProvider": "TooltipDefaults.rememberTooltipPositionProvider(TooltipAnchorPosition.Above)",
    "TooltipState": "rememberTooltipState()",
    "WideNavigationRailState": "rememberWideNavigationRailState()",
}
K_KIND = {"string": '"x"', "boolean": "true", "number": "1", "content": "{}", "icon": "Icons.Filled.Add"}
K_HEAD = """// Generated by scripts/ui_proof.py from ui/components/*/*.contract.json (story #217). Do not edit.
// CI compiles this file against Compose Material 3; it is never run. Each function calls one component
// with every prop its contract names under platforms.android.
package com.shipquick.ui.proof

import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.text.input.TextObfuscationMode
import androidx.compose.foundation.text.input.rememberTextFieldState
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material3.*
import androidx.compose.material3.carousel.HorizontalMultiBrowseCarousel
import androidx.compose.material3.carousel.rememberCarouselState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.ui.graphics.RectangleShape
import androidx.compose.ui.unit.dp
"""

IOS = {
    "AppBar": {"t": "NavigationStack { Text(\"x\").toolbar(@TOOLBAR@)@MODS@ }",
               "g": {"TOOLBAR": ["content"], "ITEM": ["placement"], "MODS": ["navigationTitle"]},
               "v": {"content": "{ ToolbarItem(@ITEM@) { Text(\"x\") } }"}},
    "BottomSheet": {"t": "Text(\"x\").sheet(@ARGS@)",
                    "g": {"ARGS": ["isPresented", "onDismiss", "content"], "MODS": ["presentationDetents"]},
                    "v": {"content": "{ Text(\"x\")@MODS@ }"}},
    "Button": {"t": "Button(\"x\") {}"},
    "Card": {"t": "GroupBox(@A@)\nGroupBox(@B@)", "g": {"A": ["titleKey", "content"], "B": ["content", "label"]},
             "p": ["titleKey"]},
    "ColorPicker": {"t": "ColorPicker(\"x\", selection: .constant(Color.accentColor))"},
    "DatePicker": {"t": "DatePicker(@ARGS@)", "g": {"ARGS": ["titleKey", "selection", "in", "displayedComponents"]},
                   "p": ["titleKey"]},
    "Dialog": {"t": "Text(\"x\").alert(@ARGS@)", "g": {"ARGS": ["titleKey", "isPresented", "actions", "message"]},
               "p": ["titleKey"]},
    "DisclosureGroup": {"t": "DisclosureGroup(\"x\") { Text(\"x\") }"},
    "Gauge": {"t": "Gauge(value: 0.5) { Text(\"x\") }"},
    "Image": {"t": "Image(systemName: \"star\")"},
    "Label": {"t": "Label(\"x\", systemImage: \"star\")"},
    "List": {"t": "List(@ARGS@)", "g": {"ARGS": ["data", "id", "selection", "rowContent"]}, "p": ["data"],
             "v": {"rowContent": "{ _ in Text(\"x\") }"}},
    "Menu": {"t": "Menu(@A@)\nMenu(@B@)", "g": {"A": ["titleKey", "content"], "B": ["content", "label"]},
             "p": ["titleKey"]},
    "NavigationBar": {"t": "TabView(@ARGS@)", "g": {"ARGS": ["selection", "content"],
                                                     "TAB": ["titleKey", "systemImage", "value"]},
                      "p": ["titleKey"], "v": {"content": "{ Tab(@TAB@) { Text(\"x\") } }"}, "ios": "18.0"},
    "NavigationDrawer": {"t": "NavigationSplitView(@ARGS@)", "g": {"ARGS": ["sidebar", "detail"], "SEL": ["selection"]},
                         "v": {"sidebar": "{ List(@SEL@) { Text(\"x\") }.listStyle(.sidebar) }"}},
    "NavigationSplitView": {"t": "NavigationSplitView { Text(\"x\") } detail: { Text(\"x\") }"},
    "PageControl": {"t": "TabView { Text(\"x\") }.tabViewStyle(PageTabViewStyle())"},
    "Popover": {"t": "Text(\"x\").popover(isPresented: .constant(false)) { Text(\"x\") }"},
    "ProgressIndicator": {"t": "ProgressView(@ARGS@)", "g": {"ARGS": ["titleKey", "value", "total"]}, "p": ["titleKey"]},
    "ScrollView": {"t": "ScrollView { Text(\"x\") }"},
    "SearchBar": {"t": "NavigationStack { Text(\"x\").searchable(@ARGS@) }", "g": {"ARGS": ["text", "placement", "prompt"]}},
    "SegmentedButton": {"t": "Picker(@ARGS@).pickerStyle(SegmentedPickerStyle())",
                        "g": {"ARGS": ["titleKey", "selection", "content"]}, "p": ["titleKey"],
                        "v": {"content": "{ Text(\"x\").tag(0) }"}},
    "ShareLink": {"t": "ShareLink(item: \"x\")"},
    "Slider": {"t": "Slider(@ARGS@)", "g": {"ARGS": ["value", "in", "step", "onEditingChanged"]},
               "v": {"onEditingChanged": "{ _ in }"}},
    "Stepper": {"t": "Stepper(\"x\", value: .constant(1))"},
    "Switch": {"t": "Toggle(@A@)\nToggle(@B@)", "g": {"A": ["titleKey", "isOn"], "B": ["isOn", "label"]},
               "p": ["titleKey"]},
    "Text": {"t": "Text(\"x\")"},
    "TextField": {"t": "TextField(@ARGS@)", "g": {"ARGS": ["titleKey", "text", "prompt", "axis"]}, "p": ["titleKey"]},
}
S_NAMED = {
    "LocalizedStringKey": '"x"',
    "ToolbarItemPlacement": ".automatic",
    "Binding<Bool>": ".constant(true)",
    "Binding<String>": '.constant("x")',
    "Binding<Date>": ".constant(Date())",
    "Binding<Double>": ".constant(0.5)",
    "Binding<SelectionValue>": ".constant(0)",
    "Binding<SelectionValue?>": ".constant(Optional<Int>.none)",
    "Binding<SelectionValue?>?": ".constant(Optional<Int>.none)",
    "Set<PresentationDetent>": "[.medium]",
    "ClosedRange<Date>": "Date()...Date()",
    "DatePickerComponents": ".date",
    "RandomAccessCollection": "[1, 2, 3]",
    "KeyPath<Data.Element, ID>": "\\.self",
    "String": '"star"',
    "SelectionValue": "0",
    "Double?": "0.5",
    "Double": "1.0",
    "ClosedRange<Double>": "0...1",
    "Text?": 'Text("x")',
    "SearchFieldPlacement": ".automatic",
    "Axis": ".vertical",
}
S_KIND = {"string": '"x"', "boolean": "true", "number": "1", "content": '{ Text("x") }', "icon": 'Image(systemName: "star")'}
S_HEAD = """// Generated by scripts/ui_proof.py from ui/components/*/*.contract.json (story #217). Do not edit.
// CI compiles this file with xcodebuild for iOS; it is never run. Each view calls one component
// with every prop its contract names under platforms.ios.
import SwiftUI
"""
HOLE = re.compile(r"@([A-Z]+)@")


def value(platform, spec, name, prop):
    if name in spec.get("v", {}):
        return spec["v"][name]  # an override: not type-proved against the contract (see the module docstring)
    t = prop["type"]
    kind = t["kind"]
    if kind == "fn":
        n = len(t.get("args", []))
        if platform == "android":
            # a Kotlin `{}` lambda compiles for any arity, so it does not prove the callback's signature
            return "{}" if n <= 1 else "{ " + ", ".join("_" * n) + " -> }"
        return "{}" if n == 0 else "{ " + ", ".join("_" * n) + " in }"
    if kind == "named":
        table = K_NAMED if platform == "android" else S_NAMED
        if t["name"] in table:
            return table[t["name"]]
        raise KeyError(f"no {platform} value for type {t['name']!r} (prop {name})")
    table = K_KIND if platform == "android" else S_KIND
    if kind in table:
        return table[kind]
    raise KeyError(f"no {platform} value for kind {kind!r} (prop {name}); add a value under 'v'")


def render_call(platform, spec, props):
    """The spec's template with each hole filled. Every contract prop must land in a hole."""
    groups = {g: list(names) for g, names in spec.get("g", {}).items()}
    routed = {n for names in groups.values() for n in names}
    extra = [n for n in props if n not in routed]
    unknown = sorted(routed - set(props))
    if unknown:
        raise KeyError(f"spec names prop(s) the contract does not have: {unknown}")
    groups.setdefault("ARGS", []).extend(extra)

    def fill(text):
        def one(m):
            g = m.group(1)
            names = groups.get(g, [])
            if g == "MODS":
                return "".join(f".{n}({fill(value(platform, spec, n, props[n]))})" for n in names)
            parts = []
            for n in names:
                v = fill(value(platform, spec, n, props[n]))
                if platform == "android":
                    parts.append(f"{n} = {v}")
                else:
                    parts.append(v if n in spec.get("p", []) else f"{n}: {v}")
            return ", ".join(parts)
        return HOLE.sub(one, text)

    if props and "@" not in spec["t"]:
        raise KeyError("contract has platform props but the spec has no hole for them")
    out = fill(spec["t"])
    used = {n for g in HOLE.findall(spec["t"] + "".join(spec.get("v", {}).values())) for n in groups.get(g, [])}
    missed = sorted(set(props) - used)
    if missed:
        raise KeyError(f"prop(s) placed in no hole: {missed}")
    return out


def experimental():
    """name -> opt-in classes, from every non-deprecated method and class line of Google's current.txt extract."""
    out = {}
    for line in EXTRACT.read_text(encoding="utf-8").splitlines():
        if line.startswith("//") or "@Deprecated" in line:
            continue
        m = re.search(r"(\w+)\($", line) or re.search(r"\b(?:class|interface) ([\w.]+)", line)
        if not m:
            continue
        found = {c for c in OPTINS if f"material3.{c}" in line}
        if found:
            out.setdefault(m.group(1).split(".")[-1], set()).update(found)
    return out


def components(root):
    """(folder name, doc, contract) for each component folder, sorted."""
    for d in sorted(p for p in root.iterdir() if p.is_dir()):
        doc, contract = d / f"{d.name}.doc.mjs", d / f"{d.name}.contract.json"
        if doc.exists() and contract.exists():
            yield d.name, read_doc(doc), json.loads(contract.read_text(encoding="utf-8"))


def render(root):
    """(files, problems): the text of both proof files, and every component that could not be proved."""
    bodies, bad = {"android": [], "ios": []}, []
    exp = experimental()
    for name, doc, contract in components(root):
        for platform, specs in (("android", ANDROID), ("ios", IOS)):
            api = (doc.get("platforms") or {}).get(platform)
            props = contract.get("platforms", {}).get(platform, {})
            if not api and not props:
                continue
            spec = specs.get(name)
            if spec is None:
                bad.append(f"{platform} {name}: no spec in scripts/ui_proof.py (doc names {api})")
                continue
            try:
                call = render_call(platform, spec, props)
            except KeyError as e:
                bad.append(f"{platform} {name}: {e.args[0]}")
                continue
            short = re.split(r"[.(]", api.split("(")[0])[-1] if api else None
            if short and short not in call:
                bad.append(f"{platform} {name}: the doc names {api}, but the proof never calls {short}")
            body = "\n".join("    " + l for l in call.splitlines())
            if platform == "android":
                need = sorted({c for tok in re.findall(r"\b[A-Za-z_]\w*\b", call) for c in exp.get(tok, ())})
                optin = f"@OptIn({', '.join(c + '::class' for c in need)})\n" if need else ""
                bodies[platform].append(f"{optin}@Composable\nfun Proof{name}() {{\n{body}\n}}\n")
            else:
                avail = f"@available(iOS {spec['ios']}, *)\n" if "ios" in spec else ""
                inner = "\n".join("        " + l for l in call.splitlines())
                bodies[platform].append(f"{avail}struct Proof{name}: View {{\n    var body: some View {{\n"
                                        f"        VStack {{\n{inner}\n        }}\n    }}\n}}\n")
    files = {"android": K_HEAD + "\n" + "\n".join(bodies["android"]), "ios": S_HEAD + "\n" + "\n".join(bodies["ios"])}
    return files, bad


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--root", type=Path, default=SRC, help="folder with one subfolder per component")
    a = ap.parse_args(argv)
    if a.root.resolve() != SRC and not a.check:
        ap.error("--root works only with --check; the proofs are written from ui/components only")
    files, bad = render(a.root)
    for b in bad:
        print(f"ui proof: {b}")
    if bad:
        print(f"{len(bad)} component(s) cannot be proved; add or fix the spec in scripts/ui_proof.py")
        return 1
    if a.check:
        stale = [str(OUT[p].relative_to(KIT)) for p in OUT
                 if not OUT[p].exists() or OUT[p].read_text(encoding="utf-8") != files[p]]
        for s in stale:
            print(f"ui proof: {s} is missing or stale; run python3 scripts/ui_proof.py")
        print("ui proof OK" if not stale else f"{len(stale)} proof file(s) out of date")
        return 1 if stale else 0
    for p, path in OUT.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(files[p], encoding="utf-8")
        print(f"wrote {path.relative_to(KIT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
