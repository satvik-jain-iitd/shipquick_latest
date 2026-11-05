"""Story #126: scripts/check_freeze.py decides whether `.shipquick/freeze` blocks a merge."""
import datetime
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import check_freeze as cf  # noqa: E402

TODAY = datetime.date(2026, 10, 30)


def test_no_file_is_not_frozen():
    assert cf.check(None, TODAY) is None


def test_empty_content_is_not_frozen():
    assert cf.check("   \n", TODAY) is None


def test_a_freeze_within_its_until_date_blocks_with_the_reason():
    why = cf.check("reason: holiday code freeze\nuntil: 2026-11-15\n", TODAY)
    assert why and "holiday code freeze" in why and "2026-11-15" in why
    assert "STALE" not in why


def test_a_freeze_past_its_until_date_is_flagged_stale_and_still_blocks():
    why = cf.check("reason: incident response\nuntil: 2026-10-01\n", TODAY)
    assert why and "STALE" in why and "incident response" in why
    assert "does not lift itself" in why


def test_a_freeze_exactly_on_its_until_date_is_not_stale():
    why = cf.check("reason: x\nuntil: 2026-10-30\n", TODAY)
    assert why and "STALE" not in why


def test_a_freeze_with_no_until_date_is_flagged_instead_of_crashing():
    why = cf.check("reason: x\n", TODAY)
    assert why and "no valid until" in why


def test_a_freeze_with_a_garbled_until_date_is_flagged():
    why = cf.check("reason: x\nuntil: not-a-date\n", TODAY)
    assert why and "no valid until" in why


def test_cli_exit_codes(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["check_freeze.py", "--today", "2026-10-30"])
    monkeypatch.setattr(sys, "stdin", type("F", (), {"read": staticmethod(lambda: "")})())
    assert cf.main() == 0
    assert "not frozen" in capsys.readouterr().out

    monkeypatch.setattr(sys, "stdin", type("F", (), {"read": staticmethod(lambda: "reason: x\nuntil: 2026-11-01\n")})())
    assert cf.main() == 1
