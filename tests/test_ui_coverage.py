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


def run(tmp_path, *extra):
    if not (tmp_path / "rows.json").exists():
        (tmp_path / "rows.json").write_text('{"ios": {}}')
    if not (tmp_path / "frameworks.md").exists():
        (tmp_path / "frameworks.md").write_text("## iOS\n\n| # | Topic | Framework | Official source |\n|---|---|---|---|\n")
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

| # | Entry | Kind | What | Family | iOS since | Apple page |
|---|---|---|---|---|---|---|
| 1 | `Button` | component | view type | Button | 13.0 | https://y |
| 2 | `buttonStyle` | modifier | view modifier | Controls | 13.0 | https://y |
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


def framework_doc(f, slug="swift-charts", items=({"name": "Chart", "use": "Apple: a chart view."},), topic=True):
    d = f / "components" / slug
    d.mkdir(parents=True)
    doc = {"name": slug, "platforms": {"android": None, "ios": None, "web": None},
           "platformUsage": {"ios": {"description": "Use Swift Charts."}}, "platformApi": {"ios": {"supporting": list(items)}}}
    (d / f"{slug}.doc.mjs").write_text("export default " + json.dumps(doc) + ";\n")
    (d / f"{slug}.contract.json").write_text("{}")
    if topic:
        (f / "topics" / f"ios-{slug}.doc.mjs").write_text("")


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
    framework_doc(f, topic=False)
    assert run_api(f, "--strict-api") == 1
    assert "Swift Charts (framework)" in capsys.readouterr().out


def test_s231_a_name_with_no_api_row_still_fails_in_a_doc_that_is_not_a_framework_doc(tmp_path, capsys):
    f = api_fixture(tmp_path)
    with_api(f, {**FULL_API, "ios": {**FULL_API["ios"], "supporting": [{"name": "Chart", "use": "x"}]}})
    assert run_api(f) == 1
    assert "has no such row" in capsys.readouterr().out


def test_s231_strict_api_fails_on_the_real_repo_today():
    """Red first: the family docs have not landed, so the full lists are not covered yet."""
    assert check_ui_coverage.main(["--strict-api"]) == 1
