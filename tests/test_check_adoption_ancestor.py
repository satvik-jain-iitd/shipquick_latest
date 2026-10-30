"""Story #131: scripts/check_adoption_ancestor.py's decide() -- a pinned ShipQuick SHA must be
merged into dev or main, or be a release tag, never just any commit that exists in history."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import check_adoption_ancestor as caa  # noqa: E402

SHA = "a" * 40


def test_identical_to_dev_passes():
    assert caa.decide(SHA, "identical", None, []) is None


def test_behind_dev_passes():
    assert caa.decide(SHA, "behind", None, []) is None


def test_behind_main_passes():
    assert caa.decide(SHA, None, "behind", []) is None


def test_a_release_tag_passes_even_with_no_compare_status():
    assert caa.decide(SHA, None, None, [SHA]) is None


def test_ahead_of_both_and_no_tag_refuses():
    why = caa.decide(SHA, "ahead", "ahead", [])
    assert why and SHA[:7] in why and "adopt.sh" in why


def test_diverged_from_both_and_no_tag_refuses():
    why = caa.decide(SHA, "diverged", "diverged", [])
    assert why and "not on dev or main" in why


def test_an_unreachable_branch_compare_and_no_tag_refuses():
    assert caa.decide(SHA, None, None, []) is not None
