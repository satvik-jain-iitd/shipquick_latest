"""Story #231: the full UI API lists are generated from Google's current.txt and Apple's documentation JSON,
pinned by a sha256, and --check fails when a list no longer matches its saved source."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import ui_api_lists  # noqa: E402

# Real line shapes from compose/material3/material3/api/current.txt (1.4.0), cut short.
CURRENT = """// Signature format: 4.0
package androidx.compose.material3 {

  @androidx.compose.runtime.Immutable public final class ButtonColors {
  }

  public final class ButtonDefaults {
    method @androidx.compose.runtime.Composable public void Icon(int x);
  }

  public final class ButtonKt {
    method @androidx.compose.runtime.Composable public static void Button(kotlin.jvm.functions.Function0<kotlin.Unit> onClick);
    method @BytecodeOnly @androidx.compose.runtime.Composable public static void Button(kotlin.jvm.functions.Function0<kotlin.Unit!>, int);
    method @androidx.compose.runtime.Composable public static void FilledTonalButton(kotlin.jvm.functions.Function0<kotlin.Unit> onClick);
    method @Deprecated @androidx.compose.runtime.Composable public static void OldButton(int x);
  }

  public final class ModalBottomSheetKt {
    method @SuppressCompatibility @androidx.compose.material3.ExperimentalMaterial3Api @androidx.compose.runtime.Composable public static void ModalBottomSheet(int x);
    method @androidx.compose.runtime.Composable public static androidx.compose.material3.SheetState rememberModalBottomSheetState(optional boolean skipPartiallyExpanded);
  }

  public final class ModalBottomSheetState {
  }

}
"""

VIEW_PAGE = {
    "metadata": {"title": "View"},
    "relationshipsSections": [
        {"type": "inheritedBy", "identifiers": ["doc://s/Shape"]},
        {"type": "conformingTypes", "identifiers": ["doc://s/Button", "doc://s/ButtonStyleConfiguration/Label", "doc://s/HSplitView"]},
    ],
    "references": {
        "doc://s/Shape": {"title": "Shape", "url": "/documentation/swiftui/shape"},
        "doc://s/Button": {"title": "Button", "url": "/documentation/swiftui/button"},
        "doc://s/ButtonStyleConfiguration/Label": {"title": "ButtonStyleConfiguration.Label", "url": "/documentation/swiftui/buttonstyleconfiguration/label-swift.struct"},
        "doc://s/HSplitView": {"title": "HSplitView", "url": "/documentation/swiftui/hsplitview"},
    },
}
MODAL_PAGE = {
    "metadata": {"title": "Modal presentations"},
    "topicSections": [{"title": "Showing a sheet", "identifiers": ["doc://s/sheet1", "doc://s/sheet2", "doc://s/DialogSeverity"]}],
    "references": {
        "doc://s/sheet1": {"title": "sheet(isPresented:onDismiss:content:)", "url": "/documentation/swiftui/view/sheet(ispresented:ondismiss:content:)"},
        "doc://s/sheet2": {"title": "sheet(item:onDismiss:content:)", "url": "/documentation/swiftui/view/sheet(item:ondismiss:content:)"},
        "doc://s/DialogSeverity": {"title": "DialogSeverity", "url": "/documentation/swiftui/dialogseverity"},
    },
}
IOS = [{"name": "iOS", "introducedAt": "13.0"}]
EXTRACT = {
    "source": "https://developer.apple.com/tutorials/data/documentation/swiftui/view.json",
    "fetched": "2026-11-09",
    "types": [
        {"name": "Button", "url": "/documentation/swiftui/button", "platforms": IOS},
        {"name": "ButtonStyleConfiguration.Label", "url": "/x", "platforms": IOS},
        {"name": "HSplitView", "url": "/documentation/swiftui/hsplitview", "platforms": [{"name": "macOS"}]},
        {"name": "NavigationView", "url": "/n", "platforms": [{"name": "iOS", "introducedAt": "13.0", "deprecatedAt": "27.3", "message": "use NavigationStack instead"}]},
    ],
    "modifiers": [
        {"title": "sheet(isPresented:onDismiss:content:)", "url": "/documentation/swiftui/view/sheet", "page": "Modal presentations", "platforms": [{"name": "iOS", "introducedAt": "14.0"}]},
        {"title": "sheet(item:onDismiss:content:)", "url": "/documentation/swiftui/view/sheet2", "page": "Modal presentations", "platforms": IOS},
    ],
}


def by_name(rows):
    return {r["name"]: r for r in rows}


def test_s231_a_composable_fun_in_its_own_file_is_a_component():
    rows = by_name(ui_api_lists.parse_android(CURRENT)[0])
    assert rows["Button"]["kind"] == "component" and rows["Button"]["family"] == "Button"
    assert rows["FilledTonalButton"]["kind"] == "variant" and rows["FilledTonalButton"]["family"] == "Button"


def test_s231_bytecode_twins_and_defaults_slot_helpers_are_not_rows():
    names = [r["name"] for r in ui_api_lists.parse_android(CURRENT)[0]]
    assert names.count("Button") == 1 and "Icon" not in names


def test_s231_remember_x_is_supporting_in_its_family():
    r = by_name(ui_api_lists.parse_android(CURRENT)[0])["rememberModalBottomSheetState"]
    assert (r["kind"], r["what"], r["family"]) == ("supporting", "remember", "ModalBottomSheet")


def test_s231_a_defaults_object_colors_and_state_are_supporting():
    rows = by_name(ui_api_lists.parse_android(CURRENT)[0])
    assert (rows["ButtonDefaults"]["kind"], rows["ButtonDefaults"]["what"], rows["ButtonDefaults"]["family"]) == ("supporting", "defaults", "Button")
    assert rows["ButtonColors"]["what"] == "colors"
    assert (rows["ModalBottomSheetState"]["what"], rows["ModalBottomSheetState"]["family"]) == ("state holder", "ModalBottomSheet")


def test_s231_an_experimental_annotation_is_kept_and_marked():
    rows = by_name(ui_api_lists.parse_android(CURRENT)[0])
    assert rows["ModalBottomSheet"]["experimental"] is True and rows["Button"]["experimental"] is False


def test_s231_a_deprecated_composable_is_left_out_with_its_reason():
    entries, left = ui_api_lists.parse_android(CURRENT)
    assert "OldButton" not in by_name(entries)
    assert "Deprecated" in by_name(left)["OldButton"]["reason"]


def test_s231_the_extract_parses_the_same_as_the_full_file():
    assert ui_api_lists.parse_android(ui_api_lists.android_extract(CURRENT)) == ui_api_lists.parse_android(CURRENT)


def test_s231_apple_json_gives_view_conformers_and_view_modifiers_only():
    assert [t for t, _ in ui_api_lists.view_conformers(VIEW_PAGE)] == ["Button", "ButtonStyleConfiguration.Label", "HSplitView"]
    assert [t for t, _ in ui_api_lists.page_modifiers(MODAL_PAGE)] == ["sheet(isPresented:onDismiss:content:)", "sheet(item:onDismiss:content:)"]


def test_s231_ios_keeps_only_ios_and_names_apples_reason_for_the_rest():
    entries, left = ui_api_lists.parse_ios(EXTRACT)
    rows, out = by_name(entries), by_name(left)
    assert rows["Button"]["kind"] == "component"
    assert (rows["ButtonStyleConfiguration.Label"]["kind"], rows["ButtonStyleConfiguration.Label"]["family"]) == ("supporting", "Button")
    assert rows["sheet"]["kind"] == "modifier" and rows["sheet"]["since"] == "13.0"
    assert "no iOS" in out["HSplitView"]["reason"] and "macOS" in out["HSplitView"]["reason"]
    assert "use NavigationStack instead" in out["NavigationView"]["reason"]


def write_sources(tmp_path):
    src, out = tmp_path / "sources", tmp_path / "out"
    src.mkdir()
    out.mkdir()
    (src / ui_api_lists.ANDROID_SRC.name).write_text(ui_api_lists.android_extract(CURRENT))
    (src / ui_api_lists.IOS_SRC.name).write_text(json.dumps(EXTRACT))
    return ["--sources", str(src), "--out", str(out)], src, out


def test_s231_written_lists_pass_check_with_count_and_pinned_sha(tmp_path):
    args, src, out = write_sources(tmp_path)
    assert ui_api_lists.main(args) == 0
    assert ui_api_lists.main(args + ["--check"]) == 0
    md = (out / ui_api_lists.ANDROID_MD.name).read_text()
    assert "Count: 7" in md and ui_api_lists.sha((src / ui_api_lists.ANDROID_SRC.name).read_text()) in md


def test_s231_check_fails_when_the_saved_source_changed(tmp_path, capsys):
    args, src, out = write_sources(tmp_path)
    ui_api_lists.main(args)
    f = src / ui_api_lists.ANDROID_SRC.name
    f.write_text(f.read_text().replace("FilledTonalButton", "ElevatedButton"))
    assert ui_api_lists.main(args + ["--check"]) == 1
    assert "android-m3-api.md" in capsys.readouterr().out


def test_s231_check_fails_when_a_list_was_edited_by_hand(tmp_path, capsys):
    args, src, out = write_sources(tmp_path)
    ui_api_lists.main(args)
    md = out / ui_api_lists.IOS_MD.name
    md.write_text(md.read_text().replace("| sheet |", "| sheets |").replace("`sheet`", "`sheets`"))
    assert ui_api_lists.main(args + ["--check"]) == 1
    assert "stale" in capsys.readouterr().out


def test_s231_the_doc_schema_takes_platform_api_and_refuses_unknown_keys():
    import check_ui_docs
    schema = json.loads((ROOT / "ui" / "schema" / "component.schema.json").read_text())
    base = {"name": "B", "displayName": "B", "platforms": {"android": None, "ios": None, "web": None}, "usage": {"description": "d"}, "props": []}
    good = {**base, "platformApi": {"android": {"variants": ["FilledTonalButton"], "supporting": ["ButtonDefaults"]}}}
    assert check_ui_docs.validate(good, schema, schema) == []
    assert check_ui_docs.validate({**base, "platformApi": {"android": {"variant": []}}}, schema, schema) != []


def test_s231_the_real_lists_match_their_saved_sources():
    assert ui_api_lists.main(["--check"]) == 0
