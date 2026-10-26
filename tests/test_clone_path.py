"""S0.19 (story #69): someone who clones ShipQuick and follows the README gets a project that matches the README."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")


def tree_paths():
    """Every path in the README's 'What's inside?' tree, built from the tree's indentation."""
    block = README.split("## What's inside?", 1)[1].split("```", 2)[1]
    stack, paths = [], []
    for line in block.splitlines():
        m = re.match(r"^((?:│   |    )*)[├└]── (\S+)", line)
        if not m or m.group(2).startswith("ios"):   # "ios / flutter READMEs" names several files, not one path
            continue
        depth = len(m.group(1)) // 4
        stack = stack[:depth] + [m.group(2).rstrip("/←").rstrip("/")]
        paths.append("/".join(stack))
    return paths


def test_s19_every_path_in_the_readme_tree_exists():
    paths = tree_paths()
    assert len(paths) > 30, paths   # the parser really read the tree
    missing = [p for p in paths if not (ROOT / p).exists()]
    assert not missing, missing


def test_s19_every_folder_in_the_structure_guide_exists():
    guide = README.split("## Folder Structure Guide", 1)[1].split("\n## ", 1)[0]
    folders = re.findall(r"^\| `([^`]+)/` \|", guide, re.M)
    assert folders, guide
    assert not [f for f in folders if not (ROOT / f).is_dir()]


def test_s19_the_quick_start_runs_the_local_checks_and_sets_up_the_roadmap_and_the_mode():
    quick = README.split("## Quick Start", 1)[1].split("\n## ", 1)[0]
    for needle in ("pre-commit install", "scripts/check_local.sh", "roadmap.json", "scripts/mode.sh set"):
        assert needle in quick, needle
    custom = README.split("## How to Customize for Your Brand", 1)[1].split("\n## ", 1)[0]
    assert "scripts/check_placeholders.py" in custom


def run_placeholders(path):
    return subprocess.run([sys.executable, str(ROOT / "scripts" / "check_placeholders.py"), str(path)], capture_output=True, text=True)


def test_s19_the_placeholder_check_lists_what_is_left_and_passes_when_filled(tmp_path):
    f = tmp_path / "design-tokens.md"
    f.write_text("Primary: <PRIMARY_COLOR>\nFont: <PRIMARY_FONT>\nA tag <b> and a link <https://x.y> are fine.\n", encoding="utf-8")
    r = run_placeholders(f)
    assert r.returncode == 1 and "<PRIMARY_COLOR>" in r.stdout and "<PRIMARY_FONT>" in r.stdout and "<b>" not in r.stdout
    f.write_text("Primary: #0066CC\nFont: Roboto\n", encoding="utf-8")
    assert run_placeholders(f).returncode == 0


def test_s19_a_fresh_clone_passes_the_local_checks(tmp_path):
    clone = tmp_path / "my-app"
    subprocess.run(["git", "clone", "-q", str(ROOT), str(clone)], check=True)
    r = subprocess.run(["bash", "scripts/check_local.sh", "sizes", "markers", "md-blocks"], cwd=clone, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
