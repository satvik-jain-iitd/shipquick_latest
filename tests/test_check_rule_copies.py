"""Story #316 (A3): scripts/check_rule_copies.py keeps the kit rules honest.

A child CLAUDE.md must carry the kit rule block unchanged between the markers, and the
load-bearing phrases must be present in the kit CLAUDE.md. A missing or changed phrase
names the file.
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_rule_copies.py"
KIT_TEXT = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
START = "<!-- shipquick-rules:start -->"
END = "<!-- shipquick-rules:end -->"


def kit_block():
    lines = KIT_TEXT.splitlines()
    first = next(i for i, line in enumerate(lines) if line.startswith("0. "))
    return "\n".join(lines[first:]).strip()


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, cwd=ROOT
    )


def kit_copy(tmp_path, text=KIT_TEXT):
    kit = tmp_path / "kit"
    kit.mkdir()
    (kit / "CLAUDE.md").write_text(text, encoding="utf-8")
    return kit


def child_copy(tmp_path, block):
    child = tmp_path / "child" / "CLAUDE.md"
    child.parent.mkdir()
    child.write_text(f"# child rules\n\n{START}\n{block}\n{END}\n", encoding="utf-8")
    return child


def test_the_kit_claude_md_passes_every_phrase():
    result = run()
    assert result.returncode == 0, result.stdout + result.stderr
    assert "ok" in result.stdout


def test_a_changed_phrase_turns_the_check_red_and_names_the_file(tmp_path):
    kit = kit_copy(tmp_path, KIT_TEXT.replace("Radar first", "Radar later"))
    result = run("--kit-root", str(kit))
    assert result.returncode == 1
    assert "CLAUDE.md" in result.stdout + result.stderr
    assert "Radar first" in result.stdout + result.stderr


def test_a_child_with_the_kit_block_unchanged_passes(tmp_path):
    kit = kit_copy(tmp_path)
    child = child_copy(tmp_path, kit_block())
    result = run("--kit-root", str(kit), "--child", str(child))
    assert result.returncode == 0, result.stdout + result.stderr


def test_a_child_with_one_word_changed_fails_and_names_the_child(tmp_path):
    kit = kit_copy(tmp_path)
    child = child_copy(tmp_path, kit_block().replace("Radar first", "Radar second", 1))
    result = run("--kit-root", str(kit), "--child", str(child))
    assert result.returncode == 1
    assert str(child) in result.stdout + result.stderr


def test_a_child_without_the_markers_fails_and_points_at_adoption(tmp_path):
    kit = kit_copy(tmp_path)
    child = tmp_path / "CLAUDE.md"
    child.write_text(kit_block() + "\n", encoding="utf-8")
    result = run("--kit-root", str(kit), "--child", str(child))
    assert result.returncode == 1
    out = result.stdout + result.stderr
    assert "shipquick-rules:start" in out and "ADOPTION.md" in out


def test_the_script_is_stdlib_only():
    src = SCRIPT.read_text(encoding="utf-8")
    for line in src.splitlines():
        if line.startswith(("import ", "from ")):
            mod = line.split()[1].split(".")[0]
            assert mod in sys.stdlib_module_names, line
