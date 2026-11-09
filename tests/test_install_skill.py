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


# ---- story #162: the qa-loop skill is a thin pointer that lives in the kit and installs the same way ----
QA_SRC = ROOT / "skills" / "qa-loop"


def test_s162_links_the_qa_loop_skill_too(tmp_path):
    r = run(tmp_path)
    assert r.returncode == 0, (r.stdout, r.stderr)
    link = tmp_path / ".claude" / "skills" / "qa-loop"
    assert link.is_symlink() and link.resolve() == QA_SRC.resolve()
    assert (tmp_path / ".claude" / "skills" / "shipquick-feedback").is_symlink()


def test_s162_a_real_qa_loop_folder_already_there_is_kept_and_named(tmp_path):
    dest = tmp_path / ".claude" / "skills" / "qa-loop"
    dest.mkdir(parents=True)
    (dest / "SKILL.md").write_text("my own copy\n", encoding="utf-8")
    r = run(tmp_path)
    assert r.returncode != 0 and "qa-loop" in r.stderr
    assert (dest / "SKILL.md").read_text(encoding="utf-8") == "my own copy\n"
    assert (tmp_path / ".claude" / "skills" / "shipquick-feedback").is_symlink(), "the other skill still installs"


def test_s162_the_pointer_skill_names_the_kit_doc_and_scripts_and_no_project():
    text = (QA_SRC / "SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---\nname: qa-loop\n")
    assert "docs/QA_LOOP.md" in text and "scripts/qa/" in text
    assert "goserve" not in text.lower()


def test_s162_the_qa_loop_doc_has_its_fifteen_sections():
    doc = (ROOT / "docs" / "QA_LOOP.md").read_text(encoding="utf-8")
    for n in range(1, 16):
        assert f"\n## {n}. " in doc, n
    for platform in ("Web", "Android", "iOS", "CLI"):
        assert platform in doc
