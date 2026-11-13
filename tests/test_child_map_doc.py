"""Story #498: the snippet in docs/ADOPTION.md ("A child skips its slow jobs with its own map") runs as written.
No YAML library: the `run: |` blocks are cut out by indent, as tests/test_screens_doc.py cuts the screens example."""
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def section(root=ROOT):
    text = (root / "docs" / "ADOPTION.md").read_text(encoding="utf-8")
    m = re.search(r"^## A child skips its slow jobs with its own map.*?\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    assert m, "docs/ADOPTION.md has no section `A child skips its slow jobs with its own map`"
    return m.group(1)


def blocks(lang, root=ROOT):
    return re.findall(rf"```{lang}\n(.*?)```", section(root), re.S)


def run_blocks(yaml_text):
    """Every `run: |` body, dedented, in file order."""
    out, lines, i = [], yaml_text.split("\n"), 0
    while i < len(lines):
        m = re.match(r"^(\s*)(?:- )?run: \|$", lines[i])
        if m:
            indent = len(m.group(1)) + 2
            body, i = [], i + 1
            while i < len(lines) and (not lines[i].strip() or len(lines[i]) - len(lines[i].lstrip()) >= indent):
                body.append(lines[i][indent:] if lines[i].strip() else "")
                i += 1
            out.append("\n".join(body))
            continue
        i += 1
    return out


def git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, check=True)


def child(tmp_path):
    repo = tmp_path / "child"
    for rel, text in {".shipquick/change_map.json": blocks("json")[0], ".github/workflows/build.yml": blocks("yaml")[0], "docs/a.md": "d\n",
                      "app/main.py": "m\n", "knowledge/shipquick_latest/scripts/change_map.py": (ROOT / "scripts" / "change_map.py").read_text(encoding="utf-8")}.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    git(repo, "init", "-q", "-b", "dev")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    git(repo, "update-ref", "refs/remotes/origin/dev", "HEAD")
    git(repo, "switch", "-q", "-c", "feat/x")
    return repo


def edit(repo, path):
    p = repo / path
    p.write_text(p.read_text(encoding="utf-8") + "x\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", f"edit {path}")


def decide(repo, tmp_path):
    out = tmp_path / "out"
    out.write_text("", encoding="utf-8")
    script = run_blocks(blocks("yaml")[0])[0]
    env = dict(os.environ, EVENT="pull_request", BASE="dev", BEFORE="", RUNNER_TEMP=str(tmp_path), GITHUB_OUTPUT=str(out))
    r = subprocess.run(["bash", "-e", "-c", script], cwd=repo, env=env, capture_output=True, text=True)
    assert r.returncode == 0, (r.stdout, r.stderr)
    return dict(line.split("=", 1) for line in out.read_text(encoding="utf-8").splitlines())


def gate(repo, tmp_path, decision, needs):
    script = run_blocks(blocks("yaml")[0])[1]
    env = dict(os.environ, DECISION=decision, NEEDS=json.dumps(needs), RUNNER_TEMP=str(tmp_path))
    return subprocess.run(["bash", "-e", "-c", script], cwd=repo, env=env, capture_output=True, text=True)


def test_s498_the_snippet_has_a_changes_job_one_if_per_slow_job_and_a_last_gate_job():
    y = blocks("yaml")[0]
    assert re.search(r"^  changes:", y, re.M) and "if: needs.changes.outputs.app != 'false'" in y
    assert "needs: [changes, app-tests]" in y and "change_map.py gate" in y and y.index("  gate:") > y.index("  app-tests:")
    assert "cancel-in-progress: true" in y


def test_s498_a_docs_only_change_turns_the_area_off_and_the_gate_accepts_a_skipped_job(tmp_path):
    repo = child(tmp_path)
    edit(repo, "docs/a.md")
    d = decide(repo, tmp_path)
    assert d["app"] == "false", d
    r = gate(repo, tmp_path, d["decision"], {"changes": {"result": "success"}, "app-tests": {"result": "skipped"}})
    assert r.returncode == 0, (r.stdout, r.stderr)


def test_s498_a_change_under_the_area_path_turns_it_on_and_a_skipped_job_fails_the_gate(tmp_path):
    repo = child(tmp_path)
    edit(repo, "app/main.py")
    d = decide(repo, tmp_path)
    assert d["app"] == "true", d
    assert gate(repo, tmp_path, d["decision"], {"changes": {"result": "success"}, "app-tests": {"result": "success"}}).returncode == 0
    r = gate(repo, tmp_path, d["decision"], {"changes": {"result": "success"}, "app-tests": {"result": "skipped"}})
    assert r.returncode == 1 and "app-tests" in r.stdout, (r.stdout, r.stderr)


def test_s498_a_missing_map_on_the_base_branch_turns_everything_on(tmp_path):
    repo = child(tmp_path)
    git(repo, "rm", "-q", "-r", ".shipquick")
    git(repo, "commit", "-q", "-m", "no map")
    git(repo, "update-ref", "refs/remotes/origin/dev", "HEAD")   # the base has no map either
    edit(repo, "docs/a.md")
    d = decide(repo, tmp_path)
    assert json.loads(d["decision"]) == {"all": True}, d
