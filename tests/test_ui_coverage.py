"""Story #216: the UI coverage gate. Every counted Android and iOS row has one doc, one contract and one topic,
no doc claims a platform that no row names, each Count line equals its rows, and no served name shadows core."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import check_ui_coverage  # noqa: E402

ANDROID = """Count: {n}

| # | Component (Google's name) | Doc folder | Compose API | Also on the page | Google doc page |
|---|---|---|---|---|---|
| 1 | Buttons | `ui/components/Button/` | `androidx.compose.material3.Button` | Button | https://x |
"""
IOS = """Count: {n}

| # | HIG component | SwiftUI type | iOS since | Doc URL | Same as M3 component | Our doc |
|---|---|---|---|---|---|---|
| 1 | Buttons | `SwiftUI.Button` | 13.0 | https://y | Buttons | - |
| 2 | Steppers | `SwiftUI.Stepper` | 13.0 | https://y | none (iOS-only) | `Stepper` |
"""


def doc(folder, name, android=None, ios=None, contract=True):
    d = folder / "components" / name
    d.mkdir(parents=True)
    plat = {"android": android, "ios": ios, "web": None}
    (d / f"{name}.doc.mjs").write_text("export default " + json.dumps({"name": name, "platforms": plat}) + ";\n")
    if contract:
        (d / f"{name}.contract.json").write_text("{}")


def fixture(tmp_path, android_n=1, ios_n=2, core=("Button",)):
    (tmp_path / "android.md").write_text(ANDROID.format(n=android_n))
    (tmp_path / "ios.md").write_text(IOS.format(n=ios_n))
    doc(tmp_path, "Button", "androidx.compose.material3.Button", "SwiftUI.Button")
    doc(tmp_path, "Stepper", None, "SwiftUI.Stepper")
    topics = tmp_path / "topics"
    topics.mkdir()
    for t in ("android-button", "ios-button", "ios-stepper"):
        (topics / f"{t}.doc.mjs").write_text("")
    (tmp_path / "integration.mjs").write_text("export default { docs: './docs' };\n")
    if core is not None:
        for c in core:
            (tmp_path / "core" / "src" / c).mkdir(parents=True)
            (tmp_path / "core" / "src" / c / f"{c}.doc.mjs").write_text("")
    return tmp_path


REAL_NAMES = ROOT / "docs" / "research" / "sources" / "framework-names.json"   # the default of --framework-names


def pin_line(names=REAL_NAMES):
    import hashlib
    return f"Saved names: `docs/research/sources/framework-names.json` sha256 `{hashlib.sha256(names.read_bytes()).hexdigest()}`"


def run(tmp_path, *extra):
    if not (tmp_path / "rows.json").exists():
        (tmp_path / "rows.json").write_text('{"ios": {}}')
    if not (tmp_path / "frameworks.md").exists():
        (tmp_path / "frameworks.md").write_text("## iOS\n\n| # | Topic | Framework | Official source |\n|---|---|---|---|\n")
    md = (tmp_path / "frameworks.md").read_text()
    if "Saved names:" not in md:   # story #288: the saved names (the default file) are pinned by sha256 in framework-topics.md
        (tmp_path / "frameworks.md").write_text(pin_line() + "\n\n" + md)
    return check_ui_coverage.main([
        "--core-floor", "1", "--row-map", str(tmp_path / "rows.json"), "--frameworks", str(tmp_path / "frameworks.md"),
        "--android-list", str(tmp_path / "android.md"), "--ios-list", str(tmp_path / "ios.md"),
        "--components", str(tmp_path / "components"), "--topics", str(tmp_path / "topics"),
        "--core", str(tmp_path / "core"), "--integration", str(tmp_path / "integration.mjs"), *extra])


def test_s216_a_clean_fixture_passes(tmp_path):
    assert run(fixture(tmp_path)) == 0


def test_s216_a_row_with_no_doc_fails(tmp_path, capsys):
    f = fixture(tmp_path)
    (f / "components" / "Stepper" / "Stepper.doc.mjs").unlink()
    assert run(f) == 1
    assert "Stepper" in capsys.readouterr().out


def test_s216_a_row_whose_doc_has_no_platform_name_fails(tmp_path, capsys):
    f = fixture(tmp_path)
    (f / "components" / "Button" / "Button.doc.mjs").write_text(
        'export default {"name": "Button", "platforms": {"android": "androidx.compose.material3.Button", "ios": null, "web": null}};')
    assert run(f) == 1
    assert "platforms.ios" in capsys.readouterr().out


def test_s216_a_doc_with_a_platform_no_row_names_is_extra(tmp_path, capsys):
    f = fixture(tmp_path)
    doc(f, "Gauge", None, "SwiftUI.Gauge")
    (f / "topics" / "ios-gauge.doc.mjs").write_text("")
    assert run(f) == 1
    assert "extra" in capsys.readouterr().out


def test_s216_a_row_with_no_topic_fails(tmp_path, capsys):
    f = fixture(tmp_path)
    (f / "topics" / "ios-stepper.doc.mjs").unlink()
    assert run(f) == 1
    assert "ios-stepper" in capsys.readouterr().out


def test_s216_a_count_line_that_does_not_equal_the_rows_fails(tmp_path, capsys):
    assert run(fixture(tmp_path, android_n=30)) == 1
    assert "Count" in capsys.readouterr().out


def test_s216_a_served_name_that_shadows_a_core_doc_fails(tmp_path, capsys):
    f = fixture(tmp_path, core=("Button", "Stepper"))
    (f / "topics" / "stepper.doc.mjs").write_text("")
    assert run(f) == 1
    assert "shadows" in capsys.readouterr().out


def test_s216_web_is_skipped_without_core_and_fails_when_required(tmp_path, capsys):
    f = fixture(tmp_path, core=None)
    assert run(f) == 0
    assert "skip web: run npm ci --ignore-scripts in ui/tool" in capsys.readouterr().out
    assert run(f, "--require-web") == 1


def test_s216_the_real_repo_passes():
    assert check_ui_coverage.main([]) == 0


def test_s216_an_empty_core_fails_with_require_web(tmp_path, capsys):
    f = fixture(tmp_path, core=())
    (f / "core").mkdir()
    assert run(f, "--require-web") == 1
    assert "core docs" in capsys.readouterr().out


def test_s216_a_core_below_the_floor_fails(tmp_path, capsys):
    f = fixture(tmp_path, core=("Button", "Stepper"))
    assert run(f, "--core-floor", "100") == 1
    assert "floor" in capsys.readouterr().out


SHARED_3 = "| 3 | Pull-down buttons | `SwiftUI.Link` | 13.0 | https://y | Buttons | - |\n"


def test_s216_every_row_of_a_shared_doc_counts(tmp_path, capsys):
    f = fixture(tmp_path, ios_n=3)
    (f / "ios.md").write_text((f / "ios.md").read_text() + SHARED_3)
    (f / "rows.json").write_text('{"ios": {"Button": ["Buttons", "Pull-down buttons"]}}')
    assert run(f) == 0
    (f / "ios.md").write_text(IOS.format(n=2))   # row 3 deleted, Count lowered
    assert run(f) == 1
    assert "Pull-down buttons" in capsys.readouterr().out


def test_s216_a_doc_with_many_rows_must_be_in_the_row_map(tmp_path, capsys):
    f = fixture(tmp_path, ios_n=3)
    (f / "ios.md").write_text((f / "ios.md").read_text() + SHARED_3)
    assert run(f) == 1
    assert "row map" in capsys.readouterr().out


def test_s216_row_numbers_run_one_to_n(tmp_path, capsys):
    f = fixture(tmp_path)
    (f / "ios.md").write_text((f / "ios.md").read_text().replace("| 2 | Steppers", "| 3 | Steppers"))
    assert run(f) == 1
    assert "1 to 2" in capsys.readouterr().out


def test_s216_a_missing_list_file_fails_clearly(tmp_path, capsys):
    f = fixture(tmp_path)
    (f / "android.md").unlink()
    assert run(f) == 1
    assert "android.md" in capsys.readouterr().out


def test_s216_components_that_are_not_a_literal_list_fail(tmp_path, capsys):
    f = fixture(tmp_path)
    (f / "integration.mjs").write_text("const names = ['Stepper'];\nexport default { docs: './docs', components: names };\n")
    assert run(f) == 1
    assert "literal list" in capsys.readouterr().out


# Story #231: the generated API lists. Each component, variant or modifier row maps to a doc (by its
# `platforms` name, or a variant in `platformApi`); each supporting row is listed in a doc's `platformApi`.
ANDROID_API = """Count: 3

| # | Entry | Kind | What | Family | Package | Experimental |
|---|---|---|---|---|---|---|
| 1 | `Button` | component | composable | Button | `androidx.compose.material3` | - |
| 2 | `FilledTonalButton` | variant | composable | Button | `androidx.compose.material3` | - |
| 3 | `ButtonDefaults` | supporting | defaults | Button | `androidx.compose.material3` | - |
"""
IOS_API = """Count: 2

| # | Entry | Kind | What | Family | iOS since | Category | Status | Detail | Apple page | Doc family |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `Button` | component | view type | Button | 13.0 | - | - | - | https://y | Button |
| 2 | `buttonStyle` | modifier | view modifier | Style modifiers | 13.0 | - | - | - | https://y | Button |
"""


def api_fixture(tmp_path):
    f = fixture(tmp_path)
    (f / "android-api.md").write_text(ANDROID_API)
    (f / "ios-api.md").write_text(IOS_API)
    return f


def run_api(f, *extra):
    return run(f, "--android-api", str(f / "android-api.md"), "--ios-api", str(f / "ios-api.md"), *extra)


def with_api(f, api):
    p = f / "components" / "Button" / "Button.doc.mjs"
    d = json.loads(p.read_text()[len("export default "):-2])
    p.write_text("export default " + json.dumps({**d, "platformApi": api}) + ";\n")


def test_s231_uncovered_api_rows_are_listed_and_pass_without_strict(tmp_path, capsys):
    f = api_fixture(tmp_path)
    assert run_api(f) == 0
    out = capsys.readouterr().out
    assert "FilledTonalButton" in out and "ButtonDefaults" in out and "buttonStyle" in out
    assert "Button (component)" not in out


def test_s231_strict_api_fails_on_an_uncovered_row(tmp_path, capsys):
    assert run_api(api_fixture(tmp_path), "--strict-api") == 1
    assert "FAIL api android Button" in capsys.readouterr().out


def v(name):
    return {"name": name, "note": "how it differs"}


FULL_API = {"android": {"variants": [v("FilledTonalButton")], "supporting": [{"name": "ButtonDefaults", "use": "defaults"}]},
            "ios": {"variants": [v("buttonStyle")]}}


def test_s231_variants_and_supporting_in_the_family_doc_cover_their_rows(tmp_path):
    f = api_fixture(tmp_path)
    with_api(f, FULL_API)
    assert run_api(f, "--strict-api") == 0


def test_s231_a_supporting_row_named_as_a_variant_is_not_covered(tmp_path, capsys):
    f = api_fixture(tmp_path)
    with_api(f, {"android": {"variants": [v("FilledTonalButton"), v("ButtonDefaults")]}, "ios": {"variants": [v("buttonStyle")]}})
    assert run_api(f, "--strict-api") == 1
    assert "ButtonDefaults" in capsys.readouterr().out


def test_s231_a_prose_mention_does_not_cover_a_row(tmp_path, capsys):
    f = api_fixture(tmp_path)
    with_api(f, {**FULL_API, "android": {"supporting": FULL_API["android"]["supporting"]}})
    p = f / "components" / "Button" / "Button.doc.mjs"
    d = json.loads(p.read_text()[len("export default "):-2])
    d["usage"] = {"description": "Use FilledTonalButton for a second action."}
    p.write_text("export default " + json.dumps(d) + ";\n")
    assert run_api(f, "--strict-api") == 1
    assert "FilledTonalButton (variant)" in capsys.readouterr().out


def test_s231_a_plain_string_item_does_not_cover_and_fails(tmp_path, capsys):
    f = api_fixture(tmp_path)
    with_api(f, {**FULL_API, "android": {**FULL_API["android"], "variants": ["FilledTonalButton"]}})
    assert run_api(f) == 1
    assert "must be an object" in capsys.readouterr().out


def test_s231_a_row_owned_by_two_docs_fails(tmp_path, capsys):
    f = api_fixture(tmp_path)
    with_api(f, FULL_API)
    p = f / "components" / "Stepper" / "Stepper.doc.mjs"
    d = json.loads(p.read_text()[len("export default "):-2])
    p.write_text("export default " + json.dumps({**d, "platformApi": {"android": {"variants": [v("FilledTonalButton")]}}}) + ";\n")
    assert run_api(f) == 1
    out = capsys.readouterr().out
    assert "FilledTonalButton" in out and "Button" in out and "Stepper" in out and "one owner" in out


DEPRECATED_ROW = ("| 4 | `TabRow` | variant | composable | TabRow | `androidx.compose.material3` | - | deprecated |"
                  " replacement: `SecondaryTabRow`; `@Deprecated` on every overload: current.txt line 2567 |\n")


def test_s231_a_deprecated_row_is_covered_only_by_an_item_with_the_same_status_and_a_replacement(tmp_path, capsys):
    f = api_fixture(tmp_path)
    (f / "android-api.md").write_text(ANDROID_API.replace("Count: 3", "Count: 4") + DEPRECATED_ROW)
    with_api(f, {**FULL_API, "android": {**FULL_API["android"], "variants": [v("FilledTonalButton"), v("TabRow")]}})
    assert run_api(f, "--strict-api") == 1
    assert "TabRow (variant, needs status deprecated)" in capsys.readouterr().out
    item = {"name": "TabRow", "note": "old", "status": "deprecated", "replacement": "SecondaryTabRow"}
    with_api(f, {**FULL_API, "android": {**FULL_API["android"], "variants": [v("FilledTonalButton"), item]}})
    assert run_api(f, "--strict-api") == 0


def test_s231_a_name_under_platform_api_that_is_not_in_the_list_fails(tmp_path, capsys):
    f = api_fixture(tmp_path)
    with_api(f, {**FULL_API, "android": {**FULL_API["android"], "variants": [v("FilledTonalButton"), v("FiledTonalButton")]}})
    assert run_api(f) == 1
    assert "FiledTonalButton" in capsys.readouterr().out


FAMILY_ROW = "| 4 | `Tooltip` | family | family | Tooltip | `androidx.compose.material3` | - | - | - |\n"


def test_s231_a_family_row_is_covered_by_platform_api_family(tmp_path, capsys):
    f = api_fixture(tmp_path)
    (f / "android-api.md").write_text(ANDROID_API.replace("Count: 3", "Count: 4") + FAMILY_ROW)
    with_api(f, FULL_API)
    assert run_api(f, "--strict-api") == 1
    assert "Tooltip (family)" in capsys.readouterr().out
    with_api(f, {**FULL_API, "android": {**FULL_API["android"], "family": "Tooltip"}})
    assert run_api(f, "--strict-api") == 0


def test_s231_the_gate_has_no_exclusion_list():
    import inspect
    src = inspect.getsource(check_ui_coverage)
    assert "Left out" not in src and "exclu" not in src.lower()


# Story #231 (framework topics, reviewer's rule for both lanes): each row of framework-topics.md is one doc, served as
# <platform>-<topic>, with platformApi items in the name plus use shape, counted like a component row.
FRAMEWORKS = """## iOS

| # | Topic | Framework | Official source |
|---|---|---|---|
| 1 | Swift Charts | Charts | https://developer.apple.com/documentation/charts |

## Android

| # | Topic | Framework | Official source |
|---|---|---|---|
"""


def framework_doc(f, slug="swift-charts", items=({"name": "Chart", "use": "Apple: a chart view."},), topic="export default {};\n",
                  variants=()):
    d = f / "components" / slug
    d.mkdir(parents=True)
    ios = {"supporting": list(items), **({"variants": list(variants)} if variants else {})}
    doc = {"name": slug, "platforms": {"android": None, "ios": None, "web": None},
           "platformUsage": {"ios": {"description": "Use Swift Charts."}}, "platformApi": {"ios": ios}}
    (d / f"{slug}.doc.mjs").write_text("export default " + json.dumps(doc) + ";\n")
    (d / f"{slug}.contract.json").write_text("{}")
    if topic is not None:
        (f / "topics" / f"ios-{slug}.doc.mjs").write_text(topic)


def test_s231_a_framework_topic_with_no_doc_is_a_gap_and_fails_strict(tmp_path, capsys):
    f = api_fixture(tmp_path)
    with_api(f, FULL_API)
    (f / "frameworks.md").write_text(FRAMEWORKS)
    assert run_api(f, "--strict-api") == 1
    assert "FAIL api ios framework topics: Swift Charts (framework)" in capsys.readouterr().out


def test_s231_a_framework_doc_and_its_topic_cover_the_row_and_its_items_need_no_api_row(tmp_path, capsys):
    f = api_fixture(tmp_path)
    with_api(f, FULL_API)
    (f / "frameworks.md").write_text(FRAMEWORKS)
    framework_doc(f)
    assert run_api(f, "--strict-api") == 0, capsys.readouterr().out


def test_s231_a_framework_doc_with_no_topic_file_is_still_a_gap(tmp_path, capsys):
    f = api_fixture(tmp_path)
    with_api(f, FULL_API)
    (f / "frameworks.md").write_text(FRAMEWORKS)
    framework_doc(f, topic=None)
    assert run_api(f, "--strict-api") == 1
    assert "Swift Charts (framework)" in capsys.readouterr().out


def test_s231_a_framework_doc_names_its_own_types_but_another_doc_naming_the_same_type_fails(tmp_path, capsys):
    """Review 2 of the iOS stack: a true red. The exemption is for the framework doc only, so in one run the
    framework doc's `Chart` passes and Button's `Chart` fails, and the error names Button, never swift-charts."""
    f = api_fixture(tmp_path)
    with_api(f, {**FULL_API, "ios": {**FULL_API["ios"], "supporting": [{"name": "Chart", "use": "x"}]}})
    (f / "frameworks.md").write_text(FRAMEWORKS)
    framework_doc(f)
    assert run_api(f) == 1
    errs = [l for l in capsys.readouterr().out.splitlines() if "names Chart" in l]
    assert errs == ["FAIL api ios: Button names Chart under platformApi.ios.supporting, but the ios API list has no such supporting row"], errs


def test_s231_a_framework_doc_still_gets_the_kind_check_for_a_name_that_is_a_row(tmp_path, capsys):
    """Review 2 probe: a real API row named in the wrong slot of a framework doc is not skipped."""
    f = api_fixture(tmp_path)
    with_api(f, {"android": FULL_API["android"], "ios": {}})
    (f / "frameworks.md").write_text(FRAMEWORKS)
    framework_doc(f, items=({"name": "Chart", "use": "x"}, {"name": "buttonStyle", "use": "x"}))
    assert run_api(f, "--strict-api") == 1
    assert "swift-charts names buttonStyle under platformApi.ios.supporting, but the ios API list has no such supporting row" \
        in capsys.readouterr().out


def test_s231_an_empty_framework_topic_file_does_not_count(tmp_path, capsys):
    f = api_fixture(tmp_path)
    with_api(f, FULL_API)
    (f / "frameworks.md").write_text(FRAMEWORKS)
    framework_doc(f, topic="")
    assert run_api(f, "--strict-api") == 1
    assert "Swift Charts (framework)" in capsys.readouterr().out


def test_s231_the_real_repo_passes_strict_api_and_ci_and_check_local_pass_the_flag():
    """Every Android and iOS row and framework topic has its doc, so the gate runs strict everywhere (story #231 done)."""
    assert check_ui_coverage.main(["--strict-api"]) == 0
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "python3 scripts/check_ui_coverage.py --require-web --strict-api" in ci
    local = (ROOT / "scripts" / "check_local.sh").read_text(encoding="utf-8")
    assert 'python3 "$HERE/check_ui_coverage.py" --strict-api;' in local


def test_s231_strict_api_prints_each_gap_once(tmp_path, capsys):
    """Second review nit: under --strict-api a gap was printed as FAIL twice, once as a gap and once as an error."""
    assert run_api(api_fixture(tmp_path), "--strict-api") == 1
    out = capsys.readouterr().out
    assert out.count("api android Button: FilledTonalButton") == 1, out


# PR #255 review 2: a component row is covered only by a doc of its own family (Android), and a doc whose Android
# name is a component row of the generated API list is not an extra, even when the 30-card list does not name it.
ICON_ROW = "| 4 | `Icon` | component | composable | Icon | `androidx.compose.material3` | - | - | - |\n"


def icon_fixture(tmp_path):
    f = api_fixture(tmp_path)
    (f / "android-api.md").write_text(ANDROID_API.replace("Count: 3", "Count: 4") + ICON_ROW)
    return f


def test_s231_a_component_row_listed_as_a_variant_of_another_family_is_not_covered(tmp_path, capsys):
    f = icon_fixture(tmp_path)
    with_api(f, {**FULL_API, "android": {**FULL_API["android"], "variants": [v("FilledTonalButton"), v("Icon")]}})
    assert run_api(f) == 0
    assert "Icon (component, needs a doc of family Icon)" in capsys.readouterr().out
    assert run_api(f, "--strict-api") == 1


def test_s231_a_doc_named_by_a_component_row_of_the_api_list_is_not_an_extra(tmp_path, capsys):
    f = icon_fixture(tmp_path)
    with_api(f, FULL_API)
    doc(f, "Icon", "androidx.compose.material3.Icon")
    assert run_api(f, "--strict-api") == 0, capsys.readouterr().out
    doc(f, "Other", "androidx.compose.material3.NotARow")
    assert run_api(f) == 1
    assert "android Other: extra" in capsys.readouterr().out


def test_s231_a_supporting_entry_naming_a_variant_row_fails(tmp_path, capsys):
    f = api_fixture(tmp_path)
    with_api(f, {**FULL_API, "android": {**FULL_API["android"], "supporting": [
        {"name": "ButtonDefaults", "use": "defaults"}, {"name": "FilledTonalButton", "use": "wrong kind"}]}})
    assert run_api(f) == 1
    assert "no such supporting row" in capsys.readouterr().out


# Story #288: a framework doc's own type names are checked against the saved package names, so a typo fails.
def test_s288_a_typo_in_a_framework_doc_name_fails(tmp_path, capsys):
    f = api_fixture(tmp_path)
    with_api(f, FULL_API)
    (f / "frameworks.md").write_text(FRAMEWORKS)
    framework_doc(f, items=({"name": "Chart", "use": "x"}, {"name": "Chrat", "use": "a typo"}))
    assert run_api(f, "--strict-api") == 1
    out = capsys.readouterr().out
    assert "FAIL api ios: swift-charts names Chrat under platformApi.ios.supporting, but neither the ios API list nor " \
        "the saved framework names (framework-names.json) have it" in out, out
    assert "names Chart " not in out


def test_s288_a_name_of_the_other_platform_fails(tmp_path, capsys):
    f = api_fixture(tmp_path)
    with_api(f, FULL_API)
    (f / "frameworks.md").write_text(FRAMEWORKS)
    framework_doc(f, items=({"name": "GlanceModifier", "use": "an Android name in an iOS slot"},))
    assert run_api(f, "--strict-api") == 1
    assert "swift-charts names GlanceModifier" in capsys.readouterr().out


def test_s288_a_qualified_name_matches_on_a_dot_boundary_only(tmp_path, capsys):
    f = api_fixture(tmp_path)
    with_api(f, FULL_API)
    (f / "frameworks.md").write_text(FRAMEWORKS)
    framework_doc(f, items=({"name": "Charts.BarMark", "use": "x"}, {"name": "arMark", "use": "x"}))
    assert run_api(f) == 1
    out = capsys.readouterr().out
    assert "names arMark" in out and "names Charts.BarMark" not in out


def test_s288_saved_names_that_do_not_match_their_pin_fail(tmp_path, capsys):
    f = api_fixture(tmp_path)
    with_api(f, FULL_API)
    (f / "frameworks.md").write_text(FRAMEWORKS)
    framework_doc(f)
    assert run_api(f, "--strict-api") == 0, capsys.readouterr().out
    md = f / "frameworks.md"
    md.write_text(md.read_text().replace(pin_line(), "Saved names: `docs/research/sources/framework-names.json` sha256 `" + "0" * 64 + "`"))
    assert run_api(f) == 1
    assert "framework-names.json: its sha256" in capsys.readouterr().out


def test_s288_a_names_file_edited_after_it_was_pinned_fails(tmp_path, capsys):
    f = api_fixture(tmp_path)
    with_api(f, FULL_API)
    names = f / "edited-names.json"
    names.write_text(REAL_NAMES.read_text().replace("Charts.BarMark", "Charts.Chrat"))
    (f / "frameworks.md").write_text(pin_line() + "\n\n" + FRAMEWORKS)
    framework_doc(f)
    assert run_api(f, "--framework-names", str(names)) == 1
    assert "edited-names.json: its sha256" in capsys.readouterr().out


def test_s288_a_missing_names_file_fails(tmp_path, capsys):
    f = api_fixture(tmp_path)
    run_api(f)
    (f / "frameworks.md").write_text(FRAMEWORKS)
    assert check_ui_coverage.main([
        "--core-floor", "1", "--row-map", str(f / "rows.json"), "--frameworks", str(f / "frameworks.md"),
        "--framework-names", str(f / "no-such-names.json"), "--android-list", str(f / "android.md"),
        "--ios-list", str(f / "ios.md"), "--components", str(f / "components"), "--topics", str(f / "topics"),
        "--core", str(f / "core"), "--integration", str(f / "integration.mjs")]) == 1
    assert "no-such-names.json: file not found" in capsys.readouterr().out


def test_s288_review_2_a_bare_fragment_is_not_a_known_name():
    names = {"android.Manifest.permission", "android.Manifest.permission.POST_NOTIFICATIONS", "android.app.Activity",
             "androidx.glance.appwidget.updateAll"}
    assert not check_ui_coverage.known("permission", names)          # a lowercase last segment must be qualified
    assert check_ui_coverage.known("Manifest.permission.POST_NOTIFICATIONS", names)
    assert check_ui_coverage.known("Activity", names)                 # a type-cased last segment may be bare
    assert not check_ui_coverage.known("ctivity", names)
    assert check_ui_coverage.known("androidx.glance.appwidget.updateAll", names)
    assert not check_ui_coverage.known("updateAll", names)


def test_s288_the_notifications_doc_names_the_platform_types_exactly():
    """Nit from the second review of #287: NotificationChannel is android.app's, POST_NOTIFICATIONS is a Manifest constant."""
    from check_ui_docs import read_doc
    d = read_doc(ROOT / "ui" / "components" / "notifications" / "notifications.doc.mjs")
    names = [i["name"] for i in d["platformApi"]["android"]["supporting"]]
    assert "android.app.NotificationChannel" in names and "Manifest.permission.POST_NOTIFICATIONS" in names, names


# Story #285: iOS has the own-family rule too. A component or modifier row is covered only by a doc of the family the
# list maps it to (column `Doc family`). A doc's families are the Doc family of its platforms.ios row and its
# platformApi.ios.family.
CAPSULE_ROW = "| 3 | `Capsule` | component | view type | Capsule | 13.0 | - | - | - | https://y | Shape |\n"


def ios_doc(f, name, family=None, variants=()):
    d = f / "components" / name
    d.mkdir(parents=True)
    ios = {**({"family": family} if family else {}), **({"variants": [v(n) for n in variants]} if variants else {})}
    doc = {"name": name, "platforms": {"android": None, "ios": None, "web": None}, "platformApi": {"ios": ios}}
    (d / f"{name}.doc.mjs").write_text("export default " + json.dumps(doc) + ";\n")
    (d / f"{name}.contract.json").write_text("{}")


def test_s285_a_swift_charts_doc_that_claims_button_style_fails(tmp_path, capsys):
    f = api_fixture(tmp_path)
    with_api(f, {"android": FULL_API["android"], "ios": {}})
    (f / "frameworks.md").write_text(FRAMEWORKS)
    framework_doc(f, variants=(v("buttonStyle"),))
    assert run_api(f, "--strict-api") == 1
    assert "FAIL api ios Style modifiers: buttonStyle (modifier, needs a doc of family Button)" in capsys.readouterr().out


def test_s285_a_modifier_in_the_doc_its_list_maps_it_to_passes(tmp_path, capsys):
    f = api_fixture(tmp_path)
    with_api(f, FULL_API)
    assert run_api(f, "--strict-api") == 0, capsys.readouterr().out


def test_s285_an_ios_component_needs_a_doc_of_its_mapped_family(tmp_path, capsys):
    f = api_fixture(tmp_path)
    (f / "ios-api.md").write_text(IOS_API.replace("Count: 2", "Count: 3") + CAPSULE_ROW)
    with_api(f, FULL_API)
    ios_doc(f, "Shape", variants=("Capsule",))
    assert run_api(f, "--strict-api") == 1
    assert "Capsule (component, needs a doc of family Shape)" in capsys.readouterr().out
    import shutil
    shutil.rmtree(f / "components" / "Shape")
    ios_doc(f, "Shapes", family="Shape", variants=("Capsule",))
    assert run_api(f, "--strict-api") == 0, capsys.readouterr().out


def test_s285_an_ios_family_that_no_row_maps_to_fails(tmp_path, capsys):
    f = api_fixture(tmp_path)
    with_api(f, {**FULL_API, "ios": {**FULL_API["ios"], "family": "Buton"}})
    assert run_api(f) == 1
    assert "api ios: Button sets platformApi.ios.family Buton, but no row of the ios API list has that Doc family" \
        in capsys.readouterr().out


def test_s285_two_ios_docs_with_one_family_fail(tmp_path, capsys):
    f = api_fixture(tmp_path)
    (f / "ios-api.md").write_text(IOS_API.replace("Count: 2", "Count: 3") + CAPSULE_ROW)
    with_api(f, FULL_API)
    ios_doc(f, "Shape", family="Shape", variants=("Capsule",))
    ios_doc(f, "Shapes", family="Shape")
    assert run_api(f) == 1
    assert "api ios: 2 docs set platformApi.ios.family Shape (Shape, Shapes); a family has one doc" in capsys.readouterr().out


def test_s285_an_ios_list_with_no_doc_family_column_fails(tmp_path, capsys):
    f = api_fixture(tmp_path)
    (f / "ios-api.md").write_text(IOS_API.replace(" Doc family |", "").replace("|---|\n", "\n", 1)
                                  .replace(" | Button |\n", " |\n"))
    with_api(f, FULL_API)
    assert run_api(f) == 1
    assert "ios API list: no Doc family column" in capsys.readouterr().out


def test_s285_adr_012_no_longer_says_ios_has_no_family_rule():
    adr = (ROOT / "docs" / "decisions" / "ADR-012.md").read_text(encoding="utf-8")
    assert "iOS has no own-family rule yet" not in adr
