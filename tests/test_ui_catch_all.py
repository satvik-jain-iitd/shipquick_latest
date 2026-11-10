"""Story #296: a catch-all iOS modifier doc (ui/components/<X>Modifiers/) holds only rows no control doc fits.

Story #285 guards a row only once `IOS_DOC_FAMILY` maps it; a row left in a catch-all under its Apple page is not
checked. This test names, per split catch-all, the row-name stems that belong to a control or task doc. A row whose
name holds one of them may not sit in that catch-all. Each later split (one catch-all per PR) adds its own entry."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from check_ui_docs import read_doc  # noqa: E402

COMPONENTS = ROOT / "ui" / "components"
# catch-all doc -> {lowercase stem found inside a row name: the doc that owns such rows}
SPLIT = {
    "InputModifiers": {
        "gesture": "Gestures", "tapgesture": "Gestures", "hittesting": "Gestures", "contentshape": "Gestures",
        "pencil": "Gestures", "manipula": "Gestures", "windowactivationevents": "Gestures",
        "focus": "Focus",
        "keyboardshortcut": "Keyboard", "keypress": "Keyboard", "modifierkey": "Keyboard", "oncommand": "Keyboard",
        "exitcommand": "Keyboard", "movecommand": "Keyboard", "playpausecommand": "Keyboard", "pagecommand": "Keyboard",
        "deletecommand": "Keyboard",
        "drag": "DragAndDrop", "drop": "DragAndDrop", "reorder": "DragAndDrop", "springloading": "DragAndDrop",
        "hover": "Hover", "pointer": "Hover",
        "copyable": "edit-menus", "cuttable": "edit-menus", "copycommand": "edit-menus", "cutcommand": "edit-menus",
        "pastecommand": "edit-menus",
        "appintent": "app-intents-and-app-shortcuts", "appentity": "app-intents-and-app-shortcuts",
        "shortcutslink": "app-intents-and-app-shortcuts", "siritip": "app-intents-and-app-shortcuts",
        "widget": "widgets", "asyncimage": "Image",
    },
    # 2/6: TechnologyModifiers split by Apple framework (each row's module read from its own Apple page, 11 Nov 2026)
    "TechnologyModifiers": {
        "inapppurchase": "InAppPurchase", "entitlement": "InAppPurchase", "storeproduct": "InAppPurchase",
        "storebutton": "InAppPurchase", "subscription": "InAppPurchase", "product": "InAppPurchase", "multiseat": "InAppPurchase",
        "map": "Map", "lookaround": "Map",
        "tip": "Tips",
        "applepay": "Wallet", "wallet": "Wallet", "paylater": "Wallet",
        "imageplayground": "ImagePlayground",
        "webview": "web-view", "gesture": "Gestures", "photospicker": "PresentationModifiers",
    },
}


def ios_variants(doc_name):
    doc = read_doc(COMPONENTS / doc_name / f"{doc_name}.doc.mjs")
    return [v["name"] for v in doc.get("platformApi", {}).get("ios", {}).get("variants", [])]


def test_s296_a_catch_all_row_whose_control_has_its_own_doc_fails():
    bad = []
    for catch_all, stems in SPLIT.items():
        for name in ios_variants(catch_all):
            owners = sorted({doc for stem, doc in stems.items() if stem in name.lower()})
            if owners:
                bad.append(f"{catch_all}: {name} belongs in {'/'.join(owners)}")
    assert bad == [], "\n".join(bad)


def test_s296_each_owner_doc_exists_sets_a_family_and_holds_a_row_of_its_stem():
    for stems in SPLIT.values():
        for stem, doc_name in stems.items():
            path = COMPONENTS / doc_name / f"{doc_name}.doc.mjs"
            assert path.is_file(), f"{doc_name}: no doc folder"
            doc = read_doc(path)
            ios = doc.get("platformApi", {}).get("ios", {})
            assert doc["platforms"].get("ios") or ios.get("family"), f"{doc_name}: the gate needs platforms.ios or platformApi.ios.family"
            assert any(stem in v["name"].lower() for v in ios.get("variants", [])), f"{doc_name}: holds no row with {stem!r}"
