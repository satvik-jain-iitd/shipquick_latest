"""Story #231, review 2 of the iOS stack: the generator of the UI API lists is protected, like the checks that read them."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_s231_ui_api_lists_is_a_protected_path():
    lines = [l.strip() for l in (ROOT / "scripts" / "protected_paths.txt").read_text(encoding="utf-8").splitlines()]
    assert "scripts/ui_api_lists.py" in lines


def test_s454_the_adopt_files_list_is_a_protected_path():
    # it decides which diffs check_tdd.py exempts, so a PR must not widen it in auto mode (rule 37)
    lines = [l.strip() for l in (ROOT / "scripts" / "protected_paths.txt").read_text(encoding="utf-8").splitlines()]
    assert "scripts/adopt_files.txt" in lines
