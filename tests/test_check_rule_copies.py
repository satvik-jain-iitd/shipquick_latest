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


def kit_copy(tmp_path, text=KIT_TEXT, skill=True):
    """A kit folder with CLAUDE.md and, unless skill=False, the shipquick-feedback skill file."""
    kit = tmp_path / "kit"
    kit.mkdir()
    (kit / "CLAUDE.md").write_text(text, encoding="utf-8")
    if skill:
        target = kit / "skills" / "shipquick-feedback" / "SKILL.md"
        target.parent.mkdir(parents=True)
        shutil.copy(ROOT / "skills" / "shipquick-feedback" / "SKILL.md", target)
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


# ---- review of #335: the rule 33 phrase also lives in the shipquick-feedback skill ----
def test_s316_the_skill_restating_rule_33_is_watched(tmp_path):
    """Changing the phrase in the skill (not in CLAUDE.md) turns the check red and names the skill file."""
    kit = kit_copy(tmp_path, skill=False)
    skill = kit / "skills" / "shipquick-feedback" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    original = (ROOT / "skills" / "shipquick-feedback" / "SKILL.md").read_text(encoding="utf-8")
    assert 'at least three "Why" lines' in original
    skill.write_text(original.replace('at least three "Why" lines', 'at least two "Why" lines'), encoding="utf-8")
    result = run("--kit-root", str(kit))
    assert result.returncode == 1, result.stdout
    assert "skills/shipquick-feedback/SKILL.md" in result.stdout
    assert "three" in result.stdout


def test_s316_the_skill_file_is_a_required_part_of_the_kit_root(tmp_path):
    result = run("--kit-root", str(kit_copy(tmp_path, skill=False)))     # a kit copy with no skill file at all
    assert result.returncode == 1
    assert "skills/shipquick-feedback/SKILL.md" in result.stdout
