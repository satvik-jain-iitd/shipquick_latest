"""PR #122 blocker fix: the UAT checklist gate only applies to a project whose own CLAUDE.md has a
filled "Dev link:" line. ShipQuick itself has none, so it is exempt — by project, not by PR title."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "has_dev_link.sh"


def claude_md(tmp_path, text):
    p = tmp_path / "CLAUDE.md"
    p.write_text(text, encoding="utf-8")
    return p


def run(*args):
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True)


def test_a_filled_dev_link_exits_0(tmp_path):
    f = claude_md(tmp_path, "## Environments\n- Dev link: https://demo-dev.vercel.app\n- Production link: https://demo.example.com\n")
    assert run(str(f)).returncode == 0


def test_an_empty_dev_link_exits_1(tmp_path):
    f = claude_md(tmp_path, "## Environments\n- Dev link:\n- Production link: https://demo.example.com\n")
    assert run(str(f)).returncode == 1


def test_a_placeholder_dev_link_exits_1(tmp_path):
    f = claude_md(tmp_path, "## Environments\n- Dev link: <url, or \"not deployed yet (D0)\">\n")
    assert run(str(f)).returncode == 1


def test_no_dev_link_line_at_all_exits_1(tmp_path):
    f = claude_md(tmp_path, "# Project Facts\n## Stack\n- Language: Python\n")
    assert run(str(f)).returncode == 1


def test_no_such_file_exits_1(tmp_path):
    assert run(str(tmp_path / "nope.md")).returncode == 1


def test_missing_arg_is_a_usage_error():
    assert run().returncode == 2
