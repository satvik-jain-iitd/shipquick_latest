"""Story #228: a platform topic never carries the other platform's API names.

`scripts/ui_topics.py` builds `ios-<name>` and `android-<name>` from one shared doc. Text that fits one platform
lives in `platformUsage.<platform>`; props come from `core` or that platform only. The generator fails on a leak."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import ui_topics
from check_ui_docs import read_doc

TOPICS = ROOT / "scripts" / "ui_topics.py"


def write_component(root, name, doc, contract):
    d = root / name
    d.mkdir(parents=True)
    (d / f"{name}.doc.mjs").write_text("export default " + json.dumps(doc) + ";\n", encoding="utf-8")
    (d / f"{name}.contract.json").write_text(json.dumps(contract), encoding="utf-8")


def text_of(t):
    return json.dumps(t, ensure_ascii=False)


def test_s228_no_topic_on_the_real_repo_names_the_other_platforms_api():
    r = subprocess.run(["python3", str(TOPICS), "--check"], capture_output=True, text=True, cwd=ROOT)
    assert "leak" not in r.stdout, r.stdout
    assert r.returncode == 0, r.stdout + r.stderr


def test_s228_a_fixture_with_a_leaked_word_fails_naming_the_topic_and_the_word(tmp_path):
    doc = {"name": "Sheet", "platforms": {"android": "androidx.X", "ios": "SwiftUI.X", "web": None}, "props": [],
           "usage": {"description": "Create it with rememberSheetState."}}
    write_component(tmp_path, "Sheet", doc, {"core": {}, "platforms": {}})
    r = subprocess.run(["python3", str(TOPICS), "--check", "--root", str(tmp_path)], capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 1
    assert "ios-sheet" in r.stdout and "rememberSheetState" in r.stdout, r.stdout


def test_s228_an_ios_word_in_an_android_topic_fails_too():
    doc = {"name": "X", "platforms": {"android": "androidx.X", "ios": None}, "props": [],
           "usage": {"description": "Bind it with @State."}}
    t = ui_topics.topic(doc, {"core": {}}, "android")
    assert any("@State" in m for m in ui_topics.leaks(t, "android"))


def test_s228_every_ios_topic_of_a_shared_doc_lists_props():
    shared = 0
    for folder in sorted(p for p in (ROOT / "ui/components").iterdir() if p.is_dir()):
        doc = read_doc(folder / f"{folder.name}.doc.mjs")
        on = [p for p, v in doc["platforms"].items() if v]
        if "ios" not in on or len(on) < 2:
            continue
        shared += 1
        contract = json.loads((folder / f"{folder.name}.contract.json").read_text(encoding="utf-8"))
        t = ui_topics.topic(doc, contract, "ios")
        props = [s for s in t["sections"] if s["title"] == "Props"]
        assert props and props[0]["content"][0]["rows"], f"ios-{folder.name.lower()} lists no props"
    assert shared >= 15


def test_s228_platform_usage_is_read_for_its_own_platform_only():
    doc = {"name": "X", "platforms": {"android": "androidx.X", "ios": "SwiftUI.X", "web": None}, "props": [],
           "usage": {"description": "Shared words.", "bestPractices": [{"guidance": True, "description": "Shared do."}]},
           "platformUsage": {
               "android": {"description": "Android words.", "bestPractices": [{"guidance": False, "description": "Android dont."}],
                           "accessibility": [{"name": "A11y A", "description": "Android a11y."}]},
               "ios": {"description": "Apple words.", "bestPractices": [{"guidance": True, "description": "Apple do."}],
                       "accessibility": [{"name": "A11y I", "description": "Apple a11y."}]}}}
    ios, android = (text_of(ui_topics.topic(doc, {"core": {}}, p)) for p in ("ios", "android"))
    for words in ("Shared words.", "Shared do."):
        assert words in ios and words in android
    for words in ("Apple words.", "Apple do.", "Apple a11y."):
        assert words in ios and words not in android
    for words in ("Android words.", "Android dont.", "Android a11y."):
        assert words in android and words not in ios


def test_s228_props_come_from_core_or_that_platform_only():
    doc = {"name": "X", "platforms": {"android": "androidx.X", "ios": "SwiftUI.X", "web": None},
           "usage": {"description": "d"},
           "props": [{"name": n, "type": "string", "description": n} for n in ("shared", "aOnly", "iOnly")]}
    contract = {"core": {"shared": {}}, "platforms": {"android": {"aOnly": {}}, "ios": {"iOnly": {}}}}
    def rows(p):
        return [r[0] for s in ui_topics.topic(doc, contract, p)["sections"] if s["title"] == "Props" for r in s["content"][0]["rows"]]

    assert rows("ios") == ["shared", "iOnly"] and rows("android") == ["shared", "aOnly"]


def test_s228_a_prop_tagged_for_ios_replaces_the_untagged_one_in_the_ios_topic_only():
    doc = {"name": "X", "platforms": {"android": "androidx.X", "ios": "SwiftUI.X", "web": None}, "usage": {"description": "d"},
           "props": [{"name": "content", "type": "@Composable () -> Unit", "description": "c"},
                     {"name": "content", "type": "() -> some View", "description": "c", "platform": "ios"}]}
    contract = {"core": {}, "platforms": {"android": {"content": {}}, "ios": {"content": {}}}}

    def types(p):
        return [r[1] for s in ui_topics.topic(doc, contract, p)["sections"] if s["title"] == "Props" for r in s["content"][0]["rows"]]

    assert types("ios") == ["() -> some View"] and types("android") == ["@Composable () -> Unit"]


# PR #230 review: wider leak lists, one injected word each.
IOS_LEAKS = ["LaunchedEffect", "16dp", "12.sp", "onValueChange", "Material3", "ExperimentalMaterial3Api",
             "ModalBottomSheet(", "mutableStateOf", "Kotlin"]
ANDROID_LEAKS = [".toggleStyle(", "@Environment", "@Observable", ".presentationDetents", "Toggle(isOn:", ".alert(",
                 "Swift", "NavigationView", "$isOn"]


def one_word(platform, text):
    other = "android" if platform == "ios" else "ios"
    doc = {"name": "X", "platforms": {platform: "X", other: None}, "props": [], "usage": {"description": text}}
    return ui_topics.leaks(ui_topics.topic(doc, {"core": {}}, platform), platform)


@pytest.mark.parametrize("word", IOS_LEAKS)
def test_s228_an_ios_topic_with_a_compose_word_fails(word):
    assert one_word("ios", f"Call {word} here."), word


@pytest.mark.parametrize("word", ANDROID_LEAKS)
def test_s228_an_android_topic_with_a_swiftui_word_fails(word):
    assert one_word("android", f"Call {word} here."), word


@pytest.mark.parametrize("text", ["It costs $5.", "Pay in US$ or EUR.", "Use 2 columns.", "Wait 300ms."])
def test_s228_money_and_plain_numbers_are_not_leaks(text):
    assert not one_word("android", text) and not one_word("ios", text), text


# Story #231: a topic lists the doc's own variants and supporting API for its platform. A deprecated or
# unavailable item is only ever a "Do not use" line, never a recommendation.
API_DOC = {"name": "Tabs", "platforms": {"android": "androidx.compose.material3.PrimaryTabRow", "ios": None, "web": None}, "props": [],
           "usage": {"description": "Tabs."},
           "platformApi": {"android": {
               "variants": [{"name": "SecondaryTabRow", "note": "A quieter row."},
                            {"name": "TabRow", "note": "The old row.", "status": "deprecated", "replacement": "PrimaryTabRow"}],
               "supporting": [{"name": "TabRowDefaults", "use": "Read the default colors."}]}}}


def test_s231_a_topic_lists_variants_and_supporting_and_says_do_not_use_for_a_deprecated_one():
    t = ui_topics.topic(API_DOC, {"core": {}}, "android")
    text = text_of(t)
    assert "SecondaryTabRow: A quieter row." in text and "TabRowDefaults: Read the default colors." in text
    assert "Do not use: TabRow. Use PrimaryTabRow." in text
    assert "TabRow: The old row." not in text
    dos = [i for s in t["sections"] for b in s["content"] if b.get("style") == "do" for i in b["items"]]
    assert not any("TabRow" in i for i in dos)


def test_s231_a_doc_level_status_turns_the_use_line_into_do_not_use():
    doc = {**API_DOC, "status": "deprecated", "replacement": "PrimaryTabRow", "platformApi": {}}
    text = text_of(ui_topics.topic(doc, {"core": {}}, "android"))
    assert "Do not use: androidx.compose.material3.PrimaryTabRow. Use PrimaryTabRow." in text
    assert "as Google ships it" not in text


# Story #231 (I1): a new iOS doc cannot set platforms.ios (the coverage gate counts only HIG rows there), so it
# speaks to iOS through platformApi.ios or platformUsage.ios. It still gets its ios topic, so agents can read it.
IOS_ONLY_API = {"name": "Picker", "platforms": {"android": None, "ios": None, "web": None}, "props": [],
                "usage": {"description": "Pick one value."},
                "platformApi": {"ios": {"variants": [{"name": "Picker", "note": "Apple: A control for picking a value."}]}}}


def test_s231_a_doc_with_only_platform_api_ios_gets_an_ios_topic_and_no_android_one(tmp_path):
    write_component(tmp_path, "Picker", IOS_ONLY_API, {"core": {}, "platforms": {}})
    files, bad = ui_topics.render(tmp_path)
    assert not bad and list(files) == ["ios-picker.doc.mjs"], list(files)
    text = files["ios-picker.doc.mjs"]
    assert "Picker: Apple: A control for picking a value." in text
    assert "as Apple ships it" in text and "None" not in text and "null" not in text


def test_s231_a_framework_doc_with_only_platform_usage_ios_gets_an_ios_topic(tmp_path):
    doc = {"name": "Widgets", "platforms": {"android": None, "ios": None, "web": None}, "props": [],
           "usage": {"description": "Widgets."}, "platformUsage": {"ios": {"description": "Use WidgetKit."}}}
    write_component(tmp_path, "Widgets", doc, {"core": {}, "platforms": {}})
    files, _ = ui_topics.render(tmp_path)
    assert list(files) == ["ios-widgets.doc.mjs"] and "Use WidgetKit." in files["ios-widgets.doc.mjs"]
