"""Story #231, review 2 of the iOS stack: the generator of the UI API lists is protected, like the checks that read them."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_s231_ui_api_lists_is_a_protected_path():
    lines = [l.strip() for l in (ROOT / "scripts" / "protected_paths.txt").read_text(encoding="utf-8").splitlines()]
    assert "scripts/ui_api_lists.py" in lines
