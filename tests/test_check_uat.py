"""Story #120: check_uat.py validates the "## UAT on dev" section of a dev -> main PR body — a story
line with no steps or no Expected: fails, and the two fixed lines plus the Known bugs line are required."""
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_uat.py"

GOOD_STORY = """- [ ] #219 Fix: cart total after removing an item
  Open: https://dev.app.example.com/cart (log in with test phone 9999999999, OTP 123456)
  1. Add "Masala Dosa" 3 times.
  2. Tap the minus on "Masala Dosa" once.
  Expected: the cart shows 2 x Masala Dosa and the total is ₹240 (2 x ₹120).
"""

TAIL = """- [ ] Old flows still work
- [ ] Design matches the approved boards
Known bugs going to production: none
"""


def run(text):
    return subprocess.run(["python3", str(SCRIPT)], input=text, capture_output=True, text=True)


def test_s120_a_fully_filled_checklist_passes():
    r = run(GOOD_STORY + TAIL)
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "OK" in r.stdout


def test_s120_empty_section_fails():
    r = run("")
    assert r.returncode == 1 and "empty" in r.stdout.lower()


def test_s120_a_story_line_with_no_open_fails_and_names_it():
    story = GOOD_STORY.replace("  Open: https://dev.app.example.com/cart (log in with test phone 9999999999, OTP 123456)\n", "")
    r = run(story + TAIL)
    assert r.returncode == 1 and "no Open" in r.stdout and "#219" in r.stdout


def test_s120_a_story_line_with_no_steps_fails_and_names_it():
    story = GOOD_STORY.replace('  1. Add "Masala Dosa" 3 times.\n  2. Tap the minus on "Masala Dosa" once.\n', "")
    r = run(story + TAIL)
    assert r.returncode == 1 and "no numbered steps" in r.stdout and "#219" in r.stdout


def test_s120_a_story_line_with_no_expected_fails_and_names_it():
    story = GOOD_STORY.replace("  Expected: the cart shows 2 x Masala Dosa and the total is ₹240 (2 x ₹120).\n", "")
    r = run(story + TAIL)
    assert r.returncode == 1 and "no Expected" in r.stdout and "#219" in r.stdout


def test_s120_no_story_lines_fails():
    r = run(TAIL)
    assert r.returncode == 1 and "no story lines" in r.stdout.lower()


@pytest.mark.parametrize("missing", ["- [ ] Old flows still work\n", "- [ ] Design matches the approved boards\n"])
def test_s120_a_missing_fixed_line_fails(missing):
    tail = TAIL.replace(missing, "")
    r = run(GOOD_STORY + tail)
    assert r.returncode == 1 and "missing" in r.stdout.lower()


def test_s120_a_missing_known_bugs_line_fails():
    tail = TAIL.replace("Known bugs going to production: none\n", "")
    r = run(GOOD_STORY + tail)
    assert r.returncode == 1 and "known bugs" in r.stdout.lower()


def test_s120_a_ticked_story_box_is_still_fine_structurally():
    r = run(GOOD_STORY.replace("- [ ] #219", "- [x] #219") + TAIL)
    assert r.returncode == 0, (r.stdout, r.stderr)
