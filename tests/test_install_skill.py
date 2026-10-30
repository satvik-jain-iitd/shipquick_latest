"""Story #118: scripts/install_skill.sh links skills/shipquick-feedback into ~/.claude/skills. Safe to run twice."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "install_skill.sh"
SKILL_SRC = ROOT / "skills" / "shipquick-feedback"


def run(home):
    return subprocess.run(["bash", str(SCRIPT)], capture_output=True, text=True, env={**__import__("os").environ, "HOME": str(home)})


def test_s118_links_the_skill_into_home_claude_skills(tmp_path):
    r = run(tmp_path)
    assert r.returncode == 0, (r.stdout, r.stderr)
    link = tmp_path / ".claude" / "skills" / "shipquick-feedback"
    assert link.is_symlink()
    assert link.resolve() == SKILL_SRC.resolve()


def test_s118_running_it_twice_is_a_no_op(tmp_path):
    run(tmp_path)
    r = run(tmp_path)
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "unchanged" in r.stdout


def test_s118_refuses_to_clobber_a_real_file_or_folder_already_there(tmp_path):
    dest_dir = tmp_path / ".claude" / "skills"
    dest_dir.mkdir(parents=True)
    (dest_dir / "shipquick-feedback").mkdir()
    (dest_dir / "shipquick-feedback" / "notes.txt").write_text("mine\n", encoding="utf-8")
    r = run(tmp_path)
    assert r.returncode != 0
    assert (dest_dir / "shipquick-feedback" / "notes.txt").exists(), "must not touch a real folder that is not our symlink"
