"""Story #503 (feedback #500): the "Wiring CI" example in docs/SCREENS.md passes the kit's own wiring check.
A project that follows the doc must not fail `check_screens_wired.py` (the adoption job)."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import check_screens_wired as csw  # noqa: E402

REAL_SCREENS = "welcome | /welcome | 390x844 | welcome\n"


def wiring_section():
    text = (ROOT / "docs" / "SCREENS.md").read_text(encoding="utf-8")
    m = re.search(r"^## Wiring CI\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    assert m, "docs/SCREENS.md has no `## Wiring CI` section"
    return m.group(1)


def yaml_examples(section):
    return re.findall(r"```yaml\n(.*?)```", section, re.S)


def test_s503_the_wiring_example_runs_screens_sh_check():
    section = wiring_section()
    assert re.search(r"bash scripts/screens\.sh --check", section), "the section must show the --check step"


def test_s503_the_wiring_example_passes_the_kit_wiring_check():
    examples = yaml_examples(wiring_section())
    assert examples, "the `## Wiring CI` section has no yaml example"
    assert csw.decide(REAL_SCREENS, examples) is None, "a project that copies the example still fails check_screens_wired.py"


def test_s503_the_section_says_how_to_split_a_shared_e2e_run():
    section = wiring_section()
    assert "exclude" in section.lower() and "once" in section.lower(), "must say how the screens spec runs once"
    assert "add up" in section.lower(), "must say how to prove the two test counts add up"


def test_s503_the_check_step_comes_before_the_upload_step_in_the_example():
    """#506 QA point 2: order by text position, no YAML library."""
    example = yaml_examples(wiring_section())[0]
    check = example.find("bash scripts/screens.sh --check")
    upload = example.find("uses: actions/upload-artifact")
    assert check != -1 and upload != -1 and check < upload, (check, upload)


def test_s503_the_section_regex_ends_at_the_end_of_the_file_too(tmp_path, monkeypatch):
    """#506 QA point 3: a `## Wiring CI` that is the last section still counts."""
    fake = tmp_path / "docs"
    fake.mkdir()
    (fake / "SCREENS.md").write_text("# x\n\n## Wiring CI\n\n```yaml\nrun: bash scripts/screens.sh --check\n```\n", encoding="utf-8")
    monkeypatch.setattr(sys.modules[__name__], "ROOT", tmp_path)
    assert "screens.sh --check" in wiring_section()
