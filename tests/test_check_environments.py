"""Story #120: scripts/check_environments.sh fails a child project whose CLAUDE.md has an empty
`Dev link:` or `Production link:` line, once the project is past milestone D0. At D0 it always passes
(nothing is deployed yet)."""
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_environments.sh"

FILLED = """# demo: Project Facts

## Environments
- Dev link: https://demo-dev.vercel.app
- Production link: https://demo.example.com
"""

EMPTY_DEV = """# demo: Project Facts

## Environments
- Dev link:
- Production link: https://demo.example.com
"""

PLACEHOLDER_PROD = """# demo: Project Facts

## Environments
- Dev link: https://demo-dev.vercel.app
- Production link: <url>
"""

NO_SECTION = """# demo: Project Facts

## Stack
- Language: Python
"""


def claude_md(tmp_path, text, name="CLAUDE.md"):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


def run(*args):
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True)


def test_s120_d0_always_passes_even_with_nothing_filled(tmp_path):
    f = claude_md(tmp_path, NO_SECTION)
    r = run("--claude-md", str(f), "--milestone", "D0")
    assert r.returncode == 0, (r.stdout, r.stderr)


@pytest.mark.parametrize("milestone", ["D1", "D2", "D6"])
def test_s120_past_d0_both_links_filled_passes(tmp_path, milestone):
    f = claude_md(tmp_path, FILLED)
    r = run("--claude-md", str(f), "--milestone", milestone)
    assert r.returncode == 0, (r.stdout, r.stderr)


def test_s120_past_d0_an_empty_dev_link_fails_and_names_it(tmp_path):
    f = claude_md(tmp_path, EMPTY_DEV)
    r = run("--claude-md", str(f), "--milestone", "D1")
    assert r.returncode == 1 and "Dev link" in r.stderr


def test_s120_past_d0_a_placeholder_production_link_fails_and_names_it(tmp_path):
    f = claude_md(tmp_path, PLACEHOLDER_PROD)
    r = run("--claude-md", str(f), "--milestone", "D2")
    assert r.returncode == 1 and "Production link" in r.stderr


def test_s120_past_d0_a_missing_section_fails_and_names_both(tmp_path):
    f = claude_md(tmp_path, NO_SECTION)
    r = run("--claude-md", str(f), "--milestone", "D1")
    assert r.returncode == 1
    assert "Dev link" in r.stderr and "Production link" in r.stderr


def test_s120_an_unknown_milestone_is_a_usage_error(tmp_path):
    f = claude_md(tmp_path, FILLED)
    r = run("--claude-md", str(f), "--milestone", "D9")
    assert r.returncode == 2 and "usage" in r.stderr.lower()
