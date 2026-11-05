"""Story #146 (PR #152 review): scripts/check_screens_wired.py -- a project with a real screen in
docs/screens.txt must also run `screens.sh --check` somewhere in its own CI."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import check_screens_wired as csw  # noqa: E402

WIRED = "run: bash scripts/screens.sh --check\n"
UNWIRED = "run: bash scripts/screens.sh\n"
REAL_SCREENS = "welcome | /welcome | 390x844 | welcome\n"
EMPTY_SCREENS = "# nothing yet\n"


def test_no_screens_configured_is_skipped():
    assert csw.decide("", []) is None
    assert csw.decide(EMPTY_SCREENS, []) is None


def test_screens_configured_with_no_check_call_anywhere_fails():
    why = csw.decide(REAL_SCREENS, [UNWIRED])
    assert why and "screens.sh --check" in why


def test_screens_configured_with_a_check_call_in_some_workflow_passes():
    assert csw.decide(REAL_SCREENS, ["other: stuff\n", WIRED]) is None


def test_screens_configured_with_no_workflows_at_all_fails():
    why = csw.decide(REAL_SCREENS, [])
    assert why and "no workflow" in why


def test_cli_exit_codes_and_messages(tmp_path, capsys):
    screens = tmp_path / "screens.txt"
    wf_dir = tmp_path / "workflows"
    wf_dir.mkdir()

    screens.write_text(EMPTY_SCREENS, encoding="utf-8")
    assert csw.main(["--screens-file", str(screens), "--workflows-dir", str(wf_dir)]) == 0
    assert "skipped" in capsys.readouterr().out

    screens.write_text(REAL_SCREENS, encoding="utf-8")
    assert csw.main(["--screens-file", str(screens), "--workflows-dir", str(wf_dir)]) == 1
    assert "no workflow" in capsys.readouterr().out

    (wf_dir / "ci.yml").write_text(WIRED, encoding="utf-8")
    assert csw.main(["--screens-file", str(screens), "--workflows-dir", str(wf_dir)]) == 0
    assert "wired OK" in capsys.readouterr().out


def test_cli_with_no_screens_file_at_all_is_skipped(tmp_path, capsys):
    wf_dir = tmp_path / "workflows"
    wf_dir.mkdir()
    assert csw.main(["--screens-file", str(tmp_path / "missing.txt"), "--workflows-dir", str(wf_dir)]) == 0
    assert "skipped" in capsys.readouterr().out
