"""Story #182 (S2): the spec layer. One doc and one contract per component, checked by scripts/check_ui_docs.py."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_ui_docs.py"
UI = ROOT / "ui"
CI = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
META = "Copyright (c) Meta Platforms, Inc. and affiliates."

PROPS = [
    {"name": "label", "type": "string", "description": "The words on the button.", "required": True},
    {"name": "variant", "type": "'primary' | 'secondary'", "description": "How loud the button looks.", "default": "'secondary'"},
    {"name": "onClick", "type": "() => void", "description": "Runs on a press."},
]
CONTRACT = {
    "name": "Button",
    "baseTarget": "root",
    "types": {},
    "core": {
        "label": {"type": {"kind": "string"}},
        "variant": {"type": {"kind": "enum", "values": ["primary", "secondary"]}, "optional": True},
        "onClick": {"type": {"kind": "fn", "args": []}, "optional": True},
    },
    "platforms": {},
    "webOnly": [],
    "sameMeaning": {"onClick": "a press, as in Compose"},
}


def doc(props=None, **extra):
    body = {"type": "component", "name": "Button", "displayName": "Button",
            "platforms": {"android": "androidx.compose.material3.Button", "ios": "SwiftUI.Button", "web": "@astryxdesign/core/Button"},
            "usage": {"description": "A button starts an action."}, "props": PROPS if props is None else props}
    body.update(extra)
    return "/** @type {import('../../schema/doctypes/component/type').ComponentDoc} */\nexport default " + json.dumps(body, indent=2) + ";\n"


def make(tmp_path, name="Button", doc_text=None, contract=None):
    d = tmp_path / name
    d.mkdir(parents=True)
    if doc_text is not False:
        (d / f"{name}.doc.mjs").write_text(doc_text or doc(), encoding="utf-8")
    if contract is not False:
        (d / f"{name}.contract.json").write_text(json.dumps(contract or CONTRACT), encoding="utf-8")
    return tmp_path


def run(root):
    return subprocess.run(["python3", str(SCRIPT), "--root", str(root)], capture_output=True, text=True)


# ---- Scenario 1: the schema is copied from Meta's repo, with one field added ----
def test_s182_the_component_type_is_copied_with_the_meta_header_and_adds_only_platforms():
    t = (UI / "schema" / "doctypes" / "component" / "type.ts").read_text(encoding="utf-8")
    assert t.startswith("// " + META)
    assert re.search(r"platforms:\s*\{\s*android: string \| null;\s*ios: string \| null;\s*web: string \| null;\s*\}", t)
    assert (UI / "schema" / "doctypes" / "base" / "type.ts").read_text(encoding="utf-8").startswith("// " + META)


def test_s182_the_json_schema_twin_requires_platforms_with_all_three_keys():
    s = json.loads((UI / "schema" / "component.schema.json").read_text(encoding="utf-8"))
    assert "platforms" in s["required"]
    assert set(s["properties"]["platforms"]["required"]) == {"android", "ios", "web"}


def test_s182_upstream_md_names_the_repo_and_a_full_commit_sha_and_the_licence_is_kept():
    up = (UI / "UPSTREAM.md").read_text(encoding="utf-8")
    assert "https://github.com/meta/astryx" in up and re.search(r"\b[0-9a-f]{40}\b", up)
    assert "MIT License" in (UI / "LICENSE.meta-astryx.txt").read_text(encoding="utf-8")


# ---- Scenario 2: the dense-writing guide and the contract format ----
def test_s182_the_dense_guide_is_copied_with_attribution():
    g = (UI / "guides" / "dense-writing.md").read_text(encoding="utf-8")
    assert META in g and "same information, fewer tokens" in g


def test_s182_the_contract_type_is_copied_and_the_json_contract_needs_a_reason_per_web_only_prop():
    assert (UI / "schema" / "contract" / "types.ts").read_text(encoding="utf-8").startswith("// " + META)
    s = json.loads((UI / "schema" / "contract.schema.json").read_text(encoding="utf-8"))
    assert s["properties"]["webOnly"]["items"]["required"] == ["name", "reason"]


def test_s182_a_web_only_prop_without_a_reason_fails(tmp_path):
    c = dict(CONTRACT, webOnly=[{"name": "form"}])
    r = run(make(tmp_path, contract=c))
    assert r.returncode == 1 and "reason" in r.stdout


# ---- Scenario 3: the doc guards ----
def test_s182_a_good_doc_and_contract_pass(tmp_path):
    r = run(make(tmp_path))
    assert r.returncode == 0, r.stdout


def test_s182_a_doc_naming_a_prop_the_contract_lacks_fails(tmp_path):
    r = run(make(tmp_path, doc_text=doc(PROPS + [{"name": "size", "type": "'sm' | 'md'", "description": "How big."}])))
    assert r.returncode == 1 and "size" in r.stdout and "contract" in r.stdout


def test_s182_a_contract_prop_the_doc_does_not_name_fails(tmp_path):
    r = run(make(tmp_path, doc_text=doc(PROPS[:2])))
    assert r.returncode == 1 and "onClick" in r.stdout


def test_s182_an_enum_prop_typed_by_a_bare_name_fails(tmp_path):
    props = [PROPS[0], dict(PROPS[1], type="ButtonVariant"), PROPS[2]]
    r = run(make(tmp_path, doc_text=doc(props)))
    assert r.returncode == 1 and "variant" in r.stdout and "'primary'" in r.stdout


def test_s182_an_enum_prop_with_a_missing_literal_fails(tmp_path):
    props = [PROPS[0], dict(PROPS[1], type="'primary'"), PROPS[2]]
    assert run(make(tmp_path, doc_text=doc(props))).returncode == 1


def test_s182_a_web_only_prop_counts_as_named_by_the_contract(tmp_path):
    c = dict(CONTRACT, webOnly=[{"name": "form", "reason": "HTML form owner"}])
    r = run(make(tmp_path, doc_text=doc(PROPS + [{"name": "form", "type": "string", "description": "Form id."}]), contract=c))
    assert r.returncode == 0, r.stdout


def test_s182_an_empty_or_missing_root_fails_and_names_the_path(tmp_path):
    for root in (tmp_path, tmp_path / "nope"):
        r = run(root)
        assert r.returncode == 1 and str(root) in r.stdout


def test_s182_a_web_only_prop_typed_by_a_bare_name_fails(tmp_path):
    c = dict(CONTRACT, webOnly=[{"name": "type", "reason": "HTML form submission type"}])
    r = run(make(tmp_path, doc_text=doc(PROPS + [{"name": "type", "type": "ButtonType", "description": "HTML type."}]), contract=c))
    assert r.returncode == 1 and "'type'" in r.stdout


def test_s182_a_union_of_literals_with_an_open_string_fails(tmp_path):
    c = dict(CONTRACT, webOnly=[{"name": "rel", "reason": "HTML link relationship"}])
    r = run(make(tmp_path, doc_text=doc(PROPS + [{"name": "rel", "type": "'noopener' | string", "description": "Link rel."}]), contract=c))
    assert r.returncode == 1 and "rel" in r.stdout and "string" in r.stdout


def test_s182_a_duplicate_prop_name_fails(tmp_path):
    r = run(make(tmp_path, doc_text=doc(PROPS + [PROPS[0]])))
    assert r.returncode == 1 and "duplicate" in r.stdout and "label" in r.stdout


def test_s182_junk_after_the_json_in_a_doc_fails(tmp_path):
    r = run(make(tmp_path, doc_text=doc() + "export const extra = 1;\n"))
    assert r.returncode == 1 and "after" in r.stdout


def test_s182_a_dense_twin_after_the_doc_is_allowed(tmp_path):
    r = run(make(tmp_path, doc_text=doc() + 'export const docsDense = {"description": "btn; starts action"};\n'))
    assert r.returncode == 0, r.stdout


def test_s182_a_component_with_no_doc_fails(tmp_path):
    r = run(make(tmp_path, doc_text=False))
    assert r.returncode == 1 and "Button.doc.mjs" in r.stdout


def test_s182_a_component_with_no_contract_fails(tmp_path):
    r = run(make(tmp_path, contract=False))
    assert r.returncode == 1 and "Button.contract.json" in r.stdout


def test_s182_a_doc_without_platforms_fails_the_schema(tmp_path):
    text = doc().replace('"platforms"', '"platformz"')
    r = run(make(tmp_path, doc_text=text))
    assert r.returncode == 1 and "platforms" in r.stdout


def test_s182_the_shipped_button_example_passes():
    r = subprocess.run(["python3", str(SCRIPT)], capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stdout
    assert (UI / "components" / "Button" / "Button.doc.mjs").exists()


def test_s182_the_guard_runs_locally_and_in_ci():
    assert "check_ui_docs.py" in (ROOT / "scripts" / "check_local.sh").read_text(encoding="utf-8")
    assert "\n  ui-docs:\n" in CI and "check_ui_docs.py" in CI
    needs = re.search(r"needs: \[([^\]]*)\]", CI.split("\n  gate:\n", 1)[1]).group(1)
    assert "ui-docs" in needs


# ---- Scenario 4: tokens carry the feel ----
def test_s182_tokens_json_has_the_feel_group():
    t = json.loads((ROOT / "design" / "tokens.json").read_text(encoding="utf-8"))
    feel = t["feel"]
    assert {"motion", "haptics", "touchTarget"} <= set(feel)
    assert feel["touchTarget"]["android"]["$value"] == "48dp" and feel["touchTarget"]["ios"]["$value"] == "44pt"
    assert feel["motion"]["duration"] and feel["motion"]["easing"]
    for group in ("color", "typography", "spacing", "shape"):
        assert group in t, group


# ---- Story #228: one prop name, a Compose type and a SwiftUI type ----
TWO = {**CONTRACT, "core": {}, "platforms": {"android": {"content": {"type": {"kind": "content"}}},
                                             "ios": {"content": {"type": {"kind": "content"}, "optional": True}}}}
COMPOSE = {"name": "content", "type": "@Composable () -> Unit", "description": "Inside."}


def test_s228_the_same_prop_name_tagged_for_two_platforms_passes(tmp_path):
    props = [COMPOSE, {"name": "content", "type": "() -> some View", "description": "Inside.", "platform": "ios"}]
    r = run(make(tmp_path, doc_text=doc(props), contract=TWO))
    assert r.returncode == 0, r.stdout


def test_s228_a_prop_tagged_for_a_platform_the_contract_lacks_it_on_fails(tmp_path):
    props = [COMPOSE, {"name": "content", "type": "() -> some View", "description": "Inside.", "platform": "web"}]
    r = run(make(tmp_path, doc_text=doc(props), contract=TWO))
    assert r.returncode == 1 and "platforms.web" in r.stdout, r.stdout


def test_s228_a_platform_prop_documented_only_for_another_platform_fails(tmp_path):
    props = [{"name": "content", "type": "() -> some View", "description": "Inside.", "platform": "ios"}]
    r = run(make(tmp_path, doc_text=doc(props), contract=TWO))
    assert r.returncode == 1 and "platforms.android" in r.stdout, r.stdout


def test_s228_a_core_prop_documented_only_for_ios_fails(tmp_path):
    # PR #230 review: it would vanish from the android and web topics.
    props = [{**p, "platform": "ios"} if p["name"] == "label" else p for p in PROPS]
    r = run(make(tmp_path, doc_text=doc(props)))
    assert r.returncode == 1 and "label" in r.stdout and "android" in r.stdout, r.stdout


def test_s228_a_core_prop_tagged_once_per_platform_passes(tmp_path):
    props = [p for p in PROPS if p["name"] != "label"] + [
        {"name": "label", "type": "string", "description": "The words.", "platform": pl} for pl in ("android", "ios", "web")]
    r = run(make(tmp_path, doc_text=doc(props)))
    assert r.returncode == 0, r.stdout


def test_s228_the_same_name_twice_for_one_platform_is_a_duplicate(tmp_path):
    tagged = {"name": "content", "type": "() -> some View", "description": "Inside.", "platform": "ios"}
    r = run(make(tmp_path, doc_text=doc([COMPOSE, tagged, tagged]), contract=TWO))
    assert r.returncode == 1 and "duplicate" in r.stdout and "(ios)" in r.stdout, r.stdout


# ---- Story #215: a prop both platforms share, same name and same spec, sits in core ----
SHARED = {**CONTRACT, "core": {}, "platforms": {"android": {"content": {"type": {"kind": "content"}}},
                                                "ios": {"content": {"type": {"kind": "content"}}}}}


def test_s215_a_prop_with_the_same_spec_on_android_and_ios_and_an_empty_core_fails(tmp_path):
    props = [COMPOSE, {"name": "content", "type": "() -> some View", "description": "Inside.", "platform": "ios"}]
    r = run(make(tmp_path, doc_text=doc(props), contract=SHARED))
    assert r.returncode == 1 and "'content'" in r.stdout and "core" in r.stdout, r.stdout


def test_s215_the_shared_prop_moved_into_core_passes(tmp_path):
    props = [COMPOSE, {"name": "content", "type": "() -> some View", "description": "Inside.", "platform": "ios"}]
    moved = {**CONTRACT, "core": {"content": {"type": {"kind": "content"}}}, "platforms": {}}
    r = run(make(tmp_path, doc_text=doc(props), contract=moved))
    assert r.returncode == 0, r.stdout


def test_s215_the_same_name_with_a_different_spec_per_platform_stays_put(tmp_path):
    # A number on Compose and a Binding<Double> on SwiftUI cannot share one core type.
    c = {**CONTRACT, "core": {}, "platforms": {"android": {"value": {"type": {"kind": "number"}}},
                                               "ios": {"value": {"type": {"kind": "named", "name": "Binding<Double>"}}}}}
    props = [{"name": "value", "type": "number", "description": "Where.", "platform": "android"},
             {"name": "value", "type": "Binding<Double>", "description": "Where.", "platform": "ios"}]
    r = run(make(tmp_path, doc_text=doc(props), contract=c))
    assert r.returncode == 0, r.stdout


def test_s215_no_kit_contract_repeats_a_shared_prop_under_both_platforms():
    for f in sorted((UI / "components").glob("*/*.contract.json")):
        plats = json.loads(f.read_text(encoding="utf-8"))["platforms"]
        a, i = plats.get("android", {}), plats.get("ios", {})
        assert not [n for n in a if n in i and a[n] == i[n]], f.name
