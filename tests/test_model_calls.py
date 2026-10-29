"""Story #107: the model load rules (smallest local model first, tasks sized to the model, a budgeted free tier) and the call-site lister.
Given a repo with model calls, when `scripts/model_calls.sh` runs, then every call site is listed with its file and line; with --check it fails when a call-site file is missing from the table."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "model_calls.sh"


def sh(cwd, *args):
    return subprocess.run(["bash", str(SCRIPT), *args], cwd=cwd, capture_output=True, text=True)


def repo(tmp_path):
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "engine.py").write_text('def ask(p):\n    return ollama_ask(url, model, num_predict=40)(p)\n', encoding="utf-8")
    (tmp_path / "app" / "ladder.py").write_text('URL = "https://openrouter.ai/api/v1/chat/completions"\n', encoding="utf-8")
    (tmp_path / "app" / "plain.py").write_text('def add(a, b):\n    return a + b\n', encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_x.py").write_text('def test_x():\n    assert ollama_ask\n', encoding="utf-8")
    return tmp_path


def test_every_model_call_site_is_listed_with_its_file_and_line_and_tests_are_left_out(tmp_path):
    r = sh(repo(tmp_path))
    assert r.returncode == 0, r.stderr
    assert "app/engine.py:2" in r.stdout and "app/ladder.py:1" in r.stdout
    assert "plain.py" not in r.stdout and "tests/test_x.py" not in r.stdout


def test_check_fails_when_a_call_site_file_is_missing_from_the_table_and_passes_when_it_is_there(tmp_path):
    root = repo(tmp_path)
    table = root / "docs" / "data" / "model-calls.md"
    table.parent.mkdir(parents=True)
    table.write_text("| # | Call | In | Out | Model | Lane |\n|---|---|---|---|---|---|\n| 1 | `app/engine.py` ask | 400 | 40 | gemma3:1b | urgent |\n", encoding="utf-8")
    r = sh(root, "--check", "docs/data/model-calls.md")
    assert r.returncode == 1 and "app/ladder.py" in r.stdout and "app/engine.py" not in r.stdout
    table.write_text(table.read_text(encoding="utf-8") + "| 2 | `app/ladder.py` remote | 2000 | 400 | openrouter :free | urgent |\n", encoding="utf-8")
    assert sh(root, "--check", "docs/data/model-calls.md").returncode == 0


def test_the_rules_doc_holds_the_ladder_the_lanes_the_budget_and_the_table_template():
    text = (ROOT / "docs" / "MODEL_LOAD.md").read_text(encoding="utf-8")
    for needed in ("smallest", "one third", "4B", "70 percent", "urgent", "background", "100", "fine-tun", "model-calls.md", "| # | Call |"):
        assert needed in text, needed


def test_claude_md_points_every_child_project_to_the_rules():
    assert "docs/MODEL_LOAD.md" in (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
