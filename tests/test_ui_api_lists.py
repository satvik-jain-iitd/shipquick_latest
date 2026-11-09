"""Story #231: the full UI API lists are generated from Google's current.txt and Apple's documentation JSON,
pinned by a sha256, and --check fails when a list no longer matches its saved source."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import ui_api_lists  # noqa: E402

DEPRECATION = '// shipquick: deprecation: OldButton {"message": "Renamed to Button", "replaceWith": "Button(onClick)", "source": "https://x/Button.kt"}\n'
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

  public enum SheetValue {
  }

  public final class SheetState {
  }

  public final class TooltipKt {
    method @androidx.compose.runtime.Composable public static void PlainTooltip(int x);
  }

}

package androidx.compose.material3.carousel {

  public final class CarouselKt {
    method @androidx.compose.runtime.Composable public static void HorizontalMultiBrowseCarousel(int x);
  }

  public final class CarouselState {
  }

  public final class CarouselStateKt {
    method @androidx.compose.runtime.Composable public static androidx.compose.material3.carousel.CarouselState rememberCarouselState(int x);
  }

}
""" + DEPRECATION

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
        {"name": "GoneView", "url": "/g", "platforms": [{"name": "iOS", "unavailable": True}]},
        {"name": "TupleView", "url": "/t", "platforms": IOS},
    ],
    "modifiers": [
        {"title": "sheet(isPresented:onDismiss:content:)", "url": "/documentation/swiftui/view/sheet", "page": "Modal presentations", "platforms": [{"name": "iOS", "introducedAt": "14.0"}]},
        {"title": "sheet(item:onDismiss:content:)", "url": "/documentation/swiftui/view/sheet2", "page": "Modal presentations", "platforms": IOS},
    ],
}


def by_name(rows):
    return {r["name"]: r for r in rows}


ALTS = {"HSplitView": "Button", "GoneView": "Button"}


def ios_rows():
    return by_name(ui_api_lists.parse_ios(EXTRACT, ALTS))


def test_s231_a_composable_fun_in_its_own_file_is_a_component():
    rows = by_name(ui_api_lists.parse_android(CURRENT))
    assert rows["Button"]["kind"] == "component" and rows["Button"]["family"] == "Button"
    assert rows["FilledTonalButton"]["kind"] == "variant" and rows["FilledTonalButton"]["family"] == "Button"


def test_s231_bytecode_twins_are_not_rows():
    names = [r["name"] for r in ui_api_lists.parse_android(CURRENT)]
    assert names.count("Button") == 1


def test_s231_a_composable_inside_a_defaults_object_is_its_own_row():
    r = by_name(ui_api_lists.parse_android(CURRENT))["ButtonDefaults.Icon"]
    assert (r["kind"], r["family"]) == ("variant", "Button")


def test_s231_every_public_top_level_class_is_a_row():
    rows = by_name(ui_api_lists.parse_android(CURRENT))
    assert (rows["SheetValue"]["kind"], rows["SheetValue"]["what"]) == ("supporting", "enum")
    assert "ButtonKt" not in rows and "CarouselStateKt" not in rows


def test_s231_a_family_with_no_same_name_component_gets_a_family_row():
    rows = [r for r in ui_api_lists.parse_android(CURRENT) if r["kind"] == "family"]
    assert sorted(r["name"] for r in rows) == ["Carousel", "Tooltip"]


def test_s231_family_hints_remember_goes_with_its_state_and_sheet_state_with_bottom_sheet():
    rows = by_name(ui_api_lists.parse_android(CURRENT))
    assert rows["rememberCarouselState"]["family"] == rows["CarouselState"]["family"] == "Carousel"
    assert rows["SheetState"]["family"] == "BottomSheet"
    assert len(rows) == 17


def test_s231_remember_x_is_supporting_in_its_family():
    r = by_name(ui_api_lists.parse_android(CURRENT))["rememberModalBottomSheetState"]
    assert (r["kind"], r["what"], r["family"]) == ("supporting", "remember", "BottomSheet")


def test_s231_a_defaults_object_colors_and_state_are_supporting():
    rows = by_name(ui_api_lists.parse_android(CURRENT))
    assert (rows["ButtonDefaults"]["kind"], rows["ButtonDefaults"]["what"], rows["ButtonDefaults"]["family"]) == ("supporting", "defaults", "Button")
    assert rows["ButtonColors"]["what"] == "colors"
    assert (rows["ModalBottomSheetState"]["what"], rows["ModalBottomSheetState"]["family"]) == ("state holder", "ModalBottomSheet")


def test_s231_an_experimental_annotation_is_kept_and_marked():
    rows = by_name(ui_api_lists.parse_android(CURRENT))
    assert rows["ModalBottomSheet"]["experimental"] is True and rows["Button"]["experimental"] is False


def test_s231_a_deprecated_composable_is_a_row_with_status_and_googles_replacement():
    r = by_name(ui_api_lists.parse_android(CURRENT))["OldButton"]
    assert (r["kind"], r["status"], r["replacement"]) == ("variant", "deprecated", "Button")
    assert "`@Deprecated` on every overload: current.txt line 15 (class `ButtonKt`)" in r["detail"]
    assert '"Renamed to Button"' in r["detail"] and "https://x/Button.kt" in r["detail"]
    assert by_name(ui_api_lists.parse_android(CURRENT))["Button"]["status"] == "-"


def test_s231_a_deprecated_composable_with_no_saved_message_fails_loudly():
    import pytest
    with pytest.raises(ValueError, match="OldButton"):
        ui_api_lists.parse_android(CURRENT.replace(DEPRECATION, ""))


def test_s231_the_extract_parses_the_same_as_the_full_file():
    assert ui_api_lists.parse_android(ui_api_lists.android_extract(CURRENT)) == ui_api_lists.parse_android(CURRENT)


def test_s231_apple_json_gives_view_conformers_and_view_modifiers_only():
    assert [t for t, _ in ui_api_lists.view_conformers(VIEW_PAGE)] == ["Button", "ButtonStyleConfiguration.Label", "HSplitView"]
    assert [t for t, _ in ui_api_lists.page_modifiers(MODAL_PAGE)] == ["sheet(isPresented:onDismiss:content:)", "sheet(item:onDismiss:content:)"]


def test_s231_modifiers_come_from_every_view_collection_page_and_methods_only():
    view = {**VIEW_PAGE, "topicSections": [{"title": "T", "identifiers": ["doc://s/body", "doc://s/pres", "doc://s/mod", "doc://s/other"]}],
            "references": {**VIEW_PAGE["references"],
                           "doc://s/body": {"title": "body", "url": "/documentation/swiftui/view/body-8kl5o"},
                           "doc://s/mod": {"title": "modifier(_:)", "url": "/documentation/swiftui/view/modifier(_:)"},
                           "doc://s/pres": {"title": "Presentation modifiers", "url": "/documentation/swiftui/view-presentation"},
                           "doc://s/other": {"title": "Previews", "url": "/documentation/swiftui/previews-in-xcode"}}}
    assert ui_api_lists.modifier_pages(view) == ["view-presentation"]
    assert [t for t, _ in ui_api_lists.page_modifiers(view)] == ["modifier(_:)"]


def test_s231_swiftui_plumbing_types_stay_with_category_plumbing():
    rows = ios_rows()
    assert rows["TupleView"]["category"] == "plumbing" and rows["Button"]["category"] == "-"


def test_s231_ios_kinds_and_since():
    rows = ios_rows()
    assert rows["Button"]["kind"] == "component" and rows["Button"]["status"] == "-"
    assert (rows["ButtonStyleConfiguration.Label"]["kind"], rows["ButtonStyleConfiguration.Label"]["family"]) == ("supporting", "Button")
    assert rows["sheet"]["kind"] == "modifier" and rows["sheet"]["since"] == "13.0"


def test_s231_nothing_is_left_out_every_ios_entry_is_a_row():
    assert len(ui_api_lists.parse_ios(EXTRACT, ALTS)) == len(EXTRACT["types"]) + 1


def test_s231_an_ios_deprecated_row_names_apples_replacement_and_field():
    r = ios_rows()["NavigationView"]
    assert (r["status"], r["replacement"]) == ("deprecated", "NavigationStack")
    assert r["detail"].startswith('`metadata.platforms[iOS].deprecatedAt`: `27.3`, `message`: "use NavigationStack instead"')


def test_s231_an_unavailable_ios_row_names_the_field_platforms_and_the_ios_alternative():
    rows = ios_rows()
    assert (rows["HSplitView"]["status"], rows["HSplitView"]["replacement"]) == ("unavailable-ios", "Button")
    assert rows["HSplitView"]["detail"].startswith("`metadata.platforms[]` has no `iOS` entry (names: macOS)")
    assert rows["GoneView"]["detail"].startswith("`metadata.platforms[iOS].unavailable`: `true`")


def test_s231_an_unavailable_ios_row_with_no_alternative_or_a_bad_one_fails():
    import pytest
    with pytest.raises(ValueError, match="GoneView"):
        ui_api_lists.parse_ios(EXTRACT, {"HSplitView": "Button"})
    with pytest.raises(ValueError, match="NotARow"):
        ui_api_lists.parse_ios(EXTRACT, {**ALTS, "GoneView": "NotARow"})


def test_s231_a_none_alternative_with_no_reason_fails_and_a_reason_is_kept():
    import pytest
    with pytest.raises(ValueError, match="GoneView: .*none.* needs a one-line reason"):
        ui_api_lists.parse_ios(EXTRACT, {**ALTS, "GoneView": "none"})
    with pytest.raises(ValueError, match="GoneView: .*none.* needs a one-line reason"):
        ui_api_lists.parse_ios(EXTRACT, {**ALTS, "GoneView": "none:  "})
    r = by_name(ui_api_lists.parse_ios(EXTRACT, {**ALTS, "GoneView": "none: a Mac window; iOS has no equivalent"}))["GoneView"]
    assert (r["replacement"], r["reason"]) == ("none", "a Mac window; iOS has no equivalent")
    assert r["detail"].endswith("`none`, because a Mac window; iOS has no equivalent")


def test_s231_every_real_none_alternative_has_a_reason():
    nones = {k: v for k, v in ui_api_lists.IOS_ALTERNATIVES.items() if v.split(":", 1)[0] == "none"}
    assert nones and all(v.startswith("none: ") and len(v) > 12 for v in nones.values()), \
        [k for k, v in nones.items() if not v.startswith("none: ")]


def test_s231_the_real_ios_alternatives_are_all_live_rows():
    ui_api_lists.parse_ios(json.loads(ui_api_lists.IOS_SRC.read_text()))


def write_sources(tmp_path):
    src, out = tmp_path / "sources", tmp_path / "out"
    src.mkdir()
    out.mkdir()
    (src / ui_api_lists.ANDROID_SRC.name).write_text(ui_api_lists.android_extract(CURRENT))
    # The real alternatives table names real rows, so the fixture keeps only its available and deprecated types.
    live = {**EXTRACT, "types": [t for t in EXTRACT["types"] if t["name"] not in ALTS]}
    (src / ui_api_lists.IOS_SRC.name).write_text(json.dumps(live))
    return ["--sources", str(src), "--out", str(out)], src, out


def test_s231_written_lists_pass_check_with_count_and_pinned_sha(tmp_path):
    args, src, out = write_sources(tmp_path)
    assert ui_api_lists.main(args) == 0
    assert ui_api_lists.main(args + ["--check"]) == 0
    md = (out / ui_api_lists.ANDROID_MD.name).read_text()
    assert "Count: 17" in md and "Left out" not in md and "Upstream file sha256" in md and ui_api_lists.sha((src / ui_api_lists.ANDROID_SRC.name).read_text()) in md


def test_s231_check_fails_when_the_saved_source_changed(tmp_path, capsys):
    args, src, out = write_sources(tmp_path)
    ui_api_lists.main(args)
    f = src / ui_api_lists.ANDROID_SRC.name
    f.write_text(f.read_text().replace("FilledTonalButton", "ElevatedButton"))
    assert ui_api_lists.main(args + ["--check"]) == 1
    out_text = capsys.readouterr().out
    assert "android-m3-api.md" in out_text and "sha256" in out_text


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
    good = {**base, "platformApi": {"android": {
        "variants": [{"name": "FilledTonalButton", "note": "A softer fill for a second action."},
                     {"name": "ElevatedButton", "props": [{"name": "elevation", "type": "ButtonElevation", "description": "Its shadow."}]}],
        "supporting": [{"name": "ButtonDefaults", "use": "Read the default colors and sizes."}]}}}
    assert check_ui_docs.validate(good, schema, schema) == []
    assert check_ui_docs.api_shape_errors(good) == []
    assert check_ui_docs.validate({**base, "platformApi": {"android": {"variant": []}}}, schema, schema) != []


def api_doc(variants=(), supporting=()):
    return {"name": "B", "platformApi": {"android": {"variants": list(variants), "supporting": list(supporting)}}}


def test_s231_a_plain_string_item_fails_the_schema():
    import check_ui_docs
    schema = json.loads((ROOT / "ui" / "schema" / "component.schema.json").read_text())
    base = {"name": "B", "displayName": "B", "platforms": {"android": None, "ios": None, "web": None}, "usage": {"description": "d"}, "props": []}
    bad = {**base, "platformApi": {"android": {"variants": ["FilledTonalButton"]}}}
    assert any("must be object" in e for e in check_ui_docs.validate(bad, schema, schema))
    bad = {**base, "platformApi": {"android": {"supporting": ["ButtonDefaults"]}}}
    assert any("must be object" in e for e in check_ui_docs.validate(bad, schema, schema))


def test_s231_an_empty_note_or_use_fails():
    import check_ui_docs
    assert any("note" in e for e in check_ui_docs.api_shape_errors(api_doc(variants=[{"name": "FilledTonalButton", "note": " "}])))
    assert any("note" in e for e in check_ui_docs.api_shape_errors(api_doc(variants=[{"name": "FilledTonalButton"}])))
    assert any("use" in e for e in check_ui_docs.api_shape_errors(api_doc(supporting=[{"name": "ButtonDefaults", "use": ""}])))


def test_s231_a_deprecated_or_unavailable_item_without_a_replacement_fails():
    import check_ui_docs
    for status in ("deprecated", "unavailable-ios"):
        errs = check_ui_docs.api_shape_errors(api_doc(variants=[{"name": "TabRow", "note": "old", "status": status}]))
        assert any("TabRow" in e and "replacement" in e for e in errs)
        errs = check_ui_docs.api_shape_errors(api_doc(supporting=[{"name": "X", "use": "u", "status": status, "replacement": " "}]))
        assert any("replacement" in e for e in errs)
    good = api_doc(variants=[{"name": "TabRow", "note": "old", "status": "deprecated", "replacement": "PrimaryTabRow"}])
    assert check_ui_docs.api_shape_errors(good) == []


def test_s231_a_doc_level_status_needs_a_replacement_and_the_schema_takes_it():
    import check_ui_docs
    schema = json.loads((ROOT / "ui" / "schema" / "component.schema.json").read_text())
    base = {"name": "B", "displayName": "B", "platforms": {"android": None, "ios": None, "web": None}, "usage": {"description": "d"}, "props": []}
    assert any("replacement" in e for e in check_ui_docs.api_shape_errors({**base, "status": "deprecated"}))
    ok = {**base, "status": "deprecated", "replacement": "NavigationStack",
          "platformApi": {"ios": {"variants": [{"name": "V", "note": "n", "status": "unavailable-ios", "replacement": "W"}]}}}
    assert check_ui_docs.validate(ok, schema, schema) == [] and check_ui_docs.api_shape_errors(ok) == []
    assert check_ui_docs.validate({**base, "status": "gone"}, schema, schema) != []


def test_s231_a_name_listed_twice_in_one_doc_fails():
    import check_ui_docs
    errs = check_ui_docs.api_shape_errors(api_doc(variants=[{"name": "X", "note": "a"}], supporting=[{"name": "X", "use": "b"}]))
    assert any("X" in e and "twice" in e for e in errs)


def test_s231_the_real_lists_match_their_saved_sources():
    assert ui_api_lists.main(["--check"]) == 0


def test_s231_an_ios_extract_split_into_two_files_gives_the_same_list():
    one = {"ios-swiftui-extract.json": json.dumps(EXTRACT)}
    head = {**EXTRACT, "modifiers": EXTRACT["modifiers"][:1]}
    two = {"ios-swiftui-extract.json": json.dumps(head), "ios-swiftui-extract-2.json": json.dumps({"modifiers": EXTRACT["modifiers"][1:]})}
    assert ui_api_lists.merge_ios(two) == ui_api_lists.merge_ios(one)
