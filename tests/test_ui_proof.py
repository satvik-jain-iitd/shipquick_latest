"""Story #217: the compile proofs are generated from the contracts, carry every platform prop by name,
and go stale (fail --check) when a contract changes. CI compiles them; these tests check the generator."""
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import ui_proof  # noqa: E402

SRC = ROOT / "ui" / "components"


def copy_components(tmp_path):
    root = tmp_path / "components"
    shutil.copytree(SRC, root)
    return root


def function(text, name):
    """`fun Proof<name>()` or `struct Proof<name>` in a proof file, with its annotations."""
    m = re.search(rf"(?:^@[^\n]*\n)*(?:fun|struct) Proof{name}\b.*?\n}}\n", text, re.S | re.M)
    assert m, f"no proof for {name}"
    return m.group(0)


def test_s217_the_committed_proofs_are_current_with_the_contracts():
    assert ui_proof.main(["--check"]) == 0


def test_s217_every_platform_prop_of_every_contract_is_called_by_its_name():
    files, bad = ui_proof.render(SRC)
    assert not bad, bad
    for d in sorted(SRC.iterdir()):
        c = d / f"{d.name}.contract.json"
        if not c.exists():
            continue
        contract = json.loads(c.read_text(encoding="utf-8"))
        for platform, sign in (("android", "{} = "), ("ios", "{}: ")):
            spec = (ui_proof.ANDROID if platform == "android" else ui_proof.IOS).get(d.name, {})
            for prop in contract["platforms"].get(platform, {}):
                body = function(files[platform], d.name)
                if prop in spec.get("p", []):
                    continue  # a Swift param with no label: passed by position
                assert sign.format(prop) in body or f".{prop}(" in body, (platform, d.name, prop)


def test_s217_an_invented_prop_lands_in_the_real_call_on_both_platforms(tmp_path):
    root = copy_components(tmp_path)
    for name, platform in (("Checkbox", "android"), ("Slider", "ios")):
        path = root / name / f"{name}.contract.json"
        contract = json.loads(path.read_text(encoding="utf-8"))
        contract["platforms"][platform]["inventedProp"] = {"type": {"kind": "boolean"}, "optional": True}
        path.write_text(json.dumps(contract), encoding="utf-8")
    files, bad = ui_proof.render(root)
    assert not bad, bad
    assert "Checkbox(" in function(files["android"], "Checkbox")
    assert "inventedProp = true" in function(files["android"], "Checkbox")
    assert "inventedProp: true" in function(files["ios"], "Slider")
    assert ui_proof.main(["--check", "--root", str(root)]) == 1, "a changed contract makes the proofs stale"


def test_s217_a_component_with_no_spec_fails_by_name(tmp_path):
    root = copy_components(tmp_path)
    shutil.copytree(root / "Checkbox", root / "Zebra")
    for f in (root / "Zebra").iterdir():
        f.rename(f.with_name(f.name.replace("Checkbox", "Zebra")))
    _, bad = ui_proof.render(root)
    assert any(b.startswith("android Zebra: no spec") for b in bad), bad


def test_s217_opt_in_comes_from_googles_api_extract():
    files, _ = ui_proof.render(SRC)
    assert "@OptIn(ExperimentalMaterial3Api::class)" in function(files["android"], "SearchBar")
    assert "@OptIn" not in function(files["android"], "Checkbox")


def test_s217_the_build_pins_are_exact_and_agree_with_ci():
    props = (ROOT / "ui" / "android" / "gradle" / "wrapper" / "gradle-wrapper.properties").read_text(encoding="utf-8")
    version = re.search(r"gradle-([\d.]+)-bin\.zip", props).group(1)
    assert re.search(r"^distributionSha256Sum=[0-9a-f]{64}$", props, re.M)
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert f'gradle-version: "{version}"' in ci
    build = (ROOT / "ui" / "android" / "build.gradle.kts").read_text(encoding="utf-8")
    assert 'platform("androidx.compose:compose-bom:2025.10.00")' in build  # maps material3 to 1.4.0
    for line in re.findall(r'version "([^"]+)"', build):
        assert re.fullmatch(r"\d+\.\d+\.\d+", line), line
    assert "xcode-select -s /Applications/Xcode_" in ci


def ui_changes_step():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    return re.search(r"  ui-changes:\n.*?\n  ui-android-compile:", ci, re.S).group(0)


def test_s217_the_ui_filter_covers_what_decides_the_compile_and_nothing_unrelated():
    pattern = re.search(r"grep -qE '([^']+)'", ui_changes_step()).group(1)
    for path in ("ui/android/build.gradle.kts", "scripts/ui_proof.py", ".github/workflows/ci.yml", "design/tokens.json"):
        assert re.search(pattern, path), f"{path} must run the compile jobs"
    for path in ("docs/x.md", "scripts/other.py", "tests/test_ui_proof.py"):
        assert not re.search(pattern, path), f"{path} must not run the compile jobs"


def test_s217_a_failed_base_fetch_outputs_ui_true():
    assert 'git fetch -q origin "$BASE" || { echo ui=true >> "$GITHUB_OUTPUT"; exit 0; }' in ui_changes_step()
